################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.1 – Fonctions génériques utiles                                            #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, pickle, yaml, time, numba, subprocess, platform
import pandas as pd
import geopandas as gpd
import numpy as np
from datetime import date
from shapely.wkb import loads

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


def reordonner_dict(dictionnaire: dict, clefs: list | None):

    if clefs is None:
        clefs = sorted(list(dictionnaire.keys()))
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


## 1.6 -- Créer un dictionnaire imbriqué ---------------------------------------


def construire_dictionnaire_imbrique(df, niveaux, colonne_valeur):
    resultat = {}

    for _, ligne in df.iterrows():

        niveau_courant = resultat

        # Parcours des niveaux intermédiaires
        for niveau in niveaux[:-1]:

            cle = ligne[niveau]

            if cle not in niveau_courant:
                niveau_courant[cle] = {}

            niveau_courant = niveau_courant[cle]

        # Dernier niveau : stockage des valeurs dans une liste
        derniere_cle = ligne[niveaux[-1]]

        if derniere_cle not in niveau_courant:
            niveau_courant[derniere_cle] = []

        niveau_courant[derniere_cle].append(ligne[colonne_valeur])

    return resultat


## 1.7 -- Simplifier un voyage -------------------------------------------------


### Fonction pour une granularité donnée ---------------------------------------


def voyages_vers_destinations_une_granu(dict_voyages: dict, clef: str):

    resultat = {}

    for voyage in list(dict_voyages.keys()):
        visites_clef = dict_voyages.get(voyage, {}).get(clef, {})

        if visites_clef:

            for pays in list(visites_clef.keys()):
                if visites_clef.get(pays):
                    resultat[pays] = list(
                        set(resultat.get(pays, []) + visites_clef.get(pays))
                    )

    return resultat


### Fonction générale ----------------------------------------------------------


def voyages_vers_destinations(dict_voyages: dict):

    return {
        granu: voyages_vers_destinations_une_granu(
            dict_voyages=dict_voyages, clef=granu
        )
        for granu in ["region", "dep"]
    }


# 2 -- Fonctions spacio-temporelles --------------------------------------------


## 2.1 -- Fonction de formatage de l'heure et de la date actuelles -------------


def formater_temps_actuel(n: int = 0) -> str:
    formats = {
        0: "%d-%m-%Y %Hh%M",
        1: "%Y-%m-%d %H:%M",
        2: "%Y-%m-%d",
    }
    return time.strftime(formats.get(n, formats[0]), time.localtime())


## 2.2 -- Fonction faisant n pauses par minute ---------------------------------


def sleep_n_fois(n: float, time_ref: float | None):

    # Si pas de temps de référence, on prend l'instant actuel
    if time_ref is None:
        time_ref = time.time()

    # Attente
    time.sleep(
        max(
            0,
            60 / n - (time.time() - time_ref),
        )
    )


## 2.3 -- Fonction de mise en forme du titre selon les événements --------------


def periode_particuliere(periodes: dict) -> dict:

    aujourdhui = date.today()
    mois_actuel = aujourdhui.month
    jour_actuel = aujourdhui.day

    # Parcourir les périodes pour trouver la bonne
    for nom, details in periodes.items():
        if "dates" in details:
            for plage in details["dates"]:
                debut_jour = plage.get("debut", {}).get("jour", 1)
                debut_mois = plage.get("debut", {}).get("mois", 1)
                fin_jour = plage.get("fin", {}).get("jour", 31)
                fin_mois = plage.get("fin", {}).get("mois", 12)

                if (
                    # Vérification que la date est supérieure à celle de début
                    mois_actuel > debut_mois
                    or (mois_actuel == debut_mois and jour_actuel >= debut_jour)
                ) and (
                    # Vérification que la date est inférieure à celle de fin
                    mois_actuel < fin_mois
                    or (mois_actuel == fin_mois and jour_actuel <= fin_jour)
                ):

                    return details["config"]

    # Retourner la configuration par défaut
    return periodes.get("Défaut", {}).get(
        "config",
        {
            "titre_police": "Vivaldi",
            "titre_police_coeff": 1,
            "emoji": "",
        },
    )


## 2.4 -- Fonction calculant la distance de Haversine --------------------------


@numba.njit
def distance_haversine(lat1, lon1, lat2, lon2):

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


## 2.5 -- Phase de la Lune -----------------------------------------------------


def phase_lunaire(date_jour=None):
    """
    Retourne la phase de la lune entre 0 et 1 :

    0.0  = nouvelle lune 🌑
    0.5  = pleine lune 🌕
    1.0  = nouvelle lune (cycle suivant)
    """

    if date_jour is None:
        date_jour = date.today()

    # Date de référence (nouvelle lune proche connue)
    date_reference = date(2000, 1, 6)

    # Durée d'un cycle lunaire
    jours_synodiques = 29.53058867

    nombre_de_jours = (date_jour - date_reference).days

    phase = (nombre_de_jours % jours_synodiques) / jours_synodiques

    return phase


# 3 -- Fonctions d'import et d'export ------------------------------------------


## 3.1 -- Fonction d'ouverture d'un fichier de type .yaml ou .pkl --------------


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

        elif extention == ".parquet":
            df = pd.read_parquet(nom_fichier)

            # Conversion en GeoDataFrame si colonne geometry présente
            if "geometry" in df.columns:
                df["geometry"] = df["geometry"].apply(
                    lambda x: loads(x) if isinstance(x, bytes) and x else None
                )
                return gpd.GeoDataFrame(df, geometry="geometry")
            else:
                return df

    except Exception as e:

        if afficher_erreur is not None:
            print(afficher_erreur)
            print(f"Détail de l'erreur : {e}")

        return defaut


## 3.2 -- Fonction de chargement des tables géographiques principales ----------


def charger_gdfs(direction_base, max_niveau):
    """
    Charge les fichiers pickle et remplit la liste_gdfs.
    """

    return [
        ouvrir_fichier(
            direction_fichier=direction_base,
            nom_fichier=f"carte_monde_niveau_{i}.pkl",
            defaut=None,
            afficher_erreur=f"Base de granularité {i} introuvable.",
        )
        for i in range(max_niveau + 1)
    ]


## 3.3 -- Fonction d'export de .yaml et de .pkl --------------------------------


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

    elif extention in [".parquet"]:
        objet.to_parquet(nom_fichier, index=False)

    elif extention == ".csv":
        objet.to_csv(nom_fichier, index=False)

    elif extention in (".xlsx", ".xls"):
        objet.to_excel(nom_fichier, index=False)

    else:
        raise ValueError(f"Extension non supportée : {extention}")


## 3.4 -- Fonction créant les .yaml Pays × Région/Département/... --------------


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


## 3.5 -- Ouverture d'un dossier -----------------------------------------------


def ouvrir_dossier(chemin: str):
    if platform.system() == "Windows":
        os.startfile(chemin)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", chemin])
    else:  # Linux et autres
        subprocess.run(["xdg-open", chemin])
