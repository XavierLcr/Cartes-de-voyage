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


def _ligne_centrale_tentacule(
    x0, y0, angle_ancrage, longueur, taille, phase, coup_de_nage, n_points=7
):
    """Calcule la ligne centrale d'un tentacule. La courbure voyage de la
    base vers la pointe, et son SENS est mirroré selon que le bras est
    au-dessus ou en-dessous de l'axe central (symétrie haut/bas), pour
    éviter que tous les bras ondulent comme une seule vague qui tourne
    dans le même sens."""
    signe = 1.0 if angle_ancrage >= 0 else -1.0
    points = []
    avance_totale = longueur
    for i in range(n_points):
        s = i / (n_points - 1)
        enveloppe = s**1.4
        onde = math.sin(phase * 1.5 - s * 4.2)
        lateral = onde * enveloppe * taille * (0.14 + 0.09 * abs(coup_de_nage)) * signe
        avance = s * avance_totale
        px = x0 - avance * math.cos(angle_ancrage * 0.4)
        py = y0 + avance * math.sin(angle_ancrage) + lateral
        points.append(QPointF(px, py))
    return points


def _construire_ruban(points, largeurs):
    hauts, bas = [], []
    n = len(points)
    for i in range(n):
        if i == 0:
            tangente = points[1] - points[0]
        elif i == n - 1:
            tangente = points[i] - points[i - 1]
        else:
            tangente = points[i + 1] - points[i - 1]
        longueur_t = math.hypot(tangente.x(), tangente.y()) or 1e-6
        nx, ny = -tangente.y() / longueur_t, tangente.x() / longueur_t
        w = largeurs[i]
        hauts.append(QPointF(points[i].x() + nx * w, points[i].y() + ny * w))
        bas.append(QPointF(points[i].x() - nx * w, points[i].y() - ny * w))

    def _tracer_spline(chemin, pts):
        for i in range(1, len(pts) - 1):
            milieu = QPointF(
                (pts[i].x() + pts[i + 1].x()) / 2, (pts[i].y() + pts[i + 1].y()) / 2
            )
            chemin.quadTo(pts[i], milieu)
        chemin.lineTo(pts[-1])

    chemin = QPainterPath()
    chemin.moveTo(hauts[0])
    _tracer_spline(chemin, hauts)
    bas_inverse = list(reversed(bas))
    chemin.lineTo(bas_inverse[0])
    _tracer_spline(chemin, bas_inverse)
    chemin.closeSubpath()
    return chemin


def _dessiner_poulpe(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    sens: float,
    couleur: QColor,
    phase: float = 0.0,
    degrade: bool = True,
    intensite_encre: float = 0.0,
) -> None:
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.translate(centre)
    if sens < 0:
        painter.scale(-1, 1)

    coup_de_nage = math.sin(phase)

    trait = QColor(couleur).darker(145)
    trait.setAlpha(210)
    pen = QPen(trait)
    pen.setWidthF(max(0.7, taille * 0.014))

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

    rayon_base = taille * 0.15
    rx_tete = rayon_base * (1.0 - coup_de_nage * 0.30)
    ry_tete = rayon_base * (1.0 + coup_de_nage * 0.32)
    tete_x = taille * 0.30

    facteur_angle = 0.45 + (1.0 - coup_de_nage) * 0.5
    facteur_longueur = 0.75 + (1.0 - coup_de_nage) * 0.30

    couleur_bras = QColor(couleur).darker(108)
    couleur_bras.setAlpha(245)
    painter.setBrush(QBrush(couleur_bras))

    angles_ancrage = [-0.75, -0.55, -0.32, -0.10, 0.10, 0.32, 0.55, 0.75]
    longueurs_rel = [0.72, 0.92, 1.12, 1.28, 1.28, 1.12, 0.92, 0.72]

    for angle_ancrage, longueur_rel in zip(angles_ancrage, longueurs_rel):
        angle_effectif = angle_ancrage * facteur_angle
        x0 = tete_x - math.cos(angle_effectif) * rx_tete * 0.3
        y0 = math.sin(angle_effectif) * ry_tete * 0.9

        longueur_reelle = taille * longueur_rel * facteur_longueur
        points = _ligne_centrale_tentacule(
            x0, y0, angle_effectif, longueur_reelle, taille, phase, coup_de_nage
        )
        n_points = len(points)
        largeurs = [
            taille * (0.028 - 0.024 * (j / (n_points - 1)) ** 0.8)
            for j in range(n_points)
        ]

        painter.setPen(pen)
        painter.drawPath(_construire_ruban(points, largeurs))

        painter.setPen(Qt.PenStyle.NoPen)
        ventouse = QColor(couleur).lighter(155)
        ventouse.setAlpha(110)
        painter.setBrush(QBrush(ventouse))
        for j in range(2, n_points - 1):
            painter.drawEllipse(points[j], taille * 0.007, taille * 0.007)
        painter.setBrush(QBrush(couleur_bras))

    if degrade:
        gradient = QRadialGradient(
            QPointF(tete_x + rx_tete * 0.2, -ry_tete * 0.35),
            max(rx_tete, ry_tete) * 1.4,
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
    tete.addEllipse(QPointF(tete_x, 0), rx_tete, ry_tete)
    painter.drawPath(tete)

    painter.setPen(Qt.PenStyle.NoPen)
    reflet = QColor(couleur).lighter(170)
    reflet.setAlpha(60)
    painter.setBrush(QBrush(reflet))
    painter.drawEllipse(
        QPointF(tete_x + rx_tete * 0.1, -ry_tete * 0.35), rx_tete * 0.35, ry_tete * 0.2
    )

    painter.setBrush(QBrush(QColor(couleur).darker(130)))
    painter.drawEllipse(
        QPointF(tete_x - rx_tete * 0.6, ry_tete * 0.35), taille * 0.018, taille * 0.014
    )
    longueur_jet = taille * (0.08 + max(0.0, -coup_de_nage) * 0.22)
    painter.setPen(QPen(QColor(200, 235, 245, 150), max(0.5, taille * 0.011)))
    jet = QPainterPath()
    jet.moveTo(tete_x - rx_tete * 0.65, ry_tete * 0.35)
    jet.lineTo(
        tete_x - rx_tete * 0.65 - longueur_jet,
        ry_tete * 0.35 + math.sin(phase * 3) * taille * 0.012,
    )
    painter.drawPath(jet)

    oeil_r = taille * 0.042
    yeux = (
        QPointF(tete_x + rx_tete * 0.45, -ry_tete * 0.30),
        QPointF(tete_x + rx_tete * 0.50, ry_tete * 0.15),
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
