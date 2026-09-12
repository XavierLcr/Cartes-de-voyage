################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.41 – Script de création d'un poulpe                                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QBrush,
    QPen,
    QColor,
    QRadialGradient,
)
from PyQt6.QtCore import Qt, QPointF

# 1 -- Fonction de création du poulpe ------------------------------------------


def _dessiner_poulpe(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    sens: float,
    couleur: QColor,
    phase: float = 0.0,
    degrade: bool = True,
    **kwargs
) -> None:
    """Dessine un poulpe en pleine nage horizontale : petite tête/manteau
    rond à l'avant, et huit longues tentacules distinctes qui ondulent
    indépendamment en traînant derrière (silhouette bien différente
    d'une raie : le corps est petit, l'essentiel de la silhouette vient
    des tentacules, pas d'un grand disque/aile).

    `intensite_encre` (0.0 à 1.0) déclenche un nuage d'encre expulsé par
    le siphon. Orienté vers la droite si `sens > 0`.
    """

    intensite_encre = kwargs.get("intensite_encre", 0.0)

    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.translate(centre)
    if sens < 0:
        painter.scale(-1, 1)

    respiration = math.sin(phase * 1.2)

    trait = QColor(couleur).darker(145)
    trait.setAlpha(210)
    pen = QPen(trait)
    pen.setWidthF(max(0.7, taille * 0.016))

    # --- 1) Nuage d'encre (derrière tout) ---
    if intensite_encre > 0.01:
        encre_couleur = QColor("#1A1A22")
        xa = -taille * 0.75
        for i in range(5):
            t = i / 4
            rayon_bulle = taille * (0.07 + t * 0.16) * (0.5 + intensite_encre * 0.5)
            dx = xa - t * taille * 0.45 * intensite_encre * 2.0
            dy = math.sin(phase * 2.0 + i * 1.7) * taille * 0.09 * (0.4 + t)
            alpha = int(140 * intensite_encre * (1.0 - t * 0.6))
            encre_couleur.setAlpha(max(0, alpha))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(encre_couleur))
            painter.drawEllipse(QPointF(dx, dy), rayon_bulle, rayon_bulle * 0.9)

    # --- 2) Tête / manteau : petit et rond, PAS allongé ---
    rayon_tete = taille * 0.15 * (1.0 + respiration * 0.05)
    tete_x = taille * 0.30

    # --- 3) Huit tentacules longues, distinctes, en éventail vers l'arrière ---
    couleur_bras = QColor(couleur).darker(108)
    couleur_bras.setAlpha(245)
    painter.setBrush(QBrush(couleur_bras))

    # Répartition des points d'ancrage autour de l'arrière de la tête,
    # sur un arc (pas alignés en une seule ligne) pour un effet éventail.
    positions_bras = [
        # angle_ancrage (rad, 0 = vers l'arrière), longueur, amplitude, phase_offset
        (-0.55, 0.95, 0.09, 0.0),
        (-0.32, 1.15, 0.10, 0.7),
        (-0.10, 1.30, 0.11, 1.4),
        (0.10, 1.30, 0.11, 2.1),
        (0.32, 1.15, 0.10, 2.8),
        (0.55, 0.95, 0.09, 3.5),
        (-0.75, 0.75, 0.08, 4.2),
        (0.75, 0.75, 0.08, 4.9),
    ]

    for angle_ancrage, longueur_rel, amplitude_rel, phase_offset in positions_bras:
        x0 = tete_x - math.cos(angle_ancrage) * rayon_tete * 0.3
        y0 = math.sin(angle_ancrage) * rayon_tete * 0.9

        longueur_reelle = taille * longueur_rel
        amplitude_reelle = taille * amplitude_rel
        phase_bras = phase * 1.1 + phase_offset

        ondulation_1 = math.sin(phase_bras)
        ondulation_2 = math.sin(phase_bras + 1.3)

        x1 = x0 - longueur_reelle
        xm = x0 - longueur_reelle * 0.5
        ym = y0 + ondulation_1 * amplitude_reelle
        y1 = y0 + ondulation_2 * amplitude_reelle * 0.85

        e_base = taille * 0.028
        e_pointe = taille * 0.004

        bras = QPainterPath()
        bras.moveTo(QPointF(x0, y0 - e_base))
        bras.quadTo(QPointF(xm, ym - e_base * 0.45), QPointF(x1, y1 - e_pointe))
        bras.lineTo(QPointF(x1 - taille * 0.015, y1))
        bras.quadTo(QPointF(xm, ym + e_base * 0.45), QPointF(x0, y0 + e_base))
        bras.closeSubpath()

        painter.setPen(pen)
        painter.drawPath(bras)

        # ventouses, discrètes
        painter.setPen(Qt.PenStyle.NoPen)
        ventouse = QColor(couleur).lighter(155)
        ventouse.setAlpha(110)
        painter.setBrush(QBrush(ventouse))
        for j in range(3):
            t = 0.25 + j * 0.25
            x = x0 + (x1 - x0) * t
            y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * ym + t**2 * y1
            painter.drawEllipse(QPointF(x, y), taille * 0.008, taille * 0.008)
        painter.setBrush(QBrush(couleur_bras))

    # --- 4) Manteau (dessiné après les bras pour masquer leur naissance) ---
    if degrade:
        gradient = QRadialGradient(
            QPointF(tete_x + rayon_tete * 0.2, -rayon_tete * 0.35), rayon_tete * 1.4
        )
        gradient.setColorAt(0.0, QColor(couleur).lighter(145))
        gradient.setColorAt(0.6, QColor(couleur))
        gradient.setColorAt(1.0, QColor(couleur).darker(120))
        pinceau_tete = QBrush(gradient)
    else:
        pinceau_tete = QBrush(couleur)

    painter.setPen(pen)
    painter.setBrush(pinceau_tete)
    tete = QPainterPath()
    tete.addEllipse(QPointF(tete_x, 0), rayon_tete, rayon_tete * 0.92)
    painter.drawPath(tete)

    # petit reflet
    painter.setPen(Qt.PenStyle.NoPen)
    reflet = QColor(couleur).lighter(170)
    reflet.setAlpha(60)
    painter.setBrush(QBrush(reflet))
    painter.drawEllipse(
        QPointF(tete_x + rayon_tete * 0.1, -rayon_tete * 0.35),
        rayon_tete * 0.35,
        rayon_tete * 0.2,
    )

    # siphon + petit jet d'eau
    painter.setBrush(QBrush(QColor(couleur).darker(130)))
    painter.drawEllipse(
        QPointF(tete_x - rayon_tete * 0.6, rayon_tete * 0.35),
        taille * 0.018,
        taille * 0.014,
    )
    painter.setPen(QPen(QColor(200, 235, 245, 130), max(0.5, taille * 0.01)))
    jet = QPainterPath()
    jet.moveTo(tete_x - rayon_tete * 0.65, rayon_tete * 0.35)
    jet.lineTo(
        tete_x - rayon_tete * 1.0,
        rayon_tete * 0.35 + math.sin(phase * 3) * taille * 0.012,
    )
    painter.drawPath(jet)

    # --- 5) Yeux (grands, proportionnellement, sur la petite tête) ---
    oeil_r = taille * 0.042
    yeux = (
        QPointF(tete_x + rayon_tete * 0.45, -rayon_tete * 0.30),
        QPointF(tete_x + rayon_tete * 0.50, rayon_tete * 0.15),
    )
    for oeil_centre in yeux:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.drawEllipse(oeil_centre, oeil_r, oeil_r)
        painter.setBrush(QBrush(QColor("#1C1F2B")))
        painter.drawEllipse(
            QPointF(oeil_centre.x() + oeil_r * 0.2, oeil_centre.y()),
            oeil_r * 0.5,
            oeil_r * 0.5,
        )
        painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
        painter.drawEllipse(
            QPointF(oeil_centre.x() + oeil_r * 0.3, oeil_centre.y() - oeil_r * 0.22),
            oeil_r * 0.17,
            oeil_r * 0.17,
        )

    painter.restore()
