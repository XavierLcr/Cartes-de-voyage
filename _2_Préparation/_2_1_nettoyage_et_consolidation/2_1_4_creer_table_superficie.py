################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation                                 #
# 2.1.4 – Fichier de création de la table de superficie utile à l'onglet n°4   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys

sys.path.append(os.getcwd())

from constantes import (
    direction_donnees_geographiques,
    direction_donnees_application,
    direction_donnees_autres,
)
from _0_Utilitaires._0_1_fonctions_utiles_gen import ouvrir_fichier, exporter_fichier
from _0_Utilitaires._0_5_isid import isid

# 1 -- Import des données ------------------------------------------------------


gdf = ouvrir_fichier(
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_2.pkl",
    defaut=None,
).reset_index(drop=True)


# Colonnes de granularité
cols = [col for col in gdf.columns if col.startswith("name_")]


# 1 -- Fonction de création de la table des pourcentages de superficie ---------


def calculer_superficie(gdf, epsg):

    return (
        gdf.copy()
        .to_crs(epsg=epsg)
        .assign(
            # Statistiques par niveau le plus fin
            superficie=lambda x: x.geometry.area,
            perimetre=lambda x: x.geometry.length,
            # Statistiques nationales
            superficie_par_pays=lambda x: x.groupby("name_0")["superficie"].transform(
                "sum"
            ),
            pct_superficie_dans_pays=lambda x: x["superficie"]
            / x["superficie_par_pays"],
        )
        # Suppression de colonnes inutiles
        .drop(columns=["geometry", "superficie_par_pays"])
    )


# 2 -- Application -------------------------------------------------------------


gdf = (
    calculer_superficie(gdf=gdf, epsg=8857)
    .sort_values(by=cols, inplace=False)
    .reset_index(drop=True, inplace=False)
)


# 3 -- Export ------------------------------------------------------------------


# Test de granularité
assert isid(df=gdf, colonnes=cols, blabla=1)

# Export de la table à utiliser dans l'application
exporter_fichier(
    objet=gdf,
    direction_fichier=direction_donnees_application,
    nom_fichier="table_superficie.pkl",
)

# Export de la table visualisable
exporter_fichier(
    objet=gdf,
    direction_fichier=direction_donnees_autres,
    nom_fichier="table_superficie.xlsx",
)
