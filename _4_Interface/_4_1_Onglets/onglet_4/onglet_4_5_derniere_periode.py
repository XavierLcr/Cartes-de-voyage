################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.5 – Voyages effectués sur la période la plus récente                #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from datetime import date
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    vider_layout,
    conteneur_graphique_simple,
)
from _0_Utilitaires._0_10_selecteur_date import SelecteurDate
from _0_Utilitaires._0_2_fonctions_graphiques import generer_couleur_aleatoire_hex
from _0_Utilitaires._0_9_plot_diagramme_gantt import plot_diagramme_gantt

# 1 -- Classe PyQt6 ------------------------------------------------------------


class CalendrierVisite(QWidget):

    def __init__(self, fct_traduction, parent=None):
        super().__init__(parent=parent)

        self.langue = "français"
        self.fct_traduction = fct_traduction
        self.voyages = {}

        # Style par défaut
        self.style = 1
        self.teinte = None
        self.nuances = {}

        # Dates de départ
        aujourdhui = date.today()
        try:
            date_il_y_a_un_an = aujourdhui.replace(year=aujourdhui.year - 1)
        except ValueError:
            date_il_y_a_un_an = aujourdhui.replace(year=aujourdhui.year - 1, day=28)

        # Début du graphique
        self.debut_voyage_label = QLabel()
        self.debut_voyage = SelecteurDate(
            parent=self, date=date_il_y_a_un_an.strftime("%Y-%m-%d")
        )
        self.debut_voyage.dateChanged.connect(self.creer_graphique)

        # Fin du graphique
        self.fin_voyage_label = QLabel()
        self.fin_voyage = SelecteurDate(
            parent=self, date=date.today().strftime("%Y-%m-%d")
        )
        self.fin_voyage.dateChanged.connect(self.creer_graphique)

        # Disposition des dates
        layout_dates = QHBoxLayout()
        layout_dates.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_dates.addWidget(self.debut_voyage_label)
        layout_dates.addWidget(self.debut_voyage)
        layout_dates.addSpacing(50)
        layout_dates.addWidget(self.fin_voyage_label)
        layout_dates.addWidget(self.fin_voyage)

        # Layout du graphique
        self.layout_graphique = QHBoxLayout()

        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.addLayout(layout_dates)
        self.layout.addLayout(self.layout_graphique)

    def set_langue(self, langue: str):
        self.langue = langue
        self.debut_voyage_label.setText(
            self.fct_traduction("general_voyage_debut", suffixe=" :")
        )
        self.fin_voyage_label.setText(
            self.fct_traduction("general_voyage_fin", suffixe=" :")
        )
        self.creer_graphique()

    def set_voyages(self, voyages: dict):
        self.voyages = voyages
        self.creer_graphique()

    def set_style(self, style, teinte, nuances):
        self.style = style
        self.teinte = teinte
        self.nuances = nuances
        self.creer_graphique()

    def creer_graphique(self):

        vider_layout(layout=self.layout_graphique)

        if self.voyages:

            fig = plot_diagramme_gantt(
                data=self.voyages,
                voyage_label="nom",
                date_min_label="date_debut",
                date_max_label="date_fin",
                palette_couleurs=[
                    generer_couleur_aleatoire_hex(
                        preset=self.nuances, teintes_autorisees=self.teinte
                    )
                    for i in range(len(self.voyages.keys()))
                ],
                date_min=self.debut_voyage.obtenir_date_str(),
                date_max=self.fin_voyage.obtenir_date_str(),
                titre=self.fct_traduction(
                    "titre_graphique_calendrier_voyages",
                ),
                label_taille_max=30,
            )

            self.layout_graphique.addWidget(
                conteneur_graphique_simple(
                    fig=fig, style=self.style, teinte=self.teinte, nuances=self.nuances
                )
            )
