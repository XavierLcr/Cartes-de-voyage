################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.38 – Script de création d'un requin                                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor, QRadialGradient

# 1 -- Fonction de création du requin (dédiée) ---------------------------------


def _dessiner_requin(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    sens: float,
    couleur: QColor,
    phase: float = 0.0,
    degrade: bool = True,
) -> None:
    """Dessine un requin stylisé : corps fuselé en torpille, museau
    pointu, queue en croissant asymétrique (hétérocerque, comme chez le
    vrai requin), nageoire dorsale triangulaire haute, nageoires
    pectorales anguleuses inclinées vers le bas, contre-ombrage
    (dos plus foncé que le ventre). Orienté vers la droite si `sens > 0`.

    `phase` anime uniquement la queue (le corps d'un requin ondule peu
    en comparaison d'un poisson classique).
    """
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.translate(centre)
    if sens < 0:
        painter.scale(-1, 1)

    corps_l = taille * 0.78
    corps_h = taille * 0.26

    trait = QColor(couleur).darker(150)
    trait.setAlpha(210)
    pen = QPen(trait)
    pen.setWidthF(max(0.8, taille * 0.025))
    painter.setPen(pen)

    ondulation_queue = math.sin(phase) * taille * 0.05

    # --- contre-ombrage : dégradé vertical dos foncé -> ventre clair ---
    if degrade:
        corps_brush = QRadialGradient(
            QPointF(-corps_l * 0.05, -corps_h * 0.5), corps_h * 1.8
        )
        corps_brush.setColorAt(0.0, QColor(couleur).darker(125))
        corps_brush.setColorAt(0.55, QColor(couleur))
        corps_brush.setColorAt(1.0, QColor(couleur).lighter(160))
        pinceau_corps = QBrush(corps_brush)
    else:
        pinceau_corps = QBrush(couleur)
    painter.setBrush(pinceau_corps)

    # --- corps : torpille effilée aux deux bouts (museau pointu, arrière fin) ---
    corps = QPainterPath()
    xm = corps_l / 2  # museau
    xa = -corps_l / 2  # arrière (pédoncule caudal)
    corps.moveTo(xm, 0)
    corps.quadTo(corps_l * 0.30, -corps_h / 2, 0, -corps_h * 0.42)
    corps.quadTo(xa * 0.55, -corps_h * 0.28, xa, -corps_h * 0.08)
    corps.quadTo(xa, corps_h * 0.08, xa * 0.55, corps_h * 0.28)
    corps.quadTo(0, corps_h * 0.42, corps_l * 0.30, corps_h / 2)
    corps.closeSubpath()
    painter.drawPath(corps)

    # --- queue en croissant asymétrique (lobe haut plus grand que le lobe bas) ---
    painter.setBrush(pinceau_corps)
    queue = QPainterPath()
    xq = xa - taille * 0.01
    queue.moveTo(xq, -corps_h * 0.06)
    queue.quadTo(
        xq - taille * 0.16,
        -taille * 0.28 + ondulation_queue,
        xq - taille * 0.06,
        -taille * 0.34 + ondulation_queue,
    )
    queue.quadTo(xq - taille * 0.10, -taille * 0.06, xq - taille * 0.02, 0)
    queue.quadTo(
        xq - taille * 0.07,
        taille * 0.14 + ondulation_queue * 0.6,
        xq - taille * 0.02,
        taille * 0.18 + ondulation_queue * 0.6,
    )
    queue.quadTo(xq - taille * 0.01, taille * 0.04, xq, corps_h * 0.06)
    queue.closeSubpath()
    painter.drawPath(queue)

    # --- nageoire dorsale (grand triangle, penché vers l'arrière) ---
    dorsale = QPainterPath()
    dorsale.moveTo(taille * 0.02, -corps_h * 0.40)
    dorsale.lineTo(-taille * 0.02, -taille * 0.40)
    dorsale.lineTo(taille * 0.16, -corps_h * 0.40)
    dorsale.closeSubpath()
    painter.drawPath(dorsale)

    # --- nageoires pectorales (anguleuses, pointant vers le bas) ---
    pectorale = QPainterPath()
    px = corps_l * 0.12
    pectorale.moveTo(px, corps_h * 0.30)
    pectorale.lineTo(px - taille * 0.05, taille * 0.20)
    pectorale.lineTo(px + taille * 0.08, corps_h * 0.35)
    pectorale.closeSubpath()
    pinceau_nageoire = QColor(couleur).darker(112)
    pinceau_nageoire.setAlpha(235)
    painter.setBrush(QBrush(pinceau_nageoire))
    painter.drawPath(pectorale)

    # --- nageoire anale (petite, sous le pédoncule) ---
    anale = QPainterPath()
    ax = xa * 0.45
    anale.moveTo(ax, corps_h * 0.20)
    anale.lineTo(ax - taille * 0.03, taille * 0.10)
    anale.lineTo(ax + taille * 0.05, corps_h * 0.22)
    anale.closeSubpath()
    painter.drawPath(anale)

    # --- ouïes : 5 fentes courbes derrière la tête (trait caractéristique du requin) ---
    ouies_pen = QPen(trait)
    ouies_pen.setWidthF(max(0.6, taille * 0.018))
    painter.setPen(ouies_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    for i in range(5):
        ox = corps_l * 0.16 + i * taille * 0.022
        fente = QPainterPath()
        fente.moveTo(ox, -corps_h * 0.30)
        fente.quadTo(ox - taille * 0.015, 0, ox, corps_h * 0.30)
        painter.drawPath(fente)

    # --- œil (petit, façon prédateur, pas de reflet mignon) ---
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#1c1f2b")))
    oeil_r = taille * 0.03
    oeil_centre = QPointF(corps_l * 0.38, -corps_h * 0.12)
    painter.drawEllipse(oeil_centre, oeil_r, oeil_r)
    painter.setBrush(QBrush(QColor(255, 255, 255, 160)))
    painter.drawEllipse(
        QPointF(oeil_centre.x() + oeil_r * 0.2, oeil_centre.y() - oeil_r * 0.25),
        oeil_r * 0.2,
        oeil_r * 0.2,
    )

    # --- bouche (fente en dessous du museau, légèrement incurvée) ---
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    bouche = QPainterPath()
    bouche.moveTo(corps_l * 0.42, corps_h * 0.10)
    bouche.quadTo(corps_l * 0.32, corps_h * 0.26, corps_l * 0.18, corps_h * 0.14)
    painter.drawPath(bouche)

    painter.restore()
