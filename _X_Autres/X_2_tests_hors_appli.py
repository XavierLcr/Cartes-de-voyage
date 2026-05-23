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
)
from _3_Calculs._3_4_carte_main import lister_cartes_a_publier

# 1 -- Paramétrisation et import des données -----------------------------------

# Profil
profil_test = ouvrir_fichier(
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="sauvegarde_utilisateurs.yaml",
    defaut={},
).get("Xavier", {})

# Dictionnaire des voyages
voyages_test = profil_test.get("dictionnaire_voyages", {})

# Pays visités
liste_pays_test = list(
    voyages_vers_destinations_une_granu(dict_voyages=voyages_test, clef="region").keys()
) + list(
    voyages_vers_destinations_une_granu(dict_voyages=voyages_test, clef="dep").keys()
)


# 2 -- Tests du listage de cartes à publier ------------------------------------


lister_cartes_a_publier(
    regroupements_pays_ref=constantes.liste_pays_groupes,
    continents_ref=constantes.liste_regions_monde,
    traductions_ref=constantes.pays_differentes_langues,
    langue="français",
    pays="True",
    monde=True,
    continents=["Europe", "Asia"],
    pays_visites=liste_pays_test,
)
