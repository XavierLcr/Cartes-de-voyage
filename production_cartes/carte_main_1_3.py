################################################################################
# Projet de cartes de voyage                                                   #
# 1.3 – Création de la base de données et de la production des graphiques      #
################################################################################

import os, sys, gc
from production_cartes import creer_carte_1_1, creer_graphique_1_2


def cree_gdf_depuis_dicts(
    liste_dfs: list,
    liste_dicts: list,
    granularite_visite=1,
    granularite_reste=1,
):
    r"""
    Cette fonction crée un graphique à partir des données mondiales en combinant plusieurs niveaux de granularité.
    Elle génère un GeoDataFrame contenant les informations sur les lieux visités et non visités, avec une indicatrice de visite.
    Ces informations sont ensuite utilisées pour créer une carte avec les lieux marqués comme visités ou non.

    Paramètres :
    – df_monde (DataFrame) : DataFrame contenant les informations géographiques mondiales, incluant des colonnes comme `NAME_0` pour les pays
      et `NAME_{granularite}` pour les régions.
    – df_monde_granu (GeoDataFrame) : Un GeoDataFrame avec les informations géographiques globales (pays, régions, etc.)
      et la géométrie associée.
    – dict1 (dict, optionnel) : Dictionnaire représentant les informations pour le deuxième niveau de granularité (par exemple, régions).
    – dict2 (dict, optionnel) : Dictionnaire représentant les informations pour le troisième niveau de granularité.
    – dict3 (dict, optionnel) : Dictionnaire représentant les informations pour le quatrième niveau de granularité.
    – dict4 (dict, optionnel) : Dictionnaire représentant les informations pour le cinquième niveau de granularité.
    – dict5 (dict, optionnel) : Dictionnaire représentant les informations pour le sixième niveau de granularité.
    – granularite (int, optionnel) : Le niveau de granularité pour lequel vous souhaitez créer le graphique. Par défaut, la granularité est de 1 (région).
    """

    return creer_carte_1_1.ajouter_indicatrice_visite(
        gdf_monde=liste_dfs[granularite_reste],
        gdf_visite=creer_carte_1_1.cree_base_toutes_granularites(
            liste_dfs=liste_dfs,
            liste_dicts=liste_dicts,
            granularite_objectif=granularite_visite,
        ),
        granularite=granularite_reste,
    )


def cas_pays_multiples(df, langue: str, liste_pays: list, nom_carte: str, pays_trad: dict):
    return {
        "nom_langue": pays_trad.get(nom_carte, {}).get(langue, nom_carte),
        "gdf": df[df["Pays"].isin(liste_pays)],
    }


def tous_cas_pays_multiples(
    dictionnaire_pays: dict,
    pays: str,
    df,
    pays_trad: dict,
    langue: str = "français",
):

    resultat = {
        "nom_groupe_pays": None,
        "nom_langue": None,
        "gdf_reduit": None,
        "dans_la_liste": False,
        "deja_fait": False,
    }

    for groupe_pays in list(dictionnaire_pays.keys()):

        if pays in dictionnaire_pays[groupe_pays]["liste"]:

            if dictionnaire_pays[groupe_pays]["deja_fait"] == True:
                resultat["deja_fait"] = True
                resultat["dans_la_liste"] = True
                return resultat

            resultat["nom_groupe_pays"] = groupe_pays
            resultat["dans_la_liste"] = True
            bases = cas_pays_multiples(
                df=df,
                nom_carte=dictionnaire_pays[groupe_pays]["categorie"],
                langue=langue,
                pays_trad=pays_trad,
                liste_pays=dictionnaire_pays[groupe_pays]["liste"],
            )
            resultat["nom_langue"] = bases["nom_langue"]
            resultat["gdf_reduit"] = bases["gdf"]

            return resultat

    return resultat


def creer_graphiques_pays(
    gdf_visite,
    gdf_fond,
    gdf_fond_regions,
    direction_res: str,
    pays_trad: dict,
    dictionnaire_pays_unis: dict,
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
    couleur_non_visites: str = "#ecebed",
    couleur_fond: str = "#FFFFFF",
    couleur_lacs: str = "#CEE3F5",
    qualite: int = 200,
    langue: str = "français",
    blabla: bool = True,
    max_cartes_additionnelles: int | None = 10,
    sortir_cartes_granu_inf=True,
    granularite_objectif: int = 1,
    tracker=None,
    afficher_nom_lieu: bool = True,
):
    """Crée les cartes de chaque pays"""

    # Aucun pays des groupes de pays n'a déjà été fait
    for p in list(dictionnaire_pays_unis.keys()):
        dictionnaire_pays_unis[p]["deja_fait"] = False

    # Récupérer les valeurs uniques de la colonne 'Pays' après filtrage
    liste_pays_visites = sorted(
        gdf_visite.loc[gdf_visite["Visite"] == True, "Pays"].unique().tolist()
    )

    # On gère la carte de fond des régions
    gdf_fond_regions = gdf_fond_regions[gdf_fond_regions["NAME_0"].isin(liste_pays_visites)]

    for i in range(len(liste_pays_visites)):

        langue_i = pays_trad.get(liste_pays_visites[i], {}).get(langue, liste_pays_visites[i])

        if tracker:
            tracker.notify(langue_i)

        if blabla == True and (i + 1) % 5 == 0 and (i + 1) != len(liste_pays_visites):
            print(f"{i+1}/{len(liste_pays_visites)} : {langue_i}", end=".\n")
        elif blabla == True:
            print_i = f"{i+1}/{len(liste_pays_visites)} : {langue_i}. "
            sys.stdout.write(print_i.ljust(25))
            sys.stdout.flush()

        groupe_pays_res_i = tous_cas_pays_multiples(
            dictionnaire_pays=dictionnaire_pays_unis,
            pays=liste_pays_visites[i],
            df=gdf_visite,
            pays_trad=pays_trad,
            langue=langue,
        )

        gdf_fond_regions_i = gdf_fond_regions.copy()

        if groupe_pays_res_i["deja_fait"] == True and groupe_pays_res_i["dans_la_liste"] == True:
            continue

        if groupe_pays_res_i["deja_fait"] == False and groupe_pays_res_i["dans_la_liste"] == True:

            langue_i = groupe_pays_res_i["nom_langue"]
            gdf_i = groupe_pays_res_i["gdf_reduit"]

            dictionnaire_pays_unis[groupe_pays_res_i["nom_groupe_pays"]]["deja_fait"] = True

            gdf_monde_i = gdf_fond.copy()

        else:

            gdf_i = gdf_visite.copy(deep=True)
            gdf_i = gdf_i[gdf_i["Pays"] == liste_pays_visites[i]]

            if len(gdf_i) == 1:
                continue

            if liste_pays_visites[i] in ["Russia"]:
                valeur_projection = "+proj=lcc +lat_1=50 +lat_2=70 +lat_0=60 +lon_0=90"
                gdf_i = gdf_i.to_crs(valeur_projection)
                gdf_eau = gdf_eau.to_crs(valeur_projection)
                gdf_fond_regions_i = gdf_fond_regions_i.to_crs(valeur_projection)

            gdf_monde_i = None

        nom_pays_i = f"{(nom_indiv + ' – ') if nom_indiv else ''}{langue_i}.{format}"
        if (
            sortir_cartes_granu_inf == True
            or max(gdf_i.loc[gdf_i["Visite"] == 1, "Granu"]) >= granularite_objectif
        ):

            creer_graphique_1_2.creer_image_carte(
                gdf=gdf_i,
                gdf_monde=gdf_monde_i,
                gdf_eau=gdf_eau,
                gdf_regions=gdf_fond_regions_i,
                theme=theme,
                teintes_autorisees=teinte,
                couleur_non_visites=couleur_non_visites,
                couleur_de_fond=couleur_fond,
                couleur_lacs=couleur_lacs,
                chemin_impression=os.path.join(direction_res, langue_i),
                nom=nom_pays_i,
                qualite=qualite,
                blabla=False,
                max_cartes_additionnelles=max_cartes_additionnelles,
                afficher_nom_lieu=afficher_nom_lieu,
            )
        del gdf_i

        if i % 10 == 0:
            gc.collect()


def creer_graphique_region(
    gdf_visite_ori,
    gdf_fond_ori,
    df_fond_granu_1,
    direction_resultat: str,
    pays_trad: dict,
    liste_pays_region: list,
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
    couleur_non_visites: str = "#ecebed",
    couleur_fond: str = "#FFFFFF",
    couleur_lacs: str = "#CEE3F5",
    qualite: int = 200,
    langue: str = "français",
    nom_region: str = "World",
    blabla=True,
    max_cartes_additionnelles: int | None = 10,
    sortir_cartes_granu_inf=True,
    granularite_objectif: int = 1,
    afficher_nom_lieu: bool = True,
):
    """Crée la carte d'une région"""

    gdf_visite = gdf_visite_ori.copy(deep=True)
    gdf_fond = gdf_fond_ori.copy(deep=True)

    if nom_region == "World":
        nom_langue_region = pays_trad.get("World Map", {}).get(langue, "World Map")
        gdf_region = gdf_visite.copy()

    else:

        if liste_pays_region is None:
            return

        # Nom du dossier
        direction_resultat = os.path.join(
            direction_resultat, pays_trad.get(nom_region, {}).get(langue, nom_region)
        )

        # Nom de la carte simple
        nom_langue_region = pays_trad.get(
            (f"Map of the {nom_region}" if nom_region == "Middle East" else f"Map of {nom_region}"),
            {},
        ).get(langue, f"Map of the {nom_region}")

        # Bases de données
        gdf_region = gdf_visite[gdf_visite["Pays"].isin(liste_pays_region)]

    if nom_region == "Asia" or nom_region == "Oceania":
        valeur_projection = "+proj=lcc +lat_1=50 +lat_2=70 +lat_0=60 +lon_0=90"
        gdf_region = gdf_region.to_crs(valeur_projection)
        gdf_fond = gdf_fond.to_crs(valeur_projection)
        df_fond_granu_1 = df_fond_granu_1.to_crs(valeur_projection)
        gdf_eau = gdf_eau.to_crs(valeur_projection)

    gdf_if = gdf_region[gdf_region["Visite"] == True]

    if len(gdf_if) > 0:

        if max(gdf_if["Granu"]) >= granularite_objectif or sortir_cartes_granu_inf == True:

            if blabla:
                print(nom_langue_region, end=". ")

            creer_graphique_1_2.creer_image_carte(
                gdf=gdf_region,
                gdf_monde=gdf_fond,
                gdf_regions=df_fond_granu_1,
                gdf_eau=gdf_eau,
                theme=theme,
                teintes_autorisees=teinte,
                couleur_non_visites=couleur_non_visites,
                couleur_de_fond=couleur_fond,
                couleur_lacs=couleur_lacs,
                chemin_impression=direction_resultat,
                nom=f"{nom_indiv + ' – ' if nom_indiv else ''}{nom_langue_region}.{format}",
                qualite=qualite,
                blabla=False,
                max_cartes_additionnelles=max_cartes_additionnelles,
                afficher_nom_lieu=afficher_nom_lieu,
            )

    del gdf_region, gdf_fond


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
    couleur_non_visites: str = "#ecebed",
    couleur_fond: str = "none",
    couleur_lacs: str = "#CEE3F5",
    qualite: int = 200,
    langue: str = "français",
    blabla: bool = False,
    pays_individuel: bool = True,
    carte_du_monde: bool = True,
    max_cartes_additionnelles: int | None = 10,
    sortir_cartes_granu_inf: bool = True,
    tracker=None,
    afficher_nom_lieu: bool = True,
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

        df_visite = cree_gdf_depuis_dicts(
            liste_dfs=liste_dfs,
            liste_dicts=liste_dicts,
            granularite_reste=granularite_reste,
            granularite_visite=granularite_visite,
        )
    else:
        return "Aucune base des pays visités n'existe ou ne peut être créée..."

    if liste_regions is None:
        liste_regions = {}

    if carte_du_monde == True:
        liste_regions["World"] = ["Inutile"]

    # Création des graphes mondial et régionaux
    for r in list(liste_regions.keys()):

        if tracker:
            tracker.notify(noms_pays.get(r, {}).get(langue, r))

        creer_graphique_region(
            gdf_visite_ori=df_visite,
            gdf_fond_ori=liste_dfs[0],
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
            gdf_eau=gdf_eau,
            max_cartes_additionnelles=max_cartes_additionnelles,
            df_fond_granu_1=liste_dfs[1],
            granularite_objectif=granularite_visite,
            sortir_cartes_granu_inf=sortir_cartes_granu_inf,
            afficher_nom_lieu=afficher_nom_lieu,
        )

    gc.collect()

    # Carte des pays
    if granularite_visite != 0 and pays_individuel == True:

        if blabla == True and len(liste_regions) > 0:
            print("\n\n")

        creer_graphiques_pays(
            gdf_visite=df_visite,
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
            qualite=qualite,
            langue=langue,
            blabla=blabla,
            dictionnaire_pays_unis=dictionnaire_pays_unis,
            max_cartes_additionnelles=max_cartes_additionnelles,
            granularite_objectif=granularite_visite,
            sortir_cartes_granu_inf=sortir_cartes_granu_inf,
            tracker=tracker,
            afficher_nom_lieu=afficher_nom_lieu,
        )

    if blabla == True:
        print("\n\n✅", end="\n\n")
