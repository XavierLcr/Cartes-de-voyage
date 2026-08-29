################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.18 – Script de création de l'icône d'une peinture                        #
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


def _dessiner_icone_peinture(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône "paramétrage & publication de cartes" : une tuile de carte
    légèrement inclinée, découpée en régions irrégulières (façon carte
    administrative) avec une petite enclave qui évoque la granularité fine.
    Même esprit que l'icône curseurs : formes rondes, dégradés doux, ombre
    portée."""

    COULEUR_ZONE_1 = QColor("#33C7E8")
    COULEUR_ZONE_2 = QColor("#8C6FFF")
    COULEUR_ZONE_3 = QColor("#FF6F6F")
    COULEUR_ENCLAVE = QColor("#FFC94A")
    COULEUR_CONTOUR = QColor("#4A5568")

    cx, cy = centre.x(), centre.y()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    largeur = taille * 0.95
    hauteur = taille * 0.80
    rayon_coin = taille * 0.07
    angle_inclinaison = -7

    # -- Ombre portée douce ----------------------------------------------------
    painter.save()
    painter.translate(cx, cy)
    painter.rotate(angle_inclinaison)
    painter.setPen(Qt.PenStyle.NoPen)
    ombre = QRadialGradient(QPointF(0, hauteur * 0.55), taille * 0.34)
    ombre.setColorAt(0.0, QColor(0, 0, 0, 55))
    ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.setBrush(QBrush(ombre))
    painter.drawEllipse(QPointF(0, hauteur * 0.55), taille * 0.30, taille * 0.08)
    painter.restore()

    # -- Tuile de carte inclinée, régions irrégulières --------------------------
    painter.save()
    painter.translate(cx, cy)
    painter.rotate(angle_inclinaison)

    rect_carte = QRectF(-largeur / 2, -hauteur / 2, largeur, hauteur)
    l, t, r, b = (
        rect_carte.left(),
        rect_carte.top(),
        rect_carte.right(),
        rect_carte.bottom(),
    )
    w, h = largeur, hauteur

    chemin_carte = QPainterPath()
    chemin_carte.addRoundedRect(rect_carte, rayon_coin, rayon_coin)
    painter.setClipPath(chemin_carte)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#EAF6FB")))
    painter.drawRoundedRect(rect_carte, rayon_coin, rayon_coin)

    # -- Frontière 1 : ondulée, ancrée à des fractions différentes en haut/bas --
    frontiere1 = QPainterPath()
    frontiere1.moveTo(l + w * 0.34, t)
    frontiere1.cubicTo(
        QPointF(l + w * 0.18, t + h * 0.30),
        QPointF(l + w * 0.30, t + h * 0.55),
        QPointF(l + w * 0.14, t + h * 0.72),
    )
    frontiere1.cubicTo(
        QPointF(l + w * 0.05, t + h * 0.85),
        QPointF(l + w * 0.22, t + h * 0.92),
        QPointF(l + w * 0.16, b),
    )

    # -- Frontière 2 : ondulée différemment, largeur de bande 2 variable --------
    frontiere2 = QPainterPath()
    frontiere2.moveTo(l + w * 0.68, t)
    frontiere2.cubicTo(
        QPointF(l + w * 0.82, t + h * 0.20),
        QPointF(l + w * 0.55, t + h * 0.45),
        QPointF(l + w * 0.70, t + h * 0.62),
    )
    frontiere2.cubicTo(
        QPointF(l + w * 0.80, t + h * 0.75),
        QPointF(l + w * 0.60, t + h * 0.88),
        QPointF(l + w * 0.62, b),
    )

    def _points_frontiere(chemin):
        pts = []
        n = 24
        for i in range(n + 1):
            pts.append(chemin.pointAtPercent(i / n))
        return pts

    pts_f1 = _points_frontiere(frontiere1)
    pts_f2 = _points_frontiere(frontiere2)

    # Région 1 (gauche)
    region1 = QPainterPath()
    region1.moveTo(l, t)
    region1.lineTo(pts_f1[0])
    for p in pts_f1[1:]:
        region1.lineTo(p)
    region1.lineTo(l, b)
    region1.closeSubpath()
    degrade1 = QLinearGradient(l, t, l, b)
    degrade1.setColorAt(0.0, COULEUR_ZONE_1.lighter(130))
    degrade1.setColorAt(1.0, COULEUR_ZONE_1.darker(110))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(degrade1))
    painter.drawPath(region1)

    # Région 2 (centrale, entre les deux frontières)
    region2 = QPainterPath()
    region2.moveTo(pts_f1[0])
    for p in pts_f1[1:]:
        region2.lineTo(p)
    region2.lineTo(pts_f2[-1])
    for p in reversed(pts_f2[:-1]):
        region2.lineTo(p)
    region2.closeSubpath()
    degrade2 = QLinearGradient(l, t, l, b)
    degrade2.setColorAt(0.0, COULEUR_ZONE_2.lighter(130))
    degrade2.setColorAt(1.0, COULEUR_ZONE_2.darker(110))
    painter.setBrush(QBrush(degrade2))
    painter.drawPath(region2)

    # Région 3 (droite)
    region3 = QPainterPath()
    region3.moveTo(r, t)
    region3.lineTo(pts_f2[0])
    for p in pts_f2[1:]:
        region3.lineTo(p)
    region3.lineTo(r, b)
    region3.closeSubpath()
    degrade3 = QLinearGradient(l, t, l, b)
    degrade3.setColorAt(0.0, COULEUR_ZONE_3.lighter(130))
    degrade3.setColorAt(1.0, COULEUR_ZONE_3.darker(110))
    painter.setBrush(QBrush(degrade3))
    painter.drawPath(region3)

    # -- Petite enclave (détail de granularité fine) dans la région centrale ---
    chemin_enclave = QPainterPath()
    cx_enclave = l + w * 0.50
    cy_enclave = t + h * 0.32
    rayon_enclave = taille * 0.045
    chemin_enclave.addEllipse(
        QPointF(cx_enclave, cy_enclave), rayon_enclave, rayon_enclave * 0.85
    )
    painter.setBrush(QBrush(COULEUR_ENCLAVE))
    painter.drawPath(chemin_enclave)

    # -- Liserés de séparation (contours des frontières + enclave) --------------
    pen_liseret = QPen(QColor(255, 255, 255, 200))
    pen_liseret.setWidthF(taille * 0.010)
    painter.setPen(pen_liseret)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(frontiere1)
    painter.drawPath(frontiere2)
    pen_liseret_enclave = QPen(QColor(255, 255, 255, 220))
    pen_liseret_enclave.setWidthF(taille * 0.008)
    painter.setPen(pen_liseret_enclave)
    painter.drawEllipse(
        QPointF(cx_enclave, cy_enclave), rayon_enclave, rayon_enclave * 0.85
    )

    painter.setClipping(False)

    # Contour général de la tuile
    pen_contour = QPen(COULEUR_CONTOUR)
    pen_contour.setWidthF(taille * 0.014)
    painter.setPen(pen_contour)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(rect_carte, rayon_coin, rayon_coin)

    # Reflet glossy en haut à gauche
    painter.setPen(Qt.PenStyle.NoPen)
    reflet = QColor(255, 255, 255, 100)
    painter.setBrush(QBrush(reflet))
    chemin_reflet = QPainterPath()
    chemin_reflet.moveTo(l + taille * 0.03, t + taille * 0.03)
    chemin_reflet.quadTo(
        QPointF(l + w * 0.4, t - taille * 0.01),
        QPointF(l + w * 0.45, t + taille * 0.05),
    )
    chemin_reflet.quadTo(
        QPointF(l + w * 0.2, t + taille * 0.09),
        QPointF(l + taille * 0.03, t + taille * 0.03),
    )
    chemin_reflet.closeSubpath()
    painter.drawPath(chemin_reflet)

    painter.restore()
