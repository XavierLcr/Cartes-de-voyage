################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.4 – Pays visités le plus grand nombre de fois                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import pandas as pd
from collections import defaultdict
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    vider_layout,
)
from _0_Utilitaires._0_8_plot_diagramme_barres import plot_diagramme_barre

# 1 -- Fonction de comptage par pays -------------------------------------------


def compter_voyages_par_pays(dictionnaire_voyages):

    comptage_pays = defaultdict(int)

    for voyage_id, voyage in dictionnaire_voyages.items():

        # Ensemble pour éviter les doublons dans un même voyage
        pays_visites = set()

        # Boucle sur region/dep
        for granu in ["dep", "region"]:

            # Ajouter les pays présents
            for pays in voyage.get(granu, {}).keys():
                pays_visites.add(pays)

        # Incrémenter le compteur pour chaque pays unique du voyage
        for pays in pays_visites:
            comptage_pays[pays] += 1

    # Trier par ordre décroissant de voyages
    return pd.DataFrame(
        list(comptage_pays.items()), columns=["pays", "voyages"]
    ).sort_values(by="voyages", ascending=False, inplace=False)


# 2 -- Classe du graphique -----------------------------------------------------


class PaysLesPlusVisites(QWidget):

    def __init__(self, fct_traduction, parent=None):
        super().__init__(parent=None)

        self.langue = "français"
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
                titre=self.fct_traduction(
                    "titre_graphique_n_voyages",
                ),
                x_label="",
                y_label=self.fct_traduction(
                    "y_label_n_voyages",
                ),
                color_label="",
                palette=[
                    "#ADCEDB",
                ],
                figsize=(6, 3),
                wrap_ncol=3,
                y_decimales=0,
            )

            self.layout.addWidget(FigureCanvas(fig))
