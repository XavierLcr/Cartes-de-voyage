################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.1 – Script de création de l'icône d'un Soleil souriant                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math

from PyQt6.QtCore import QRectF, Qt, QPointF
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPen

# 1 -- Fonction de création du Soleil souriant ---------------------------------


def _dessiner_icone_soleil(painter: QPainter, centre: QPointF, taille: float) -> None:
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
