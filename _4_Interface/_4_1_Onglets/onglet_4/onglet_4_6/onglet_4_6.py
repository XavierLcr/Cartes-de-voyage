################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.6 – Onglet du portrait du profil                                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtWidgets import QWidget, QVBoxLayout

from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_1_IA import (
    ProfilVoyageurIA,
)

# 1 -- Onglet du portrait client -----------------------------------------------


class OngletPortrait(QWidget):

    langue = "français"
    voyages = {}

    def __init__(self, fct_traduction, parent=None):
        super().__init__(parent=parent)

        # Agent IA
        self.description_IA = ProfilVoyageurIA(
            fct_traduction=fct_traduction, parent=self
        )

        layout = QVBoxLayout()
        layout.addWidget(self.description_IA)
        self.setLayout(layout)

    def set_langue(self, langue):

        self.langue = langue
        self.description_IA.set_langue(langue=langue)

    def set_voyages(self, voyages):

        self.voyages = voyages
        self.description_IA.set_voyages(voyages=voyages)

    def initialiser_onglet(self, **kwargs):
        self.description_IA.initialiser_onglet()
