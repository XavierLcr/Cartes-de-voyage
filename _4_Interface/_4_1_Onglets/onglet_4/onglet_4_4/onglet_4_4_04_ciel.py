################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_4                                #
# Onglet 4.4.3 – Classe du ciel                                                #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QLinearGradient, QPainter, QBrush


class Ciel:
    """Dessine le ciel de la scène."""

    def dessiner(
        self,
        painter: QPainter,
        rect: QRectF,
        theme,
    ) -> None:

        degrade = QLinearGradient(
            rect.left(),
            rect.top(),
            rect.left(),
            rect.bottom(),
        )

        degrade.setColorAt(0.0, theme.couleur("ciel_haut"))
        degrade.setColorAt(0.55, theme.couleur("ciel_milieu"))
        degrade.setColorAt(1.0, theme.couleur("ciel_bas"))

        painter.fillRect(
            rect,
            QBrush(degrade),
        )
