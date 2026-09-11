################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.36 – Script de création d'une tortue de mer                              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor, QRadialGradient

# 1 -- Fonction de création de la tortue de mer --------------------------------


def _dessiner_tortue(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    sens: float,
    couleur: QColor,
    phase: float = 0.0,
    degrade: bool = True,
) -> None:
    """Dessine une tortue de mer stylisée, vue de dessus, en pleine nage.
    Orientée vers la droite si `sens > 0`.

    Les 4 nageoires battent par paire opposée (avant-gauche + arrière-droite
    ensemble, puis l'inverse), comme une vraie tortue qui "vole" sous l'eau.
    `phase` pilote ce battement ; à faire varier dans le temps par l'appelant,
    idéalement plus lentement que pour un poisson (la nage de tortue est ample
    mais peu fréquente).
    """
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.translate(centre)
    if sens < 0:
        painter.scale(-1, 1)

    carapace_l = taille * 0.55
    carapace_h = taille * 0.42

    trait = QColor(couleur).darker(140)
    trait.setAlpha(210)
    pen = QPen(trait)
    pen.setWidthF(max(0.8, taille * 0.025))
    painter.setPen(pen)

    battement = math.sin(phase) * taille * 0.16

    # --- nageoires (dessinées avant la carapace pour passer dessous) ---
    couleur_nageoire = QColor(couleur).darker(112)
    painter.setBrush(QBrush(couleur_nageoire))

    def _nageoire(
        x0: float, y0: float, avant: bool, angle_battement: float
    ) -> QPainterPath:
        # nageoire en forme de goutte allongée, pivotant autour de son
        # point d'attache pour simuler le battement
        longueur = taille * (0.30 if avant else 0.22)
        largeur = taille * (0.14 if avant else 0.11)
        chemin = QPainterPath()
        dy = angle_battement
        chemin.moveTo(x0, y0)
        chemin.quadTo(
            x0 - longueur * 0.3,
            y0 + largeur * 0.9 + dy,
            x0 - longueur,
            y0 + largeur * 0.2 + dy * 1.4,
        )
        chemin.quadTo(
            x0 - longueur * 0.7,
            y0 - largeur * 0.5 + dy * 0.6,
            x0,
            y0,
        )
        chemin.closeSubpath()
        return chemin

    # avant-gauche + arrière-droite en phase ; avant-droite + arrière-gauche en opposition
    painter.drawPath(_nageoire(carapace_l * 0.30, -carapace_h * 0.55, True, battement))
    painter.drawPath(_nageoire(-carapace_l * 0.30, carapace_h * 0.50, False, battement))
    painter.drawPath(_nageoire(carapace_l * 0.30, carapace_h * 0.55, True, -battement))
    painter.drawPath(
        _nageoire(-carapace_l * 0.30, -carapace_h * 0.50, False, -battement)
    )

    # --- queue (courte, discrète) ---
    queue = QPainterPath()
    xq = -carapace_l * 0.48
    queue.moveTo(xq, 0)
    queue.lineTo(xq - taille * 0.08, -taille * 0.03)
    queue.lineTo(xq - taille * 0.08, taille * 0.03)
    queue.closeSubpath()
    painter.setBrush(QBrush(couleur_nageoire))
    painter.drawPath(queue)

    # --- tête + cou (dépasse à l'avant) ---
    tete_ondulation = math.sin(phase * 0.5) * taille * 0.015  # léger dandinement
    cou = QPainterPath()
    xc = carapace_l * 0.42
    cou.moveTo(xc - taille * 0.03, -taille * 0.06)
    cou.quadTo(
        xc + taille * 0.10,
        -taille * 0.05 + tete_ondulation,
        xc + taille * 0.16,
        tete_ondulation,
    )
    cou.quadTo(
        xc + taille * 0.10,
        taille * 0.05 + tete_ondulation,
        xc - taille * 0.03,
        taille * 0.06,
    )
    cou.closeSubpath()
    painter.setBrush(QBrush(couleur_nageoire))
    painter.drawPath(cou)

    # --- carapace (dôme avec dégradé pour l'effet de volume) ---
    if degrade:
        carapace_brush = QRadialGradient(
            QPointF(-carapace_l * 0.05, -carapace_h * 0.15), carapace_l * 0.6
        )
        carapace_brush.setColorAt(0.0, QColor(couleur).lighter(125))
        carapace_brush.setColorAt(1.0, QColor(couleur).darker(120))
        pinceau_carapace = QBrush(carapace_brush)
    else:
        pinceau_carapace = QBrush(couleur)
    painter.setBrush(pinceau_carapace)

    carapace = QPainterPath()
    carapace.addEllipse(QPointF(0, 0), carapace_l / 2, carapace_h / 2)
    painter.drawPath(carapace)

    # --- motif écailles de la carapace (petits hexagones simplifiés) ---
    motif_pen = QPen(trait)
    motif_pen.setWidthF(max(0.5, taille * 0.015))
    painter.setPen(motif_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    for ligne, dy in enumerate((-carapace_h * 0.20, 0.0, carapace_h * 0.20)):
        decalage = (carapace_l * 0.13) if ligne % 2 else 0.0
        for i in range(-2, 3):
            cx = i * carapace_l * 0.22 + decalage
            cy = dy
            # simple losange pour évoquer une écaille, seulement si dans l'ellipse
            if (cx / (carapace_l / 2)) ** 2 + (cy / (carapace_h / 2)) ** 2 < 0.75:
                ecaille = QPainterPath()
                r = taille * 0.045
                ecaille.moveTo(cx, cy - r)
                ecaille.lineTo(cx + r, cy)
                ecaille.lineTo(cx, cy + r)
                ecaille.lineTo(cx - r, cy)
                ecaille.closeSubpath()
                painter.drawPath(ecaille)

    # --- œil ---
    painter.setPen(Qt.PenStyle.NoPen)
    oeil_centre = QPointF(xc + taille * 0.10, -taille * 0.02 + tete_ondulation)
    oeil_r = taille * 0.028
    painter.setBrush(QBrush(QColor("#1c1f2b")))
    painter.drawEllipse(oeil_centre, oeil_r, oeil_r)
    painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
    painter.drawEllipse(
        QPointF(oeil_centre.x() + oeil_r * 0.2, oeil_centre.y() - oeil_r * 0.2),
        oeil_r * 0.25,
        oeil_r * 0.25,
    )

    painter.restore()
