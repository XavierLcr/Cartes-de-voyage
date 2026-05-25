################################################################################
# Projet de cartes de voyage                                                   #
# _3_Calculs/                                                                  #
# 3.1 – Fichier de création de la base de données                              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import pandas as pd
from _0_Utilitaires._0_5_isid import isid

# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Création de la table de visite pour un pays à une granularité donnée -


def creer_base_une_granularite(
    gdf,
    liste_destinations: dict,
    granularite: int = 1,
):
    """Crée la base pour une liste de pays à un niveau de granularité donnée.

    Args:
        gdf : la base geopandas du monde.
        liste_destinations : le dictionnaire des destinations à ce niveau de granularité.
        granularite : le niveau de granularité souhaité (entre 0 et 5).

    Returns :
        La base geopandas au bon avec les bonnes frontières
    """

    return (
        # Filtre sur les pays visités
        gdf.loc[gdf["name_0"].isin(liste_destinations.keys())]
        # Création de l'indicatrice des lieux visités
        .assign(
            # Indicatrice de visite
            visite=lambda x: x.apply(
                lambda row: row[f"name_{granularite}"]
                in liste_destinations.get(row["name_0"], []),
                axis=1,
            ),
            # Ajout de la granularité
            Pays=lambda x: x["name_0"],
            subdivision=lambda x: x[f"name_{granularite}"],
            Granu=granularite,
        )
        # Sélection des colonnes
        [["Pays", "subdivision", "visite", "geometry", "Granu"]]
    )


## 1.2 -- Création de la table de visite pour un pays --------------------------


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
            gdf=df_donnee,
            granularite=granularite_donnee,
            liste_destinations=liste_destinations,
        )

    # Sélection des lieux visités
    resultat = df_donnee.loc[
        df_donnee.apply(
            lambda row: row["name_0"] in liste_destinations
            and row[f"name_{granularite_donnee}"] in liste_destinations[row["name_0"]],
            axis=1,
        )
    ]

    return creer_base_une_granularite(
        gdf=df_obj,
        granularite=granularite_obj,
        liste_destinations=pd.DataFrame(
            # Création des paires Pays/Région visités
            list(set(zip(resultat["name_0"], resultat[f"name_{granularite_obj}"]))),
            columns=["nom1", "nom2"],
        )
        # Mise sous la forme d'un dictionnaire
        .groupby("nom1")["nom2"].apply(list).to_dict(),
    )


## 1.3 -- Création du mode 'Amusant' -------------------------------------------


### Fonction unissant les territoires pour un niveau de granularité ------------


def agreger_lieux_constants_une_granu(
    liste_dfs: list, df_visite: pd.DataFrame, granularite: int = 1
):

    if granularite == 0:
        return df_visite[df_visite["Granu"] == granularite]

    # Tests de cohérence
    assert (
        len(liste_dfs) > granularite
    ), "Tables non disponibles à la granularité souhaitée"
    assert granularite >= 0, "granularite doit être positive"

    # Récupération des tables
    df_visite = df_visite[df_visite["Granu"] == granularite][
        ["Pays", "subdivision", "visite"]
    ].copy()
    df_granu = liste_dfs[granularite].filter(regex="^name_").copy()
    cols_df_granu = [col for col in df_granu.columns if col.startswith("name_")]
    df_granu = df_granu[df_granu["name_0"].isin(set(df_visite["Pays"]))].assign(
        Pays=lambda x: x["name_0"], subdivision=lambda x: x[max(cols_df_granu)]
    )

    # Tests de granularité
    assert isid(df=df_visite, colonnes=["Pays", "subdivision"], blabla=0)
    assert isid(df=df_granu, colonnes=["Pays", "subdivision"], blabla=0)

    # Jointure
    df_visite = df_visite.merge(right=df_granu, how="left", on=["Pays", "subdivision"])

    # Tentatives d'agrégation
    for granu in range(granularite):

        # Indicatrice d'agrégation
        df_visite["joindre"] = (
            df_visite.groupby(cols_df_granu[: (granu + 1)])["visite"].transform(
                "nunique"
            )
            == 1
        )

        df_agregee = df_visite[df_visite["joindre"] == True][
            cols_df_granu[: (granu + 1)] + ["visite"]
        ].drop_duplicates()

        # Tests de granularité
        assert isid(df=df_agregee, colonnes=cols_df_granu[: (granu + 1)], blabla=0)
        assert isid(
            df=liste_dfs[granu], colonnes=cols_df_granu[: (granu + 1)], blabla=0
        )

        # Jointure
        df_agregee = df_agregee.merge(
            right=liste_dfs[granu], how="left", on=cols_df_granu[: (granu + 1)]
        ).assign(
            Pays=lambda x: x["name_0"],
            subdivision=lambda x: x[cols_df_granu[granu]],
            Granu=granu,
        )[
            ["Pays", "subdivision", "visite", "geometry", "Granu"]
        ]

        # Concaténation
        if granu == 0:
            df_resultat = df_agregee.copy()
        else:
            df_resultat = pd.concat([df_resultat, df_agregee], ignore_index=True)

        # Parties non agrégées à tester à une granularité plus fine
        df_visite = df_visite[df_visite["joindre"] == False].drop(
            columns=["joindre"], inplace=False
        )

    # Normalisation de df_visite
    if len(df_visite) > 0:
        df_visite = df_visite.assign(Granu=granularite)[
            ["Pays", "subdivision", "visite", "Granu"]
        ]

        # Tests de granularité
        assert isid(df=df_visite, colonnes=["Pays", "subdivision"], blabla=0)
        assert isid(
            df=liste_dfs[granularite],
            colonnes=["name_0", f"name_{granularite}"],
            blabla=0,
        )

        # Jointure
        df_visite = df_visite.merge(
            right=liste_dfs[granularite].assign(
                Pays=lambda x: x["name_0"],
                subdivision=lambda x: x[f"name_{granularite}"],
            )[["Pays", "subdivision", "geometry"]],
        )

        # Concaténation
        df_resultat = pd.concat([df_resultat, df_visite], ignore_index=True)

    # Renvoi
    return df_resultat


### Fonction générale d'union des territoires ----------------------------------


def agreger_lieux_constants(liste_dfs: list, df_visite: pd.DataFrame):

    granu_max = df_visite["Granu"].max()

    return pd.concat(
        [
            agreger_lieux_constants_une_granu(
                liste_dfs=liste_dfs, df_visite=df_visite, granularite=g
            )
            for g in range(granu_max + 1)
        ]
    ).reset_index(drop=True, inplace=False)


## 1.4 -- Création de la table complète des pays visités -----------------------


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
    # Test de cohérence
    assert len(granu) == len(dicos), "Problème."

    if granularite_objectif < 0:
        granularite_objectif = int(max(granu))

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
            else (
                pd.concat([resultat, res_i], ignore_index=True),
                pays_reste + clefs_none_i,
            )
        )

    if len(pays_reste) > 0:

        resultat = pd.concat(
            [
                # Table des pays détaillés
                resultat,
                # Table des pays non détaillés
                liste_dfs[0][liste_dfs[0]["name_0"].isin(pays_reste)].assign(
                    Pays=lambda x: x["name_0"] * 1,
                    Region=lambda x: x["name_0"] * 1,
                    Granu=0,
                    Visite=1,
                )[["Pays", "subdivision", "visite", "geometry", "Granu"]],
            ],
            ignore_index=True,
        )

    # Renvoi
    return resultat


## 1.5 -- Complétion de la carte du monde avec les pays non visités ------------


def ajouter_indicatrice_visite(gdf_monde, gdf_visite, granularite=1):
    r"""
    Cette fonction ajoute une indicatrice de visite à un GeoDataFrame mondial (`gdf_monde`) en fonction des informations
    sur les pays ou régions visitées dans un autre GeoDataFrame (`gdf_visite`). Les pays non visités sont marqués avec une
    valeur `False` dans la colonne "visite", tandis que les pays ou régions visités auront cette valeur définie sur `True`.
    Les pays et régions visités sont également concaténés avec ceux non visités pour produire un GeoDataFrame complet.

    Paramètres :
    – gdf_monde (GeoDataFrame) : Un GeoDataFrame contenant les informations mondiales, incluant des colonnes comme `name_0` pour les pays
      et `name_{granularite}` pour les régions (selon le niveau de granularité).
    – gdf_visite (GeoDataFrame) : Un GeoDataFrame contenant les informations des pays ou régions visités, avec une colonne "Pays" ou
      "subdivision" correspondante.
    – granularite (int, optionnel) : Le niveau de granularité pour la région (par défaut, 1 représente la région, mais cela peut être
      modifié pour les granularités supérieures). Par exemple, 0 représente les pays, et des valeurs plus grandes pour des
      niveaux plus fins (comme des départements ou des villes).

    Retourne :
    – (GeoDataFrame) : Un GeoDataFrame combiné avec une nouvelle colonne "visite", indiquant si chaque pays ou région a été visité.
    """

    # Concaténation des deux tables et renvoi
    return pd.concat(
        [
            # Table des pays visités
            gdf_visite,
            # Table des pays non visités
            (
                # Suppression des pays visités
                gdf_monde[gdf_monde["name_0"].isin(gdf_visite["Pays"]) == False].assign(
                    # Création de la région
                    subdivision=lambda x: x[f"name_{granularite}"]
                )
                # Renommage
                .rename(columns={"name_0": "Pays"})
                # Ajout de la granularité
                .assign(Granu=granularite)
                # Ajout de l'indicatrice de visite
                .assign(visite=False)
                # Sélection des colonnes
                [["Pays", "subdivision", "visite", "geometry", "Granu"]]
            ),
        ],
        ignore_index=True,
    )


## 1.6 -- Création de la table complète ----------------------------------------


def cree_gdf_depuis_dicts(
    liste_dfs: list,
    liste_dicts: list,
    granularite_visite=1,
    granularite_reste=1,
):
    r"""
    Cette fonction crée la table complète d'un individu aux granularités souhaitées.

    Paramètres :
    – liste_dfs : liste des GeoDataFrames.
    – liste_dicts: liste des lieux visités pour chaque niveau de granularité.
    – granularite_visite (int, optionnel) : Le niveau de granularité des pays visités.
    – granularite_reste (int, optionnel) : Le niveau de granularité des pays non visités.
    """

    # Création de la table à la granularité souhaité
    df_temp = cree_base_toutes_granularites(
        liste_dfs=liste_dfs,
        liste_dicts=liste_dicts,
        granularite_objectif=granularite_visite,
    )

    # Agréagtion des lieux constantes (si souhaité)
    if granularite_visite == -1:
        df_temp = agreger_lieux_constants(
            liste_dfs=liste_dfs,
            df_visite=df_temp,
        )

    # Ajout du reste du monde
    df_temp = ajouter_indicatrice_visite(
        gdf_monde=liste_dfs[granularite_reste],
        gdf_visite=df_temp,
        granularite=granularite_reste,
    )

    # Renvoi
    return df_temp
