################################################################################
# Projet de cartes de voyage                                                   #
# _3_Calculs/                                                                  #
# 3.4 – Création de la base de données et de la production des graphiques      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, gc
import pandas as pd
from _3_Calculs._3_1_creer_carte import cree_gdf_depuis_dicts
from _3_Calculs import _3_2_creer_graphique
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_dossier,
    reordonner_dict,
    voyages_vers_destinations_une_granu,
)
from _0_Utilitaires._0_6_fonctions_utiles_traductions import traduire_pays

# 1 -- Fonction de création d'un dictionnaire des cartes à sortir --------------


def lister_cartes_a_publier(
    regroupements_pays_ref: dict,
    continents_ref: dict,
    traductions_ref: dict,
    langue: str,
    pays: bool,
    monde: bool,
    continents: list | None,
    voyages: dict,
    sortir_cartes_granu_inf: bool,
    granularite_objectif: int,
):

    # Pays visités
    pays_visites_regions = list(
        voyages_vers_destinations_une_granu(dict_voyages=voyages, clef="region").keys()
    )
    pays_visites_departements = list(
        voyages_vers_destinations_une_granu(dict_voyages=voyages, clef="dep").keys()
    )
    pays_visites = list(set(pays_visites_regions + pays_visites_departements))

    # Initialisation du résultat
    dict_temp = {}

    # Ajout de la carte du monde
    if monde:
        dict_temp[
            traduire_pays(referentiel=traductions_ref, pays="World Map", langue=langue)
        ] = None

    # Ajout des continents (si souhaité)
    if continents:

        dict_cont = {}
        for cont, cont_pays in continents_ref.items():

            # Nom traduit du continent
            nom_temp = traduire_pays(
                referentiel=traductions_ref, pays=cont, langue=langue
            )

            # Continent souhaité
            if cont in continents:

                # Pays visité
                if len(set(pays_visites) & set(cont_pays)) >= 1:

                    # Pays à la bonne granularité
                    if (
                        sortir_cartes_granu_inf
                        or granularite_objectif <= 1
                        or len(set(pays_visites_departements) & set(cont_pays)) >= 1
                    ):

                        dict_cont[nom_temp] = cont_pays

        dict_temp = dict_temp | reordonner_dict(dictionnaire=dict_cont, clefs=None)

    # Ajout des pays ou regroupements de pays (si souhaité)
    if granularite_objectif >= 2 and sortir_cartes_granu_inf == False:
        pays_visites = pays_visites_departements.copy()

    if pays and len(pays_visites) > 0:

        dict_pays = {}
        for pays_temp in pays_visites:

            inclus = False

            # Le pays est présent dans un regroupement
            for clef, val in regroupements_pays_ref.items():

                pays_regroup = val.get("liste")
                nom_regroup = traduire_pays(
                    referentiel=traductions_ref,
                    pays=val.get("categorie"),
                    langue=langue,
                )

                # Pays/Regroupement de pays visité
                if pays_temp in val.get("liste"):
                    dict_pays[nom_regroup] = pays_regroup
                    inclus = True
                    continue

            # Le pays est isolé
            if not inclus:
                nom_pays = traduire_pays(
                    referentiel=traductions_ref,
                    pays=pays_temp,
                    langue=langue,
                )
                dict_pays[nom_pays] = [pays_temp]

        dict_temp = dict_temp | reordonner_dict(dictionnaire=dict_pays, clefs=None)

    # Renvoi
    return dict_temp


# 2 -- Fonction créant une carte -----------------------------------------------


def creer_une_carte(
    gdf: pd.DataFrame,
    gdf_0: pd.DataFrame | None,
    gdf_1: pd.DataFrame | None,
    gdf_eau: pd.DataFrame | None,
    direction_dossier: str,
    **kwargs,
):

    # Périmètre de la carte
    carte_nom = kwargs.get("carte_nom", None)
    carte_liste_pays = kwargs.get("carte_liste_pays")

    # Préférences techniques de l'individu
    individu_nom = kwargs.get("individu_nom", "")
    format = kwargs.get("format", "png")
    qualite = kwargs.get("qualite", 200)
    reprojeter = kwargs.get("reprojeter", False)
    limite_n_cartes = kwargs.get(
        "limite_n_cartes",
        10,
    )

    # Affichage des noms des lieux
    afficher_nom_lieu = kwargs.get(
        "afficher_nom_lieu",
        False,
    )
    langue = kwargs.get("langue", None)
    dict_trad_pays = kwargs.get("dict_trad_pays", {})

    # Style de la carte
    theme = kwargs.get(
        "theme",
        {
            "min_luminosite": 0.8,
            "max_luminosite": 0.95,
            "min_saturation": 0.2,
            "max_saturation": 0.4,
        },
    )
    teinte = kwargs.get("teinte", None)
    couleur_non_visites = kwargs.get(
        "couleur_non_visites",
        "#ECEBED",
    )
    couleur_pays_contours = kwargs.get(
        "couleur_pays_contours",
        "#F9F9FA",
    )
    couleur_fond = kwargs.get(
        "couleur_fond",
        "#FFFFFF",
    )
    couleur_lacs = kwargs.get(
        "couleur_lacs",
        "#CEE3F5",
    )

    # Envoi des cartes
    adresse_email = kwargs.get(
        "adresse_email",
        None,
    )

    if carte_liste_pays:
        gdf = gdf[gdf["Pays"].isin(carte_liste_pays)]
        gdf_1 = gdf_1[gdf_1["name_0"].isin(carte_liste_pays)]

    # Création du nom de la carte
    if not carte_nom:
        carte_nom = "Temp"

    if individu_nom:
        carte_nom = f"{carte_nom} – {individu_nom}"

    carte_nom = f"{carte_nom}.{format}"

    # Création du graphique
    _3_2_creer_graphique.creer_image_carte(
        gdf=gdf,
        gdf_monde=gdf_0,
        gdf_regions=gdf_1,
        gdf_eau=gdf_eau,
        theme=theme,
        teintes_autorisees=teinte,
        couleur_non_visites=couleur_non_visites,
        couleur_pays_contours=couleur_pays_contours,
        couleur_de_fond=couleur_fond,
        couleur_lacs=couleur_lacs,
        chemin_impression=direction_dossier,
        nom=carte_nom,
        qualite=qualite,
        blabla=False,
        limite_n_cartes=limite_n_cartes,
        afficher_nom_lieu=afficher_nom_lieu,
        marge_carte=0.03,
        reprojeter=reprojeter,
        adresse_email=adresse_email,
        langue=langue,
        dict_trad_pays=dict_trad_pays,
    )


# 3 -- Fonction créant un ensemble de graphiques -------------------------------


def creer_multiples_cartes(
    liste_dfs: list,
    liste_dicts: list,
    gdf_eau: pd.DataFrame | None,
    granularite_visite: int,
    granularite_reste: int,
    dict_cartes: dict,
    direction_dossier,
    **kwargs,
):

    # Table des visites
    df_temp = cree_gdf_depuis_dicts(
        liste_dfs=liste_dfs,
        liste_dicts=liste_dicts,
        granularite_visite=granularite_visite,
        granularite_reste=granularite_reste,
    )

    # Récupération des arguments
    tracker = kwargs.get("tracker", None)
    ouvrir_dossier_stockage = kwargs.get("ouvrir_dossier_stockage", False)

    # Pays à reprojeter
    pays_reprojection = ["Russia", "United States"]

    # Itération sur les cartes à publier
    for i, (nom, liste_pays) in enumerate(dict_cartes.items(), start=1):

        if tracker:
            tracker.notify(f"{i}/{len(dict_cartes.keys())} : {nom}")

        creer_une_carte(
            gdf=df_temp,
            gdf_0=liste_dfs[0],
            gdf_1=liste_dfs[1],
            gdf_eau=gdf_eau,
            # Absence de dossier additionnel pour la Carte du monde
            direction_dossier=(
                direction_dossier
                if liste_pays is None
                else os.path.join(direction_dossier, nom)
            ),
            carte_nom=nom,
            carte_liste_pays=liste_pays,
            reprojeter=len(set(liste_pays or []) & set(pays_reprojection)) > 0,
            **kwargs,
        )

        gc.collect()

    # Ouverture du dossier des résultats
    if ouvrir_dossier_stockage:
        ouvrir_dossier(chemin=direction_dossier)
