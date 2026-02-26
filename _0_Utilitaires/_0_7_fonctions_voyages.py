################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.7 – Fonctions utiles afin de manupuler des voyages                         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import re

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
