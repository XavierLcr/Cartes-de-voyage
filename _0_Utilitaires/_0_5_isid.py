################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.5 – Fonctiontestant si une table est isid                                  #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import pandas as pd


# 1 -- Fonction isid -----------------------------------------------------------


def isid(df: pd.DataFrame, colonnes: str | list, blabla: int):

    vals_uniques = len(df.drop_duplicates(subset=colonnes))
    len_df = len(df)
    doublons_id = df.duplicated(subset=colonnes, keep=False)

    if (blabla == 1 and vals_uniques != len_df) or blabla == 2:
        print(f"Valeurs uniques : {vals_uniques}" f"Lignes : {len_df}")
    elif blabla == 3:
        print(df[doublons_id])

    return doublons_id.sum() == 0
