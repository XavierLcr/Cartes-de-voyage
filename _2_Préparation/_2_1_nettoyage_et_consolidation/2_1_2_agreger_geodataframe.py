################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation                                 #
# 2.1.2 – Fichier d'agrégation de la table des données géographiques           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys, copy
import geopandas as gpd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from constantes import direction_donnees_geographiques, direction_donnees_intermediaires
from _0_Utilitaires._0_1_fonctions_utiles_gen import exporter_fichier, ouvrir_fichier


# 1 -- Import des données ------------------------------------------------------


gdf = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="geodataframe_propre.pkl",
    defaut=None,
)


# 2 -- Fonctions ---------------------------------------------------------------


## 2.1 -- Fonction d'agrégation  -----------------------------------------------


def agreger_table(
    gdf, direction: str | None, nom_fichier: str | None, variables: list | str
):

    # Homogénéisation des variables passées
    if isinstance(variables, str):
        variables = [variables]

    gdf_temp = (
        copy.deepcopy(gdf)[variables + ["geometry"]]
        .dissolve(by=variables)
        .reset_index()
    )

    if direction and nom_fichier:

        exporter_fichier(
            objet=gdf_temp,
            direction_fichier=direction,
            nom_fichier=nom_fichier,
            sort_keys=True,
        )

    else:
        return gdf_temp


## 2.2 -- Fonction générale ----------------------------------------------------


def main(gdf, direction: str):

    for granularite in range(6):

        print(f"Début d'agrégation : granularité {granularite}")

        agreger_table(
            gdf=gdf,
            direction=direction,
            nom_fichier=f"carte_monde_niveau_{granularite}.pkl",
            variables=[f"name_{i}" for i in range(granularite + 1)],
        )

        print("Terminé.", end="\n" * 2)


# 3 -- Application -------------------------------------------------------------


main(gdf=gpd, direction=direction_donnees_geographiques)
