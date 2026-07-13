################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6                                #
# Onglet 4.6.3 – Jours voyagés par mois                                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Optional, Sequence, Tuple
import math
from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    Qt,
    pyqtProperty,
    QPointF,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QSizePolicy, QWidget, QToolTip

from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)

# Initiales des mois, dans l'ordre calendaire (index 0 = janvier)
NOMS_MOIS_INITIALES = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]


# 1 -- Jours voyagés par mois ---------------------------------------------------


def jours_voyages_par_mois(data, n_mois: int = 12) -> Tuple[List[int], List[int], int]:
    """
    Calcule le nombre de jours voyagés par mois sur les `n_mois` derniers
    mois (mois calendaire courant inclus), à partir de `date_debut` et
    `date_fin`.

    - Un voyage dont `date_debut` OU `date_fin` vaut None (ou est mal
      formatée) est ignoré.
    - Un voyage à cheval sur plusieurs mois voit ses jours répartis sur
      chacun des mois concernés (pas tout attribué au mois de départ).

    Renvoie (valeurs, mois_numeros, total) :
    - valeurs       : liste de n_mois entiers, du plus ancien au plus
                      récent (le dernier élément = mois en cours).
    - mois_numeros  : numéro du mois (1 = janvier ... 12 = décembre)
                      correspondant à chaque élément de `valeurs`.
    - total         : somme des jours voyagés sur la période.
    """
    aujourd_hui = datetime.now()

    # 1. Bornes calendaires des n_mois derniers mois (du plus ancien au
    #    plus récent), sous la forme (premier_jour, dernier_jour).
    bornes_mois: List[Tuple[datetime, datetime]] = []
    mois_numeros: List[int] = []
    for i in range(n_mois - 1, -1, -1):
        mois_index = aujourd_hui.month - 1 - i
        annee = aujourd_hui.year + mois_index // 12
        mois = mois_index % 12 + 1
        debut_mois = datetime(annee, mois, 1)
        if mois == 12:
            fin_mois = datetime(annee + 1, 1, 1) - timedelta(days=1)
        else:
            fin_mois = datetime(annee, mois + 1, 1) - timedelta(days=1)
        bornes_mois.append((debut_mois, fin_mois))
        mois_numeros.append(mois)

    valeurs = [0] * n_mois

    # 2. Parcourir les voyages valides et répartir leurs jours sur les mois
    #    qu'ils traversent.
    for voyage in data.values():
        date_deb_str = voyage.get("date_debut")
        date_fin_str = voyage.get("date_fin")
        if date_deb_str is None or date_fin_str is None:
            continue
        try:
            date_deb = datetime.strptime(date_deb_str, "%Y-%m-%d")
            date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d")
        except ValueError:
            # Date mal formatée : on ignore ce voyage plutôt que de planter
            continue
        if date_fin < date_deb:
            date_deb, date_fin = date_fin, date_deb

        for i, (debut_mois, fin_mois) in enumerate(bornes_mois):
            chevauchement_debut = max(date_deb, debut_mois)
            chevauchement_fin = min(date_fin, fin_mois)
            if chevauchement_fin >= chevauchement_debut:
                valeurs[i] += (chevauchement_fin - chevauchement_debut).days + 1

    total = sum(valeurs)
    return valeurs, mois_numeros, total


# 2 -- Classe de création des couleurs -----------------------------------------


class ThemeJoursVoyages:
    """
    Palette de couleurs de la carte "Jours voyagés".

    Reprend la même structure que `ThemeCarte` (onglet 4.6.3) et
    `CompteurTheme` (onglet 4.6.2) — même fond de carte, même convention
    d'ombre, mêmes appels de style — avec son propre accent indigo ->
    violet, pour que le tableau de bord affiche trois teintes distinctes
    mais construites de façon identique.
    """

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
        # Fond de carte : identique aux deux autres widgets.
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
        # Sous-texte
        self.sous_texte = QColor(self.texte)
        self.sous_texte.setAlpha(140)

        # Barres "normales" du graphique mensuel : dérivées du texte, très
        # diluées, même alpha que les widgets voisins.
        self.barre = QColor(self.texte)
        self.barre.setAlpha(30 if style == 1 else 25)

        # Dégradé du badge (icône calendrier) : indigo -> violet.
        self.badge_debut = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#6366F1",
                sombre="#818CF8",
            )
        )
        self.badge_fin = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#8B5CF6",
                sombre="#A78BFA",
                reference=self.badge_debut.name(),
                essais=limite_essais,
            )
        )

        # Barre du mois en cours, mise en avant : même famille que le
        # badge mais dans l'autre sens (comme `barre_surbrillance` dans
        # ThemeCarte), pour un léger contraste avec le reste du graphique.
        self.barre_surbrillance = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#8B5CF6",
                sombre="#6366F1",
                reference=self.badge_fin.name(),
                essais=limite_essais,
            )
        )

        # Ombre portée : même convention que les widgets voisins.
        self.ombre = QColor(self.texte)
        self.ombre.setAlpha(60 if style == 1 else 120)


# 3 -- Classe du widget ----------------------------------------------------------


class JoursVoyagesParMoisWidget(QWidget):
    """
    Carte "Jours voyagés" : nombre total de jours passés en voyage sur les
    12 derniers mois (gros chiffre animé + badge), avec un mini graphique
    en barres montrant la répartition mois par mois.

    Reprend le vocabulaire visuel des deux autres widgets du tableau de
    bord (carte à coins arrondis, même ombre, même typographie) avec son
    propre accent indigo -> violet, pour compléter la palette turquoise
    du compteur de pays et orange/rose du nombre de voyages.
    """

    def __init__(
        self,
        fonction_traduction,
        jours: Optional[Sequence[int]] = None,
        mois_numeros: Optional[Sequence[int]] = None,
        etiquette: str = "Jours voyagés",
        n_mois: int = 12,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        jours          : historique de jours voyagés par mois (n_mois
                         valeurs, du plus ancien au plus récent). Si None,
                         démarre à zéro partout (à remplir via
                         `set_voyages`).
        mois_numeros   : numéro de mois (1-12) associé à chaque valeur de
                         `jours`, pour l'étiquette sous chaque barre.
        n_mois         : profondeur du graphique mensuel (12 par défaut).
        """
        super().__init__(parent)

        self.setMouseTracking(True)
        self.points_hover = []

        self.voyages = {}
        self.fonction_traduction = fonction_traduction
        self.n_mois = n_mois
        self._total = 0.0
        self.total_cible = 0
        self.texte_etiquette = etiquette
        self.historique_jours: List[int] = list(jours) if jours else [0] * n_mois
        self.mois_numeros: List[int] = (
            list(mois_numeros) if mois_numeros else self._mois_par_defaut()
        )
        self._progression_barres = 0.0

        self.theme = ThemeJoursVoyages(style=1)

        self.setMinimumSize(320, 180)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(30)
        self._ombre_effet.setOffset(0, 8)
        self._ombre_effet.setColor(self.theme.ombre)
        self.setGraphicsEffect(self._ombre_effet)

        self._animation_total = QPropertyAnimation(self, b"valeurAnimee", self)
        self._animation_total.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._animation_barres = QPropertyAnimation(self, b"progressionBarres", self)
        self._animation_barres.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation_barres.setStartValue(0.0)
        self._animation_barres.setEndValue(1.0)

        self.definir_historique(self.historique_jours, self.mois_numeros, animer=False)
        self.definir_valeur(sum(self.historique_jours), animer=True)
        self.set_langue()

    @staticmethod
    def _mois_par_defaut() -> List[int]:
        """Numéros de mois (1-12) des 12 derniers mois, par défaut."""
        aujourd_hui = datetime.now()
        return [((aujourd_hui.month - 1 - i) % 12) + 1 for i in range(11, -1, -1)]

    # ---------------------------------------------------------------
    # Propriétés animables Qt
    # ---------------------------------------------------------------
    def _obtenir_valeur_animee(self) -> float:
        return self._total

    def _definir_valeur_animee(self, v: float) -> None:
        self._total = v
        self.update()

    valeurAnimee = pyqtProperty(float, _obtenir_valeur_animee, _definir_valeur_animee)

    def _obtenir_progression_barres(self) -> float:
        return self._progression_barres

    def _definir_progression_barres(self, v: float) -> None:
        self._progression_barres = v
        self.update()

    progressionBarres = pyqtProperty(
        float, _obtenir_progression_barres, _definir_progression_barres
    )

    # ---------------------------------------------------------------
    # API publique
    # ---------------------------------------------------------------
    def definir_valeur(
        self, total: int, animer: bool = True, duree: int = 1000
    ) -> None:
        """Met à jour le nombre total de jours affiché (avec ou sans animation)."""
        total = max(0, total)
        self.total_cible = total

        self._animation_total.stop()
        self._animation_total.setDuration(duree if animer else 0)
        self._animation_total.setStartValue(self._total)
        self._animation_total.setEndValue(float(total))
        self._animation_total.start()

    def definir_historique(
        self,
        historique: Sequence[int],
        mois_numeros: Optional[Sequence[int]] = None,
        animer: bool = True,
        duree: int = 900,
    ) -> None:
        """Remplace les valeurs du graphique mensuel (et les rejoue en entrée)."""
        self.historique_jours = list(historique)
        if mois_numeros is not None:
            self.mois_numeros = list(mois_numeros)

        self._animation_barres.stop()
        self._animation_barres.setDuration(duree if animer else 0)
        if animer:
            self._progression_barres = 0.0
        else:
            self._progression_barres = 1.0
        self._animation_barres.start()

    def set_langue(self):
        """Mise à jour de la langue."""
        self.texte_etiquette = self.fonction_traduction("4_6_4_jours_voyages")
        self.update()

    def set_style(self, style, nuances, teintes):
        self.theme = ThemeJoursVoyages(
            style=style, nuances=nuances, teinte=teintes, limite_essais=20
        )
        self._ombre_effet.setColor(self.theme.ombre)
        self.update()

    def set_voyages(self, voyages):
        self.voyages = voyages.copy()
        self.set_valeurs()
        self.update()

    def set_valeurs(self):
        valeurs, mois_numeros, total = jours_voyages_par_mois(
            data=self.voyages, n_mois=self.n_mois
        )
        self.definir_historique(valeurs, mois_numeros)
        self.definir_valeur(total)

    # ---------------------------------------------------------------
    # Rendu
    # ---------------------------------------------------------------
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()

        # --- carte à coins arrondis : même formule que les widgets voisins ---
        rect_carte = QRectF(0, 0, w, h).adjusted(2, 2, -2, -2)
        rayon = min(24, min(w, h) * 0.14)
        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(rect_carte, rayon, rayon)
        painter.fillPath(chemin_carte, QBrush(self.theme.fond))
        painter.setClipPath(chemin_carte)

        marge = w * 0.055
        taille_badge = h * 0.24

        # --- badge (icône calendrier) ---
        rect_badge = QRectF(marge, h * 0.08, taille_badge, taille_badge)
        self._dessiner_badge_calendrier(painter, rect_badge)

        # --- zone texte à droite du badge ---
        x_texte = rect_badge.right() + marge * 0.8
        largeur_texte = w - x_texte - marge

        police_valeur = QFont("Segoe UI", max(11, int(h * 0.15)), QFont.Weight.Bold)
        painter.setFont(police_valeur)
        painter.setPen(self.theme.texte)
        rect_valeur = QRectF(x_texte, h * 0.05, largeur_texte, h * 0.20)
        painter.drawText(
            rect_valeur,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"{int(round(self._total))}",
        )

        police_etiquette = QFont("Segoe UI", max(7, int(h * 0.075)))
        painter.setFont(police_etiquette)
        painter.setPen(self.theme.sous_texte)
        rect_etiquette = QRectF(x_texte, h * 0.27, largeur_texte, h * 0.14)
        painter.drawText(
            rect_etiquette,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.texte_etiquette,
        )

        # --- graphique en barres mensuel + étiquettes des mois ---
        rect_barres = QRectF(marge, h * 0.52, w - 2 * marge, h * 0.30)
        rect_etiquettes = QRectF(marge, h * 0.83, w - 2 * marge, h * 0.13)
        self._dessiner_graphique_mensuel(painter, rect_barres, rect_etiquettes)

    def _dessiner_badge_calendrier(self, painter: QPainter, rect: QRectF) -> None:
        """Badge calendrier dont la couleur de fond ET l'illustration sur la
        page changent selon la saison en cours (flocon sur colline enneigée
        en hiver, pousse sur colline verte au printemps, soleil sur colline
        en été, feuille tombante en automne)."""
        rayon_badge = rect.width() * 0.3
        mois = datetime.now().month
        couleur_debut, couleur_fin = self._couleurs_saison(mois)

        degrade = QLinearGradient(rect.topLeft(), rect.bottomRight())
        degrade.setColorAt(0.0, couleur_debut)
        degrade.setColorAt(1.0, couleur_fin)
        chemin_corps = QPainterPath()
        chemin_corps.addRoundedRect(rect, rayon_badge, rayon_badge)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(degrade))
        painter.drawPath(chemin_corps)

        painter.setClipPath(chemin_corps)

        # léger vernis en haut du badge, pour donner du relief
        vernis = QLinearGradient(rect.topLeft(), QPointF(rect.left(), rect.bottom()))
        vernis.setColorAt(0.0, QColor(255, 255, 255, 70))
        vernis.setColorAt(0.5, QColor(255, 255, 255, 15))
        vernis.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(vernis))
        painter.drawRect(rect)

        s = rect.width()

        # petits anneaux de reliure, en haut du calendrier
        largeur_anneau = s * 0.07
        hauteur_anneau = s * 0.16
        painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
        for fraction_x in (0.28, 0.72):
            rect_anneau = QRectF(
                rect.left() + s * fraction_x - largeur_anneau / 2,
                rect.top() - hauteur_anneau * 0.35,
                largeur_anneau,
                hauteur_anneau,
            )
            chemin_anneau = QPainterPath()
            chemin_anneau.addRoundedRect(
                rect_anneau, largeur_anneau / 2, largeur_anneau / 2
            )
            painter.drawPath(chemin_anneau)

        # bandeau d'en-tête (léger voile blanc translucide)
        rect_entete = QRectF(rect.left(), rect.top() + s * 0.18, s, s * 0.16)
        painter.setBrush(QBrush(QColor(255, 255, 255, 60)))
        painter.drawRect(rect_entete)

        # --- scène saisonnière, sur le reste de la page du calendrier ---
        rect_scene = QRectF(
            rect.left(),
            rect_entete.bottom(),
            s,
            rect.bottom() - rect_entete.bottom(),
        )
        self._dessiner_scene_saison(painter, rect_scene, mois)

        painter.setClipping(False)

    def _couleurs_saison(self, mois: int) -> tuple[QColor, QColor]:
        """Renvoie le couple (début, fin) de dégradé du badge pour le mois
        donné : la teinte tourne selon la saison, tandis que saturation /
        luminosité restent pilotées par le thème (cohérence clair/sombre)."""
        if mois in (12, 1, 2):
            teinte_debut, teinte_fin = 205, 225  # bleu glacé -> bleu-violet froid
        elif mois in (3, 4, 5):
            teinte_debut, teinte_fin = 150, 115  # vert tendre -> vert printemps
        elif mois in (6, 7, 8):
            teinte_debut, teinte_fin = 45, 25  # jaune soleil -> orangé chaud
        else:
            teinte_debut, teinte_fin = 20, 355  # roux automnal -> rouge feuille

        _, saturation_debut, valeur_debut, alpha_debut = self.theme.badge_debut.getHsv()
        _, saturation_fin, valeur_fin, alpha_fin = self.theme.badge_fin.getHsv()

        # on garantit une saturation minimale pour que les couleurs
        # saisonnières restent franches même si la palette du thème est pastel
        saturation_debut = max(saturation_debut, 140)
        saturation_fin = max(saturation_fin, 140)

        couleur_debut = QColor.fromHsv(
            teinte_debut, saturation_debut, valeur_debut, alpha_debut
        )
        couleur_fin = QColor.fromHsv(teinte_fin, saturation_fin, valeur_fin, alpha_fin)
        return couleur_debut, couleur_fin

    def _dessiner_scene_saison(
        self, painter: QPainter, rect_scene: QRectF, mois: int
    ) -> None:
        """Dessine, dans la zone `rect_scene` (la page du calendrier), une
        petite colline avec un élément saisonnier au-dessus."""
        # colline (silhouette commune à toutes les saisons)
        colline = QPainterPath()
        colline.moveTo(rect_scene.left(), rect_scene.bottom())
        colline.quadTo(
            QPointF(
                rect_scene.center().x(),
                rect_scene.top() + rect_scene.height() * 0.32,
            ),
            QPointF(rect_scene.right(), rect_scene.bottom()),
        )
        colline.lineTo(rect_scene.right(), rect_scene.bottom())
        colline.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 80)))
        painter.drawPath(colline)

        centre_icone = QPointF(
            rect_scene.center().x(), rect_scene.top() + rect_scene.height() * 0.24
        )
        taille_icone = rect_scene.height() * 0.9

        if mois in (12, 1, 2):
            self._dessiner_icone_flocon(painter, centre_icone, taille_icone)
        elif mois in (3, 4, 5):
            self._dessiner_icone_pousse(painter, centre_icone, taille_icone)
        elif mois in (6, 7, 8):
            self._dessiner_icone_soleil(painter, centre_icone, taille_icone)
        else:
            self._dessiner_icone_feuille(painter, centre_icone, taille_icone)

    @staticmethod
    def _dessiner_icone_soleil(
        painter: QPainter, centre: QPointF, taille: float
    ) -> None:
        """Icône été : disque plein avec halo, entouré de rayons alternés
        (longs et courts), pour un rendu plus détaillé qu'un simple
        cercle au contour."""
        rayon = taille * 0.32  # disque plus grand qu'avant

        # --- halo, derrière le disque ---
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 55)))
        painter.drawEllipse(centre, rayon * 1.55, rayon * 1.55)

        # --- disque plein, légèrement dégradé pour un effet de galbe ---
        degrade_disque = QLinearGradient(
            QPointF(centre.x() - rayon, centre.y() - rayon),
            QPointF(centre.x() + rayon, centre.y() + rayon),
        )
        degrade_disque.setColorAt(0.0, QColor(255, 255, 255, 245))
        degrade_disque.setColorAt(1.0, QColor(255, 255, 255, 195))
        painter.setBrush(QBrush(degrade_disque))
        painter.drawEllipse(centre, rayon, rayon)

        # --- rayons alternés : longs/fins et courts/épais ---
        n_rayons = 12
        for i in range(n_rayons):
            angle = i * (2 * math.pi / n_rayons)
            est_rayon_long = i % 2 == 0

            depart = 1.22 if est_rayon_long else 1.30
            fin = 1.85 if est_rayon_long else 1.55
            largeur = taille * (0.045 if est_rayon_long else 0.032)
            alpha = 235 if est_rayon_long else 170

            p1 = QPointF(
                centre.x() + math.cos(angle) * rayon * depart,
                centre.y() + math.sin(angle) * rayon * depart,
            )
            p2 = QPointF(
                centre.x() + math.cos(angle) * rayon * fin,
                centre.y() + math.sin(angle) * rayon * fin,
            )
            painter.setPen(
                QPen(
                    QColor(255, 255, 255, alpha),
                    max(1.1, largeur),
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                )
            )
            painter.drawLine(p1, p2)

        # --- Petit visage discret, pour un peu de caractère ---
        painter.setPen(Qt.PenStyle.NoPen)

        rayon_oeil = rayon * 0.09
        painter.setBrush(QBrush(QColor(230, 130, 20, 190)))
        for signe in (-1, 1):
            centre_oeil = QPointF(
                centre.x() + signe * rayon * 0.32, centre.y() - rayon * 0.12
            )
            painter.drawEllipse(centre_oeil, rayon_oeil, rayon_oeil)

        # petit sourire
        rect_sourire = QRectF(
            centre.x() - rayon * 0.28,
            centre.y() - rayon * 0.05,
            rayon * 0.56,
            rayon * 0.4,
        )
        painter.setPen(
            QPen(
                QColor(230, 130, 20, 190),
                max(0.9, rayon * 0.08),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect_sourire, 200 * 16, 140 * 16)

    @staticmethod
    def _dessiner_icone_flocon(
        painter: QPainter, centre: QPointF, taille: float
    ) -> None:
        """Icône hiver : flocon à 6 branches, avec petites ramifications."""
        rayon = taille * 0.42
        painter.setPen(
            QPen(
                QColor(255, 255, 255, 235),
                max(1.3, taille * 0.045),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )

        for i in range(3):
            angle = i * math.pi / 3
            dx, dy = math.cos(angle) * rayon, math.sin(angle) * rayon
            p1 = QPointF(centre.x() - dx, centre.y() - dy)
            p2 = QPointF(centre.x() + dx, centre.y() + dy)
            painter.drawLine(p1, p2)

            for signe in (1, -1):
                base = QPointF(
                    centre.x() + dx * 0.55 * signe, centre.y() + dy * 0.55 * signe
                )
                for decalage in (math.pi / 3.2, -math.pi / 3.2):
                    a = angle + decalage
                    embout = QPointF(
                        base.x() + math.cos(a) * rayon * 0.3 * signe,
                        base.y() + math.sin(a) * rayon * 0.3 * signe,
                    )
                    painter.drawLine(base, embout)

    @staticmethod
    def _dessiner_icone_pousse(
        painter: QPainter, centre: QPointF, taille: float
    ) -> None:
        """Icône printemps : tige en léger S, deux feuilles asymétriques
        attachées à des hauteurs différentes, et un petit bourgeon au
        sommet."""
        bas = QPointF(centre.x(), centre.y() + taille * 0.36)
        haut = QPointF(centre.x() + taille * 0.03, centre.y() - taille * 0.30)

        # --- tige, légère forme en S ---
        tige = QPainterPath()
        tige.moveTo(bas)
        tige.cubicTo(
            QPointF(bas.x() - taille * 0.09, bas.y() - taille * 0.32),
            QPointF(haut.x() + taille * 0.09, haut.y() + taille * 0.30),
            haut,
        )
        painter.setPen(
            QPen(
                QColor(255, 255, 255, 235),
                max(1.3, taille * 0.045),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(tige)

        @staticmethod
        def _point_sur_tige(t: float) -> QPointF:
            """Point interpolé sur la courbe de tige (Bézier cubique), pour
            attacher les feuilles bien sur le tracé plutôt qu'à côté."""
            u = 1 - t
            c1 = QPointF(bas.x() - taille * 0.09, bas.y() - taille * 0.32)
            c2 = QPointF(haut.x() + taille * 0.09, haut.y() + taille * 0.30)
            x = (
                u**3 * bas.x()
                + 3 * u**2 * t * c1.x()
                + 3 * u * t**2 * c2.x()
                + t**3 * haut.x()
            )
            y = (
                u**3 * bas.y()
                + 3 * u**2 * t * c1.y()
                + 3 * u * t**2 * c2.y()
                + t**3 * haut.y()
            )
            return QPointF(x, y)

        def dessiner_feuille(
            attache: QPointF, signe: int, echelle: float, rotation_deg: float
        ) -> None:
            """Dessine une feuille en forme de goutte (asymétrique), avec
            une fine nervure centrale, attachée au point `attache` de la
            tige et orientée par `signe` (gauche/droite) et `rotation_deg`."""
            longueur = taille * 0.34 * echelle
            largeur = taille * 0.16 * echelle
            angle = math.radians(rotation_deg) * signe

            # direction principale de la feuille (vers l'extérieur et le haut)
            direction = QPointF(math.sin(angle) * signe, -math.cos(angle))
            normale = QPointF(-direction.y(), direction.x())

            pointe = QPointF(
                attache.x() + direction.x() * longueur,
                attache.y() + direction.y() * longueur,
            )
            # point le plus large de la feuille, décalé pour l'asymétrie
            large = QPointF(
                attache.x() + direction.x() * longueur * 0.42 + normale.x() * largeur,
                attache.y() + direction.y() * longueur * 0.42 + normale.y() * largeur,
            )

            feuille = QPainterPath()
            feuille.moveTo(attache)
            feuille.quadTo(large, pointe)
            feuille.quadTo(
                QPointF(
                    attache.x()
                    + direction.x() * longueur * 0.5
                    - normale.x() * largeur * 0.35,
                    attache.y()
                    + direction.y() * longueur * 0.5
                    - normale.y() * largeur * 0.35,
                ),
                attache,
            )
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 225)))
            painter.drawPath(feuille)

            # nervure centrale, légèrement incurvée
            nervure = QPainterPath()
            nervure.moveTo(attache)
            nervure.quadTo(large, pointe)
            painter.setPen(QPen(QColor(255, 255, 255, 130), max(0.8, taille * 0.02)))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(nervure)

        # feuille basse, plus grande, penchée vers la gauche
        dessiner_feuille(_point_sur_tige(0.42), signe=-1, echelle=1.0, rotation_deg=48)
        # feuille haute, plus petite, penchée vers la droite
        dessiner_feuille(_point_sur_tige(0.74), signe=1, echelle=0.75, rotation_deg=40)

        # --- petit bourgeon au sommet de la tige ---
        rayon_bourgeon = taille * 0.06
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
        painter.drawEllipse(haut, rayon_bourgeon, rayon_bourgeon)

    @staticmethod
    def _dessiner_icone_feuille(
        painter: QPainter, centre: QPointF, taille: float
    ) -> None:
        """Icône automne : feuille tombante, agrandie, avec nervure
        centrale et nervures secondaires "creusées" dans la feuille (la
        transparence laisse apparaître le fond du badge, plutôt qu'un
        trait dessiné par-dessus)."""
        echelle = 1.2  # feuille légèrement plus grande qu'avant

        haut = QPointF(centre.x(), centre.y() - taille * 0.34 * echelle)
        bas = QPointF(centre.x(), centre.y() + taille * 0.30 * echelle)

        feuille = QPainterPath()
        feuille.moveTo(bas)
        feuille.cubicTo(
            QPointF(
                centre.x() - taille * 0.32 * echelle,
                centre.y() + taille * 0.12 * echelle,
            ),
            QPointF(
                centre.x() - taille * 0.28 * echelle,
                centre.y() - taille * 0.26 * echelle,
            ),
            haut,
        )
        feuille.cubicTo(
            QPointF(
                centre.x() + taille * 0.28 * echelle,
                centre.y() - taille * 0.26 * echelle,
            ),
            QPointF(
                centre.x() + taille * 0.32 * echelle,
                centre.y() + taille * 0.12 * echelle,
            ),
            bas,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 225)))
        painter.drawPath(feuille)

        # petite tige, en dur (pas "creusée", pour rester bien visible)
        painter.setPen(QPen(QColor(255, 255, 255, 150), max(1.0, taille * 0.035)))
        painter.drawLine(
            bas,
            QPointF(
                bas.x() + taille * 0.07 * echelle, bas.y() + taille * 0.1 * echelle
            ),
        )

        # --- nervures "creusées" dans la feuille (transparence) ---
        haut_nervure = QPointF(centre.x(), centre.y() - taille * 0.28 * echelle)
        bas_nervure = QPointF(centre.x(), centre.y() + taille * 0.24 * echelle)

        painter.save()
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_DestinationOut
        )

        # nervure centrale
        painter.setPen(
            QPen(
                QColor(255, 255, 255, 130),
                max(0.9, taille * 0.028),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(haut_nervure, bas_nervure)

        # nervures secondaires, en épi le long de la nervure centrale
        n_paires = 3
        for i in range(1, n_paires + 1):
            t = i / (n_paires + 1)
            point_depart = QPointF(
                haut_nervure.x(),
                haut_nervure.y() + (bas_nervure.y() - haut_nervure.y()) * t,
            )
            longueur = taille * 0.16 * echelle * (1.0 - t * 0.35)
            for signe in (-1, 1):
                point_arrivee = QPointF(
                    point_depart.x() + signe * longueur,
                    point_depart.y() + longueur * 0.55,
                )
                painter.setPen(
                    QPen(
                        QColor(255, 255, 255, 100),
                        max(0.7, taille * 0.02),
                        Qt.PenStyle.SolidLine,
                        Qt.PenCapStyle.RoundCap,
                    )
                )
                painter.drawLine(point_depart, point_arrivee)

        painter.restore()

    def _dessiner_graphique_mensuel(
        self, painter: QPainter, rect_barres: QRectF, rect_etiquettes: QRectF
    ) -> None:

        valeurs = self.historique_jours
        n = len(valeurs)

        self.points_hover = []

        if n == 0:
            return

        maximum = max(valeurs) or 1
        espace = rect_barres.width() * 0.18 / max(1, n - 1) if n > 1 else 0
        largeur_barre = (rect_barres.width() - espace * (n - 1)) / n

        police_mois = QFont("Segoe UI", max(6, int(rect_etiquettes.height() * 0.6)))
        painter.setFont(police_mois)

        painter.setPen(Qt.PenStyle.NoPen)
        for i, v in enumerate(valeurs):
            x = rect_barres.left() + i * (largeur_barre + espace)

            hauteur_pleine = rect_barres.height() * (v / maximum) if maximum else 0.0
            hauteur_pleine = max(hauteur_pleine, rect_barres.height() * 0.06)
            hauteur_barre = hauteur_pleine * self._progression_barres
            y = rect_barres.bottom() - hauteur_barre

            est_mois_courant = i == n - 1
            couleur = (
                self.theme.barre_surbrillance if est_mois_courant else self.theme.barre
            )
            painter.setBrush(QBrush(couleur))
            rect_barre = QRectF(x, y, largeur_barre, hauteur_barre)
            chemin = QPainterPath()
            chemin.addRoundedRect(
                rect_barre, largeur_barre * 0.35, largeur_barre * 0.35
            )

            self.points_hover.append(
                {
                    "rect": rect_barre,
                    "valeur": v,
                }
            )

            painter.drawPath(chemin)

            # étiquette du mois, centrée sous la barre
            if i < len(self.mois_numeros):
                numero_mois = self.mois_numeros[i]
                texte_mois = NOMS_MOIS_INITIALES[(numero_mois - 1) % 12]
                painter.setPen(
                    self.theme.sous_texte
                    if not est_mois_courant
                    else self.theme.barre_surbrillance
                )
                rect_mois = QRectF(
                    x, rect_etiquettes.top(), largeur_barre, rect_etiquettes.height()
                )
                painter.drawText(rect_mois, Qt.AlignmentFlag.AlignCenter, texte_mois)
                painter.setPen(Qt.PenStyle.NoPen)

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
