################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.37 – Script de création d'un poisson-globe                               #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor, QRadialGradient

# 1 -- Fonction de création du poisson-globe -----------------------------------


def _dessiner_poisson_globe(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    sens: float,
    couleur: QColor,
    phase: float = 0.0,
    degrade: bool = True,
    **kwargs
) -> None:
    """Dessine un poisson-globe stylisé, quasi rond, avec de petites
    épines tout autour du corps qui "respirent" légèrement au rythme de
    `phase` (le poisson-globe nage lentement mais palpite un peu, contrairement
    à l'ondulation de nage classique des autres poissons).
    Orienté vers la droite si `sens > 0`.
    """
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.translate(centre)
    if sens < 0:
        painter.scale(-1, 1)

    rayon = taille * 0.32

    trait = QColor(couleur).darker(140)
    trait.setAlpha(200)
    pen = QPen(trait)
    pen.setWidthF(max(0.8, taille * 0.03))
    painter.setPen(pen)

    # légère pulsation du corps (respiration), pas une ondulation de nage
    pulsation = 1.0 + math.sin(phase * 0.6) * 0.04
    rayon_pulse = rayon * pulsation

    if degrade:
        corps_brush = QRadialGradient(
            QPointF(-rayon_pulse * 0.15, -rayon_pulse * 0.2), rayon_pulse * 0.9
        )
        corps_brush.setColorAt(0.0, QColor(couleur).lighter(135))
        corps_brush.setColorAt(1.0, QColor(couleur).darker(115))
        pinceau_corps = QBrush(corps_brush)
    else:
        pinceau_corps = QBrush(couleur)
    painter.setBrush(pinceau_corps)

    # --- épines (dessinées avant le corps pour être partiellement recouvertes à la base) ---
    epine_longueur = taille * 0.06 * (0.85 + math.sin(phase * 0.6) * 0.15)
    epine_pen = QPen(trait)
    epine_pen.setWidthF(max(0.6, taille * 0.015))
    painter.setPen(epine_pen)
    nb_epines = 14
    for i in range(nb_epines):
        angle = (i / nb_epines) * math.tau
        # on évite la zone du museau (droite) pour ne pas gêner l'œil/bouche
        if -0.5 < angle < 0.5:
            continue
        xb = math.cos(angle) * rayon_pulse * 0.95
        yb = math.sin(angle) * rayon_pulse * 0.95
        xe = math.cos(angle) * (rayon_pulse + epine_longueur)
        ye = math.sin(angle) * (rayon_pulse + epine_longueur)
        painter.drawLine(QPointF(xb, yb), QPointF(xe, ye))

    # --- corps (quasi cercle) ---
    painter.setPen(pen)
    painter.setBrush(pinceau_corps)
    corps = QPainterPath()
    corps.addEllipse(QPointF(0, 0), rayon_pulse, rayon_pulse * 0.92)
    painter.drawPath(corps)

    # --- nageoire pectorale (petite, presque décorative) ---
    pectorale = QPainterPath()
    px = rayon_pulse * 0.05
    py = rayon_pulse * 0.55
    pectorale.moveTo(px, py)
    pectorale.quadTo(
        px + taille * 0.10, py + taille * 0.10, px + taille * 0.03, py + taille * 0.20
    )
    pectorale.quadTo(px - taille * 0.03, py + taille * 0.08, px, py)
    pectorale.closeSubpath()
    pinceau_nageoire = QColor(couleur).darker(108)
    pinceau_nageoire.setAlpha(230)
    painter.setBrush(QBrush(pinceau_nageoire))
    painter.drawPath(pectorale)

    # --- petite queue courte (le globe n'a presque pas de queue) ---
    queue = QPainterPath()
    xq = -rayon_pulse * 0.92
    queue.moveTo(xq, 0)
    queue.quadTo(xq - taille * 0.06, -taille * 0.05, xq - taille * 0.10, 0)
    queue.quadTo(xq - taille * 0.06, taille * 0.05, xq, 0)
    queue.closeSubpath()
    painter.setBrush(pinceau_corps)
    painter.drawPath(queue)

    # --- motif ventral (quelques taches plus claires, façon poisson-globe) ---
    painter.setPen(Qt.PenStyle.NoPen)
    tache_brush = QColor(couleur).lighter(150)
    tache_brush.setAlpha(90)
    painter.setBrush(QBrush(tache_brush))
    for dx, dy, r in (
        (-rayon_pulse * 0.15, rayon_pulse * 0.35, taille * 0.03),
        (rayon_pulse * 0.10, rayon_pulse * 0.45, taille * 0.025),
        (-rayon_pulse * 0.40, rayon_pulse * 0.20, taille * 0.02),
    ):
        painter.drawEllipse(QPointF(dx, dy), r, r)

    # --- œil (grand, façon poisson-globe attachant) ---
    painter.setBrush(QBrush(QColor("#FFFFFF")))
    oeil_r = taille * 0.065
    oeil_centre = QPointF(rayon_pulse * 0.45, -rayon_pulse * 0.20)
    painter.drawEllipse(oeil_centre, oeil_r, oeil_r)
    painter.setBrush(QBrush(QColor("#1c1f2b")))
    painter.drawEllipse(oeil_centre, oeil_r * 0.5, oeil_r * 0.5)
    painter.setBrush(QBrush(QColor(255, 255, 255, 210)))
    painter.drawEllipse(
        QPointF(oeil_centre.x() + oeil_r * 0.15, oeil_centre.y() - oeil_r * 0.2),
        oeil_r * 0.18,
        oeil_r * 0.18,
    )

    # --- bouche (petite moue en O) ---
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    bouche_centre = QPointF(rayon_pulse * 0.85, rayon_pulse * 0.05)
    bouche_r = taille * 0.025
    painter.drawEllipse(bouche_centre, bouche_r, bouche_r)

    painter.restore()
