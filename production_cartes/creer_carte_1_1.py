################################################################################
# Projet de cartes de voyage                                                   #
# 1.1 – Fichier de création de la base de données                              #
################################################################################

import pandas as pd


def creer_base_une_granularite(
    df,
    liste_destinations: dict,
    granularite: int = 1,
):
    """Crée la base pour une liste de pays à un niveau de granularité donnée

    Args:
        df : la base geopandas du monde
        liste_destinations : la liste des destinations à ce niveau de granularité
        granularite : le niveau de granularité souhaité (entre 0 et 5)

    Returns :
        la base geopandas au bon avec les bonnes frontières
    """

    # On limite la base aux pays en question
    df_resultat = df[df["NAME_0"].isin(list(liste_destinations.keys()))]
    df_resultat["Visite"] = df_resultat.apply(
        lambda row: (
            1 if row[f"NAME_{granularite}"] in liste_destinations.get(row["NAME_0"], []) else 0
        ),
        axis=1,
    )

    df_resultat["Region"] = df_resultat[f"NAME_{granularite}"]
    df_resultat.rename(columns={"NAME_0": "Pays"}, inplace=True)
    df_resultat["Granu"] = granularite

    # Renvoi
    return df_resultat[["Pays", "Region", "Visite", "geometry", "Granu"]]


def creer_base_double_granularite(
    df_donnee,
    df_obj,
    liste_destinations: dict,
    granularite_obj: int = 1,
    granularite_donnee: int = 1,
):

    # Suppression des pays sans régions assorties
    liste_destinations = {k: v for k, v in liste_destinations.items() if v is not None}

    if granularite_obj > granularite_donnee:
        return creer_base_une_granularite(
            df=df_donnee,
            granularite=granularite_donnee,
            liste_destinations=liste_destinations,
        )

    # On limite la base aux pays en question
    df_resultat = df_donnee[df_donnee["NAME_0"].isin(list(liste_destinations.keys()))]
    df_resultat["Visite"] = df_resultat.apply(
        lambda row: (
            1
            if row[f"NAME_{granularite_donnee}"] in liste_destinations.get(row["NAME_0"], [])
            else 0
        ),
        axis=1,
    )
    df_resultat = df_resultat[df_resultat["Visite"] == 1]
    unique_gdf = set(zip(df_resultat["NAME_0"], df_resultat[f"NAME_{granularite_obj}"]))
    unique_combinaison = pd.DataFrame(list(unique_gdf), columns=["nom1", "nom2"])
    df_dict = unique_combinaison.groupby("nom1")["nom2"].apply(list).to_dict()

    return creer_base_une_granularite(
        df=df_obj,
        granularite=granularite_obj,
        liste_destinations=df_dict,
    )


def remplacer_lieux_constants(liste_dfs: list, df_visite: pd.DataFrame, granularite: int = 1):

    if granularite == 0:
        return df_visite
    else:

        # On isole la base à modifier
        df_visite["granu_unique_pays"] = (
            df_visite.groupby("Pays")["Granu"].transform("nunique") == 1
        )
        df_resultat = df_visite[
            (df_visite["Granu"] != granularite) | (df_visite["granu_unique_pays"] == False)
        ].drop(columns=["granu_unique_pays"])
        df_a_modifier = df_visite[
            (df_visite["Granu"] == granularite) & (df_visite["granu_unique_pays"] == True)
        ].drop(columns=["granu_unique_pays"])

        # Si la granularité en question n'existe pas, on renvoie la table originelle
        if len(df_a_modifier) == 0:
            return df_visite

        # Récupération de la base à la bonne granularité
        df_monde_granu = liste_dfs[granularite].copy().reset_index(drop=True)
        assert not df_monde_granu.duplicated(
            subset=["NAME_0", f"NAME_{granularite}"]
        ).any(), "Le couple (NAME_0, NAME_{granularite}) n'est pas une clé unique."
        df_monde_granu["Pays"] = df_monde_granu["NAME_0"]
        df_monde_granu["Region"] = df_monde_granu[f"NAME_{granularite}"]
        df_monde_granu["region_temp"] = df_monde_granu[f"NAME_{granularite-1}"]
        df_monde_granu = df_monde_granu[["Pays", "Region", "region_temp"]]

        # Ajout de la granularité inférieure à la table
        df_a_modifier = (
            df_a_modifier[["Pays", "Region", "Granu", "geometry", "Visite"]]
            .merge(
                df_monde_granu,
                how="left",
                on=["Pays", "Region"],
            )
            .reset_index()
        )

        # Ajout d'une indicatrice informant de si une région est visitée en entier ou pas du tout
        df_a_modifier["visite_constante"] = (
            df_a_modifier.groupby(["Pays", "region_temp"])["Visite"].transform("nunique") == 1
        )

        # Séparation de la table à modifier et celle à garder identique
        df_a_modifier_oui = df_a_modifier[df_a_modifier["visite_constante"] == True]
        df_a_modifier_non = df_a_modifier[
            # Sélection de la sous-table
            df_a_modifier["visite_constante"]
            == False
        ][
            # Sélection des variables
            [
                "Pays",
                "Region",
                "Granu",
                "geometry",
                "Visite",
            ]
        ]

        # Ajout au résultat de la partie inchangée
        df_resultat = pd.concat([df_resultat, df_a_modifier_non])
        if len(df_a_modifier_oui) == 0:
            return df_resultat

        # Récupération de la base de granularité inférieure
        df_granu_monde_moins = liste_dfs[granularite - 1].copy().reset_index(drop=True)
        df_granu_monde_moins["Pays"] = df_granu_monde_moins["NAME_0"]
        df_granu_monde_moins["region_temp"] = df_granu_monde_moins[f"NAME_{granularite-1}"]

        # Ajout de la géométrie
        df_a_modifier_oui = (
            df_a_modifier_oui[["Pays", "region_temp", "Visite"]]
            # Récupération des régions concernées
            .drop_duplicates()
            # Ajout de la géométrie
            .merge(
                df_granu_monde_moins[["Pays", "region_temp", "geometry"]],
                how="left",
                on=["Pays", "region_temp"],
                # Sélection des colonnes
            )[["Pays", "region_temp", "Visite", "geometry"]]
            # Mise à jour des noms de colonnes
            .rename(columns={"region_temp": "Region"})
            # Ajout de la granularité
            .assign(Granu=granularite - 1)
        )

        # Concatnéation
        df_resultat = pd.concat([df_resultat, df_a_modifier_oui], ignore_index=True)

        # Récursivité
        return remplacer_lieux_constants(
            liste_dfs=liste_dfs, df_visite=df_resultat, granularite=granularite - 1
        )


def gerer_pays_sans_regions(df_0, liste_pays: list):

    df_resultat = df_0[df_0["NAME_0"].isin(liste_pays)]
    df_resultat["Pays"] = df_resultat["NAME_0"] * 1
    df_resultat["Region"] = df_resultat["NAME_0"] * 1
    df_resultat["Granu"] = 0
    df_resultat["Visite"] = 1

    return df_resultat[["Pays", "Region", "Visite", "geometry", "Granu"]]


def cree_base_toutes_granularites(
    liste_dfs: list,
    liste_dicts: list,
    granularite_objectif: int = 1,
):
    r"""
    Cette fonction génère une base de données combinée à partir de différents niveaux de granularité fournis sous forme de dictionnaires.
    Chaque niveau de granularité est spécifié par un dictionnaire et une valeur associée à un niveau de granularité.
    La fonction fusionne les résultats de ces niveaux pour produire un résultat global.

    Paramètres :
    – df_monde (DataFrame) : DataFrame contenant les données mondiales de base. Cela peut être une table de pays, régions, etc.
    – liste_dicts (list) : La liste des dictionnaires de pays visités selon la granularité. La position 0 correspond à la granularité 1.

    Chaque dictionnaire représente un niveau de granularité. Si un dictionnaire est `None`, il est ignoré dans le calcul.

    Retourne :
    – (DataFrame) : Un DataFrame combiné contenant les résultats de toutes les granularités spécifiées.
    """

    granu = [i + 1 for i, val in enumerate(liste_dicts) if isinstance(val, dict)]
    dicos = [val for i, val in enumerate(liste_dicts) if isinstance(val, dict)]

    assert len(granu) == len(dicos), "Problème."

    if granularite_objectif >= 0:

        for i in range(len(granu)):

            # On calcule la dataframe de chaque granularité
            clefs_none_i = [k for k, v in dicos[i].items() if v is None]

            res_i = creer_base_double_granularite(
                df_donnee=liste_dfs[granu[i]],
                granularite_donnee=granu[i],
                liste_destinations=dicos[i],
                granularite_obj=granularite_objectif,
                df_obj=liste_dfs[granularite_objectif],
            )

            if i == 0:
                resultat = res_i
                pays_reste = clefs_none_i
            else:
                resultat = pd.concat([resultat, res_i], ignore_index=True)
                pays_reste = pays_reste + clefs_none_i

        if len(pays_reste) > 0:

            res_sans_region = gerer_pays_sans_regions(df_0=liste_dfs[0], liste_pays=pays_reste)
            resultat = pd.concat([resultat, res_sans_region], ignore_index=True)

    else:

        resultat = cree_base_toutes_granularites(
            liste_dfs=liste_dfs,
            liste_dicts=liste_dicts,
            granularite_objectif=max(granu),
        )

        # On regroupe les régions non visitées
        resultat = remplacer_lieux_constants(
            liste_dfs=liste_dfs, granularite=int(max(resultat["Granu"])), df_visite=resultat
        )

    # Renvoi
    return resultat


def ajouter_indicatrice_visite(gdf_monde, gdf_visite, granularite=1):
    r"""
    Cette fonction ajoute une indicatrice de visite à un GeoDataFrame mondial (`gdf_monde`) en fonction des informations
    sur les pays ou régions visitées dans un autre GeoDataFrame (`gdf_visite`). Les pays non visités sont marqués avec une
    valeur `False` dans la colonne "Visite", tandis que les pays ou régions visités auront cette valeur définie sur `True`.
    Les pays et régions visités sont également concaténés avec ceux non visités pour produire un GeoDataFrame complet.

    Paramètres :
    – gdf_monde (GeoDataFrame) : Un GeoDataFrame contenant les informations mondiales, incluant des colonnes comme `NAME_0` pour les pays
      et `NAME_{granularite}` pour les régions (selon le niveau de granularité).
    – gdf_visite (GeoDataFrame) : Un GeoDataFrame contenant les informations des pays ou régions visités, avec une colonne "Pays" ou
      "Region" correspondante.
    – granularite (int, optionnel) : Le niveau de granularité pour la région (par défaut, 1 représente la région, mais cela peut être
      modifié pour les granularités supérieures). Par exemple, 0 représente les pays, et des valeurs plus grandes pour des
      niveaux plus fins (comme des départements ou des villes).

    Retourne :
    – (GeoDataFrame) : Un GeoDataFrame combiné avec une nouvelle colonne "Visite", indiquant si chaque pays ou région a été visité.
    """

    # On renome la variable NAME_0
    gdf_monde = gdf_monde.rename(columns={f"NAME_0": "Pays"})
    if granularite > 0:
        gdf_monde = gdf_monde.rename(columns={f"NAME_{granularite}": "Region"})
    else:
        gdf_monde["Region"] = gdf_monde["Pays"]

    # On supprime les pays visités
    gdf_monde = gdf_monde[gdf_monde["Pays"].isin(gdf_visite["Pays"]) == False]

    # On met une indicatrice de visite
    gdf_monde["Visite"] = False
    gdf_monde["Granu"] = granularite

    # On supprime les colonnes autres
    gdf_monde = gdf_monde[["Pays", "Region", "Visite", "geometry", "Granu"]]

    # Concaténation des deux bases et renvoi
    return pd.concat([gdf_visite, gdf_monde], ignore_index=True)
