################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6                                #
# Onglet 4.6.4 – Continent favori                                              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
from typing import Dict, Optional, Tuple

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    Qt,
    pyqtProperty,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
)
from PyQt6.QtWidgets import (
    QSizePolicy,
    QWidget,
)

from _0_Utilitaires._0_1_fonctions_utiles_gen import voyages_vers_destinations
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import ombre_onglet_4_6
from _0_Utilitaires._0_07_fonctions_voyages import table_pays_visites
from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)
from _4_Interface._4_3_Icones._4_3_05_globe_terrestre import _dessiner_badge_globe

# 1 -- Répartition des pays visités par continent -----------------------------


def repartition_continents_depuis_table(
    df_pays_visites,
) -> Tuple[Dict[str, int], Optional[str], int, Dict[str, int]]:
    """
    Calcule la répartition des pays visités par continent.

    Les noms de continents restent dans leur forme de référence (anglais)
    dans les données retournées. La traduction est uniquement effectuée
    lors de l'affichage.

    Renvoie (compte_visites, continent_favori, total_visites, compte_total) :
    - compte_visites : dict {continent (EN): nombre de pays visités}.
    - continent_favori : nom (EN) du continent avec le plus de pays visités.
    - total_visites : nombre total de pays visités.
    - compte_total : dict {continent (EN): nombre total de pays}.
    """
    if df_pays_visites is None or df_pays_visites.empty:
        return {}, None, 0, {}

    df_temp = (
        df_pays_visites.copy()
        .groupby("continent")["visite"]
        .agg(visites="sum", total="count")
        .assign(
            pct_pays=lambda x: x["visites"] / x["total"],
        )
    )

    # IMPORTANT :
    # On conserve les noms anglais comme clés internes.
    # La traduction sera faite uniquement lors de l'affichage.

    compte_total = df_temp["total"].to_dict()

    compte_visites = (
        df_temp.loc[df_temp["visites"] > 0, "visites"].astype(int).to_dict()
    )

    if not compte_visites:
        return {}, None, 0, compte_total

    favori = max(
        compte_visites,
        key=compte_visites.get,
    )

    total_visites = sum(compte_visites.values())

    return compte_visites, favori, total_visites, compte_total


# 2 -- Classe de création des couleurs -----------------------------------------


class ThemeContinentFavori:
    """
    Palette de couleurs de la carte "Continent favori".

    La couleur du badge est directement dérivée du continent favori.
    Chaque continent possède sa propre couleur, avec deux niveaux
    d'opacité pour le début et la fin du dégradé.
    """

    continents_couleurs = {
        "Africa": "#D4C220",
        "Antarctica": "#A7C9E6",
        "Asia": "#EE211E",
        "Europe": "#9A0EE6",
        "North America": "#1310CE",
        "Oceania": "#1EC3CF",
        "South America": "#23E958",
    }

    def __init__(
        self,
        style,
        continent_favori: Optional[str] = None,
        teinte=[i / 360 for i in range(0, 360, 45)],
        nuances={
            "min_luminosite": 0.8,
            "max_luminosite": 0.95,
            "min_saturation": 0.2,
            "max_saturation": 0.4,
        },
        limite_essais=20,
    ):
        # Fond de carte : identique aux trois autres widgets.
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

        self.sous_texte = QColor(self.texte)
        self.sous_texte.setAlpha(140)

        # Barres "normales" du classement : dérivées du texte, très diluées.
        self.barre = QColor(self.texte)
        self.barre.setAlpha(30 if style == 1 else 25)

        # ------------------------------------------------------------------
        # Couleur du continent favori
        # ------------------------------------------------------------------

        couleur_continent = self.continents_couleurs.get(
            continent_favori,
            "#10B981",
        )

        self.couleur_continent = QColor(couleur_continent)

        # Badge : même couleur que le continent favori, avec deux niveaux
        # d'alpha pour créer un dégradé doux.
        self.badge_debut = QColor(self.couleur_continent)
        self.badge_debut.setAlpha(100)

        self.badge_fin = QColor(self.couleur_continent)
        self.badge_fin.setAlpha(190)

        # Barre du continent favori, mise en avant.
        self.barre_surbrillance = QColor(self.couleur_continent)
        self.barre_surbrillance.setAlpha(220)

        # Couleurs utilisées par le globe.
        self.globe_debut = QColor(self.couleur_continent)
        self.globe_debut.setAlpha(120)

        self.globe_fin = QColor(self.couleur_continent)
        self.globe_fin.setAlpha(210)


# 3 -- Classe du widget ---------------------------------------------------------


class ContinentFavoriWidget(QWidget):
    """
    Carte "Continent favori" : nom du continent avec le plus de pays
    visités, avec le pourcentage de pays visités qu'il représente, et un
    classement en barres horizontales de tous les continents concernés.

    Alimenté via `set_voyages(df_pays_visites)`, où `df_pays_visites` est
    le DataFrame renvoyé par la fonction existante `table_pays_visites`
    (colonnes "continent", "pays", "visite").

    Reprend le vocabulaire visuel des trois autres widgets du tableau de
    bord (carte à coins arrondis, même ombre, même typographie).
    """

    def __init__(
        self,
        fonction_traduction,
        constantes,
        repartition: Optional[Dict[str, int]] = None,
        continent_favori: Optional[str] = None,
        parent: Optional[QWidget] = None,
        duree_animation: int = 1000,
    ) -> None:
        super().__init__(parent)

        self.table_pays_visites = None
        self.fonction_traduction = fonction_traduction
        self.traductions_pays = constantes.pays_differentes_langues
        self.repartition: Dict[str, int] = dict(repartition) if repartition else {}
        self.continent_favori: Optional[str] = continent_favori
        self._pourcentage = 0.0
        self.pourcentage_cible = 0.0
        self._progression_barres = 0.0
        self.duree_animation = duree_animation * 1  # ms
        self.valeur_claire = constantes.parametres_application.get("transparence_alpha")
        self.continents = constantes.liste_regions_monde

        self.theme = ThemeContinentFavori(
            style=1,
            continent_favori=self.continent_favori,
        )

        self.setMinimumSize(320, 130)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._animation_pourcentage = QPropertyAnimation(
            self,
            b"valeurAnimee",
            self,
        )
        self._animation_pourcentage.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._animation_barres = QPropertyAnimation(
            self,
            b"progressionBarres",
            self,
        )
        self._animation_barres.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation_barres.setStartValue(0.0)
        self._animation_barres.setEndValue(1.0)

        self._recalculer_pourcentage(animer=False)
        self.definir_repartition(
            self.repartition,
            self.continent_favori,
            animer=False,
        )
        self.set_langue(langue="français")

    # ---------------------------------------------------------------
    # Propriétés animables Qt
    # ---------------------------------------------------------------

    def _obtenir_valeur_animee(self) -> float:
        return self._pourcentage

    def _definir_valeur_animee(self, v: float) -> None:
        self._pourcentage = v
        self.update()

    valeurAnimee = pyqtProperty(
        float,
        _obtenir_valeur_animee,
        _definir_valeur_animee,
    )

    def _obtenir_progression_barres(self) -> float:
        return self._progression_barres

    def _definir_progression_barres(self, v: float) -> None:
        self._progression_barres = v
        self.update()

    progressionBarres = pyqtProperty(
        float,
        _obtenir_progression_barres,
        _definir_progression_barres,
    )

    # ---------------------------------------------------------------
    # API publique
    # ---------------------------------------------------------------

    def definir_repartition(
        self,
        repartition: Dict[str, int],
        continent_favori: Optional[str] = None,
        animer: bool = True,
    ) -> None:
        """Remplace la répartition par continent affichée dans le classement."""

        self.repartition = dict(repartition)

        self.continent_favori = continent_favori or (
            max(self.repartition, key=self.repartition.get)
            if self.repartition
            else None
        )

        # La couleur du thème dépend maintenant du continent favori.
        # On la reconstruit à chaque changement de favori.
        self.theme = ThemeContinentFavori(
            style=1,
            continent_favori=self.continent_favori,
        )

        self._animation_barres.stop()
        self._animation_barres.setDuration(self.duree_animation if animer else 0)
        self._progression_barres = 0.0 if animer else 1.0
        self._animation_barres.start()

        self._recalculer_pourcentage(animer=animer)
        self.update()

    def _recalculer_pourcentage(self, animer: bool = True) -> None:
        total = sum(self.repartition.values())

        if total and self.continent_favori:
            pourcentage = 100.0 * self.repartition.get(self.continent_favori, 0) / total
        else:
            pourcentage = 0.0

        self.pourcentage_cible = pourcentage

        self._animation_pourcentage.stop()
        self._animation_pourcentage.setDuration(self.duree_animation if animer else 0)
        self._animation_pourcentage.setStartValue(self._pourcentage)
        self._animation_pourcentage.setEndValue(pourcentage)
        self._animation_pourcentage.start()

    def set_langue(self, langue):
        """Mise à jour de la langue."""
        self.langue = langue
        self.set_valeurs()
        self.update()

    def set_style(self, style, nuances, teintes):
        self.theme = ThemeContinentFavori(
            style=style,
            continent_favori=self.continent_favori,
            nuances=nuances,
            teinte=teintes,
            limite_essais=20,
        )

        self.setGraphicsEffect(ombre_onglet_4_6(style=style, parent=self))
        self.update()

    def set_voyages(self, voyages) -> None:
        """
        Reçoit la table renvoyée par `table_pays_visites` (colonnes
        "continent", "pays", "visite") et met à jour le classement ainsi
        que le continent favori.
        """
        self.table_pays_visites = table_pays_visites(
            voyages_vers_destinations(dict_voyages=voyages),
            continents=self.continents,
            palette={},
        )[["continent", "pays", "visite"]]

        self.set_valeurs()

    def set_valeurs(self) -> None:
        repartition, favori, _total, _compte_total = (
            repartition_continents_depuis_table(self.table_pays_visites)
        )

        self.definir_repartition(
            repartition,
            favori,
        )

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
        rayon = min(24, min(w, h) * 0.12)

        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(
            rect_carte,
            rayon,
            rayon,
        )

        painter.fillPath(
            chemin_carte,
            QBrush(self.theme.fond),
        )
        painter.setClipPath(chemin_carte)

        marge = w * 0.055
        taille_badge = h * 0.235

        # --- badge (icône globe) ---
        rect_badge = QRectF(
            marge,
            h * 0.06,
            taille_badge,
            taille_badge,
        )

        _dessiner_badge_globe(
            painter,
            rect_badge,
            badge_debut=self.theme.globe_debut,
            badge_fin=self.theme.globe_fin,
        )

        # --- zone texte à droite du badge ---
        x_texte = rect_badge.right() + marge * 0.8
        largeur_texte = w - x_texte - marge

        nom_continent = (
            self.traductions_pays.get(self.continent_favori, {}).get(
                self.langue, self.continent_favori
            )
            if self.continent_favori
            else "—"
        )

        police_valeur = self._police_ajustee(
            painter,
            nom_continent,
            largeur_texte,
            taille_pt_max=max(11, int(h * 0.11)),
        )

        painter.setFont(police_valeur)
        painter.setPen(self.theme.texte)

        rect_valeur = QRectF(
            x_texte,
            h * 0.045,
            largeur_texte,
            h * 0.18,
        )

        painter.drawText(
            rect_valeur,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            nom_continent,
        )

        police_etiquette = QFont(
            "Segoe UI",
            max(7, int(h * 0.06)),
        )

        painter.setFont(police_etiquette)
        painter.setPen(self.theme.sous_texte)

        rect_etiquette = QRectF(
            x_texte,
            h * 0.22,
            largeur_texte,
            h * 0.10,
        )

        painter.drawText(
            rect_etiquette,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.fonction_traduction("4_6_5_continent_favori"),
        )

        # --- bulle de pourcentage ---
        if self.continent_favori is not None:
            self._dessiner_bulle_pourcentage(
                painter,
                QRectF(
                    x_texte,
                    h * 0.33,
                    largeur_texte,
                    h * 0.12,
                ),
            )

        # --- classement en barres horizontales ---
        rect_classement = QRectF(
            marge,
            h * 0.52,
            w - 2 * marge,
            h * 0.42,
        )

        self._dessiner_classement(
            painter,
            rect_classement,
        )

    def _police_ajustee(
        self,
        painter: QPainter,
        texte: str,
        largeur_max: float,
        taille_pt_max: int,
        taille_pt_min: int = 9,
    ) -> QFont:
        """Réduit la taille de police jusqu'à ce que le texte tienne sur une ligne."""

        taille_pt = taille_pt_max

        police = QFont(
            "Segoe UI",
            taille_pt,
            QFont.Weight.Bold,
        )

        painter.setFont(police)

        largeur_texte = painter.fontMetrics().horizontalAdvance(texte)

        while largeur_texte > largeur_max and taille_pt > taille_pt_min:
            taille_pt -= 1
            police.setPointSize(taille_pt)
            painter.setFont(police)
            largeur_texte = painter.fontMetrics().horizontalAdvance(texte)

        return police

    def _dessiner_bulle_pourcentage(
        self,
        painter: QPainter,
        zone: QRectF,
    ) -> None:
        """Petite pastille : "42 % des pays visités"."""

        texte = f"{int(round(self._pourcentage))} % " + self.fonction_traduction(
            "4_6_4_pays_visites"
        )

        police = QFont(
            "Segoe UI",
            max(6, int(zone.height() * 0.55)),
            QFont.Weight.DemiBold,
        )

        painter.setFont(police)

        fm = painter.fontMetrics()

        largeur_bulle = min(
            zone.width(),
            fm.horizontalAdvance(texte) + zone.height() * 0.7,
        )

        hauteur_bulle = zone.height() * 0.85

        rect_bulle = QRectF(
            0,
            0,
            largeur_bulle,
            hauteur_bulle,
        )

        rect_bulle.moveLeft(zone.left())
        rect_bulle.moveTop(zone.top() + (zone.height() - hauteur_bulle) / 2)

        chemin_bulle = QPainterPath()
        chemin_bulle.addRoundedRect(
            rect_bulle,
            hauteur_bulle / 2,
            hauteur_bulle / 2,
        )

        couleur_bulle = QColor(self.theme.badge_debut)
        couleur_bulle.setAlpha(28)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(couleur_bulle))
        painter.drawPath(chemin_bulle)

        painter.setPen(self.theme.barre_surbrillance)

        painter.drawText(
            rect_bulle,
            Qt.AlignmentFlag.AlignCenter,
            texte,
        )

    def _dessiner_classement(
        self,
        painter: QPainter,
        zone: QRectF,
    ) -> None:
        """Classement en barres horizontales de tous les continents visités."""

        if not self.repartition:
            painter.setPen(self.theme.sous_texte)

            police = QFont(
                "Segoe UI",
                max(7, int(zone.height() * 0.09)),
            )

            painter.setFont(police)

            painter.drawText(
                zone,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                (
                    self.fonction_traduction("4_6_5_aucun_continent")
                    if self._traduction_disponible("4_6_5_aucun_continent")
                    else "Aucun pays visité pour l'instant"
                ),
            )

            return

        continents_tries = sorted(
            self.repartition.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        n = len(continents_tries)
        maximum = continents_tries[0][1] or 1
        hauteur_ligne = zone.height() / n

        largeur_etiquette = zone.width() * 0.34
        largeur_valeur = zone.width() * 0.08

        x_barre = zone.left() + largeur_etiquette

        largeur_barre_max = zone.width() - largeur_etiquette - largeur_valeur

        for i, (continent, compte) in enumerate(continents_tries):
            y = zone.top() + i * hauteur_ligne

            est_favori = continent == self.continent_favori

            couleur = self.theme.barre_surbrillance if est_favori else self.theme.barre

            couleur_texte = self.theme.texte if est_favori else self.theme.sous_texte

            nom_continent = self.traductions_pays.get(
                continent,
                {},
            ).get(
                self.langue,
                continent,
            )

            # étiquette du continent
            police_nom = QFont(
                "Segoe UI",
                max(6, int(hauteur_ligne * 0.34)),
                (QFont.Weight.DemiBold if est_favori else QFont.Weight.Normal),
            )

            painter.setFont(police_nom)
            painter.setPen(couleur_texte)

            rect_nom = QRectF(
                zone.left(),
                y,
                largeur_etiquette - hauteur_ligne * 0.1,
                hauteur_ligne,
            )

            painter.drawText(
                rect_nom,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                nom_continent,
            )

            # barre
            largeur_barre = (
                largeur_barre_max * (compte / maximum) * self._progression_barres
            )

            largeur_barre = (
                max(
                    largeur_barre,
                    hauteur_ligne * 0.25,
                )
                if self._progression_barres > 0
                else 0
            )

            hauteur_barre = hauteur_ligne * 0.42

            rect_barre = QRectF(
                x_barre,
                y + (hauteur_ligne - hauteur_barre) / 2,
                largeur_barre,
                hauteur_barre,
            )

            chemin_barre = QPainterPath()

            chemin_barre.addRoundedRect(
                rect_barre,
                hauteur_barre / 2,
                hauteur_barre / 2,
            )

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(couleur))
            painter.drawPath(chemin_barre)

            # valeur numérique
            police_valeur = QFont(
                "Segoe UI",
                max(6, int(hauteur_ligne * 0.32)),
                (QFont.Weight.DemiBold if est_favori else QFont.Weight.Normal),
            )

            painter.setFont(police_valeur)
            painter.setPen(couleur_texte)

            rect_valeur = QRectF(
                zone.right() - largeur_valeur,
                y,
                largeur_valeur,
                hauteur_ligne,
            )

            painter.drawText(
                rect_valeur,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                str(compte),
            )

    def _traduction_disponible(self, cle: str) -> bool:
        try:
            texte = self.fonction_traduction(cle)
        except Exception:
            return False

        return bool(texte) and texte != cle

    def relancer_animation(self):
        self._animation_barres.stop()
        self._animation_barres.setStartValue(0.0)
        self._animation_barres.setEndValue(1.0)
        self._animation_barres.setDuration(self.duree_animation)
        self._animation_barres.start()

        self._animation_pourcentage.stop()
        self._animation_pourcentage.setStartValue(0.0)
        self._animation_pourcentage.setEndValue(self.pourcentage_cible)
        self._animation_pourcentage.setDuration(self.duree_animation)
        self._animation_pourcentage.start()
