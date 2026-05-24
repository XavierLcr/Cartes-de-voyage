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
from _3_Calculs._3_1_creer_carte import cree_gdf_depuis_dicts
from _3_Calculs._3_4_carte_main import (
    lister_cartes_a_publier,
    creer_une_carte,
    creer_multiples_cartes,
)

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

# Données géographiques
liste_gdfs = charger_gdfs(
    direction_base=constantes.direction_donnees_geographiques, max_niveau=2
)


# 2 -- Tests du listage de cartes à publier ------------------------------------


liste_tests = lister_cartes_a_publier(
    regroupements_pays_ref=constantes.liste_pays_groupes,
    continents_ref=constantes.liste_regions_monde,
    traductions_ref=constantes.pays_differentes_langues,
    langue="français",
    pays=False,
    monde=True,
    continents=["Europe", "Asia"],
    voyages=voyages_test,
    sortir_cartes_granu_inf=True,
    granularite_objectif=2,
)


# 3 -- Tests de la fonction de sortie d'un graphique ---------------------------


df_test = cree_gdf_depuis_dicts(
    liste_dfs=liste_gdfs,
    liste_dicts=[
        voyages_vers_destinations_une_granu(dict_voyages=voyages_test, clef=granu)
        for granu in ["region", "dep"]
    ],
    granularite_visite=1,
    granularite_reste=1,
)


creer_une_carte(
    gdf=df_test,
    gdf_0=liste_gdfs[0],
    gdf_1=liste_gdfs[1],
    gdf_eau=None,
    carte_liste_pays=["France", "Germany"],
    direction_dossier=r"C:\Users\xaruo\Downloads",
    couleur_pays_contours="#C22929",
)


# 4 -- Tests de la fonction de sortie de multiples graphiques ------------------


creer_multiples_cartes(
    liste_dfs=liste_gdfs,
    liste_dicts=[
        voyages_vers_destinations_une_granu(dict_voyages=voyages_test, clef=granu)
        for granu in ["region", "dep"]
    ],
    gdf_eau=None,
    granularite_visite=2,
    granularite_reste=1,
    dict_cartes=liste_tests,
    direction_dossier=os.path.join(r"C:\Users\xaruo\Downloads", "Test"),
)
