################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.33 – Script de création de l'icône d'un coquillage (v2)                  #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_coquillage(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    fond: QColor,
    trait: QColor,
    angle_deg: float = 0.0,
    nb_cotes: int = 7,
    bombement: float = 0.22,
) -> None:
    """Petit coquillage stylisé, façon coquille Saint-Jacques : une
    charnière plate en haut (avec deux petites oreillettes) d'où
    rayonnent des côtes jusqu'aux creux d'un bord festonné en vrais
    lobes arrondis (pas une simple ondulation).

    nb_cotes   : nombre de côtes / lobes (7 est un bon compromis pour
                 une icône lisible en petit format).
    bombement  : à quel point chaque lobe gonfle vers l'extérieur,
                 en fraction du rayon local (0.15 = discret,
                 0.3 = très festonné).
    """
    painter.save()
    painter.translate(centre)
    painter.rotate(angle_deg)

    rayon_x = taille
    rayon_y = taille * 0.92  # dôme légèrement aplati, plus proche d'une vraie coquille

    pen = QPen(trait)
    pen.setWidthF(max(0.6, taille * 0.07))
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(QBrush(fond))

    # -- Points "vallée" : bases des côtes, répartis sur l'ellipse ---------
    vallees = []
    for i in range(nb_cotes + 1):
        t = i / nb_cotes
        ang = math.radians(180 - 180 * t)
        vallees.append((math.cos(ang) * rayon_x, -math.sin(ang) * rayon_y, ang))

    # -- Oreillettes de part et d'autre de la charnière ---------------------
    largeur_oreille = taille * 0.20
    hauteur_oreille = taille * 0.12

    oreille_g = QPainterPath()
    oreille_g.moveTo(-rayon_x * 0.85, 0)
    oreille_g.lineTo(-rayon_x - largeur_oreille, hauteur_oreille * 0.3)
    oreille_g.lineTo(-rayon_x, 0)
    oreille_g.closeSubpath()

    oreille_d = QPainterPath()
    oreille_d.moveTo(rayon_x * 0.85, 0)
    oreille_d.lineTo(rayon_x + largeur_oreille, hauteur_oreille * 0.3)
    oreille_d.lineTo(rayon_x, 0)
    oreille_d.closeSubpath()

    painter.drawPath(oreille_g)
    painter.drawPath(oreille_d)

    # -- Corps principal : bord en lobes arrondis (courbes cubiques) -------
    chemin = QPainterPath()
    chemin.moveTo(vallees[0][0], vallees[0][1])
    for i in range(nb_cotes):
        x1, y1, a1 = vallees[i]
        x2, y2, a2 = vallees[i + 1]
        ang_milieu = (a1 + a2) / 2
        # sommet du lobe, gonflé vers l'extérieur par rapport à l'ellipse de base
        px = math.cos(ang_milieu) * rayon_x * (1 + bombement)
        py = -math.sin(ang_milieu) * rayon_y * (1 + bombement)
        controle_1 = QPointF(x1 + (px - x1) * 0.55, y1 + (py - y1) * 0.55)
        controle_2 = QPointF(x2 + (px - x2) * 0.55, y2 + (py - y2) * 0.55)
        chemin.cubicTo(controle_1, controle_2, QPointF(x2, y2))
    chemin.closeSubpath()  # referme via la ligne de charnière
    painter.drawPath(chemin)

    # -- Côtes : de la charnière jusqu'au creux entre deux lobes ------------
    for x, y, _ in vallees:
        painter.drawLine(QPointF(0, 0), QPointF(x, y))

    painter.restore()
