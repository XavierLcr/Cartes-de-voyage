################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# 1.09 – Gestionnaire de chargement des GeoDataFrames                          #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QObject, QThread, pyqtSignal

from _0_Utilitaires._0_1_fonctions_utiles_gen import charger_gdfs

# 1 -- Worker de chargement ----------------------------------------------------


class WorkerChargementGDFS(QObject):
    """Charge les GeoDataFrames dans un thread secondaire."""

    donnees_chargees = pyqtSignal(object)
    erreur = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, direction):
        super().__init__()

        self.direction = direction

    def run(self):
        """Effectue le chargement des données géographiques."""

        try:
            liste_gdfs = charger_gdfs(
                direction_base=self.direction,
                max_niveau=2,
            )

            self.donnees_chargees.emit(liste_gdfs)

        except Exception as e:
            self.erreur.emit(str(e))

        finally:
            self.finished.emit()


# 2 -- Gestionnaire du thread --------------------------------------------------


class GestionnaireChargementGDFS(QObject):
    """Gère le lancement et le suivi du chargement des GeoDataFrames."""

    donnees_chargees = pyqtSignal(object)
    erreur = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._thread = None
        self._worker = None

    def lancer(self, direction):

        if self._thread is not None:
            raise RuntimeError("Un chargement des GeoDataFrames est déjà en cours.")

        self._thread = QThread(self)
        self._worker = WorkerChargementGDFS(direction)

        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)

        self._worker.donnees_chargees.connect(self.donnees_chargees)
        self._worker.erreur.connect(self.erreur)

        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)

        self._thread.finished.connect(self._nettoyer)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    def _nettoyer(self):

        self._worker = None
        self._thread = None
