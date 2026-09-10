################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.32 – Script de création de l'icône d'une étoile de mer                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math
import random

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QBrush,
    QPen,
    QColor,
    QRadialGradient,
)

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_etoile_mer(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    fond: QColor,
    trait: QColor,
    angle_deg: float = 0.0,
    graine: int | None = 0,
) -> None:
    """Étoile de mer stylisée à 5 bras arrondis, avec relief et granulosité.

    Contrairement à une étoile géométrique classique (pointes triangulaires),
    le contour est construit avec des courbes de Bézier pour obtenir des bras
    charnus qui s'évasent depuis le disque central puis se referment en
    pointe arrondie — la silhouette caractéristique d'une vraie étoile de mer.
    """
    painter.save()
    painter.translate(centre)
    painter.rotate(angle_deg)

    alea = random.Random(graine)

    branches = 5
    rayon_ext = taille  # longueur des bras
    rayon_creux = taille * 0.40  # profondeur des sillons entre les bras
    rayon_bulbe = taille * 1.05  # largeur (via les points de contrôle)

    pas = math.tau / branches
    depart = -math.pi / 2

    def point(angle: float, rayon: float) -> QPointF:
        return QPointF(math.cos(angle) * rayon, math.sin(angle) * rayon)

    # -- 1.1 Contour organique du corps ------------------------------------
    chemin = QPainterPath()
    for i in range(branches):
        a_creux1 = depart + pas * i - pas / 2
        a_pointe = depart + pas * i
        a_creux2 = depart + pas * i + pas / 2

        # légère irrégularité pour casser la symétrie parfaite
        variance = 1.0 + alea.uniform(-0.05, 0.05)

        p_creux1 = point(a_creux1, rayon_creux)
        p_pointe = point(a_pointe, rayon_ext * variance)
        p_creux2 = point(a_creux2, rayon_creux)

        c1 = point(a_creux1 + pas * 0.22, rayon_bulbe * 0.55)
        c2 = point(a_pointe - pas * 0.20, rayon_bulbe * 0.66)
        c3 = point(a_pointe + pas * 0.20, rayon_bulbe * 0.66)
        c4 = point(a_creux2 - pas * 0.22, rayon_bulbe * 0.55)

        if i == 0:
            chemin.moveTo(p_creux1)
        chemin.cubicTo(c1, c2, p_pointe)
        chemin.cubicTo(c3, c4, p_creux2)
    chemin.closeSubpath()

    # -- 1.2 Remplissage en dégradé pour donner du volume -------------------
    degrade = QRadialGradient(QPointF(-taille * 0.15, -taille * 0.15), taille * 1.3)
    degrade.setColorAt(0.0, fond.lighter(130))
    degrade.setColorAt(0.55, fond)
    degrade.setColorAt(1.0, fond.darker(115))

    pen = QPen(trait)
    pen.setWidthF(max(0.6, taille * 0.06))
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(QBrush(degrade))
    painter.drawPath(chemin)

    # -- 1.3 Sillon central de chaque bras (ambulacre) -----------------------
    painter.setBrush(Qt.BrushStyle.NoBrush)
    pen_sillon = QPen(trait.darker(120))
    pen_sillon.setWidthF(max(0.4, taille * 0.025))
    pen_sillon.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_sillon)
    for i in range(branches):
        a_pointe = depart + pas * i
        p_pointe = point(a_pointe, rayon_ext * 0.92)
        sillon = QPainterPath()
        sillon.moveTo(point(a_pointe, rayon_creux * 0.5))
        sillon.quadTo(point(a_pointe, rayon_ext * 0.55), p_pointe)
        painter.drawPath(sillon)

    # -- 1.4 Granules / tubercules dispersés sur la surface ------------------
    painter.setPen(Qt.PenStyle.NoPen)
    for i in range(branches):
        a_pointe = depart + pas * i
        a_gauche = a_pointe - pas * 0.30
        a_droite = a_pointe + pas * 0.30

        for t in (0.30, 0.45, 0.60, 0.72, 0.84):
            for cote, a_ref in ((-1, a_gauche), (1, a_droite)):
                decal = alea.uniform(-0.05, 0.05)
                ang = a_pointe + (a_ref - a_pointe) * (0.5 + decal) * (1 - t * 0.3)
                r = rayon_creux + (rayon_ext * 0.9 - rayon_creux) * t
                r *= 1.0 + alea.uniform(-0.04, 0.04)
                p = point(ang, r)
                taille_granule = taille * alea.uniform(0.035, 0.065) * (1.0 - t * 0.3)
                teinte = fond.lighter(int(115 + alea.uniform(-10, 15)))
                painter.setBrush(QBrush(teinte))
                painter.drawEllipse(p, taille_granule, taille_granule)

    # -- 1.5 Disque central légèrement surélevé (madréporite inclus) --------
    painter.setPen(QPen(trait.darker(110), max(0.5, taille * 0.03)))
    painter.setBrush(QBrush(fond.lighter(118)))
    painter.drawEllipse(QPointF(0, 0), taille * 0.16, taille * 0.16)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(trait.darker(130)))
    painter.drawEllipse(
        QPointF(taille * 0.04, -taille * 0.04), taille * 0.045, taille * 0.045
    )

    painter.restore()
