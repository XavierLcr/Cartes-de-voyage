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
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.label = QLabel()
        self.label.setWordWrap(True)
        self.scroll_area.setWidget(self.label)

        layout.addWidget(self.scroll_area)

    def set_description(self, texte_html: str):
        """Permet de mettre à jour le texte affiché."""
        self.label.setText(texte_html)
