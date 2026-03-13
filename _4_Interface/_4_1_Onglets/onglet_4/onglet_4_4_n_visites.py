################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.4 – Pays visités le plus grand nombre de fois                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import copy
import numpy as np
import pandas as pd
from collections import defaultdict
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QScrollArea,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from _0_Utilitaires._0_1_fonctions_utiles_gen import distance_haversine
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    creer_QLabel_centre,
    creer_ligne_horizontale,
    vider_layout,
)
from _0_Utilitaires._0_8_plot_diagramme_barres import plot_diagramme_barre

from _4_Interface._4_2_Style._4_2_2_styles_complementaires import (
    style_bouton_recommandation,
)


# 1 -- Fonction de comptage par pays -------------------------------------------


def compter_voyages_par_pays(dictionnaire_voyages):

    comptage_pays = defaultdict(int)

    for voyage_id, voyage in dictionnaire_voyages.items():
        # Ensemble pour éviter les doublons dans un même voyage
        pays_visites = set()

        # Ajouter les pays de 'region'
        regions = voyage.get("region", {})
        for pays in regions.keys():
            pays_visites.add(pays)

        # Ajouter les pays de 'dep'
        dep = voyage.get("dep", {})
        for pays in dep.keys():
            pays_visites.add(pays)

        # Incrémenter le compteur pour chaque pays unique du voyage
        for pays in pays_visites:
            comptage_pays[pays] += 1

    # Trier par ordre décroissant de voyages
    return pd.DataFrame(
        sorted(comptage_pays.items(), key=lambda item: item[1], reverse=True),
        columns=["pays", "voyages"],
    )


# 2 -- Classe du graphique -----------------------------------------------------


class PaysLesPlusVisites(QWidget):

    def __init__(self, constantes, fct_traduction, parent=None):
        super().__init__(parent=None)

        self.langue = "français"
        self.constantes = constantes
        self.fct_traduction = fct_traduction
        self.voyages = {}

        self.layout = QVBoxLayout(self)

    def set_langue(self, langue: str):
        self.langue = langue
        self.creer_graphique()

    def set_voyages(self, voyages: dict):
        self.voyages = voyages
        self.creer_graphique()

    def creer_graphique(self):

        vider_layout(layout=self.layout)

        if self.voyages:

            fig = plot_diagramme_barre(
                df=compter_voyages_par_pays(self.voyages).head(n=5),
                var_x="pays",
                var_y="voyages",
                var_color=None,
                var_wrap=None,
                titre="Pays ayant été le plus visités",
                x_label="",
                y_label="Nombre de visites",
                color_label="",
                palette=[
                    "#7DC8E8",
                    "#F5E474",
                    "#E15759",
                    "#76B7B2",
                    "#59A14F",
                    "#EDC948",
                    "#B07AA1",
                    "#FF9DA7",
                    "#9C755F",
                    "#BAB0AC",
                ],
                figsize=(6, 4),
                wrap_ncol=3,
                y_decimales=0,
            )

            self.layout.addWidget(FigureCanvas(fig))
