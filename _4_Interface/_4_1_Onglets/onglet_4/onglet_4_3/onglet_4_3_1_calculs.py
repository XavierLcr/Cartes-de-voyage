################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_3                                #
# Onglet 4.3.1 – Suggestions de nouvelles destinations (partie calculs)        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import numba
import numpy as np
import pandas as pd
from PyQt6.QtCore import pyqtSignal, QObject


from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    distance_haversine,
)
from _0_Utilitaires._0_5_isid import isid
from _0_Utilitaires._0_7_fonctions_voyages import (
    compter_occurences_destinations_une_granu,
    compter_occurrences_regions_depuis_departements,
)

# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de comptage du nombre de visites par région -----------------


def nombre_visites_par_region(dict_voyages: dict, df_superficie: pd.DataFrame):

    # Création des tables départementales et régionales
    df_temp = compter_occurences_destinations_une_granu(
        dict_voyages=dict_voyages, granu=1
    )
    df_dep = compter_occurrences_regions_depuis_departements(
        dict_voyages=dict_voyages, df_superficie=df_superficie
    )

    # Tests de granularité
    assert isid(df=df_temp, colonnes=["pays", "subdivision"], blabla=1)
    assert isid(df=df_dep, colonnes=["pays", "subdivision"], blabla=1)

    # Jointure des tables régionale et départementale
    df_temp = (
        df_temp.merge(
            right=df_dep, on=["pays", "subdivision"], how="outer", suffixes=("_1", "_2")
        )
        .reset_index(drop=False)
        .assign(
            N_1=lambda x: x["N_1"].fillna(0),
            N_2=lambda x: x["N_2"].fillna(0),
            N=lambda x: x["N_1"] + x["N_2"],
        )[
            # Sélection des variables
            ["pays", "subdivision", "N"]
        ]
    )

    # Renvoi
    return df_temp


## 1.2 -- Fonction de calcul des scores entre régions --------------------------


@numba.njit(parallel=True)
def calculer_score_region(
    lats_visite,
    lons_visite,
    vals_visite,
    na_visite,
    superficie_visite,
    N_visite,
    lats_reste,
    lons_reste,
    vals_reste,
    na_reste,
    alpha,
    beta,
):
    n_reste = lats_reste.shape[0]
    n_visite = lats_visite.shape[0]
    scores = np.zeros(n_reste)
    pond_visite = superficie_visite * N_visite**beta * (1 - na_visite)
    pond_visite_total = np.sum(pond_visite) / 100
    for i in numba.prange(n_reste):
        s = 0.0
        na_reste_i = 1 - na_reste[i]
        for j in range(n_visite):
            s += (
                # Un bon score est un score avec une faible norme
                (1 / (1 + np.linalg.norm(vals_reste[i] - vals_visite[j])))
                # Pondération par la distance
                / (
                    (
                        1
                        + distance_haversine(
                            lats_reste[i], lons_reste[i], lats_visite[j], lons_visite[j]
                        )
                    )
                    ** alpha
                )
                # Pondération par la superficie et les NA
                * pond_visite[j]
                * na_reste_i
            )

            # Pondération par la superficie
        scores[i] = (s / pond_visite_total) if n_visite > 0 else 0.0
    return scores


## 1.3 -- Fonction renvoyant les régions recommandées, à l'aide des scores -----


def calculer_recommandations(
    df_caracteristiques: pd.DataFrame,
    df_voyages: pd.DataFrame,
    top_n: int = 10,
    alpha: float = 1 / 3,
    beta: float = 1 / 3,
    par_pays: bool = False,
    n_par_pays: int = 3,
):

    # Tests de granularité
    assert isid(df=df_caracteristiques, colonnes=["name_0", "name_1"], blabla=1)
    assert isid(df=df_voyages, colonnes=["pays", "subdivision"], blabla=1)

    # Ajout du nombre de visites à la table des caractéristiques
    df_temp = (
        df_caracteristiques.merge(
            right=df_voyages,
            left_on=["name_0", "name_1"],
            right_on=["pays", "subdivision"],
            how="left",
        )
        .assign(
            # Complétion des subdivisions sans visite
            N=lambda x: x["N"].fillna(0)
        )
        .drop(columns=["pays", "subdivision"])
    )

    # Séparer les colonnes
    mask_visite = df_temp["N"] > 0
    df_visite = df_temp[mask_visite]
    df_reste = df_temp[~mask_visite]

    # Extraire arrays NumPy
    cols_val = [
        c
        for c in df_temp.columns
        if c
        not in [
            "name_0",
            "name_1",
            "name_2",
            "latitude",
            "longitude",
            "superficie",
            "N",
            "population",
            "nombre_na",
        ]
    ]

    df_reste = (
        df_reste.assign(
            # Calcul des scores
            score_region=calculer_score_region(
                lats_visite=np.radians(df_visite["latitude"].to_numpy()),
                lons_visite=np.radians(df_visite["longitude"].to_numpy()),
                vals_visite=df_visite[cols_val].to_numpy(),
                na_visite=df_visite["nombre_na"].to_numpy(),
                superficie_visite=df_visite["superficie"].to_numpy(),
                N_visite=df_visite["N"].to_numpy(),
                lats_reste=np.radians(df_reste["latitude"].to_numpy()),
                lons_reste=np.radians(df_reste["longitude"].to_numpy()),
                vals_reste=df_reste[cols_val].to_numpy(),
                na_reste=df_reste["nombre_na"].to_numpy(),
                alpha=alpha,
                beta=beta,
            )
        )
        # Tri
        .sort_values("score_region", ascending=False)
    )

    # Limitation aux top pays (si souhaité)
    if par_pays:
        df_reste = (
            df_reste.groupby("name_0")
            .apply(lambda x: x.nlargest(n_par_pays, columns="score_region"))
            .reset_index(drop=False)
        )

    df_reste = (
        df_reste
        # Sélection du top des recommandations
        .nlargest(top_n, columns="score_region")
        # Sélection des colonnes
        .reset_index(drop=True)[
            ["name_0", "name_1", "latitude", "longitude", "superficie", "score_region"]
        ]
    )

    return df_reste


# 2 -- Classe de calcul du tableau de recommandations --------------------------


class WorkerRecommandation(QObject):
    finished = pyqtSignal(object)  # Signal pour retourner le résultat

    def __init__(
        self,
        top_n: int,
        alpha: float,
        beta: float,
        df_caracteristiques: pd.DataFrame,
        df_superficie: pd.DataFrame,
        dict_voyages: dict,
        par_pays: bool,
        n_par_pays: int,
    ):
        super().__init__()
        self.df_caracteristiques = df_caracteristiques
        self.df_superficie = df_superficie
        self.dict_voyages = dict_voyages

        self.top_n = top_n
        self.alpha = alpha
        self.beta = beta
        self.par_pays = par_pays
        self.n_par_pays = n_par_pays

    def creer_df_recommandations(self):

        # Table de comptage des visites
        df_temp = nombre_visites_par_region(
            dict_voyages=self.dict_voyages, df_superficie=self.df_superficie
        )

        # Table des recommandations
        df_temp = calculer_recommandations(
            df_caracteristiques=self.df_caracteristiques,
            df_voyages=df_temp,
            top_n=self.top_n,
            alpha=self.alpha,
            beta=self.beta,
            par_pays=self.par_pays,
            n_par_pays=self.n_par_pays,
        )

        # Renvoi
        return df_temp

    def calculer(self):
        """Méthode exécutée dans le thread."""
        self.finished.emit(
            self.creer_df_recommandations() if self.dict_voyages else None
        )  # Émet le résultat
