################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.34 – Script de création de poissons et de génération d'une liste         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor, QRadialGradient

# 1 -- Fonction de création du poisson -----------------------------------------


def _dessiner_poisson(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    sens: float,
    couleur: QColor,
    phase: float = 0.0,
    degrade: bool = True,
    **kwargs
) -> None:
    """Dessine un poisson stylisé, orienté vers la droite si
    `sens > 0`, vers la gauche sinon. `taille` correspond grossièrement à
    la longueur totale (corps + queue).

    `phase` (en radians) permet d'animer la nage : fait onduler la queue
    et les nageoires selon un sinus, à faire varier dans le temps par
    l'appelant (ex: phase = t * vitesse).
    `degrade` active un léger dégradé radial sur le corps pour un effet
    de volume ; à désactiver si tu dessines beaucoup de poissons et veux
    économiser du temps de rendu.
    """
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.translate(centre)
    if sens < 0:
        painter.scale(-1, 1)  # symétrie horizontale : nage vers la gauche

    corps_l = taille * 0.62
    corps_h = taille * 0.34

    trait = QColor(couleur).darker(140)
    trait.setAlpha(200)
    pen = QPen(trait)
    pen.setWidthF(max(0.8, taille * 0.03))
    painter.setPen(pen)

    ondulation = math.sin(phase) * taille * 0.06

    if degrade:
        corps_brush = QRadialGradient(
            QPointF(-corps_l * 0.1, -corps_h * 0.15), corps_l * 0.65
        )
        corps_brush.setColorAt(0.0, QColor(couleur).lighter(130))
        corps_brush.setColorAt(1.0, QColor(couleur).darker(115))
        pinceau_corps = QBrush(corps_brush)
    else:
        pinceau_corps = QBrush(couleur)
    painter.setBrush(pinceau_corps)

    # --- corps ---
    corps = QPainterPath()
    corps.addEllipse(QPointF(-taille * 0.06, 0), corps_l / 2, corps_h / 2)
    painter.drawPath(corps)

    # --- nageoire pectorale ---
    pectorale = QPainterPath()
    px = taille * 0.02
    pectorale.moveTo(px, corps_h * 0.15)
    pectorale.quadTo(
        px + taille * 0.10,
        corps_h * 0.45 + ondulation * 0.5,
        px + taille * 0.02,
        corps_h * 0.55,
    )
    pectorale.quadTo(px - taille * 0.05, corps_h * 0.30, px, corps_h * 0.15)
    pectorale.closeSubpath()
    pinceau_nageoire = QColor(couleur).darker(105)
    pinceau_nageoire.setAlpha(230)
    painter.setBrush(QBrush(pinceau_nageoire))
    painter.drawPath(pectorale)

    # --- queue (triangle échancré, ondule avec la phase) ---
    painter.setBrush(pinceau_corps)
    queue = QPainterPath()
    xq = -corps_l / 2 - taille * 0.02
    queue.moveTo(xq, 0)
    queue.lineTo(xq - taille * 0.22, -taille * 0.18 + ondulation)
    queue.lineTo(xq - taille * 0.12, 0)
    queue.lineTo(xq - taille * 0.22, taille * 0.18 + ondulation)
    queue.closeSubpath()
    painter.drawPath(queue)

    dorsale = QPainterPath()
    dorsale.moveTo(-taille * 0.05, -corps_h * 0.40)
    dorsale.quadTo(taille * 0.05, -corps_h * 0.78, taille * 0.15, -corps_h * 0.38)
    dorsale.closeSubpath()
    painter.drawPath(dorsale)

    # --- œil (avec reflet) ---
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#FFFFFF")))
    oeil_r = taille * 0.045
    oeil_centre = QPointF(corps_l * 0.22, -corps_h * 0.08)
    painter.drawEllipse(oeil_centre, oeil_r, oeil_r)
    painter.setBrush(QBrush(QColor("#1c1f2b")))
    painter.drawEllipse(oeil_centre, oeil_r * 0.45, oeil_r * 0.45)
    painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
    painter.drawEllipse(
        QPointF(oeil_centre.x() + oeil_r * 0.15, oeil_centre.y() - oeil_r * 0.2),
        oeil_r * 0.15,
        oeil_r * 0.15,
    )

    painter.restore()
