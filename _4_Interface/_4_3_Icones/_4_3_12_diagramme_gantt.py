################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.12 – Script de création d'undiagramme de Gantt miniature                 #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen

# 1 -- Classe de création du diagramme -----------------------------------------


def _dessiner_icone_gantt(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône diagramme de Gantt : 4 barres de tâches à des positions et
    durées variées sur leur piste, plus un repère vertical (type
    "aujourd'hui") traversant les rangées."""

    # Couleurs des barres (une par "tâche", façon code couleur d'un vrai Gantt)
    COULEURS_BARRES = [
        QColor("#5B8DEF"),
        QColor("#F2A65A"),
        QColor("#4FBDBA"),
        QColor("#E9647B"),
    ]
    COULEUR_FOND_PISTE = QColor("#8A94A6")
    COULEUR_MARQUEUR = QColor("#3D4A5C")

    # (début, durée) en fraction de la largeur totale de la piste
    BARRES = [
        (0.00, 0.55),
        (0.20, 0.45),
        (0.10, 0.70),
        (0.35, 0.40),
    ]

    cx, cy = centre.x(), centre.y()
    zone_largeur = taille * 0.78
    zone_gauche = cx - zone_largeur / 2
    zone_hauteur = taille * 0.62
    zone_haut = cy - zone_hauteur / 2
    hauteur_barre = taille * 0.09
    rayon_arrondi = hauteur_barre / 2
    nb_lignes = len(BARRES)
    espacement = zone_hauteur / (nb_lignes - 1)

    painter.setPen(Qt.PenStyle.NoPen)

    for i, (debut, duree) in enumerate(BARRES):
        y_centre = zone_haut + i * espacement
        y_haut = y_centre - hauteur_barre / 2

        # Piste de fond (légère, pour situer la durée totale disponible)
        painter.setBrush(QBrush(COULEUR_FOND_PISTE))
        painter.setOpacity(0.22)
        painter.drawRoundedRect(
            QRectF(zone_gauche, y_haut, zone_largeur, hauteur_barre),
            rayon_arrondi,
            rayon_arrondi,
        )

        # Barre de tâche colorée, positionnée selon (début, durée)
        painter.setOpacity(1.0)
        painter.setBrush(QBrush(COULEURS_BARRES[i % len(COULEURS_BARRES)]))
        painter.drawRoundedRect(
            QRectF(
                zone_gauche + debut * zone_largeur,
                y_haut,
                duree * zone_largeur,
                hauteur_barre,
            ),
            rayon_arrondi,
            rayon_arrondi,
        )

    # # Repère vertical (type ligne "aujourd'hui") traversant les rangées
    # x_marqueur = zone_gauche + 0.62 * zone_largeur
    # y1 = zone_haut - hauteur_barre * 0.6
    # y2 = zone_haut + zone_hauteur + hauteur_barre * 0.6

    # pen_marqueur = QPen(COULEUR_MARQUEUR)
    # pen_marqueur.setWidthF(taille * 0.014)
    # pen_marqueur.setCapStyle(Qt.PenCapStyle.RoundCap)
    # painter.setPen(pen_marqueur)
    # painter.drawLine(QPointF(x_marqueur, y1), QPointF(x_marqueur, y2))

    # painter.setPen(Qt.PenStyle.NoPen)
    # painter.setBrush(QBrush(COULEUR_MARQUEUR))
    # painter.drawEllipse(QPointF(x_marqueur, y1), taille * 0.025, taille * 0.025)
