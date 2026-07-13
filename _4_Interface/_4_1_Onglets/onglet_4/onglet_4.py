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
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
)

from _0_Utilitaires._0_1_fonctions_utiles_gen import voyages_vers_destinations
from _0_Utilitaires._0_2_fonctions_graphiques import renvoyer_couleur_texte
from _4_Interface._4_1_Onglets.onglet_4 import (
    onglet_4_1_hemicycle,
    onglet_4_3_recommendations,
    onglet_4_4_n_visites,
    onglet_4_5_derniere_periode,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_2 import onglet_4_2_classement
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6 import onglet_4_6
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_7_portrait_IA import (
    ProfilVoyageurIA,
)

# 1 -- Fonction de renvoi d'un bouton ------------------------------------------


def creer_bouton(texte: str):

    btn_temp = QPushButton(texte)
    btn_temp.setStyleSheet("""
        QPushButton {
            text-align: left;
            padding-left: 10px;
        }
    """)

    return btn_temp


# 2 -- Classe de l'onglet contenant les statistiques ---------------------------


class OngletTopPays(QWidget):

    dict_voyages = {}

    def __init__(
        self,
        constantes,
        fct_traduction,
        table_superficie,
        parent,
    ):
        super().__init__(parent)

        self.fonction_traduction = fct_traduction

        # Hémicycle
        self.hemicycle = onglet_4_1_hemicycle.HemicycleWidget(
            constantes=constantes,
        )

        # Pays les plus visités (en %)
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

        # Pays visités les plus de fois
        self.pays_souvent_visites = onglet_4_4_n_visites.PaysLesPlusVisites(
            constantes=constantes, fct_traduction=fct_traduction, parent=None
        )

        # Calendrier des visites
        self.calendrier_visites = onglet_4_5_derniere_periode.CalendrierVisite(
            fct_traduction=fct_traduction, parent=None
        )

        # Tableau de bord
        self.tableau_de_bord = onglet_4_6.OngletTableauDeBord(
            fct_traduction=fct_traduction, parent=None, constantes=constantes
        )

        self.portrait_IA = ProfilVoyageurIA(fct_traduction=fct_traduction, parent=self)

        # Mise en page des sous-onglets
        layout = QHBoxLayout(self)

        ## === Stack (remplace QTabWidget) ===
        self.pages = QStackedWidget()
        self.pages.addWidget(self.tableau_de_bord)
        self.pages.addWidget(self.hemicycle)
        self.pages.addWidget(self.classement_widget)
        self.pages.addWidget(self.recommandations)
        self.pages.addWidget(self.pays_souvent_visites)
        self.pages.addWidget(self.calendrier_visites)
        self.pages.addWidget(self.portrait_IA)

        # === Barre de boutons (navigation) ===
        self.btn_hemicycle = creer_bouton("Hémicycle")
        self.btn_top_pays = creer_bouton("Top Pays")
        self.btn_recommandations = creer_bouton("Suggestions")
        self.btn_pays_souvent_visites = creer_bouton("Pays fréquents")
        self.btn_calendrier = creer_bouton("Dernières destinations")
        self.btn_tableau_de_bord = creer_bouton("Votre tableau de bord")
        self.btn_portrait_IA = creer_bouton("Votre portrait")

        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.btn_tableau_de_bord)
        btn_layout.addWidget(self.btn_hemicycle)
        btn_layout.addWidget(self.btn_top_pays)
        btn_layout.addWidget(self.btn_recommandations)
        btn_layout.addWidget(self.btn_pays_souvent_visites)
        btn_layout.addWidget(self.btn_calendrier)
        btn_layout.addWidget(self.btn_portrait_IA)
        btn_layout.addStretch()

        # Connexions
        # Chaque bouton doit chercher l'index de SA page (le widget affiché
        # dans le stack), pas l'index d'un autre bouton : c'est ce qui
        # faisait échouer "Dernières destinations" et "Votre tableau de
        # bord" (indexOf() cherchait le bouton lui-même dans le stack, où
        # il n'a jamais été ajouté, et renvoyait -1).
        self.btn_hemicycle.clicked.connect(
            lambda: self.cliquer_bouton_onglet(
                num_onglet=self.pages.indexOf(self.hemicycle)
            )
        )
        self.btn_top_pays.clicked.connect(
            lambda: self.cliquer_bouton_onglet(
                num_onglet=self.pages.indexOf(self.classement_widget)
            )
        )
        self.btn_recommandations.clicked.connect(
            lambda: self.cliquer_bouton_onglet(
                num_onglet=self.pages.indexOf(self.recommandations)
            )
        )
        self.btn_pays_souvent_visites.clicked.connect(
            lambda: self.cliquer_bouton_onglet(
                num_onglet=self.pages.indexOf(self.pays_souvent_visites)
            )
        )
        self.btn_calendrier.clicked.connect(
            lambda: self.cliquer_bouton_onglet(
                num_onglet=self.pages.indexOf(self.calendrier_visites)
            )
        )
        self.btn_tableau_de_bord.clicked.connect(
            lambda: self.cliquer_bouton_onglet(
                num_onglet=self.pages.indexOf(self.tableau_de_bord)
            )
        )
        self.btn_portrait_IA.clicked.connect(
            lambda: self.cliquer_bouton_onglet(
                num_onglet=self.pages.indexOf(self.portrait_IA)
            )
        )

        # Layout principal
        layout.addLayout(btn_layout)
        layout.addWidget(self.pages)

    def set_langue(self, nouvelle_langue):
        self.hemicycle.set_langue(langue=nouvelle_langue)
        self.classement_widget.set_langue(nouvelle_langue)
        self.recommandations.set_langue(langue=nouvelle_langue)
        self.pays_souvent_visites.set_langue(langue=nouvelle_langue)
        self.calendrier_visites.set_langue(langue=nouvelle_langue)
        self.tableau_de_bord.set_langue(langue=nouvelle_langue)
        self.portrait_IA.set_langue(langue=nouvelle_langue)

        texte_onglet_1 = self.fonction_traduction(
            "titre_sous_onglet_4_1",
            prefixe=("🗺️ "),
        )
        texte_onglet_2 = self.fonction_traduction(
            "titre_sous_onglet_4_2",
            prefixe=("🏆 "),
        )
        texte_onglet_3 = self.fonction_traduction(
            "titre_sous_onglet_4_3",
            prefixe=("🚂 "),
        )
        texte_onglet_4 = self.fonction_traduction(
            "titre_sous_onglet_4_4",
            prefixe=("⚓ "),
        )
        texte_onglet_5 = self.fonction_traduction(
            "titre_sous_onglet_4_5",
            prefixe=("📅 "),
        )
        texte_onglet_6 = self.fonction_traduction(
            "titre_sous_onglet_4_6",
            prefixe=("📰 "),
        )
        texte_onglet_7 = self.fonction_traduction(
            "titre_sous_onglet_4_7",
            prefixe=("🫆 "),
        )

        self.btn_hemicycle.setText(texte_onglet_1)
        self.btn_top_pays.setText(texte_onglet_2)
        self.btn_top_pays.setToolTip(
            self.fonction_traduction("description_onglet_4", suffixe=".")
        )
        self.btn_recommandations.setText(texte_onglet_3)
        self.btn_pays_souvent_visites.setText(texte_onglet_4)
        self.btn_calendrier.setText(texte_onglet_5)
        self.btn_tableau_de_bord.setText(texte_onglet_6)
        self.btn_portrait_IA.setText(texte_onglet_7)

    def set_style(self, style: int, teinte, nuances):

        # Style de l'hémicycle
        self.hemicycle.set_style(
            couleur=renvoyer_couleur_texte(
                style=style,
                couleur=self.palette().color(self.backgroundRole()).name(),
            )
        )

        # Pays les plus visités
        self.classement_widget.set_style(style=style, teintes=teinte, nuances=nuances)

        # Onglet 4.3
        self.recommandations.set_bouton_recommandation(
            style=style, teinte=teinte, nuances=nuances
        )

        # Graphiques
        self.pays_souvent_visites.set_style(style=style, teinte=teinte, nuances=nuances)
        self.calendrier_visites.set_style(style=style, teinte=teinte, nuances=nuances)

        # Onglet de tableau de bord
        self.tableau_de_bord.set_style(style=style, teintes=teinte, nuances=nuances)

    def set_dicts_granu(self, dict_nv):
        # Attention, la màj de self.classement_widget se fait dans cliquer_bouton_onglet
        dict_temp = voyages_vers_destinations(copy.deepcopy(dict_nv))
        self.dict_voyages = copy.deepcopy(dict_nv)
        self.hemicycle.set_pays_visites(pays_visites=dict_temp)
        self.recommandations.set_dicts_granu(dict_nv=dict_temp)
        self.pays_souvent_visites.set_voyages(voyages=copy.deepcopy(dict_nv))
        self.calendrier_visites.set_voyages(voyages=copy.deepcopy(dict_nv))
        self.tableau_de_bord.set_voyages(voyages=copy.deepcopy(dict_nv))
        self.portrait_IA.set_voyages(voyages=copy.deepcopy(dict_nv))

    def initialiser_onglet(self, **kwargs):
        self.cliquer_bouton_onglet(num_onglet=self.pages.indexOf(self.tableau_de_bord))
        self.recommandations.initialiser_onglet(**kwargs)
        self.portrait_IA.initialiser_onglet()

    def set_hemicycle_position(self, val: int):
        self.hemicycle.set_points_visites_position(position=val)

    def get_hemicycle_position(self):
        return self.hemicycle.get_points_visites_position()

    def get_recommandations_nb(self):
        return self.recommandations.get_recommandations_nb()

    def creer_dict_parametres(self):

        return {
            # Hémicycle
            "hemicycle_position": self.get_hemicycle_position(),
            # Recommandations
            "recommandations_nb": self.get_recommandations_nb(),
        }

    def cliquer_bouton_onglet(self, num_onglet: int):

        self.pages.setCurrentIndex(num_onglet)

        if num_onglet == self.pages.indexOf(self.classement_widget):
            self.classement_widget.set_dicts_granu(
                dict_nv=voyages_vers_destinations(copy.deepcopy(self.dict_voyages))
            )
