import os
import sys

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yaml
import copy
import pickle
import textwrap
import warnings
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
    QFrame,
    QButtonGroup,
    QRadioButton,
    QTabWidget,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QProgressBar,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QTimer, QSize, QObject, pyqtSignal, QThread

import constantes
from production_cartes import creer_carte_1_1, creer_graphique_1_2, carte_main_1_3
from application import fonctions_utiles_2_0

warnings.filterwarnings("ignore")

# Paramères
## Paramètres d'interface
interface_foncee = True
inclure_emojis_onglets = True
inclure_emojis = True
top_n_pays = None
affichage_groupe = False

## Paramètres des cartes
qualite_min = 200
qualite_max = 4000


# Import dela sauvegarde
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

bouton_de_suppression = f"""
                QPushButton {{
                    background-color:{"#000000" if interface_foncee else "#f8d7da"};
                    color: {"#E6E6E6" if interface_foncee else "#2C2C2C"};
                    font-size: 12px;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                }}
                QPushButton:hover {{
                    background-color: {"#85040d" if interface_foncee else "#f5c6cb"};
                }}
            """


class TrackerPays(QObject):
    tracker_pays_en_cours = pyqtSignal(str)

    def notify(self, libelle_pays: str):
        self.tracker_pays_en_cours.emit(libelle_pays)


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


class CreerClassementPays(QObject):

    resultat = pyqtSignal(object)
    erreur = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, granularite, top_n, liste_dicts):
        super().__init__()
        self.granularite = granularite
        self.top_n = top_n
        self.liste_dicts = liste_dicts

    def run(self):
        try:
            gdf = creer_carte_1_1.cree_base_toutes_granularites(
                liste_dfs=liste_gdfs,
                liste_dicts=self.liste_dicts,
                granularite_objectif=self.granularite,
            )

            classement = fonctions_utiles_2_0.creer_classement_pays(
                gdf,
                constantes.table_superficie,
                granularite=self.granularite,
                top_n=self.top_n,
            )
            self.resultat.emit(classement)

        except Exception as e:
            self.erreur.emit(str(e))

        finally:
            self.finished.emit()


class SettingsApp(QWidget):
    def __init__(self):
        super().__init__()

        self.traductions_interface = constantes.outil_differentes_langues

        self.setWindowTitle("Cartes de voyage")
        self.setGeometry(300, 40, 800, 300)
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
        self.langue_utilisee = QComboBox()
        self.langue_utilisee.addItems(liste_langues_dispo_joli)
        layout_params_individu.addWidget(self.label_langue)
        layout_params_individu.addWidget(self.langue_utilisee)
        self.langue_utilisee.currentIndexChanged.connect(
            lambda: self.maj_langue_interface(True)
        )

        # Ajouter une barre verticale
        ligne_verticale = QFrame()
        ligne_verticale.setFrameShape(QFrame.Shape.VLine)
        ligne_verticale.setFrameShadow(QFrame.Shadow.Raised)
        layout_params_individu.addWidget(ligne_verticale)

        # Ajout de la possibilité de supprimer un profil
        self.suppression_profil = QPushButton()
        self.suppression_profil.clicked.connect(
            lambda: self.supprimer_clef(self.nom_individu.currentText())
        )
        self.suppression_profil.setStyleSheet(bouton_de_suppression)
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
        self.granularite_visite = QComboBox()
        self.label_granularite_visite = QLabel()
        layout_granularite_visite = QHBoxLayout()
        layout_granularite_visite.addWidget(self.label_granularite_visite)
        layout_granularite_visite.addWidget(self.granularite_visite)

        ligne_verticale_granu = QFrame()
        ligne_verticale_granu.setFrameShape(QFrame.Shape.VLine)
        ligne_verticale_granu.setFrameShadow(QFrame.Shadow.Raised)
        layout_granularite_visite.addWidget(ligne_verticale_granu)

        # Granularité de fond
        self.granularite_fond = QComboBox()
        self.label_granularite_fond = QLabel()
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

        ligne = QFrame()
        ligne.setFrameShape(QFrame.Shape.HLine)
        ligne.setFrameShadow(QFrame.Shadow.Sunken)
        ligne.setLineWidth(1)
        layout_cartes_a_creer.addWidget(ligne, 1, 0, 1, 6)

        ligne_regions_1 = 2
        layout_cartes_a_creer.addWidget(self.afrique, ligne_regions_1, 0, 1, 2)
        layout_cartes_a_creer.addWidget(self.amerique, ligne_regions_1, 2, 1, 2)
        layout_cartes_a_creer.addWidget(self.asie, ligne_regions_1, 4, 1, 2)

        ligne_regions_1 = 3
        layout_cartes_a_creer.addWidget(self.europe, ligne_regions_1, 0, 1, 2)
        layout_cartes_a_creer.addWidget(self.moyen_orient, ligne_regions_1, 2, 1, 2)
        layout_cartes_a_creer.addWidget(self.autres_regions, ligne_regions_1, 4, 1, 2)

        ligne2 = QFrame()
        ligne2.setFrameShape(QFrame.Shape.HLine)
        ligne2.setFrameShadow(QFrame.Shadow.Sunken)
        ligne2.setLineWidth(1)
        layout_cartes_a_creer.addWidget(ligne2, 4, 0, 1, 6)

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
        layout.addWidget(self.groupe_cartes_a_creer)

        # Boîte des couleurs
        self.groupe_couleurs = QGroupBox()
        layout_theme_color = QVBoxLayout()

        # Choix du thème
        layout_theme = QHBoxLayout()
        self.theme_label = QLabel()
        self.theme_combo = QComboBox()
        layout_theme.addWidget(self.theme_label)
        layout_theme.addWidget(self.theme_combo)
        self.theme_combo.currentTextChanged.connect(self.maj_style)

        # Choix des couleurs
        layout_couleurs = QHBoxLayout()
        self.color_label = QLabel()
        self.color_combo = QComboBox()
        layout_couleurs.addWidget(self.color_label)
        layout_couleurs.addWidget(self.color_combo)
        self.color_combo.currentTextChanged.connect(self.maj_style)

        # Utilisation ou non du thème dans l'interface
        self.utiliser_theme = QCheckBox()
        self.utiliser_theme.stateChanged.connect(self.maj_style)

        # Ajout des widgets au layout vertical
        layout_theme_color.addLayout(layout_theme)
        layout_theme_color.addLayout(layout_couleurs)
        layout_theme_color.addWidget(self.utiliser_theme)

        # Ajout du layout de couleurs au groupbox et ajout du groupbox au layout principal
        self.groupe_couleurs.setLayout(layout_theme_color)

        # Ajout des groupbox des cartes et des couleurs
        layout_cartes_et_couleurs.addWidget(self.groupe_cartes_a_creer)
        layout_cartes_et_couleurs.addWidget(self.groupe_couleurs)

        # Ajouter ce layout horizontal au layout principal
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
        self.curseur_qualite.setMinimum(qualite_min)
        self.curseur_qualite.setMaximum(qualite_max)
        self.curseur_qualite.setValue(int((qualite_min + qualite_max) / 2))

        # Choix du format d'image
        self.label_format = QLabel()
        self.format_cartes = QComboBox()
        self.format_cartes.addItems(["png", "jpg", "svg", "pdf", "tif", "webp"])

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
            lambda: self.fonction_principale(False)
        )
        self.barre_progression = QProgressBar()
        self.barre_progression.setMinimum(0)
        self.barre_progression.setValue(0)
        self.barre_progression.setFormat("")

        # Bouton de sauvegarde
        self.bouton_sauvegarde = QPushButton()
        self.bouton_sauvegarde.clicked.connect(lambda: self.fonction_principale(True))

        # Bouton de réinitialisation
        self.reinit_parametres = QPushButton()
        self.reinit_parametres.clicked.connect(
            lambda: self.reinitialisation_parametres(True)
        )
        self.reinit_parametres.clicked.connect(lambda: self.maj_langue_interface(True))
        self.reinit_parametres.setStyleSheet(bouton_de_suppression)

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
        self.tab_resume_pays = QWidget()
        self.tabs.addTab(self.tab_resume_pays, "Liste des lieux visités")

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
        self.liste_endroits.setGridSize(QSize(280, 25))

        self.dicts_granu = {"region": {}, "dep": {}}

        # Remplir les déroulés
        self.liste_des_pays.addItems(constantes.regions_par_pays.keys())

        self.liste_des_pays.currentTextChanged.connect(self.maj_liste_reg_dep_pays)
        self.liste_niveaux.currentTextChanged.connect(self.maj_liste_reg_dep_pays)
        self.liste_endroits.itemChanged.connect(self.changer_item_liste_pays)

        layout_selection_params = QHBoxLayout()
        layout_selection_params.addWidget(self.liste_des_pays)
        layout_selection_params.addWidget(self.liste_niveaux)

        layout_selection_lieux.addLayout(layout_selection_params)
        layout_selection_lieux.addWidget(self.avertissement_prio)
        layout_selection_lieux.addWidget(self.liste_endroits)
        self.groupe_selection_lieux.setLayout(layout_selection_lieux)

        layout_yaml.addWidget(self.groupe_selection_lieux)
        layout_yaml.addWidget(self.groupe_chargement_yaml)

        self.tab_yaml.setLayout(layout_yaml)

        # Troisième onglet
        self.layout_resume_pays = QHBoxLayout()

        # Pour les régions
        self.layout_resume_regions = QVBoxLayout()
        self.widget_regions = QWidget()
        self.widget_regions.setLayout(self.layout_resume_regions)

        self.scroll_regions = QScrollArea()
        self.scroll_regions.setWidgetResizable(True)
        self.scroll_regions.setWidget(self.widget_regions)

        # Pour les départements
        self.layout_resume_departements = QVBoxLayout()
        self.widget_departements = QWidget()
        self.widget_departements.setLayout(self.layout_resume_departements)

        self.scroll_departements = QScrollArea()
        self.scroll_departements.setWidgetResizable(True)
        self.scroll_departements.setWidget(self.widget_departements)

        # Ajouter les deux scrolls à la ligne principale
        self.layout_resume_pays.addWidget(self.scroll_regions)
        self.layout_resume_pays.addWidget(self.scroll_departements)
        self.tab_resume_pays.setLayout(self.layout_resume_pays)

        # Quatrième obglet
        self.top_pays_visites = QWidget()
        self.tabs.addTab(self.top_pays_visites, "Pays les plus visités")
        self.layout_top_pays = QHBoxLayout()

        # Top pays par région
        self.layout_entete_top_pays_regions = QVBoxLayout()
        self.entete_top_pays_regions = QLabel()
        self.entete_top_pays_regions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_entete_top_pays_regions.addWidget(self.entete_top_pays_regions)
        ligne = QFrame()
        ligne.setFrameShape(QFrame.Shape.HLine)
        ligne.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout_entete_top_pays_regions.addWidget(ligne)
        self.layout_entete_top_pays_regions.addWidget(QLabel(""))
        self.layout_top_pays_regions = QGridLayout()
        self.widget_top_pays_regions = QWidget()
        self.layout_entete_top_pays_regions.addLayout(self.layout_top_pays_regions)
        self.layout_entete_top_pays_regions.addStretch()
        self.widget_top_pays_regions.setLayout(self.layout_entete_top_pays_regions)

        self.scroll_top_pays_regions = QScrollArea()
        self.scroll_top_pays_regions.setWidgetResizable(True)
        self.scroll_top_pays_regions.setWidget(self.widget_top_pays_regions)

        # Top pays par département
        self.layout_entete_top_pays_departements = QVBoxLayout()
        self.entete_top_pays_departements = QLabel()
        self.entete_top_pays_departements.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_entete_top_pays_departements.addWidget(
            self.entete_top_pays_departements
        )
        ligne = QFrame()
        ligne.setFrameShape(QFrame.Shape.HLine)
        ligne.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout_entete_top_pays_departements.addWidget(ligne)
        self.layout_entete_top_pays_departements.addWidget(QLabel(""))
        self.layout_top_pays_deps = QGridLayout()
        self.widget_top_pays_deps = QWidget()
        self.layout_entete_top_pays_departements.addLayout(self.layout_top_pays_deps)
        self.layout_entete_top_pays_departements.addStretch()
        self.widget_top_pays_deps.setLayout(self.layout_entete_top_pays_departements)

        self.scroll_top_pays_deps = QScrollArea()
        self.scroll_top_pays_deps.setWidgetResizable(True)
        self.scroll_top_pays_deps.setWidget(self.widget_top_pays_deps)

        # Ajout des classements à l'application
        self.layout_top_pays.addWidget(self.scroll_top_pays_regions)
        self.layout_top_pays.addWidget(self.scroll_top_pays_deps)
        self.top_pays_visites.setLayout(self.layout_top_pays)

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
        self.nom_individu.editTextChanged.connect(
            lambda: self.initialiser_sauvegarde(sauvegarde)
        )

        self.nom_individu.editTextChanged.connect(
            lambda: self.maj_langue_interface(True)
        )
        self.nom_individu.currentIndexChanged.connect(
            lambda: self.maj_langue_interface(True)
        )

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
                "titre_onglet_1", suffixe=" 🎨" if inclure_emojis_onglets else ""
            ),
        )

        self.tabs.setTabText(
            self.tabs.indexOf(self.tab_yaml),
            self.traduire_depuis_id(
                "titre_onglet_2",
                suffixe=" 📌" if inclure_emojis_onglets else "",
            ),
        )

        self.tabs.setTabText(
            self.tabs.indexOf(self.tab_resume_pays),
            self.traduire_depuis_id(
                "titre_onglet_3",
                suffixe=" 🧭" if inclure_emojis_onglets else "",
            ),
        )

        self.tabs.setTabText(
            self.tabs.indexOf(self.top_pays_visites),
            self.traduire_depuis_id(
                "titre_onglet_4",
                suffixe=" 🏆" if inclure_emojis_onglets else "",
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
            self.traduire_depuis_id("granularite_pays_visites", suffixe="\u00a0:")
        )
        self.label_granularite_fond.setText(
            self.traduire_depuis_id("granularite_pays_non_visites", suffixe="\u00a0:")
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
            self.traduire_depuis_id(clef="cartes_couleurs", suffixe=" :")
        )
        self.theme_label.setText(
            self.traduire_depuis_id(clef="cartes_theme", suffixe=" :")
        )
        self.utiliser_theme.setText(self.traduire_depuis_id("tick_style_dans_app"))
        self.utiliser_theme.setToolTip(
            self.traduire_depuis_id("description_tick_style_dans_app", suffixe=".")
        )

        # Paramètres de format et de qualité
        self.groupe_params_publication.setTitle(
            self.traduire_depuis_id("titre_params_techniques")
        )
        self.label_format.setText(
            self.traduire_depuis_id("cartes_format", suffixe=" :")
        )
        self.label_qualite.setText(
            self.traduire_depuis_id("cartes_qualite", suffixe=" :")
        )
        self.label_qualite_max.setText(self.traduire_depuis_id("qualite_elevee"))
        self.label_qualite_min.setText(self.traduire_depuis_id("qualite_faible"))
        self.label_nb_copies_cartes.setText(
            self.traduire_depuis_id("nombre_exemplaires_cartes", suffixe="\u00a0: ")
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
                suffixe=" 💾" if inclure_emojis else "",
            )
        )

        # Onlet 2

        # Titre
        self.groupe_selection_lieux.setTitle(
            self.traduire_depuis_id("titre_choix_destinations_visitees")
        )
        self.avertissement_prio.setText(
            self.traduire_depuis_id(
                "avertissement_onglet_2", prefixe="⚠️\u00a0", suffixe="."
            )
        )

        # Chargement des YAMLs
        self.groupe_chargement_yaml.setTitle(
            self.traduire_depuis_id("titre_chargement_yamls", prefixe="...\u00a0")
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

        # Onglet 4
        self.entete_top_pays_regions.setText(
            self.traduire_depuis_id(
                "classement_selon_regions", prefixe="<b>", suffixe="</b>"
            )
        )
        self.entete_top_pays_departements.setText(
            self.traduire_depuis_id(
                "classement_selon_departements", prefixe="<b>", suffixe="</b>"
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

        self.maj_layout_resume(affichage_groupe=affichage_groupe)

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
        self.utiliser_style_dynamique(
            nuances=liste_theme_temp,
            teinte=liste_teintes_temp,
        )

    def utiliser_style_dynamique(
        self,
        teinte=[i / 360 for i in range(0, 360, 45)],
        nuances={
            "min_luminosite": 0.8,
            "max_luminosite": 0.95,
            "min_saturation": 0.2,
            "max_saturation": 0.4,
        },
    ):

        if self.utiliser_theme.isChecked() == True:

            couleur_widget = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )
            couleur_widget_texte = creer_graphique_1_2.transformer_couleur_texte(
                couleur_widget
            )

            couleur_push = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )
            couleur_push_texte = creer_graphique_1_2.transformer_couleur_texte(
                couleur_push
            )

            couleur_push2 = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )
            couleur_push2_texte = creer_graphique_1_2.transformer_couleur_texte(
                couleur_push2
            )

            couleur_slider = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )
            couleur_slider2 = couleur_slider * 1

            compteur_barre = 0
            while compteur_barre < 20 and couleur_slider2 == couleur_slider:
                couleur_slider2 = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                    preset=nuances, teintes_autorisees=teinte
                )
                compteur_barre = compteur_barre + 1

            couleur_box = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )
            couleur_box_texte = creer_graphique_1_2.transformer_couleur_texte(
                couleur_box
            )
            couleur_box_bord = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )

            couleur_line = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )
            couleur_line_texte = creer_graphique_1_2.transformer_couleur_texte(
                couleur_line
            )
            couleur_line_bord = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )

            couleur_groupbox = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )

            onglet_selection = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )
            onglet_selection_texte = creer_graphique_1_2.transformer_couleur_texte(
                onglet_selection
            )

            onglet_fond = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )
            onglet_texte = creer_graphique_1_2.transformer_couleur_texte(onglet_fond)
            onglet_survol = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )

            couleur_scroll_area_barre = (
                creer_graphique_1_2.generer_couleur_aleatoire_hex(
                    preset=nuances, teintes_autorisees=teinte
                )
            )
            couleur_scroll_area_barre_survol = (
                creer_graphique_1_2.generer_couleur_aleatoire_hex(
                    preset=nuances, teintes_autorisees=teinte
                )
            )
            couleur_scroll_area_fond = (
                creer_graphique_1_2.generer_couleur_aleatoire_hex(
                    preset=nuances, teintes_autorisees=teinte
                )
            )
            couleur_scroll_area_texte = creer_graphique_1_2.transformer_couleur_texte(
                couleur_scroll_area_fond
            )
            couleur_scroll_area_barre_partie = (
                creer_graphique_1_2.generer_couleur_aleatoire_hex(
                    preset=nuances, teintes_autorisees=teinte
                )
            )
            couleur_scroll_area_bord = (
                creer_graphique_1_2.generer_couleur_aleatoire_hex(
                    preset=nuances, teintes_autorisees=teinte
                )
            )

            couleur_widget_list_fond = (
                creer_graphique_1_2.generer_couleur_aleatoire_hex(
                    preset=nuances, teintes_autorisees=teinte
                )
            )
            couleur_widget_list_texte = creer_graphique_1_2.transformer_couleur_texte(
                couleur_widget_list_fond
            )
            couleur_widget_list_select = (
                creer_graphique_1_2.generer_couleur_aleatoire_hex(
                    preset=nuances, teintes_autorisees=teinte
                )
            )
            couleur_widget_list_select_texte = (
                creer_graphique_1_2.transformer_couleur_texte(
                    couleur_widget_list_select
                )
            )
            couleur_widget_list_survol_fond = (
                creer_graphique_1_2.generer_couleur_aleatoire_hex(
                    preset=nuances, teintes_autorisees=teinte
                )
            )
            couleur_widget_list_survol_texte = (
                creer_graphique_1_2.transformer_couleur_texte(
                    couleur_widget_list_survol_fond
                )
            )

            # Checkbox
            couleur_checkbox_bord = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )
            couleur_checkbox_cochee_fond = couleur_widget * 1
            while couleur_checkbox_cochee_fond == couleur_widget:
                couleur_checkbox_cochee_fond = (
                    creer_graphique_1_2.generer_couleur_aleatoire_hex(
                        preset=nuances, teintes_autorisees=teinte
                    )
                )

            # Barre de progression
            couleur_barre = creer_graphique_1_2.generer_couleur_aleatoire_hex(
                preset=nuances, teintes_autorisees=teinte
            )

        elif interface_foncee == False:

            couleur_widget = "#F3F4F8"  # Fond principal bleu-lavande très pâle
            couleur_widget_texte = "#2C2C2C"  # Texte gris anthracite doux

            # Boutons avec variations douces
            couleur_push = "#D6E4F0"  # Bleu clair (bouton standard)
            couleur_push_texte = "#2C2C2C"

            couleur_push2 = "#DAD3EB"  # Lavande clair (hover ou bouton secondaire)
            couleur_push2_texte = "#2C2C2C"

            # Boîtes légèrement teintées différemment
            couleur_box = "#EBF0F2"  # Bleu-gris clair
            couleur_box_texte = "#2C2C2C"
            couleur_box_bord = "#C9D6E0"  # Bordure bleu poussière

            # Lignes : variation vers le gris chaud
            couleur_line = "#F1F2F4"  # Fond de ligne bleu-gris clair
            couleur_line_texte = "#2C2C2C"
            couleur_line_bord = "#D4D4D8"  # Gris chaud discret

            # Sliders : une touche légèrement aqua
            couleur_slider = "#C7DEE7"  # Bleu-vert doux
            couleur_slider2 = "#ADCEDB"  # Bleu-vert plus soutenu

            # GroupBox : ton lavande très pâle pour contraste léger
            couleur_groupbox = "#E6E4F2"

            # Onglets
            onglet_selection = "#C2D4E8"
            onglet_selection_texte = "#2C2C2C"

            onglet_fond = "#E8EAF1"
            onglet_texte = "#2C2C2C"
            onglet_survol = "#CFC4E2"

            # Scroll area
            couleur_scroll_area_fond = "#F3F4F8"
            couleur_scroll_area_texte = "#2C2C2C"
            couleur_scroll_area_barre_partie = "#EBF0F2"
            couleur_scroll_area_barre_survol = "#C7DEE7"
            couleur_scroll_area_barre = "#ADCEDB"
            couleur_scroll_area_bord = "#C9D6E0"

            # Widget list
            couleur_widget_list_fond = "#F4F6FA"
            couleur_widget_list_texte = "#2C2C2C"
            couleur_widget_list_select = "#D6E4F0"
            couleur_widget_list_select_texte = "#2C2C2C"
            couleur_widget_list_survol_fond = "#E0EBF5"
            couleur_widget_list_survol_texte = "#2C2C2C"

            # Checkbox
            couleur_checkbox_bord = "#6c7780"
            couleur_checkbox_cochee_fond = "#ADCEDB"

            # Barre de progression
            couleur_barre = "#ADCEDB"

        else:

            # Fond principal
            couleur_widget = "#07215E"  # Bleu-gris très sombre, mais pas noir
            couleur_widget_texte = "#E8EBEF"  # Gris clair chaud

            # Boutons
            couleur_push = "#3F51B5"  # Bleu moins saturé
            couleur_push_texte = "#FFFFFF"
            couleur_push2 = "#6A4FB3"  # Violet doux
            couleur_push2_texte = "#FFFFFF"

            # Boîtes
            couleur_box = "#07736F"  # Bleu-gris foncé
            couleur_box_texte = "#DADDE0"
            couleur_box_bord = "#5C79A4"

            # Lignes
            couleur_line = "#1E2734"
            couleur_line_texte = "#DADDE0"
            couleur_line_bord = "#32475B"

            # Sliders
            couleur_slider = "#26C6DA"  # Bleu turquoise adouci
            couleur_slider2 = "#4DD0E1"  # Variante plus claire

            # GroupBox
            couleur_groupbox = "#2C3A82"  # Indigo adouci

            # Onglets
            onglet_selection = "#2D3D80"  # Bleu foncé doux
            onglet_selection_texte = "#FFFFFF"

            onglet_fond = "#1A1F2B"
            onglet_texte = "#CCCCCC"
            onglet_survol = "#6A4FB3"

            # Scroll area
            couleur_scroll_area_fond = "#1A1F2B"
            couleur_scroll_area_texte = "#E8EBEF"
            couleur_scroll_area_barre_partie = "#27364D"
            couleur_scroll_area_barre = "#3F7DDC"
            couleur_scroll_area_barre_survol = "#5C9EFF"
            couleur_scroll_area_bord = "#2C3A4F"

            # Widget list
            couleur_widget_list_fond = "#222B3C"
            couleur_widget_list_texte = "#E8EBEF"
            couleur_widget_list_select = "#3F7DDC"
            couleur_widget_list_select_texte = "#FFFFFF"
            couleur_widget_list_survol_fond = "#2F456A"
            couleur_widget_list_survol_texte = "#FFFFFF"

            # Checkbox
            couleur_checkbox_bord = "#2C3A82"
            couleur_checkbox_cochee_fond = "#26C6DA"

            # Barre de progression
            couleur_barre = "#26C6DA"

        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {couleur_widget};
                color: {couleur_widget_texte};
                font-size: 12px;
            }}
            QPushButton {{
                background-color: {couleur_push};
                color: {couleur_push_texte};
                border-radius: 5px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {couleur_push2};
                color: {couleur_push2_texte};
            }}
            QComboBox {{
                background-color: {couleur_box};
                color: {couleur_box_texte};
                border: 1px solid {couleur_box_bord};
                padding: 5px;
                border-radius: 5px;
            }}
            QLineEdit {{
                background-color: {couleur_line};
                color: {couleur_line_texte};
                border: 1px solid {couleur_line_bord};
                padding: 5px;
                border-radius: 5px;
            }}
            QSlider::groove:horizontal {{
                background: {couleur_slider};
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {couleur_slider2};
                width: 20px;
                border-radius: 12px;
                margin: -5px 0;
            }}
            QGroupBox {{
                border: 2px solid {couleur_groupbox};
                border-radius: 5px;
                padding: 10px;
            }}
            QTabBar::tab {{
                background: {onglet_fond};
                color: {onglet_texte};
                padding: 8px 16px;
                border: none;
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }}

            QTabBar::tab:selected {{
                background: {onglet_selection};
                color: {onglet_selection_texte};
                font-weight: bold;
            }}

            QTabBar::tab:hover {{
                background: {onglet_survol};
            }}
            QComboBox QAbstractItemView {{
                border: none;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 5px;
            }}
            QListWidget {{
            background-color: {couleur_widget_list_fond}; /* Très proche de ton fond principal, mais un peu plus lumineux */
            color: {couleur_widget_list_texte};
            border: none;
            padding: 4px;
            border-radius: 5px;
        }}
        QListWidget::item:selected {{
            background-color: {couleur_widget_list_select}; /* Bleu clair (déjà utilisé dans QPushButton) */
            color: {couleur_widget_list_select_texte};
            border-radius: 4px;
        }}
        QListWidget::item:hover {{
            background-color: {couleur_widget_list_survol_fond};
            color: {couleur_widget_list_survol_texte};
        }}
        QScrollArea {{
            background-color: {couleur_scroll_area_fond}; 
            color : {couleur_scroll_area_texte};
            border: 2px solid {couleur_scroll_area_bord};
            border-radius: 5px;
        }}
        QScrollBar:vertical {{
            background: {couleur_scroll_area_barre_partie}; /* cohérent avec couleur_box */
            width: 12px;
            margin: 2px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: {couleur_scroll_area_barre}; /* slider2 : bleu-vert soutenu */
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {couleur_scroll_area_barre_survol}; /* slider : bleu-vert doux */
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
            height: 0;
        }}

        QCheckBox::indicator {{
            border: 1px solid {couleur_checkbox_bord}; /* couleur du cadre */
            background-color: transparent; 
            border-radius: 3px;
        }}

        QCheckBox::indicator:checked {{
            background-color: {couleur_checkbox_cochee_fond};  /* laisse Qt dessiner le tick */
            border: 1px solid {couleur_checkbox_bord};
        }}
        QProgressBar {{
                border: none; 
                text-align: right;
                color: {couleur_widget_texte};
                padding-left: 10px;
                padding-right: 130px;
                background-color: transparent;
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background-color: {couleur_barre};
                width: 8px;
                margin: 0.5px;
            }}

        """
        )

    def choisir_dossier(self):
        dossier = QFileDialog.getExistingDirectory(
            self, self.traduire_depuis_id("dossier_stockage_pop_up")
        )
        if dossier:
            self.dossier_stockage = dossier  # Stocke le chemin sélectionné

    def fonction_principale(self, sauvegarder_seulement=True):

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

            phrase_repertoire = self.traduire_depuis_id(
                "pop_up_pas_de_dossier_de_stockage",
                suffixe=".",
            )
            self.montrer_popup(
                contenu=phrase_repertoire,
                titre=self.traduire_depuis_id("pop_up_probleme_titre", suffixe="."),
                temps_max=10000,
            )

        else:
            # Export des paramètres
            self.fonction_principale(sauvegarder_seulement=True)

            # Publication des cartes
            self.publier_cartes(settings)

    def montrer_popup(
        self,
        titre="Création des cartes",
        contenu="Début de l'opération.",
        temps_max: int | None = 5000,
    ):
        # Crée le message box
        msg = QMessageBox(self)
        msg.setWindowTitle(titre)
        msg.setText(contenu)
        msg.setIcon(QMessageBox.Icon.Information)

        # Configure le bouton OK et centre le message box
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)

        # Timer pour fermer le message box après 3 secondes (3000 ms)
        if temps_max is not None:
            QTimer.singleShot(max(3000, temps_max), msg.close)

        msg.exec()  # Affiche le message box

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
            "nom_indiv": settings["name"],
            "format": settings["format"],
            "noms_pays": constantes.pays_differentes_langues,
            "langue": settings["language"],
            "direction_resultat": settings["results"],
            "granularite_visite": granularite,
            "qualite": settings["quality"],
            "theme": constantes.liste_ambiances[settings["theme"]],
            "teinte": constantes.liste_couleurs[settings["color"]],
            "granularite_reste": granularite_fond,
            "pays_individuel": settings["cartes_des_pays"],
            "liste_regions": liste_regions_temp,
            "dictionnaire_pays_unis": constantes.liste_pays_groupes,
            "couleur_fond": "#FFFFFF",
            "max_cartes_additionnelles": settings["limite_nb_cartes"],
            "carte_du_monde": settings["carte_du_monde"],
            "sortir_cartes_granu_inf": settings["publier_granu_faible"],
            "couleur_non_visites": "#ECEBED",
        }

        self.thread = QThread()
        self.worker = CreerCartes(parametres)
        self.worker.moveToThread(self.thread)

        self.worker.tracker_signal.connect(self.afficher_avancement)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(
            lambda: self.debut_fin_creation_cartes(debut=False)
        )

        self.thread.started.connect(self.worker.run)
        self.thread.start()

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
                suffixe="." if debut else " ​​✅​",
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

    def ajouter_partie_a_layout(self, granu, pays_donnees, vbox, affichage_groupe=True):

        label_titre_onglet_3 = QLabel(
            self.traduire_depuis_id(clef=granu, prefixe="<b>", suffixe="</b>")
        )
        label_titre_onglet_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(label_titre_onglet_3)

        layout_temp = QHBoxLayout()
        ligne = QFrame()
        ligne.setFixedHeight(2)
        ligne.setFrameShape(QFrame.Shape.HLine)  # Ligne horizontale
        ligne.setFrameShadow(QFrame.Shadow.Sunken)  # Style de relief
        layout_temp.addStretch(1)
        layout_temp.addWidget(ligne, 4)
        layout_temp.addStretch(1)
        vbox.addLayout(layout_temp)
        vbox.addWidget(QLabel(""))

        for pays, items in pays_donnees.items():

            emoji_i = (
                f"{constantes.emojis_pays[pays]} "
                if pays in list(constantes.emojis_pays.keys()) and inclure_emojis
                else ""
            )

            if affichage_groupe:

                texte_items = ", ".join(items) if items else "Aucun élément"
                texte = f"<b>{pays}</b> {emoji_i}: {texte_items}"
                label = QLabel(texte)
                label.setWordWrap(True)
                vbox.addWidget(label)

            else:

                vbox.addWidget(QLabel(f"<b>{pays}</b> {emoji_i}:"))

                for item in items:
                    label = QLabel(f"   • {item}")
                    label.setWordWrap(True)
                    vbox.addWidget(label)

            label = QLabel("– " * 3)
            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
                if affichage_groupe
                else Qt.AlignmentFlag.AlignLeft
            )
            vbox.addWidget(label)

        vbox.addStretch()

    def vider_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def maj_layout_resume(self, affichage_groupe=True):
        # Effacer les layouts
        self.vider_layout(self.layout_resume_regions)
        self.vider_layout(self.layout_resume_departements)

        # Ajouter les nouvelles parties aux layouts
        self.ajouter_partie_a_layout(
            "titre_regions_visitees",
            self.dicts_granu.get("region", {}),
            self.layout_resume_regions,
            affichage_groupe=affichage_groupe,
        )
        self.ajouter_partie_a_layout(
            "titre_departements_visites",
            self.dicts_granu.get("dep", {}),
            self.layout_resume_departements,
            affichage_groupe=affichage_groupe,
        )

        self.lancer_classement_par_region_departement(top_n=top_n_pays)

    def lancer_classement_pays(
        self, granularite: int, top_n: int | None, vbox: QGridLayout
    ):
        dict_regions = (
            self.dicts_granu["region"] if self.dicts_granu["region"] != {} else None
        )
        dict_departements = (
            self.dicts_granu["dep"] if self.dicts_granu["dep"] != {} else None
        )

        # Met à jour la vbox avec le résultat
        self.vider_layout(vbox)

        try:
            # Appelle directement la fonction de création des données (similaire au run())
            gdf = creer_carte_1_1.cree_base_toutes_granularites(
                liste_dfs=liste_gdfs,
                liste_dicts=[dict_regions, dict_departements],
                granularite_objectif=granularite,
            )

            classement = fonctions_utiles_2_0.creer_classement_pays(
                gdf,
                constantes.table_superficie,
                granularite=granularite,
                top_n=top_n,
            )

            i = 0
            for _, row in classement.iterrows():
                pays = row["Pays"]

                indice = ["🥇", "🥈", "🥉"][i] if i < 3 else f"<b>{i + 1}.</b>"
                separateur = "<br>"
                pay_lib = f"<b>{pays}</b>" if i < 3 else pays
                label_pays = (
                    indice
                    + separateur
                    + f"{pay_lib}<br>{round(100 * row['pct_superficie_dans_pays'])} %"
                )

                label_pays = QLabel(label_pays)
                label_pays.setAlignment(
                    Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
                )

                if i == 0:

                    label_couronne = QLabel("👑")
                    label_couronne.setAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                    vbox.addWidget(label_couronne, i, 0)

                    vbox.addWidget(label_pays, i, 1)

                    label_couronne = QLabel("👑")
                    label_couronne.setAlignment(
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                    )
                    vbox.addWidget(label_couronne, i, 2)

                elif i in [1, 2]:
                    vbox.addWidget(label_pays, 1, 2 * i - 2)
                else:
                    vbox.addWidget(label_pays, (i + 3) // 3, i % 3)

                i = i + 1

        except Exception as e:
            pass

        # vbox.addStretch()

    def lancer_classement_par_region_departement(self, top_n: int | None = 10):

        self.lancer_classement_pays(
            granularite=1,
            top_n=top_n,
            vbox=self.layout_top_pays_regions,
        )

        self.lancer_classement_pays(
            granularite=2,
            top_n=top_n,
            vbox=self.layout_top_pays_deps,
        )

    def initialiser_sauvegarde(self, sauvegarde_complete):

        nom_individu_actuel = self.nom_individu.currentText()
        sauv = sauvegarde_complete.get(nom_individu_actuel, {})

        # Nom
        if sauv.get("name") is not None:
            # self.nom_individu.setCurrentText(sauv.get("name"))

            # Dossier de publication
            if sauv.get("results") is not None:
                self.dossier_stockage = sauv.get("results")

            # Langue
            if sauv.get("language") is not None:
                self.langue_utilisee.setCurrentText(
                    constantes.dict_langues_dispo[sauv.get("language")]
                )

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

            self.maj_liste_reg_dep_pays()
            self.lancer_classement_par_region_departement(top_n=top_n_pays)

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
        self.maj_layout_resume(affichage_groupe=affichage_groupe)

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
        self.curseur_qualite.setValue(int((qualite_min + qualite_max) / 2))
        self.format_cartes.setCurrentText("png")

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

        self.maj_layout_resume(affichage_groupe=affichage_groupe)

    def supprimer_clef(self, clef):
        global sauvegarde
        if clef in sauvegarde:
            del sauvegarde[clef]

            self.nom_individu.clear()
            self.nom_individu.addItems(list(sauvegarde.keys()))

            with open(
                os.path.join(
                    constantes.direction_donnees_application, "sauvegarde_param.yaml"
                ),
                "w",
                encoding="utf-8",
            ) as f:
                yaml.dump(sauvegarde, f, allow_unicode=True, default_flow_style=False)

            self.reinitialisation_parametres(True)
            self.dicts_granu = {"region": {}, "dep": {}}
            self.maj_layout_resume(affichage_groupe=affichage_groupe)
            self.maj_langue_interface(True)


if __name__ == "__main__":

    # Lancement de l'application
    app = QApplication(sys.argv)
    window = SettingsApp()
    window.show()

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

    sys.exit(app.exec())
