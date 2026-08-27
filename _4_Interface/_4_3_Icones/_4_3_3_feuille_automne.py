################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.3 – Script de création de l'icône d'une feuille à l'automne              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen

# 1 -- Fonction de création de la feuille --------------------------------------


def _dessiner_icone_feuille(painter: QPainter, centre: QPointF, taille: float) -> None:
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
        QPointF(bas.x() + taille * 0.07 * echelle, bas.y() + taille * 0.1 * echelle),
    )

    # --- nervures "creusées" dans la feuille (transparence) ---
    haut_nervure = QPointF(centre.x(), centre.y() - taille * 0.28 * echelle)
    bas_nervure = QPointF(centre.x(), centre.y() + taille * 0.24 * echelle)

    painter.save()
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOut)

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
