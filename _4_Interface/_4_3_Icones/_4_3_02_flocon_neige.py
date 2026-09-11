################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.2 – Script de création de l'icône d'un flocon de neige                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen

# 1 -- Fonction de création du flocon de neige ---------------------------------


def _dessiner_icone_flocon(painter: QPainter, centre: QPointF, taille: float) -> None:
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
