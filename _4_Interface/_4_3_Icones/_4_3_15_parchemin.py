################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.15 – Script de création d'un icône de parchemin                          #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen

# 1 -- Classe de création de l'icône -------------------------------------------


def _dessiner_icone_parchemin(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône profil de voyageur : rouleau de parchemin jauni (bords enroulés
    haut/bas), quelques lignes d'écriture, et une plume posée en diagonale
    avec une pointe trempée d'encre."""

    OMBRE = QColor("#C9B383")
    CREME = QColor("#E8D9B5")
    CREME_CLAIR = QColor("#F1E4C4")
    ENCRE = QColor("#8A7658")
    PLUME = QColor("#3A2E22")
    PLUME_ACCENT = QColor("#6B4A2E")

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

    # Roulés (ombre) haut et bas
    painter.setBrush(QBrush(OMBRE))
    painter.drawEllipse(QPointF(cx, y_haut), rx_roul, ry_roul_ombre)
    painter.drawEllipse(QPointF(cx, y_bas), rx_roul, ry_roul_ombre)

    # Corps du parchemin
    painter.setBrush(QBrush(CREME))
    painter.drawRect(QRectF(x_gauche, y_haut, largeur, hauteur_corps))

    # Face claire des roulés (donne le volume, recouvre le haut de l'ombre)
    painter.setBrush(QBrush(CREME_CLAIR))
    painter.drawEllipse(QPointF(cx, y_haut), rx_roul * 0.94, ry_roul_face)
    painter.drawEllipse(QPointF(cx, y_bas), rx_roul * 0.94, ry_roul_face)

    # Lignes d'écriture
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

    # Plume : hampe diagonale, pointe trempée d'encre sur le parchemin
    nib = QPointF(x_gauche + largeur * 0.22, y_bas - hauteur_corps * 0.14)
    pointe = QPointF(cx + largeur / 2 + taille * 0.10, y_haut - taille * 0.06)

    pen_hampe = QPen(PLUME)
    pen_hampe.setWidthF(taille * 0.02)
    pen_hampe.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_hampe)
    painter.drawLine(nib, pointe)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(ENCRE))
    painter.drawEllipse(nib, taille * 0.014, taille * 0.014)

    # Barbes de la plume (courtes obliques près du sommet de la hampe)
    angle_hampe = math.atan2(pointe.y() - nib.y(), pointe.x() - nib.x())
    pen_barbe = QPen(PLUME_ACCENT)
    pen_barbe.setWidthF(taille * 0.012)
    pen_barbe.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_barbe)

    for t, longueur, sens in [(0.60, 0.11, 1), (0.72, 0.13, -1), (0.85, 0.10, 1)]:
        base = QPointF(
            nib.x() + (pointe.x() - nib.x()) * t,
            nib.y() + (pointe.y() - nib.y()) * t,
        )
        angle_barbe = angle_hampe + sens * math.radians(55)
        fin = QPointF(
            base.x() + math.cos(angle_barbe) * taille * longueur,
            base.y() + math.sin(angle_barbe) * taille * longueur,
        )
        painter.drawLine(base, fin)
