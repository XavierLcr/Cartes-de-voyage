################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.4 – Pays visités le plus grand nombre de fois                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import pandas as pd
from collections import defaultdict
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    vider_layout,
    conteneur_graphique_simple,
)
from _0_Utilitaires._0_8_plot_diagramme_barres import plot_diagramme_barre

# 1 -- Fonctions utiles --------------------------------------------------------


## 1.1 -- Fonction de comptage par pays ----------------------------------------


def compter_voyages_par_pays(
    dictionnaire_voyages: dict, traductions: dict, langue: str
):

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
    return (
        pd.DataFrame(list(comptage_pays.items()), columns=["pays", "voyages"])
        .sort_values(by="voyages", ascending=False, inplace=False)
        .reset_index(drop=True, inplace=False)
        # Ajout de la traduction des pays
        .assign(
            pays_traduction=lambda x: x["pays"].apply(
                lambda y: traductions.get(y, {}).get(langue, y)
            )
        )
    )


# 2 -- Classe du graphique -----------------------------------------------------


class PaysLesPlusVisites(QWidget):

    def __init__(self, constantes, fct_traduction, parent=None):

        super().__init__(parent=None)

        # Variables globales
        self.langue = "français"
        self.fct_traduction = fct_traduction
        self.voyages = {}
        self.n_pays = 5
        self.n_pays_limite = 1
        self.pays_trad = constantes.pays_differentes_langues

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

            fig = plot_diagramme_barre(
                df=compter_voyages_par_pays(
                    self.voyages, traductions=self.pays_trad, langue=self.langue
                ).head(n=5),
                var_x="pays_traduction",
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

            self.layout.addWidget(
                conteneur_graphique_simple(
                    fig=fig, style=self.style, teinte=self.teinte, nuances=self.nuances
                )
            )
