################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Suggestions de nouvelles destinations                             #
################################################################################


import os, copy, numba
import numpy as np
import pandas as pd
from _0_Utilitaires._0_1_Fonctions_utiles import distance_haversine
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QStyle,
    QScrollArea,
)

from _0_Utilitaires._0_1_Fonctions_utiles import vider_layout


# === Fonctions  === #


@numba.njit
def calculer_score_region(
    lats_visite, lons_visite, vals_visite, lats_reste, lons_reste, vals_reste, alpha
):
    n_reste = lats_reste.shape[0]
    n_visite = lats_visite.shape[0]
    scores = np.zeros(n_reste)

    for i in range(n_reste):
        s = 0.0
        for j in range(n_visite):
            geo_dist = distance_haversine(
                lats_reste[i], lons_reste[i], lats_visite[j], lons_visite[j]
            )
            diff_val = np.linalg.norm(vals_reste[i] - vals_visite[j])
            s += diff_val / ((1 + geo_dist) ** alpha)
        scores[i] = s / n_visite if n_visite > 0 else 0.0
    return scores


def calculer_recommandation(df, dict_visite, top_n=10, alpha=1 / 3):
    # Création du set pour filtrer
    visite_set = {(p, r) for p, regions in dict_visite.items() for r in regions}

    # Séparer les colonnes
    mask_visite = np.array(
        [(row[0], row[1]) in visite_set for row in df[["name_0", "name_1"]].values]
    )
    mask_reste = ~mask_visite

    df_visite = df.iloc[mask_visite]
    df_reste = df.iloc[mask_reste]

    # Extraire arrays NumPy
    cols_val = [
        c
        for c in df.columns
        if c
        not in [
            "name_0",
            "name_1",
            "name_2",
            "latitude",
            "longitude",
            "superficie",
            "population",
        ]
    ]
    lats_visite = df_visite["latitude"].to_numpy()
    lons_visite = df_visite["longitude"].to_numpy()
    vals_visite = df_visite[cols_val].to_numpy()

    lats_reste = df_reste["latitude"].to_numpy()
    lons_reste = df_reste["longitude"].to_numpy()
    vals_reste = df_reste[cols_val].to_numpy()

    # Calcul des scores
    scores = calculer_score_region(
        lats_visite, lons_visite, vals_visite, lats_reste, lons_reste, vals_reste, alpha
    )

    df_reste = df_reste.copy()
    df_reste["score_region"] = scores
    return df_reste.sort_values("score_region", ascending=False).head(top_n)


class PaysAVisiter(QWidget):

    def __init__(self, constantes, table_superficie, fct_traduire, parent=None, top_n=10):
        super().__init__(parent)

        self.langue = "français"
        self.constantes = constantes
        self.fonction_traduire = fct_traduire
        self.dict_granu = {"region": {}, "dep": {}}
        self.top_n = top_n
        self.df = None
        self.table_superficie = table_superficie

        layout = QVBoxLayout()
        # Bouton de lancement
        self.bouton_recommandations = QPushButton()
        layout.addWidget(self.bouton_recommandations)
        self.bouton_recommandations.clicked.connect(self.calculer_afficher_recommandation)

        # Scroll area pour les recommandations
        scroll_widget = QWidget()  # widget qui contiendra le layout des recommandations
        self.corps_recommandations = QVBoxLayout()  # layout pour les QLabel
        scroll_widget.setLayout(self.corps_recommandations)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # permet au scroll de s’adapter à la taille
        scroll_area.setWidget(scroll_widget)

        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def calculer_prochaine_destination(self):

        vider_layout(self.corps_recommandations)

        # Affichage temporaire
        label_temp = QLabel()
        label_temp.setPixmap(
            self.style().standardPixmap(getattr(QStyle.StandardPixmap, "SP_BrowserReload"))
        )
        self.corps_recommandations.addWidget(label_temp)

        # Ajout des régions des départements
        dt_temp = self.table_superficie[
            self.table_superficie.apply(
                lambda row: (row["name_0"], row["name_2"])
                in {(p, r) for p, dep in self.dict_granu.get("dep").items() for r in dep},
                axis=1,
            )
        ]
        dict_temp = copy.deepcopy(self.dict_granu.get("region"))
        for pays, groupe in dt_temp.groupby("name_0"):
            regions = groupe["name_1"].tolist()
            if pays in dict_temp:
                # Ajouter les nouvelles régions sans doublons
                dict_temp[pays] = list(set(dict_temp[pays]) | set(regions))
            else:
                # Ajouter le pays s'il n'existait pas encore
                dict_temp[pays] = regions

        # Calcul de la table
        self.df = (
            calculer_recommandation(
                df=self.constantes.df_caracteristiques_pays,
                dict_visite=dict_temp,
                top_n=self.top_n,
            ).reset_index()
            if dict_temp != {}
            else None
        )

    def afficher_recommandation(self):

        # Affichage
        vider_layout(self.corps_recommandations)
        if self.df is None:
            return
        self.corps_recommandations.addWidget(
            QLabel(self.fonction_traduire("titre_recommandations", suffixe=" :"))
        )
        if self.df is not None:
            if len(self.df) > 0:

                for i, ligne in self.df.iterrows():

                    self.corps_recommandations.addWidget(
                        QLabel(
                            # Numéro
                            f"{i + 1}. "
                            # Pays avec emoji
                            f"<b>{ligne['name_0']}</b> {self.constantes.emojis_pays.get(ligne['name_0'], '')}: "
                            # Régions si affichage regroupé
                            f"{ligne['name_1']} : {ligne['score_region']}",
                            wordWrap=True,
                        )
                    )

    def calculer_afficher_recommandation(self):
        self.calculer_prochaine_destination()
        self.afficher_recommandation()

    def set_dicts_granu(self, dict_nv: dict):
        """Permet de mettre à jour les sélections de destinations."""
        self.dict_granu = dict_nv
        # self.df = calculer_recommandation(
        #     df=self.df_caracteristiques, dict_visite=self.dict_granu, top_n=self.top_n
        # )
        if self.dict_granu == {"region": {}, "dep": {}}:
            self.calculer_prochaine_destination()

    def set_langue(self, langue: str):
        self.langue = langue
        self.bouton_recommandations.setText(self.fonction_traduire("bouton_recommandations"))
