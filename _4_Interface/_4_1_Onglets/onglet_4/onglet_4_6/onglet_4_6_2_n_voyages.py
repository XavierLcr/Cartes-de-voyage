################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6                                #
# Onglet 4.6.2 – Nombre de voyages                                             #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
from collections import defaultdict
from datetime import datetime

from typing import List, Optional, Sequence

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, pyqtProperty
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
)
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QSizePolicy, QWidget, QToolTip

from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)
from _4_Interface._4_3_Icones._4_3_06_badge_pin import _dessiner_badge_pin

# 1 -- Nombre de voyages par an ------------------------------------------------


def nombre_voyages_par_annee(data, n_annees):
    # 1. Extraire les années des dates non None
    annees = []
    for voyage in data.values():
        date_deb = voyage.get("date_debut")
        if date_deb is not None:
            try:
                annee = datetime.strptime(date_deb, "%Y-%m-%d").year
                annees.append(annee)
            except ValueError:
                # Ignorer les dates mal formatées
                continue

    # 2. Compter le nombre de voyages par année
    compte_par_annee = defaultdict(int)
    for annee in annees:
        compte_par_annee[annee] += 1

    # 3. Générer la liste des 5 dernières années (ex: 2022-2026)
    annee_actuelle = datetime.now().year
    annees_5_dernieres = list(range(annee_actuelle - n_annees + 1, annee_actuelle + 1))

    # 4. Créer la liste finale avec les zéros pour les années manquantes
    resultat = [compte_par_annee.get(annee, 0) for annee in annees_5_dernieres]

    return resultat


# 2 -- Classe de création des couleurs -----------------------------------------


class ThemeCarte:
    """Palette de couleurs de la carte, générée depuis le style de l'appli."""

    def __init__(
        self,
        style,
        teinte=[i / 360 for i in range(0, 360, 45)],
        nuances={
            "min_luminosite": 0.8,
            "max_luminosite": 0.95,
            "min_saturation": 0.2,
            "max_saturation": 0.4,
        },
        limite_essais=20,
    ):
        # Fond : identique au fond général de l'appli
        self.fond = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#ffffff",
                sombre="#12141c",
            )
        )
        self.texte = QColor(
            str(renvoyer_couleur_texte(style=style, couleur=self.fond.name()))
            if style != 1
            else "#1c1f2b"
        )
        # Barre (fond des mini-barres du graphique) : dérivée du texte, très diluée
        self.barre = QColor(self.texte)
        self.barre.setAlpha(30 if style == 1 else 25)
        # Dégradé du badge (pin de destination)
        self.badge_debut = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#ff9d5c",
                sombre="#ff9d5c",
            )
        )
        self.badge_fin = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#ff5c8a",
                sombre="#ff5c8a",
                reference=self.badge_debut.name(),
                essais=limite_essais,
            )
        )
        # Sous-texte
        self.sous_texte = QColor(self.texte)
        self.sous_texte.setAlpha(140)
        # Barre mise en avant (dernière période du mini graphique)
        self.barre_surbrillance = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#ff5c8a",
                sombre="#ff9d5c",
                reference=self.badge_fin.name(),
                essais=limite_essais,
            )
        )
        # Indicateurs de tendance
        self.positif = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#1fa15c",
                sombre="#3ee08c",
            )
        )
        self.negatif = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#e0453f",
                sombre="#ff6b6b",
            )
        )
        self.neutre = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#5A595A",
                sombre="#d2d1d2",
            )
        )

        # Ombre portée de la carte
        self.ombre = QColor(self.texte)
        self.ombre.setAlpha(60 if style == 1 else 120)


# 3 -- Classe du compteur  -----------------------------------------------------


class NombreVoyagesAnnu(QWidget):
    """
    Carte "Voyages effectués" : gros chiffre animé, badge en forme de pin
    de destination, indicateur de tendance, mini graphique en barres
    (historique par période). Style volontairement différent du compteur
    circulaire, pour varier les widgets d'un même tableau de bord.
    """

    def __init__(
        self,
        fonction_traduction,
        nombre: int = 0,
        etiquette: str = "Voyages effectués",
        historique: Optional[Sequence[int]] = None,
        tendance: Optional[int] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        nombre             : valeur affichée (nombre de voyages).
        historique          : historique court pour le mini graphique en
                              barres (ex. [3, 5, 4, 6, 8, 9] = 6 dernières
                              périodes).
        tendance            : évolution à afficher (ex. +3 ou -2). None =
                              masqué.
        style               : style de l'appli transmis à ThemeCarte
                              (ignoré si `theme` fourni).
        """
        super().__init__(parent)

        self.setMouseTracking(True)
        self.points_hover = []

        self.voyages = {}
        self.fonction_traduction = fonction_traduction
        self._nombre = 0.0
        self.nombre_cible = 0
        self.texte_etiquette = etiquette
        self.historique: List[int] = list(historique) if historique else []
        self.tendance = tendance
        self.etiquette_tendance = f"{datetime.now().year} vs {datetime.now().year-1}"
        self.n_annees_histo = 6

        self.theme = ThemeCarte(style=1)

        self.setMinimumSize(300, 100)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(30)
        self._ombre_effet.setOffset(0, 8)
        self._ombre_effet.setColor(self.theme.ombre)
        self.setGraphicsEffect(self._ombre_effet)

        self._animation_nombre = QPropertyAnimation(self, b"valeurAnimee", self)
        self._animation_nombre.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.definir_valeur(nombre, animer=True)
        self.set_langue()

    # ---------------------------------------------------------------
    # Propriété animable Qt
    # ---------------------------------------------------------------
    def _obtenir_valeur_animee(self) -> float:
        return self._nombre

    def _definir_valeur_animee(self, v: float) -> None:
        self._nombre = v
        self.update()

    valeurAnimee = pyqtProperty(float, _obtenir_valeur_animee, _definir_valeur_animee)

    # ---------------------------------------------------------------
    # API publique
    # ---------------------------------------------------------------
    def definir_valeur(
        self, nombre: int, animer: bool = True, duree: int = 1000
    ) -> None:
        """Met à jour le nombre affiché (avec ou sans animation)."""
        nombre = max(0, nombre)
        self.nombre_cible = nombre

        self._animation_nombre.stop()
        self._animation_nombre.setDuration(duree if animer else 0)
        self._animation_nombre.setStartValue(self._nombre)
        self._animation_nombre.setEndValue(float(nombre))
        self._animation_nombre.start()

    def definir_historique(self, historique: Sequence[int]) -> None:
        """Remplace l'historique utilisé pour le mini graphique en barres."""
        self.historique = list(historique)
        self.update()

    def definir_tendance(
        self, tendance: Optional[int], etiquette_tendance: str = "vs l'an dernier"
    ) -> None:
        """Affiche/masque l'indicateur de tendance (+3, -2, ...)."""
        self.tendance = tendance
        self.etiquette_tendance = etiquette_tendance
        self.update()

    @property
    def style(self):
        return self._style

    # ---------------------------------------------------------------
    # Rendu
    # ---------------------------------------------------------------
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()
        rect_carte = QRectF(0, 0, w, h).adjusted(2, 2, -2, -2)
        rayon = min(24, h * 0.18)

        # --- fond de carte ---
        chemin = QPainterPath()
        chemin.addRoundedRect(rect_carte, rayon, rayon)
        painter.fillPath(chemin, QBrush(self.theme.fond))

        marge = w * 0.06
        taille_badge = h * 0.4

        # --- badge (pin de destination) ---
        rect_badge = QRectF(marge, (h - taille_badge) / 2, taille_badge, taille_badge)
        _dessiner_badge_pin(
            painter,
            rect_badge,
            badge_debut=self.theme.badge_debut,
            badge_fin=self.theme.badge_fin,
        )

        # --- zone texte à droite du badge ---
        x_texte = rect_badge.right() + marge * 0.8
        largeur_texte = w - x_texte - marge

        police_valeur = QFont("Segoe UI", max(11, int(h * 0.2)), QFont.Weight.Bold)
        painter.setFont(police_valeur)
        painter.setPen(self.theme.texte)
        rect_valeur = QRectF(x_texte, h * 0.08, largeur_texte, h * 0.4)
        painter.drawText(
            rect_valeur,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"{int(round(self._nombre))}",
        )

        police_etiquette = QFont("Segoe UI", max(7, int(h * 0.08)))
        painter.setFont(police_etiquette)
        painter.setPen(self.theme.sous_texte)
        rect_etiquette = QRectF(x_texte, h * 0.46, largeur_texte, h * 0.18)
        painter.drawText(
            rect_etiquette,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.texte_etiquette,
        )

        # --- indicateur de tendance ---
        if self.tendance is not None:
            self._dessiner_tendance(
                painter, QRectF(x_texte, h * 0.60, largeur_texte, h * 0.16)
            )

        # --- mini graphique en barres (historique) ---
        if self.historique:
            rect_graphique = QRectF(marge, h * 0.80, w - 2 * marge, h * 0.14)
            self._dessiner_graphique_barres(painter, rect_graphique)

    def _dessiner_tendance(self, painter: QPainter, rect: QRectF) -> None:
        if self.tendance > 0:
            couleur = self.theme.positif
            fleche = "▲"
            signe = "+"
        elif self.tendance < 0:
            couleur = self.theme.negatif
            fleche = "▼"
            signe = ""
        else:
            couleur = self.theme.neutre
            fleche = "⚖"  # ou "→", "▬", voire ""
            signe = "+"

        police = QFont(
            "Segoe UI", max(6, int(rect.height() * 0.55)), QFont.Weight.DemiBold
        )
        painter.setFont(police)
        painter.setPen(couleur)
        texte = f"{fleche} {signe}{self.tendance}"
        painter.drawText(
            rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, texte
        )

        fm = painter.fontMetrics()
        largeur_texte = fm.horizontalAdvance(texte)

        police_suffixe = QFont("Segoe UI", max(6, int(rect.height() * 0.4)))
        painter.setFont(police_suffixe)
        painter.setPen(self.theme.sous_texte)
        rect_suffixe = rect.adjusted(largeur_texte + 6, 0, 0, 0)
        painter.drawText(
            rect_suffixe,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.etiquette_tendance,
        )

    def _dessiner_graphique_barres(self, painter: QPainter, rect: QRectF) -> None:

        self.points_hover = []

        valeurs = self.historique[-8:]  # 8 dernières périodes max, pour rester lisible
        if not valeurs:
            return
        maximum = max(valeurs) or 1
        n = len(valeurs)
        espace = rect.width() * 0.10 / max(1, n - 1) if n > 1 else 0
        largeur_barre = (rect.width() - espace * (n - 1)) / n

        painter.setPen(Qt.PenStyle.NoPen)
        for i, v in enumerate(valeurs):
            hauteur_barre = rect.height() * (v / maximum) if maximum else 0
            hauteur_barre = max(
                hauteur_barre, rect.height() * 0.08
            )  # toujours un peu visible
            x = rect.left() + i * (largeur_barre + espace)
            y = rect.bottom() - hauteur_barre
            est_derniere = i == n - 1
            couleur = (
                self.theme.barre_surbrillance if est_derniere else self.theme.barre
            )
            painter.setBrush(QBrush(couleur))
            rect_barre = QRectF(x, y, largeur_barre, hauteur_barre)
            chemin = QPainterPath()
            chemin.addRoundedRect(rect_barre, largeur_barre * 0.3, largeur_barre * 0.3)
            painter.drawPath(chemin)

            self.points_hover.append(
                {
                    "rect": rect_barre,
                    "valeur": v,
                }
            )

    def set_langue(self):
        """Mise à jour de la langue"""
        self.texte_etiquette = self.fonction_traduction("4_6_3_voyages_effectues")
        self.update()

    def set_style(self, style, nuances, teintes):

        self.theme = ThemeCarte(
            style=style, nuances=nuances, teinte=teintes, limite_essais=20
        )
        self._ombre_effet.setColor(self.theme.ombre)
        self.update()

    def set_voyages(self, voyages):
        self.voyages = voyages.copy()
        self.set_valeurs()
        self.update()

    def set_valeurs(self):

        voyages_temp = nombre_voyages_par_annee(
            data=self.voyages, n_annees=self.n_annees_histo
        )

        self.definir_valeur(nombre=len(self.voyages))
        self.definir_historique(historique=voyages_temp)
        self.definir_tendance(
            tendance=voyages_temp[-1] - voyages_temp[-2],
            etiquette_tendance=self.etiquette_tendance,
        )

    def mouseMoveEvent(self, event):

        pos = event.position()

        for point in self.points_hover:
            if point["rect"].contains(pos):
                QToolTip.showText(
                    event.globalPosition().toPoint(),
                    f"{point['valeur']}",
                    self,
                )
                return

        QToolTip.hideText()
