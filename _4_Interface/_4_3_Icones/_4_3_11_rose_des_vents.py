################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.11 – Script de création d'une rose des vents                             #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QPolygonF

# 1 -- Classe de création de la rose des vents ---------------------------------


def _dessiner_icone_rose_vents(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône boussole (rose des vents) : étoile à 4 branches en effet
    pinwheel (chaque branche = un triangle clair + un triangle sombre),
    cercle de contour, et repère coloré marquant le nord."""

    COULEUR_TEINTE_CLAIRE = QColor("#98C1D9")
    COULEUR_TEINTE_SOMBRE = QColor("#3D5A80")
    COULEUR_CERCLE = QColor("#3D5A80")
    COULEUR_NORD = QColor("#EE6C4D")
    COULEUR_CENTRE = QColor("#293241")

    cx, cy = centre.x(), centre.y()
    rayon_cercle = taille * 0.44
    rayon_long = taille * 0.40
    rayon_court = taille * 0.15
    rayon_centre = taille * 0.035
    rayon_pointe_nord = taille * 0.03

    def point_angle(angle_deg: float, rayon: float) -> QPointF:
        # 0° = nord (en haut), sens horaire
        angle_rad = math.radians(angle_deg - 90)
        return QPointF(
            cx + math.cos(angle_rad) * rayon, cy + math.sin(angle_rad) * rayon
        )

    # Cercle extérieur (contour fin)
    pen_cercle = QPen(COULEUR_CERCLE)
    pen_cercle.setWidthF(taille * 0.018)
    pen_cercle.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_cercle)
    painter.setOpacity(0.5)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(centre, rayon_cercle, rayon_cercle)
    painter.setOpacity(1.0)

    # Étoile à 4 branches (N, E, S, O), chaque branche divisée en 2 triangles
    # ombrés différemment pour un effet de relief "pinwheel"
    painter.setPen(Qt.PenStyle.NoPen)
    for angle_pointe in (0, 90, 180, 270):
        pointe = point_angle(angle_pointe, rayon_long)
        cote_gauche = point_angle(angle_pointe - 45, rayon_court)
        cote_droit = point_angle(angle_pointe + 45, rayon_court)

        painter.setBrush(QBrush(COULEUR_TEINTE_CLAIRE))
        painter.drawPolygon(QPolygonF([centre, cote_gauche, pointe]))

        painter.setBrush(QBrush(COULEUR_TEINTE_SOMBRE))
        painter.drawPolygon(QPolygonF([centre, pointe, cote_droit]))

    # Repère coloré à la pointe nord (convention boussole)
    pointe_nord = point_angle(0, rayon_long)
    painter.setBrush(QBrush(COULEUR_NORD))
    painter.drawEllipse(pointe_nord, rayon_pointe_nord, rayon_pointe_nord)

    # Point central
    painter.setBrush(QBrush(COULEUR_CENTRE))
    painter.drawEllipse(centre, rayon_centre, rayon_centre)
