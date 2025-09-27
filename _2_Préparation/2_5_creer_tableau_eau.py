################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/                                                              #
# 2.5 – Fichier de création dela table des surfaces d'eau (lacs, ...)          #
################################################################################


import os, sys
import geopandas as gpd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constantes
from _0_Utilitaires._0_1_Fonctions_utiles import exporter_fichier


# 1 -- Import des données ------------------------------------------------------

gdf = gpd.read_file(
    os.path.join(constantes.direction_donnees, "_1_1_Données_brutes", "gadm_410.gpkg")
).rename(columns={f"NAME_{i}": f"name_{i}" for i in range(6)})


# 2 -- Sélection des lignes faisant allusion à des étendues d'eau --------------


mask = (
    gdf[[f"ENGTYPE_{i}" for i in range(1, 6)]]
    .apply(lambda col: col.str.lower().isin(["water body", "waterbody"]))
    .any(axis=1)
)


# 3 -- Export ------------------------------------------------------------------


exporter_fichier(
    objet=gdf[mask],
    direction_fichier=constantes.direction_donnees_geographiques,
    nom_fichier="carte_monde_lacs.pkl",
)
