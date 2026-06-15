################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation                                 #
# 2.1.3 – Fichier de création dela table des surfaces d'eau (lacs, ...)        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys

sys.path.append(os.getcwd())

from constantes import direction_donnees_intermediaires, direction_donnees_geographiques
from _0_Utilitaires._0_1_fonctions_utiles_gen import exporter_fichier, ouvrir_fichier

# 1 -- Import des données ------------------------------------------------------

gdf = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="geodataframe_propre.pkl",
    defaut=None,
    afficher_erreur="Fichier non trouvé",
)


# 2 -- Sélection des lignes faisant allusion à des étendues d'eau --------------


mask = (
    gdf[[f"ENGTYPE_{i}" for i in range(1, 6)]]
    .apply(lambda col: col.str.lower().isin(["water body", "waterbody"]))
    .any(axis=1)
)
gdf = gdf[mask]


# 3 -- Export ------------------------------------------------------------------


exporter_fichier(
    objet=gdf,
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_lacs.pkl",
)
