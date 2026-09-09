################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.32 – Script de création de l'icône d'une étoile de mer                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_etoile_mer(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    fond: QColor,
    trait: QColor,
    angle_deg: float = 0.0,
) -> None:
    """Petite étoile de mer stylisée à 5 branches."""
    painter.save()
    painter.translate(centre)
    painter.rotate(angle_deg)

    branches = 5
    rayon_ext = taille
    rayon_int = taille * 0.42

    chemin = QPainterPath()
    for i in range(branches * 2):
        ang = math.pi * i / branches - math.pi / 2
        r = rayon_ext if i % 2 == 0 else rayon_int
        pt = QPointF(math.cos(ang) * r, math.sin(ang) * r)
        if i == 0:
            chemin.moveTo(pt)
        else:
            chemin.lineTo(pt)
    chemin.closeSubpath()

    pen = QPen(trait)
    pen.setWidthF(max(0.6, taille * 0.07))
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(QBrush(fond))
    painter.drawPath(chemin)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(trait))
    for i in range(branches):
        ang = math.tau * i / branches - math.pi / 2
        pt = QPointF(math.cos(ang) * rayon_ext * 0.6, math.sin(ang) * rayon_ext * 0.6)
        painter.drawEllipse(pt, taille * 0.05, taille * 0.05)

    painter.restore()
