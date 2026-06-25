################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_3_tests/                                                   #
# 2.3.1 – Script de vérification de l'existance des drapeaux                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys

sys.path.append(os.getcwd())

from constantes import hierarchie_par_pays, direction_donnees_drapeaux

# 1 -- Données -----------------------------------------------------------------


# Liste des pays
liste_pays = list(hierarchie_par_pays.keys())

# Liste des drapeaux disponibles
liste_drapeaux = os.listdir(direction_donnees_drapeaux)


# 2 -- Tests -------------------------------------------------------------------


for pays in liste_pays:

    if f"{pays}.png" not in liste_drapeaux:
        print(pays)
