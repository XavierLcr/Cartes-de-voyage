################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/                                                   #
# Onglet 5 – Informations générales (inspiré du README)                        #
################################################################################


from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QScrollArea,
)


from _0_Utilitaires._0_1_Fonctions_utiles import renvoyer_groupbox


class OngletInformations(QWidget):
    def __init__(self, fct_traduire, version_logiciel, parent=None):
        super().__init__(parent)

        # Récupération des variables
        self.fonction_traduire = fct_traduire
        self.version_logiciel = version_logiciel

        layout = QHBoxLayout(self)

        # Scroll area car le texte peut être long
        self.scroll_area = QScrollArea(widgetResizable=True)

        self.label = QLabel(wordWrap=True)
        self.scroll_area.setWidget(self.label)

        layout.addWidget(renvoyer_groupbox(self.scroll_area))

    def set_langue(self):
        """Met à jour la langue."""

        self.label.setText(
            self.fonction_traduire(
                "description_application",
                prefixe=self.fonction_traduire(
                    "version",
                    prefixe=self.fonction_traduire(
                        "sous_titre_description_application",
                        prefixe="<h2>Mes Voyages – ",
                        suffixe="</h2><h3>(",
                    ),
                    suffixe=f" {self.version_logiciel})</h3><hr>",
                ),
                suffixe="<br>",
            )
        )
