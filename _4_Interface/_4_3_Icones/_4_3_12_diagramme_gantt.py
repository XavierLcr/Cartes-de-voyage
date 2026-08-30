################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.12 – Script de création d'un diagramme de Gantt miniature                #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QRadialGradient,
    QLinearGradient,
)

# 1 -- Fonction de création du diagramme -----------------------------------------


def _dessiner_icone_gantt(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône diagramme de Gantt : 4 barres de tâches fines et glossy, à des
    positions et durées variées, sur une ligne de base discrète (et non plus
    une piste pleine qui les faisait ressembler à des sliders). Un repère
    vertical "aujourd'hui" traverse les rangées. Même esprit que les autres
    icônes : dégradés doux, ombre portée, reflet glossy."""

    COULEURS_BARRES = [
        QColor("#5B8DEF"),
        QColor("#F2A65A"),
        QColor("#4FBDBA"),
        QColor("#E9647B"),
    ]
    COULEUR_LIGNE_BASE = QColor("#C4CAD4")
    COULEUR_MARQUEUR = QColor("#4A5568")

    # (début, durée) en fraction de la largeur totale de la piste
    BARRES = [
        (0.00, 0.50),
        (0.22, 0.40),
        (0.10, 0.65),
        (0.38, 0.35),
    ]

    cx, cy = centre.x(), centre.y()
    zone_largeur = taille * 0.74
    zone_gauche = cx - zone_largeur / 2
    zone_hauteur = taille * 0.58
    zone_haut = cy - zone_hauteur / 2
    hauteur_barre = taille * 0.062
    rayon_arrondi = hauteur_barre / 2
    nb_lignes = len(BARRES)
    espacement = zone_hauteur / (nb_lignes - 1)

    # -- Ombre douce sous toute la composition -----------------------------------
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setPen(Qt.PenStyle.NoPen)
    ombre = QRadialGradient(
        QPointF(cx, zone_haut + zone_hauteur + taille * 0.10), taille * 0.4
    )
    ombre.setColorAt(0.0, QColor(0, 0, 0, 40))
    ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.setBrush(QBrush(ombre))
    painter.drawEllipse(
        QPointF(cx, zone_haut + zone_hauteur + taille * 0.08),
        taille * 0.34,
        taille * 0.06,
    )

    # -- Lignes de base discrètes (fine ligne, pas une piste pleine) -------------
    pen_ligne_base = QPen(COULEUR_LIGNE_BASE)
    pen_ligne_base.setWidthF(taille * 0.012)
    pen_ligne_base.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_ligne_base)
    for i in range(nb_lignes):
        y_centre = zone_haut + i * espacement
        painter.drawLine(
            QPointF(zone_gauche, y_centre),
            QPointF(zone_gauche + zone_largeur, y_centre),
        )

    # -- Barres de tâches, fines et glossy ----------------------------------------
    for i, (debut, duree) in enumerate(BARRES):
        y_centre = zone_haut + i * espacement
        y_haut = y_centre - hauteur_barre / 2
        x_gauche_barre = zone_gauche + debut * zone_largeur
        largeur_barre = duree * zone_largeur
        rect_barre = QRectF(x_gauche_barre, y_haut, largeur_barre, hauteur_barre)

        couleur = COULEURS_BARRES[i % len(COULEURS_BARRES)]
        degrade_barre = QLinearGradient(
            x_gauche_barre, y_haut, x_gauche_barre, y_haut + hauteur_barre
        )
        degrade_barre.setColorAt(0.0, couleur.lighter(130))
        degrade_barre.setColorAt(1.0, couleur.darker(110))

        pen_contour = QPen(couleur.darker(130))
        pen_contour.setWidthF(taille * 0.004)
        painter.setPen(pen_contour)
        painter.setBrush(QBrush(degrade_barre))
        painter.drawRoundedRect(rect_barre, rayon_arrondi, rayon_arrondi)

        # Reflet glossy sur le dessus de la barre
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 100)))
        painter.drawRoundedRect(
            QRectF(
                x_gauche_barre + hauteur_barre * 0.15,
                y_haut + hauteur_barre * 0.10,
                max(largeur_barre - hauteur_barre * 0.3, hauteur_barre * 0.2),
                hauteur_barre * 0.32,
            ),
            rayon_arrondi * 0.5,
            rayon_arrondi * 0.5,
        )

    # -- Repère vertical "aujourd'hui" traversant les rangées ---------------------
    x_marqueur = zone_gauche + 0.66 * zone_largeur
    y1 = zone_haut - hauteur_barre * 0.9
    y2 = zone_haut + zone_hauteur + hauteur_barre * 0.9

    pen_marqueur = QPen(COULEUR_MARQUEUR)
    pen_marqueur.setWidthF(taille * 0.013)
    pen_marqueur.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen_marqueur.setStyle(Qt.PenStyle.CustomDashLine)
    pen_marqueur.setDashPattern([1, 1.6])
    painter.setPen(pen_marqueur)
    painter.drawLine(QPointF(x_marqueur, y1), QPointF(x_marqueur, y2))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_MARQUEUR))
    painter.drawEllipse(QPointF(x_marqueur, y1), taille * 0.022, taille * 0.022)
