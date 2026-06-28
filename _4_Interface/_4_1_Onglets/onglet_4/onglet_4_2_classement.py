################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4.2 – Partie classement des pays visités                              #
################################################################################


import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QGridLayout,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    creer_QLabel_centre,
    creer_ligne_horizontale,
    vider_layout,
)

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
        .groupby("pays")[["pct_superficie_dans_pays", "superficie"]]
        .sum()
        .reset_index()
        # Tri des valeurs par ordre décroissant
        .sort_values(
            by=["pct_superficie_dans_pays", "superficie"], ascending=[False, False]
        )
        # Arrondi de la valeur
        .assign(
            pct_superficie_dans_pays=lambda x: x["pct_superficie_dans_pays"].apply(
                lambda x: round(100 * (x or 0), ndigits=ndigits)
            )
        )
        .assign(
            # Mise en forme du pourcentage
            pct_superficie_dans_pays_label=lambda x: x[
                "pct_superficie_dans_pays"
            ].apply(lambda x: f"{x} %".replace(".", ",")),
            # Récupération du nom du pays dans la langue utilisée
            nom_pays=lambda x: x["pays"].apply(
                lambda y: pays_traductions.get(y, {}).get(langue, y)
            ),
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
    df_temp = df_temp[(df_temp["pct_superficie_dans_pays"] > 0) | (df_temp.index < 3)]

    return df_temp


# 2 -- Classe affichant les pays les plus visités ------------------------------


# Quatrième onglet
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

        # Variables passées en paramètre
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

        # --- Bloc "Top pays par région" ---
        self.entete_top_pays_regions = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        layout_entete_top_pays_regions = QVBoxLayout()
        layout_entete_top_pays_regions.addWidget(self.entete_top_pays_regions)

        layout_entete_top_pays_regions.addWidget(creer_ligne_horizontale())
        layout_entete_top_pays_regions.addWidget(QLabel(""))

        self.layout_top_pays_regions = QGridLayout()
        layout_entete_top_pays_regions.addLayout(self.layout_top_pays_regions)
        layout_entete_top_pays_regions.addStretch()

        widget_top_pays_regions = QWidget()
        widget_top_pays_regions.setLayout(layout_entete_top_pays_regions)

        scroll_top_pays_regions = QScrollArea()
        scroll_top_pays_regions.setWidgetResizable(True)
        scroll_top_pays_regions.setWidget(widget_top_pays_regions)

        # --- Bloc "Top pays par département" ---
        self.entete_top_pays_departements = QLabel(
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout_entete_top_pays_departements = QVBoxLayout()
        layout_entete_top_pays_departements.addWidget(self.entete_top_pays_departements)

        layout_entete_top_pays_departements.addWidget(creer_ligne_horizontale())
        layout_entete_top_pays_departements.addWidget(QLabel(""))

        self.layout_top_pays_deps = QGridLayout()
        layout_entete_top_pays_departements.addLayout(self.layout_top_pays_deps)
        layout_entete_top_pays_departements.addStretch()

        widget_top_pays_deps = QWidget()
        widget_top_pays_deps.setLayout(layout_entete_top_pays_departements)

        scroll_top_pays_deps = QScrollArea()
        scroll_top_pays_deps.setWidgetResizable(True)
        scroll_top_pays_deps.setWidget(widget_top_pays_deps)

        # --- Layout principal ---
        layout = QHBoxLayout(self)
        layout.addWidget(scroll_top_pays_regions)
        layout.addWidget(scroll_top_pays_deps)

    def classement_standard(
        self,
        df: pd.DataFrame,
        vbox: QGridLayout,
        top_n_lignes: int,
    ):
        """
        Affiche le classement des pays dans un QGridLayout (vbox).
        - df : DataFrame contenant 'Pays' et 'pct_superficie_dans_pays'
        - vbox : QGridLayout où ajouter les QLabel
        """

        if df is None or df.empty:
            return

        if (
            top_n_lignes < self.min_changement_mise_en_forme
            or not self.adapter_mise_en_forme
        ):
            top_n_lignes = None

        df_temp = df.copy()

        # Ajout des couronnes
        for couronne in [0, 2]:
            vbox.addWidget(
                creer_QLabel_centre(
                    text="👑",
                    alignement=(
                        Qt.AlignmentFlag.AlignRight
                        if couronne == 0
                        else Qt.AlignmentFlag.AlignLeft
                    )
                    | Qt.AlignmentFlag.AlignVCenter,
                ),
                0,
                couronne,
            )

        # Gestion des premières lignes
        if top_n_lignes is not None:

            vbox.addWidget(
                creer_QLabel_centre(
                    text="🥇<br>"
                    f"{', '.join(f'<b>{x}</b>' for x in df_temp['nom_pays'].head(top_n_lignes))}"
                    "<br>100 %",
                    wordWrap=True,
                ),
                0,
                1,
            )

            # Suppression des lignes déjà gérées
            df_temp = df_temp.iloc[top_n_lignes:]

        # Complétion du reste des cases
        for i, (_, row) in enumerate(df_temp.iterrows()):

            if top_n_lignes is not None or i >= 3:
                ligne = 1 + (i // 3)
                col = i % 3
            elif i == 0:
                ligne, col = 0, 1
            else:  # i == 1 ou 2
                ligne, col = 1, 2 * i - 2

            vbox.addWidget(
                creer_QLabel_centre(
                    text=(
                        # Classement
                        f"<b>{row['classement']}</b>"
                        # Nom du pays
                        + f"<br>{'<b>' if ligne == 0 else ''}{row['nom_pays']}{'</b>' if ligne == 0 else ''}<br>"
                        # Part de la superficie visitée
                        + f"{row['pct_superficie_dans_pays_label']}"
                    )
                ),
                ligne,
                col,
            )

    def lancer_classement_pays(self, granularite: int, vbox: QGridLayout):

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

        # Layout nettoyé
        vider_layout(vbox)

        try:

            # Classement des pays
            df_temp = creer_classement_pays(
                # transformation du dictionnaire en Data.frame
                gdf_visite=pd.DataFrame(
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
                ),
                table_superficie=self.table_superficie,
                pays_traductions=self.pays_traductions,
                langue=self.langue_utilisee,
                granularite=granularite,
                top_n=self.top_n,
                ndigits=self.ndigits,
            )
            self.classement_standard(
                df=df_temp,
                vbox=vbox,
                top_n_lignes=(df_temp["pct_superficie_dans_pays"] == 100).sum(),
            )

        except Exception as e:
            pass

    def lancer_classement_par_region_departement(self):
        self.lancer_classement_pays(
            vbox=self.layout_top_pays_regions,
            granularite=1,
        )
        self.lancer_classement_pays(
            vbox=self.layout_top_pays_deps,
            granularite=2,
        )

    def set_dicts_granu(self, dict_nv):
        self.dicts_granu = dict_nv
        self.lancer_classement_par_region_departement()

    def set_langue(self, nouvelle_langue):
        self.langue_utilisee = nouvelle_langue
        self.lancer_classement_par_region_departement()

        self.entete_top_pays_regions.setText(
            self.fonction_traduction(
                "classement_selon_regions", prefixe="<b>", suffixe="</b>"
            )
        )
        self.entete_top_pays_departements.setText(
            self.fonction_traduction(
                "classement_selon_departements", prefixe="<b>", suffixe="</b>"
            )
        )
