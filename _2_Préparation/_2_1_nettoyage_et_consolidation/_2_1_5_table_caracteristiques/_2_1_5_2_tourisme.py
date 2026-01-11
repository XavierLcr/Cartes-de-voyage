################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation/_2_1_5_table_caracteristiques/  #
# 2.1.5.2 – Script de nettoyage des données de tourisme                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os
import pandas as pd

from constantes import direction_donnees_intermediaires, direction_donnees_brutes
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_fichier,
    exporter_fichier,
)
from _0_Utilitaires._0_4_fonctions_utiles_nettoyage import (
    mapping_pays,
    remplacer_valeurs_colonne,
    valeurs_contenues,
    nettoyer_nom_colonne,
    derniere_valeur_valide_par_ligne,
)
from _0_Utilitaires._0_5_isid import isid


# 1 -- Import des données ------------------------------------------------------


df_tourisme = pd.read_csv(
    os.path.join(direction_donnees_brutes, "API_ST.INT.ARVL_DS2_en_csv_v2_697553.csv"),
    skiprows=4,
)


# 2 -- Nettoyage des données ---------------------------------------------------


# Suppression des colonnes constantes et NA
df_tourisme = df_tourisme.loc[:, df_tourisme.nunique(dropna=False) > 1]
df_tourisme.dropna(axis=1, how="all", inplace=True)

# Nettoyage des noms de colonnes
df_tourisme.columns = [nettoyer_nom_colonne(col) for col in df_tourisme.columns]
df_tourisme.rename(
    columns={
        "country name": "name_0",
    },
    inplace=True,
)


# récupération de la valeur la plus récente
df_tourisme["tourisme"] = derniere_valeur_valide_par_ligne(df=df_tourisme)

# Sélection des variables
df_tourisme = df_tourisme[["name_0", "tourisme"]]

# Suppression des lignes sans valeurs
df_tourisme.dropna(axis=0, subset=["tourisme"], inplace=True)


# 3 -- Export ------------------------------------------------------------------


# Test de granularité
assert isid(df=df_tourisme, colonnes="name_0", blabla=1)

exporter_fichier(
    objet=df_tourisme,
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="tourisme.pkl",
    sort_keys=True,
)
