################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.42 – Script de création d'étoiles                                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math
import random
import time

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QColor, QBrush, QPainter, QPainterPath

# 1 -- Fonction de création d'une étoile ---------------------------------------


def _dessiner_une_etoile(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    couleur: QColor | str = "#FFF4C2",
    rotation: float = 0.0,
    phase: float = 0.0,
    scintillement: bool = True,
) -> None:
    """
    Dessine une petite étoile à quatre branches.
    """

    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    couleur = QColor(couleur)

    # -- Scintillement ---------------------------------------------------------

    if scintillement:
        luminosite = 100 + 15 * (0.5 + 0.5 * math.sin(phase))
        couleur = couleur.lighter(int(luminosite))

    # -- Rotation --------------------------------------------------------------

    painter.translate(centre)
    painter.rotate(math.degrees(rotation))

    # -- Forme -----------------------------------------------------------------

    rayon_exterieur = taille * 0.50
    rayon_interieur = taille * 0.16

    etoile = QPainterPath()

    for i in range(8):

        angle = -math.pi / 2 + i * math.pi / 4
        rayon = rayon_exterieur if i % 2 == 0 else rayon_interieur

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
    painter.setBrush(QBrush(couleur))
    painter.drawPath(etoile)

    painter.restore()


# 2 -- Classe de gestion d'un ensemble d'étoiles -------------------------------


class Etoiles:
    """
    Gère la génération et le dessin d'un ensemble d'étoiles animées.

    Les positions et tailles sont stockées sous forme de ratios afin que
    l'ensemble s'adapte automatiquement aux dimensions de la zone dessinée.
    """

    def __init__(
        self,
        n: int = 20,
        couleur: QColor | str = "#FFF4C2",
        x_min: float = 0.04,
        x_max: float = 0.96,
        y_min: float = 0.04,
        y_max: float = 0.38,
        taille_min: float = 0.02,
        taille_max: float = 0.036,
        vitesse_min: float = 0.4,
        vitesse_max: float = 2.2,
    ) -> None:

        self.n = n
        self.couleur = QColor(couleur)

        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

        self.taille_min = taille_min
        self.taille_max = taille_max

        self.vitesse_min = vitesse_min
        self.vitesse_max = vitesse_max

        self.etoiles = []

        self.generer()

    # --------------------------------------------------------------------------
    # Génération
    # --------------------------------------------------------------------------

    def generer(self) -> None:
        """Génère un nouvel ensemble d'étoiles avec les paramètres définis."""

        rng = random.Random()

        self.etoiles = [
            {
                "x_ratio": rng.uniform(self.x_min, self.x_max),
                "y_ratio": rng.uniform(self.y_min, self.y_max),
                "taille_ratio": rng.uniform(
                    self.taille_min,
                    self.taille_max,
                ),
                "phase_offset": rng.uniform(
                    0.0,
                    2.0 * math.pi,
                ),
                "vitesse": rng.uniform(
                    self.vitesse_min,
                    self.vitesse_max,
                ),
                "rotation": rng.uniform(
                    0.0,
                    2.0 * math.pi,
                ),
            }
            for _ in range(self.n)
        ]

    # --------------------------------------------------------------------------
    # Dessin
    # --------------------------------------------------------------------------

    def dessiner_etoiles(
        self,
        painter: QPainter,
        rect: QRectF,
        side: float,
        opacite: float = 1.0,
    ) -> None:
        """Dessine toutes les étoiles dans la zone indiquée."""

        if opacite <= 0.0:
            return

        t = time.monotonic()

        painter.save()

        for etoile in self.etoiles:

            centre = QPointF(
                rect.left() + etoile["x_ratio"] * rect.width(),
                rect.top() + etoile["y_ratio"] * rect.height(),
            )

            taille = etoile["taille_ratio"] * side
            phase = etoile["phase_offset"] + t * etoile["vitesse"]

            # -- Scintillement --------------------------------------------------

            onde = math.sin(phase)
            intensite = 0.15 + 0.85 * (0.5 + 0.5 * onde) ** 2

            taille_effective = taille * (0.85 + 0.15 * intensite)

            painter.setOpacity(opacite * intensite)

            _dessiner_une_etoile(
                painter=painter,
                centre=centre,
                taille=taille_effective,
                couleur=self.couleur,
                rotation=etoile["rotation"],
                scintillement=False,
            )

        painter.restore()
