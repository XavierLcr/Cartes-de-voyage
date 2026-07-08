################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4.2 – Partie classement des pays visités                              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    creer_QLabel_centre,
    creer_ligne_horizontale,
    vider_layout,
    creer_scroll,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_2.onglet_4_2_1_podium import Podium

# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de création du classement des pays les plus visités ---------


def creer_classement_pays(
    gdf_visite,
    table_superficie,
    pays_traductions: dict,
    langue: str,
    granularite: int = 1,
    top_n: int | None = None,
    ndigits: int | None = None,
):

    df_temp = (
        # Ajout des superficies
        gdf_visite.copy()
        .merge(
            table_superficie,
            how="left",
            left_on=["pays", "subdivision"],
            right_on=["name_0", f"name_{granularite}"],
        )
        # Somme par pays des superficies visitées
        .groupby("pays")[["pct_superficie_pays", "superficie"]]
        .sum()
        .reset_index()
        # Tri des valeurs par ordre décroissant
        .sort_values(by=["pct_superficie_pays", "superficie"], ascending=[False, False])
        # Arrondi de la valeur
        .assign(
            pct_superficie_pays=lambda x: x["pct_superficie_pays"].apply(
                lambda x: round(100 * (x or 0), ndigits=ndigits)
            )
        )
        .assign(
            # Mise en forme du pourcentage
            pct_superficie_pays_label=lambda x: x["pct_superficie_pays"].apply(
                lambda x: f"{x} %".replace(".", ",")
            ),
            # Récupération du nom du pays dans la langue utilisée
            nom_pays=lambda x: x["pays"]
            .map({k: v.get(langue, k) for k, v in pays_traductions.items()})
            .fillna(x["pays"]),
        )
        .reset_index()
    )

    # Ajout du classement
    df_temp["classement"] = df_temp.index.to_series().apply(
        lambda i: ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
    )

    # Sélection du top pays si souhaité
    if top_n is not None:
        df_temp = df_temp.head(top_n)

    # Pays avec un pourcentage arrondi non nul ou dans les trois premières lignes
    df_temp = df_temp[(df_temp["pct_superficie_pays"] > 0) | (df_temp.index < 3)]

    return df_temp


## 1.2 -- Fonction d'agrégation des lignes à 100 % -----------------------------


def agreger_top_pays(df: pd.DataFrame, top_n_lignes_min: int | None):

    df_temp = df.copy()

    top_n_lignes = (df_temp["pct_superficie_pays"] == 100).sum()

    # Agrégation des pays à 100 % (si souhaité)
    if top_n_lignes_min is not None and top_n_lignes >= top_n_lignes_min:

        df_temp = pd.concat(
            [  # Agrégation des premières lignes
                pd.DataFrame(
                    {
                        "classement": [df_temp["classement"].iloc[0]],
                        "nom_pays": [", ".join(df_temp.head(top_n_lignes)["nom_pays"])],
                        "pct_superficie_pays_label": [
                            df_temp["pct_superficie_pays_label"].iloc[0]
                        ],
                        "pct_superficie_pays": [df_temp["pct_superficie_pays"].iloc[0]],
                    }
                ),
                # reste de la table
                df_temp.iloc[top_n_lignes:][
                    [
                        "classement",
                        "nom_pays",
                        "pct_superficie_pays",
                        "pct_superficie_pays_label",
                    ]
                ],
            ],
            axis=0,
        ).assign(agreg=True)

    else:

        df_temp["agreg"] = False

    # Mise en forme additionnelle
    df_temp["classement"] = "<b>" + df_temp["classement"] + "</b>"

    # Renvoi
    return df_temp


## 1.3 -- Fonction de création d'un label --------------------------------------


def creer_label_pays(ligne):

    return creer_QLabel_centre(
        text=(
            f"{ligne['classement']}"
            "<br>"
            f"{ligne['nom_pays']}"
            "<br>"
            f"{ligne['pct_superficie_pays_label']}"
        ),
        wordWrap=True,
        alignement=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
    )


# 2 -- Classe affichant les pays les plus visités ------------------------------


class ClassementPays(QWidget):
    def __init__(
        self,
        constantes,
        fct_traduction,
        table_superficie,
        parent=None,
        min_changement_mise_en_forme: int = 4,
        adapter_mise_en_forme: bool = True,
    ):
        super().__init__(parent)

        # === Variables globales === #
        self.pays_traductions = constantes.pays_differentes_langues
        self.table_superficie = table_superficie
        self.top_n = constantes.parametres_application["top_n_pays"]
        self.ndigits = constantes.parametres_application["pct_ndigits"]
        self.ndigits = None if self.ndigits == 0 else self.ndigits
        self.fonction_traduction = fct_traduction
        self.dicts_granu = {"region": {}, "dep": {}}
        self.langue_utilisee = "français"
        self.min_changement_mise_en_forme = min_changement_mise_en_forme
        self.adapter_mise_en_forme = adapter_mise_en_forme
        self.n_colonnes = 3

        # === Layout principal === #
        self.layout = QHBoxLayout(self)

    def creer_layout_classement(self, df: pd.DataFrame, vbox: QVBoxLayout):
        """
        Affiche le classement des pays dans un QGridLayout (vbox).
        - df : DataFrame contenant 'Pays' et 'pct_superficie_pays'
        - vbox : QVBoxLayout où ajouter les QLabel
        """

        if df is None or df.empty:
            return

        df_temp = df.copy()

        # === Ajout de la première ligne === #

        layout_temp = QHBoxLayout()
        n_lignes = 3 if df_temp["agreg"].sum() == 0 else 1

        podium_temp = Podium()
        podium_temp.set_donnees(df_temp.head(n=n_lignes).to_dict(orient="records"))
        layout_temp.addWidget(podium_temp)

        # Ajout au layout
        vbox.addLayout(layout_temp)

        # Suppression de la première ligne
        df_temp = df_temp.iloc[n_lignes:]

        # === Ajout des autres lignes === #

        layout_temp = QGridLayout()
        n_col_temp = self.n_colonnes
        layout_necessaire = False

        # Complétion du reste des cases
        for i, (_, ligne) in enumerate(df_temp.iterrows()):

            layout_necessaire = True

            # Ajout du label
            layout_temp.addWidget(
                creer_label_pays(ligne=ligne),
                i // n_col_temp,
                i % n_col_temp,
            )

            # Largueur de la colonne
            layout_temp.setColumnStretch(i % n_col_temp, 1)

        # Ajout au layout
        if layout_necessaire:
            vbox.addLayout(layout_temp)

    def lancer_classement_pays(self, granularite: int):

        # Complétion des régions à partir des départements
        dict_regions = self.dicts_granu.get("region") or {}
        dict_departements = self.dicts_granu.get("dep") or {}

        for pays, deps in dict_departements.items():
            mask = (self.table_superficie["name_0"] == pays) & (
                self.table_superficie["name_2"].isin(deps)
            )
            dict_regions[pays] = (
                self.table_superficie.loc[mask, "name_1"].unique().tolist()
            )

        layout_final = QVBoxLayout()

        # Création du layout
        layout_final.addWidget(
            creer_QLabel_centre(
                text=self.fonction_traduction(
                    f"classement_selon_{'regions' if granularite==1 else 'departements'}",
                    prefixe="<b>",
                    suffixe="</b>",
                )
            )
        )

        layout_final.addWidget(creer_ligne_horizontale())
        layout_final.addWidget(creer_QLabel_centre())

        try:

            # Création de la table des lieux visités
            df_temp = pd.DataFrame(
                [
                    (k, v)
                    for k, lst in (
                        dict_regions.items()
                        if granularite == 1
                        else dict_departements.items()
                    )
                    for v in (lst or [])
                ],
                columns=["pays", "subdivision"],
            )

            # Classement des pays
            df_temp = creer_classement_pays(
                # Transformation du dictionnaire en Data.frame
                gdf_visite=df_temp,
                table_superficie=self.table_superficie,
                pays_traductions=self.pays_traductions,
                langue=self.langue_utilisee,
                granularite=granularite,
                top_n=self.top_n,
                ndigits=self.ndigits,
            )
            # Agrégation du top pays (si souhaité et nécessaire)
            df_temp = agreger_top_pays(
                df=df_temp,
                top_n_lignes_min=(
                    None
                    if not self.adapter_mise_en_forme
                    else self.min_changement_mise_en_forme
                ),
            )

            self.creer_layout_classement(
                df=df_temp,
                vbox=layout_final,
            )

        except Exception as e:
            pass

        layout_final.addStretch()

        # Mise en scroll et renvoi
        return creer_scroll(layout=layout_final)

    def lancer_classement_par_region_departement(self):

        # Nettoyage du layout
        vider_layout(self.layout)

        # Ajout des classements
        for i in range(1, 3):

            self.layout.addWidget(
                self.lancer_classement_pays(
                    granularite=i,
                )
            )

    def set_dicts_granu(self, dict_nv):
        self.dicts_granu = dict_nv
        self.lancer_classement_par_region_departement()

    def set_langue(self, nouvelle_langue):
        self.langue_utilisee = nouvelle_langue
        self.lancer_classement_par_region_departement()
