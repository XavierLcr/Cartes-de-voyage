################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.15 – Script de création d'un icône de parchemin                          #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QPainterPath

# 1 -- Classe de création de l'icône -------------------------------------------


def _dessiner_icone_parchemin(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône profil de voyageur : rouleau de parchemin jauni (bords enroulés
    haut/bas), quelques lignes d'écriture, et une plume à empennage posée
    en diagonale, pointe trempée d'encre."""

    OMBRE = QColor("#C9B383")
    CREME = QColor("#E8D9B5")
    CREME_CLAIR = QColor("#F1E4C4")
    ENCRE = QColor("#8A7658")
    PLUME_VANE = QColor("#5C4632")
    PLUME_VANE_CLAIR = QColor("#7A5F42")
    PLUME_SPINE = QColor("#3A2E22")

    cx, cy = centre.x(), centre.y()
    largeur = taille * 0.5
    hauteur_corps = taille * 0.62
    rx_roul = largeur / 2
    ry_roul_ombre = taille * 0.065
    ry_roul_face = taille * 0.045

    x_gauche = cx - largeur / 2
    y_haut = cy - hauteur_corps / 2
    y_bas = cy + hauteur_corps / 2

    painter.setPen(Qt.PenStyle.NoPen)

    # -- Parchemin (inchangé) ------------------------------------------------
    painter.setBrush(QBrush(OMBRE))
    painter.drawEllipse(QPointF(cx, y_haut), rx_roul, ry_roul_ombre)
    painter.drawEllipse(QPointF(cx, y_bas), rx_roul, ry_roul_ombre)

    painter.setBrush(QBrush(CREME))
    painter.drawRect(QRectF(x_gauche, y_haut, largeur, hauteur_corps))

    painter.setBrush(QBrush(CREME_CLAIR))
    painter.drawEllipse(QPointF(cx, y_haut), rx_roul * 0.94, ry_roul_face)
    painter.drawEllipse(QPointF(cx, y_bas), rx_roul * 0.94, ry_roul_face)

    lignes_largeur = [0.72, 0.82, 0.58, 0.68]
    y0 = y_haut + hauteur_corps * 0.30
    espace_ligne = hauteur_corps * 0.15
    pen_ligne = QPen(ENCRE)
    pen_ligne.setWidthF(taille * 0.014)
    pen_ligne.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_ligne)
    painter.setOpacity(0.75)
    for i, frac in enumerate(lignes_largeur):
        yl = y0 + i * espace_ligne
        lw = largeur * 0.72 * frac
        xl = cx - lw / 2
        painter.drawLine(QPointF(xl, yl), QPointF(xl + lw, yl))
    painter.setOpacity(1.0)

    # -- Plume à empennage (nouvelle version) -------------------------------
    nib = QPointF(x_gauche + largeur * 0.22, y_bas - hauteur_corps * 0.14)
    angle_deg = 40.0
    calamus_len = taille * 0.16
    vane_len = taille * 0.34
    w = taille * 0.13
    h_round = w * 0.4

    painter.save()
    painter.translate(nib)
    painter.rotate(angle_deg)
    # Repère local : (0,0) = pointe au contact du papier, -y = vers le haut de la plume

    # Hampe fine (calamus)
    pen_calamus = QPen(PLUME_SPINE)
    pen_calamus.setWidthF(taille * 0.016)
    pen_calamus.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_calamus)
    painter.drawLine(QPointF(0, 0), QPointF(0, -calamus_len))

    # -- Plume classique (forme en amande symétrique) -----------------------
    nib = QPointF(x_gauche + largeur * 0.22, y_bas - hauteur_corps * 0.14)
    angle_deg = 40.0
    calamus_len = taille * 0.16
    vane_len = taille * 0.30
    w = taille * 0.14

    painter.save()
    painter.translate(nib)
    painter.rotate(angle_deg)
    # Repère local : (0,0) = pointe au contact du papier, -y = vers le haut de la plume

    pointe = QPointF(0, -calamus_len)
    sommet = QPointF(0, -(calamus_len + vane_len))
    y_milieu = -(calamus_len + vane_len / 2)

    # Hampe fine (calamus)
    pen_calamus = QPen(PLUME_SPINE)
    pen_calamus.setWidthF(taille * 0.018)
    pen_calamus.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_calamus)
    painter.drawLine(QPointF(0, 0), pointe)

    # Empennage : une seule forme en amande symétrique
    chemin = QPainterPath(pointe)
    chemin.quadTo(QPointF(-w / 2, y_milieu), sommet)
    chemin.quadTo(QPointF(w / 2, y_milieu), pointe)
    chemin.closeSubpath()

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(PLUME_VANE))
    painter.drawPath(chemin)

    # Nervure centrale
    pen_spine = QPen(PLUME_SPINE)
    pen_spine.setWidthF(taille * 0.009)
    pen_spine.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_spine)
    painter.drawLine(pointe, QPointF(0, sommet.y() + 2))

    # Barbes en chevrons, largeur proportionnelle à celle de l'amande à cet endroit
    pen_barbe = QPen(PLUME_SPINE)
    pen_barbe.setWidthF(taille * 0.006)
    pen_barbe.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_barbe)
    painter.setOpacity(0.65)
    for t in (0.25, 0.5, 0.75):
        y = -calamus_len - vane_len * t
        largeur_frac = math.sin(math.pi * t)
        ex = (w / 2) * largeur_frac * 0.85
        ey = y + 12
        painter.drawLine(QPointF(0, y), QPointF(-ex, ey))
        painter.drawLine(QPointF(0, y), QPointF(ex, ey))
    painter.setOpacity(1.0)

    painter.restore()

    # Point d'encre au contact du papier
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(ENCRE))
    painter.drawEllipse(nib, taille * 0.015, taille * 0.015)
