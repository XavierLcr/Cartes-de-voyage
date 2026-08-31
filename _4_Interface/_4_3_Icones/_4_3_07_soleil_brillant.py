################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.7 – Script de création d'un Soleil qui brille                            #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPen, QRadialGradient

# 1 -- Fonction de création du Soleil brillant ---------------------------------


def _dessiner_soleil(painter, centre, taille):

    # =========================================================
    # PARAMÈTRES
    # =========================================================

    rayon = taille * 0.18

    rayon_interieur = rayon + taille * 0.02
    rayon_exterieur = rayon + taille * 0.14

    # =========================================================
    # GLOW (halo doux)
    # =========================================================

    lueur = QRadialGradient(centre, taille * 0.45)
    lueur.setColorAt(0.0, QColor(255, 230, 80, 180))
    lueur.setColorAt(0.4, QColor(255, 200, 0, 80))
    lueur.setColorAt(1.0, QColor(255, 200, 0, 0))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(lueur)
    painter.drawEllipse(centre, taille * 0.45, taille * 0.45)

    # =========================================================
    # RAYONS (douce variation d'épaisseur)
    # =========================================================

    for i in range(12):

        angle = (2 * math.pi / 12) * i

        x1 = centre.x() + math.cos(angle) * rayon_interieur
        y1 = centre.y() + math.sin(angle) * rayon_interieur

        x2 = centre.x() + math.cos(angle) * rayon_exterieur
        y2 = centre.y() + math.sin(angle) * rayon_exterieur

        stylo = QPen(QColor(255, 170, 0, 180), 2)
        stylo.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(stylo)

        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    # =========================================================
    # CŒUR DU SOLEIL (gradient + léger relief)
    # =========================================================

    gradient_coeur = QRadialGradient(centre, rayon * 1.2)
    gradient_coeur.setColorAt(0.0, QColor(255, 255, 140))
    gradient_coeur.setColorAt(0.6, QColor(255, 200, 0))
    gradient_coeur.setColorAt(1.0, QColor(255, 140, 0))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient_coeur)
    painter.drawEllipse(centre, rayon, rayon)

    # =========================================================
    # BRILLANCE (petit reflet en haut à gauche)
    # =========================================================

    reflet = QPointF(centre.x() - rayon * 0.4, centre.y() - rayon * 0.4)

    painter.setBrush(QColor(255, 255, 255, 120))
    painter.drawEllipse(reflet, rayon * 0.35, rayon * 0.35)
