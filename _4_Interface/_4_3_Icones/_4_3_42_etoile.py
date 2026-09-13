################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.42 – Script de création d'une étoile                                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QColor
from PyQt6.QtCore import Qt, QPointF

# 1 -- Fonction de création de l'étoile ---------------------------------------


def _dessiner_etoile(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    couleur: QColor = None,
    rotation: float = 0.0,
    phase: float = 0.0,
    scintillement: bool = True,
) -> None:
    """
    Dessine une petite étoile à quatre branches.

    Paramètres
    ----------
    painter :
        QPainter utilisé pour le dessin.

    centre :
        Position du centre de l'étoile.

    taille :
        Taille globale de l'étoile.

    couleur :
        Couleur de l'étoile.

    rotation :
        Rotation de l'étoile en radians.

    phase :
        Phase utilisée pour animer légèrement le scintillement.

    scintillement :
        Si True, la luminosité de l'étoile varie légèrement avec la phase.
    """

    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    if couleur is None:
        couleur = QColor("#FFF4C2")

    # -- Scintillement ---------------------------------------------------------

    if scintillement:
        luminosite = 100 + 15 * (0.5 + 0.5 * math.sin(phase))
        couleur_etoile = QColor(couleur).lighter(int(luminosite))
    else:
        couleur_etoile = QColor(couleur)

    # -- Rotation --------------------------------------------------------------

    painter.translate(centre)
    painter.rotate(math.degrees(rotation))

    # -- Forme -----------------------------------------------------------------

    rayon_exterieur = taille * 0.50
    rayon_interieur = taille * 0.16

    etoile = QPainterPath()

    # 4 branches principales + 4 creux intermédiaires
    for i in range(8):

        angle = -math.pi / 2 + i * math.pi / 4

        if i % 2 == 0:
            rayon = rayon_exterieur
        else:
            rayon = rayon_interieur

        point = QPointF(
            math.cos(angle) * rayon,
            math.sin(angle) * rayon,
        )

        if i == 0:
            etoile.moveTo(point)
        else:
            etoile.lineTo(point)

    etoile.closeSubpath()

    # -- Dessin ----------------------------------------------------------------

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(couleur_etoile))
    painter.drawPath(etoile)

    painter.restore()
