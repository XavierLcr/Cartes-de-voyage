################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Suggestions de nouvelles destinations                             #
################################################################################


import os
import numpy as np
import pandas as pd
import constantes
from _0_Utilitaires._0_1_Fonctions_utiles import distance_haversine


# === Fonctions  === #


def calculer_distance_deux_lieux(ligne1: pd.Series, ligne2: pd.Series, alpha=1 / 3):

    index = [
        i
        for i in ligne1.index
        if i not in ["name_0", "name_1", "latitude", "longitude", "superficie", "population"]
    ]

    return np.linalg.norm(ligne1[index] - ligne2[index]) / (
        (
            1
            + distance_haversine(
                lat1=ligne1["latitude"],
                lon1=ligne1["longitude"],
                lat2=ligne2["latitude"],
                lon2=ligne2["longitude"],
            )
        )
        ** alpha
    )


def calculer_recommandation(df: pd.DataFrame, dict_visite: dict, top_n=10):

    dict_visite = {(p, r) for p, regions in dict_visite.items() for r in regions}

    df_visite = df[df.apply(lambda row: (row["name_0"], row["name_1"]) in dict_visite, axis=1)]
    df_reste = df[~df.apply(lambda row: (row["name_0"], row["name_1"]) in dict_visite, axis=1)]

    df_reste["score_region"] = df_reste.apply(
        lambda row1: df_visite.apply(
            lambda row2: calculer_distance_deux_lieux(row1, row2), axis=1
        ).mean(),
        axis=1,
    )

    return df_reste.sort_values("score_region", ascending=False).head(top_n)
