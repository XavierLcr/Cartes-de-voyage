################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.5 – Voyages effectués sur la période la plus récente                #
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


# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de transformation du dictionnaire en table générale ---------


def creer_table_derniers_voyages(dictionnaire: dict):

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

    df_temp = pd.DataFrame(rows)
    # Filtre sur les dates

    return pd.DataFrame(rows)


## 1.2 -- Création de la table finale ------------------------------------------


# 2 -- Classe PyQt6 ------------------------------------------------------------
