################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.6 – Onglet du portrait du profil                                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from _0_Utilitaires._0_1_fonctions_utiles_gen import voyages_vers_destinations
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_2_nb_pays_visites import (
    CompteurCirculaireWidget,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_1_IA import (
    ProfilVoyageurIA,
)

# 1 -- Onglet du portrait client -----------------------------------------------


class OngletPortrait(QWidget):

    langue = "français"
    voyages = {}

    def __init__(self, constantes, fct_traduction, parent=None):
        super().__init__(parent=parent)

        layout = QVBoxLayout()

        # Compteur de pays visités
        self.compteur_pays = CompteurCirculaireWidget(
            maximum=len(constantes.granularite_max_pays.keys()),
            fonction_traduction=fct_traduction,
        )

        layout_temp = QHBoxLayout()
        layout_temp.addWidget(self.compteur_pays)
        layout_temp.addStretch()
        layout.addLayout(layout_temp)

        # Agent IA
        self.description_IA = ProfilVoyageurIA(
            fct_traduction=fct_traduction, parent=self
        )

        layout.addWidget(self.description_IA)
        self.setLayout(layout)

    def set_langue(self, langue):

        self.langue = langue
        self.description_IA.set_langue(langue=langue)
        self.compteur_pays.set_langue()

    def set_voyages(self, voyages):

        self.voyages = voyages
        self.description_IA.set_voyages(voyages=voyages)

        destinations_temp = voyages_vers_destinations(dict_voyages=voyages)
        destinations_temp = set(
            list((destinations_temp.get("region") or {}).keys())
            + list((destinations_temp.get("dep") or {}).keys())
        )
        self.compteur_pays.set_value(value=len(destinations_temp))

    def initialiser_onglet(self, **kwargs):
        self.description_IA.initialiser_onglet()

    def set_style(self, style, nuances, teintes):

        self.compteur_pays.set_style(style=style, nuances=nuances, teintes=teintes)
