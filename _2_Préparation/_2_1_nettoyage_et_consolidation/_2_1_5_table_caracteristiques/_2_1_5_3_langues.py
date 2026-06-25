################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation/_2_1_5_table_caracteristiques/  #
# 2.1.5.3 – Script de nettoyage des correspondances linguistiques              #
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


## 1.1 -- Table des correspondances linguistiques ------------------------------


df_langues = pd.read_csv(
    os.path.join(
        direction_donnees_brutes,
        "DICL_v2.csv",
    ),
)


## 1.2 -- Table du GADM (Granularité 1) ----------------------------------------


gdf_1 = ouvrir_fichier(
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_1.pkl",
    defaut=None,
    afficher_erreur="Table non trouvée...",
)[["name_0", "name_1"]]


# 2 -- Nettoyage des données ---------------------------------------------------


df_langues = (
    df_langues[["country_i", "country_j", "csl"]]
    .pipe(remplacer_valeurs_colonne, colonne="country_i", mapping=mapping_pays)
    .pipe(remplacer_valeurs_colonne, colonne="country_j", mapping=mapping_pays)
    .assign(
        country_j=lambda x: x["country_j"]
        .str.lower()
        .str.strip()
        .str.replace(r"[^a-zA-Z0-9_]", "", regex=True)
    )
    .pivot(index="country_i", columns="country_j", values="csl")
    .add_prefix("langue_")
    .dropna(axis=1, how="all", inplace=False)
    .reset_index()
    .rename(columns={"country_i": "name_0"}, inplace=False)
)


# Test – Macao et Hong Kong
valeurs_contenues(df1=df_langues, col1="name_0", df2=gdf_1, col2="name_0")


# 3 -- Export ------------------------------------------------------------------


assert isid(df=df_langues, colonnes=["name_0"], blabla=1)

exporter_fichier(
    objet=df_langues,
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="langues.pkl",
    sort_keys=True,
)
