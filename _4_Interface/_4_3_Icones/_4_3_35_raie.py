################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.35 – Script de création d'une raie                                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor, QRadialGradient

# 1 -- Fonction de création de la raie -----------------------------------------


def _dessiner_raie(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    sens: float,
    couleur: QColor,
    phase: float = 0.0,
    degrade: bool = True,
) -> None:
    """Dessine une raie stylisée vue de dessus, nageoires (ailes) en
    ondulation via `phase`. Orientée vers la droite si `sens > 0`.

    Contrairement au poisson classique, l'ondulation anime ici les deux
    pointes d'ailes en même temps (battement synchronisé, comme une raie
    qui "vole" sous l'eau) plutôt que la seule queue.
    """
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.translate(centre)
    if sens < 0:
        painter.scale(-1, 1)

    largeur = taille * 0.85
    longueur = taille * 0.55

    trait = QColor(couleur).darker(140)
    trait.setAlpha(200)
    pen = QPen(trait)
    pen.setWidthF(max(0.8, taille * 0.025))
    painter.setPen(pen)

    battement = math.sin(phase) * taille * 0.10

    if degrade:
        corps_brush = QRadialGradient(QPointF(taille * 0.05, 0), largeur * 0.6)
        corps_brush.setColorAt(0.0, QColor(couleur).lighter(125))
        corps_brush.setColorAt(1.0, QColor(couleur).darker(120))
        pinceau_corps = QBrush(corps_brush)
    else:
        pinceau_corps = QBrush(couleur)
    painter.setBrush(pinceau_corps)

    # --- corps + ailes (losange arrondi) ---
    corps = QPainterPath()
    corps.moveTo(longueur / 2, 0)  # museau
    corps.quadTo(
        taille * 0.08, -largeur / 2 + battement, -longueur * 0.15, -largeur * 0.08
    )
    corps.quadTo(-longueur * 0.35, -taille * 0.04, -longueur * 0.30, 0)
    corps.quadTo(-longueur * 0.35, taille * 0.04, -longueur * 0.15, largeur * 0.08)
    corps.quadTo(taille * 0.08, largeur / 2 - battement, longueur / 2, 0)
    corps.closeSubpath()
    painter.drawPath(corps)

    # --- queue en fouet, avec un petit aiguillon ---
    queue = QPainterPath()
    xq = -longueur * 0.30
    queue.moveTo(xq, 0)
    ondulation_queue = math.sin(phase + 1.2) * taille * 0.05
    queue.quadTo(
        xq - taille * 0.30,
        ondulation_queue,
        xq - taille * 0.55,
        ondulation_queue * 1.6,
    )
    painter.setBrush(Qt.BrushStyle.NoBrush)
    fouet_pen = QPen(trait)
    fouet_pen.setWidthF(max(0.6, taille * 0.018))
    painter.setPen(fouet_pen)
    painter.drawPath(queue)

    aiguillon = QPainterPath()
    ax = xq - taille * 0.20
    ay = math.sin(phase + 1.2) * taille * 0.05 * 1.2
    aiguillon.moveTo(ax, ay - taille * 0.02)
    aiguillon.lineTo(ax - taille * 0.06, ay)
    aiguillon.lineTo(ax, ay + taille * 0.02)
    aiguillon.closeSubpath()
    painter.setBrush(QBrush(trait))
    painter.drawPath(aiguillon)

    # --- yeux (sur le dessus, bien espacés) ---
    painter.setPen(Qt.PenStyle.NoPen)
    for signe in (-1, 1):
        oeil_centre = QPointF(longueur * 0.20, signe * taille * 0.08)
        oeil_r = taille * 0.035
        painter.setBrush(QBrush(QColor("#1c1f2b")))
        painter.drawEllipse(oeil_centre, oeil_r, oeil_r)
        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        painter.drawEllipse(
            QPointF(oeil_centre.x() + oeil_r * 0.2, oeil_centre.y() - oeil_r * 0.2),
            oeil_r * 0.25,
            oeil_r * 0.25,
        )

    # --- fentes branchiales (petits traits sur le dessous) ---
    painter.setPen(pen)
    for i in range(3):
        gx = taille * 0.00 + i * taille * 0.05
        painter.drawLine(
            QPointF(gx, taille * 0.10), QPointF(gx - taille * 0.015, taille * 0.16)
        )

    painter.restore()
