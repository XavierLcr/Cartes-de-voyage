################################################################################
# Projet de cartes de voyage                                                   #
# application/onglets                                                          #
# Onglet 5 – Informations                                                      #
################################################################################


from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QScrollArea,
)


class OngletInformations(QWidget):
    def __init__(self, fct_traduire, version_logiciel, parent=None):
        super().__init__(parent)

        # Récupération des variables
        self.fonction_traduire = fct_traduire
        self.version_logiciel = version_logiciel

        layout = QHBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.label = QLabel()
        self.label.setWordWrap(True)
        self.scroll_area.setWidget(self.label)

        layout.addWidget(self.scroll_area)

    def set_langue(self):
        """Permet de mettre à jour le texte affiché."""

        self.label.setText(
            self.fonction_traduire(
                "description_application",
                prefixe=self.fonction_traduire(
                    "version",
                    prefixe=self.fonction_traduire(
                        "sous_titre_description_application",
                        prefixe="<h2>MesVoyages – ",
                        suffixe="<br>(",
                    ),
                    suffixe=f" {self.version_logiciel})</h2><hr>",
                ),
                suffixe="<br>",
            )
        )
