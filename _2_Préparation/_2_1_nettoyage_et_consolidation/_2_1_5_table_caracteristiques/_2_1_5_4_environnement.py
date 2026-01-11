################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation/_2_1_5_table_caracteristiques/  #
# 2.1.5.4 – Script de nettoyage des données environnementales                  #
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


# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Import et nettoyage d'une table --------------------------------------


def importer_table_environnement(
    direction: str, nom: str, suffixe: str
) -> pd.DataFrame:

    df_temp = remplacer_valeurs_colonne(
        df=pd.read_csv(
            os.path.join(
                direction,
                nom,
            )
        ),
        colonne="country",
        mapping=mapping_pays,
    )

    df_temp.columns = [nettoyer_nom_colonne(col) for col in df_temp.columns]
    df_temp.rename(columns={"country": "name_0"}, inplace=True)
    df_temp[f"environnement_{suffixe}"] = derniere_valeur_valide_par_ligne(df_temp)
    df_temp = df_temp[["name_0", f"environnement_{suffixe}"]]

    return df_temp


## 1.2 -- Import de multiples tables -------------------------------------------


def importer_tables_environnement(direction: str, prefixes: list):

    # Création de la liste des fichiers à ouvir
    fichiers = {}
    for f in os.listdir(direction):
        # CSV uniquement
        if f.endswith(".csv"):
            for prefixe in prefixes:
                if f.startswith(prefixe):
                    fichiers[prefixe] = f
                    # Un fichier par préfixe
                    break

    for i, (prefixe, nom_fichier) in enumerate(fichiers.items()):

        print(prefixe)

        # Table d'un préfixe
        df_temp = importer_table_environnement(
            direction=direction, nom=nom_fichier, suffixe=prefixe
        )

        # Initialiser df_environnement avec le premier DataFrame
        if i == 0:
            df_environnement = df_temp.copy()
        # Jointures avec les DataFrames suivants
        else:
            df_environnement = df_environnement.merge(
                right=df_temp, on="name_0", how="outer"
            )

    return df_environnement


# 2 -- Autres imports ----------------------------------------------------------


gdf_1 = ouvrir_fichier(
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_1.pkl",
    defaut=None,
    afficher_erreur="Table non trouvée...",
)[["name_0", "name_1"]]


# 3 -- Application -------------------------------------------------------------


# Création de la table
df_env = importer_tables_environnement(
    direction=os.path.join(
        direction_donnees_brutes,
        "Environnement",
    ),
    prefixes=["RMS", "FCL", "WWR", "UWD", "PAR"],
)

# Suppression des lignes sans données
df_env = df_env.dropna(
    subset=[col for col in df_env.columns if col != "name_0"], how="all"
)

# Vérification des pays non inclus dans la table du GADM
# Hong Kong et Macao
valeurs_contenues(df1=df_env, col1="name_0", df2=gdf_1, col2="name_0")


# 4 -- Export ------------------------------------------------------------------


# Test de granularité
assert isid(df=df_env, colonnes="name_0", blabla=1)

exporter_fichier(
    objet=df_env,
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="environnement.pkl",
    sort_keys=True,
)
