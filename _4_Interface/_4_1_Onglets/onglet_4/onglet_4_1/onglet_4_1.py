################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_1                                #
# Onglet 4.1.X – Onglet contenant l'hémicycle                                  #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from _4_Interface._4_1_Onglets.onglet_4.onglet_4_1.onglet_4_1_3_hemicycle import (
    HemicycleWidget,
)

# 1 -- Classe de l'onglet contenant l'hémicycle --------------------------------


class OngletHemicycle(QWidget):

    CONTINENTS_HAUT = (
        "World",
        "Europe",
        "North America",
        "Asia",
    )

    CONTINENTS_BAS = (
        "Africa",
        "South America",
        "Oceania",
        "Antarctica",
    )

    def __init__(self, constantes, fonction_traduction, parent=None):
        super().__init__(parent=parent)

        # Récupération des paramètres
        self.fonction_traduction = fonction_traduction
        self.langue = "français"

        # Ajout de l'hémicycle
        self.hemicycle = HemicycleWidget(constantes=constantes)

        # Groupe exclusif des boutons de zoom
        self.groupe_zoom = QButtonGroup(self)
        self.groupe_zoom.setExclusive(True)
        self.boutons_zoom = {}

        # Lignes supérieure et inférieure
        layout_haut = self._creer_ligne_zoom(self.CONTINENTS_HAUT)
        layout_bas = self._creer_ligne_zoom(self.CONTINENTS_BAS)

        # Vue mondiale sélectionnée par défaut
        self.boutons_zoom["World"].setChecked(True)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addLayout(layout_haut)
        layout.addWidget(self.hemicycle, stretch=1)
        layout.addLayout(layout_bas)

        self._mettre_a_jour_textes_zoom()

    # --------------------------------------------------------------------------
    # Création des boutons de zoom
    # --------------------------------------------------------------------------

    def _creer_ligne_zoom(self, continents):

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        for continent in continents:

            bouton = QPushButton()
            bouton.setCheckable(True)
            bouton.clicked.connect(
                lambda checked, continent=continent: self._changer_zoom(continent)
            )

            self.groupe_zoom.addButton(bouton)
            self.boutons_zoom[continent] = bouton

            layout.addWidget(bouton, stretch=1)

        return layout

    # --------------------------------------------------------------------------
    # Zoom
    # --------------------------------------------------------------------------

    def _changer_zoom(self, continent):
        self.hemicycle.set_zoom_continent(continent=continent)

    # --------------------------------------------------------------------------
    # Traduction des boutons
    # --------------------------------------------------------------------------

    def _mettre_a_jour_textes_zoom(self):

        for continent, bouton in self.boutons_zoom.items():
            bouton.setText(self.fonction_traduction(continent))

    # --------------------------------------------------------------------------
    # Mise à jour des données
    # --------------------------------------------------------------------------

    def set_pays_visites(self, pays_visites: dict):
        self.hemicycle.set_pays_visites(pays_visites=pays_visites)

    def set_langue(self, langue):

        self.langue = langue

        # Hémicycle
        self.hemicycle.set_langue(langue=langue)

        # Boutons de zoom
        self._mettre_a_jour_textes_zoom()

    def set_style(self, style, teinte, nuances):
        self.hemicycle.set_style(style=style, teinte=teinte, nuances=nuances)

    def initialiser_onglet(self, **kwargs):
        pass
