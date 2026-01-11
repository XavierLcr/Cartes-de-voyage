################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation/_2_1_5_table_caracteristiques/  #
# 2.1.5.2 – Script de nettoyage des données de tourisme                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os
import pandas as pd

from constantes import (
    direction_donnees_intermediaires,
    direction_donnees_brutes,
    direction_donnees_geographiques,
)
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


## 1.1 -- Table du tourisme ----------------------------------------------------


df_tourisme = pd.read_csv(
    os.path.join(direction_donnees_brutes, "API_ST.INT.ARVL_DS2_en_csv_v2_697553.csv"),
    skiprows=4,
)


## 1.2 -- Table du GADM (Granularité 1) ----------------------------------------


gdf_1 = ouvrir_fichier(
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_1.pkl",
    defaut=None,
    afficher_erreur="Table non trouvée...",
)[["name_0", "name_1"]]


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


# Récupération de la valeur la plus récente
df_tourisme["tourisme"] = derniere_valeur_valide_par_ligne(df=df_tourisme)

# Sélection des variables
df_tourisme = df_tourisme[["name_0", "tourisme"]]

# Suppression des lignes sans valeurs
df_tourisme.dropna(axis=0, subset=["tourisme"], inplace=True)


# Remplacement des noms de pays
df_tourisme = remplacer_valeurs_colonne(
    df=df_tourisme,
    colonne="name_0",
    mapping=mapping_pays,
)


# Test
valeurs_contenues(df1=df_tourisme, col1="name_0", df2=gdf_1, col2="name_0")


# 3 -- Export ------------------------------------------------------------------


# Test de granularité
assert isid(df=df_tourisme, colonnes="name_0", blabla=1)

exporter_fichier(
    objet=df_tourisme,
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="tourisme.pkl",
    sort_keys=True,
)
