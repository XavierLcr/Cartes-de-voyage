################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6/onglet_4_6_1                   #
# Onglet 4.6.1.3 – Cercle de données (anneau de progression)                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------

from __future__ import annotations
import math
from typing import Tuple

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QBrush,
    QPen,
    QColor,
    QFont,
    QFontMetrics,
    QRadialGradient,
    QConicalGradient,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import _QColor_avec_alpha
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_1.onglet_4_6_1_1_theme import (
    interpoler_couleurs,
)
from _0_Utilitaires._0_2_fonctions_graphiques import renvoyer_couleur_texte

# 1 -- Classe du cercle de données ----------------------------------------------


class CercleDonnees:
    """
    Anneau de progression contenant les données (valeur, libellé,
    pourcentage) du compteur circulaire.

    Fonctionnalités :
    - Anneau à dégradé conique qui s'intensifie (couleurs plus saturées)
      à mesure que le pourcentage augmente, dans la même famille de
      couleurs que le sable du bocal voisin.
    - Petit curseur lumineux (halo + cœur blanc) à l'extrémité de l'arc.
    - Fond du disque intérieur et liseré dépendant de la palette fournie
      (peut varier selon l'heure du jour, le thème, etc. — géré en
      amont par l'appelant via `palette`).
    - Valeur centrale, libellé élidé et pourcentage dans une petite
      bulle, le tout contenu dans le cercle.
    - Halo doré optionnel autour de l'anneau (à dessiner avant l'anneau
      lui-même via `dessiner_glow`), pour signaler un niveau presque
      plein.

    Totalement sans état persistant lié au widget parent : chaque appel
    à `dessiner` reçoit tout ce dont il a besoin (rect, valeur, palette).
    """

    def __init__(
        self,
        start_angle: int = 90,
        arc_width_ratio: float = 0.10,
    ) -> None:

        # L'arc démarre en haut du cercle par défaut.
        self._angle_depart = start_angle
        # Épaisseur de l'arc / diamètre du cercle.
        self._arc_epaisseur_ratio = arc_width_ratio

    # ---------------------------------------------------------------
    # Halo "presque plein"
    # ---------------------------------------------------------------
    def dessiner_glow(
        self,
        painter: QPainter,
        cercle_rect: QRectF,
        side_cercle: float,
        palette: dict,
        glow_opacity: float,
    ) -> None:
        """Halo doré, discret, autour du cercle de données, à dessiner avant
        `dessiner` lorsque `glow_opacity` > 0 (typiquement piloté par une
        QPropertyAnimation côté widget parent)."""
        if glow_opacity <= 0:
            return
        expand = side_cercle * 0.06 * self._glow_opacity
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(
            QBrush(
                _QColor_avec_alpha(
                    self._PALETTE["cercle_tour"], alpha=0.25 * self._glow_opacity
                )
            )
        )
        painter.drawEllipse(cercle_rect.adjusted(-expand, -expand, expand, expand))

    # ---------------------------------------------------------------
    # Géométrie de l'arc
    # ---------------------------------------------------------------
    @staticmethod
    def _point_sur_arc(
        rect: QRectF, _angle_depart_deg: float, percent: float
    ) -> QPointF:
        """Calcule le point sur le cercle correspondant à l'extrémité de l'arc."""
        angle_deg = _angle_depart_deg - percent * 360.0
        angle_rad = math.radians(angle_deg)
        cx, cy = rect.center().x(), rect.center().y()
        rx, ry = rect.width() / 2, rect.height() / 2
        return QPointF(cx + rx * math.cos(angle_rad), cy - ry * math.sin(angle_rad))

    @staticmethod
    def _couleurs_intensifiees(
        palette: dict, percent: float
    ) -> Tuple[QColor, QColor, QColor]:
        """
        Renvoie 3 arrêts de couleur pour le dégradé conique de l'anneau :
        la fin de l'arc devient progressivement plus saturée/vive à mesure
        que le pourcentage augmente, pour donner une sensation de
        progression "qui s'intensifie" plutôt qu'un dégradé statique.
        Reprend le même dégradé sable que les grains du bocal.
        """
        debut = palette["progression_debut"]
        cible_fin = palette["progression_fin"]
        fin = interpoler_couleurs(
            couleurs=[debut, cible_fin],
            poids=[1 - (0.35 + 0.65 * percent), 0.35 + 0.65 * percent],
            retour="qcolor",
        )
        milieu = interpoler_couleurs(
            couleurs=[debut, fin], poids=[0.5, 0.5], retour="qcolor"
        )
        return debut, milieu, fin

    # ---------------------------------------------------------------
    # Rendu
    # ---------------------------------------------------------------
    def dessiner(
        self,
        painter: QPainter,
        cercle_rect: QRectF,
        percent: float,
        valeur: float,
        label_text: str,
        palette: dict,
    ) -> None:
        """
        Dessine l'anneau de progression complet (piste, arc, curseur,
        valeur centrale, libellé, bulle de pourcentage) dans `cercle_rect`.

        - `percent` : progression courante (0-1).
        - `valeur` : valeur brute affichée au centre (ex. nb de pays visités).
        - `label_text` : libellé sous la valeur (déjà traduit).
        - `palette` : dict de couleurs (mêmes clés que `CompteurTheme()._PALETTE`).
        """
        side_cercle = cercle_rect.width()
        arc_width = max(4.0, side_cercle * self._arc_epaisseur_ratio)
        marge = side_cercle * 0.05
        rect_arc = QRectF(
            cercle_rect.left() + marge,
            cercle_rect.top() + marge,
            cercle_rect.width() - 2 * marge,
            cercle_rect.height() - 2 * marge,
        )

        # --- fond du disque intérieur : teinte fournie par la palette ---
        rayon_interieur = rect_arc.width() / 2 - arc_width * 0.5

        gradient_fond = QRadialGradient(
            rect_arc.center() - QPointF(rayon_interieur * 0.15, rayon_interieur * 0.15),
            rayon_interieur * 1.15,
        )
        gradient_fond.setColorAt(0.0, palette["centre"])
        gradient_fond.setColorAt(1.0, palette["bord"])
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient_fond))
        painter.drawEllipse(rect_arc.center(), rayon_interieur, rayon_interieur)

        # --- fin liseré "type lune/soleil", juste sous la piste ---
        pen_rim = QPen(palette["rim"])
        pen_rim.setWidthF(max(1.0, side_cercle * 0.012))
        painter.setPen(pen_rim)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect_arc.center(), rayon_interieur, rayon_interieur)

        # --- piste (arc de fond, toujours complet) ---
        pen = QPen(palette["piste"])
        pen.setWidthF(arc_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect_arc, 0, 360 * 16)

        # --- arc de progression : dégradé sable qui s'intensifie ---
        if percent > 0:
            gradient = QConicalGradient(rect_arc.center(), self._angle_depart)
            c_debut, c_milieu, c_fin = self._couleurs_intensifiees(palette, percent)
            gradient.setColorAt(0.0, c_debut)
            gradient.setColorAt(0.55, c_milieu)
            gradient.setColorAt(1.0, c_fin)

            pen = QPen(QBrush(gradient), arc_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            span = int(360 * percent * 16)
            painter.drawArc(rect_arc, self._angle_depart * 16, -span)

            # --- petit curseur lumineux à l'extrémité de l'arc ---
            point_fin = self._point_sur_arc(rect_arc, self._angle_depart, percent)
            halo_curseur = QColor(c_fin)
            halo_curseur.setAlpha(85)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo_curseur))
            r_halo = arc_width * 0.58
            painter.drawEllipse(point_fin, r_halo, r_halo)
            painter.setBrush(QBrush(palette.get("fond", "#FFFFFF")))
            r_coeur = arc_width * 0.22
            painter.drawEllipse(point_fin, r_coeur, r_coeur)

        # --- couleurs de texte lisibles sur le fond dynamique du disque ---
        couleur_texte_dyn = QColor(
            renvoyer_couleur_texte(style=0, couleur=palette["centre"].name())
        )
        couleur_sous_texte_dyn = QColor(couleur_texte_dyn)
        couleur_sous_texte_dyn.setAlpha(160)

        # --- valeur centrale ---
        painter.setPen(couleur_texte_dyn)
        police_valeur = QFont(
            "Segoe UI", max(9, int(side_cercle * 0.19)), QFont.Weight.Bold
        )
        painter.setFont(police_valeur)
        valeur_str = f"{int(round(valeur))}"
        rect_valeur = rect_arc.adjusted(0, -side_cercle * 0.07, 0, -side_cercle * 0.07)
        painter.drawText(rect_valeur, Qt.AlignmentFlag.AlignCenter, valeur_str)

        # --- légende, élidée pour rester dans le cercle ---
        police_etiquette = QFont("Segoe UI", max(6, int(side_cercle * 0.065)))
        fm_etiquette = QFontMetrics(police_etiquette)
        largeur_dispo = rect_arc.width() * 0.86
        texte_etiquette = fm_etiquette.elidedText(
            label_text, Qt.TextElideMode.ElideRight, int(largeur_dispo)
        )
        painter.setPen(couleur_sous_texte_dyn)
        painter.setFont(police_etiquette)
        rect_etiquette = rect_arc.adjusted(0, side_cercle * 0.15, 0, side_cercle * 0.15)
        painter.drawText(rect_etiquette, Qt.AlignmentFlag.AlignCenter, texte_etiquette)

        # --- pourcentage dans une petite bulle ---
        pct_texte = f"{int(round(percent * 100))} %"
        police_pct = QFont(
            "Segoe UI", max(6, int(side_cercle * 0.055)), QFont.Weight.DemiBold
        )
        painter.setFont(police_pct)
        fm = painter.fontMetrics()
        largeur_bulle = fm.horizontalAdvance(pct_texte) + side_cercle * 0.06
        hauteur_bulle = fm.height() * 1.2
        rect_bulle = QRectF(0, 0, largeur_bulle, hauteur_bulle)
        rect_bulle.moveCenter(
            QPointF(rect_arc.center().x(), rect_arc.center().y() + side_cercle * 0.28)
        )

        chemin_bulle = QPainterPath()
        chemin_bulle.addRoundedRect(rect_bulle, hauteur_bulle / 2, hauteur_bulle / 2)
        couleur_bulle = QColor(palette["progression_debut"])
        couleur_bulle.setAlpha(30)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(couleur_bulle))
        painter.drawPath(chemin_bulle)

        painter.setPen(palette["progression_debut"])
        painter.drawText(rect_bulle, Qt.AlignmentFlag.AlignCenter, pct_texte)
