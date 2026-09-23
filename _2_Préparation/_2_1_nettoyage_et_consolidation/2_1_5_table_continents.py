################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation                                 #
# 2.1.5 – Tables à la granularité continent                                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys, math
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

sys.path.append(os.getcwd())

from constantes import (
    direction_donnees_geographiques,
    direction_donnees_application,
    liste_regions_monde,
)
from _0_Utilitaires._0_1_fonctions_utiles_gen import ouvrir_fichier, exporter_fichier
from _0_Utilitaires._0_05_isid import isid
from _0_Utilitaires._0_07_fonctions_voyages import table_pays_visites

# 1 -- Import des données ------------------------------------------------------


gdf = ouvrir_fichier(
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_0.pkl",
    defaut=None,
).reset_index(drop=True)

# Suppression de la Mer Caspienne
gdf = gdf[gdf["name_0"] != "Caspian Sea"]


# 2 -- Ajout du continent ------------------------------------------------------


df_continents = table_pays_visites(
    dict_granu={"region": {p: "" for p in gdf["name_0"].unique()}},
    continents=liste_regions_monde,
    palette={},
)[["continent", "pays"]]


# 3 -- Jointure ----------------------------------------------------------------


# Tests de granularité
assert isid(df=gdf, colonnes="name_0", blabla=0)
assert isid(df=df_continents, colonnes="pays", blabla=0)

# Jointure
gdf = gdf.merge(
    right=df_continents, left_on="name_0", right_on="pays", how="outer"
).reset_index(drop=True, inplace=False)

# Tests de réussite
assert (gdf["name_0"] == gdf["pays"]).all()
assert not (gdf["name_0"].isna()).any()
assert not (gdf["pays"].isna()).any()
assert not (gdf["continent"].isna()).any()

# Suppression des pays
gdf.drop(columns=["pays", "name_0"], inplace=True)


# 4 -- Conservation des frontières de continents uniquement --------------------


gdf = gdf[["continent", "geometry"]].dissolve(by="continent").reset_index()


# 5 -- Simplification de la geometry -------------------------------------------


## 5.1 -- Suppression des trop petits détails ----------------------------------


### Fonction associée ----------------------------------------------------------


def supprimer_petits_polygones(
    gdf: gpd.GeoDataFrame,
    pourcentage: float,
) -> gpd.GeoDataFrame:
    """
    Supprime les `pourcentage` % de polygones élémentaires ayant la plus
    petite superficie, sur l'ensemble du GeoDataFrame.

    Les MultiPolygon sont préalablement décomposés :
    chaque Polygon compte donc individuellement dans le classement global.

    Les lignes d'origine sont ensuite reconstruites :
        - 1 polygone restant  -> Polygon
        - plusieurs restants -> MultiPolygon
        - aucun restant      -> ligne supprimée

    Parameters
    ----------
    gdf : GeoDataFrame
        GeoDataFrame contenant des Polygon / MultiPolygon.
        Le CRS doit idéalement être projeté afin que `.area` soit pertinente.

    pourcentage : float
        Pourcentage du nombre total de polygones élémentaires à supprimer.
        Doit être compris entre 0 et 100.

    Returns
    -------
    GeoDataFrame
        Copie du GeoDataFrame avec les plus petits polygones supprimés.
    """

    if not 0 <= pourcentage < 100:
        raise ValueError(
            "`pourcentage` doit être compris entre 0 inclus et 100 exclus."
        )

    if gdf.empty:
        return gdf.copy()

    # ------------------------------------------------------------------
    # Copie + identifiant interne indépendant de l'index utilisateur
    # ------------------------------------------------------------------

    gdf_temp = gdf.copy()

    gdf_temp["_id_ligne_temp"] = range(len(gdf_temp))

    # ------------------------------------------------------------------
    # Décomposition de tous les MultiPolygon
    # ------------------------------------------------------------------

    morceaux = gdf_temp.explode(
        column="geometry",
        ignore_index=False,
    ).copy()

    # On ne conserve que les Polygon.
    morceaux = morceaux.loc[morceaux.geometry.geom_type == "Polygon"].copy()

    if morceaux.empty:
        return gdf.copy()

    # ------------------------------------------------------------------
    # Superficie de CHAQUE polygone élémentaire
    # ------------------------------------------------------------------

    morceaux["_superficie_temp"] = morceaux.geometry.area

    # ------------------------------------------------------------------
    # Nombre global de polygones à supprimer
    # ------------------------------------------------------------------

    nb_polygones = len(morceaux)

    nb_a_supprimer = math.floor(nb_polygones * pourcentage / 100)

    if nb_a_supprimer == 0:
        gdf_temp = gdf_temp.drop(columns="_id_ligne_temp")

        return gdf_temp

    # ------------------------------------------------------------------
    # Classement GLOBAL de tous les polygones
    # ------------------------------------------------------------------

    morceaux = morceaux.sort_values(
        "_superficie_temp",
        ascending=True,
    )

    # Suppression des n % plus petits
    morceaux = morceaux.iloc[nb_a_supprimer:].copy()

    # ------------------------------------------------------------------
    # Reconstruction des géométries par ligne d'origine
    # ------------------------------------------------------------------

    geometries_reconstruites = {}

    for id_ligne, groupe in morceaux.groupby("_id_ligne_temp"):

        polygones = list(groupe.geometry)

        if len(polygones) == 1:
            geometrie = polygones[0]

        else:
            geometrie = MultiPolygon(polygones)

        geometries_reconstruites[id_ligne] = geometrie

    # ------------------------------------------------------------------
    # Réinjection dans la table originale
    # ------------------------------------------------------------------

    gdf_temp["geometry"] = gdf_temp["_id_ligne_temp"].map(geometries_reconstruites)

    # Les lignes dont TOUS les polygones ont été supprimés disparaissent
    gdf_temp = gdf_temp.loc[gdf_temp.geometry.notna()].copy()

    gdf_temp = gdf_temp.drop(columns="_id_ligne_temp")

    return gpd.GeoDataFrame(
        gdf_temp,
        geometry="geometry",
        crs=gdf.crs,
    )


### Application ----------------------------------------------------------------


gdf_mini = gdf.copy(deep=True).to_crs("EPSG:8857")
gdf_mini = supprimer_petits_polygones(
    gdf=gdf_mini,
    pourcentage=50,
).to_crs("EPSG:4326")


## 5.2 -- Simplification des détails -------------------------------------------


# Tolérence
# En mètres si EPSG:8857
# En degrés si EPSG:4326
tolerance = 0.4

# Simplification
gdf_mini = gdf.to_crs("EPSG:4326")
gdf_mini["geometry"] = gdf_mini["geometry"].simplify(
    tolerance=tolerance,
)
gdf_mini = gdf_mini.to_crs("EPSG:4326")


# 3 -- Export ------------------------------------------------------------------


### Table des continents -------------------------------------------------------


# Test de granularite
assert isid(df=gdf, colonnes="continent", blabla=0)

# Export
exporter_fichier(
    objet=gdf,
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_continents.pkl",
)


### Table simplifiée des continents --------------------------------------------


# Test de granularite
assert isid(df=gdf_mini, colonnes="continent", blabla=0)

# Export
exporter_fichier(
    objet=gdf_mini,
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_continents_simpl.pkl",
)
