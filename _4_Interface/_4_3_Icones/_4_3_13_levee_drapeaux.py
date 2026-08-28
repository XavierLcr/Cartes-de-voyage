################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.13 – Script de création d'e petits drapeaux                              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QPolygonF

# 1 -- Classe de création de l'icône -------------------------------------------


def _dessiner_icone_drapeaux(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône "pays les plus visités" : mâts de hauteurs variables
    (proportionnelles au nombre de visites) surmontés de fanions colorés,
    façon petit classement en barres, posés sur une ligne de sol."""

    COULEURS_DRAPEAUX = [
        QColor("#FC2E2E"),
        QColor("#39EFFC"),
        QColor("#FD3FDD"),
        QColor("#6EFF49"),
    ]
    COULEUR_MAT = QColor("#5C5C5C")
    COULEUR_SOL = QColor("#8A94A6")

    # Hauteurs relatives des mâts (1.0 = pays le plus visité)
    # → à remplacer dynamiquement par les données réelles de visites
    HAUTEURS_RELATIVES = [1.0, 0.78, 0.58, 0.40]

    cx, cy = centre.x(), centre.y()
    nb_mats = len(HAUTEURS_RELATIVES)
    zone_largeur = taille * 0.72
    x_gauche = cx - zone_largeur / 2
    espace_x = zone_largeur / (nb_mats - 1) if nb_mats > 1 else 0

    y_base = cy + taille * 0.28
    hauteur_max_mat = taille * 0.56
    epaisseur_mat = taille * 0.025
    largeur_drapeau = taille * 0.15
    hauteur_drapeau = taille * 0.115

    # Ligne de sol
    pen_sol = QPen(COULEUR_SOL)
    pen_sol.setWidthF(taille * 0.014)
    pen_sol.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_sol)
    painter.setOpacity(0.35)
    painter.drawLine(
        QPointF(x_gauche - taille * 0.06, y_base),
        QPointF(x_gauche + zone_largeur + taille * 0.06, y_base),
    )
    painter.setOpacity(1.0)

    for i, ratio in enumerate(HAUTEURS_RELATIVES):
        x = x_gauche + i * espace_x
        hauteur_mat = hauteur_max_mat * ratio
        y_sommet = y_base - hauteur_mat

        # Mât
        pen_mat = QPen(COULEUR_MAT)
        pen_mat.setWidthF(epaisseur_mat)
        pen_mat.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_mat)
        painter.drawLine(QPointF(x, y_base), QPointF(x, y_sommet))

        # Fanion triangulaire flottant vers la droite
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(COULEURS_DRAPEAUX[i % len(COULEURS_DRAPEAUX)]))
        drapeau = QPolygonF(
            [
                QPointF(x, y_sommet),
                QPointF(x + largeur_drapeau, y_sommet + hauteur_drapeau * 0.5),
                QPointF(x, y_sommet + hauteur_drapeau),
            ]
        )
        painter.drawPolygon(drapeau)
