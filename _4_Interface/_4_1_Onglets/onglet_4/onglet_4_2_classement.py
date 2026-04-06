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

    gdf_visite = (
        # Ajout des superficies
        gdf_visite.merge(
            table_superficie,
            how="left",
            left_on=["Pays", "Region"],
            right_on=["name_0", f"name_{granularite}"],
        )
        # Somme par pays des superficies visitées
        .groupby("Pays")[["pct_superficie_dans_pays", "superficie"]]
        .sum()
        .reset_index()
        # Tri des valeurs par ordre décroissant
        .sort_values(
            by=["pct_superficie_dans_pays", "superficie"], ascending=[False, False]
        )
        .assign(
            # Mise en forme du pourcentage
            pct_superficie_dans_pays_label=lambda x: x[
                "pct_superficie_dans_pays"
            ].apply(
                lambda x: f"{round(100 * (x or 0), ndigits=ndigits)} %".replace(
                    ".", ","
                )
            ),
            # Récupération du nom du pays dans la langue utilisée
            nom_pays=lambda x: x["Pays"].apply(
                lambda y: pays_traductions.get(y, {}).get(langue, y)
            ),
        )
    )

    # Sélection du top pays si souhaité
    if top_n is not None:
        gdf_visite = gdf_visite.head(top_n)

    return (
        gdf_visite,
        gdf_visite[gdf_visite["pct_superficie_dans_pays"] == 1].shape[0],
    )


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
        self.constantes = constantes
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
        classement: pd.DataFrame,
        vbox: QGridLayout,
        taille_top_100: int,
        adapter: bool,
    ):
        """
        Affiche le classement des pays dans un QGridLayout (vbox).
        - classement : DataFrame contenant 'Pays' et 'pct_superficie_dans_pays'
        - vbox : QGridLayout où ajouter les QLabel
        """

        if classement is None or classement.empty:
            return

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
        if adapter:

            liste_pays = classement["nom_pays"].head(taille_top_100)

            vbox.addWidget(
                creer_QLabel_centre(
                    text=f"🥇<br>{', '.join(f'<b>{x}</b>' for x in liste_pays)}<br>100 %",
                    wordWrap=True,
                ),
                0,
                1,
            )

        else:

            taille_top_100 = min(3, classement.shape[0])
            for i in range(taille_top_100):

                nom_pays = classement["nom_pays"].iloc[i]

                vbox.addWidget(
                    creer_QLabel_centre(
                        text=(
                            ["🥇", "🥈", "🥉"][i]
                            + f"<br><b>{nom_pays}</b><br>"
                            + str(classement["pct_superficie_dans_pays_label"].iloc[i])
                        ).replace(".", ",")
                    ),
                    int(i != 0),
                    {0: 1, 1: 0}.get(i, i),
                )

        for i, (_, row) in enumerate(classement.iloc[taille_top_100:].iterrows()):

            if round(100 * row["pct_superficie_dans_pays"], ndigits=self.ndigits) > 0:

                vbox.addWidget(
                    creer_QLabel_centre(
                        text=(
                            # Classement
                            (f"<b>{taille_top_100 + i + 1}.</b>")
                            # Nom du pays
                            + f"<br>{row['nom_pays']}<br>"
                            # Part de la superficie visitée
                            + f"{row['pct_superficie_dans_pays_label']}"
                        )
                    ),
                    2 + (i // 3) - int(adapter),
                    i % 3,
                )

    def lancer_classement_pays(
        self, granularite: int, vbox: QGridLayout, adapter_mise_en_forme=True
    ):

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
            classement, taille_top_100 = creer_classement_pays(
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
                    columns=["Pays", "Region"],
                ),
                table_superficie=self.table_superficie,
                pays_traductions=self.constantes.pays_differentes_langues.get(pays, {}),
                langue=self.langue_utilisee,
                granularite=granularite,
                top_n=self.top_n,
                ndigits=self.ndigits,
            )

            self.classement_standard(
                classement=classement,
                vbox=vbox,
                taille_top_100=taille_top_100,
                adapter=(taille_top_100 >= self.min_changement_mise_en_forme)
                and adapter_mise_en_forme,
            )

        except Exception as e:
            pass

    def lancer_classement_par_region_departement(self):
        self.lancer_classement_pays(
            vbox=self.layout_top_pays_regions,
            granularite=1,
            adapter_mise_en_forme=self.adapter_mise_en_forme,
        )
        self.lancer_classement_pays(
            vbox=self.layout_top_pays_deps,
            granularite=2,
            adapter_mise_en_forme=self.adapter_mise_en_forme,
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
