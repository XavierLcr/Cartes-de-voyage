################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4 – Création de l'onglet complet                                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import copy

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QButtonGroup,
)

from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
)
from _0_Utilitaires._0_1_fonctions_utiles_gen import voyages_vers_destinations
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_0_menu import BoutonNav
from _4_Interface._4_1_Onglets.onglet_4 import (
    onglet_4_4_n_visites,
    onglet_4_5_derniere_periode,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_1.onglet_4_1 import OngletHemicycle
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_2 import onglet_4_2_classement
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3 import onglet_4_3_recommendations
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6 import onglet_4_6
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_7_portrait_IA import (
    ProfilVoyageurIA,
)
from _4_Interface._4_3_Icones._4_3_9_podium import _dessiner_icone_podium
from _4_Interface._4_3_Icones._4_3_10_hemicycle import _dessiner_icone_hemicycle
from _4_Interface._4_3_Icones._4_3_11_rose_des_vents import (
    _dessiner_icone_rose_vents,
)
from _4_Interface._4_3_Icones._4_3_12_diagramme_gantt import _dessiner_icone_gantt
from _4_Interface._4_3_Icones._4_3_13_levee_drapeaux import _dessiner_icone_drapeaux

# 1 -- Fonctions et widgets annexes ---------------------------------------------


## 1.1 -- Fonction de calcul de la couleur d'accent de la navigation -----------


def renvoyer_couleur_accent(style, teinte, nuances):
    """Convertit `teinte` (couleur, chaîne, ou liste/tuple de couleurs) en QColor.
    Si le format n'est pas reconnu, renvoie une couleur d'accent par défaut."""

    couleur_defaut = QColor(
        renvoyer_couleur_widget(
            style=style,
            teinte=teinte,
            nuances=nuances,
            clair="#6C4AB6",
            sombre="#52F5E7",
        )
    )

    try:
        if isinstance(teinte, (list, tuple)) and len(teinte) > 0:
            teinte = teinte[0]

        couleur = teinte if isinstance(teinte, QColor) else QColor(teinte)

        return couleur if couleur.isValid() else couleur_defaut

    except Exception:
        return couleur_defaut


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
        self.hemicycle = OngletHemicycle(
            constantes=constantes, fonction_traduction=fct_traduction
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

        self.portrait_IA = ProfilVoyageurIA(
            fct_traduction=fct_traduction,
            parent=self,  # contexte=131072
        )

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
        # Les icônes sont fixées ici une fois pour toutes (elles ne dépendent
        # pas de la langue) ; le texte, lui, est renseigné dans set_langue().
        # Pour passer à des dessins maison, il suffira de remplacer la chaîne
        # emoji par un appel à set_icone(QPixmap("chemin/icone.svg")).
        self.btn_hemicycle = BoutonNav(_dessiner_icone_hemicycle)
        self.btn_top_pays = BoutonNav(_dessiner_icone_podium)
        self.btn_recommandations = BoutonNav(_dessiner_icone_rose_vents)
        self.btn_pays_souvent_visites = BoutonNav(_dessiner_icone_drapeaux)
        self.btn_calendrier = BoutonNav(_dessiner_icone_gantt)
        self.btn_tableau_de_bord = BoutonNav("📰")
        self.btn_portrait_IA = BoutonNav("🫆")

        # Association page <-> bouton, utilisée pour mettre en évidence le
        # bouton actif (y compris quand la navigation est déclenchée sans
        # passer par un clic, ex: initialiser_onglet)
        self._boutons_pages = [
            (self.tableau_de_bord, self.btn_tableau_de_bord),
            (self.hemicycle, self.btn_hemicycle),
            (self.classement_widget, self.btn_top_pays),
            (self.recommandations, self.btn_recommandations),
            (self.pays_souvent_visites, self.btn_pays_souvent_visites),
            (self.calendrier_visites, self.btn_calendrier),
            (self.portrait_IA, self.btn_portrait_IA),
        ]

        # Un seul bouton actif à la fois (mise en évidence visuelle de la page courante)
        self.groupe_navigation = QButtonGroup(self)
        self.groupe_navigation.setExclusive(True)
        for _, bouton in self._boutons_pages:
            self.groupe_navigation.addButton(bouton)

        # Couleurs mémorisées pour pouvoir recolorier les libellés à chaque
        # bascule de bouton (le QSS seul ne suffit pas à colorer de façon
        # fiable des QLabel enfants selon l'état :checked du parent)
        self._couleur_texte_defaut = "#161B1B"
        self._couleur_accent = "#6C4AB6"

        for _, bouton in self._boutons_pages:
            bouton.toggled.connect(
                lambda checked, b=bouton: self._maj_couleur_bouton(b, checked)
            )

        btn_layout = QVBoxLayout()
        btn_layout.setContentsMargins(10, 14, 10, 14)
        btn_layout.setSpacing(4)
        btn_layout.addWidget(self.btn_tableau_de_bord)
        btn_layout.addWidget(self.btn_hemicycle)
        btn_layout.addWidget(self.btn_top_pays)
        btn_layout.addWidget(self.btn_recommandations)
        btn_layout.addWidget(self.btn_pays_souvent_visites)
        btn_layout.addWidget(self.btn_calendrier)
        btn_layout.addWidget(self.btn_portrait_IA)
        btn_layout.addStretch()

        # Panneau contenant la barre de navigation, pour pouvoir le styliser
        # comme un vrai panneau latéral (fond, séparateur) plutôt qu'un simple layout
        self.panneau_navigation = QWidget()
        self.panneau_navigation.setObjectName("panneau_navigation")
        self.panneau_navigation.setLayout(btn_layout)
        # Largeur minimale généreuse : sans elle, le panneau se comprime au
        # strict minimum et le texte des boutons (ex. "Votre tableau de
        # bord", "Dernières destinations") se retrouve tronqué
        self.panneau_navigation.setMinimumWidth(220)

        # Style par défaut, avant qu'un thème ne soit appliqué via set_style
        self.styliser_navigation(style=1, teinte=None, nuances={})

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
        layout.addWidget(self.panneau_navigation)
        layout.addWidget(self.pages)

    def _maj_couleur_bouton(self, bouton: BoutonNav, checked: bool):
        """Recolore le libellé d'un bouton de navigation selon qu'il est
        actif ou non. Appelé à chaque bascule (toggled), et donc aussi bien
        pour le bouton qui devient actif que pour celui qui redevient inactif."""
        couleur = self._couleur_accent if checked else self._couleur_texte_defaut
        bouton.set_couleur_texte(couleur, gras=checked)

    def styliser_navigation(self, style, teinte, nuances):
        """Applique un style « panneau latéral » moderne et plat aux boutons de
        navigation, avec une couleur d'accent pour le bouton de la page active."""

        accent = renvoyer_couleur_accent(style=style, teinte=teinte, nuances=nuances)
        r, g, b = accent.red(), accent.green(), accent.blue()

        couleur_texte_defaut = renvoyer_couleur_texte(
            style=style,
            couleur=renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#FCFCFC",
                sombre="#161B1B",
            ),
        )

        # Mémorisation pour les mises à jour dynamiques (cf. _maj_couleur_bouton)
        self._couleur_texte_defaut = couleur_texte_defaut
        self._couleur_accent = f"rgb({r}, {g}, {b})"

        self.panneau_navigation.setStyleSheet(f"""
            QWidget#panneau_navigation {{
                background-color: rgba(0, 0, 0, 10);
                border-right: 1px solid rgba(0, 0, 0, 22);
                border-radius: 8px;
            }}
            QPushButton#bouton_nav {{
                border: none;
                border-left: 3px solid transparent;
                border-radius: 8px;
                background-color: transparent;
            }}
            QPushButton#bouton_nav:hover {{
                background-color: rgba(0, 0, 0, 18);
            }}
            QPushButton#bouton_nav:pressed {{
                background-color: rgba(0, 0, 0, 30);
            }}
            QPushButton#bouton_nav:checked {{
                background-color: rgba({r}, {g}, {b}, 38);
                border-left: 3px solid rgb({r}, {g}, {b});
            }}
            QLabel#icone_nav {{
                font-size: 15px;
                background-color: transparent;
            }}
            QLabel#texte_nav {{
                font-size: 13px;
                background-color: transparent;
                color: {couleur_texte_defaut};
            }}
        """)

        # Réapplique la bonne couleur de texte à chaque bouton (checked ou non)
        # puisque le QSS ci-dessus ne peut pas cibler fiablement un QLabel
        # enfant en fonction de l'état :checked de son QPushButton parent.
        for _, bouton in self._boutons_pages:
            self._maj_couleur_bouton(bouton, bouton.isChecked())

    def set_langue(self, nouvelle_langue):
        self.hemicycle.set_langue(langue=nouvelle_langue)
        self.classement_widget.set_langue(nouvelle_langue)
        self.recommandations.set_langue(langue=nouvelle_langue)
        self.pays_souvent_visites.set_langue(langue=nouvelle_langue)
        self.calendrier_visites.set_langue(langue=nouvelle_langue)
        self.tableau_de_bord.set_langue(langue=nouvelle_langue)
        self.portrait_IA.set_langue(langue=nouvelle_langue)

        texte_onglet_1 = self.fonction_traduction("titre_sous_onglet_4_1")
        texte_onglet_2 = self.fonction_traduction("titre_sous_onglet_4_2")
        texte_onglet_3 = self.fonction_traduction("titre_sous_onglet_4_3")
        texte_onglet_4 = self.fonction_traduction("titre_sous_onglet_4_4")
        texte_onglet_5 = self.fonction_traduction("titre_sous_onglet_4_5")
        texte_onglet_6 = self.fonction_traduction("titre_sous_onglet_4_6")
        texte_onglet_7 = self.fonction_traduction("titre_sous_onglet_4_7")

        self.btn_hemicycle.set_texte(texte_onglet_1)
        self.btn_top_pays.set_texte(texte_onglet_2)
        self.btn_top_pays.setToolTip(
            self.fonction_traduction("description_onglet_4", suffixe=".")
        )
        self.btn_recommandations.set_texte(texte_onglet_3)
        self.btn_pays_souvent_visites.set_texte(texte_onglet_4)
        self.btn_calendrier.set_texte(texte_onglet_5)
        self.btn_tableau_de_bord.set_texte(texte_onglet_6)
        self.btn_portrait_IA.set_texte(texte_onglet_7)

    def set_style(self, style: int, teinte, nuances):

        # Style de l'hémicycle
        self.hemicycle.set_style(style=style, teinte=teinte, nuances=nuances)

        # Style de la barre de navigation (accent basé sur la teinte de l'appli)
        self.styliser_navigation(style=style, teinte=teinte, nuances=nuances)

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
        dict_copy = copy.deepcopy(dict_nv)
        self.dict_voyages = dict_copy
        dict_temp = voyages_vers_destinations(dict_copy)
        self.hemicycle.set_pays_visites(pays_visites=dict_temp)
        self.classement_widget.set_dicts_granu(dict_nv=dict_temp)
        self.recommandations.set_dicts_granu(dict_nv=dict_copy)
        self.pays_souvent_visites.set_voyages(voyages=dict_copy)
        self.calendrier_visites.set_voyages(voyages=dict_copy)
        self.tableau_de_bord.set_voyages(voyages=dict_copy)
        self.portrait_IA.set_voyages(voyages=dict_copy)

    def initialiser_onglet(self, **kwargs):
        self.cliquer_bouton_onglet(num_onglet=self.pages.indexOf(self.tableau_de_bord))
        self.recommandations.initialiser_onglet(**kwargs)
        self.portrait_IA.initialiser_onglet()
        self.hemicycle.initialiser_onglet(**kwargs)

    def set_hemicycle_position(self, val: int):
        self.hemicycle.set_hemicycle_position(position=val)

    def get_hemicycle_position(self):
        return self.hemicycle.get_hemicycle_position()

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

        # Met en évidence le bouton correspondant à la page affichée, même
        # quand cette méthode est appelée sans passer par un clic
        for page, bouton in self._boutons_pages:
            if self.pages.indexOf(page) == num_onglet:
                bouton.setChecked(True)
                break

        if num_onglet == self.pages.indexOf(self.classement_widget):
            self.classement_widget.lancer_classement_par_region_departement()

        if num_onglet == self.pages.indexOf(self.tableau_de_bord):
            self.tableau_de_bord.update_widgets()

        if num_onglet == self.pages.indexOf(self.pays_souvent_visites):
            self.pays_souvent_visites.creer_graphique()
