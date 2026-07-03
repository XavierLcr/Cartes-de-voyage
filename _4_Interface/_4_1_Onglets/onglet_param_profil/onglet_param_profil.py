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
    QPushButton,
    QComboBox,
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QButtonGroup,
    QRadioButton,
    QLineEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    obtenir_clef_par_valeur,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    creer_QLabel_centre,
    creer_ligne_horizontale,
    set_emoji_sauvegarde,
)
from _4_Interface._4_1_Onglets.onglet_param_profil.onglet_param_profil_switch import (
    BoutonSwitch,
)
from _4_Interface._4_2_Style._4_2_2_styles_complementaires import (
    style_bouton_de_suppression,
)

# 1 -- Classe des paramètres individuels ---------------------------------------


class OngletParametresProfil(QWidget):

    # Signaux
    signal_dossier = pyqtSignal(str)
    signal_langue = pyqtSignal(str)
    signal_theme_application = pyqtSignal(bool)
    signal_hemicyle_position = pyqtSignal(int)

    def __init__(self, constantes, fct_traduction):

        super().__init__()

        # Initialisation des variables
        self.langue = "français"
        self.fonction_traduction = fct_traduction
        self.dict_langues = constantes.dict_langues_dispo
        self.dossier_stockage = None
        self.theme_application = True

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
        langues_layout = QHBoxLayout(self.langues_groupbox)
        langues_layout.addWidget(self.langues_dispos)
        self.langues_dispos.currentIndexChanged.connect(self.get_langue)

        # Dossier de stockage
        self.dossier_stockage = None
        self.dossier_stockage_bouton = QPushButton()
        self.dossier_stockage_bouton.clicked.connect(self.choisir_dossier)
        self.dossier_stockage_groupbox = QGroupBox()
        dossier_stockage_layout = QHBoxLayout(self.dossier_stockage_groupbox)
        dossier_stockage_layout.addWidget(self.dossier_stockage_bouton, stretch=2)

        # Ouverture du dossier après publication des cartes
        self.dossier_stockage_ouverture = QCheckBox()
        dossier_stockage_layout.addWidget(
            self.dossier_stockage_ouverture,
            stretch=1,
            alignment=Qt.AlignmentFlag.AlignHCenter,
        )

        # Thème de l'application
        self.theme_application_groupbox = QGroupBox()
        theme_application_layout = QHBoxLayout()
        self.theme_application_bouton = BoutonSwitch()
        theme_application_layout.addWidget(self.theme_application_bouton)
        self.theme_application_groupbox.setLayout(theme_application_layout)
        self.theme_application_bouton.stateChanged.connect(self.set_theme_application)
        self.signal_theme_application.emit(self.theme_application)

        # Cartes à faible granularité
        self.sortir_cartes_granu_inf = QCheckBox()

        # Nombre limite de cartes
        widget_nb_copies_cartes = QWidget()
        radio_layout = QHBoxLayout(widget_nb_copies_cartes)
        self.label_nb_copies_cartes = creer_QLabel_centre()
        radio_layout.setContentsMargins(0, 0, 0, 0)
        radio_layout.setSpacing(9)

        # Création des boutons radio avec noms clairs
        self.radio_carte_1 = QRadioButton()
        self.radio_carte_2 = QRadioButton()
        self.radio_carte_3 = QRadioButton()
        self.radio_carte_sans_limite = QRadioButton()

        # Option par défaut
        self.radio_carte_2.setChecked(True)

        # Groupe exclusif
        self.groupe_radio_max_cartes = QButtonGroup(self)
        self.groupe_radio_max_cartes.addButton(self.radio_carte_1, 1)
        self.groupe_radio_max_cartes.addButton(self.radio_carte_2, 2)
        self.groupe_radio_max_cartes.addButton(self.radio_carte_3, 3)
        self.groupe_radio_max_cartes.addButton(self.radio_carte_sans_limite, -1)

        # Ajout au layout horizontal
        radio_layout.addWidget(self.label_nb_copies_cartes)
        radio_layout.addWidget(self.radio_carte_1)
        radio_layout.addWidget(self.radio_carte_2)
        radio_layout.addWidget(self.radio_carte_3)
        radio_layout.addWidget(self.radio_carte_sans_limite)

        # Groupbox des préférences de cartes
        self.preferences_cartes_groupbox = QGroupBox()
        preferences_cartes_layout = QVBoxLayout(self.preferences_cartes_groupbox)
        preferences_cartes_layout.addWidget(self.sortir_cartes_granu_inf)
        preferences_cartes_layout.addWidget(creer_ligne_horizontale())
        preferences_cartes_layout.addWidget(widget_nb_copies_cartes)

        # Groupbox – e-mails
        self.email_groupbox = QGroupBox()
        email_layout = QHBoxLayout()
        self.email_groupbox.setLayout(email_layout)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("...")
        email_layout.addWidget(creer_QLabel_centre(text="📧 "))
        email_layout.addWidget(self.email_input)

        # Groupbox – Hemicycle
        self.hemicycle_groupbox = QGroupBox()
        hemicycle_layout = QVBoxLayout()
        hemicycle_position_layout = QHBoxLayout()
        self.hemicycle_position_label = creer_QLabel_centre()
        self.hemicycle_position_gauche = QRadioButton()
        self.hemicycle_position_alea = QRadioButton()
        self.hemicycle_position_droite = QRadioButton()
        self.hemicycle_position = QButtonGroup(self)
        self.hemicycle_position.addButton(self.hemicycle_position_gauche, -1)
        self.hemicycle_position.addButton(self.hemicycle_position_alea, 0)
        self.hemicycle_position.addButton(self.hemicycle_position_droite, 1)
        self.hemicycle_position.buttonClicked.connect(self.get_hemicycle_position)
        hemicycle_position_layout.addWidget(self.hemicycle_position_label)
        hemicycle_position_layout.addWidget(self.hemicycle_position_gauche)
        hemicycle_position_layout.addWidget(self.hemicycle_position_alea)
        hemicycle_position_layout.addWidget(self.hemicycle_position_droite)
        hemicycle_layout.addLayout(hemicycle_position_layout)
        self.hemicycle_groupbox.setLayout(hemicycle_layout)
        self.hemicycle_position_gauche.setChecked(True)

        # Bouton de sauvegarde
        self.bouton_sauvegarde = QPushButton()
        self.bouton_sauvegarde.clicked.connect(
            lambda: set_emoji_sauvegarde(self.bouton_sauvegarde, 3000)
        )

        # Suppression du profil
        self.suppression_profil = QPushButton()

        # --- Agencement des groupbox, layouts et widgets --- #

        # Ajout de la langue, du dossier et du thème
        layout_temp = QHBoxLayout()
        layout_temp.addWidget(self.langues_groupbox, stretch=3)
        layout_temp.addWidget(self.dossier_stockage_groupbox, stretch=5)
        layout_temp.addWidget(self.theme_application_groupbox, stretch=2)
        layout.addLayout(layout_temp)

        # Préférences de publication de cartes
        layout.addWidget(self.preferences_cartes_groupbox)

        # E-mail & Statistiques
        layout_temp = QHBoxLayout()
        layout_temp.addWidget(self.email_groupbox)
        layout_temp.addWidget(self.hemicycle_groupbox)
        layout.addLayout(layout_temp)

        # Stretch
        layout.addStretch()

        # Layout des boutons
        layout_boutons_finaux = QHBoxLayout()
        layout_boutons_finaux.addWidget(self.bouton_sauvegarde, stretch=10)
        layout_boutons_finaux.addWidget(self.suppression_profil, stretch=3)
        layout.addLayout(layout_boutons_finaux)

        # Layout principal
        self.setLayout(layout)

    def get_langue(self):

        self.langue = obtenir_clef_par_valeur(
            dictionnaire=self.dict_langues,
            valeur=self.langues_dispos.currentText(),
        )
        self.signal_langue.emit(self.langue)

    def set_langue(self):

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

        # Thème de l'application
        self.theme_application_groupbox.setTitle(
            self.fonction_traduction("theme_application")
        )

        # Préférences de cartes
        self.preferences_cartes_groupbox.setTitle(
            self.fonction_traduction("preferences_cartes_groupbox")
        )

        # Sorties des cartes avec une faible granularité
        self.sortir_cartes_granu_inf.setText(
            self.fonction_traduction(
                "publier_cartes_faible_granularite_uniquement", largeur_max=None
            )
        )
        self.sortir_cartes_granu_inf.setToolTip(
            self.fonction_traduction(
                clef="description_publier_cartes_faible_granularite_uniquement",
                largeur_max=None,
            )
        )

        # Nombre limite de cartes
        self.label_nb_copies_cartes.setText(
            self.fonction_traduction("nombre_exemplaires_cartes", suffixe=" : ")
        )
        self.label_nb_copies_cartes.setToolTip(
            self.fonction_traduction(
                "description_nombre_exemplaires_cartes", suffixe="."
            )
        )
        self.radio_carte_1.setText(self.fonction_traduction("cinq_cartes"))
        self.radio_carte_2.setText(self.fonction_traduction("dix_cartes"))
        self.radio_carte_3.setText(self.fonction_traduction("quinze_cartes"))
        self.radio_carte_sans_limite.setText(
            self.fonction_traduction("pas_de_limite_de_cartes")
        )

        # E-mails
        self.email_groupbox.setTitle(self.fonction_traduction("email_groupbox"))
        self.email_input.setToolTip(
            self.fonction_traduction("email_tooltip", suffixe=".")
        )

        # Hémicycle
        self.hemicycle_groupbox.setTitle(
            self.fonction_traduction("titre_sous_onglet_4_1")
        )
        self.hemicycle_position_label.setText(
            self.fonction_traduction("hemicycle_position_label", suffixe=" :")
        )
        self.hemicycle_position_gauche.setText(
            self.fonction_traduction("hemicycle_position_gauche", prefixe="← ")
        )
        self.hemicycle_position_alea.setText(
            self.fonction_traduction("hemicycle_position_alea", prefixe="⛬ ")
        )
        self.hemicycle_position_droite.setText(
            self.fonction_traduction("hemicycle_position_droite", prefixe="→ ")
        )

        # Bouton de sauvegarde
        self.bouton_sauvegarde.setText("💾")
        self.bouton_sauvegarde.setToolTip(
            self.fonction_traduction("sauvegarder_profil", suffixe=".")
        )

        # Bouton de suppression
        self.suppression_profil.setText(self.fonction_traduction("supprimer_profil"))

    def set_style(self, theme: bool):
        self.suppression_profil.setStyleSheet(style_bouton_de_suppression(sombre=theme))

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

    def get_ouvrir_dossier(self):
        return self.dossier_stockage_ouverture.isChecked()

    def set_ouvrir_dossier(self, ouvrir):
        self.dossier_stockage_ouverture.setChecked(ouvrir)

    def get_theme_application(self):
        return self.theme_application

    def set_theme_application(self, theme: bool):
        self.theme_application = theme
        self.signal_theme_application.emit(self.theme_application)

    def get_sortir_cartes_granu_inf(self):
        return self.sortir_cartes_granu_inf.isChecked()

    def get_hemicycle_position(self, defaut: int = -1):

        self.signal_hemicyle_position.emit(
            {
                self.hemicycle_position_gauche: -1,
                self.hemicycle_position_alea: 0,
                self.hemicycle_position_droite: 1,
            }.get(self.hemicycle_position.checkedButton(), defaut)
        )

    def set_hemicycle_position(self, val: int):
        {
            0: self.hemicycle_position_alea,
            1: self.hemicycle_position_droite,
        }.get(
            val,
            self.hemicycle_position_gauche,
        ).setChecked(True)
        self.signal_hemicyle_position.emit(val)

    def set_sortir_cartes_granu_inf(self, sortir):
        self.sortir_cartes_granu_inf.setChecked(sortir)

    def get_limite_de_cartes(self):

        return {
            self.radio_carte_1: 5,
            self.radio_carte_2: 10,
            self.radio_carte_3: 15,
        }.get(self.groupe_radio_max_cartes.checkedButton(), None)

    def set_limite_de_cartes(self, n_limite: int | None):

        {
            5: self.radio_carte_1,
            10: self.radio_carte_2,
            15: self.radio_carte_3,
        }.get(
            n_limite,
            self.radio_carte_sans_limite,
        ).setChecked(True)

    def get_email(self):
        return self.email_input.text()

    def set_email(self, email: str):
        self.email_input.setText(email)

    def initialiser_param_profil(self, **kwargs):

        # Récupération des valeurs avec des valeurs par défaut
        langue = kwargs.get("langue", None)
        dossier = kwargs.get("dossier_stockage", None)
        ouvrir_dossier = kwargs.get("ouvrir_dossier_stockage", False)
        sortir_cartes_granu_inf = kwargs.get("sortir_cartes_granu_inf", False)
        n_limite_cartes = kwargs.get("limite_n_cartes", 10)
        theme_application = kwargs.get("theme_application", True)
        adresse_email = kwargs.get("adresse_email", "")
        hemicycle_position = kwargs.get("hemicycle_position", -1)

        # Langue
        self.langues_dispos.setCurrentIndex(
            self.langues_dispos.findText(
                self.dict_langues.get(langue or self.langue, "Français")
            )
        )
        self.langue = self.get_langue()

        # Dossier
        self.set_dossier(dossier=dossier)
        self.set_ouvrir_dossier(ouvrir=ouvrir_dossier)

        # Thème de l'application
        self.theme_application_bouton.set_position(checked=theme_application)

        # Sortir les cartes à une granularité inférieure
        self.set_sortir_cartes_granu_inf(sortir=sortir_cartes_granu_inf)

        # Limite de cartes
        self.set_limite_de_cartes(n_limite=n_limite_cartes)

        # Adresse e-mail
        self.set_email(email=adresse_email)

        # Alignement des pays dans l'hémicycle
        self.set_hemicycle_position(val=hemicycle_position)

    def creer_dict_parametres(self):

        return {
            # Adresse e-mail
            "adresse_email": self.get_email(),
            # Thème de l'application
            "theme_application": self.get_theme_application(),
            # Paramètres de stockage
            "dossier_stockage": self.get_dossier(),
            "ouvrir_dossier_stockage": self.get_ouvrir_dossier(),
            # Paramètres des cartes
            "sortir_cartes_granu_inf": self.get_sortir_cartes_granu_inf(),
            "limite_n_cartes": self.get_limite_de_cartes(),
        }
