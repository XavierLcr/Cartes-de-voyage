################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4 – Création de l'onglet complet                                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import copy

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
)

from _0_Utilitaires._0_1_fonctions_utiles_gen import voyages_vers_destinations
from _0_Utilitaires._0_2_fonctions_graphiques import renvoyer_couleur_texte
from _4_Interface._4_1_Onglets.onglet_4 import (
    onglet_4_1_hemicycle,
    onglet_4_2_classement,
    onglet_4_3_recommendations,
)


# 1 -- Classe de l'onglet contenant les statistiques ---------------------------


class OngletTopPays(QWidget):
    def __init__(
        self,
        constantes,
        fct_traduction,
        table_superficie,
        parent,
    ):
        super().__init__(parent)

        self.mise_en_page = constantes.parametres_application.get(
            "onglet_4_mise_en_page"
        )
        self.fonction_traduction = fct_traduction
        self.constantes = constantes

        # Hémicycle
        self.hemicycle = onglet_4_1_hemicycle.HemicycleWidget(
            constantes=constantes,
        )
        page_hemicycle = QWidget()
        layout_hemicycle = QVBoxLayout(page_hemicycle)
        layout_hemicycle.addWidget(self.hemicycle)

        # Pays les plus visités
        self.classement_widget = onglet_4_2_classement.ClassementPays(
            constantes=constantes,
            table_superficie=table_superficie,
            fct_traduction=self.fonction_traduction,
        )

        # Recommandations de voyage
        self.recommandations = onglet_4_3_recommendations.PaysAVisiter(
            constantes=constantes,
            table_superficie=table_superficie,
            fct_traduire=fct_traduction,
            parent=None,
        )

        # Mise en page des sous-onglets
        layout = QVBoxLayout(self)

        if self.mise_en_page == 0:

            ## === Stack (remplace QTabWidget) ===
            self.pages = QStackedWidget()
            self.pages.addWidget(page_hemicycle)  # index 0
            self.pages.addWidget(self.classement_widget)  # index 1
            self.pages.addWidget(self.recommandations)  # index 2

            # === Barre de boutons (navigation) ===
            btn_layout = QHBoxLayout()
            self.btn_hemicycle = QPushButton("Hémicycle")
            self.btn_top_pays = QPushButton("Top Pays")
            self.btn_recommandations = QPushButton("Suggestions")
            btn_layout.addWidget(self.btn_hemicycle)
            btn_layout.addWidget(self.btn_top_pays)
            btn_layout.addWidget(self.btn_recommandations)

            # Connexions
            self.btn_hemicycle.clicked.connect(lambda: self.pages.setCurrentIndex(0))
            self.btn_top_pays.clicked.connect(lambda: self.pages.setCurrentIndex(1))
            self.btn_recommandations.clicked.connect(
                lambda: self.pages.setCurrentIndex(2)
            )
            # self.btn_recommandations.clicked.connect(self.pop_up_recommandations)

            # Layout principal
            layout.addLayout(btn_layout)
            layout.addWidget(self.pages)

        elif self.mise_en_page == 1:

            ## === Création du QTabWidget ===
            self.sous_onglets = QTabWidget()
            self.sous_onglets.addTab(page_hemicycle, "Hémicycle")
            self.sous_onglets.addTab(self.classement_widget, "Top Pays")
            self.sous_onglets.addTab(self.recommandations, "Top Pays")

            ## === Layout principal ===
            layout.addWidget(self.sous_onglets)

    def set_langue(self, nouvelle_langue):
        self.hemicycle.set_langue(langue=nouvelle_langue)
        self.classement_widget.set_langue(nouvelle_langue)
        self.recommandations.set_langue(langue=nouvelle_langue)

        texte_onglet_1 = self.fonction_traduction(
            "titre_sous_onglet_4_1",
            suffixe=(" 🗺️"),
        )
        texte_onglet_2 = self.fonction_traduction(
            "titre_sous_onglet_4_2",
            suffixe=(" 🏆"),
        )
        texte_onglet_3 = self.fonction_traduction(
            "titre_sous_onglet_4_3",
            suffixe=(" 🚂​"),
        )

        if self.mise_en_page == 0:
            self.btn_hemicycle.setText(texte_onglet_1)
            self.btn_top_pays.setText(texte_onglet_2)
            self.btn_top_pays.setToolTip(
                self.fonction_traduction("description_onglet_4", suffixe=".")
            )
            self.btn_recommandations.setText(texte_onglet_3)
        elif self.mise_en_page == 1:
            self.sous_onglets.setTabText(
                self.sous_onglets.indexOf(self.hemicycle.parentWidget()), texte_onglet_1
            )
            self.sous_onglets.setTabText(
                self.sous_onglets.indexOf(self.classement_widget), texte_onglet_2
            )
            self.sous_onglets.setTabToolTip(
                self.sous_onglets.indexOf(self.classement_widget),
                self.fonction_traduction("description_onglet_4", suffixe="."),
            )
            self.sous_onglets.setTabText(
                self.sous_onglets.indexOf(self.recommandations), texte_onglet_3
            )

    def set_style(self, style: int, teinte, nuances):

        # Style de l'hémicycle
        self.hemicycle.set_style(
            couleur=renvoyer_couleur_texte(
                style=style,
                couleur=self.palette().color(self.backgroundRole()).name(),
            )
        )

        # Onglet 4.3
        self.recommandations.set_bouton_recommandation(
            style=style, teinte=teinte, nuances=nuances
        )

    def set_dicts_granu(self, dict_nv):
        dict_temp = voyages_vers_destinations(copy.deepcopy(dict_nv))
        self.hemicycle.set_pays_visites(pays_visites=dict_temp)
        self.classement_widget.set_dicts_granu(dict_nv=dict_temp)
        self.recommandations.set_dicts_granu(dict_nv=dict_temp)

    def initialiser_onglet(self):
        self.recommandations.initialiser_onglet()

    def set_hemicycle_position(self, val: int):
        self.hemicycle.set_points_visites_position(position=val)

    def get_hemicycle_position(self):
        return self.hemicycle.get_points_visites_position()

    def set_recommandations_par_pays(self, val: bool):
        self.recommandations.set_recommandations_par_pays(val=val)

    def get_recommandations_par_pays(self):
        return self.recommandations.get_recommandations_par_pays()

    def set_recommandations_nb(self, val: int):
        self.recommandations.set_recommandations_nb(val=val)

    def get_recommandations_nb(self):
        return self.recommandations.get_recommandations_nb()
