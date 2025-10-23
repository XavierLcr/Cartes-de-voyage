################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/                                                              #
# 2.2 – Fichier de création des YAMLs des granularités par pays                #
################################################################################


import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from constantes import (
    direction_donnees_autres,
    direction_donnees_application,
)
from _0_Utilitaires._0_1_Fonctions_utiles import ouvrir_fichier, cree_yaml_un_pays


for granularite in range(1, 6):

    print(granularite)

    cree_yaml_un_pays(
        # Import des données
        gdf=ouvrir_fichier(
            direction_fichier=direction_donnees_application,
            nom_fichier=f"carte_monde_niveau_{granularite}.pkl",
            defaut=None,
            afficher_erreur="Base non trouvée.",
        ),
        nom_pays=None,
        granularite=granularite,
        direction_fichier=direction_donnees_application,
        nom_fichier=f"liste_pays_granularite_{granularite}.yaml",
    )
