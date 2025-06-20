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

# Import des lieux avec de l'eau
with open(
    os.path.join(direction_donnees_pickle, "carte_monde_lacs.pkl"),
    "rb",
) as f:
    gdf_lacs = pickle.load(f)

# Import dela table des superficies
with open(
    os.path.join(direction_donnees_pickle, "table_superficie.pkl"),
    "rb",
) as f:
    table_superficie = pickle.load(f)

# Import de la traduction des pays
with open(
    os.path.join(direction_donnees_application, "traductions_nom_pays.yaml"),
    "r",
    encoding="utf-8",
) as file:
    pays_differentes_langues = yaml.safe_load(file)

# Import des pays regroupés
with open(
    os.path.join(direction_donnees_application, "liste_pays_groupes.yaml"),
    "r",
    encoding="utf-8",
) as file:
    liste_pays_groupes = yaml.safe_load(file)

# Import des phrases de l'interfaces
with open(
    os.path.join(direction_donnees_application, "phrases_interface.yaml"),
    "r",
    encoding="utf-8",
) as file:
    phrases_interface = yaml.safe_load(file)

# Import de la traduction de l'interface
with open(
    os.path.join(direction_donnees_application, "traductions_phrase_outil.yaml"),
    "r",
    encoding="utf-8",
) as file:
    outil_differentes_langues = yaml.safe_load(file)

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
with open(
    os.path.join(direction_donnees_application, "traductions_noms_langues.yaml"),
    "r",
    encoding="utf-8",
) as file:
    dict_langues_dispo = yaml.safe_load(file)

# Import des paramètres traduits
with open(
    os.path.join(direction_donnees_application, "traductions_parametres.yaml"),
    "r",
    encoding="utf-8",
) as file:
    parametres_traduits = yaml.safe_load(file)

emojis_pays = {
    "Antarctica": "🐧​",
    "Australia": "🦘​",
    "Canada": "​🍁​",
    "Chile": "🗿​",
    "China": "​🥮​",
    "Finland": "​​🎅​",
    "France": "🥐",
    "Germany": "🥨​​",
    "Greece": "🏛️​",
    "India": "🛕",
    "Ireland": "☘️​​",
    "Italy": "🍝​",
    "Japan": "​⛩️​",
    "Monaco": "​​🎲​",
    "Romania": "​🧛​",
    "Saudi Arabia": "🕋​",
    "United Kingdom": "​​💂🏻‍♂️​",
    "United States": "🗽",
}
