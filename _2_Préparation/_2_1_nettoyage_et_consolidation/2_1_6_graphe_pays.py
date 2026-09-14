################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation                                 #
# 2.1.6 – Graphe des pays                                                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys

sys.path.append(os.getcwd())

import geopandas as gpd
import pandas as pd

from constantes import (
    direction_donnees_geographiques,
    direction_donnees_application,
    direction_donnees_autres,
)
from _0_Utilitaires._0_1_fonctions_utiles_gen import ouvrir_fichier, exporter_fichier
from _0_Utilitaires._0_05_isid import isid

# 1 -- Import des données ------------------------------------------------------


gdf = ouvrir_fichier(
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_0.pkl",
    defaut=None,
).reset_index(drop=True)


# 2 -- Fonction de création du graphe ------------------------------------------


def construire_graphe_pays(
    gdf: gpd.GeoDataFrame,
    colonne_pays: str,
    epsg_calcul: int,
):
    """
    À partir d'un GeoDataFrame contenant un pays et sa géométrie :

    - calcule le centre de gravité de chaque pays ;
    - trouve tous les couples de pays partageant une frontière.

    Retourne
    --------
    centres : GeoDataFrame
        Colonnes :
            pays
            geometry   -> centroïde du pays

    voisins : DataFrame
        Colonnes :
            pays_1
            pays_2
    """

    gdf_temp = gdf[[colonne_pays, "geometry"]].copy()

    # --------------------------------------------------------------------------
    # 1 -- Nettoyage
    # --------------------------------------------------------------------------

    gdf_temp = gdf_temp.loc[
        gdf_temp.geometry.notna() & ~gdf_temp.geometry.is_empty
    ].copy()

    # --------------------------------------------------------------------------
    # 2 -- Centres de gravité
    # --------------------------------------------------------------------------

    crs_origine = gdf_temp.crs

    gdf_proj = gdf_temp.to_crs(epsg=epsg_calcul)

    centres = gpd.GeoDataFrame(
        {
            colonne_pays: gdf_proj[colonne_pays],
        },
        geometry=gdf_proj.geometry.centroid,
        crs=gdf_proj.crs,
    )

    centres = centres.to_crs(crs_origine)

    # --------------------------------------------------------------------------
    # 3 -- Pays voisins
    # --------------------------------------------------------------------------

    voisins = gpd.sjoin(
        gdf_temp[[colonne_pays, "geometry"]],
        gdf_temp[[colonne_pays, "geometry"]],
        how="inner",
        predicate="touches",
        lsuffix="1",
        rsuffix="2",
    )

    voisins = voisins[
        [
            f"{colonne_pays}_1",
            f"{colonne_pays}_2",
        ]
    ].copy()

    voisins.columns = [
        "pays_1",
        "pays_2",
    ]

    # --------------------------------------------------------------------------
    # 4 -- Suppression des doublons A-B / B-A
    # --------------------------------------------------------------------------

    voisins["couple"] = voisins.apply(
        lambda ligne: tuple(
            sorted(
                (
                    ligne["pays_1"],
                    ligne["pays_2"],
                )
            )
        ),
        axis=1,
    )

    voisins = (
        voisins.drop_duplicates(subset="couple")
        .drop(columns="couple")
        .reset_index(drop=True)
    )

    return centres, voisins


# 3 -- Application -------------------------------------------------------------


### Calcul des gentres et des arêtes -------------------------------------------


centres, voisins = construire_graphe_pays(
    gdf=gdf, colonne_pays="name_0", epsg_calcul=8857
)

# Test de granularité
assert isid(df=centres, colonnes="name_0", blabla=1)


### Formatage ------------------------------------------------------------------


graphe = {
    "centres": {
        ligne.name_0: (
            ligne.geometry.x,
            ligne.geometry.y,
        )
        for ligne in centres.itertuples(index=False)
    },
    "aretes": list(
        voisins[["pays_1", "pays_2"]].itertuples(
            index=False,
            name=None,
        )
    ),
}


# 4 -- Export ------------------------------------------------------------------


exporter_fichier(
    objet=graphe,
    direction_fichier=direction_donnees_application,
    nom_fichier="graphe_pays.pkl",
)
