################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/                                                   #
# Onglet des paramètres du profil                                              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QCheckBox,
    QFileDialog,
    QSlider,
    QGroupBox,
    QButtonGroup,
    QRadioButton,
    QProgressBar,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    obtenir_clef_par_valeur,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    reset_combo,
    creer_QLabel_centre,
    creer_ligne_horizontale,
    creer_ligne_verticale,
)
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_1_creation_cartes import CreerCartes
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_2_combobox_coloree import (
    FondCarteCombo,
)
from _4_Interface._4_2_Style._4_2_2_styles_complementaires import (
    style_bouton_de_suppression,
)


# 1 -- Classe des paramètres individuels ---------------------------------------


class OngletParametresProfil(QWidget):

    # Signaux
    signal_dossier = pyqtSignal(str)
    signal_langue = pyqtSignal(str)
    signal_suppression_profil = pyqtSignal(str)

    def __init__(self, constantes, fct_traduction):

        super().__init__()

        # Initialisation des variables
        self.constantes = constantes
        self.fonction_traduction = fct_traduction
        self.langue = "français"
        self.dossier_stockage = None

        # Création du layout principal
        layout = QVBoxLayout()

        # Choix de la langue
        self.langues_dispos = QComboBox()  # Création de la liste déroulante
        self.langues_dispos.addItems(
            ["Français", "English"]
            + sorted(
                langue
                for langue in constantes.dict_langues_dispo.values()
                if langue not in {"Français", "English"}
            )
        )
        self.langues_groupbox = QGroupBox()
        langues_layout = QHBoxLayout()
        langues_layout.addWidget(self.langues_dispos)
        self.langues_groupbox.setLayout(langues_layout)
        layout.addWidget(self.langues_groupbox)
        self.langues_dispos.currentIndexChanged.connect(self.get_langue)

        # Dossier de stockage
        # Choix du dossier
        self.dossier_stockage = None
        self.dossier_stockage_bouton = QPushButton()
        self.dossier_stockage_bouton.clicked.connect(self.choisir_dossier)
        self.dossier_stockage_groupbox = QGroupBox()
        dossier_stockage_layout = QHBoxLayout()
        dossier_stockage_layout.addWidget(self.dossier_stockage_bouton, stretch=2)
        # Ouverture du dossier après publication des cartes
        self.dossier_stockage_ouverture = QCheckBox()
        dossier_stockage_layout.addWidget(self.dossier_stockage_ouverture, stretch=1)
        self.dossier_stockage_groupbox.setLayout(dossier_stockage_layout)
        layout.addWidget(self.dossier_stockage_groupbox)

        # Suppression du profil
        self.suppression_profil = QPushButton()
        self.suppression_profil.setStyleSheet(
            style_bouton_de_suppression(
                sombre=constantes.parametres_application.get("interface_foncee", False)
            )
        )
        layout.addWidget(self.suppression_profil)

        # Layout principal
        self.setLayout(layout)

    def get_langue(self):

        self.langue = obtenir_clef_par_valeur(
            dictionnaire=self.constantes.dict_langues_dispo,
            valeur=self.langues_dispos.currentText(),
        )
        self.signal_langue.emit(self.langue)

    def set_langue(self):

        # Récupération de la langue
        self.langue = obtenir_clef_par_valeur(
            dictionnaire=self.constantes.dict_langues_dispo,
            valeur=self.langues_dispos.currentText(),
        )

        # Langue
        self.langues_groupbox.setTitle(self.fonction_traduction("langue_individu"))

        # Dossier
        self.dossier_stockage_groupbox.setTitle(
            self.fonction_traduction("dossier_stockage_titre")
        )
        self.dossier_stockage_bouton.setText(
            self.fonction_traduction("dossier_stockage_individu")
            if self.dossier_stockage is None
            else os.sep.join(os.path.normpath(self.dossier_stockage).split(os.sep)[-3:])
        )
        self.dossier_stockage_ouverture.setText(
            self.fonction_traduction("dossier_stockage_ouverture")
        )
        self.dossier_stockage_ouverture.setToolTip(
            self.fonction_traduction("dossier_stockage_ouverture_description")
        )

        # Bouton de suppression
        self.suppression_profil.setText(self.fonction_traduction("supprimer_profil"))

    def get_dossier(self):
        return self.dossier_stockage

    def set_dossier(self, dossier):

        self.dossier_stockage = dossier
        self.set_langue()
        self.signal_dossier.emit(self.dossier_stockage)

    def choisir_dossier(self):
        dossier = QFileDialog.getExistingDirectory(
            self, self.fonction_traduction("dossier_stockage_pop_up")
        )
        if dossier:
            self.set_dossier(dossier=dossier)
            self.set_langue()

    def initialiser_param_profil(self, langue, dossier):

        # Langue
        self.langues_dispos.setCurrentIndex(
            self.langues_dispos.findText(
                self.constantes.dict_langues_dispo.get(langue, "Français")
            )
        )
        self.langue = self.get_langue()

        # Dossier
        self.set_dossier(dossier=dossier)
