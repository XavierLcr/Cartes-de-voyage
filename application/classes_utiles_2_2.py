################################################################################
# Projet de cartes de voyage                                                   #
# 2.2 - Classes utiles à l'application                                         #
################################################################################

from PyQt6.QtCore import pyqtSignal, QObject


class TrackerPays(QObject):
    tracker_pays_en_cours = pyqtSignal(str)

    def notify(self, libelle_pays: str):
        self.tracker_pays_en_cours.emit(libelle_pays)
