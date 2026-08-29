################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.17 – Script de création de l'icône d'une valise                          #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QRadialGradient,
    QLinearGradient,
    QPainterPath,
)

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_icone_valise(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône "voyages effectués" : une valise glossy avec poignée arrondie,
    sangle centrale et petite étiquette de destination. Même esprit que
    l'icône curseurs : formes rondes, dégradés doux, ombre portée."""

    COULEUR_CORPS = QColor("#33A0E8")
    COULEUR_SANGLE = QColor("#2C6FA0")
    COULEUR_ETIQUETTE = QColor("#FF9F4A")

    cx, cy = centre.x(), centre.y()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    largeur = taille * 0.80
    hauteur = taille * 0.60
    rayon_coin = taille * 0.09

    x_gauche = cx - largeur / 2
    y_haut = cy - hauteur / 2 + taille * 0.04
    rect_corps = QRectF(x_gauche, y_haut, largeur, hauteur)

    # -- Ombre portée douce ---------------------------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    ombre = QRadialGradient(
        QPointF(cx, y_haut + hauteur + taille * 0.05), taille * 0.32
    )
    ombre.setColorAt(0.0, QColor(0, 0, 0, 55))
    ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.setBrush(QBrush(ombre))
    painter.drawEllipse(
        QPointF(cx, y_haut + hauteur + taille * 0.02), taille * 0.30, taille * 0.08
    )

    # -- Poignée (anse arrondie) ----------------------------------------------
    largeur_anse = taille * 0.22
    hauteur_anse = taille * 0.14
    rect_anse = QRectF(
        cx - largeur_anse / 2, y_haut - hauteur_anse * 0.85, largeur_anse, hauteur_anse
    )
    pen_anse = QPen(COULEUR_SANGLE)
    pen_anse.setWidthF(taille * 0.045)
    pen_anse.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_anse)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    chemin_anse = QPainterPath()
    chemin_anse.moveTo(rect_anse.left(), y_haut + taille * 0.01)
    chemin_anse.arcTo(rect_anse, 180, -180)
    painter.drawPath(chemin_anse)

    # -- Corps de la valise : dégradé glossy -----------------------------------
    degrade_corps = QLinearGradient(x_gauche, y_haut, x_gauche, y_haut + hauteur)
    degrade_corps.setColorAt(0.0, COULEUR_CORPS.lighter(135))
    degrade_corps.setColorAt(0.5, COULEUR_CORPS)
    degrade_corps.setColorAt(1.0, COULEUR_CORPS.darker(115))

    pen_contour = QPen(COULEUR_CORPS.darker(150))
    pen_contour.setWidthF(taille * 0.008)
    painter.setPen(pen_contour)
    painter.setBrush(QBrush(degrade_corps))
    painter.drawRoundedRect(rect_corps, rayon_coin, rayon_coin)

    # -- Sangle verticale centrale ---------------------------------------------
    largeur_sangle = taille * 0.07
    rect_sangle = QRectF(cx - largeur_sangle / 2, y_haut, largeur_sangle, hauteur)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_SANGLE))
    painter.drawRect(rect_sangle)

    # Petite boucle sur la sangle
    rayon_boucle = taille * 0.035
    pen_boucle = QPen(COULEUR_SANGLE.darker(120))
    pen_boucle.setWidthF(taille * 0.018)
    painter.setPen(pen_boucle)
    painter.setBrush(QBrush(QColor("#F5F7FA")))
    painter.drawEllipse(QPointF(cx, cy + taille * 0.02), rayon_boucle, rayon_boucle)

    # -- Deux lignes de nervures horizontales (détail réaliste) -----------------
    pen_nervure = QPen(COULEUR_CORPS.darker(125))
    pen_nervure.setWidthF(taille * 0.012)
    painter.setPen(pen_nervure)
    for frac in (0.28, 0.72):
        y_ligne = y_haut + hauteur * frac
        painter.drawLine(
            QPointF(x_gauche + taille * 0.03, y_ligne),
            QPointF(cx - largeur_sangle / 2 - taille * 0.015, y_ligne),
        )
        painter.drawLine(
            QPointF(cx + largeur_sangle / 2 + taille * 0.015, y_ligne),
            QPointF(x_gauche + largeur - taille * 0.03, y_ligne),
        )

    # -- Étiquette de destination (petit tag qui dépasse) ------------------------
    largeur_tag = taille * 0.16
    hauteur_tag = taille * 0.12
    x_tag = x_gauche + largeur * 0.86
    y_tag = y_haut + hauteur * 0.72
    chemin_tag = QPainterPath()
    chemin_tag.moveTo(x_tag, y_tag)
    chemin_tag.lineTo(x_tag + largeur_tag * 0.72, y_tag)
    chemin_tag.lineTo(x_tag + largeur_tag, y_tag + hauteur_tag / 2)
    chemin_tag.lineTo(x_tag + largeur_tag * 0.72, y_tag + hauteur_tag)
    chemin_tag.lineTo(x_tag, y_tag + hauteur_tag)
    chemin_tag.closeSubpath()

    degrade_tag = QRadialGradient(
        QPointF(x_tag + largeur_tag * 0.3, y_tag + hauteur_tag * 0.3), largeur_tag
    )
    degrade_tag.setColorAt(0.0, COULEUR_ETIQUETTE.lighter(140))
    degrade_tag.setColorAt(1.0, COULEUR_ETIQUETTE.darker(110))

    pen_tag = QPen(COULEUR_ETIQUETTE.darker(140))
    pen_tag.setWidthF(taille * 0.006)
    painter.setPen(pen_tag)
    painter.setBrush(QBrush(degrade_tag))
    painter.drawPath(chemin_tag)

    # Petit trou de l'étiquette
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#F5F7FA")))
    painter.drawEllipse(
        QPointF(x_tag + largeur_tag * 0.16, y_tag + hauteur_tag / 2),
        taille * 0.012,
        taille * 0.012,
    )

    # -- Reflet glossy sur le corps ----------------------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    reflet = QColor(255, 255, 255, 90)
    painter.setBrush(QBrush(reflet))
    chemin_reflet = QPainterPath()
    chemin_reflet.moveTo(x_gauche + taille * 0.05, y_haut + taille * 0.03)
    chemin_reflet.quadTo(
        QPointF(x_gauche + largeur * 0.35, y_haut - taille * 0.01),
        QPointF(x_gauche + largeur * 0.4, y_haut + taille * 0.06),
    )
    chemin_reflet.quadTo(
        QPointF(x_gauche + largeur * 0.2, y_haut + taille * 0.1),
        QPointF(x_gauche + taille * 0.05, y_haut + taille * 0.03),
    )
    chemin_reflet.closeSubpath()
    painter.drawPath(chemin_reflet)
