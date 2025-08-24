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

    return (
        # Filtre sur les pays visités
        df.loc[df["NAME_0"].isin(liste_destinations.keys())]
        # Création de l'indicatrice des lieux visités
        .assign(
            Visite=lambda x: x.apply(
                lambda row: row[f"NAME_{granularite}"] in liste_destinations.get(row["NAME_0"], []),
                axis=1,
            ),
            # Récupération de la région
            Region=lambda x: x[f"NAME_{granularite}"],
            # Ajout de la granularité
            Granu=granularite,
        )
        # Renommage
        .rename(columns={"NAME_0": "Pays"})
        # Sélection des colonnes
        .loc[:, ["Pays", "Region", "Visite", "geometry", "Granu"]]
    )


def creer_base_double_granularite(
    df_donnee,
    df_obj,
    liste_destinations: dict,
    granularite_obj: int = 1,
    granularite_donnee: int = 1,
):

    # Suppression des pays sans régions assorties
    liste_destinations = {k: v for k, v in liste_destinations.items() if v is not None}

    # Renvoi de la granularité maximale possible si la souhaitée n'est pas disponible
    if granularite_obj >= granularite_donnee:
        return creer_base_une_granularite(
            df=df_donnee,
            granularite=granularite_donnee,
            liste_destinations=liste_destinations,
        )

    # Sélection des lieux visités
    resultat = df_donnee.loc[
        df_donnee.apply(
            lambda row: row["NAME_0"] in liste_destinations
            and row[f"NAME_{granularite_donnee}"] in liste_destinations[row["NAME_0"]],
            axis=1,
        )
    ]

    return creer_base_une_granularite(
        df=df_obj,
        granularite=granularite_obj,
        liste_destinations=pd.DataFrame(
            # Création des paires Pays/Région visités
            list(set(zip(resultat["NAME_0"], resultat[f"NAME_{granularite_obj}"]))),
            columns=["nom1", "nom2"],
        )
        # Mise sous la forme d'un dictionnaire
        .groupby("nom1")["nom2"].apply(list).to_dict(),
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
        df_monde_granu = (
            liste_dfs[granularite]
            .copy()
            .reset_index(drop=True)
            .assign(
                Pays=lambda x: x["NAME_0"],
                Region=lambda x: x[f"NAME_{granularite}"],
                region_temp=lambda x: x[f"NAME_{granularite-1}"],
            )[["Pays", "Region", "region_temp"]]
        )
        assert not df_monde_granu.duplicated(
            subset=["Pays", "Region"]
        ).any(), f"Le couple (Pays, Region) n'est pas une clé unique pour le passage de la granularité {granularite} à la granularité {granularite-1}."

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

        # Séparation de la table à modifier et celle non
        ## Concaténation de la table de résultat avec celle des lieux partiellement visités
        df_resultat = pd.concat(
            [
                # Table à ne pas modifier
                df_resultat,
                # Table pour laquelle aucune modification n'est nécessaire
                df_a_modifier[
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
                ],
            ]
        )

        # Restriction de la table nécessitant des modifications
        df_a_modifier = df_a_modifier[df_a_modifier["visite_constante"] == True]
        if len(df_a_modifier) == 0:
            return df_resultat

        # Ajout de la géométrie de la granularité inférieure
        df_a_modifier = (
            df_a_modifier[["Pays", "region_temp", "Visite"]]
            # Récupération des régions concernées
            .drop_duplicates()
            # Ajout de la géométrie
            .merge(
                # Table de granularité inférieure
                liste_dfs[granularite - 1].copy().reset_index(drop=True)
                # Renommage
                .assign(
                    Pays=lambda x: x["NAME_0"],
                    region_temp=lambda x: x[f"NAME_{granularite-1}"],
                    # Sélection des variables
                )[["Pays", "region_temp", "geometry"]],
                how="left",
                on=["Pays", "region_temp"],
                # Sélection des colonnes
            )[["Pays", "region_temp", "Visite", "geometry"]]
            # Mise à jour des noms de colonnes
            .rename(columns={"region_temp": "Region"})
            # Ajout de la granularité
            .assign(Granu=granularite - 1)
        )

        # Concaténation puis récursivité
        return remplacer_lieux_constants(
            liste_dfs=liste_dfs,
            df_visite=pd.concat([df_resultat, df_a_modifier], ignore_index=True),
            granularite=granularite - 1,
        )


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

            # Pays non détaillés
            clefs_none_i = [k for k, v in dicos[i].items() if v is None]

            # Calcul du dataframe de chaque granularité
            res_i = creer_base_double_granularite(
                df_donnee=liste_dfs[granu[i]],
                granularite_donnee=granu[i],
                liste_destinations=dicos[i],
                granularite_obj=granularite_objectif,
                df_obj=liste_dfs[granularite_objectif],
            )

            resultat, pays_reste = (
                (res_i, clefs_none_i)
                if i == 0
                else (pd.concat([resultat, res_i], ignore_index=True), pays_reste + clefs_none_i)
            )

        if len(pays_reste) > 0:

            resultat = pd.concat(
                [
                    # Table des pays détaillés
                    resultat,
                    # Table des pays non détaillés
                    liste_dfs[0][liste_dfs[0]["NAME_0"].isin(pays_reste)].assign(
                        Pays=lambda x: x["NAME_0"] * 1,
                        Region=lambda x: x["NAME_0"] * 1,
                        Granu=0,
                        Visite=1,
                    )[["Pays", "Region", "Visite", "geometry", "Granu"]],
                ],
                ignore_index=True,
            )

        # Renvoi
        return resultat

    else:

        # Regroupement des régions non visitées
        return remplacer_lieux_constants(
            liste_dfs=liste_dfs,
            granularite=int(max(granu)),
            df_visite=cree_base_toutes_granularites(
                liste_dfs=liste_dfs,
                liste_dicts=liste_dicts,
                granularite_objectif=int(max(granu)),
            ),
        )


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

    # Concaténation des deux tables et renvoi
    return pd.concat(
        [
            # Table des pays visités
            gdf_visite,
            # Table des pays non visités
            (
                # Suppression des pays visités
                gdf_monde[gdf_monde["NAME_0"].isin(gdf_visite["Pays"]) == False].assign(
                    # Création de la région
                    Region=lambda x: x[f"NAME_{granularite}"]
                )
                # Renommage
                .rename(columns={"NAME_0": "Pays"})
                # Ajout de la granularité
                .assign(Granu=granularite)
                # Ajout de l'indicatrice de visite
                .assign(Visite=False)
                # Sélection des colonnes
                [["Pays", "Region", "Visite", "geometry", "Granu"]]
            ),
        ],
        ignore_index=True,
    )
