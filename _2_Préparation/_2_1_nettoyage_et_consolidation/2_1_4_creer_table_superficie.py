################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation                                 #
# 2.1.4 – Fichier de création de la table de superficie utile à l'onglet n°4   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys

sys.path.append(os.getcwd())

import constantes
from _0_Utilitaires._0_1_fonctions_utiles_gen import ouvrir_fichier, exporter_fichier


# 1 -- Import des données ------------------------------------------------------


gdf = ouvrir_fichier(
    direction_fichier=constantes.direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_2.pkl",
    defaut=None,
).reset_index(drop=True)


# 1 -- Fonction de création de la table des pourcentages de superficie ---------


def calculer_superficie(gdf, epsg):

    return (
        gdf.copy()
        .to_crs(epsg=epsg)
        .assign(
            superficie=lambda x: x.geometry.area,
            superficie_par_pays=lambda x: x.groupby("name_0")["superficie"].transform(
                "sum"
            ),
            pct_superficie_dans_pays=lambda x: x["superficie"]
            / x["superficie_par_pays"],
        )
        .drop(columns=["geometry", "superficie_par_pays"])
    )


# 2 -- Application -------------------------------------------------------------


gdf = calculer_superficie(gdf=gdf, epsg=8857)


# 3 -- Export ------------------------------------------------------------------


exporter_fichier(
    objet=gdf,
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="table_superficie.pkl",
)
