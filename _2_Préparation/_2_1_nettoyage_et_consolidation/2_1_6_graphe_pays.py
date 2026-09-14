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
import math


from pyproj import CRS, Geod

from constantes import (
    direction_donnees_geographiques,
    direction_donnees_application,
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


_GEOD = Geod(ellps="WGS84")


## 2.1 -- Renvoyer polygone ----------------------------------------------------


def _iterer_polygones(geometry):
    """
    Renvoie récursivement les polygones contenus dans une géométrie.
    """

    if geometry.geom_type == "Polygon":

        yield geometry

    elif geometry.geom_type in (
        "MultiPolygon",
        "GeometryCollection",
    ):

        for geom in geometry.geoms:

            yield from _iterer_polygones(geom)


## 2.2 -- Calcul de la longitude moyenne ---------------------------------------


def _longitude_centrale(
    geometry,
) -> float:
    """
    Calcule une longitude centrale en tenant compte du caractère cyclique
    des longitudes.

    Ainsi, +179° et -179° sont considérés comme voisins et non comme étant
    séparés de 358°.
    """

    somme_cos = 0.0
    somme_sin = 0.0
    somme_poids = 0.0

    for polygone in _iterer_polygones(geometry):

        # Point situé à l'intérieur de la composante
        point = polygone.representative_point()

        longitude = math.radians(point.x)

        # Pondération par la superficie géodésique de la composante
        aire, _ = _GEOD.geometry_area_perimeter(polygone)

        poids = abs(aire)

        if poids <= 0:
            poids = 1.0

        somme_cos += poids * math.cos(longitude)
        somme_sin += poids * math.sin(longitude)

        somme_poids += poids

    if somme_poids == 0:

        return 0.0

    longitude = math.degrees(
        math.atan2(
            somme_sin,
            somme_cos,
        )
    )

    return longitude


## 2.3 -- Calcul du centroïde d'un pays ----------------------------------------


def _calculer_centroide_pays(
    geometry,
    crs_origine,
):
    """
    Calcule le centroïde d'un pays dans une projection Equal Earth dont
    le méridien central est adapté au pays.

    Cela évite notamment les erreurs pour les pays traversant
    l'antiméridien : Kiribati, Fidji, Russie, etc.
    """

    # ----------------------------------------------------------------------
    # Passage en WGS84
    # ----------------------------------------------------------------------

    serie = gpd.GeoSeries(
        [geometry],
        crs=crs_origine,
    ).to_crs(4326)

    geometry_wgs84 = serie.iloc[0]

    # ----------------------------------------------------------------------
    # Méridien central optimal
    # ----------------------------------------------------------------------

    longitude_centrale = _longitude_centrale(
        geometry=geometry_wgs84,
    )

    # ----------------------------------------------------------------------
    # Equal Earth recentrée sur le pays
    # ----------------------------------------------------------------------

    crs_local = CRS.from_proj4(
        f"+proj=eqearth "
        f"+lon_0={longitude_centrale} "
        f"+datum=WGS84 "
        f"+units=m "
        f"+no_defs"
    )

    geometry_proj = gpd.GeoSeries(
        [geometry_wgs84],
        crs=4326,
    ).to_crs(crs_local)

    centroide_proj = geometry_proj.centroid.iloc[0]

    # ----------------------------------------------------------------------
    # Retour dans le CRS d'origine
    # ----------------------------------------------------------------------

    centroide = (
        gpd.GeoSeries(
            [centroide_proj],
            crs=crs_local,
        )
        .to_crs(crs_origine)
        .iloc[0]
    )

    return centroide


# --------------------------------------------------------------------------
# Construction du graphe
# --------------------------------------------------------------------------


## 2.4 -- Fonction de création du résultat -------------------------------------


def construire_graphe_pays(
    gdf: gpd.GeoDataFrame,
    colonne_pays: str,
):
    """
    À partir d'un GeoDataFrame contenant un pays et sa géométrie :

    - calcule le centre de gravité de chaque pays ;
    - trouve tous les couples de pays partageant une frontière.

    Le calcul des centres tient compte de l'antiméridien.

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

    gdf_temp = gdf[
        [
            colonne_pays,
            "geometry",
        ]
    ].copy()

    # --------------------------------------------------------------------------
    # 1 -- Nettoyage
    # --------------------------------------------------------------------------

    gdf_temp = gdf_temp.loc[
        gdf_temp.geometry.notna() & ~gdf_temp.geometry.is_empty
    ].copy()

    crs_origine = gdf_temp.crs

    # --------------------------------------------------------------------------
    # 2 -- Centres de gravité
    # --------------------------------------------------------------------------

    centres_geometries = [
        _calculer_centroide_pays(
            geometry=geometry,
            crs_origine=crs_origine,
        )
        for geometry in gdf_temp.geometry
    ]

    centres = gpd.GeoDataFrame(
        {
            colonne_pays: gdf_temp[colonne_pays].values,
        },
        geometry=centres_geometries,
        crs=crs_origine,
    )

    # --------------------------------------------------------------------------
    # 3 -- Pays voisins
    # --------------------------------------------------------------------------

    voisins = gpd.sjoin(
        gdf_temp[
            [
                colonne_pays,
                "geometry",
            ]
        ],
        gdf_temp[
            [
                colonne_pays,
                "geometry",
            ]
        ],
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
    gdf=gdf,
    colonne_pays="name_0",
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
