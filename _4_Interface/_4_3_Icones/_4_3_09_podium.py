################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.9 – Script de création d'un podium miniature    '                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QColor, QLinearGradient, QBrush, QPainter

# 1 -- Fonction de création du podium miniature --------------------------------


def _dessiner_icone_podium(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône de classement : podium à 3 marches (or/argent/bronze),
    avec une petite étoile au-dessus de la marche centrale (1re place)."""

    COULEURS = {
        1: (QColor("#FBBF24"), QColor("#F59E0B")),  # or
        2: (QColor("#CBD5E1"), QColor("#94A3B8")),  # argent
        3: (QColor("#F0B27A"), QColor("#C2703D")),  # bronze
    }

    largeur_marche = taille * 0.26
    espacement = taille * 0.03

    hauteur_gauche = taille * 0.32  # 2e place
    hauteur_centre = taille * 0.44  # 1re place
    hauteur_droite = taille * 0.24  # 3e place

    base_y = centre.y() + taille * 0.30

    x_centre = centre.x() - largeur_marche / 2
    x_gauche = x_centre - largeur_marche - espacement
    x_droite = x_centre + largeur_marche + espacement

    painter.setPen(Qt.PenStyle.NoPen)

    def _dessiner_marche(x: float, hauteur: float, place: int):
        rect = QRectF(x, base_y - hauteur, largeur_marche, hauteur)

        couleur_haut, couleur_bas = COULEURS[place]
        degrade = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        degrade.setColorAt(0.0, couleur_haut)
        degrade.setColorAt(1.0, couleur_bas)

        painter.setBrush(QBrush(degrade))
        painter.drawRoundedRect(rect, taille * 0.03, taille * 0.03)

    # Ordre de dessin : marches latérales d'abord, centrale en dernier
    # (par-dessus) pour un léger effet de premier plan sur la 1re place
    _dessiner_marche(x_gauche, hauteur_gauche, place=2)
    _dessiner_marche(x_droite, hauteur_droite, place=3)
    _dessiner_marche(x_centre, hauteur_centre, place=1)

    # Petite étoile dorée au-dessus de la 1re marche
    painter.setBrush(QBrush(COULEURS[1][0]))
    _dessiner_petite_etoile(
        painter,
        centre_etoile=QPointF(
            x_centre + largeur_marche / 2, base_y - hauteur_centre - taille * 0.14
        ),
        rayon=taille * 0.10,
    )


def _dessiner_petite_etoile(
    painter: QPainter, centre_etoile: QPointF, rayon: float
) -> None:
    """Dessine une étoile à 5 branches pleine, centrée sur `centre_etoile`."""
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = rayon if i % 2 == 0 else rayon * 0.45
        points.append(
            QPointF(
                centre_etoile.x() + math.cos(angle) * r,
                centre_etoile.y() - math.sin(angle) * r,
            )
        )
    painter.drawPolygon(points)
