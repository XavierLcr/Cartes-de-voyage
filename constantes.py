################################################################################
# Projet de cartes de voyage                                                   #
# Fichier contenant les constantes et les données secondaires                  #
################################################################################

import os, sys
from _0_Utilitaires._0_1_Fonctions_utiles import ouvrir_fichier


# 1 -- Gestion des directions --------------------------------------------------


if getattr(sys, "frozen", False):
    # cx_Freeze place tout à côté de l'exécutable
    direction_base = os.path.dirname(sys.executable)
    direction_donnees_geographiques = os.path.join(
        direction_base, "1 – Données géographiques"
    )
    direction_donnees_application = os.path.join(
        direction_base, "2 – Données application"
    )
    direction_donnees_traductions = os.path.join(direction_base, "3 – Traductions")
    compilation = True
else:
    direction_base = os.path.dirname(os.path.abspath(__file__))
    direction_donnees = os.path.join(direction_base, "_1_Données")
    direction_donnees_brutes = os.path.join(direction_donnees, "_1_1_Données_brutes")
    direction_donnees_geographiques = os.path.join(
        direction_donnees, "_1_2_Données_géographiques"
    )
    direction_donnees_application = os.path.join(
        direction_donnees, "_1_3_Données_application"
    )
    print(direction_donnees_application)
    direction_donnees_traductions = os.path.join(direction_donnees, "_1_4_Traductions")
    direction_donnees_autres = os.path.join(direction_donnees, "_1_X_Autres")
    compilation = False


# 2 -- Version du logiciel -----------------------------------------------------


version_logiciel = "2.2"


# 3 -- Import des données ------------------------------------------------------


## 3.1 -- Import des paramètres ------------------------------------------------


# Paramètres par défaut si nécessaires
parametres_application_defaut = {
    # Paramètres d'application
    "application_position_largeur": 250,
    "application_position_hauteur": 40,
    "application_largeur": 750,
    "application_hauteur": 250,
    # Paramètres d'interface
    "interface_foncee": False,
    # Paramètres des cartes
    "qualite_min": 200,
    "qualite_max": 4000,
    # Onglet 4
    "onglet_4_mise_en_page": 0,
    ## Classement
    "top_n_pays": None,
    "pct_ndigits": None,
    ## Hémicycle
    "min_width": 500,
    "min_height": 300,
    "n_rangees": 9,
    "points_base": 15,
    "points_increment": 4,
    "lighter_value": 190,
    "couleurs_continents": {
        "Africa": "#F0E68C",  # Désert
        "Antarctica": "#A7C9E6",  # Glace
        "Asia": "#EE211E",  # Rouge
        "Europe": "#9A0EE6",  # Violet
        "North America": "#1310CE",  # Bleu océan
        "Oceania": "#1EC3CF",  # Bleu lagon
        "South America": "#23E958",  # Vert forêt
    },
}

# Import
parametres_application = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="parametres_application.yaml",
    defaut=parametres_application_defaut,
    afficher_erreur="Paramètres introuvables.",
)

# Complétion si nécessaire des paramètres
parametres_application.update(
    {
        k: v
        for k, v in parametres_application_defaut.items()
        if k not in parametres_application
    }
)


## 3.2 -- Import des données internes ------------------------------------------


### Import de la traduction des noms des pays ----------------------------------


pays_differentes_langues = ouvrir_fichier(
    direction_fichier=direction_donnees_traductions,
    nom_fichier="noms_pays_traduction.yaml",
    defaut={},
    afficher_erreur="Traductions des noms de pays introuvables.",
)


### Import des regroupements de pays -------------------------------------------


liste_pays_groupes = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="cartes_pays_regroupements.yaml",
    defaut={},
    afficher_erreur="Regroupements des pays introuvables.",
)


### Import des régions mondiales considérées -----------------------------------


liste_regions_monde = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="continents.yaml",
    defaut={},
    afficher_erreur="Continents introuvables.",
)


### Import des emojis associés aux pays ----------------------------------------


emojis_pays = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="emojis_pays.yaml",
    defaut={},
    afficher_erreur="Emojis des pays introuvables.",
)


### Import des caractéristiques des pays ---------------------------------------


df_caracteristiques_pays = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="caracteristiques_des_regions.pkl",
    defaut=None,
    afficher_erreur="Données caractéristiques des pays introuvables.",
)


## 3.3 -- Import des paramètres accessibles à l'utilisateur –––––––––––––-------


### Import des phrases de l'interface ------------------------------------------


phrases_interface = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="phrases_interface.yaml",
    defaut={},
    afficher_erreur="Phrases de l'interface introuvables.",
)


### Import de la traduction de l'interface -------------------------------------


outil_differentes_langues = ouvrir_fichier(
    direction_fichier=direction_donnees_traductions,
    nom_fichier="phrases_interface_traduction.yaml",
    defaut={},
    afficher_erreur="Traduction des phrases de l'interface introuvables.",
)


### Import des régions ---------------------------------------------------------


regions_par_pays = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="liste_pays_granularite_1.yaml",
    defaut={},
    afficher_erreur="Régions des pays introuvables.",
)


### Import des départements ----------------------------------------------------


departements_par_pays = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="liste_pays_granularite_2.yaml",
    defaut={},
    afficher_erreur="Départements des pays introuvables.",
)


### Import de la liste de thèmes -----------------------------------------------


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
    afficher_erreur="Ambiances introuvables.",
)


### Import de la liste des teintes ---------------------------------------------


liste_couleurs = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="cartes_teintes.yaml",
    defaut={"Multicolore": [i / 360 for i in range(0, 360)]},
    afficher_erreur="Teintes introuvables.",
)


### Import de la liste des arrières-plans --------------------------------------


dictionnaire_arriere_plans = ouvrir_fichier(
    direction_fichier=direction_donnees_application,
    nom_fichier="cartes_arriere_plans.yaml",
    defaut={},
)


### Import des langues disponibles ---------------------------------------------


dict_langues_dispo = ouvrir_fichier(
    direction_fichier=direction_donnees_traductions,
    nom_fichier="noms_langues_traduction.yaml",
    defaut={},
    afficher_erreur="Langues introuvables.",
)


### Import des paramètres traduits ---------------------------------------------


parametres_traduits = ouvrir_fichier(
    direction_fichier=direction_donnees_traductions,
    nom_fichier="parametres_cartes_traduction.yaml",
    defaut={},
    afficher_erreur="Traductions des paramètres introuvables.",
)
