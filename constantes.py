################################################################################
# Projet de cartes de voyage                                                   #
# Fichier contenant les constantes et les données secondaires                  #
################################################################################

import os
import sys
import yaml
import pickle

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

version_logiciel = "2.2"

# Import des paramètres
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

try:
    with open(
        os.path.join(direction_base, "parametres_application.yaml"),
        "r",
        encoding="utf-8",
    ) as f:
        parametres_application = yaml.safe_load(f)
except:
    parametres_application = {}

parametres_application.update(
    {
        k: v
        for k, v in parametres_application_defaut.items()
        if k not in parametres_application
    }
)


# Import des lieux avec de l'eau
try:
    with open(
        os.path.join(direction_donnees_pickle, "carte_monde_lacs.pkl"),
        "rb",
    ) as f:
        gdf_lacs = pickle.load(f)
except:
    gdf_lacs = None

# Import dela table des superficies
try:
    with open(
        os.path.join(direction_donnees_pickle, "table_superficie.pkl"),
        "rb",
    ) as f:
        table_superficie = pickle.load(f)
except:
    table_superficie = None

# Import de la traduction des pays
try:
    with open(
        os.path.join(direction_donnees_application, "traductions_nom_pays.yaml"),
        "r",
        encoding="utf-8",
    ) as file:
        pays_differentes_langues = yaml.safe_load(file)
except Exception as e:
    print("Une erreur est survenue :", e)
    pays_differentes_langues = {}

# Import des pays regroupés
try:
    with open(
        os.path.join(direction_donnees_application, "liste_pays_groupes.yaml"),
        "r",
        encoding="utf-8",
    ) as file:
        liste_pays_groupes = yaml.safe_load(file)
except:
    liste_pays_groupes = {}

# Import des phrases de l'interfaces
try:
    with open(
        os.path.join(direction_donnees_application, "phrases_interface.yaml"),
        "r",
        encoding="utf-8",
    ) as file:
        phrases_interface = yaml.safe_load(file)
except:
    phrases_interface = {}

# Import de la traduction de l'interface
try:
    with open(
        os.path.join(direction_donnees_application, "traductions_phrase_outil.yaml"),
        "r",
        encoding="utf-8",
    ) as file:
        outil_differentes_langues = yaml.safe_load(file)
except:
    outil_differentes_langues = {}

# Import des régions mondiales considérées
with open(
    os.path.join(direction_donnees_application, "liste_regions_monde.yaml"),
    "r",
    encoding="utf-8",
) as file:
    liste_regions_monde = yaml.safe_load(file)

# Import des régions
with open(
    os.path.join(direction_donnees_application, "liste_pays_regions.yaml"),
    "r",
    encoding="utf-8",
) as file:
    regions_par_pays = yaml.safe_load(file)

# Import des départements
with open(
    os.path.join(direction_donnees_application, "liste_pays_departements.yaml"),
    "r",
    encoding="utf-8",
) as file:
    departements_par_pays = yaml.safe_load(file)

# Import de la liste des teintes
with open(
    os.path.join(direction_donnees_application, "teintes_couleurs.yaml"),
    "r",
    encoding="utf-8",
) as file:
    liste_couleurs = yaml.safe_load(file)

# Import de la liste de thèmes
with open(
    os.path.join(direction_donnees_application, "themes_cartes.yaml"),
    "r",
    encoding="utf-8",
) as file:
    liste_ambiances = yaml.safe_load(file)

# Import des langues disponibles
try:
    with open(
        os.path.join(direction_donnees_application, "traductions_noms_langues.yaml"),
        "r",
        encoding="utf-8",
    ) as file:
        dict_langues_dispo = yaml.safe_load(file)
except:
    dict_langues_dispo = {}

# Import des paramètres traduits
try:
    with open(
        os.path.join(direction_donnees_application, "traductions_parametres.yaml"),
        "r",
        encoding="utf-8",
    ) as file:
        parametres_traduits = yaml.safe_load(file)
except:
    parametres_traduits = {}


# Import des emojis associés aux pays
try:
    with open(
        os.path.join(direction_donnees_application, "emojis_pays.yaml"),
        "r",
        encoding="utf-8",
    ) as file:
        emojis_pays = yaml.safe_load(file)
except:
    emojis_pays = {}
