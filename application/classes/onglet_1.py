################################################################################
# Projet de cartes de voyage                                                   #
# application/classes                                                          #
# Onglet 1 – Paramètres et création des cartes                                 #
################################################################################


import os
import sys
from PyQt6.QtCore import pyqtSignal, QObject

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from production_cartes import carte_main_1_3


# Classe de suivi du pays en cours de cartographie
class TrackerPays(QObject):
    tracker_pays_en_cours = pyqtSignal(str)

    def notify(self, libelle_pays: str):
        self.tracker_pays_en_cours.emit(libelle_pays)


# Classe de création des cartes
class CreerCartes(QObject):
    finished = pyqtSignal()
    tracker_signal = pyqtSignal(str)
    avancer = pyqtSignal(int)

    def __init__(self, params):
        super().__init__()
        self.parametres = params

    def run(self):
        tracker = TrackerPays()
        tracker.tracker_pays_en_cours.connect(self.tracker_signal.emit)

        carte_main_1_3.cree_graphe_depuis_debut(
            **self.parametres, tracker=tracker, blabla=False, afficher_nom_lieu=False
        )

        self.finished.emit()
