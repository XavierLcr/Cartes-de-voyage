################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/                                                              #
# 2.2 – Fichier de création des YAMLs des granularités par pays                #
################################################################################


import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constantes
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_fichier,
    cree_yaml_un_pays,
    exporter_fichier,
    tronquer_dict,
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


## 2.1 -- Fonctions utiles -------------------------------------------------


### Transformer un df en dictionniares de dictionnaires --------------------


def build_nested_dict(df, levels, value_col):
    result = {}
    for _, row in df.iterrows():
        current_level = result
        for level in levels[:-1]:
            key = row[level]
            if key not in current_level:
                current_level[key] = {}
            current_level = current_level[key]
        # Dernier niveau : liste de valeurs
        last_key = row[levels[-1]]
        if last_key not in current_level:
            current_level[last_key] = []
        current_level[last_key].append(row[value_col])
    return result


## 2.2 -- Application ----------------------------------------------------------


print("Dictionnaire hiérarchique.")
dictception = build_nested_dict(
    df=ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_geographiques,
        nom_fichier=f"carte_monde_niveau_{5}.pkl",
        defaut=None,
        afficher_erreur="Base non trouvée.",
    ),
    levels=["name_0", "name_1", "name_2", "name_3", "name_4"],
    value_col="name_5",
)

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
