################################################################################
# Projet de cartes de voyage                                                   #
# _3_Calculs/                                                                  #
# 3.4 – Création de la base de données et de la production des graphiques      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys, gc
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
                if len(set(pays_visites) & set(cont_pays)) > 1:
                    # Pays à la bonne granularité
                    if (
                        sortir_cartes_granu_inf
                        or granularite_objectif <= 1
                        or len(set(pays_visites_departements) & set(cont_pays)) > 1
                    ):
                        dict_cont[nom_temp] = cont_pays

        dict_temp = dict_temp | reordonner_dict(dictionnaire=dict_cont, clefs=None)

    # Ajout des pays ou regroupements de pays (si souhaité)
    if granularite_objectif >= 2 & sortir_cartes_granu_inf == False:
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
    afficher_nom_lieu = kwargs.get(
        "afficher_nom_lieu",
        False,
    )

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
    for nom, liste_pays in dict_cartes.items():

        if tracker:
            tracker.notify(nom)

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


# 2 -- Fonction renvoyant la table et le nom des groupes de pays ---------------


def cas_pays_multiples(
    df, langue: str, liste_pays: list, nom_carte: str, pays_trad: dict
):
    return {
        "nom_langue": pays_trad.get(nom_carte, {}).get(langue, nom_carte),
        "gdf": df[df["Pays"].isin(liste_pays)],
    }


# 3 -- Fonction renvoyant les informations d'un groupe de pays -----------------


def tous_cas_pays_multiples(
    dict_pays: dict,
    pays: str,
    df,
    pays_trad: dict,
    langue: str = "français",
):
    """
    tous_cas_pays_multiples informe de si un pays doit être groupé et de si le
    graphique a déjà été créé. Si le graphique avec plusieurs pays doit être créé,
    renvoie la table à considérer, ainsi que le nom du pays et la langue.

    :param dict_pays: Dictionnaire contenant les regroupements de pays.
    :type dict_pays: dict
    :param pays: Le pays à étudier.
    :type pays: str
    :param df: La table consolidée du monde à la granularité souhaitée.
    :param pays_trad: Traduction du nom des pays et des groupes de pays.
    :type pays_trad: dict
    :param langue: Langue de la traduction.
    :type langue: str
    """

    resultat = {
        "nom_groupe_pays": None,
        "nom_langue": None,
        "gdf_reduit": None,
        "dans_la_liste": False,
        "deja_fait": False,
    }

    for groupe_pays in list(dict_pays.keys()):

        if pays in dict_pays[groupe_pays]["liste"]:

            if dict_pays[groupe_pays]["deja_fait"] == True:
                resultat["deja_fait"] = True
                resultat["dans_la_liste"] = True
                return resultat

            resultat["nom_groupe_pays"] = groupe_pays
            resultat["dans_la_liste"] = True
            bases = cas_pays_multiples(
                df=df,
                nom_carte=dict_pays[groupe_pays]["categorie"],
                langue=langue,
                pays_trad=pays_trad,
                liste_pays=dict_pays[groupe_pays]["liste"],
            )
            resultat["nom_langue"] = bases["nom_langue"]
            resultat["gdf_reduit"] = bases["gdf"]

            return resultat

    return resultat


# 4 -- Fonction de création des cartes des pays --------------------------------


def creer_graphiques_pays(
    gdf_visite,
    gdf_fond,
    gdf_fond_regions,
    direction_res: str,
    pays_trad: dict,
    dict_pays_unis: dict,
    gdf_eau=None,
    nom_indiv: str = "Xavier",
    format: str = "png",
    theme: dict = {
        "min_luminosite": 0.8,
        "max_luminosite": 0.95,
        "min_saturation": 0.2,
        "max_saturation": 0.4,
    },
    teinte=None,
    couleur_non_visites: str = "#ECEBED",
    couleur_pays_contours: str = "#ECEBED",
    couleur_fond: str = "#FFFFFF",
    couleur_lacs: str = "#CEE3F5",
    qualite: int = 200,
    langue: str = "français",
    blabla: bool = True,
    limite_n_cartes: int | None = 10,
    sortir_cartes_granu_inf=True,
    granularite_objectif: int = 1,
    tracker=None,
    afficher_nom_lieu: bool = True,
    adresse_email: str | None = None,
):
    """Crée les cartes de chaque pays"""

    # Aucun pays des groupes de pays n'a déjà été fait
    for p in list(dict_pays_unis.keys()):
        dict_pays_unis[p]["deja_fait"] = False

    # Récupérer les valeurs uniques de la colonne 'Pays' après filtrage
    liste_pays_visites = sorted(
        gdf_visite.loc[gdf_visite["Visite"] == True, "Pays"].unique().tolist()
    )

    for i in range(len(liste_pays_visites)):

        nom_i = pays_trad.get(liste_pays_visites[i], {}).get(
            langue, liste_pays_visites[i]
        )

        if blabla == True and (i + 1) % 5 == 0 and (i + 1) != len(liste_pays_visites):
            print(f"{i+1}/{len(liste_pays_visites)} : {nom_i}", end=".\n")
        elif blabla == True:
            print_i = f"{i+1}/{len(liste_pays_visites)} : {nom_i}. "
            sys.stdout.write(print_i.ljust(25))
            sys.stdout.flush()

        groupe_pays_i = tous_cas_pays_multiples(
            dict_pays=dict_pays_unis,
            pays=liste_pays_visites[i],
            df=gdf_visite,
            pays_trad=pays_trad,
            langue=langue,
        )

        if (
            groupe_pays_i["deja_fait"] == True
            and groupe_pays_i["dans_la_liste"] == True
        ):

            if (
                sortir_cartes_granu_inf == True
                or max(
                    gdf_visite.loc[
                        (gdf_visite["Visite"] == 1)
                        & (gdf_visite["Pays"] == liste_pays_visites[i]),
                        "Granu",
                    ]
                )
                >= granularite_objectif
            ) and tracker:
                tracker.notify(nom_i)

            continue

        elif (
            groupe_pays_i["deja_fait"] == False
            and groupe_pays_i["dans_la_liste"] == True
        ):

            nom_i = groupe_pays_i["nom_langue"]
            gdf_i = groupe_pays_i["gdf_reduit"]

            dict_pays_unis[groupe_pays_i["nom_groupe_pays"]]["deja_fait"] = True

        else:

            gdf_i = gdf_visite[gdf_visite["Pays"] == liste_pays_visites[i]].copy()

            if len(gdf_i) == 1:
                continue

        nom_pays_i = f"{(nom_indiv + ' – ') if nom_indiv else ''}{nom_i}.{format}"
        if (
            sortir_cartes_granu_inf == True
            or max(gdf_i.loc[gdf_i["Visite"] == 1, "Granu"]) >= granularite_objectif
        ):

            if tracker:
                tracker.notify(nom_i)

            _3_2_creer_graphique.creer_image_carte(
                gdf=gdf_i,
                gdf_monde=gdf_fond,
                gdf_eau=gdf_eau,
                gdf_regions=gdf_fond_regions,
                theme=theme,
                teintes_autorisees=teinte,
                couleur_non_visites=couleur_non_visites,
                couleur_de_fond=couleur_fond,
                couleur_lacs=couleur_lacs,
                couleur_pays_contours=couleur_pays_contours,
                chemin_impression=os.path.join(direction_res, nom_i),
                nom=nom_pays_i,
                qualite=qualite,
                blabla=False,
                limite_n_cartes=limite_n_cartes,
                afficher_nom_lieu=afficher_nom_lieu,
                reprojeter=liste_pays_visites[i] in ["Russia", "United States"],
                adresse_email=adresse_email,
            )
        del gdf_i

        if i % 10 == 0:
            gc.collect()


# 5 -- Fonction créant la carte d'une région du monde --------------------------


def creer_graphique_region(
    gdf,
    gdf_0,
    gdf_1,
    gdf_eau,
    direction_resultat: str,
    pays_trad: dict,
    liste_pays_region: list,
    nom_indiv: str = "Xavier",
    format: str = "png",
    theme: dict = {
        "min_luminosite": 0.8,
        "max_luminosite": 0.95,
        "min_saturation": 0.2,
        "max_saturation": 0.4,
    },
    teinte=None,
    couleur_non_visites: str = "#ECEBED",
    couleur_pays_contours: str = "#ECEBED",
    couleur_fond: str = "#FFFFFF",
    couleur_lacs: str = "#CEE3F5",
    qualite: int = 200,
    langue: str = "français",
    nom_region: str = "World",
    blabla=True,
    limite_n_cartes: int | None = 10,
    sortir_cartes_granu_inf=True,
    granularite_objectif: int = 1,
    afficher_nom_lieu: bool = True,
    adresse_email: str | None = None,
):
    """Crée la carte d'une région"""

    gdf_temp = gdf.copy(deep=True)

    if nom_region == "World":
        nom_langue_region = pays_trad.get("World Map", {}).get(langue, "World Map")
    else:

        if liste_pays_region is None:
            return

        # Nom du dossier
        direction_resultat = os.path.join(
            direction_resultat, pays_trad.get(nom_region, {}).get(langue, nom_region)
        )

        # Nom de la carte simple
        nom_langue_region = pays_trad.get(
            (
                f"Map of the {nom_region}"
                if nom_region == "Middle East"
                else f"Map of {nom_region}"
            ),
            {},
        ).get(langue, f"Map of the {nom_region}")

        # Bases de données
        gdf_temp = gdf_temp[gdf_temp["Pays"].isin(liste_pays_region)]

    if gdf_temp["Visite"].any():

        if (
            gdf_temp.loc[gdf_temp["Visite"], "Granu"].max() >= granularite_objectif
            or sortir_cartes_granu_inf == True
        ):

            if blabla:
                print(nom_langue_region, end=". ")

            _3_2_creer_graphique.creer_image_carte(
                gdf=gdf_temp,
                gdf_monde=gdf_0,
                gdf_regions=gdf_1,
                gdf_eau=gdf_eau,
                theme=theme,
                teintes_autorisees=teinte,
                couleur_non_visites=couleur_non_visites,
                couleur_de_fond=couleur_fond,
                couleur_lacs=couleur_lacs,
                couleur_pays_contours=couleur_pays_contours,
                chemin_impression=direction_resultat,
                nom=f"{nom_indiv + ' – ' if nom_indiv else ''}{nom_langue_region}.{format}",
                qualite=qualite,
                blabla=False,
                limite_n_cartes=limite_n_cartes,
                afficher_nom_lieu=afficher_nom_lieu,
                reprojeter=nom_region in ["Asia", "North America"],
                adresse_email=adresse_email,
            )

    del gdf_temp


# 6 -- Fonction créant et publiant l'ensemble des cartes souhaitées ------------


def cree_graphe_depuis_debut(
    liste_dfs: list,
    liste_dicts,
    noms_pays: dict,
    direction_resultat: str,
    dictionnaire_pays_unis: dict,
    liste_regions: dict | None = None,
    gdf_eau=None,
    nom_indiv: str = "Xavier",
    format: str = "jpg",
    granularite_visite: int = 1,
    granularite_reste: int = 1,
    theme: dict = {
        "min_luminosite": 0.8,
        "max_luminosite": 0.95,
        "min_saturation": 0.2,
        "max_saturation": 0.4,
    },
    teinte: list | None = None,
    couleur_non_visites: str = "#ECEBED",
    couleur_pays_contours: str = "#ECEBED",
    couleur_fond: str = "none",
    couleur_lacs: str = "#CEE3F5",
    qualite: int = 200,
    langue: str = "français",
    blabla: bool = False,
    pays_individuel: bool = True,
    carte_du_monde: bool = True,
    limite_n_cartes: int | None = 10,
    sortir_cartes_granu_inf: bool = True,
    tracker=None,
    afficher_nom_lieu: bool = True,
    ouvrir_direction_resultat: bool = True,
    adresse_email: str | None = None,
):
    r"""
    Cette fonction crée une carte géographique à partir de données mondiales en utilisant des dictionnaires définissant
    différents niveaux de granularité (par exemple, pays, régions, etc.). Elle génère une carte et l'exporte sous un fichier
    image à l'emplacement spécifié. Le niveau de granularité et les informations sur les lieux visités peuvent être ajustés
    à l'aide des paramètres passés à la fonction.

    Paramètres :
    – df_monde (DataFrame) : DataFrame contenant les informations géographiques mondiales (par exemple, pays, continents).
    – df_monde_granu (GeoDataFrame) : Un GeoDataFrame contenant les informations géographiques détaillées (pays, régions, etc.)
      et leurs géométries associées.
    – direction_resultat (str) : Chemin où le fichier d'image résultant sera sauvegardé.
    – nom_export (str, optionnel) : Le nom du fichier d'image exporté. Par défaut, il est "Carte_du_monde.jpg".
    – df_monde_0 (DataFrame, optionnel) : Un DataFrame supplémentaire avec des informations supplémentaires à intégrer dans la carte.
    – liste_dicts (list) : Dictionnaires représentant différents niveaux de granularité pour
      l'affichage (pays, régions, départements, etc.).
    – granularite (int, optionnel) : Le niveau de granularité à utiliser pour la carte. Par défaut, la granularité est de 1 (régions).

    Retourne :
    – (GeoDataFrame) : Un GeoDataFrame prêt à être visualisé, contenant les informations géographiques et les données associées
      aux lieux visités ou non visités.
    """

    # Gestion de la création ou utilisation de la base utilisée
    if any(isinstance(element, dict) for element in liste_dicts):

        gdf_temp = cree_gdf_depuis_dicts(
            liste_dfs=liste_dfs,
            liste_dicts=liste_dicts,
            granularite_reste=granularite_reste,
            granularite_visite=granularite_visite,
        )
    else:
        return "Aucune base des pays visités n'existe ou ne peut être créée..."

    liste_regions = liste_regions or {}
    if carte_du_monde == True:
        liste_regions["World"] = ["Inutile"]

    # Création des graphes mondial et régionaux
    for r in list(liste_regions.keys()):

        if tracker:
            tracker.notify(noms_pays.get(r, {}).get(langue, r))

        creer_graphique_region(
            gdf=gdf_temp,
            gdf_0=liste_dfs[0],
            gdf_1=liste_dfs[1],
            gdf_eau=gdf_eau,
            direction_resultat=direction_resultat,
            pays_trad=noms_pays,
            nom_indiv=nom_indiv,
            format=format,
            theme=theme,
            teinte=teinte,
            couleur_non_visites=couleur_non_visites,
            couleur_fond=couleur_fond,
            couleur_lacs=couleur_lacs,
            qualite=qualite,
            langue=langue,
            liste_pays_region=liste_regions[r],
            nom_region=r,
            blabla=blabla,
            limite_n_cartes=limite_n_cartes,
            granularite_objectif=granularite_visite,
            sortir_cartes_granu_inf=sortir_cartes_granu_inf,
            afficher_nom_lieu=afficher_nom_lieu,
            adresse_email=adresse_email,
        )

    gc.collect()

    # Carte des pays
    if granularite_visite != 0 and pays_individuel == True:

        if blabla == True and len(liste_regions) > 0:
            print("\n")

        creer_graphiques_pays(
            gdf_visite=gdf_temp,
            gdf_fond=liste_dfs[0],
            gdf_eau=gdf_eau,
            gdf_fond_regions=liste_dfs[1],
            direction_res=direction_resultat,
            pays_trad=noms_pays,
            nom_indiv=nom_indiv,
            format=format,
            theme=theme,
            teinte=teinte,
            couleur_non_visites=couleur_non_visites,
            couleur_lacs=couleur_lacs,
            couleur_fond=couleur_fond,
            couleur_pays_contours=couleur_pays_contours,
            qualite=qualite,
            langue=langue,
            blabla=blabla,
            dict_pays_unis=dictionnaire_pays_unis,
            limite_n_cartes=limite_n_cartes,
            granularite_objectif=granularite_visite,
            sortir_cartes_granu_inf=sortir_cartes_granu_inf,
            tracker=tracker,
            afficher_nom_lieu=afficher_nom_lieu,
            adresse_email=adresse_email,
        )

    # Ouverture du dossier des résultats
    if ouvrir_direction_resultat:
        ouvrir_dossier(chemin=direction_resultat)

    if blabla == True:
        print("\n\n✅", end="\n\n")
