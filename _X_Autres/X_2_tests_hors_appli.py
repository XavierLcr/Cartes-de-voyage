################################################################################
# Projet de cartes de voyage                                                   #
# _X_Autres/                                                                   #
# X.2 – Script de tests de publication des cartes hors application             #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys

sys.path.append(os.getcwd())

import constantes
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    voyages_vers_destinations_une_granu,
    ouvrir_fichier,
    charger_gdfs,
)
from _0_Utilitaires._0_7_fonctions_voyages import creer_liste_destinations
from _3_Calculs._3_1_creer_carte import (
    agreger_lieux_constants,
    cree_base_toutes_granularites,
)

# 1 -- Paramétrisation et import des données -----------------------------------

# Profil
profil_test = ouvrir_fichier(
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="sauvegarde_utilisateurs.yaml",
    defaut={},
    # ).get("Xavier", {})
).get("24-05-2026 16h49", {})

# Dictionnaire des voyages
voyages_test = profil_test.get("dictionnaire_voyages", {})

# Pays visités
liste_pays_test = list(
    voyages_vers_destinations_une_granu(dict_voyages=voyages_test, clef="region").keys()
) + list(
    voyages_vers_destinations_une_granu(dict_voyages=voyages_test, clef="dep").keys()
)

# Liste des dictionnaires des destinations
liste_destinations = creer_liste_destinations(
    dict_regions=voyages_vers_destinations_une_granu(
        dict_voyages=voyages_test, clef="region"
    ),
    dict_dep=voyages_vers_destinations_une_granu(dict_voyages=voyages_test, clef="dep"),
)

# Données géographiques
liste_gdfs = charger_gdfs(
    direction_base=constantes.direction_donnees_geographiques, max_niveau=2
)


# 2 -- Tests -------------------------------------------------------------------
