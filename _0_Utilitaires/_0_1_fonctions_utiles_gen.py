################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.1 – Fonctions génériques utiles                                            #
################################################################################


import os, pickle, yaml, time, numba
import pandas as pd
import numpy as np
from datetime import date
from PyQt6.QtWidgets import QHBoxLayout, QFrame, QWidget


# 1 -- Fonctions sur les dictionnaires -----------------------------------------


## 1.1 -- Retourne la première clef dont la valeur en vaut une de référence ----


def obtenir_clef_par_valeur(dictionnaire, valeur):
    """Retourne la clé associée à une valeur donnée dans un dictionnaire."""
    for clef, val in dictionnaire.items():
        if val == valeur:
            return clef
    return None


## 1.2 -- Tronquer un dictionnaire imbriqué ------------------------------------


def tronquer_dict(d, n):
    if n == 1:
        return list(d.keys())
    else:
        return {k: tronquer_dict(v, n - 1) for k, v in d.items()}


## 1.3 -- Aplanir un dictionnaire imbriqué -------------------------------------


def aplanir_dictionnaire(d):
    """Aplatis un dict de dict de dicts... avec listes finales"""
    resultat = {}

    def explorer(clef_top, valeur):
        if isinstance(valeur, dict):
            for sous_valeur in valeur.values():
                explorer(clef_top, sous_valeur)
        elif isinstance(valeur, list):
            resultat.setdefault(clef_top, []).extend(valeur)
        else:
            raise ValueError(f"Valeur inattendue : {valeur}")

    for clef, valeur in d.items():
        explorer(clef, valeur)

    return resultat


## 1.4 -- Fonction réordonnant un dictionnaire ---------------------------------


def reordonner_dict(dictionnaire: dict, clefs: list):
    return {k: dictionnaire[k] for k in clefs if k in dictionnaire}


## 1.5 -- Filtrer un dictionnaire en deux --------------------------------------


def separer_combinaisons(dico1, dico2):
    """Filtrer un dictionnaire en deux : les entrées présentes dans un second dictionnaire, et celles qui n’y sont pas."""

    result = {True: {}, False: {}}

    for pays in dico1:
        if pays not in result[True]:
            result[True][pays] = []
        if pays not in result[False]:
            result[False][pays] = []

        if dico1[pays] is not None:
            for region in dico1[pays]:
                if pays in dico2 and region in dico2[pays]:
                    result[True][pays].append(region)
                else:
                    result[False][pays].append(region)

    # Supprimer les pays sans régions
    result[True] = {pays: regions for pays, regions in result[True].items() if regions}
    result[False] = {
        pays: regions
        for pays, regions in result[False].items()
        if regions or (dico1[pays] is None or not dico1[pays])
    }

    return result


# 2 -- Fonctions d'import et d'export ------------------------------------------


## 2.1 -- Vide l'entièreté d'un layout PyQt6 -----------------------------------


def vider_layout(layout):
    """Supprime tous les widgets d'un QLayout."""
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


## 2.2 -- Ouvre un fichier de type .yaml ou .pkl -------------------------------


# Fonction d'ouverture dedonnées
def ouvrir_fichier(
    direction_fichier, nom_fichier, defaut, afficher_erreur: str | None = None
):
    """Ouvre un fichier de type YAML ou pickle."""

    nom_fichier = os.path.join(direction_fichier, nom_fichier)
    nom, extention = os.path.splitext(nom_fichier)

    try:

        if extention == ".pkl":

            with open(
                nom_fichier,
                "rb",
            ) as file:
                return pickle.load(file)

        elif extention == ".yaml":

            with open(
                nom_fichier,
                "r",
                encoding="utf-8",
            ) as file:
                return yaml.safe_load(file)
    except:

        if afficher_erreur is not None:
            print(afficher_erreur)

        return defaut


## 2.3 -- Fonction de chargement des .pkl principaux ---------------------------


def charger_gdfs(liste_gdfs, direction_base, max_niveau=3):
    """
    Charge les fichiers pickle et remplit la liste_gdfs.
    """
    for i in range(max_niveau):
        liste_gdfs[i] = ouvrir_fichier(
            direction_fichier=direction_base,
            nom_fichier=f"carte_monde_niveau_{i}.pkl",
            defaut=None,
            afficher_erreur=f"Base de granularité {i} introuvable.",
        )  # mise à jour de la liste partagée


## 2.4 -- Fonction d'export de .yaml et de .pkl --------------------------------


def exporter_fichier(objet, direction_fichier, nom_fichier, sort_keys: bool = True):
    """Exporte un fichier de type YAML ou pickle."""

    nom_fichier = os.path.join(direction_fichier, nom_fichier)
    nom, extention = os.path.splitext(nom_fichier)

    # Création de la direction de sauvegarde du résultat si nécessaire
    if not os.path.exists(direction_fichier):
        os.makedirs(direction_fichier)

    if extention == ".yaml":

        with open(
            nom_fichier,
            "w",
            encoding="utf-8",
        ) as file:
            yaml.dump(
                objet,
                file,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=sort_keys,
            )

    elif extention == ".pkl":
        with open(
            nom_fichier,
            "wb",
        ) as f:
            pickle.dump(objet, f)

    else:
        print("Fichier non exportable.")


## 2.5 -- Fonction de formatage de l'heure et de la date actuelles -------------


def formater_temps_actuel():
    return time.strftime("%d-%m-%Y %Hh%M", time.localtime())


## 2.6 -- Fonction créant les .yaml Pays × Région/Département/... --------------


def cree_yaml_un_pays(
    gdf,
    direction_fichier,
    nom_fichier,
    nom_pays: None | list = None,
    granularite: int = 1,
):
    """Crée le yaml pour un pays à un niveau de granularité donné

    Args:
        gdf: la base geopandas.
        nom_pays (str): nom du pays dans la dataframe geopandas.
        granularite (int): 1 (faible) à 5 (forte). Sera réduite si inexistante.
        nom (str): nom du document.
    """

    if nom_pays is not None:
        gdf = gdf[gdf["name_0"].isin(nom_pays)]

    # Créer un DataFrame avec les résultats
    liste_combinaisons = (
        (
            pd.DataFrame(
                list(set(zip(gdf["name_0"], gdf[f"name_{granularite}"]))),
                columns=["nom1", "nom2"],
            )
            # Tri par nom2
            .sort_values(by="nom2", inplace=False)
        )
        .groupby("nom1")["nom2"]
        .apply(list)
        .to_dict()
    )

    if nom_fichier is None:
        return liste_combinaisons

    # Exporter vers YAML
    exporter_fichier(
        objet=liste_combinaisons,
        direction_fichier=direction_fichier,
        nom_fichier=nom_fichier,
        sort_keys=True,
    )


## 2.7 -- Fonction calculant la distance entre deux points sur terre -----------


@numba.njit
def distance_haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    return (
        2
        * 6371
        * np.arcsin(
            np.sqrt(
                np.sin((lat2 - lat1) / 2) ** 2
                + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
            )
        )
    )


## 2.8 -- Sommes-nous dans la période de Halloween ? ---------------------------


def periode_particuliere() -> dict:

    mois = date.today().month
    jour = date.today().day

    # Halloween
    if mois == 10 and jour >= 20:
        return {"titre_police": "Chiller", "titre_police_coeff": 1.2, "emoji": " 🎃​"}

    # Noël
    elif mois == 12 and jour >= 15 and jour <= 28:
        return {
            "titre_police": "Edwardian Script ITC",
            "titre_police_coeff": 1.8,
            "emoji": " 🎄​​",
        }

    # Nouvel an
    elif (mois == 12 and jour >= 29) or (mois == 1 and jour <= 2):
        return {
            "titre_police": "Monotype Corsiva",
            "titre_police_coeff": 1.6,
            "emoji": " 🎆​​​",
        }

    # Printemps
    elif mois == 3 and jour in [19, 20, 21]:
        return {
            "titre_police": "Segoe Print",
            "titre_police_coeff": 1.4,
            "emoji": " 🌷​​​",
        }

    # Autômne
    elif mois == 9 and jour in [21, 22, 23]:
        return {
            "titre_police": "Constantia",
            "titre_police_coeff": 1,
            "emoji": " 🍂​​​",
        }

    # Saint-Valentin
    elif mois == 2 and jour in [12, 13, 14]:
        return {
            "titre_police": "French Script MT",
            "titre_police_coeff": 1,
            "emoji": " 💝​​​",
        }

    # Défaut
    else:
        return {
            "titre_police": "Vivaldi",
            "titre_police_coeff": 1,
            "emoji": "",
        }
