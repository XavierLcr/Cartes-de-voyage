################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# 0.16 – Sélecteur de valeurs                                                  #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QButtonGroup,
    QLabel,
    QVBoxLayout,
)

# 1 -- Sélecteur de valeurs ----------------------------------------------------


class SelecteurValeurs(QWidget):

    valeur_changee = pyqtSignal(int)

    # Style graphique
    STYLE_CONTENEUR = """
        QWidget#selecteur {
            background-color: #E9ECF2;
            border-radius: 10px;
        }
    """

    STYLE_BOUTON = """
        QPushButton {
            background-color: transparent;
            color: #687386;
            border: none;
            border-radius: 7px;
            padding: 5px 12px;
            font-size: 10pt;
            font-weight: 500;
        }

        QPushButton:hover:!checked {
            background-color: rgba(255, 255, 255, 100);
            color: #34445C;
        }

        QPushButton:checked {
            background-color: #FFFFFF;
            color: #34445C;
            font-weight: 600;
        }
    """

    def __init__(
        self,
        valeurs,
        valeur_initiale_index: int = 0,
        layout_horizontal: bool = True,
        parent=None,
    ):
        super().__init__(parent)

        # Initialisation des attributs
        self.valeurs = []
        self.index = None
        self.boutons = {}
        self.layout_horizontal = layout_horizontal

        # Initialisation de l'interface
        self._initialiser_interface()

        # Définition des valeurs
        self.definir_valeurs(
            valeurs,
            valeur_initiale_index=valeur_initiale_index,
        )

    # 1.1 -- Initialisation de l'interface -------------------------------------

    def _initialiser_interface(self):

        self.setObjectName("selecteur")
        self.setStyleSheet(self.STYLE_CONTENEUR)

        self.layout_principal = {
            True: QHBoxLayout,
            False: QVBoxLayout,
        }.get(
            self.layout_horizontal, QHBoxLayout
        )(self)

        self.layout_principal.setContentsMargins(3, 3, 3, 3)
        self.layout_principal.setSpacing(2)

        self.groupe = QButtonGroup(self)
        self.groupe.setExclusive(True)

    def _creer_bouton(self, index):

        bouton = QPushButton(str(self.valeurs[index]))
        bouton.setCheckable(True)
        bouton.setCursor(Qt.CursorShape.PointingHandCursor)
        bouton.setMinimumHeight(32)
        bouton.setSizePolicy(
            bouton.sizePolicy().Policy.Expanding,
            bouton.sizePolicy().Policy.Preferred,
        )
        bouton.setStyleSheet(self.STYLE_BOUTON)

        bouton.clicked.connect(lambda checked, i=index: self._changer_valeur(i))

        self.groupe.addButton(bouton, index)
        self.layout_principal.addWidget(bouton)

        self.boutons[index] = bouton

        return bouton

    # 1.2 -- Gestion des valeurs -----------------------------------------------

    def _valider_valeurs(self, valeurs, valeur_initiale_index):

        if not valeurs:
            raise ValueError("Le sélecteur doit contenir au moins une valeur.")

        if not all(isinstance(valeur, str) for valeur in valeurs):
            raise ValueError("Les libellés doivent être des chaînes de caractères.")

        if not isinstance(valeur_initiale_index, int) or isinstance(
            valeur_initiale_index, bool
        ):
            raise ValueError("L'index initial doit être un entier.")

        if not 0 <= valeur_initiale_index < len(valeurs):
            raise ValueError("L'index initial est en dehors des valeurs proposées.")

    def definir_valeurs(
        self,
        valeurs,
        valeur_initiale_index=None,
        emettre_signal=False,
    ):

        # Conversion en liste
        valeurs = list(valeurs) if valeurs is not None else []

        # Déterminer la nouvelle sélection
        ancien_index = self.index

        if valeur_initiale_index is not None:
            nouvel_index = valeur_initiale_index
        elif ancien_index is not None and ancien_index < len(valeurs):
            nouvel_index = ancien_index
        else:
            nouvel_index = 0

        # Validation
        self._valider_valeurs(valeurs, nouvel_index)

        # Supprimer les anciens boutons
        for bouton in self.boutons.values():
            self.groupe.removeButton(bouton)
            self.layout_principal.removeWidget(bouton)
            bouton.deleteLater()

        self.boutons.clear()

        # Mettre à jour les valeurs
        self.valeurs = valeurs
        self.index = nouvel_index

        # Créer les nouveaux boutons
        for index in range(len(self.valeurs)):

            bouton = self._creer_bouton(index)

            if index == self.index:
                bouton.setChecked(True)

        # Émettre le signal si nécessaire
        if emettre_signal and ancien_index != nouvel_index:
            self.valeur_changee.emit(nouvel_index)

    # 1.3 -- Gestion de la sélection -------------------------------------------

    def _changer_valeur(self, index):

        if index == self.index:
            return

        self.index = index
        self.valeur_changee.emit(index)

    def definir_valeur(self, index, emettre_signal=False):

        if index not in self.boutons:
            raise ValueError(f"Index inconnu : {index}")

        if index == self.index:
            return

        self.index = index
        self.boutons[index].setChecked(True)

        if emettre_signal:
            self.valeur_changee.emit(index)

    def obtenir_valeur(self):

        return self.index

    # 1.4 -- Gestion des boutons -----------------------------------------------

    def definir_activation(self, index, actif=True):

        if index not in self.boutons:
            raise ValueError(f"Index inconnu : {index}")

        self.boutons[index].setEnabled(actif)


# 2 -- Visualisation -----------------------------------------------------------


if __name__ == "__main__":

    app = QApplication(sys.argv)

    fenetre = QWidget()
    fenetre.setWindowTitle("Test - Sélecteur de valeurs")
    fenetre.resize(460, 220)

    layout = QVBoxLayout(fenetre)
    layout.setContentsMargins(30, 30, 30, 30)
    layout.setSpacing(20)

    titre = QLabel("Granularité géographique")

    selecteur = SelecteurValeurs(
        valeurs=["Pays", "Continents", "Régions", "Départements"],
        valeur_initiale_index=2,
    )

    resultat = QLabel(f"Index sélectionné : {selecteur.obtenir_valeur()}")

    selecteur.valeur_changee.connect(
        lambda index: resultat.setText(f"Index sélectionné : {index}")
    )

    # Modification de la liste (exemple)
    # selecteur.definir_valeurs(["Faible", "Moyen", "Élevé"])

    layout.addWidget(titre)
    layout.addWidget(selecteur)
    layout.addWidget(resultat)
    layout.addStretch()

    fenetre.show()
    sys.exit(app.exec())
