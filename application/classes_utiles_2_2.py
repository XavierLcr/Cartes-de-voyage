################################################################################
# Projet de cartes de voyage                                                   #
# 2.2 - Classes utiles à l'application                                         #
################################################################################

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QScrollArea, QLabel


class TrackerPays(QObject):
    tracker_pays_en_cours = pyqtSignal(str)

    def notify(self, libelle_pays: str):
        self.tracker_pays_en_cours.emit(libelle_pays)


# Cinquième onglet
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
