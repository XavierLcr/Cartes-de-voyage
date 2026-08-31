################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# 0.13 – LLM appelable en local                                                #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QSize, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import creer_icone
from _4_Interface._4_3_Icones._4_3_25_disquette import _dessiner_icone_disquette

# 1 -- Fonction générale -------------------------------------------------------


class QPushButtonIcone(QPushButton):
    """QPushButton affichant uniquement une icône."""

    def __init__(
        self,
        icone: QIcon,
        taille: int = 32,
        parent=None,
    ):
        super().__init__(parent)

        self.setIcon(icone)
        self.setIconSize(QSize(taille, taille))
        self.setFixedSize(taille, taille)

        self.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 0px;
                margin: 0px;
                background: transparent;
            }

            QPushButton:hover {
                background: rgba(128, 128, 128, 30);
                border-radius: 4px;
            }

            QPushButton:pressed {
                background: rgba(128, 128, 128, 60);
                border-radius: 4px;
            }
        """)


# 2 -- Application -------------------------------------------------------------


## 2.1 -- Bouton de sauvegarde -------------------------------------------------


class QPushButtonSauvegarde(QPushButtonIcone):

    def __init__(self, taille=32, parent=None):

        super().__init__(
            icone=creer_icone(_dessiner_icone_disquette), taille=taille, parent=parent
        )

        self.clicked.connect(lambda: self.sauvegarde_effectuee(temps_ms=3000))

    def setBonIcone(self, validee: bool):

        self.setIcon(
            creer_icone(
                fonction_dessin=lambda painter, centre, taille: _dessiner_icone_disquette(
                    painter=painter, centre=centre, taille=taille, validee=validee
                )
            )
        )

    def sauvegarde_effectuee(self, temps_ms: int):

        self.setBonIcone(validee=True)

        QTimer.singleShot(
            temps_ms,
            lambda: self.setBonIcone(validee=False),
        )
