################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.39 – Script de création d'une bouée                                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor, QRadialGradient
from PyQt6.QtCore import Qt, QPointF

# 1 -- Fonction de création de la bouée ----------------------------------------


def _dessiner_bouee(
    painter: QPainter,
    centre_surface: QPointF,
    taille: float,
    profondeur_corde: float,
    couleur: QColor = None,
    phase: float = 0.0,
    degrade: bool = True,
) -> None:
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    if couleur is None:
        couleur = QColor("#E85A2A")

    tangage_vertical = math.sin(phase) * taille * 0.06
    balancement_corde = math.sin(phase * 0.7 + 0.5) * taille * 0.08

    centre_flottant = QPointF(centre_surface.x(), centre_surface.y() + tangage_vertical)

    trait_corde = QColor("#4a4a4a")
    corde_pen = QPen(trait_corde)
    corde_pen.setWidthF(max(0.8, taille * 0.025))
    painter.setPen(corde_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    point_ancrage = QPointF(
        centre_surface.x() + balancement_corde,
        centre_surface.y() + profondeur_corde,
    )
    corde = QPainterPath()
    corde.moveTo(centre_flottant.x(), centre_flottant.y() + taille * 0.15)
    corde.quadTo(
        (centre_flottant.x() + point_ancrage.x()) / 2 + balancement_corde * 0.5,
        (centre_flottant.y() + point_ancrage.y()) / 2,
        point_ancrage.x(),
        point_ancrage.y(),
    )
    painter.drawPath(corde)

    painter.setBrush(QBrush(trait_corde))
    painter.setPen(Qt.PenStyle.NoPen)
    ancre = QPainterPath()
    r_ancre = taille * 0.06
    ancre.addEllipse(point_ancrage, r_ancre, r_ancre * 0.7)
    painter.drawPath(ancre)

    painter.translate(centre_flottant)

    trait = QColor(couleur).darker(140)
    trait.setAlpha(220)
    pen = QPen(trait)
    pen.setWidthF(max(0.8, taille * 0.03))
    painter.setPen(pen)

    largeur = taille * 0.34
    hauteur = taille * 0.42

    if degrade:
        corps_brush = QRadialGradient(
            QPointF(-largeur * 0.2, -hauteur * 0.25), largeur * 1.1
        )
        corps_brush.setColorAt(0.0, QColor(couleur).lighter(135))
        corps_brush.setColorAt(1.0, QColor(couleur).darker(115))
        pinceau_corps = QBrush(corps_brush)
    else:
        pinceau_corps = QBrush(couleur)
    painter.setBrush(pinceau_corps)

    corps = QPainterPath()
    corps.moveTo(-largeur / 2, -hauteur * 0.10)
    corps.quadTo(-largeur * 0.55, -hauteur * 0.55, 0, -hauteur * 0.62)
    corps.quadTo(largeur * 0.55, -hauteur * 0.55, largeur / 2, -hauteur * 0.10)
    corps.quadTo(largeur * 0.50, hauteur * 0.25, largeur * 0.30, hauteur * 0.42)
    corps.lineTo(-largeur * 0.30, hauteur * 0.42)
    corps.quadTo(-largeur * 0.50, hauteur * 0.25, -largeur / 2, -hauteur * 0.10)
    corps.closeSubpath()
    painter.drawPath(corps)

    painter.setBrush(QBrush(QColor("#F5F0E8")))
    painter.setPen(Qt.PenStyle.NoPen)
    for y_bande, h_bande in (
        (-hauteur * 0.32, hauteur * 0.12),
        (hauteur * 0.02, hauteur * 0.12),
    ):
        bande = QPainterPath()
        bande.addRoundedRect(
            -largeur * 0.50,
            y_bande,
            largeur * 1.0,
            h_bande,
            h_bande * 0.15,
            h_bande * 0.15,
        )
        painter.drawPath(bande)

    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    anneau = QPainterPath()
    anneau.addEllipse(QPointF(0, -hauteur * 0.66), taille * 0.045, taille * 0.06)
    painter.drawPath(anneau)

    ombre_flottaison = QColor("#1c1f2b")
    ombre_flottaison.setAlpha(40)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(ombre_flottaison))
    ligne_eau = QPainterPath()
    ligne_eau.addRect(-largeur / 2, hauteur * 0.12, largeur, taille * 0.03)
    painter.drawPath(ligne_eau)

    painter.restore()
