################################################################################
# MesVoyages                                                                   #
# Application principale                                                       #
################################################################################

import os
import sys

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yaml
import copy
import pickle
import textwrap
import warnings

# PyQt6
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QLabel,
    QFileDialog,
    QSlider,
    QHBoxLayout,
    QCheckBox,
    QGroupBox,
    QMessageBox,
    QGridLayout,
    QButtonGroup,
    QRadioButton,
    QTabWidget,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QTimer, QSize, QThread

# Scripts et fonctions du projet
import constantes
from production_cartes import creer_graphique_1_2
from application import fonctions_utiles_2_0
from application.onglets import onglet_1, onglet_3, onglet_5
from application.onglets.onglet_4 import onglet_4_2_classement


warnings.filterwarnings("ignore")


# Import de la sauvegarde
try:
    with open(
        os.path.join(constantes.direction_donnees_application, "sauvegarde_param.yaml"),
        "r",
        encoding="utf-8",
    ) as file:
        sauvegarde = yaml.safe_load(file)
except FileNotFoundError:
    sauvegarde = {}

liste_langues_dispo_joli = ["Français", "English"] + sorted(
    langue
    for langue in constantes.dict_langues_dispo.values()
    if langue not in {"Français", "English"}
)


class SettingsApp(QWidget):
    def __init__(self):
        super().__init__()

        self.traductions_interface = constantes.outil_differentes_langues

        self.setWindowTitle("Cartes de voyage")
        self.setGeometry(
            constantes.parametres_application["application_position_largeur"],
            constantes.parametres_application["application_position_hauteur"],
            constantes.parametres_application["application_largeur"],
            constantes.parametres_application["application_hauteur"],
        )
        self.setWindowIcon(
            QIcon(
                os.path.join(
                    constantes.direction_donnees_application, "icone_france.ico"
                )
            )
        )

        self.tabs = QTabWidget()

        # Créer un QWidget pour le contenu de l'onglet principal
        self.main_tab = QWidget()
        self.tabs.addTab(self.main_tab, "Paramètres")

        layout = QVBoxLayout()

        # Créer un label comme titre
        self.titre = QLabel()
        self.titre.setStyleSheet(
            "font-size: 24px; font-weight: bold; text-align: center; font-family: Vivaldi, sans-serif;"
        )

        # Layout vertical
        layout.addWidget(self.titre)  # Ajouter le titre en haut

        self.setLayout(layout)

        self.groupe_params_individu = QGroupBox()

        # Layout horizontal pour organiser les éléments dans la boîte
        layout_params_individu = QHBoxLayout()

        # Champ de texte pour le nom de l'individu
        self.nom_individu = QComboBox(self)
        self.nom_individu.setEditable(True)
        self.nom_individu.setPlaceholderText(" ")
        self.nom_individu.addItems(list(sauvegarde.keys()))
        layout_params_individu.addWidget(self.nom_individu)

        # Bouton pour choisir le dossier de stockage
        self.dossier_stockage = None
        self.dossier_stockage_bouton = QPushButton()
        self.dossier_stockage_bouton.clicked.connect(self.choisir_dossier)
        self.dossier_stockage_bouton.clicked.connect(
            lambda: self.maj_langue_interface(False)
        )
        layout_params_individu.addWidget(self.dossier_stockage_bouton)

        # Choix de la langue
        self.label_langue = QLabel()
        self.label_langue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.langue_utilisee = QComboBox()
        self.langue_utilisee.addItems(liste_langues_dispo_joli)
        layout_params_individu.addWidget(self.label_langue)
        layout_params_individu.addWidget(self.langue_utilisee)
        self.langue_utilisee.currentIndexChanged.connect(
            lambda: self.maj_langue_interface(True)
        )

        # Ajout de la possibilité de supprimer un profil
        layout_params_individu.addWidget(fonctions_utiles_2_0.creer_ligne_verticale())
        self.suppression_profil = QPushButton()
        self.suppression_profil.clicked.connect(
            lambda: self.supprimer_clef(self.nom_individu.currentText())
        )
        self.suppression_profil.setStyleSheet(
            fonctions_utiles_2_0.style_bouton_de_suppression(
                sombre=constantes.parametres_application["interface_foncee"]
            )
        )
        layout_params_individu.addWidget(self.suppression_profil)

        # Ajouter le layout à la group box et la group box au layout général
        self.groupe_params_individu.setLayout(layout_params_individu)
        layout.addWidget(self.groupe_params_individu)

        self.groupe_chargement_yaml = QGroupBox()

        # Stockage des données YAML
        self.fichier_yaml_1 = None
        self.fichier_yaml_2 = None

        # Création des boutons pour charger les YAML
        self.chemin_fichier_yaml_1 = None
        self.chemin_fichier_yaml_2 = None
        self.fichier_yaml_1_bouton = QPushButton()
        self.fichier_yaml_1_bouton.clicked.connect(lambda: self.charger_yaml(1))
        self.fichier_yaml_1_bouton.clicked.connect(
            lambda: self.maj_langue_interface(False)
        )
        self.fichier_yaml_2_bouton = QPushButton()
        self.fichier_yaml_2_bouton.clicked.connect(lambda: self.charger_yaml(2))
        self.fichier_yaml_2_bouton.clicked.connect(
            lambda: self.maj_langue_interface(False)
        )

        # Layout horizontal pour les boutons
        layout_fichiers_yaml = QHBoxLayout()
        layout_fichiers_yaml.addWidget(self.fichier_yaml_1_bouton)
        layout_fichiers_yaml.addWidget(self.fichier_yaml_2_bouton)
        self.groupe_chargement_yaml.setLayout(layout_fichiers_yaml)

        # Créer un QGroupBox pour les choix de granularité
        self.groupe_granularite = QGroupBox()

        # Choix de la granularité
        self.label_granularite_visite = QLabel()
        self.label_granularite_visite.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.granularite_visite = QComboBox()
        layout_granularite_visite = QHBoxLayout()
        layout_granularite_visite.addWidget(self.label_granularite_visite)
        layout_granularite_visite.addWidget(self.granularite_visite)
        layout_granularite_visite.addWidget(
            fonctions_utiles_2_0.creer_ligne_verticale()
        )

        # Granularité de fond
        self.label_granularite_fond = QLabel()
        self.label_granularite_fond.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.granularite_fond = QComboBox()
        layout_granularite_fond = QHBoxLayout()
        layout_granularite_fond.addWidget(self.label_granularite_fond)
        layout_granularite_fond.addWidget(self.granularite_fond)

        # Ajouter le layout horizontal à la group box
        layout_granularite = QHBoxLayout()
        layout_granularite.addLayout(layout_granularite_visite)
        layout_granularite.addLayout(layout_granularite_fond)
        self.groupe_granularite.setLayout(layout_granularite)
        layout.addWidget(self.groupe_granularite)

        # Création des cases à cocher
        self.groupe_cartes_a_creer = QGroupBox()
        self.carte_monde = QCheckBox()
        self.carte_pays = QCheckBox()

        self.europe = QCheckBox()
        self.asie = QCheckBox()
        self.amerique = QCheckBox()

        self.afrique = QCheckBox()
        self.moyen_orient = QCheckBox()
        self.autres_regions = QCheckBox()

        self.publier_granu_faible = QCheckBox()

        self.carte_pays.setChecked(True)
        self.europe.setChecked(True)

        # Création du layout des cartes à créer et des couleurs
        layout_cartes_et_couleurs = QHBoxLayout()

        # Layout des cartes à créer
        layout_cartes_a_creer = QGridLayout()
        layout_cartes_a_creer.addWidget(
            self.carte_monde, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout_cartes_a_creer.addWidget(
            self.carte_pays, 0, 3, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout_cartes_a_creer.addLayout(
            fonctions_utiles_2_0.creer_ligne_separation(
                lStretch=0, ligne_largeur=1, rStretch=0
            ),
            1,
            0,
            1,
            6,
        )

        ligne_regions_1 = 2
        layout_cartes_a_creer.addWidget(self.afrique, ligne_regions_1, 0, 1, 2)
        layout_cartes_a_creer.addWidget(self.amerique, ligne_regions_1, 2, 1, 2)
        layout_cartes_a_creer.addWidget(self.asie, ligne_regions_1, 4, 1, 2)

        ligne_regions_1 = 3
        layout_cartes_a_creer.addWidget(self.europe, ligne_regions_1, 0, 1, 2)
        layout_cartes_a_creer.addWidget(self.moyen_orient, ligne_regions_1, 2, 1, 2)
        layout_cartes_a_creer.addWidget(self.autres_regions, ligne_regions_1, 4, 1, 2)

        layout_cartes_a_creer.addLayout(
            fonctions_utiles_2_0.creer_ligne_separation(
                lStretch=0, ligne_largeur=1, rStretch=0
            ),
            4,
            0,
            1,
            6,
        )

        layout_cartes_a_creer.addWidget(
            self.publier_granu_faible,
            5,
            0,
            1,
            6,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        widget_nb_copies_cartes = QWidget()
        radio_layout = QHBoxLayout()
        radio_layout.setContentsMargins(0, 0, 0, 0)
        radio_layout.setSpacing(10)
        widget_nb_copies_cartes.setLayout(radio_layout)

        # Titre (centré verticalement)
        self.label_nb_copies_cartes = QLabel()
        self.label_nb_copies_cartes.setAlignment(Qt.AlignmentFlag.AlignVCenter)

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

        # Ajout du layout au QGroupBox puis ajout au layout principal
        self.groupe_cartes_a_creer.setLayout(layout_cartes_a_creer)
        layout_granu_cartes_a_creer = QVBoxLayout()
        layout_granu_cartes_a_creer.addWidget(self.groupe_granularite)
        layout_granu_cartes_a_creer.addWidget(self.groupe_cartes_a_creer)
        # layout.addWidget(self.groupe_cartes_a_creer)

        # Boîte des couleurs
        self.groupe_couleurs = QGroupBox()
        layout_theme_color = QVBoxLayout()

        # Choix du thème
        self.theme_label = QLabel()
        self.theme_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.theme_combo = QComboBox()
        self.theme_combo.currentTextChanged.connect(self.maj_style)
        layout_theme = QHBoxLayout()
        layout_theme.addWidget(self.theme_label)
        layout_theme.addWidget(self.theme_combo)

        # Choix des couleurs
        self.color_label = QLabel()
        self.color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.color_combo = QComboBox()
        self.color_combo.currentTextChanged.connect(self.maj_style)
        layout_couleurs = QHBoxLayout()
        layout_couleurs.addWidget(self.color_label)
        layout_couleurs.addWidget(self.color_combo)

        # Utilisation ou non du thème dans l'interface
        self.utiliser_theme = QCheckBox()
        self.utiliser_theme.stateChanged.connect(self.maj_style)

        # Choix de la couleur de fond
        self.couleur_fond_checkbox = QCheckBox()

        # Ajout des widgets au layout vertical
        layout_theme_color.addLayout(layout_theme)
        layout_theme_color.addLayout(layout_couleurs)
        layout_theme_color.addWidget(self.utiliser_theme)
        layout_theme_color.addLayout(
            fonctions_utiles_2_0.creer_ligne_separation(
                lStretch=0, ligne_largeur=1, rStretch=0
            )
        )
        layout_theme_color.addWidget(
            self.couleur_fond_checkbox, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        # Ajout du layout de couleurs au groupbox et ajout du groupbox au layout principal
        self.groupe_couleurs.setLayout(layout_theme_color)

        # # Ajout des groupbox des cartes et des couleurs
        layout_cartes_et_couleurs.addLayout(layout_granu_cartes_a_creer)
        layout_cartes_et_couleurs.addWidget(self.groupe_couleurs)

        # # Ajouter ce layout horizontal au layout principal
        layout.addLayout(layout_cartes_et_couleurs)

        # Group box et layout des paramètres de publication
        self.groupe_params_publication = QGroupBox()
        layout_params_publication = QVBoxLayout()

        # Layout horizontal pour la qualité de l'image et le format
        layout_format_qualite = QHBoxLayout()

        # Curseur pour la qualité de l’image
        self.label_qualite = QLabel()
        self.label_qualite_min = QLabel()
        self.label_qualite_max = QLabel()
        self.curseur_qualite = QSlider(Qt.Orientation.Horizontal)
        self.curseur_qualite.setMinimum(
            constantes.parametres_application["qualite_min"]
        )
        self.curseur_qualite.setMaximum(
            constantes.parametres_application["qualite_max"]
        )
        self.curseur_qualite.setValue(
            int(
                (
                    constantes.parametres_application["qualite_min"]
                    + constantes.parametres_application["qualite_max"]
                )
                / 2
            )
        )

        # Choix du format d'image
        self.label_format = QLabel()
        self.format_cartes = QComboBox()
        self.format_cartes.addItems(
            ["png", "jpg", "svg", "pdf", "tif", "webp", "raw", "ps"]
        )

        # Ajout des widgets au layout horizontal
        layout_format_qualite.addWidget(self.label_format)
        layout_format_qualite.addWidget(self.format_cartes)
        layout_format_qualite.addWidget(self.label_qualite)
        layout_format_qualite.addWidget(self.label_qualite_min)
        layout_format_qualite.addWidget(self.curseur_qualite)
        layout_format_qualite.addWidget(self.label_qualite_max)

        # Ajouter le layout horizontal au layout principal
        layout_params_publication.addLayout(layout_format_qualite)
        layout_params_publication.addWidget(widget_nb_copies_cartes)
        # Ajouter le layout principal à la group box
        self.groupe_params_publication.setLayout(layout_params_publication)

        # Ajouter le QGroupBox au layout principal
        layout.addWidget(self.groupe_params_publication)

        # Bouton de validation
        layout_valid_reinit = QGridLayout()

        # Création du bouton "Créer cartes"
        self.creation_cartes_bouton = QPushButton()
        self.creation_cartes_bouton.clicked.connect(
            lambda: self.fonction_principale(False, False)
        )
        self.barre_progression = QProgressBar()
        self.barre_progression.setMinimum(0)
        self.barre_progression.setValue(0)
        self.barre_progression.setFormat("")

        # Bouton de sauvegarde
        self.bouton_sauvegarde = QPushButton()
        self.bouton_sauvegarde.clicked.connect(
            lambda: self.fonction_principale(True, True)
        )

        # Bouton de réinitialisation
        self.reinit_parametres = QPushButton()
        self.reinit_parametres.clicked.connect(
            lambda: self.reinitialisation_parametres(True)
        )
        self.reinit_parametres.clicked.connect(lambda: self.maj_langue_interface(True))
        self.reinit_parametres.setStyleSheet(
            fonctions_utiles_2_0.style_bouton_de_suppression(
                sombre=constantes.parametres_application["interface_foncee"]
            )
        )

        # Ajouter les widgets dans la grille
        layout_valid_reinit.addWidget(self.reinit_parametres, 0, 0)
        layout_valid_reinit.addWidget(self.creation_cartes_bouton, 0, 1)
        layout_valid_reinit.addWidget(self.barre_progression, 0, 1)
        self.barre_progression.setVisible(False)
        layout_valid_reinit.addWidget(self.bouton_sauvegarde, 0, 2)

        # Ajuster les proportions : colonne 1 (droite) prend plus de place
        layout_valid_reinit.setColumnStretch(0, 1)  # petite colonne gauche
        layout_valid_reinit.setColumnStretch(1, 4)  # plus grande colonne au milieu
        layout_valid_reinit.setColumnStretch(2, 1)  # petite colonne à gauche

        layout.addLayout(layout_valid_reinit)
        self.main_tab.setLayout(layout)

        # Créer de nouveaux onglets
        self.tab_yaml = QWidget()
        self.tabs.addTab(self.tab_yaml, "Création de la liste des pays visités")

        # Ajouter un layout et un label au deuxième onglet
        layout_yaml = QVBoxLayout()
        self.groupe_selection_lieux = QGroupBox()
        layout_selection_lieux = QVBoxLayout()

        self.liste_des_pays = QComboBox()
        self.liste_niveaux = QComboBox()
        self.avertissement_prio = QLabel()
        self.avertissement_prio.setWordWrap(True)
        self.liste_endroits = QListWidget()
        self.liste_endroits.setWrapping(True)
        self.liste_endroits.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.liste_endroits.setGridSize(QSize(250, 25))
        self.telecharger_lieux_visites = QPushButton()
        self.telecharger_lieux_visites.clicked.connect(self.exporter_yamls_visites)
        self.bouton_sauvegarde2 = QPushButton()
        self.bouton_sauvegarde2.clicked.connect(
            lambda: self.fonction_principale(True, True)
        )

        self.dicts_granu = {"region": {}, "dep": {}}

        # Remplir les déroulés
        self.liste_des_pays.addItems(constantes.regions_par_pays.keys())

        self.liste_des_pays.currentTextChanged.connect(self.maj_liste_reg_dep_pays)
        self.liste_niveaux.currentTextChanged.connect(self.maj_liste_reg_dep_pays)
        self.liste_endroits.itemChanged.connect(self.changer_item_liste_pays)

        layout_selection_params = QHBoxLayout()
        layout_selection_params.addWidget(self.liste_des_pays)
        layout_selection_params.addWidget(self.liste_niveaux)
        layout_selection_params.addWidget(self.telecharger_lieux_visites)
        layout_selection_params.addWidget(self.bouton_sauvegarde2)
        layout_selection_params.setStretch(
            0, 3
        )  # Le premier widget prend plus de place
        layout_selection_params.setStretch(
            1, 3
        )  # Le deuxième widget prend plus de place
        layout_selection_params.setStretch(
            2, 1
        )  # Le troisième widget prend moins de place
        layout_selection_params.setStretch(
            3, 1
        )  # Le troisième widget prend moins de place

        layout_selection_lieux.addLayout(layout_selection_params)
        layout_selection_lieux.addWidget(self.avertissement_prio)
        layout_selection_lieux.addWidget(self.liste_endroits)
        self.groupe_selection_lieux.setLayout(layout_selection_lieux)

        layout_yaml.addWidget(self.groupe_selection_lieux)
        layout_yaml.addWidget(self.groupe_chargement_yaml)

        self.tab_yaml.setLayout(layout_yaml)

        # Troisième onglet
        self.onglet_resume_pays = onglet_3.OngletResumeDestinations(
            traduire_depuis_id=self.traduire_depuis_id,
            constantes=constantes,
            dicts_granu=self.dicts_granu,
            langue_utilisee=fonctions_utiles_2_0.obtenir_clef_par_valeur(
                dictionnaire=constantes.dict_langues_dispo,
                valeur=self.langue_utilisee.currentText(),
            ),
        )
        self.tabs.addTab(self.onglet_resume_pays, "📊")

        # Quatrième onglet
        self.top_pays_visites = onglet_4_2_classement.OngletTopPays(
            dicts_granu=self.dicts_granu,
            constantes=constantes,
            langue_utilisee=fonctions_utiles_2_0.obtenir_clef_par_valeur(
                dictionnaire=constantes.dict_langues_dispo,
                valeur=self.langue_utilisee.currentText(),
            ),
            liste_gdfs=liste_gdfs,
            top_n=constantes.parametres_application["top_n_pays"],
            lighter_value=constantes.parametres_application["lighter_value"],
            min_height=constantes.parametres_application["min_height"],
            min_width=constantes.parametres_application["min_width"],
            n_rangees=constantes.parametres_application["n_rangees"],
            points_base=constantes.parametres_application["points_base"],
            points_increment=constantes.parametres_application["points_increment"],
            continent_colors=constantes.parametres_application["couleurs_continents"],
        )
        self.tabs.addTab(self.top_pays_visites, "Pays les plus visités")

        # Onglet 5
        self.description_application = onglet_5.OngletInformations()
        self.tabs.addTab(self.description_application, "ℹ️")

        # Définir le QTabWidget comme layout principal pour le widget principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        self.maj_style()
        self.maj_liste_reg_dep_pays()
        self.maj_langue_interface(True)
        self.setLayout(main_layout)

        # Connections aux fonctions
        self.nom_individu.currentIndexChanged.connect(
            lambda: self.initialiser_sauvegarde(sauvegarde)
        )
        # self.nom_individu.editTextChanged.connect(
        #     lambda: self.initialiser_sauvegarde(sauvegarde)
        # )

        self.nom_individu.currentIndexChanged.connect(
            lambda: self.maj_langue_interface(True)
        )
        # self.nom_individu.editTextChanged.connect(
        #     lambda: self.maj_langue_interface(True)
        # )

    def maj_langue_interface(self, parametres_aussi=True):
        """Met à jour les textes des widgets selon la langue sélectionnée."""
        langue_actuelle = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            dictionnaire=constantes.dict_langues_dispo,
            valeur=self.langue_utilisee.currentText(),
        )

        # Titres généraux
        self.setWindowTitle(self.traduire_depuis_id("titre_windows"))
        self.titre.setText(self.traduire_depuis_id(clef="titre_application"))

        self.tabs.setTabText(
            self.tabs.indexOf(self.main_tab),
            self.traduire_depuis_id(
                "titre_onglet_1",
                suffixe=(" 🎨"),
            ),
        )

        self.tabs.setTabText(
            self.tabs.indexOf(self.tab_yaml),
            self.traduire_depuis_id(
                "titre_onglet_2",
                suffixe=(" 📌"),
            ),
        )

        self.tabs.setTabText(
            self.tabs.indexOf(self.onglet_resume_pays),
            self.traduire_depuis_id(
                "titre_onglet_3",
                suffixe=(" 🧭"),
            ),
        )

        self.tabs.setTabText(
            self.tabs.indexOf(self.top_pays_visites),
            self.traduire_depuis_id(
                "titre_onglet_4",
                suffixe=(" 📊"),
            ),
        )
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.top_pays_visites),
            self.traduire_depuis_id("description_onglet_4", suffixe="."),
        )

        self.traduire_depuis_id("description_bouton_publier_cartes", suffixe=".")

        # Paramètres de l'individu
        self.groupe_params_individu.setTitle(
            self.traduire_depuis_id("titre_params_individu")
        )
        self.dossier_stockage_bouton.setText(
            self.traduire_depuis_id("dossier_stockage_individu")
            if self.dossier_stockage is None
            else os.sep.join(os.path.normpath(self.dossier_stockage).split(os.sep)[-3:])
        )
        self.label_langue.setText(
            self.traduire_depuis_id(clef="langue_individu", suffixe=" :")
        )
        self.suppression_profil.setText(self.traduire_depuis_id("supprimer_profil"))

        # Granularité des cartes
        self.groupe_granularite.setTitle(self.traduire_depuis_id("titre_granularite"))
        self.label_granularite_visite.setText(
            self.traduire_depuis_id("granularite_pays_visites", suffixe=" :")
        )
        self.label_granularite_fond.setText(
            self.traduire_depuis_id("granularite_pays_non_visites", suffixe=" :")
        )

        # Choix des cartes à publier
        self.groupe_cartes_a_creer.setTitle(
            self.traduire_depuis_id("titre_cartes_a_publier")
        )
        self.carte_pays.setText(self.traduire_depuis_id("cartes_pays_visites"))
        self.carte_monde.setText(self.traduire_depuis_id("carte_du_monde"))
        self.afrique.setText(self.traduire_depuis_id("afrique"))
        self.amerique.setText(self.traduire_depuis_id("amerique"))
        self.asie.setText(self.traduire_depuis_id("asie"))
        self.europe.setText(self.traduire_depuis_id("europe"))
        self.moyen_orient.setText(self.traduire_depuis_id("moyen_orient"))
        self.autres_regions.setText(self.traduire_depuis_id("autres_regions_monde"))
        self.publier_granu_faible.setText(
            self.traduire_depuis_id("publier_cartes_faible_granularite_uniquement")
        )
        self.publier_granu_faible.setToolTip(
            self.traduire_depuis_id(
                clef="description_publier_cartes_faible_granularite_uniquement",
                largeur_max=None,
            )
        )

        # Paramètres visuels
        self.groupe_couleurs.setTitle(
            self.traduire_depuis_id("titre_params_esthetiques")
        )
        self.color_label.setText(
            self.traduire_depuis_id(clef="cartes_couleurs", suffixe=" :")
        )
        self.theme_label.setText(
            self.traduire_depuis_id(clef="cartes_theme", suffixe=" :")
        )
        self.utiliser_theme.setText(self.traduire_depuis_id("tick_style_dans_app"))
        self.utiliser_theme.setToolTip(
            self.traduire_depuis_id("description_tick_style_dans_app", suffixe=".")
        )

        self.couleur_fond_checkbox.setText(
            self.traduire_depuis_id(clef="cartes_couleurs_fond", suffixe="")
        )
        self.couleur_fond_checkbox.setToolTip(
            self.traduire_depuis_id(clef="cartes_couleurs_fond_tool_tip", suffixe=".")
        )

        # Paramètres de format et de qualité
        self.groupe_params_publication.setTitle(
            self.traduire_depuis_id("titre_params_techniques")
        )
        self.label_format.setText(
            self.traduire_depuis_id("cartes_format", suffixe=" :")
        )
        self.label_qualite.setText(
            self.traduire_depuis_id("cartes_qualite", suffixe=" :")
        )
        self.label_qualite_max.setText(self.traduire_depuis_id("qualite_elevee"))
        self.label_qualite_min.setText(self.traduire_depuis_id("qualite_faible"))
        self.label_nb_copies_cartes.setText(
            self.traduire_depuis_id("nombre_exemplaires_cartes", suffixe=" : ")
        )
        self.label_nb_copies_cartes.setToolTip(
            self.traduire_depuis_id(
                "description_nombre_exemplaires_cartes", suffixe="."
            )
        )
        self.radio_carte_1.setText(self.traduire_depuis_id("cinq_cartes"))
        self.radio_carte_2.setText(self.traduire_depuis_id("dix_cartes"))
        self.radio_carte_3.setText(self.traduire_depuis_id("quinze_cartes"))
        self.radio_carte_sans_limite.setText(
            self.traduire_depuis_id("pas_de_limite_de_cartes")
        )

        # Boutons en bas de l'onglet 1
        self.reinit_parametres.setText(
            self.traduire_depuis_id("reinitialisation_interface")
        )
        self.reinit_parametres.setToolTip(
            self.traduire_depuis_id(
                "description_bouton_reinitialisation_interface", suffixe="."
            )
        )
        self.creation_cartes_bouton.setText(
            self.traduire_depuis_id("bouton_publier_cartes")
        )
        self.creation_cartes_bouton.setToolTip(
            self.traduire_depuis_id("description_bouton_publier_cartes", suffixe=".")
        )
        self.bouton_sauvegarde.setText(
            self.traduire_depuis_id(
                "sauvegarder_profil",
                suffixe=" 💾",
            )
        )

        # Onglet 2

        # Titre
        self.groupe_selection_lieux.setTitle(
            self.traduire_depuis_id("titre_choix_destinations_visitees")
        )
        self.avertissement_prio.setText(
            self.traduire_depuis_id("avertissement_onglet_2", prefixe="⚠️ ", suffixe=".")
        )
        self.telecharger_lieux_visites.setText("📥")
        self.telecharger_lieux_visites.setToolTip(
            self.traduire_depuis_id("telecharger_lieux_visites", suffixe=".")
        )
        self.bouton_sauvegarde2.setText("💾")

        # Chargement des YAMLs
        self.groupe_chargement_yaml.setTitle(
            self.traduire_depuis_id("titre_chargement_yamls", prefixe="... ")
        )
        self.groupe_chargement_yaml.setToolTip(
            self.traduire_depuis_id("description_titre_chargement_yamls", suffixe=".")
        )
        self.fichier_yaml_1_bouton.setText(
            self.traduire_depuis_id("yaml_regions")
            if self.fichier_yaml_1 is None
            else os.path.basename(self.chemin_fichier_yaml_1)
        )
        self.fichier_yaml_2_bouton.setText(
            self.traduire_depuis_id("yaml_departements")
            if self.fichier_yaml_2 is None
            else os.path.basename(self.chemin_fichier_yaml_2)
        )

        # Onglet 3
        self.onglet_resume_pays.set_langue(nouvelle_langue=langue_actuelle)

        # Onglet 4
        self.top_pays_visites.set_entetes(
            texte_region=self.traduire_depuis_id(
                "classement_selon_regions", prefixe="<b>", suffixe="</b>"
            ),
            texte_departement=self.traduire_depuis_id(
                "classement_selon_departements", prefixe="<b>", suffixe="</b>"
            ),
            texte_onglet_1="🗺️",
            texte_onglet_2=self.traduire_depuis_id(
                "titre_sous_onglet_4_2",
                suffixe=(" 🏆"),
            ),
        )

        self.top_pays_visites.set_langue(nouvelle_langue=langue_actuelle)

        # # Onglet 5
        self.description_application.set_description(
            self.traduire_depuis_id(
                "description_application",
                prefixe=self.traduire_depuis_id(
                    "version",
                    prefixe=self.traduire_depuis_id(
                        "sous_titre_description_application",
                        prefixe="<h2>MesVoyages – ",
                        suffixe="<br>(",
                    ),
                    suffixe=f" {constantes.version_logiciel})</h2><hr>",
                ),
                suffixe="<br>",
            )
        )

        if parametres_aussi:
            gran = constantes.parametres_traduits["granularite"][langue_actuelle]
            teintes = constantes.parametres_traduits["teintes_couleurs"].get(
                langue_actuelle, {}
            )
            themes = constantes.parametres_traduits["themes_cartes"].get(
                langue_actuelle, {}
            )

            def reset_combo(combo, items, set_index=True):
                combo.clear()
                combo.addItems(items)
                if set_index:
                    combo.setCurrentIndex(0)

            liste_granularite = [
                gran[k] for k in ["Pays", "Région", "Département", "Amusant"]
            ]
            reset_combo(self.granularite_visite, liste_granularite)
            reset_combo(self.granularite_fond, liste_granularite[:-1], set_index=False)

            liste_granularite_simple = [gran[k] for k in ["Régions", "Départements"]]
            reset_combo(self.liste_niveaux, liste_granularite_simple)

            reset_combo(self.color_combo, sorted(teintes.values()))
            reset_combo(self.theme_combo, sorted(themes.values()))

    def traduire(self, cle, langue=None, prefixe="", suffixe=""):
        if langue is None:
            langue = fonctions_utiles_2_0.obtenir_clef_par_valeur(
                dictionnaire=constantes.dict_langues_dispo,
                valeur=self.langue_utilisee.currentText(),
            )
        return (
            prefixe + self.traductions_interface.get(cle, {}).get(langue, cle) + suffixe
        )

    def traduire_depuis_id(
        self, clef, langue=None, prefixe="", suffixe="", largeur_max: int | None = None
    ):
        traduction = self.traduire(
            cle=constantes.phrases_interface.get(clef, clef),
            langue=langue,
            prefixe=prefixe,
            suffixe=suffixe,
        )
        if largeur_max is not None:
            traduction = textwrap.wrap(
                traduction,
                width=largeur_max,
                break_long_words=False,
                break_on_hyphens=False,
            )[0]

        return traduction

    def maj_style(self):
        # Récupérer la langue sélectionnée
        langue_l = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            dictionnaire=constantes.dict_langues_dispo,
            valeur=self.langue_utilisee.currentText(),
        )

        # Récupérer la couleur sélectionnée
        couleur_affichee = self.color_combo.currentText()

        # Récupérer la clé pour la teinte
        teinte_l = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            dictionnaire=constantes.parametres_traduits["teintes_couleurs"].get(
                langue_l, {}
            ),
            valeur=couleur_affichee,
        )

        # Vérifier si la teinte est valide
        if teinte_l is None:
            return  # Sortir si teinte non trouvée

        # Récupérer les données pour la teinte
        liste_teintes_temp = constantes.liste_couleurs.get(teinte_l)
        if liste_teintes_temp is None:
            return

        # Récupérer le thème sélectionné
        theme_selectionne = self.theme_combo.currentText()

        # Récupérer la clé pour le thème
        theme_l = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            dictionnaire=constantes.parametres_traduits["themes_cartes"].get(
                langue_l, {}
            ),
            valeur=theme_selectionne,
        )

        # Vérifier si le thème est valide
        if theme_l is None:
            return  # Sortir si thème non trouvé

        # Récupérer les données pour le thème
        liste_theme_temp = constantes.liste_ambiances.get(theme_l)
        if liste_theme_temp is None:
            return

        # Appliquer les styles dynamiques
        self.setStyleSheet(
            creer_graphique_1_2.utiliser_style_dynamique(
                style=(
                    0
                    if self.utiliser_theme.isChecked()
                    else int(constantes.parametres_application["interface_foncee"] + 1)
                ),
                nuances=liste_theme_temp,
                teinte=liste_teintes_temp,
                limite_essais=50,
            )
        )

    def choisir_dossier(self):
        dossier = QFileDialog.getExistingDirectory(
            self, self.traduire_depuis_id("dossier_stockage_pop_up")
        )
        if dossier:
            self.dossier_stockage = dossier  # Stocke le chemin sélectionné

    def fonction_principale(self, sauvegarder_seulement=True, pop_up=False):

        settings = {
            "name": self.nom_individu.currentText(),
            "granularity": self.granularite_visite.currentText(),
            "granularity_back": self.granularite_fond.currentText(),
            "language": fonctions_utiles_2_0.obtenir_clef_par_valeur(
                valeur=self.langue_utilisee.currentText(),
                dictionnaire=constantes.dict_langues_dispo,
            ),
            "theme": self.theme_combo.currentText(),
            "color": self.color_combo.currentText(),
            "couleur_fond_carte": self.couleur_fond_checkbox.isChecked(),
            "quality": self.curseur_qualite.value(),
            "format": self.format_cartes.currentText(),
            "results": self.dossier_stockage,
            "carte_du_monde": self.carte_monde.isChecked(),
            "europe": self.europe.isChecked(),
            "asie": self.asie.isChecked(),
            "amerique": self.amerique.isChecked(),
            "afrique": self.afrique.isChecked(),
            "moyen_orient": self.moyen_orient.isChecked(),
            "autres_regions": self.autres_regions.isChecked(),
            "publier_granu_faible": self.publier_granu_faible.isChecked(),
            "cartes_des_pays": self.carte_pays.isChecked(),
            "limite_nb_cartes": self.groupe_radio_max_cartes.checkedButton(),
            "dictionnaire_regions": (
                self.dicts_granu["region"] if self.dicts_granu["region"] != {} else None
            ),
            "dictionnaire_departements": (
                self.dicts_granu["dep"] if self.dicts_granu["dep"] != {} else None
            ),
            "format_onglet_3": self.onglet_resume_pays.mise_en_forme.isChecked(),
        }

        settings["granularity"] = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            valeur=settings["granularity"],
            dictionnaire=constantes.parametres_traduits["granularite"][
                settings["language"]
            ],
        )
        settings["granularity_back"] = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            valeur=settings["granularity_back"],
            dictionnaire=constantes.parametres_traduits["granularite"][
                settings["language"]
            ],
        )

        settings["color"] = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            valeur=settings["color"],
            dictionnaire=constantes.parametres_traduits["teintes_couleurs"][
                settings["language"]
            ],
        )

        settings["limite_nb_cartes"] = {
            self.radio_carte_1: 5,
            self.radio_carte_2: 10,
            self.radio_carte_3: 15,
        }.get(settings["limite_nb_cartes"], None)

        settings["theme"] = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            valeur=settings["theme"],
            dictionnaire=constantes.parametres_traduits["themes_cartes"][
                settings["language"]
            ],
        )

        if sauvegarder_seulement:

            # Export
            settings["name"] = settings.get("name", "")
            sauvegarde[settings["name"]] = copy.deepcopy(settings)
            if settings["name"] not in [
                self.nom_individu.itemText(i) for i in range(self.nom_individu.count())
            ]:
                self.nom_individu.addItem(settings["name"])
            with open(
                os.path.join(
                    constantes.direction_donnees_application, "sauvegarde_param.yaml"
                ),
                "w",
                encoding="utf-8",
            ) as f:
                yaml.dump(sauvegarde, f, allow_unicode=True, default_flow_style=False)

            if pop_up:
                self.montrer_popup(
                    contenu=self.traduire_depuis_id(
                        "sauvegarde_effectuee", suffixe=" !"
                    ),
                    titre=self.traduire_depuis_id("sauvegarder_profil", suffixe=""),
                    temps_max=10000,
                )

        elif self.dicts_granu["dep"] == {} and self.dicts_granu["region"] == {}:

            phrase_yaml = self.traduire_depuis_id(
                "pop_up_aucun_lieu_coche", suffixe="."
            )
            self.montrer_popup(
                contenu=phrase_yaml,
                titre=self.traduire_depuis_id("pop_up_probleme_titre", suffixe="."),
                temps_max=10000,
            )

        elif settings["results"] is None:

            self.montrer_popup(
                contenu=self.traduire_depuis_id(
                    "pop_up_pas_de_dossier_de_stockage",
                    suffixe=".",
                ),
                titre=self.traduire_depuis_id("pop_up_probleme_titre", suffixe="."),
                temps_max=10000,
            )

        else:
            # Export des paramètres
            self.fonction_principale(sauvegarder_seulement=True, pop_up=False)

            # Publication des cartes
            self.publier_cartes(settings)

    def montrer_popup(
        self,
        titre="Création des cartes",
        contenu="Début de l'opération.",
        temps_max: int | None = 5000,
        bouton_ok: bool = True,
        boutons_oui_non: bool = False,
        renvoyer_popup: bool = False,
    ):
        # Crée le message box
        msg = QMessageBox(self)
        msg.setWindowTitle(titre)
        msg.setText(contenu)
        msg.setIcon(QMessageBox.Icon.Information)

        # Configure le bouton OK et centre le message box
        if bouton_ok:
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setDefaultButton(QMessageBox.StandardButton.Ok)

        if boutons_oui_non:
            # msg.setStandardButtons(
            #     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            # )
            msg.addButton(
                self.traduire_depuis_id(clef="oui"), QMessageBox.ButtonRole.YesRole
            )
            msg.addButton(
                self.traduire_depuis_id(clef="non"), QMessageBox.ButtonRole.NoRole
            )
            msg.setIcon(QMessageBox.Icon.Question)

        # Timer pour fermer le message box après 3 secondes (3000 ms)
        if temps_max is not None and not boutons_oui_non:
            QTimer.singleShot(max(3000, temps_max), msg.close)

        if renvoyer_popup == False:
            msg.exec()  # Affiche le message box
        else:
            return msg

    def publier_cartes(self, settings):
        # Logique de traitement avec les paramètres validés

        # Ganularite
        granularite = {"Pays": 0, "Région": 1, "Département": 2}.get(
            settings.get("granularity"), -1
        )

        granularite_fond = {"Pays": 0, "Région": 1}.get(
            settings.get("granularity_back"), 2
        )

        # Gestion des régions du monde
        liste_regions_temp = {}

        mo = "Middle East"
        if settings["moyen_orient"] == True:
            liste_regions_temp[mo] = constantes.liste_regions_monde[mo]

        euro = "Europe"
        if settings["europe"] == True:
            liste_regions_temp[euro] = constantes.liste_regions_monde[euro]

        amsud = "South America"
        amnord = "North America"
        if settings["amerique"] == True:
            liste_regions_temp[amsud] = constantes.liste_regions_monde[amsud]
            liste_regions_temp[amnord] = constantes.liste_regions_monde[amnord]

        afr = "Africa"
        if settings["afrique"] == True:
            liste_regions_temp[afr] = constantes.liste_regions_monde[afr]

        asie = "Asia"
        if settings["asie"] == True:
            liste_regions_temp[asie] = constantes.liste_regions_monde[asie]

        if settings["autres_regions"] == True:
            liste_regions_temp.update(
                {
                    k: v
                    for k, v in constantes.liste_regions_monde.items()
                    if k not in [euro, asie, afr, amsud, amnord, mo]
                }
            )

        dict_regions = settings["dictionnaire_regions"]
        if settings["dictionnaire_departements"] is not None:
            if settings["dictionnaire_departements"] != {} and dict_regions is not None:
                dict_regions = {
                    k: v
                    for k, v in settings["dictionnaire_regions"].items()
                    if k not in settings["dictionnaire_departements"]
                }

        if settings["dictionnaire_departements"] == {}:
            settings["dictionnaire_departements"] = None
        if dict_regions == {}:
            dict_regions = None

        nb_total_graphes = (
            (
                (len(list(dict_regions.keys())) if dict_regions is not None else 0)
                + (
                    len(list(settings["dictionnaire_departements"].keys()))
                    if settings["dictionnaire_departements"] is not None
                    else 0
                )
            )
            * settings["cartes_des_pays"]
            * (granularite != 0)
            + len(liste_regions_temp)
            + int(settings["carte_du_monde"])
        )

        self.barre_progression.setMaximum(nb_total_graphes)
        self.barre_progression.setValue(0)
        self.nb_total_graphes = nb_total_graphes
        self.graphique_i = 0

        self.debut_fin_creation_cartes(debut=True)

        parametres = {
            "liste_dfs": liste_gdfs,
            "liste_dicts": [dict_regions, settings["dictionnaire_departements"]],
            "gdf_eau": constantes.gdf_lacs,
            "noms_pays": constantes.pays_differentes_langues,
            "dictionnaire_pays_unis": constantes.liste_pays_groupes,
            "nom_indiv": settings["name"],
            "direction_resultat": settings["results"],
            "langue": settings["language"],
            "granularite_visite": granularite,
            "granularite_reste": granularite_fond,
            "theme": constantes.liste_ambiances[settings["theme"]],
            "teinte": constantes.liste_couleurs[settings["color"]],
            "couleur_fond": "#CDEAF7" if settings["couleur_fond_carte"] else "#FFFFFF",
            "couleur_non_visites": "#ECEBED",
            "couleur_lacs": "#CEE3F5",
            "format": settings["format"],
            "qualite": settings["quality"],
            "carte_du_monde": settings["carte_du_monde"],
            "liste_regions": liste_regions_temp,
            "pays_individuel": settings["cartes_des_pays"],
            "max_cartes_additionnelles": settings["limite_nb_cartes"],
            "sortir_cartes_granu_inf": settings["publier_granu_faible"],
        }

        self.thread_temp = QThread()
        self.worker = onglet_1.CreerCartes(parametres)
        self.worker.moveToThread(self.thread_temp)

        self.worker.tracker_signal.connect(self.afficher_avancement)
        self.worker.finished.connect(self.thread_temp.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread_temp.finished.connect(self.thread_temp.deleteLater)
        self.thread_temp.finished.connect(
            lambda: self.debut_fin_creation_cartes(debut=False)
        )

        self.thread_temp.started.connect(self.worker.run)
        self.thread_temp.start()

    def afficher_avancement(self, libelle_pays):
        self.graphique_i = self.graphique_i + 1
        self.barre_progression.setValue(self.graphique_i)
        self.barre_progression.setFormat(
            f"{self.graphique_i}/{self.nb_total_graphes} : {libelle_pays}"
        )

    def debut_fin_creation_cartes(self, debut):

        self.barre_progression.setVisible(debut)
        self.creation_cartes_bouton.setVisible(not debut)

        self.montrer_popup(
            contenu=self.traduire_depuis_id(
                clef=(
                    "debut_publication_cartes"
                    if debut
                    else "publication_cartes_reussie"
                ),
                suffixe="." if debut else " ✅​",
            ),
            temps_max=5000 if debut else None,
            titre=self.traduire_depuis_id(clef="titre_pop_up_publication_cartes"),
        )

    def charger_yaml(self, num):
        chemin_yaml, _ = QFileDialog.getOpenFileName(
            self,
            self.traduire_depuis_id("pop_up_yaml"),
            "",
            "YAML Files (*.yaml *.yml)",
        )
        if chemin_yaml:
            with open(chemin_yaml, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if num == 1:
                    self.chemin_fichier_yaml_1 = chemin_yaml
                    self.fichier_yaml_1 = data  # Stocke les données du YAML 1
                    self.dicts_granu["region"] = data

                else:
                    self.chemin_fichier_yaml_2 = chemin_yaml
                    self.fichier_yaml_2 = data  # Stocke les données du YAML 2
                    self.dicts_granu["dep"] = data

    def initialiser_sauvegarde(self, sauvegarde_complete):

        nom_individu_actuel = self.nom_individu.currentText()
        sauv = sauvegarde_complete.get(nom_individu_actuel, {})

        # Nom
        if sauv.get("name") is not None:

            # Dossier de publication
            if sauv.get("results") is not None:
                self.dossier_stockage = sauv.get("results")

            # Langue
            if sauv.get("language") is not None:
                self.langue_utilisee.setCurrentText(
                    constantes.dict_langues_dispo[sauv.get("language")]
                )
                self.top_pays_visites.set_langue(nouvelle_langue=sauv.get("language"))

            # Cartes à publier
            checkboxes = {
                "carte_du_monde": self.carte_monde,
                "cartes_des_pays": self.carte_pays,
                "asie": self.asie,
                "amerique": self.amerique,
                "afrique": self.afrique,
                "europe": self.europe,
                "moyen_orient": self.moyen_orient,
                "autres_regions": self.autres_regions,
                "publier_granu_faible": self.publier_granu_faible,
            }
            for nom_cle, checkbox in checkboxes.items():
                if sauv.get(nom_cle) is not None:
                    checkbox.setChecked(sauv.get(nom_cle))

            # Qualité
            if sauv.get("quality") is not None:
                self.curseur_qualite.setValue(sauv.get("quality"))

            # Format
            if sauv.get("format") is not None:
                self.format_cartes.setCurrentText(sauv.get("format"))

            if sauv.get("dictionnaire_regions") is not None:
                self.dicts_granu["region"] = sauv.get("dictionnaire_regions")
            else:
                self.dicts_granu["region"] = {}
            if sauv.get("dictionnaire_departements") is not None:
                self.dicts_granu["dep"] = sauv.get("dictionnaire_departements")
            else:
                self.dicts_granu["dep"] = {}

            if sauv.get("limite_nb_cartes") is not None:
                if sauv.get("limite_nb_cartes") == 5:
                    self.radio_carte_1.setChecked(True)
                elif sauv.get("limite_nb_cartes") == 10:
                    self.radio_carte_2.setChecked(True)
                elif sauv.get("limite_nb_cartes") == 15:
                    self.radio_carte_3.setChecked(True)
                else:
                    self.radio_carte_sans_limite.setChecked(True)

            if sauv.get("format_onglet_3") is not None:
                self.onglet_resume_pays.mise_en_forme.setChecked(
                    sauv.get("format_onglet_3")
                )

            if sauv.get("couleur_fond_carte") is not None:
                self.couleur_fond_checkbox.setChecked(sauv.get("couleur_fond_carte"))

            self.maj_liste_reg_dep_pays()
            self.top_pays_visites.set_dicts_granu(dict_nv=self.dicts_granu)
            self.onglet_resume_pays.set_dicts_granu(dict_nv=self.dicts_granu)

    def reinitialisation_parametres(self, nom_aussi=True):

        # Paramètres individuels
        if nom_aussi == True:
            self.nom_individu.setCurrentText("")

            self.nom_individu.blockSignals(True)
            self.nom_individu.setCurrentIndex(-1)
            self.nom_individu.blockSignals(False)

        self.liste_niveaux.blockSignals(True)
        self.dicts_granu = {"region": {}, "dep": {}}
        self.maj_liste_reg_dep_pays()

        self.liste_niveaux.blockSignals(False)

        self.dossier_stockage = None
        self.radio_carte_2.setChecked(True)
        self.langue_utilisee.setCurrentIndex(0)

        # Fichiers YAML
        self.chemin_fichier_yaml_1 = None
        self.fichier_yaml_1 = None
        self.chemin_fichier_yaml_2 = None
        self.fichier_yaml_2 = None

        # Paramètres de publication
        self.curseur_qualite.setValue(
            int(
                (
                    constantes.parametres_application["qualite_min"]
                    + constantes.parametres_application["qualite_max"]
                )
                / 2
            )
        )
        self.format_cartes.setCurrentText("png")
        self.couleur_fond_checkbox.setChecked(False)

        # Cartes à créer
        self.carte_monde.setChecked(False)
        self.carte_pays.setChecked(True)
        self.asie.setChecked(False)
        self.amerique.setChecked(False)
        self.afrique.setChecked(False)
        self.europe.setChecked(True)
        self.moyen_orient.setChecked(False)
        self.autres_regions.setChecked(False)
        self.publier_granu_faible.setChecked(False)

        self.utiliser_theme.setChecked(False)
        self.onglet_resume_pays.mise_en_forme.setChecked(False)
        self.onglet_resume_pays.set_dicts_granu(dict_nv=self.dicts_granu)
        self.top_pays_visites.set_dicts_granu(dict_nv=self.dicts_granu)

    def maj_liste_reg_dep_pays(self):

        langue_l = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            dictionnaire=constantes.dict_langues_dispo,
            valeur=self.langue_utilisee.currentText(),
        )

        pays_i = self.liste_des_pays.currentText()
        niveau_i = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            valeur=self.liste_niveaux.currentText(),
            dictionnaire=constantes.parametres_traduits["granularite"][langue_l],
        )

        self.liste_endroits.blockSignals(
            True
        )  # ⚠️ Empêche les signaux pendant le remplissage
        self.liste_endroits.clear()

        if niveau_i == "Régions":
            liste_end = constantes.regions_par_pays.get(pays_i, [])
        elif niveau_i == "Départements":
            liste_end = constantes.departements_par_pays.get(pays_i, [])
        else:
            liste_end = []

        for item in liste_end:
            liste_item = QListWidgetItem(item)
            liste_item.setFlags(liste_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)

            # Si déjà sélectionné dans le dict, on coche
            clef = "region" if niveau_i == "Régions" else "dep"
            est_coche = item in self.dicts_granu.get(clef, {}).get(pays_i, [])
            liste_item.setCheckState(
                Qt.CheckState.Checked if est_coche else Qt.CheckState.Unchecked
            )
            self.liste_endroits.addItem(liste_item)

        self.liste_endroits.blockSignals(False)

        # Connecte le signal (une seule fois idéalement)
        try:
            self.liste_endroits.itemChanged.disconnect()
        except TypeError:
            pass
        self.liste_endroits.itemChanged.connect(self.changer_item_liste_pays)

    def changer_item_liste_pays(self, item):
        langue_l = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            dictionnaire=constantes.dict_langues_dispo,
            valeur=self.langue_utilisee.currentText(),
        )

        pays_i = self.liste_des_pays.currentText()
        niveau_i = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            valeur=self.liste_niveaux.currentText(),
            dictionnaire=constantes.parametres_traduits["granularite"][langue_l],
        )
        texte = item.text()

        # Détermine la clé du dictionnaire selon le niveau
        clef = "region" if niveau_i == "Régions" else "dep"

        # Initialise le dictionnaire pour le pays s’il n’existe pas
        if pays_i not in self.dicts_granu[clef]:
            self.dicts_granu[clef][pays_i] = []

        # Ajoute ou retire l’élément selon son état
        if item.checkState() == Qt.CheckState.Checked:
            if texte not in self.dicts_granu[clef][pays_i]:
                self.dicts_granu[clef][pays_i].append(texte)
                self.dicts_granu[clef][pays_i].sort()
                self.dicts_granu[clef] = {
                    pays: self.dicts_granu[clef][pays]
                    for pays in sorted(self.dicts_granu[clef])
                }
        else:
            if texte in self.dicts_granu[clef][pays_i]:
                self.dicts_granu[clef][pays_i].remove(texte)
                if self.dicts_granu[clef][pays_i] == []:
                    del self.dicts_granu[clef][pays_i]

        self.onglet_resume_pays.set_dicts_granu(dict_nv=self.dicts_granu)
        self.top_pays_visites.set_dicts_granu(dict_nv=self.dicts_granu)

    def supprimer_clef(self, clef):
        global sauvegarde

        # Pop-up afin de s'assurer de la décision
        message = self.montrer_popup(
            titre=self.traduire_depuis_id(clef="titre_pop_up_suppression"),
            contenu=self.traduire_depuis_id(
                clef="contenu_pop_up_suppression", suffixe="."
            ),
            temps_max=None,
            bouton_ok=False,
            boutons_oui_non=True,
            renvoyer_popup=True,
        )
        message = message.exec()

        if message != 2:
            return

        # Suppression de l'individu
        if clef in sauvegarde:
            del sauvegarde[clef]

            # Mise à jour de la liste déroulante
            self.nom_individu.clear()
            self.nom_individu.addItems(list(sauvegarde.keys()))

            # sauvegarde
            with open(
                os.path.join(
                    constantes.direction_donnees_application, "sauvegarde_param.yaml"
                ),
                "w",
                encoding="utf-8",
            ) as f:
                yaml.dump(sauvegarde, f, allow_unicode=True, default_flow_style=False)

            # Réinitialisation des paramètres
            self.reinitialisation_parametres(True)
            self.dicts_granu = {"region": {}, "dep": {}}
            self.maj_langue_interface(True)

    def exporter_yamls_visites(self):

        if self.dossier_stockage is None:

            self.montrer_popup(
                contenu=self.traduire_depuis_id(
                    "pop_up_pas_de_dossier_de_stockage",
                    suffixe=".",
                ),
                titre=self.traduire_depuis_id("pop_up_probleme_titre", suffixe="."),
                temps_max=10000,
            )

        else:

            langue_actuelle = fonctions_utiles_2_0.obtenir_clef_par_valeur(
                dictionnaire=constantes.dict_langues_dispo,
                valeur=self.langue_utilisee.currentText(),
            )
            gran = constantes.parametres_traduits["granularite"][langue_actuelle]

            nom = self.nom_individu.currentText()
            if nom is None:
                nom = ""

            nom_yaml_regions = f"{nom}{' – ' if nom != '' else nom}{self.traduire_depuis_id(clef='granularite_pays_visites')} – {gran['Régions']}.yaml"
            nom_yaml_departements = f"{nom}{' – ' if nom != '' else nom}{self.traduire_depuis_id(clef='granularite_pays_visites')} – {gran['Départements']}.yaml"

            try:

                # Export des régions
                with open(
                    os.path.join(self.dossier_stockage, nom_yaml_regions),
                    "w",
                    encoding="utf-8",
                ) as f:
                    yaml.dump(
                        self.dicts_granu["region"],
                        f,
                        allow_unicode=True,
                        default_flow_style=False,
                    )
                # Export des départements
                with open(
                    os.path.join(self.dossier_stockage, nom_yaml_departements),
                    "w",
                    encoding="utf-8",
                ) as f:
                    yaml.dump(
                        self.dicts_granu["dep"],
                        f,
                        allow_unicode=True,
                        default_flow_style=False,
                    )

                self.telecharger_lieux_visites.setText("📥✅")
                QTimer.singleShot(
                    3000, lambda: self.telecharger_lieux_visites.setText("📥")
                )

            except:

                self.montrer_popup(
                    titre=self.traduire_depuis_id("pop_up_probleme_titre", suffixe="."),
                    contenu=self.traduire_depuis_id(
                        "export_pas_fonctionnel",
                        suffixe=".",
                    ),
                    temps_max=10000,
                )


if __name__ == "__main__":

    # Lancement de l'application
    app = QApplication(sys.argv)

    # Import des bases de données contenant les cartes
    liste_gdfs = []
    for i in range(3):
        with open(
            os.path.join(
                constantes.direction_donnees_pickle, f"carte_monde_niveau_{i}.pkl"
            ),
            "rb",
        ) as f:
            gdf_niveau_i = pickle.load(f)
        liste_gdfs.append(gdf_niveau_i)

    window = SettingsApp()
    window.show()

    sys.exit(app.exec())
