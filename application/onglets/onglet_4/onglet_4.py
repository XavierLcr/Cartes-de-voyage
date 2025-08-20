################################################################################
# Projet de cartes de voyage                                                   #
# application/classes/onglet_4                                                 #
# Onglet 4 – Création de l'onglet complet                                      #
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
from application.onglets.onglet_4 import onglet_4_1_hemicycle, onglet_4_2_classement


class OngletTopPays(QWidget):
    def __init__(
        self,
        dicts_granu,
        constantes,
        liste_gdfs,
        langue_utilisee,
        top_n,
        min_width=500,
        min_height=300,
        n_rangees=9,
        points_base=15,
        points_increment=4,
        lighter_value=150,
        parent=None,
        continent_colors={},
    ):

        super().__init__(parent)

        # Création du QTabWidget
        self.sous_onglets = QTabWidget()

        self.hemicycle = onglet_4_1_hemicycle.HemicycleWidget(
            continents=constantes.liste_regions_monde,
            constantes=constantes,
            langue=langue_utilisee,
            min_width=min_width,
            min_height=min_height,
            n_rangees=n_rangees,
            points_base=points_base,
            points_increment=points_increment,
            lighter_value=lighter_value,
            continent_colors=continent_colors,
        )
        page_hemicycle = QWidget()
        layout_hemicycle = QVBoxLayout(page_hemicycle)
        layout_hemicycle.addWidget(self.hemicycle)
        self.sous_onglets.addTab(page_hemicycle, "Hémicycle")

        # Onglet Classement
        self.classement_widget = onglet_4_2_classement.ClassementPays(
            dicts_granu, constantes, liste_gdfs, langue_utilisee, top_n
        )
        self.sous_onglets.addTab(self.classement_widget, "Top Pays")

        # Layout principal
        layout = QVBoxLayout(self)
        layout.addWidget(self.sous_onglets)

    def set_entetes(
        self, texte_region, texte_departement, texte_onglet_1, texte_onglet_2
    ):
        self.classement_widget.set_entetes(texte_region, texte_departement)
        self.sous_onglets.setTabText(
            self.sous_onglets.indexOf(self.hemicycle.parentWidget()), texte_onglet_1
        )
        self.sous_onglets.setTabText(
            self.sous_onglets.indexOf(self.classement_widget), texte_onglet_2
        )

    def set_dicts_granu(self, dict_nv):
        self.hemicycle.set_pays_visites(pays_visites=dict_nv)
        self.classement_widget.set_dicts_granu(dict_nv)

    def set_langue(self, nouvelle_langue):
        self.hemicycle.set_langue(langue=nouvelle_langue)
        self.classement_widget.set_langue(nouvelle_langue)
