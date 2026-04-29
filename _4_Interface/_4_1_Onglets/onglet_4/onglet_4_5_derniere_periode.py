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
)
from _0_Utilitaires._0_8_plot_diagramme_barres import plot_diagramme_barre


# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de transformation du dictionnaire en table générale ---------


def creer_table_derniers_voyages(
    dictionnaire: dict, date_min: str | None = None, date_max: str | None = None
):

    dict_temp = dictionnaire.copy()

    rows = []

    for voyage_id, infos in dict_temp.items():
        date_debut = infos.get("date_debut")
        date_fin = infos.get("date_fin")
        nom = infos.get("nom")

        # Récupérer tous les pays (dep + region)
        pays_region = set(infos.get("region", {}).keys())
        pays_dep = set(infos.get("dep", {}).keys())
        pays = pays_region.union(pays_dep)

        for p in pays:
            rows.append(
                {
                    "voyage_id": voyage_id,
                    "nom": nom,
                    "date_debut": date_debut,
                    "date_fin": date_fin,
                    "pays": p,
                }
            )

    # Mise au format data.frame
    df_temp = pd.DataFrame(rows)
    df_temp = df_temp[~df_temp["date_debut"].isna()]

    # Mise au format date
    df_temp["date_debut"] = pd.to_datetime(df_temp["date_debut"])
    df_temp["date_fin"] = pd.to_datetime(df_temp["date_fin"])

    # Ajout d'une colonne avec une liste de date
    df_temp["mois"] = df_temp.apply(
        lambda row: pd.date_range(
            start=row["date_debut"],
            end=row["date_fin"],
            freq="MS",  # début de chaque mois
        ),
        axis=1,
    )

    # Expansion de la table
    df_temp = df_temp.explode("mois").reset_index(drop=True)

    # Filtres sur les dates
    if date_min is not None:
        df_temp = df_temp[df_temp["mois"] >= pd.to_datetime(date_min)]
    if date_max is not None:
        df_temp = df_temp[df_temp["mois"] <= pd.to_datetime(date_max)]

    # Renvoi
    return df_temp


# 2 -- Classe PyQt6 ------------------------------------------------------------


class CalendrierVisite(QWidget):

    def __init__(self, constantes, fct_traduction, parent=None):
        super().__init__(parent=None)

        self.langue = "français"
        self.constantes = constantes
        self.fct_traduction = fct_traduction
        self.voyages = {}

        # Dates du graphique
        self.date_min = "2025-05-01"
        self.date_max = None

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

            df_temp = (
                creer_table_derniers_voyages(
                    dictionnaire=self.voyages,
                    date_min=self.date_min,
                    date_max=self.date_max,
                )[["mois", "nom"]]
                .drop_duplicates(inplace=False)
                .assign(
                    indicatrice=1, mois_str=lambda x: x["mois"].dt.strftime("%Y-%m")
                )
                .reset_index(drop=True, inplace=False)
            )

            fig = plot_diagramme_barre(
                # Création de la table
                df=df_temp,
                var_x="mois_str",
                var_y="indicatrice",
                var_color="nom",
                var_wrap=None,
                titre=self.fct_traduction(
                    "titre_graphique_calendrier_voyages",
                ),
                x_label="",
                y_label="",
                color_label="",
                # palette=[
                #     "#ADCEDB",
                # ],
                figsize=(6, 3),
                wrap_ncol=3,
                y_decimales=0,
                stack_vals=True,
            )

            self.layout.addWidget(FigureCanvas(fig))
