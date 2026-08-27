################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4.1.1 – Classe de création d'un point                                 #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


import math

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QRadialGradient

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import _QColor_avec_alpha

# 1 -- Classe de création d'un point -------------------------------------------


class PointPays:
    """
    Représente un point de l'hémicycle correspondant à un pays donné.

    Cette classe porte à la fois les données du point (position, couleurs,
    nom traduit, etc.) et la logique qui lui est propre : dessin et
    détection du survol par la souris.
    """

    def __init__(
        self,
        x: float,
        y: float,
        pays: str,
        pays_trad: str,
        continent: str,
        visite: bool,
        couleur: str,
        eclaircissement: int,
    ):
        self.x = x
        self.y = y
        self.pays = pays
        self.pays_trad = pays_trad
        self.continent = continent
        self.visite = visite
        self.couleur_bord = QColor(couleur)
        self.couleur_centre = _QColor_avec_alpha(
            couleur=self.couleur_bord, alpha=255 if visite else eclaircissement
        )

    def est_survole(
        self, pos_x: float, pos_y: float, diametre: float, tolerance: float = 1.1
    ) -> bool:
        """Indique si la position (pos_x, pos_y) se trouve dans la zone de survol du point."""
        distance = math.hypot(pos_x - self.x, pos_y - self.y)
        return distance <= diametre * tolerance

    def peindre(
        self,
        painter: QPainter,
        diametre: float,
        epaisseur_bord: float,
        survole: bool = False,
        facteur_survol: float = 1.4,
    ):
        """Dessine le point sur le painter fourni, en le grossissant si survole=True."""

        diametre_affiche = diametre * facteur_survol if survole else diametre

        # Dégradé radial très subtil, juste pour donner un peu de volume
        gradient = QRadialGradient(
            QPointF(self.x - diametre_affiche * 0.25, self.y - diametre_affiche * 0.25),
            diametre_affiche * 1.3,
        )
        gradient.setColorAt(0.0, self.couleur_centre.lighter(120))
        gradient.setColorAt(1.0, self.couleur_centre)

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self.couleur_bord, epaisseur_bord))
        painter.drawEllipse(
            QPointF(self.x, self.y),
            diametre_affiche,
            diametre_affiche,
        )
