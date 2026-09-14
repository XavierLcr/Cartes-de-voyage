################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.48 – Classe de création d'un avion                                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import random
import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPen

# 1 -- Fonctions de dessin d'un avion ------------------------------------------


## 1.1 -- Avion de ligne -------------------------------------------------------


def _dessiner_avion_ligne(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    rotation: float = 0.0,
    **kwargs,
) -> None:
    """
    Dessine un gros avion de ligne stylisé vu de dessus,
    inspiré des proportions d'un Airbus A380.

    `rotation` est exprimée en degrés.
    """

    if taille <= 0:
        return

    couleur = QColor(kwargs.get("couleur", "#E8ECEF"))
    couleur_secondaire = QColor(kwargs.get("couleur_secondaire", "#AAB4BC"))
    couleur_vitre = QColor(kwargs.get("couleur_vitre", "#496778"))
    couleur_moteur = QColor(kwargs.get("couleur_moteur", "#D7DDE1"))
    couleur_entree_moteur = QColor(kwargs.get("couleur_entree_moteur", "#4D5961"))

    # L'A380 possède une très grande envergure.
    longueur = taille
    envergure = taille * 0.90

    rect = QRectF(
        centre.x() - longueur / 2,
        centre.y() - envergure / 2,
        longueur,
        envergure,
    )

    painter.save()

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing,
        True,
    )

    painter.translate(centre)
    painter.rotate(rotation)
    painter.translate(-centre)

    cx = centre.x()
    cy = centre.y()

    l = longueur
    h = envergure

    painter.setPen(Qt.PenStyle.NoPen)

    # --------------------------------------------------------------------------
    # Réacteurs
    # --------------------------------------------------------------------------

    def dessiner_moteur(
        x: float,
        y: float,
        echelle: float = 1.0,
    ) -> None:

        longueur_moteur = l * 0.105 * echelle
        largeur_moteur = h * 0.055 * echelle

        # Petit pylône reliant le moteur à l'aile
        pylone = QPainterPath()

        pylone.moveTo(
            x - longueur_moteur * 0.15,
            y,
        )

        pylone.lineTo(
            x - longueur_moteur * 0.35,
            y - largeur_moteur * 0.90,
        )

        pylone.lineTo(
            x + longueur_moteur * 0.18,
            y - largeur_moteur * 0.45,
        )

        pylone.closeSubpath()

        painter.setBrush(couleur_secondaire.darker(105))

        painter.drawPath(pylone)

        # Nacelle
        moteur = QPainterPath()

        moteur.moveTo(
            x + longueur_moteur / 2,
            y,
        )

        moteur.cubicTo(
            x + longueur_moteur * 0.38,
            y - largeur_moteur / 2,
            x - longueur_moteur * 0.32,
            y - largeur_moteur / 2,
            x - longueur_moteur / 2,
            y,
        )

        moteur.cubicTo(
            x - longueur_moteur * 0.32,
            y + largeur_moteur / 2,
            x + longueur_moteur * 0.38,
            y + largeur_moteur / 2,
            x + longueur_moteur / 2,
            y,
        )

        moteur.closeSubpath()

        gradient_moteur = QLinearGradient(
            x,
            y - largeur_moteur / 2,
            x,
            y + largeur_moteur / 2,
        )

        gradient_moteur.setColorAt(
            0.0,
            couleur_moteur.lighter(125),
        )

        gradient_moteur.setColorAt(
            0.5,
            couleur_moteur,
        )

        gradient_moteur.setColorAt(
            1.0,
            couleur_moteur.darker(115),
        )

        painter.setBrush(QBrush(gradient_moteur))
        painter.drawPath(moteur)

        # Entrée sombre du réacteur
        rayon = largeur_moteur * 0.31

        painter.setBrush(couleur_entree_moteur)

        painter.drawEllipse(
            QPointF(
                x + longueur_moteur * 0.39,
                y,
            ),
            rayon,
            rayon,
        )

        # Centre de la turbine
        painter.setBrush(couleur_entree_moteur.lighter(150))

        painter.drawEllipse(
            QPointF(
                x + longueur_moteur * 0.40,
                y,
            ),
            rayon * 0.30,
            rayon * 0.30,
        )

    # Deux réacteurs par aile
    positions_moteurs = (
        (cx + l * 0.045, cy - h * 0.155),
        (cx - l * 0.025, cy - h * 0.305),
        (cx + l * 0.045, cy + h * 0.155),
        (cx - l * 0.025, cy + h * 0.305),
    )

    for x, y in positions_moteurs:
        dessiner_moteur(
            x,
            y,
        )

    # --------------------------------------------------------------------------
    # Ailes
    # --------------------------------------------------------------------------

    ailes = QPainterPath()

    # Aile supérieure
    ailes.moveTo(
        cx + l * 0.13,
        cy - h * 0.040,
    )

    # Bord d'attaque : très balayé vers l'arrière
    ailes.lineTo(
        cx - l * 0.12,
        cy - h * 0.46,
    )

    # Saumon d'aile
    ailes.cubicTo(
        cx - l * 0.15,
        cy - h * 0.485,
        cx - l * 0.19,
        cy - h * 0.48,
        cx - l * 0.20,
        cy - h * 0.455,
    )

    # Bord de fuite
    ailes.lineTo(
        cx - l * 0.12,
        cy - h * 0.20,
    )

    ailes.lineTo(
        cx - l * 0.20,
        cy - h * 0.055,
    )

    ailes.lineTo(
        cx + l * 0.13,
        cy - h * 0.040,
    )

    ailes.closeSubpath()

    # Aile inférieure
    ailes.moveTo(
        cx + l * 0.13,
        cy + h * 0.040,
    )

    ailes.lineTo(
        cx - l * 0.12,
        cy + h * 0.46,
    )

    ailes.cubicTo(
        cx - l * 0.15,
        cy + h * 0.485,
        cx - l * 0.19,
        cy + h * 0.48,
        cx - l * 0.20,
        cy + h * 0.455,
    )

    ailes.lineTo(
        cx - l * 0.12,
        cy + h * 0.20,
    )

    ailes.lineTo(
        cx - l * 0.20,
        cy + h * 0.055,
    )

    ailes.lineTo(
        cx + l * 0.13,
        cy + h * 0.040,
    )

    ailes.closeSubpath()

    gradient_ailes = QLinearGradient(
        cx,
        cy - h / 2,
        cx,
        cy + h / 2,
    )

    gradient_ailes.setColorAt(
        0.0,
        couleur_secondaire.lighter(118),
    )

    gradient_ailes.setColorAt(
        0.5,
        couleur_secondaire,
    )

    gradient_ailes.setColorAt(
        1.0,
        couleur_secondaire.darker(108),
    )

    painter.setBrush(QBrush(gradient_ailes))
    painter.drawPath(ailes)

    # --------------------------------------------------------------------------
    # Empennage horizontal
    # --------------------------------------------------------------------------

    empennage = QPainterPath()

    # Partie supérieure
    empennage.moveTo(
        cx - l * 0.34,
        cy - h * 0.028,
    )

    empennage.lineTo(
        cx - l * 0.45,
        cy - h * 0.20,
    )

    empennage.cubicTo(
        cx - l * 0.47,
        cy - h * 0.22,
        cx - l * 0.49,
        cy - h * 0.21,
        cx - l * 0.48,
        cy - h * 0.18,
    )

    empennage.lineTo(
        cx - l * 0.415,
        cy - h * 0.025,
    )

    empennage.closeSubpath()

    # Partie inférieure
    empennage.moveTo(
        cx - l * 0.34,
        cy + h * 0.028,
    )

    empennage.lineTo(
        cx - l * 0.45,
        cy + h * 0.20,
    )

    empennage.cubicTo(
        cx - l * 0.47,
        cy + h * 0.22,
        cx - l * 0.49,
        cy + h * 0.21,
        cx - l * 0.48,
        cy + h * 0.18,
    )

    empennage.lineTo(
        cx - l * 0.415,
        cy + h * 0.025,
    )

    empennage.closeSubpath()

    painter.setBrush(couleur_secondaire)
    painter.drawPath(empennage)

    # --------------------------------------------------------------------------
    # Fuselage
    # --------------------------------------------------------------------------

    fuselage = QPainterPath()

    # Pointe avant arrondie
    fuselage.moveTo(
        cx + l * 0.50,
        cy,
    )

    # Flanc supérieur
    fuselage.cubicTo(
        cx + l * 0.485,
        cy - h * 0.025,
        cx + l * 0.44,
        cy - h * 0.043,
        cx + l * 0.36,
        cy - h * 0.050,
    )

    fuselage.cubicTo(
        cx + l * 0.15,
        cy - h * 0.060,
        cx - l * 0.15,
        cy - h * 0.060,
        cx - l * 0.34,
        cy - h * 0.045,
    )

    # Rétrécissement vers la queue
    fuselage.cubicTo(
        cx - l * 0.41,
        cy - h * 0.038,
        cx - l * 0.46,
        cy - h * 0.020,
        cx - l * 0.49,
        cy,
    )

    fuselage.cubicTo(
        cx - l * 0.46,
        cy + h * 0.020,
        cx - l * 0.41,
        cy + h * 0.038,
        cx - l * 0.34,
        cy + h * 0.045,
    )

    fuselage.cubicTo(
        cx - l * 0.15,
        cy + h * 0.060,
        cx + l * 0.15,
        cy + h * 0.060,
        cx + l * 0.36,
        cy + h * 0.050,
    )

    fuselage.cubicTo(
        cx + l * 0.44,
        cy + h * 0.043,
        cx + l * 0.485,
        cy + h * 0.025,
        cx + l * 0.50,
        cy,
    )

    fuselage.closeSubpath()

    gradient_fuselage = QLinearGradient(
        cx,
        cy - h * 0.07,
        cx,
        cy + h * 0.07,
    )

    gradient_fuselage.setColorAt(
        0.0,
        couleur.lighter(125),
    )

    gradient_fuselage.setColorAt(
        0.48,
        couleur,
    )

    gradient_fuselage.setColorAt(
        1.0,
        couleur.darker(115),
    )

    painter.setBrush(QBrush(gradient_fuselage))
    painter.drawPath(fuselage)

    # --------------------------------------------------------------------------
    # Cockpit
    # --------------------------------------------------------------------------

    cockpit = QPainterPath()

    cockpit.moveTo(
        cx + l * 0.455,
        cy,
    )

    cockpit.cubicTo(
        cx + l * 0.440,
        cy - h * 0.018,
        cx + l * 0.410,
        cy - h * 0.025,
        cx + l * 0.390,
        cy - h * 0.019,
    )

    cockpit.lineTo(
        cx + l * 0.405,
        cy,
    )

    cockpit.lineTo(
        cx + l * 0.390,
        cy + h * 0.019,
    )

    cockpit.cubicTo(
        cx + l * 0.410,
        cy + h * 0.025,
        cx + l * 0.440,
        cy + h * 0.018,
        cx + l * 0.455,
        cy,
    )

    cockpit.closeSubpath()

    painter.setBrush(couleur_vitre)
    painter.drawPath(cockpit)

    # --------------------------------------------------------------------------
    # Double rangée de hublots
    # --------------------------------------------------------------------------

    if taille >= 70:

        couleur_hublots = couleur_vitre.darker(115)

        painter.setBrush(couleur_hublots)

        rayon_hublot = max(
            0.7,
            l * 0.0040,
        )

        n_hublots = 18

        x_debut = cx - l * 0.27
        x_fin = cx + l * 0.32

        for i in range(n_hublots):

            t = i / (n_hublots - 1)

            x = x_debut + (x_fin - x_debut) * t

            # Deux ponts de l'A380 suggérés par
            # deux lignes de petits hublots.
            for y in (
                cy - h * 0.020,
                cy + h * 0.020,
            ):

                painter.drawEllipse(
                    QPointF(x, y),
                    rayon_hublot,
                    rayon_hublot * 0.65,
                )

    painter.restore()


## 1.2 -- Rafale ---------------------------------------------------------------


def _dessiner_rafale(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    rotation: float = 0.0,
    **kwargs,
) -> None:
    """
    Dessine un Rafale stylisé vu de dessus.

    L'avion pointe vers la droite lorsque rotation = 0.
    """

    if taille <= 0:
        return

    couleur = QColor(kwargs.get("couleur", "#AAB4C2"))
    couleur_secondaire = QColor(kwargs.get("couleur_secondaire", "#758291"))
    couleur_vitre = QColor(kwargs.get("couleur_vitre", "#253B4D"))

    longueur = taille
    hauteur = taille * 0.72

    rect = QRectF(
        centre.x() - longueur / 2,
        centre.y() - hauteur / 2,
        longueur,
        hauteur,
    )

    painter.save()

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing,
        True,
    )

    painter.translate(centre)
    painter.rotate(rotation)
    painter.translate(-centre)

    painter.setPen(Qt.PenStyle.NoPen)

    cx = rect.center().x()
    cy = rect.center().y()

    l = rect.width()
    h = rect.height()

    # --------------------------------------------------------------------------
    # Ailes delta
    # --------------------------------------------------------------------------

    ailes = QPainterPath()

    # Partie supérieure
    ailes.moveTo(
        cx + l * 0.08,
        cy - h * 0.055,
    )

    ailes.lineTo(
        cx - l * 0.28,
        cy - h * 0.47,
    )

    ailes.lineTo(
        cx - l * 0.42,
        cy - h * 0.47,
    )

    ailes.lineTo(
        cx - l * 0.39,
        cy - h * 0.12,
    )

    ailes.lineTo(
        cx - l * 0.32,
        cy - h * 0.065,
    )

    # Partie arrière centrale
    ailes.lineTo(
        cx - l * 0.43,
        cy,
    )

    # Partie inférieure
    ailes.lineTo(
        cx - l * 0.32,
        cy + h * 0.065,
    )

    ailes.lineTo(
        cx - l * 0.39,
        cy + h * 0.12,
    )

    ailes.lineTo(
        cx - l * 0.42,
        cy + h * 0.47,
    )

    ailes.lineTo(
        cx - l * 0.28,
        cy + h * 0.47,
    )

    ailes.lineTo(
        cx + l * 0.08,
        cy + h * 0.055,
    )

    ailes.closeSubpath()

    gradient_ailes = QLinearGradient(
        cx,
        cy - h * 0.5,
        cx,
        cy + h * 0.5,
    )

    gradient_ailes.setColorAt(
        0.0,
        couleur.lighter(118),
    )

    gradient_ailes.setColorAt(
        0.48,
        couleur,
    )

    gradient_ailes.setColorAt(
        1.0,
        couleur.darker(112),
    )

    painter.setBrush(QBrush(gradient_ailes))
    painter.drawPath(ailes)

    # --------------------------------------------------------------------------
    # Bord de fuite des ailes
    # --------------------------------------------------------------------------

    pen_bord = QPen(
        couleur_secondaire,
        max(0.5, taille * 0.006),
    )

    pen_bord.setCapStyle(
        Qt.PenCapStyle.RoundCap,
    )

    painter.setPen(pen_bord)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    painter.drawLine(
        QPointF(
            cx - l * 0.28,
            cy - h * 0.47,
        ),
        QPointF(
            cx - l * 0.39,
            cy - h * 0.12,
        ),
    )

    painter.drawLine(
        QPointF(
            cx - l * 0.28,
            cy + h * 0.47,
        ),
        QPointF(
            cx - l * 0.39,
            cy + h * 0.12,
        ),
    )

    painter.setPen(Qt.PenStyle.NoPen)

    # --------------------------------------------------------------------------
    # Plans canards
    # --------------------------------------------------------------------------

    canards = QPainterPath()

    # Canard supérieur
    canards.moveTo(
        cx + l * 0.22,
        cy - h * 0.045,
    )

    canards.lineTo(
        cx + l * 0.08,
        cy - h * 0.22,
    )

    canards.lineTo(
        cx - l * 0.015,
        cy - h * 0.205,
    )

    canards.lineTo(
        cx + l * 0.11,
        cy - h * 0.035,
    )

    canards.closeSubpath()

    # Canard inférieur
    canards.moveTo(
        cx + l * 0.22,
        cy + h * 0.045,
    )

    canards.lineTo(
        cx + l * 0.08,
        cy + h * 0.22,
    )

    canards.lineTo(
        cx - l * 0.015,
        cy + h * 0.205,
    )

    canards.lineTo(
        cx + l * 0.11,
        cy + h * 0.035,
    )

    canards.closeSubpath()

    painter.setBrush(
        couleur.lighter(108),
    )

    painter.drawPath(canards)

    # --------------------------------------------------------------------------
    # Fuselage
    # --------------------------------------------------------------------------

    fuselage = QPainterPath()

    # Pointe très fine du Rafale
    fuselage.moveTo(
        cx + l * 0.50,
        cy,
    )

    fuselage.cubicTo(
        cx + l * 0.43,
        cy - h * 0.020,
        cx + l * 0.34,
        cy - h * 0.040,
        cx + l * 0.26,
        cy - h * 0.052,
    )

    # Zone cockpit / épaules
    fuselage.cubicTo(
        cx + l * 0.19,
        cy - h * 0.065,
        cx + l * 0.11,
        cy - h * 0.080,
        cx + l * 0.03,
        cy - h * 0.075,
    )

    # Entrées d'air / corps central
    fuselage.cubicTo(
        cx - l * 0.07,
        cy - h * 0.105,
        cx - l * 0.17,
        cy - h * 0.105,
        cx - l * 0.27,
        cy - h * 0.085,
    )

    # Zone moteurs
    fuselage.lineTo(
        cx - l * 0.44,
        cy - h * 0.065,
    )

    fuselage.lineTo(
        cx - l * 0.48,
        cy - h * 0.045,
    )

    fuselage.lineTo(
        cx - l * 0.49,
        cy,
    )

    fuselage.lineTo(
        cx - l * 0.48,
        cy + h * 0.045,
    )

    fuselage.lineTo(
        cx - l * 0.44,
        cy + h * 0.065,
    )

    fuselage.lineTo(
        cx - l * 0.27,
        cy + h * 0.085,
    )

    fuselage.cubicTo(
        cx - l * 0.17,
        cy + h * 0.105,
        cx - l * 0.07,
        cy + h * 0.105,
        cx + l * 0.03,
        cy + h * 0.075,
    )

    fuselage.cubicTo(
        cx + l * 0.11,
        cy + h * 0.080,
        cx + l * 0.19,
        cy + h * 0.065,
        cx + l * 0.26,
        cy + h * 0.052,
    )

    fuselage.cubicTo(
        cx + l * 0.34,
        cy + h * 0.040,
        cx + l * 0.43,
        cy + h * 0.020,
        cx + l * 0.50,
        cy,
    )

    fuselage.closeSubpath()

    gradient_fuselage = QLinearGradient(
        cx,
        cy - h * 0.12,
        cx,
        cy + h * 0.12,
    )

    gradient_fuselage.setColorAt(
        0.0,
        couleur.lighter(132),
    )

    gradient_fuselage.setColorAt(
        0.40,
        couleur.lighter(110),
    )

    gradient_fuselage.setColorAt(
        0.60,
        couleur,
    )

    gradient_fuselage.setColorAt(
        1.0,
        couleur.darker(120),
    )

    painter.setBrush(
        QBrush(gradient_fuselage),
    )

    painter.drawPath(fuselage)

    # --------------------------------------------------------------------------
    # Entrées d'air
    # --------------------------------------------------------------------------

    entrees_air = QPainterPath()

    # Supérieure
    entrees_air.moveTo(
        cx + l * 0.08,
        cy - h * 0.072,
    )

    entrees_air.cubicTo(
        cx + l * 0.01,
        cy - h * 0.115,
        cx - l * 0.10,
        cy - h * 0.125,
        cx - l * 0.18,
        cy - h * 0.095,
    )

    entrees_air.lineTo(
        cx - l * 0.09,
        cy - h * 0.070,
    )

    entrees_air.closeSubpath()

    # Inférieure
    entrees_air.moveTo(
        cx + l * 0.08,
        cy + h * 0.072,
    )

    entrees_air.cubicTo(
        cx + l * 0.01,
        cy + h * 0.115,
        cx - l * 0.10,
        cy + h * 0.125,
        cx - l * 0.18,
        cy + h * 0.095,
    )

    entrees_air.lineTo(
        cx - l * 0.09,
        cy + h * 0.070,
    )

    entrees_air.closeSubpath()

    couleur_entree = couleur_secondaire.darker(165)

    painter.setBrush(
        couleur_entree,
    )

    painter.drawPath(entrees_air)

    # --------------------------------------------------------------------------
    # Cockpit
    # --------------------------------------------------------------------------

    cockpit = QPainterPath()

    cockpit.moveTo(
        cx + l * 0.35,
        cy,
    )

    cockpit.cubicTo(
        cx + l * 0.31,
        cy - h * 0.040,
        cx + l * 0.21,
        cy - h * 0.052,
        cx + l * 0.15,
        cy - h * 0.035,
    )

    cockpit.cubicTo(
        cx + l * 0.12,
        cy - h * 0.020,
        cx + l * 0.12,
        cy + h * 0.020,
        cx + l * 0.15,
        cy + h * 0.035,
    )

    cockpit.cubicTo(
        cx + l * 0.21,
        cy + h * 0.052,
        cx + l * 0.31,
        cy + h * 0.040,
        cx + l * 0.35,
        cy,
    )

    cockpit.closeSubpath()

    gradient_cockpit = QLinearGradient(
        cx + l * 0.18,
        cy - h * 0.05,
        cx + l * 0.31,
        cy + h * 0.04,
    )

    gradient_cockpit.setColorAt(
        0.0,
        couleur_vitre.lighter(155),
    )

    gradient_cockpit.setColorAt(
        0.40,
        couleur_vitre,
    )

    gradient_cockpit.setColorAt(
        1.0,
        couleur_vitre.darker(160),
    )

    painter.setBrush(
        QBrush(gradient_cockpit),
    )

    painter.drawPath(cockpit)

    # --------------------------------------------------------------------------
    # Deux tuyères
    # --------------------------------------------------------------------------

    largeur_tuyere = h * 0.042
    hauteur_tuyere = h * 0.052

    for decalage in (-h * 0.034, h * 0.034):

        rect_tuyere = QRectF(
            cx - l * 0.49,
            cy + decalage - hauteur_tuyere / 2,
            l * 0.050,
            hauteur_tuyere,
        )

        gradient_tuyere = QLinearGradient(
            rect_tuyere.left(),
            rect_tuyere.top(),
            rect_tuyere.right(),
            rect_tuyere.bottom(),
        )

        gradient_tuyere.setColorAt(
            0.0,
            couleur_secondaire.lighter(115),
        )

        gradient_tuyere.setColorAt(
            0.50,
            couleur_secondaire.darker(190),
        )

        gradient_tuyere.setColorAt(
            1.0,
            couleur_secondaire.darker(240),
        )

        painter.setBrush(
            QBrush(gradient_tuyere),
        )

        painter.drawRoundedRect(
            rect_tuyere,
            largeur_tuyere * 0.25,
            largeur_tuyere * 0.25,
        )

    # --------------------------------------------------------------------------
    # Dérive centrale
    # --------------------------------------------------------------------------

    # Vue de dessus : elle doit rester très fine, contrairement à une aile.
    derive = QPainterPath()

    derive.moveTo(
        cx - l * 0.17,
        cy,
    )

    derive.lineTo(
        cx - l * 0.43,
        cy - h * 0.018,
    )

    derive.lineTo(
        cx - l * 0.52,
        cy,
    )

    derive.lineTo(
        cx - l * 0.43,
        cy + h * 0.018,
    )

    derive.closeSubpath()

    painter.setBrush(
        couleur_secondaire.lighter(108),
    )

    painter.drawPath(derive)

    # --------------------------------------------------------------------------
    # Rails / missiles en bout d'aile
    # --------------------------------------------------------------------------

    painter.setPen(
        QPen(
            couleur_secondaire.darker(135),
            max(1.0, taille * 0.012),
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
        )
    )

    for sens in (-1, 1):

        y = cy + sens * h * 0.475

        painter.drawLine(
            QPointF(
                cx - l * 0.43,
                y,
            ),
            QPointF(
                cx - l * 0.25,
                y,
            ),
        )

        # Pointe du missile
        painter.drawLine(
            QPointF(
                cx - l * 0.25,
                y,
            ),
            QPointF(
                cx - l * 0.22,
                y,
            ),
        )

    # --------------------------------------------------------------------------
    # Quelques lignes de structure
    # --------------------------------------------------------------------------

    couleur_lignes = QColor(
        couleur_secondaire,
    )

    couleur_lignes.setAlpha(75)

    painter.setPen(
        QPen(
            couleur_lignes,
            max(0.4, taille * 0.003),
        )
    )

    # Racines des ailes
    painter.drawLine(
        QPointF(
            cx - l * 0.04,
            cy - h * 0.075,
        ),
        QPointF(
            cx - l * 0.36,
            cy - h * 0.38,
        ),
    )

    painter.drawLine(
        QPointF(
            cx - l * 0.04,
            cy + h * 0.075,
        ),
        QPointF(
            cx - l * 0.36,
            cy + h * 0.38,
        ),
    )

    painter.restore()


## 2.3 -- Dictionnaire des fonctions -------------------------------------------


_AVIONS_MODELES = {
    "ligne": _dessiner_avion_ligne,
    "rafale": _dessiner_rafale,
}


# 2 -- Classe de gestion de l'avion --------------------------------------------


class Avion:
    """
    Gère un avion animé suivant un chemin passant par plusieurs points.

    Le chemin commence hors de la zone à gauche, passe par tous les points
    fournis, puis ressort hors de la zone à droite.
    """

    def __init__(
        self,
        taille: float = 42.0,
        vitesse: float = 120.0,
        tension: float = 0.80,
        marge_sortie: float = 50.0,
        anticipation_rotation: float = 60.0,
        graine: int | None = None,
    ) -> None:

        self.taille = taille
        self.vitesse = vitesse
        self.tension = tension
        self.marge_sortie = marge_sortie
        self.anticipation_rotation = anticipation_rotation
        self.repeter_en_boucle = False

        self._rng = random.Random(graine)

        self._y_entree = self._rng.uniform(
            0.15,
            0.85,
        )

        self._y_sortie = self._rng.uniform(
            0.15,
            0.85,
        )

        self._distance = 0.0
        self._longueur_chemin = 0.0

    # 2.1 -- Nouveau passage ----------------------------------------------------

    def _nouveau_passage(self) -> None:

        self._distance = 0.0

        self._y_entree = self._rng.uniform(
            0.15,
            0.85,
        )

        self._y_sortie = self._rng.uniform(
            0.15,
            0.85,
        )

    # 2.2 -- Construction du chemin --------------------------------------------

    def _creer_chemin_lisse(
        self,
        points: list[QPointF],
    ) -> QPainterPath:
        """
        Crée un chemin passant par tous les points avec des virages arrondis,
        sans créer les boucles que peut produire une spline Catmull-Rom.
        """

        chemin = QPainterPath()

        if not points:
            return chemin

        if len(points) == 1:
            chemin.moveTo(points[0])
            return chemin

        chemin.moveTo(points[0])

        # Plus cette valeur est grande, plus les virages sont arrondis.
        # On reste volontairement sous 0.5 pour éviter les boucles.
        arrondi = max(
            0.0,
            min(0.45, self.tension * 0.45),
        )

        for i in range(1, len(points) - 1):

            precedent = points[i - 1]
            courant = points[i]
            suivant = points[i + 1]

            # Distances avec les points voisins
            distance_avant = math.hypot(
                courant.x() - precedent.x(),
                courant.y() - precedent.y(),
            )

            distance_apres = math.hypot(
                suivant.x() - courant.x(),
                suivant.y() - courant.y(),
            )

            if distance_avant <= 0 or distance_apres <= 0:
                chemin.lineTo(courant)
                continue

            # Point où commence l'arrondi avant le point courant
            entree = QPointF(
                courant.x() - (courant.x() - precedent.x()) * arrondi,
                courant.y() - (courant.y() - precedent.y()) * arrondi,
            )

            # Point où se termine l'arrondi après le point courant
            sortie = QPointF(
                courant.x() + (suivant.x() - courant.x()) * arrondi,
                courant.y() + (suivant.y() - courant.y()) * arrondi,
            )

            chemin.lineTo(entree)

            # Courbe quadratique autour du point réellement visité
            chemin.quadTo(
                courant,
                sortie,
            )

        chemin.lineTo(points[-1])

        return chemin

    def creer_chemin(
        self,
        points_passage: list[QPointF],
        rect_zone: QRectF,
    ) -> QPainterPath:
        """
        Ajoute automatiquement les points d'entrée et de sortie au chemin.
        """

        hauteur = rect_zone.height()

        entree = QPointF(
            rect_zone.left() - self.marge_sortie,
            rect_zone.top() + hauteur * self._y_entree,
        )

        sortie = QPointF(
            rect_zone.right() + self.marge_sortie,
            rect_zone.top() + hauteur * self._y_sortie,
        )

        points = [
            entree,
            *points_passage,
            sortie,
        ]

        return self._creer_chemin_lisse(points)

    # 2.3 -- Animation ----------------------------------------------------------

    def animer(
        self,
        delta_s: float,
    ) -> None:
        """Fait avancer l'avion selon sa vitesse."""

        if self._longueur_chemin <= 0:
            return

        self._distance += self.vitesse * delta_s

        if self._distance >= self._longueur_chemin:

            if self.repeter_en_boucle == True:
                self._nouveau_passage()
            else:
                self._distance = self._longueur_chemin

    # 2.4 -- Dessin -------------------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        points_passage: list[QPointF],
        rect_zone: QRectF,
        **kwargs,
    ) -> None:
        """Construit le chemin courant et dessine l'avion dessus."""

        chemin = self.creer_chemin(
            points_passage=points_passage,
            rect_zone=rect_zone,
        )

        self._longueur_chemin = chemin.length()

        if self._longueur_chemin <= 0:
            return

        distance = min(
            self._distance,
            self._longueur_chemin,
        )

        progression = chemin.percentAtLength(distance)
        position = chemin.pointAtPercent(progression)

        distance_avant = max(
            0.0,
            distance - self.anticipation_rotation,
        )
        distance_apres = min(
            self._longueur_chemin,
            distance + self.anticipation_rotation,
        )

        t_avant = chemin.percentAtLength(distance_avant)
        t_apres = chemin.percentAtLength(distance_apres)

        point_avant = chemin.pointAtPercent(t_avant)
        point_apres = chemin.pointAtPercent(t_apres)

        dx = point_apres.x() - point_avant.x()
        dy = point_apres.y() - point_avant.y()

        rotation = math.degrees(
            math.atan2(
                dy,
                dx,
            )
        )

        # Fonction de dessin
        modele_temp = kwargs.get("modele") or "ligne"
        _fonction_temp = _AVIONS_MODELES.get(modele_temp, _dessiner_avion_ligne)

        _fonction_temp(
            painter=painter,
            centre=position,
            taille=self.taille,
            rotation=rotation,
            **kwargs,
        )
