################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.33 – Script de création de l'icône d'uncoquillage                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_coquillage(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    fond: QColor,
    trait: QColor,
    angle_deg: float = 0.0,
) -> None:
    """Petit coquillage stylisé (forme en éventail, façon coquille
    Saint-Jacques) : dôme cannelé avec une charnière en bas."""
    painter.save()
    painter.translate(centre)
    painter.rotate(angle_deg)

    largeur = taille * 2.0
    hauteur = taille * 1.15
    rect = QRectF(-largeur / 2, -hauteur, largeur, hauteur)

    chemin = QPainterPath()
    chemin.moveTo(-largeur / 2, 0)
    chemin.arcTo(rect, 180, 180)
    chemin.closeSubpath()

    pen = QPen(trait)
    pen.setWidthF(max(0.6, taille * 0.07))
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(QBrush(fond))
    painter.drawPath(chemin)

    nb_cannelures = 7
    for i in range(nb_cannelures):
        t = i / (nb_cannelures - 1)
        ang = math.radians(180 - 180 * t)
        bord = QPointF(math.cos(ang) * largeur / 2, -math.sin(ang) * hauteur)
        painter.drawLine(QPointF(0, 0), bord)

    painter.restore()
