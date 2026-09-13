################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_4                                #
# Onglet 4.4.2 – Fonctions de traitement des données                           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, textwrap
import pandas as pd

from _0_Utilitaires._0_07_fonctions_voyages import (
    compter_occurences_destinations_une_granu,
)

# 1 -- Fonctions de création du classement des pays ----------------------------


# 1 -- Fonction de comptage par pays -------------------------------------------


def compter_voyages_par_pays(
    dictionnaire_voyages: dict, traductions: dict, langue: str
):

    return (
        compter_occurences_destinations_une_granu(
            dict_voyages=dictionnaire_voyages, granu=0
        )
        .assign(
            pays_traduction=lambda x: x["pays"].apply(
                lambda y: traductions.get(y, {}).get(langue, y)
            )
        )
        .sort_values(
            by=["N", "pays_traduction"], ascending=(False, True), inplace=False
        )
        .reset_index(drop=True, inplace=False)
    )


# 2 -- Fonction de limite du nombre de pays ------------------------------------


def limiter_nombre_pays(df: pd.DataFrame, n: int, type: bool, agreger: bool):

    # Récupération des paramètres
    df_temp = df.copy()
    n = max(n, 2)

    # Conservation du top pays
    if type and len(df_temp) > n:
        df_temp = df_temp[df_temp["N"] >= df_temp.iloc[n - 1]["N"]]

    else:
        df_temp = df_temp.head(n)

    if agreger and len(df_temp) > n + 1:

        min_n = df_temp["N"].min()

        df_temp = (
            pd.concat(
                [
                    # Partie agrégée de la table
                    df_temp[df_temp["N"] == min_n]
                    .groupby("N", as_index=False)
                    .agg({"pays": ", ".join, "pays_traduction": ", ".join}),
                    # Partie non agrégée
                    df_temp[df_temp["N"] > min_n],
                ],
                ignore_index=True,
            )
            .sort_values(by=["N"], ascending=False)
            .assign(
                pays_traduction=lambda x: x["pays_traduction"].apply(
                    lambda y: textwrap.fill(y, width=20, max_lines=3, placeholder="...")
                )
            )
        )

    return df_temp


# 3 -- Résolution du chemin d'un drapeau ---------------------------------------


def resoudre_chemin_drapeau(
    dossier: str,
    nom_pays: str,
) -> str:

    chemin_drapeau = os.path.join(dossier, f"{nom_pays}.png")

    if os.path.exists(chemin_drapeau):
        return chemin_drapeau

    return os.path.join(dossier, "United Nations.png")
