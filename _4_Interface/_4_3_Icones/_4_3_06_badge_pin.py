################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.6 – Script de création d'un pin                                          #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath

# 1 -- Fonction de création du bagde -------------------------------------------


def _dessiner_badge_pin(
    painter: QPainter, rect: QRectF, badge_debut, badge_fin
) -> None:
    """Badge circulaire dégradé avec une icône de pin de destination."""
    degrade = QLinearGradient(rect.topLeft(), rect.bottomRight())
    degrade.setColorAt(0.0, badge_debut)
    degrade.setColorAt(1.0, badge_fin)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(degrade))
    painter.drawEllipse(rect)

    # icône : pin (tête ronde + pointe), dessinée au centre du badge
    cx, cy = rect.center().x(), rect.center().y()
    s = rect.width()  # échelle de référence

    chemin_pin = QPainterPath()
    rayon_tete = s * 0.20
    cy_tete = cy - s * 0.08
    chemin_pin.addEllipse(
        QRectF(cx - rayon_tete, cy_tete - rayon_tete, rayon_tete * 2, rayon_tete * 2)
    )

    pointe = (cx, cy + s * 0.28)
    gauche = (cx - rayon_tete * 0.85, cy_tete + rayon_tete * 0.55)
    droite = (cx + rayon_tete * 0.85, cy_tete + rayon_tete * 0.55)
    triangle = QPainterPath()
    triangle.moveTo(*gauche)
    triangle.lineTo(*pointe)
    triangle.lineTo(*droite)
    triangle.closeSubpath()
    chemin_pin = chemin_pin.united(triangle)

    painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
    painter.drawPath(chemin_pin)

    # petit trou au centre de la tête du pin
    rayon_trou = rayon_tete * 0.4
    painter.setBrush(QBrush(badge_debut))
    painter.drawEllipse(
        QRectF(cx - rayon_trou, cy_tete - rayon_trou, rayon_trou * 2, rayon_trou * 2)
    )
