################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_2_application/                                             #
# 2.2.1 – Fichier de création des YAMLs des granularités par pays              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys

sys.path.append(os.getcwd())

import constantes
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_fichier,
    cree_yaml_un_pays,
    exporter_fichier,
    tronquer_dict,
    construire_dictionnaire_imbrique,
)

# 1 -- YAML sans hiérarchie ----------------------------------------------------


for granularite in range(1, 6):

    print("Granularité :", granularite, end=".\n")

    cree_yaml_un_pays(
        # Import des données
        gdf=ouvrir_fichier(
            direction_fichier=constantes.direction_donnees_geographiques,
            nom_fichier=f"carte_monde_niveau_{granularite}.pkl",
            defaut=None,
            afficher_erreur="Base non trouvée.",
        ),
        nom_pays=None,
        granularite=granularite,
        direction_fichier=constantes.direction_donnees_autres,
        nom_fichier=f"liste_pays_granularite_{granularite}.yaml",
    )


# 2 -- YAMLs avec hiérarchie -----------------------------------------------


print("Dictionnaire hiérarchique.")
dictception = construire_dictionnaire_imbrique(
    df=ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_geographiques,
        nom_fichier=f"carte_monde_niveau_{5}.pkl",
        defaut=None,
        afficher_erreur="Base non trouvée.",
    ),
    levels=["name_0", "name_1", "name_2", "name_3", "name_4"],
    value_col="name_5",
)
del dictception["Caspian Sea"]

# Hiérarchie complète
exporter_fichier(
    objet=dictception,
    direction_fichier=constantes.direction_donnees_autres,
    nom_fichier="hierarchie_complete_granularite_pays.pkl",
    sort_keys=True,
)

# Hiérarchie néessaire à l'application
exporter_fichier(
    objet=tronquer_dict(d=dictception, n=3),
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="hierarchie_granularite_pays.pkl",
    sort_keys=True,
)


# 3 -- Export de la table sans les coordonnées ---------------------------------


exporter_fichier(
    objet=ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_geographiques,
        nom_fichier=f"carte_monde_niveau_{5}.pkl",
        defaut=None,
        afficher_erreur="Base non trouvée.",
    )[["name_0", "name_1", "name_2", "name_3", "name_4", "name_5"]],
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="hierarchie_complete_granularite_pays_df.pkl",
    sort_keys=True,
)
