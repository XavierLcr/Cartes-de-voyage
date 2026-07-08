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
    onglet_4_3_recommendations,
    onglet_4_4_n_visites,
    onglet_4_5_derniere_periode,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_2 import onglet_4_2_classement
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6 import onglet_4_6

# 1 -- Classe de l'onglet contenant les statistiques ---------------------------


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

        self.mise_en_page = constantes.parametres_application.get(
            "onglet_4_mise_en_page"
        )
        self.fonction_traduction = fct_traduction

        # Hémicycle
        self.hemicycle = onglet_4_1_hemicycle.HemicycleWidget(
            constantes=constantes,
        )
        page_hemicycle = QWidget()
        layout_hemicycle = QVBoxLayout(page_hemicycle)
        layout_hemicycle.addWidget(self.hemicycle)

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

        # Profil de voyageur
        self.profil_voyageur = onglet_4_6.OngletPortrait(
            fct_traduction=fct_traduction, parent=None
        )

        # Mise en page des sous-onglets
        layout = QHBoxLayout(self)

        if self.mise_en_page == 0:

            ## === Stack (remplace QTabWidget) ===
            self.pages = QStackedWidget()
            self.pages.addWidget(page_hemicycle)
            self.pages.addWidget(self.classement_widget)
            self.pages.addWidget(self.recommandations)
            self.pages.addWidget(self.pays_souvent_visites)
            self.pages.addWidget(self.calendrier_visites)
            self.pages.addWidget(self.profil_voyageur)

            # === Barre de boutons (navigation) ===
            btn_layout = QVBoxLayout()
            self.btn_hemicycle = QPushButton("Hémicycle")
            self.btn_top_pays = QPushButton("Top Pays")
            self.btn_recommandations = QPushButton("Suggestions")
            self.btn_pays_souvent_visites = QPushButton("Pays fréquents")
            self.btn_calendrier = QPushButton("Dernières destinations")
            self.btn_profil_voyageur = QPushButton("Votre profil")
            btn_layout.addWidget(self.btn_hemicycle)
            btn_layout.addWidget(self.btn_top_pays)
            btn_layout.addWidget(self.btn_recommandations)
            btn_layout.addWidget(self.btn_pays_souvent_visites)
            btn_layout.addWidget(self.btn_calendrier)
            btn_layout.addWidget(self.btn_profil_voyageur)
            btn_layout.addStretch()

            # Connexions
            self.btn_hemicycle.clicked.connect(
                lambda: self.cliquer_bouton_onglet(num_onglet=0)
            )
            self.btn_top_pays.clicked.connect(
                lambda: self.cliquer_bouton_onglet(num_onglet=1)
            )
            self.btn_recommandations.clicked.connect(
                lambda: self.cliquer_bouton_onglet(num_onglet=2)
            )
            self.btn_pays_souvent_visites.clicked.connect(
                lambda: self.cliquer_bouton_onglet(num_onglet=3)
            )
            self.btn_calendrier.clicked.connect(
                lambda: self.cliquer_bouton_onglet(num_onglet=4)
            )
            self.btn_profil_voyageur.clicked.connect(
                lambda: self.cliquer_bouton_onglet(num_onglet=5)
            )

            # Layout principal
            layout.addLayout(btn_layout)
            layout.addWidget(self.pages)

        elif self.mise_en_page == 1:

            ## === Création du QTabWidget ===
            self.sous_onglets = QTabWidget()
            self.sous_onglets.addTab(page_hemicycle, "Hémicycle")
            self.sous_onglets.addTab(self.classement_widget, "Top Pays")
            self.sous_onglets.addTab(self.recommandations, "Suggestions")
            self.sous_onglets.addTab(self.pays_souvent_visites, "Pays fréquents")
            self.sous_onglets.addTab(self.calendrier_visites, "Calendrier")
            self.sous_onglets.addTab(self.profil_voyageur, "Votre portrait")

            ## === Layout principal ===
            layout.addWidget(self.sous_onglets)

    def set_langue(self, nouvelle_langue):
        self.hemicycle.set_langue(langue=nouvelle_langue)
        self.classement_widget.set_langue(nouvelle_langue)
        self.recommandations.set_langue(langue=nouvelle_langue)
        self.pays_souvent_visites.set_langue(langue=nouvelle_langue)
        self.calendrier_visites.set_langue(langue=nouvelle_langue)
        self.profil_voyageur.set_langue(langue=nouvelle_langue)

        texte_onglet_1 = self.fonction_traduction(
            "titre_sous_onglet_4_1",
            suffixe=(" 🗺️"),
        )
        texte_onglet_2 = self.fonction_traduction(
            "titre_sous_onglet_4_2",
            suffixe=(" 🏆"),
        )
        texte_onglet_3 = self.fonction_traduction(
            "titre_sous_onglet_4_3",
            suffixe=(" 🚂​"),
        )
        texte_onglet_4 = self.fonction_traduction(
            "titre_sous_onglet_4_4",
            suffixe=(" ⚓​​"),
        )
        texte_onglet_5 = self.fonction_traduction(
            "titre_sous_onglet_4_5",
            suffixe=(" 📅"),
        )
        texte_onglet_6 = self.fonction_traduction(
            "titre_sous_onglet_4_6",
            suffixe=(" 🫆​"),
        )

        if self.mise_en_page == 0:
            self.btn_hemicycle.setText(texte_onglet_1)
            self.btn_top_pays.setText(texte_onglet_2)
            self.btn_top_pays.setToolTip(
                self.fonction_traduction("description_onglet_4", suffixe=".")
            )
            self.btn_recommandations.setText(texte_onglet_3)
            self.btn_pays_souvent_visites.setText(texte_onglet_4)
            self.btn_calendrier.setText(texte_onglet_5)
            self.btn_profil_voyageur.setText(texte_onglet_6)
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
            self.sous_onglets.setTabText(
                self.sous_onglets.indexOf(self.pays_souvent_visites), texte_onglet_4
            )
            self.sous_onglets.setTabText(
                self.sous_onglets.indexOf(self.calendrier_visites), texte_onglet_5
            )
            self.sous_onglets.setTabText(
                self.sous_onglets.indexOf(self.profil_voyageur), texte_onglet_6
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

        # Graphiques
        self.pays_souvent_visites.set_style(style=style, teinte=teinte, nuances=nuances)
        self.calendrier_visites.set_style(style=style, teinte=teinte, nuances=nuances)

    def set_dicts_granu(self, dict_nv):
        # Attention, la màj de self.classement_widget se fait dans cliquer_bouton_onglet
        dict_temp = voyages_vers_destinations(copy.deepcopy(dict_nv))
        self.dict_voyages = copy.deepcopy(dict_nv)
        self.hemicycle.set_pays_visites(pays_visites=dict_temp)
        self.recommandations.set_dicts_granu(dict_nv=dict_temp)
        self.pays_souvent_visites.set_voyages(voyages=copy.deepcopy(dict_nv))
        self.calendrier_visites.set_voyages(voyages=copy.deepcopy(dict_nv))
        self.profil_voyageur.set_voyages(voyages=copy.deepcopy(dict_nv))

    def initialiser_onglet(self, **kwargs):
        self.recommandations.initialiser_onglet(**kwargs)
        self.profil_voyageur.initialiser_onglet(**kwargs)

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

        if num_onglet == 1:
            self.classement_widget.set_dicts_granu(
                dict_nv=voyages_vers_destinations(copy.deepcopy(self.dict_voyages))
            )
