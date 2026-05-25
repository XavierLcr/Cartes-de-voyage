################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.5 – Voyages effectués sur la période la plus récente                #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    vider_layout,
    conteneur_graphique_simple,
)
from _0_Utilitaires._0_9_plot_diagramme_gantt import plot_diagramme_grantt

# 1 -- Classe PyQt6 ------------------------------------------------------------


class CalendrierVisite(QWidget):

    def __init__(self, fct_traduction, parent=None):
        super().__init__(parent=None)

        self.langue = "français"
        self.fct_traduction = fct_traduction
        self.voyages = {}

        # Dates du graphique
        self.date_max = pd.Timestamp.today().normalize()
        self.date_min = self.date_max - pd.DateOffset(years=1)

        # Style par défaut
        self.style = 1
        self.teinte = None
        self.nuances = {}

        self.layout = QVBoxLayout(self)

    def set_langue(self, langue: str):
        self.langue = langue
        self.creer_graphique()

    def set_voyages(self, voyages: dict):
        self.voyages = voyages
        self.creer_graphique()

    def set_style(self, style, teinte, nuances):
        self.style = style
        self.teinte = teinte
        self.nuances = nuances
        self.creer_graphique()

    def creer_graphique(self):

        vider_layout(layout=self.layout)

        if self.voyages:

            fig = plot_diagramme_grantt(
                data=self.voyages,
                voyage_label="nom",
                date_min_label="date_debut",
                date_max_label="date_fin",
                palette_couleurs=[
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
                date_min=self.date_min,
                date_max=self.date_max,
                titre=self.fct_traduction(
                    "titre_graphique_calendrier_voyages",
                ),
            )

            self.layout.addWidget(
                conteneur_graphique_simple(
                    fig=fig, style=self.style, teinte=self.teinte, nuances=self.nuances
                )
            )
