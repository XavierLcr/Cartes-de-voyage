################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_2_application/                                             #
# 2.2.1 – Fichier de création des YAMLs des granularités par pays              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys, re
import pandas as pd

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


# 2 -- Arborescence avec hiérarchie --------------------------------------------


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


print("Table complète")
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


# 4 -- Niveau maximal par pays -------------------------------------------------


## 4.1 -- Fonction de calcul ---------------------------------------------------


def obtenir_niveau_max_pays(df: pd.DataFrame):
    """
    Retourne un dictionnaire contenant le niveau géographique
    maximal disponible pour chaque pays.

    Format :
    {
        "France": 4,
        "Belgique": 2,
        "Vatican": 0
    }

    name_0 = pays
    name_1, name_2, ... = niveaux administratifs
    """

    # Détection automatique des colonnes name_X
    colonnes_niveaux = sorted(
        [col for col in df.columns if re.fullmatch(r"name_\d+", col)],
        key=lambda x: int(x.split("_")[1]),
    )

    resultats = {}

    for pays, groupe in df.groupby("name_0"):

        niveau_max = 0

        for i in range(1, len(colonnes_niveaux)):

            colonne_precedente = colonnes_niveaux[i - 1]
            colonne_actuelle = colonnes_niveaux[i]

            # Nettoyage des valeurs
            valeurs_precedentes = (
                groupe[colonne_precedente].fillna("").astype(str).str.strip()
            )

            valeurs_actuelles = (
                groupe[colonne_actuelle].fillna("").astype(str).str.strip()
            )

            # Vérifie si le niveau apporte une information supplémentaire
            niveau_existe = (valeurs_actuelles != valeurs_precedentes).any()

            if niveau_existe:
                niveau_max = int(colonne_actuelle.split("_")[1])

        resultats[pays] = niveau_max

    return resultats


## 4.2 -- Application ----------------------------------------------------------


print("Niveau maximal d'un pays")
exporter_fichier(
    objet=ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_geographiques,
        nom_fichier=f"carte_monde_niveau_{5}.pkl",
        defaut=None,
        afficher_erreur="Base non trouvée.",
    )[["name_0", "name_1", "name_2", "name_3", "name_4", "name_5"]].pipe(
        obtenir_niveau_max_pays
    ),
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="niveau_maximal_par_pays.yaml",
    sort_keys=True,
)
