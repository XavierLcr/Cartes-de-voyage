################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.7 – Fonctions utiles afin de manupuler des voyages                         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import re, copy
from collections import Counter
import pandas as pd
from datetime import datetime, date
from typing import Literal, List

from _0_Utilitaires._0_5_isid import isid
from _0_Utilitaires._0_6_fonctions_utiles_traductions import traduire_pays
from constantes import hierarchie_par_pays, pays_differentes_langues

# 1 -- Création d'un voyage ----------------------------------------------------


def creer_voyage(
    nom: str | None,
    compagnons: str | list | None,
    date_deb,
    date_fin,
    regions: dict,
    departements: dict,
    langue: str,
    referentiel: dict = pays_differentes_langues,
):

    # Gestion des compagnons
    if compagnons is not None:
        if isinstance(compagnons, str) == True:
            compagnons = [compagnons]

    # Création du voyage
    resultat = {
        "nom": nom,
        "compagnons": compagnons,
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
            [
                traduire_pays(langue=langue, pays=pays, referentiel=referentiel)
                for pays in list(set(nom_temp))
            ]
        )

    return resultat


# 2 -- Fonction de détection du type d'un YAML chargé --------------------------


def detecter_type_yaml(dictionnaire: dict):

    # Cas 1 : le dictionnaire est vide
    if not dictionnaire:
        return False

    # Cas 2 : le dictionnaire est au bon format
    if all(cle.startswith("voyage_") for cle in dictionnaire.keys()):
        return True

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


# 6 -- Transformer les destinations en dictionnaire de voyages -----------------


def destinations_vers_voyages(
    regions: dict, departements: dict, langue: str, longueur_id_voyage
):

    # Initialisation du résultat
    voyages_temp = {}

    # Régions
    if regions:
        for pays in list(regions.keys()):
            voyages_temp[
                voyage_id(
                    voyages=voyages_temp,
                    clef=None,
                    longueur=longueur_id_voyage,
                )
            ] = creer_voyage(
                nom=None,
                date_deb=None,
                date_fin=None,
                compagnons=None,
                regions={pays: regions.get(pays)},
                departements={},
                langue=langue,
            )

    # Départements
    if departements:
        for pays in list(departements.keys()):
            voyages_temp[
                voyage_id(
                    voyages=voyages_temp,
                    clef=None,
                    longueur=longueur_id_voyage,
                )
            ] = creer_voyage(
                nom=None,
                date_deb=None,
                date_fin=None,
                compagnons=None,
                regions={},
                departements={pays: departements.get(pays)},
                langue=langue,
            )

    # Renvoi
    return voyages_temp


# 7 -- Comptage des voyages ----------------------------------------------------


## 7.1 -- Même granularité -----------------------------------------------------


def compter_occurences_destinations_une_granu(dict_voyages: dict, granu: int):
    compteur_temp = Counter()

    for voyage in dict_voyages.values():

        # Comptage par pays
        if granu == 0:
            for niveau in ("region", "dep"):
                if niveau not in voyage:
                    continue

                for pays in voyage[niveau].keys():
                    compteur_temp[pays] += 1

        # Comptage par région
        elif granu == 1:
            if "region" not in voyage:
                continue

            for pays, regions in voyage["region"].items():
                for region in regions:
                    compteur_temp[(pays, region)] += 1

        # Comptage par département
        elif granu == 2:
            if "dep" not in voyage:
                continue

            for pays, deps in voyage["dep"].items():
                for dep in deps:
                    compteur_temp[(pays, dep)] += 1

    # Conversion en DataFrame
    if granu == 0:
        df = pd.DataFrame(
            [(pays, n) for pays, n in compteur_temp.items()], columns=["pays", "N"]
        )

    else:
        df = pd.DataFrame(
            [(pays, lieu, n) for (pays, lieu), n in compteur_temp.items()],
            columns=["pays", "subdivision", "N"],
        )

    return df.sort_values("N", ascending=False).reset_index(drop=True)


## 7.2 -- Départements vers régions --------------------------------------------


def compter_occurrences_regions_depuis_departements(
    dict_voyages: dict, df_superficie: pd.DataFrame
):
    """
    Compte le nombre de voyages contenant chaque région à partir des
    départements visités.

    Si plusieurs départements d'une même région sont visités lors d'un
    même voyage, la région n'est comptée qu'une seule fois.

    Renvoie un DataFrame avec les colonnes :
        - pays
        - subdivision (région)
        - N
    """

    # Test de granularité
    assert isid(df=df_superficie, colonnes=["name_0", "name_2"], blabla=1)

    compteur = Counter()

    for voyage in dict_voyages.values():

        if "dep" not in voyage:
            continue

        for pays, deps in voyage["dep"].items():

            regions = (
                pd.DataFrame(
                    {
                        "pays": pays,
                        "subdivision": deps,
                    }
                )
                .merge(
                    df_superficie,
                    left_on=["pays", "subdivision"],
                    right_on=["name_0", "name_2"],
                    how="left",
                )["name_1"]
                .dropna()
                .unique()
            )

            for region in regions:
                compteur[(pays, region)] += 1

    return pd.DataFrame(
        [(pays, region, n) for (pays, region), n in compteur.items()],
        columns=["pays", "subdivision", "N"],
    )
