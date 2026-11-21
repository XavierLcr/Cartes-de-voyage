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
)

# 1 -- Sélecteur de valeurs ----------------------------------------------------


class SelecteurValeurs(QWidget):

    valeur_changee = pyqtSignal(int)

    # Styles graphiques
    STYLES = {
        "clair": {
            "fond": "#E9EDF4",
            "bouton": "#DCE3EF",
            "bouton_survol": "#D0D9EA",
            "bouton_selectionne": "#C9C5E0",
            "texte": "#737D91",
            "texte_survol": "#4F5870",
            "texte_selectionne": "#45415F",
            "texte_desactive": "#AEB6C5",
        },
        "sombre": {
            "fond": "#292F40",
            "bouton": "#414B61",
            "bouton_survol": "#56627C",
            "bouton_selectionne": "#BDB5DC",
            "texte": "#D0D6E3",
            "texte_survol": "#FFFFFF",
            "texte_selectionne": "#1B1927",
            "texte_desactive": "#778197",
        },
    }

    def __init__(
        self,
        valeurs,
        valeur_initiale_index: int = 0,
        layout_horizontal: bool = True,
        style: str = "sombre",
        parent=None,
    ):
        super().__init__(parent)

        # Initialisation des attributs
        self.valeurs = []
        self.index = None
        self.boutons = {}
        self.layout_horizontal = layout_horizontal
        self.style_actuel = None

        # Initialisation de l'interface
        self._initialiser_interface()

        # Définition des valeurs
        self.definir_valeurs(
            valeurs,
            valeur_initiale_index=valeur_initiale_index,
        )

        # Application du style
        self.set_style(style)

    # 1.1 -- Initialisation de l'interface -------------------------------------

    def _initialiser_interface(self):

        classe_layout = QHBoxLayout if self.layout_horizontal else QVBoxLayout
        self.layout_principal = classe_layout(self)

        self.layout_principal.setContentsMargins(4, 4, 4, 4)
        self.layout_principal.setSpacing(3)

        self.groupe = QButtonGroup(self)
        self.groupe.setExclusive(True)

    def _creer_bouton(self, index):

        bouton = QPushButton(str(self.valeurs[index]))
        bouton.setCheckable(True)
        bouton.setCursor(Qt.CursorShape.PointingHandCursor)
        bouton.setMinimumHeight(34)
        bouton.setSizePolicy(
            bouton.sizePolicy().Policy.Expanding,
            bouton.sizePolicy().Policy.Preferred,
        )

        bouton.clicked.connect(lambda checked, i=index: self._changer_valeur(i))

        self.groupe.addButton(bouton, index)
        self.layout_principal.addWidget(bouton)

        self.boutons[index] = bouton

        return bouton

    # 1.2 -- Gestion des styles ------------------------------------------------

    def set_style(self, style="clair"):

        if style not in self.STYLES:
            raise ValueError(
                f"Style inconnu : {style}. "
                f"Valeurs possibles : {', '.join(self.STYLES)}."
            )

        self.style_actuel = style
        couleurs = self.STYLES[style]

        # Style du conteneur
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {couleurs["fond"]};
                border-radius: 10px;
            }}
        """)

        # Style des boutons
        style_bouton = f"""
            QPushButton {{
                background-color: {couleurs["bouton"]};
                color: {couleurs["texte"]};
                border: 1px solid transparent;
                border-radius: 7px;
                padding: 5px 12px;
                font-size: 10pt;
                font-weight: 500;
            }}

            QPushButton:hover:!checked:!disabled {{
                background-color: {couleurs["bouton_survol"]};
                color: {couleurs["texte_survol"]};
            }}

            QPushButton:checked {{
                background-color: {couleurs["bouton_selectionne"]};
                color: {couleurs["texte_selectionne"]};
                font-weight: 600;
                border: 1px solid {couleurs["bouton_selectionne"]};
            }}

            QPushButton:disabled {{
                background-color: transparent;
                color: {couleurs["texte_desactive"]};
                border: 1px solid transparent;
            }}
        """

        for bouton in self.boutons.values():
            bouton.setStyleSheet(style_bouton)

    # 1.3 -- Gestion des valeurs -----------------------------------------------

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

        # Réappliquer le style aux nouveaux boutons
        if self.style_actuel is not None:
            self.set_style(self.style_actuel)

        # Émettre le signal si nécessaire
        if emettre_signal and ancien_index != nouvel_index:
            self.valeur_changee.emit(nouvel_index)

    # 1.4 -- Gestion de la sélection -------------------------------------------

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

    # 1.5 -- Gestion des boutons -----------------------------------------------

    def definir_activation(self, index, actif=True):

        if index not in self.boutons:
            raise ValueError(f"Index inconnu : {index}")

        self.boutons[index].setEnabled(actif)


# 2 -- Visualisation -----------------------------------------------------------


if __name__ == "__main__":

    app = QApplication(sys.argv)

    fenetre = QWidget()
    fenetre.setWindowTitle("Test - Sélecteur de valeurs")
    fenetre.resize(500, 300)
    fenetre.setStyleSheet("background-color: #F3F4F8;")

    layout = QVBoxLayout(fenetre)
    layout.setContentsMargins(30, 30, 30, 30)
    layout.setSpacing(18)

    titre = QLabel("Granularité géographique")
    titre.setStyleSheet("color: #55516F; font-size: 12pt; font-weight: 600;")

    selecteur = SelecteurValeurs(
        valeurs=["Pays", "Continents", "Régions", "Départements"],
        valeur_initiale_index=2,
        style="clair",
    )

    resultat = QLabel(f"Index sélectionné : {selecteur.obtenir_valeur()}")
    resultat.setStyleSheet("color: #737D91; font-size: 10pt;")

    selecteur.valeur_changee.connect(
        lambda index: resultat.setText(f"Index sélectionné : {index}")
    )

    # Démonstration du changement de thème
    bouton_style = QPushButton("Changer de thème")
    bouton_style.clicked.connect(
        lambda: selecteur.set_style(
            "sombre" if selecteur.style_actuel == "clair" else "clair"
        )
    )

    layout.addWidget(titre)
    layout.addWidget(selecteur)
    layout.addWidget(resultat)
    layout.addWidget(bouton_style)
    layout.addStretch()

    fenetre.show()
    sys.exit(app.exec())
