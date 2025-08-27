################################################################################
# Projet de cartes de voyage                                                   #
# application/onglets/onglet_4                                                 #
# Onglet 4 – Partie classement des pays visités                                #
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

from application.fonctions_utiles_2_0 import creer_ligne_separation


def creer_classement_pays(
    gdf_visite,
    table_superficie,
    granularite: int = 1,
    top_n: int | None = None,
):

    gdf_visite = (
        # Ajout des superficies
        gdf_visite.merge(
            table_superficie,
            how="left",
            left_on=["Pays", "Region"],
            right_on=["NAME_0", f"NAME_{granularite}"],
        )
        # Somme par pays des superficies visitées
        .groupby("Pays")[["pct_superficie_dans_pays", "superficie"]]
        .sum()
        .reset_index()
        # Tri des valeurs par ordre décroissant
        .sort_values(by=["pct_superficie_dans_pays", "superficie"], ascending=[False, False])
    )

    return gdf_visite if top_n is None else gdf_visite.head(top_n)


# Quatrième onglet
class ClassementPays(QWidget):
    def __init__(
        self,
        constantes,
        table_superficie,
        parent=None,
    ):
        super().__init__(parent)

        # Variables passées en paramètre
        self.constantes = constantes
        self.table_superficie = table_superficie
        self.top_n = constantes.parametres_application["top_n_pays"]
        self.ndigits = constantes.parametres_application["pct_ndigits"]
        self.ndigits = None if self.ndigits == 0 else self.ndigits
        self.dicts_granu = {"region": {}, "dep": {}}
        self.langue_utilisee = "français"

        # --- Bloc "Top pays par région" ---
        self.entete_top_pays_regions = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        layout_entete_top_pays_regions = QVBoxLayout()
        layout_entete_top_pays_regions.addWidget(self.entete_top_pays_regions)

        layout_entete_top_pays_regions.addLayout(creer_ligne_separation())
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
        self.entete_top_pays_departements = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        layout_entete_top_pays_departements = QVBoxLayout()
        layout_entete_top_pays_departements.addWidget(self.entete_top_pays_departements)

        layout_entete_top_pays_departements.addLayout(creer_ligne_separation())
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

    def vider_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def lancer_classement_pays(self, granularite: int, vbox: QGridLayout):

        # Complétion des régions à partir des départements
        dict_regions = self.dicts_granu["region"]
        for pays, deps in self.dicts_granu["dep"].items():
            mask = (self.table_superficie["NAME_0"] == pays) & (
                self.table_superficie["NAME_2"].isin(deps)
            )
            dict_regions[pays] = self.table_superficie.loc[mask, "NAME_1"].unique().tolist()

        self.vider_layout(vbox)

        try:

            classement = creer_classement_pays(
                gdf_visite=pd.DataFrame(
                    [
                        (k, v)
                        for k, lst in (
                            dict_regions.items()
                            if granularite == 1
                            else self.dicts_granu["dep"].items()
                        )
                        for v in lst
                    ],
                    columns=["Pays", "Region"],
                ),
                table_superficie=self.table_superficie,
                granularite=granularite,
                top_n=self.top_n,
            )

            for i, (_, row) in enumerate(classement.iterrows()):
                pays = row["Pays"]

                if (
                    i < 3
                    or round(100 * row["pct_superficie_dans_pays"], ndigits=self.ndigits) > 0
                ):

                    indice = ["🥇", "🥈", "🥉"][i] if i < 3 else f"<b>{i + 1}.</b>"
                    label_widget = self.constantes.pays_differentes_langues.get(pays, {}).get(
                        self.langue_utilisee,
                        pays,
                    )
                    if i < 3:
                        label_widget = f"<b>{label_widget}</b>"

                    label_widget = (
                        indice
                        + "<br>"
                        + f"{label_widget}<br>{round(100 * row['pct_superficie_dans_pays'], ndigits=self.ndigits)} %"
                    ).replace(".", ",")

                    label_widget = QLabel(label_widget)
                    label_widget.setAlignment(
                        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
                    )

                    if i == 0:
                        couronne_g = QLabel("👑")
                        couronne_g.setAlignment(
                            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                        )
                        vbox.addWidget(couronne_g, i, 0)
                        vbox.addWidget(label_widget, i, 1)
                        couronne_d = QLabel("👑")
                        couronne_d.setAlignment(
                            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                        )
                        vbox.addWidget(couronne_d, i, 2)
                    elif i in [1, 2]:
                        vbox.addWidget(label_widget, 1, 2 * i - 2)
                    else:
                        vbox.addWidget(label_widget, (i + 3) // 3, i % 3)

        except:
            pass

    def lancer_classement_par_region_departement(self):
        self.lancer_classement_pays(vbox=self.layout_top_pays_regions, granularite=1)
        self.lancer_classement_pays(vbox=self.layout_top_pays_deps, granularite=2)

    def set_dicts_granu(self, dict_nv):
        self.dicts_granu = dict_nv
        self.lancer_classement_par_region_departement()

    def set_langue(self, nouvelle_langue):
        self.langue_utilisee = nouvelle_langue
        self.lancer_classement_par_region_departement()

    def set_entetes(self, texte_region, texte_departement):
        self.entete_top_pays_regions.setText(texte_region)
        self.entete_top_pays_departements.setText(texte_departement)
