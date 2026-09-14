################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_1                                #
# Onglet 4.1.X – Onglet contenant l'hémicycle                                  #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


from PyQt6.QtWidgets import QWidget, QVBoxLayout

from _4_Interface._4_1_Onglets.onglet_4.onglet_4_1.onglet_4_1_3_hemicycle import (
    HemicycleWidget,
)

# 1 -- Classe de l'onglet contenant l'hémicycle --------------------------------


class OngletHemicycle(QWidget):

    def __init__(self, constantes, fonction_traduction, parent=None):
        super().__init__(parent=parent)

        # Récupération des paramètres
        self.fonction_traduction = fonction_traduction

        # Ajout de l'hémicycle
        self.hemicycle = HemicycleWidget(constantes=constantes)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.addWidget(self.hemicycle, stretch=1)

    def set_pays_visites(self, pays_visites: dict):
        self.hemicycle.set_pays_visites(pays_visites=pays_visites)

    def set_langue(self, langue):

        # Hémicycle
        self.hemicycle.set_langue(langue=langue)

    def set_style(self, style, teinte, nuances):
        self.hemicycle.set_style(style=style, teinte=teinte, nuances=nuances)

    def initialiser_onglet(self, **kwargs):
        pass
