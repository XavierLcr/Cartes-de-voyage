################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_1                                #
# Onglet 4.1.X – Onglet contenant l'hémicycle                                  #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QButtonGroup,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import creer_QLabel_centre
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

        # Ajout de l'alignement
        hemicycle_position_layout = QHBoxLayout()
        self.hemicycle_position_label = creer_QLabel_centre()
        self.hemicycle_position_gauche = QRadioButton()
        self.hemicycle_position_alea = QRadioButton()
        self.hemicycle_position_droite = QRadioButton()
        self.hemicycle_position_alphabet = QRadioButton()
        self.hemicycle_position = QButtonGroup(self)
        self.hemicycle_position.addButton(self.hemicycle_position_gauche, -1)
        self.hemicycle_position.addButton(self.hemicycle_position_alea, 0)
        self.hemicycle_position.addButton(self.hemicycle_position_droite, 1)
        self.hemicycle_position.addButton(self.hemicycle_position_alphabet, 2)
        self.hemicycle_position.buttonClicked.connect(
            self.on_hemicycle_position_clicked
        )
        hemicycle_position_layout.addWidget(self.hemicycle_position_label)
        hemicycle_position_layout.addWidget(self.hemicycle_position_gauche)
        hemicycle_position_layout.addWidget(self.hemicycle_position_alea)
        hemicycle_position_layout.addWidget(self.hemicycle_position_alphabet)
        hemicycle_position_layout.addWidget(self.hemicycle_position_droite)
        self.hemicycle_position_gauche.setChecked(True)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.addWidget(self.hemicycle, stretch=1)
        layout.addLayout(hemicycle_position_layout, stretch=1)

    def set_pays_visites(self, pays_visites: dict):
        self.hemicycle.set_pays_visites(pays_visites=pays_visites)

    def set_langue(self, langue):

        # Hémicycle
        self.hemicycle.set_langue(langue=langue)

        # Alignement
        self.hemicycle_position_label.setText(
            self.fonction_traduction("hemicycle_position_label", suffixe=" :")
        )
        self.hemicycle_position_gauche.setText(
            self.fonction_traduction("hemicycle_position_gauche", prefixe="← ")
        )
        self.hemicycle_position_alea.setText(
            self.fonction_traduction("hemicycle_position_alea", prefixe="⛬ ")
        )
        self.hemicycle_position_droite.setText(
            self.fonction_traduction("hemicycle_position_droite", prefixe="→ ")
        )
        self.hemicycle_position_alphabet.setText(
            self.fonction_traduction(
                "hemicycle_position_alphabet",
                prefixe="𝒶𝒷 ",
            )
        )

    def set_style(self, style, teinte, nuances):
        self.hemicycle.set_style(style=style, teinte=teinte, nuances=nuances)

    def get_hemicycle_position(self, defaut: int = -1):

        return {
            self.hemicycle_position_gauche: -1,
            self.hemicycle_position_alea: 0,
            self.hemicycle_position_droite: 1,
            self.hemicycle_position_alphabet: 2,
        }.get(self.hemicycle_position.checkedButton(), defaut)

    def on_hemicycle_position_clicked(self, bouton):
        position = self.get_hemicycle_position()
        self.hemicycle.set_points_visites_position(position=position)

    def set_hemicycle_position(self, position: int):
        {
            0: self.hemicycle_position_alea,
            1: self.hemicycle_position_droite,
            2: self.hemicycle_position_alphabet,
        }.get(position, self.hemicycle_position_gauche).setChecked(True)
        self.hemicycle.set_points_visites_position(position=position)

    def initialiser_onglet(self, **kwargs):
        self.set_hemicycle_position(position=kwargs.get("hemicycle_position", -1))
