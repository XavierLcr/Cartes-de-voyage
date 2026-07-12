################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.6 – Onglet du portrait du profil                                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from _0_Utilitaires._0_1_fonctions_utiles_gen import voyages_vers_destinations

from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_1_nb_pays_visites import (
    CompteurCirculaireWidget,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_2_n_voyages import (
    NombreVoyagesAnnu,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_3_jours_par_mois import (
    JoursVoyagesParMoisWidget,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_4_continent_favori import (
    ContinentFavoriWidget,
)

# 1 -- Onglet du portrait client -----------------------------------------------


class OngletTableauDeBord(QWidget):

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

        # Compteur de voyages
        self.n_voyages_histo = NombreVoyagesAnnu(
            fonction_traduction=fct_traduction,
        )

        # Compteur de jours
        self.n_jours_voyages = JoursVoyagesParMoisWidget(
            fonction_traduction=fct_traduction
        )

        # Continent favori
        self.continent_favori = ContinentFavoriWidget(
            constantes=constantes, fonction_traduction=fct_traduction
        )

        layout_temp = QHBoxLayout()
        layout_temp.addWidget(self.n_voyages_histo, stretch=1)
        layout_temp.addWidget(self.n_jours_voyages, stretch=1)
        # layout_temp.addStretch()
        layout.addLayout(layout_temp, stretch=1)

        layout_temp = QHBoxLayout()
        layout_temp.addWidget(self.compteur_pays, stretch=1)
        layout_temp.addWidget(self.continent_favori, stretch=1)
        layout_temp.addStretch()
        layout.addLayout(layout_temp, stretch=1)

        self.setLayout(layout)

    def set_langue(self, langue):

        self.langue = langue
        self.compteur_pays.set_langue()
        self.n_voyages_histo.set_langue()
        self.n_jours_voyages.set_langue()
        self.continent_favori.set_langue(langue=langue)

    def set_voyages(self, voyages):

        self.voyages = voyages
        self.n_voyages_histo.set_voyages(voyages=voyages)
        self.n_jours_voyages.set_voyages(voyages=voyages)
        self.continent_favori.set_voyages(voyages=voyages)

        destinations_temp = voyages_vers_destinations(dict_voyages=voyages)
        destinations_temp = set(
            list((destinations_temp.get("region") or {}).keys())
            + list((destinations_temp.get("dep") or {}).keys())
        )
        self.compteur_pays.set_value(value=len(destinations_temp))

    def set_style(self, style, nuances, teintes):

        self.compteur_pays.set_style(style=style, nuances=nuances, teintes=teintes)
        self.n_voyages_histo.set_style(style=style, nuances=nuances, teintes=teintes)
        self.n_jours_voyages.set_style(style=style, nuances=nuances, teintes=teintes)
        self.continent_favori.set_style(style=style, nuances=nuances, teintes=teintes)
