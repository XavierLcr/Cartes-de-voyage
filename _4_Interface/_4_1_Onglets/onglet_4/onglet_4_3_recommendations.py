################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Suggestions de nouvelles destinations                             #
################################################################################


import os
import numpy as np
import pandas as pd
from _0_Utilitaires._0_1_Fonctions_utiles import distance_haversine
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QDialogButtonBox,
    QStyle,
)

from _0_Utilitaires._0_1_Fonctions_utiles import vider_layout


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


class PaysAVisiter(QDialog):

    def __init__(self, df_caract, constantes, fct_traduire, parent=None, top_n=10):
        super().__init__(parent)

        self.langue = "français"
        self.constantes = constantes
        self.fonction_traduire = fct_traduire
        self.dict_granu = {"region": {}, "dep": {}}
        self.top_n = top_n
        self.df_caracteristiques = df_caract
        self.df = None

        layout = QVBoxLayout()

        # Bouton de lancement
        self.bouton_recommandations = QPushButton()
        layout.addWidget(self.bouton_recommandations)

        # Widgets post classement
        self.titre_recommandations = QLabel()
        self.titre_recommandations.setVisible(False)
        layout.addWidget(self.titre_recommandations)

        self.corps_recommandations = QVBoxLayout()
        layout.addLayout(self.corps_recommandations)

    def calculer_prochaine_destination(self):

        # Mise à jour visuelle
        self.bouton_recommandations.setVisible(False)
        self.titre_recommandations.setVisible(True)

        vider_layout(self.corps_recommandations)
        label_temp = QLabel()
        label_temp.setPixmap(
            self.style().standardPixmap(
                enum_value=getattr(QStyle.StandardPixmap, "SP_BrowserReload")
            )
        )
        self.corps_recommandations.addWidget(label_temp)


        # Calcul de la table
        self.df = calculer_recommandation(
            df=self.df_caracteristiques, dict_visite=self.dict_granu, top_n=self.top_n
        )

        # Affichage
        vider_layout(self.corps_recommandations)
        if self.df is not None:
            if len(self.df) > 0:

                for i, ligne in self.df.iterrows():

                    self.corps_recommandations.addWidget(
                    QLabel(
                        # Numéro
                        f"{i + 1}. "
                        # Pays avec emoji
                        f"<b>{ligne["name_0"]}</b> {self.constantes.emojis_pays.get(ligne["name_0"], '')}: "
                        # Régions si affichage regroupé
                        f"{ligne["name_1"]}",
                        wordWrap=True,
                    )
                )
        

    # def set_dicts_granu(self, dict_nv: dict):
    #     """Permet de mettre à jour les sélections de destinations."""
    #     self.dicts_granu = dict_nv
    #     self.df = calculer_recommandation(
    #         df=self.df_caracteristiques, dict_visite=self.dict_granu, top_n=self.top_n
    #     )

    def set_langue(self, langue: str):
        self.langue = langue

        self.bouton_recommandations.setText(self.fonction_traduire("bouton_recommandations"))
        self.titre_recommandations.setText(
            self.fonction_traduire("titre_recommandations"), suffixe=" :"
        )
