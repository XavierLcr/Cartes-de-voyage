################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.7 – Fonctions utiles afin de manupuler des voyages                         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import re
from datetime import datetime, date
from typing import Literal, List

from _0_Utilitaires._0_6_fonctions_utiles_traductions import traduire_pays
from constantes import hierarchie_par_pays

# 1 -- Création d'un voyage ----------------------------------------------------


def creer_voyage(
    nom: str | None, date_deb, date_fin, regions: dict, departements: dict, langue: str
):

    # Création du voyage
    resultat = {
        "nom": nom,
        "date_debut": date_deb,
        "date_fin": date_fin,
        "region": regions,
        "dep": departements,
    }

    # Nom automatique s'il est inexistant
    if not resultat.get("nom"):
        nom_temp = list((resultat.get("region", {})).keys()) + list(
            (resultat.get("dep", {})).keys()
        )

        resultat["nom"] = ", ".join(
            [traduire_pays(langue=langue, pays=pays) for pays in list(set(nom_temp))]
        )

    return resultat


# 2 -- Fonction de détection du type d'un YAML chargé --------------------------


def detecter_type_yaml(dictionnaire: dict):

    # Cas 1 : le dictionnaire est vide
    if not dict:
        return False

    # Cas 2 : le dictionnaire est au bon format
    if all(cle.startswith("voyage_") for cle in dictionnaire.keys()):
        return False

    # Cas 3 : le dictionnaire correspond à un des deux anciens dictionnaires
    for pays, liste_div in dictionnaire.items():
        for div in liste_div:
            if div not in list(hierarchie_par_pays.get(pays).keys()):
                return "dep"

    return "region"


# 3 -- Créer l'identifiant d'un voyage -----------------------------------------


## 3.1 -- Fonction de renvoi de l'identifiant formaté du voyage ----------------


def identifiant_voyage(n: int, longueur: int):

    return f"voyage_{n:0{longueur}d}"


## 3.2 -- Sélection de l'identifiant automatique et formatage ------------------


def voyage_id(voyages: dict, clef: str | None, longueur: int):

    if clef is not None:
        return clef
    else:
        clefs_actu = sorted(list(voyages.keys()))

        if len(clefs_actu) == 0:
            return identifiant_voyage(n=1, longueur=longueur)
        else:

            return identifiant_voyage(
                n=int(re.search(r"\d+$", clefs_actu[-1]).group()) + 1,
                longueur=longueur,
            )


# 4 -- Tri de l'ordre des voyages ----------------------------------------------


def trier_voyages(dictionnaire: dict, tri: Literal["nom", "date", "clef"]) -> List[str]:

    # Copie du dictionnaire
    dict_temp = dictionnaire.copy()

    # Définir l'ordre des critères de tri
    if tri == "nom":
        criteres_tri = ["nom", "date_debut", "date_fin", "clef"]
    elif tri == "date":
        criteres_tri = ["date_debut", "date_fin", "nom", "clef"]
    else:  # tri == "clef"
        criteres_tri = ["clef"]

    # Préparer les données : remplacer None par date.max et ajouter la clé
    voyages_prepares = []
    for id_voyage, infos in dict_temp.items():
        infos = infos.copy()  # Éviter de modifier l'original
        infos["date_debut"] = infos.get("date_debut") or date.max
        infos["date_fin"] = infos.get("date_fin") or date.max
        infos["clef"] = id_voyage
        voyages_prepares.append((id_voyage, infos))

    # Fonction de clé de tri
    def cle_tri(item):
        id_voyage, infos = item
        return tuple(
            (
                datetime.strptime(infos[criteres], "%Y-%m-%d").date()
                if criteres in ["date_debut", "date_fin"]
                and infos[criteres] != date.max
                else infos[criteres]
            )
            for criteres in criteres_tri
        )

    # Renvoi des clefs triées
    return [id_voyage for id_voyage, _ in sorted(voyages_prepares, key=cle_tri)]


# 5 -- Opérations sur les destionations et voyages -----------------------------


def creer_liste_destinations(dict_regions: dict, dict_dep: dict):

    # Stabilisation
    dict_regions = dict_regions.copy()
    dict_dep = dict_dep.copy()

    # Suppression des pays présents dans les départements
    if dict_dep is not None:
        if dict_dep != {} and dict_regions is not None:
            dict_regions = {k: v for k, v in dict_regions.items() if k not in dict_dep}

    # Mise en None si vide
    if dict_dep == {}:
        dict_dep = None
    if dict_regions == {}:
        dict_regions = None

    # Renvoi
    return [dict_regions, dict_dep]
