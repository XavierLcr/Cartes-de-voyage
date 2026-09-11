################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.34 – Script de création de poissons et de génération d'une liste         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math
import random
from typing import List

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor, QRadialGradient

# 1 -- Fonction de création du poisson -----------------------------------------


def _dessiner_poisson(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    sens: float,
    couleur: QColor,
    requin: bool = False,
    phase: float = 0.0,
    degrade: bool = True,
) -> None:
    """Dessine un poisson (ou requin) stylisé, orienté vers la droite si
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

    corps_l = taille * (0.62 if not requin else 0.68)
    corps_h = taille * (0.34 if not requin else 0.30)

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

    # --- nageoire dorsale ---
    if requin:
        dorsale = QPainterPath()
        dorsale.moveTo(-taille * 0.02, -corps_h * 0.42)
        dorsale.lineTo(taille * 0.06, -corps_h * 1.05)
        dorsale.lineTo(taille * 0.14, -corps_h * 0.42)
        dorsale.closeSubpath()
        painter.drawPath(dorsale)

        # ouïes : petites fentes derrière la tête
        ouies_pen = QPen(trait)
        ouies_pen.setWidthF(max(0.6, taille * 0.02))
        painter.setPen(ouies_pen)
        for i in range(3):
            ox = corps_l * 0.10 + i * taille * 0.03
            painter.drawLine(
                QPointF(ox, -corps_h * 0.30),
                QPointF(ox - taille * 0.02, corps_h * 0.30),
            )
        painter.setPen(pen)
    else:
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

    # --- bouche (requin uniquement) ---
    if requin:
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        bouche = QPainterPath()
        bouche.moveTo(corps_l * 0.30, corps_h * 0.05)
        bouche.quadTo(corps_l * 0.20, corps_h * 0.25, corps_l * 0.05, corps_h * 0.10)
        painter.drawPath(bouche)

    painter.restore()


# 2 -- Fonction de génération des caractéristiques d'une liste de poissons -----


def _generer_poissons(n: int) -> List[dict]:
    """Prégénère n poissons nageant dans la mer : trajectoire horizontale
    en va-et-vient (gauche <-> droite), à une hauteur et une vitesse qui
    varient d'un poisson à l'autre pour un banc naturel plutôt que des
    clones synchronisés."""
    rng = random.Random(2024)
    couleurs = ["#E8834A", "#5FA8A0", "#D96C6C", "#4C7FB0", "#E0B24C"]
    poissons = []
    for i in range(n):
        sens = 1 if rng.random() < 0.5 else -1
        poissons.append(
            {
                "nx": rng.uniform(0.0, 1.0),  # position horizontale (0-1) dans la mer
                "ny": rng.uniform(0.12, 0.75),  # hauteur (0 = surface, 1 = fond)
                "sens": sens,  # 1 = va vers la droite, -1 = vers la gauche
                "vitesse": rng.uniform(
                    0.05, 0.11
                ),  # fraction de largeur / seconde-anim
                "echelle": rng.uniform(0.75, 1.25),
                "amplitude_verticale": rng.uniform(0.015, 0.035),
                "phase": rng.uniform(0.0, math.tau),
                "couleur": QColor(couleurs[i % len(couleurs)]),
                "requin": (
                    i == 0
                ),  # le premier du banc est un peu plus gros / différent
            }
        )
    return poissons
