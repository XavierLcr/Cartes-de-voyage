################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.8 – Script de création de la Lune selon sa phrase                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math, random

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QRadialGradient

# 1 -- Fonction de création de la Lune selon sa phase --------------------------


def _dessiner_lune(painter, centre, taille, phase=0.25):
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    rayon = taille * 0.3

    # =========================================================
    # 1. Base lune (gradient doux = essentiel)
    # =========================================================
    base = QRadialGradient(centre - QPointF(rayon * 0.2, rayon * 0.2), rayon * 1.2)

    base.setColorAt(0.0, QColor(255, 255, 255))
    base.setColorAt(0.6, QColor(235, 235, 240))
    base.setColorAt(1.0, QColor(190, 190, 200))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(base)
    painter.drawEllipse(centre, rayon, rayon)

    # =========================================================
    # 2. Ombre de phase (propre et douce)
    # =========================================================
    illumination = (1 - math.cos(2 * math.pi * phase)) / 2

    # direction du croissant
    direction = 1 if phase < 0.5 else -1

    decalage = rayon * (1 - illumination) * 1.8 * direction

    ombre = QRadialGradient(centre + QPointF(decalage, 0), rayon * 1.2)

    ombre.setColorAt(0.0, QColor(0, 0, 0, 0))
    ombre.setColorAt(0.6, QColor(10, 10, 20, 120))
    ombre.setColorAt(1.0, QColor(0, 0, 0, 255))

    painter.setBrush(ombre)
    painter.drawEllipse(centre, rayon, rayon)

    # =========================================================
    # 3. Cratères subtils (très léger)
    # =========================================================
    painter.setBrush(QColor(180, 180, 190, 40))

    random.seed(3)

    for _ in range(8):
        angle = random.uniform(0, 6.28)
        distance = random.uniform(0, rayon * 0.7)

        x = centre.x() + math.cos(angle) * distance
        y = centre.y() + math.sin(angle) * distance

        r = random.uniform(rayon * 0.05, rayon * 0.12)

        painter.drawEllipse(QPointF(x, y), r, r)

    # =========================================================
    # 4. Glow léger (donne le côté “lune lumineuse”)
    # =========================================================
    lueur = QRadialGradient(centre, rayon * 1.6)
    lueur.setColorAt(0.7, QColor(255, 255, 255, 0))
    lueur.setColorAt(1.0, QColor(200, 200, 255, 30))

    painter.setBrush(lueur)
    painter.drawEllipse(centre, rayon * 1.05, rayon * 1.05)
