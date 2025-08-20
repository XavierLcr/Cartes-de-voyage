################################################################################
# Projet de cartes de voyage                                                   #
# Fichier contenant les constantes et les données secondaires                  #
################################################################################

import os, sys, yaml, pickle
from application.fonctions_utiles_2_0 import ouvrir_fichier


if getattr(sys, "frozen", False):
    # cx_Freeze place tout à côté de l'exécutable
    direction_base = os.path.dirname(sys.executable)
    direction_donnees_pickle = os.path.join(direction_base, "Données pickle")
    direction_donnees_application = os.path.join(direction_base, "Données application")
    compilation = True
else:
    direction_base = os.path.dirname(os.path.abspath(__file__))
    direction_generale = os.path.dirname(direction_base)
    direction_donnees = os.path.join(direction_base, "donnees")
    direction_donnees_pickle = os.path.join(direction_donnees, "donnees_pickle")
    direction_donnees_application = os.path.join(
        direction_donnees, "donnees_application"
    )
    direction_donnees_autres = os.path.join(direction_donnees, "donnees_autres")
    compilation = False

# Version de l'application
version_logiciel = "2.2"


# ––––––– Import des paramètres –––––––

# Paramètres par défaut
parametres_application_defaut = {
    # Paramètres d'application
    "application_position_largeur": 250,
    "application_position_hauteur": 40,
    "application_largeur": 750,
    "application_hauteur": 250,
    # Paramètres d'interface
    "interface_foncee": False,
    # Paramètres des statistiques
    "min_width": 500,
    "min_height": 300,
    "n_rangees": 9,
    "points_base": 15,
    "points_increment": 4,
    "lighter_value": 190,
    "top_n_pays": None,
    "couleurs_continents": {
        "Africa": "#F0E68C",  # Désert
        "Antarctica": "#A7C9E6",  # Glace
        "Asia": "#EE211E",  # Rouge
        "Europe": "#9A0EE6",  # Violet
        "North America": "#1310CE",  # Bleu océan
        "Oceania": "#1EC3CF",  # Bleu lagon
        "South America": "#23E958",  # Vert forêt
    },
    # Paramètres des cartes
    "qualite_min": 200,
    "qualite_max": 4000,
}

# Import
parametres_application = ouvrir_fichier(
    direction_fichier=direction_base,
    nom_fichier="parametres_application.yaml",
    defaut=parametres_application_defaut,
)

# Complétion si nécessaire des paramètres
parametres_application.update(
    {
        k: v
        for k, v in parametres_application_defaut.items()
        if k not in parametres_application
    }
)


# ––––––– Import des données géographiques –––––––


# Import des lieux avec de l'eau
gdf_lacs = ouvrir_fichier(
    direction_fichier=direction_donnees_pickle,
    nom_fichier="carte_monde_lacs.pkl",
    defaut=None,
)

# Import dela table des superficies
table_superficie = ouvrir_fichier(
    direction_fichier=direction_donnees_pickle,
    nom_fichier="table_superficie.pkl",
    defaut=None,
)


# ––––––– Import des données YAML internes –––––––


# Import de la traduction des nom des pays
pays_differentes_langues = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="noms_pays_traduction.yaml",
    defaut={},
)

# Import des regroupements de pays
liste_pays_groupes = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="cartes_pays_regroupements.yaml",
    defaut={},
)

# Import des régions mondiales considérées
liste_regions_monde = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="continents.yaml",
    defaut={},
)

# Import des emojis associés aux pays
emojis_pays = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="emojis_pays.yaml",
    defaut={},
)


# ––––––– Import des données YAML liées aux paramètres –––––––


# Import des phrases de l'interface
phrases_interface = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="phrases_interface.yaml",
    defaut={},
)

# Import de la traduction de l'interface
outil_differentes_langues = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="phrases_interface_traduction.yaml",
    defaut={},
)

# Import des régions
regions_par_pays = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="regions_par_pays.yaml",
    defaut={},
)

# Import des départements
departements_par_pays = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="departements_par_pays.yaml",
    defaut={},
)

# Import de la liste de thèmes
liste_ambiances = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="cartes_ambiances.yaml",
    defaut={
        "Pastel": {
            "min_luminosite": 0.8,
            "max_luminosite": 0.95,
            "min_saturation": 0.2,
            "max_saturation": 0.4,
        }
    },
)

# Import de la liste des teintes
liste_couleurs = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="cartes_teintes.yaml",
    defaut={"Multicolore": [i / 360 for i in range(0, 360)]},
)

# Import des langues disponibles
dict_langues_dispo = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="noms_langues_traduction.yaml",
    defaut={},
)

# Import des paramètres traduits
parametres_traduits = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="parametres_cartes_traduction.yaml",
    defaut={},
)
