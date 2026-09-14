################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones/_4_3_48_avion                                       #
# 4.3.48.3 – Classe de création d'un avion de chasse Dassault Rafale           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

from _4_Interface._4_3_Icones._4_3_48_avion._4_3_48_1_lumieres import (
    dessiner_lumiere_avion,
)

# 1 -- Fonctions de dessin d'un Rafale -----------------------------------------


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
    lumieres = kwargs.get("lumieres", False)
    lumieres_droite = kwargs.get("lumieres_droite", "#35FF70")
    lumieres_gauche = kwargs.get("lumieres_gauche", "#FF3030")
    lumieres_centre = kwargs.get("lumieres_centre", "#FFFFFF")

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

    # --------------------------------------------------------------------------
    # Lumières
    # --------------------------------------------------------------------------

    if lumieres == True:

        rayon_lumiere = l * 0.06

        # Gauche
        dessiner_lumiere_avion(
            painter,
            QPointF(
                cx - l * 0.22,
                cy - h * 0.465,
            ),
            lumieres_gauche,
            rayon_lumiere,
        )

        # Droite
        dessiner_lumiere_avion(
            painter,
            QPointF(
                cx - l * 0.22,
                cy + h * 0.465,
            ),
            lumieres_droite,
            rayon_lumiere,
        )

        # Centre
        dessiner_lumiere_avion(
            painter,
            QPointF(
                cx - l * 0.485,
                cy,
            ),
            lumieres_centre,
            rayon_lumiere * 0.8,
        )

    painter.restore()
