################################################################################
# Projet de cartes de voyage                                                   #
# Application principale                                                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys, warnings

# PyQt6
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Scripts et fonctions du projet
import constantes
from _0_Utilitaires import _0_1_fonctions_utiles_gen
from _5_Application._5_2_classe_principale import MesVoyagesApplication

# Suppression d'alertes, d'avis et de messages additionnels
warnings.filterwarnings("ignore")
os.environ["QT_LOGGING_RULES"] = "qt.text.font.db=false"


# 1 -- Import des données ------------------------------------------------------


## 1.1 -- Import de la sauvegarde ----------------------------------------------


sauvegarde = _0_1_fonctions_utiles_gen.ouvrir_fichier(
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="sauvegarde_utilisateurs.yaml",
    defaut={},
)


## 1.2 -- Superficie des territoires -------------------------------------------


df_superficie = _0_1_fonctions_utiles_gen.ouvrir_fichier(
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="table_superficie.pkl",
    defaut=None,
    afficher_erreur="Problème avec la table de superficie.",
)


# 2 -- Lancement de la classe principale ---------------------------------------


if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Affichage du logo en splash screen
    splash = QSplashScreen(
        QPixmap(
            os.path.join(
                constantes.direction_donnees_application, "icone_application.ico"
            )
        ),
        Qt.WindowType.WindowStaysOnTopHint,
    )
    splash.show()
    app.processEvents()  # Force l'affichage

    # Lancement de la fenêtre principale
    window = MesVoyagesApplication(
        constantes=constantes, sauvegarde=sauvegarde, df_superficie=df_superficie
    )
    window.show()

    # Fermeture du splash
    splash.finish(window)

    sys.exit(app.exec())
