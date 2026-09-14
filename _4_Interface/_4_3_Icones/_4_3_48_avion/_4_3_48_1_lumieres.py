################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones/_4_3_48_avion                                       #
# 4.3.48.1 – Fonction de dessin de lumières d'avion                            #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QRadialGradient

# 1 -- Fonctions de dessin d'une lumière ---------------------------------------


def dessiner_lumiere_avion(
    painter: QPainter,
    centre: QPointF,
    couleur: QColor | str,
    rayon: float,
) -> None:
    """
    Dessine un feu d'avion avec un halo lumineux.
    """

    couleur = QColor(couleur)

    # Halo
    halo = QRadialGradient(
        centre,
        rayon,
    )

    couleur_centre = QColor(couleur)
    couleur_centre.setAlpha(190)

    couleur_bord = QColor(couleur)
    couleur_bord.setAlpha(0)

    halo.setColorAt(0.0, couleur_centre)
    halo.setColorAt(0.25, couleur_centre)
    halo.setColorAt(1.0, couleur_bord)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(halo))

    painter.drawEllipse(
        centre,
        rayon,
        rayon,
    )

    # Cœur lumineux
    coeur = couleur.lighter(160)
    coeur.setAlpha(255)

    painter.setBrush(coeur)

    painter.drawEllipse(
        centre,
        rayon * 0.18,
        rayon * 0.18,
    )
