################################################################################
# Projet de cartes de voyage                                                   #
# application/classes/onglet_4                                                 #
# Onglet 4 – Partie classement des pays visités                                #
################################################################################


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QGridLayout,
    QTabWidget,
)

from application.fonctions_utiles_2_0 import (
    creer_classement_pays,
    creer_ligne_separation,
)
from production_cartes.creer_carte_1_1 import cree_base_toutes_granularites
from application.classes.onglet_4 import onglet_4_1_hemicycle


# Quatrième onglet
class OngletTopPays(QWidget):
    def __init__(
        self,
        dicts_granu: dict,
        constantes,
        liste_gdfs: list,
        langue_utilisee: str,
        top_n: int | None,
        min_width=500,
        min_height: int = 300,
        n_rangees: int = 9,
        points_base: int = 15,
        points_increment: int = 4,
        lighter_value: int = 150,
        parent=None,
        continent_colors: dict = {
            "Africa": "#3454D1",  # Bleu roi
            "Antarctica": "#2E8B57",  # Vert océan
            "Asia": "#C3423F",  # Rouge cerise
            "Europe": "#7B4B94",  # Violet prune
            "North America": "#2A7F9E",  # Bleu sarcelle
            "Oceania": "#E27D60",  # Orange chaud
            "South America": "#4A7856",  # Vert forêt clair
        },
    ):
        super().__init__(parent)

        # Variables passées en paramètre
        self.constantes = constantes
        self.liste_gdfs = liste_gdfs
        self.langue_utilisee = langue_utilisee
        self.dicts_granu = dicts_granu
        self.top_n = top_n

        # Création de l'hémicycle
        self.hemicycle = onglet_4_1_hemicycle.HemicycleWidget(
            continents=self.constantes.liste_regions_monde,
            constantes=self.constantes,
            langue=self.langue_utilisee,
            min_width=min_width,
            min_height=min_height,
            n_rangees=n_rangees,
            points_base=points_base,
            points_increment=points_increment,
            lighter_value=lighter_value,
            continent_colors=continent_colors,
        )

        # Classement
        layout_top_pays = QHBoxLayout()

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
        self.entete_top_pays_departements = QLabel(
            alignment=Qt.AlignmentFlag.AlignCenter
        )
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

        # --- Ajout des deux scrolls au layout principal ---
        layout_top_pays.addWidget(scroll_top_pays_regions)
        layout_top_pays.addWidget(scroll_top_pays_deps)

        # Layout principal vertical
        statistiques = QVBoxLayout(self)

        # Création d'un QTabWidget pour les sous-onglets
        self.sous_onglets = QTabWidget()

        # ---------- Onglet 1 : Hémicycle ----------
        self.page_hemicycle = QWidget()
        layout_hemicycle = QVBoxLayout(self.page_hemicycle)
        layout_hemicycle.addWidget(self.hemicycle)
        self.sous_onglets.addTab(self.page_hemicycle, "Hémicycle")

        # ---------- Onglet 2 : Top pays ----------
        self.page_top_pays = QWidget()
        layout_top_pays_page = QVBoxLayout(self.page_top_pays)
        layout_top_pays_page.addLayout(layout_top_pays)  # ton layout existant
        self.sous_onglets.addTab(self.page_top_pays, "Top Pays")

        # Ajouter le QTabWidget au layout principal
        statistiques.addWidget(self.sous_onglets)

    def set_entetes(
        self,
        texte_region: str,
        texte_departement: str,
        texte_onglet_1: str,
        texte_onglet_2: str,
    ):
        self.entete_top_pays_regions.setText(texte_region)
        self.entete_top_pays_departements.setText(texte_departement)
        self.sous_onglets.setTabText(
            self.sous_onglets.indexOf(self.page_hemicycle), texte_onglet_1
        )
        self.sous_onglets.setTabText(
            self.sous_onglets.indexOf(self.page_top_pays), texte_onglet_2
        )

    def vider_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def lancer_classement_pays(
        self, granularite: int, top_n: int | None, vbox: QGridLayout, ndigits=0
    ):
        dict_regions = self.dicts_granu["region"] or None
        dict_departements = self.dicts_granu["dep"] or None

        if dict_departements and dict_regions:
            dict_regions = {
                k: v for k, v in dict_regions.items() if k not in dict_departements
            }

        self.vider_layout(vbox)

        try:
            gdf = cree_base_toutes_granularites(
                liste_dfs=self.liste_gdfs,
                liste_dicts=[dict_regions, dict_departements],
                granularite_objectif=granularite,
            )

            classement = creer_classement_pays(
                gdf,
                self.constantes.table_superficie,
                granularite=granularite,
                top_n=top_n,
            )

            for i, (_, row) in enumerate(classement.iterrows()):
                pays = row["Pays"]

                indice = ["🥇", "🥈", "🥉"][i] if i < 3 else f"<b>{i + 1}.</b>"
                label_widget = self.constantes.pays_differentes_langues.get(
                    pays, {}
                ).get(
                    self.langue_utilisee,
                    pays,
                )
                if i < 3:
                    label_widget = f"<b>{label_widget}</b>"

                label_widget = (
                    indice
                    + "<br>"
                    + f"{label_widget}<br>{round(100 * row['pct_superficie_dans_pays'], ndigits=ndigits)} %"
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

    def lancer_classement_par_region_departement(self, top_n: int | None = 10):
        self.lancer_classement_pays(
            granularite=1, top_n=top_n, vbox=self.layout_top_pays_regions
        )
        self.lancer_classement_pays(
            granularite=2, top_n=top_n, vbox=self.layout_top_pays_deps
        )

    def set_dicts_granu(self, dict_nv: dict):
        """Permet de mettre à jour les sélections de destinations."""
        self.dicts_granu = dict_nv
        self.lancer_classement_par_region_departement(top_n=self.top_n)
        self.hemicycle.set_pays_visites(pays_visites=dict_nv)

    def set_langue(self, nouvelle_langue):
        """Permet de mettre à jour la langue."""
        self.langue_utilisee = nouvelle_langue
        self.lancer_classement_par_region_departement(top_n=self.top_n)
        self.hemicycle.set_langue(langue=nouvelle_langue)
