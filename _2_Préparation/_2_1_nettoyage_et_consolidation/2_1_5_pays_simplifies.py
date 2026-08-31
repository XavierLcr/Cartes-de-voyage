################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation                                 #
# 2.1.5 – Version simplifiée de la table à la granularité 0                    #
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
from _0_Utilitaires._0_05_isid import isid

# 1 -- Import des données ------------------------------------------------------


gdf = ouvrir_fichier(
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_0.pkl",
    defaut=None,
).reset_index(drop=True)


# 2 -- Simplification de la geometry -------------------------------------------


gdf["geometry"] = gdf["geometry"].simplify(tolerance=0.0001)


# 3 -- Export ------------------------------------------------------------------


# Test de granularite
assert isid(df=gdf, colonnes="name_0", blabla=0)

# Export
exporter_fichier(
    objet=gdf,
    direction_fichier=direction_donnees_application,
    nom_fichier="carte_monde_niveau_0_simplifiee.pkl",
)
