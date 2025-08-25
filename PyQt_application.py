################################################################################
# MesVoyages                                                                   #
# Application principale                                                       #
################################################################################

import os, sys, warnings, copy, textwrap, threading

# PyQt6
from PyQt6.QtWidgets import (
    QApplication,
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
    QMessageBox,
    QButtonGroup,
    QRadioButton,
    QTabWidget,
    QProgressBar,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QTimer, QThread

# Scripts et fonctions du projet
import constantes
from production_cartes import creer_graphique_1_2
from application import fonctions_utiles_2_0
from application.onglets import onglet_1, onglet_2, onglet_3, onglet_5
from application.onglets.onglet_4 import onglet_4


warnings.filterwarnings("ignore")


# Import de la sauvegarde
sauvegarde = fonctions_utiles_2_0.ouvrir_fichier(
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="sauvegarde_utilisateurs.yaml",
    defaut={},
)


class MesVoyagesApplication(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cartes de voyage")
        self.setGeometry(
            constantes.parametres_application["application_position_largeur"],
            constantes.parametres_application["application_position_hauteur"],
            constantes.parametres_application["application_largeur"],
            constantes.parametres_application["application_hauteur"],
        )
        self.setWindowIcon(
            QIcon(os.path.join(constantes.direction_donnees_application, "icone_france.ico"))
        )

        self.tabs = QTabWidget()

        # Créer un QWidget pour le contenu de l'onglet principal
        self.onglet_parametres = QWidget()
        self.tabs.addTab(self.onglet_parametres, "Paramètres")

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
        self.dossier_stockage_bouton.clicked.connect(lambda: self.maj_langue_interface(False))
        layout_params_individu.addWidget(self.dossier_stockage_bouton)

        # Choix de la langue
        self.label_langue = fonctions_utiles_2_0.creer_QLabel_centre()
        self.langue_utilisee = QComboBox()
        self.langue_utilisee.addItems(
            ["Français", "English"]
            + sorted(
                langue
                for langue in constantes.dict_langues_dispo.values()
                if langue not in {"Français", "English"}
            )
        )
        layout_params_individu.addWidget(self.label_langue)
        layout_params_individu.addWidget(self.langue_utilisee)
        self.langue_utilisee.currentIndexChanged.connect(lambda: self.maj_langue_interface(True))

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

        # Créer un QGroupBox pour les choix de granularité
        self.groupe_granularite = QGroupBox()

        # Choix de la granularité
        self.label_granularite_visite = fonctions_utiles_2_0.creer_QLabel_centre()

        self.granularite_visite = QComboBox()
        layout_granularite_visite = QHBoxLayout()
        layout_granularite_visite.addWidget(self.label_granularite_visite)
        layout_granularite_visite.addWidget(self.granularite_visite)
        layout_granularite_visite.addWidget(fonctions_utiles_2_0.creer_ligne_verticale())

        # Granularité de fond
        self.label_granularite_fond = fonctions_utiles_2_0.creer_QLabel_centre()
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

        self.sortir_cartes_granu_inf = QCheckBox()

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
            fonctions_utiles_2_0.creer_ligne_separation(lStretch=0, ligne_largeur=1, rStretch=0),
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
            fonctions_utiles_2_0.creer_ligne_separation(lStretch=0, ligne_largeur=1, rStretch=0),
            4,
            0,
            1,
            6,
        )

        layout_cartes_a_creer.addWidget(
            self.sortir_cartes_granu_inf,
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
        self.label_nb_copies_cartes = fonctions_utiles_2_0.creer_QLabel_centre()

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
        layout_theme_couleurs = QVBoxLayout()

        # Choix du thème
        self.theme_label = fonctions_utiles_2_0.creer_QLabel_centre()
        self.theme_combo = QComboBox()
        self.theme_combo.currentTextChanged.connect(self.maj_style)
        layout_theme = QHBoxLayout()
        layout_theme.addWidget(self.theme_label)
        layout_theme.addWidget(self.theme_combo)

        # Choix des couleurs
        self.color_label = fonctions_utiles_2_0.creer_QLabel_centre()
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
        layout_theme_couleurs.addLayout(layout_theme)
        layout_theme_couleurs.addLayout(layout_couleurs)
        layout_theme_couleurs.addWidget(self.utiliser_theme)
        layout_theme_couleurs.addLayout(
            fonctions_utiles_2_0.creer_ligne_separation(lStretch=0, ligne_largeur=1, rStretch=0)
        )
        layout_theme_couleurs.addWidget(
            self.couleur_fond_checkbox, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        # Ajout du layout de couleurs au groupbox et ajout du groupbox au layout principal
        self.groupe_couleurs.setLayout(layout_theme_couleurs)

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
        self.label_qualite = fonctions_utiles_2_0.creer_QLabel_centre()
        self.label_qualite_min = fonctions_utiles_2_0.creer_QLabel_centre()
        self.label_qualite_max = fonctions_utiles_2_0.creer_QLabel_centre()
        self.curseur_qualite = QSlider(Qt.Orientation.Horizontal)
        self.curseur_qualite.setMinimum(constantes.parametres_application["qualite_min"])
        self.curseur_qualite.setMaximum(constantes.parametres_application["qualite_max"])
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
        self.label_format = fonctions_utiles_2_0.creer_QLabel_centre()
        self.format_cartes = QComboBox()
        self.format_cartes.addItems(["png", "jpg", "svg", "pdf", "tif", "webp", "raw", "ps"])

        # Ajout des widgets au layout horizontal
        layout_format_qualite.addWidget(self.label_format)
        layout_format_qualite.addWidget(self.format_cartes)
        layout_format_qualite.addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
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
        self.creation_cartes_bouton.clicked.connect(self.fonction_principale)
        self.barre_progression = QProgressBar()
        self.barre_progression.setMinimum(0)
        self.barre_progression.setValue(0)
        self.barre_progression.setFormat("")

        # Bouton de sauvegarde
        self.bouton_sauvegarde = QPushButton()
        self.bouton_sauvegarde.clicked.connect(self.exporter_liste_parametres)

        # Bouton de réinitialisation
        self.reinit_parametres = QPushButton()
        self.reinit_parametres.clicked.connect(lambda: self.reinitialisation_parametres(True))
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
        self.onglet_parametres.setLayout(layout)

        # Deuxième onglet
        self.dicts_granu = {"region": {}, "dep": {}}
        self.selection_destinations = onglet_2.OngletSelectionnerDestinations(
            constantes=constantes,
            fct_traduire=self.traduire_depuis_id,
            fct_sauvegarde=self.exporter_liste_parametres,
            fct_pop_up=self.montrer_popup,
        )
        self.tabs.addTab(self.selection_destinations, "Création de la liste des pays visités")

        # Troisième onglet
        self.onglet_resume_pays = onglet_3.OngletResumeDestinations(
            traduire_depuis_id=self.traduire_depuis_id,
            constantes=constantes,
        )
        self.tabs.addTab(self.onglet_resume_pays, "📊")

        # Quatrième onglet
        self.onglet_top_pays_visites = onglet_4.OngletTopPays(
            constantes=constantes,
            parent=None,
            mise_en_page=constantes.parametres_application["onglet_4_mise_en_page"],
            # Classement
            top_n=constantes.parametres_application["top_n_pays"],
            ndigits=constantes.parametres_application["pct_ndigits"],
            # Hémicycle
            lighter_value=constantes.parametres_application["lighter_value"],
            n_rangees=constantes.parametres_application["n_rangees"],
            points_base=constantes.parametres_application["points_base"],
            points_increment=constantes.parametres_application["points_increment"],
            continent_colors=constantes.parametres_application["couleurs_continents"],
        )
        self.tabs.addTab(self.onglet_top_pays_visites, "Pays les plus visités")

        # Cinquième onglet
        self.onglet_description_application = onglet_5.OngletInformations()
        self.tabs.addTab(self.onglet_description_application, "ℹ️")

        # Définir le QTabWidget comme layout principal pour le widget principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        self.maj_style()
        self.maj_langue_interface(True)
        self.setLayout(main_layout)
        self.selection_destinations.dict_modif.connect(self.maj_dict_granu)

        # Connections aux fonctions
        self.nom_individu.currentIndexChanged.connect(
            lambda: self.initialiser_sauvegarde(sauvegarde)
        )
        # self.nom_individu.editTextChanged.connect(
        #     lambda: self.initialiser_sauvegarde(sauvegarde)
        # )

        self.nom_individu.currentIndexChanged.connect(lambda: self.maj_langue_interface(True))
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
            self.tabs.indexOf(self.onglet_parametres),
            self.traduire_depuis_id(
                "titre_onglet_1",
                suffixe=(" 🎨"),
            ),
        )

        self.tabs.setTabText(
            self.tabs.indexOf(self.selection_destinations),
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
            self.tabs.indexOf(self.onglet_top_pays_visites),
            self.traduire_depuis_id(
                "titre_onglet_4",
                suffixe=(" 📊"),
            ),
        )
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.onglet_top_pays_visites),
            self.traduire_depuis_id("description_onglet_4", suffixe="."),
        )

        self.traduire_depuis_id("description_bouton_publier_cartes", suffixe=".")

        # Paramètres de l'individu
        self.groupe_params_individu.setTitle(self.traduire_depuis_id("titre_params_individu"))
        self.dossier_stockage_bouton.setText(
            self.traduire_depuis_id("dossier_stockage_individu")
            if self.dossier_stockage is None
            else os.sep.join(os.path.normpath(self.dossier_stockage).split(os.sep)[-3:])
        )
        self.label_langue.setText(self.traduire_depuis_id(clef="langue_individu", suffixe=" :"))
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
        self.groupe_cartes_a_creer.setTitle(self.traduire_depuis_id("titre_cartes_a_publier"))
        self.carte_pays.setText(self.traduire_depuis_id("cartes_pays_visites"))
        self.carte_monde.setText(self.traduire_depuis_id("carte_du_monde"))
        self.afrique.setText(self.traduire_depuis_id("afrique"))
        self.amerique.setText(self.traduire_depuis_id("amerique"))
        self.asie.setText(self.traduire_depuis_id("asie"))
        self.europe.setText(self.traduire_depuis_id("europe"))
        self.moyen_orient.setText(self.traduire_depuis_id("moyen_orient"))
        self.autres_regions.setText(self.traduire_depuis_id("autres_regions_monde"))
        self.sortir_cartes_granu_inf.setText(
            self.traduire_depuis_id("publier_cartes_faible_granularite_uniquement")
        )
        self.sortir_cartes_granu_inf.setToolTip(
            self.traduire_depuis_id(
                clef="description_publier_cartes_faible_granularite_uniquement",
                largeur_max=None,
            )
        )

        # Paramètres visuels
        self.groupe_couleurs.setTitle(self.traduire_depuis_id("titre_params_esthetiques"))
        self.color_label.setText(self.traduire_depuis_id(clef="cartes_couleurs", suffixe=" :"))
        self.theme_label.setText(self.traduire_depuis_id(clef="cartes_theme", suffixe=" :"))
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
        self.groupe_params_publication.setTitle(self.traduire_depuis_id("titre_params_techniques"))
        self.label_format.setText(self.traduire_depuis_id("cartes_format", suffixe=" :"))
        self.label_qualite.setText(self.traduire_depuis_id("cartes_qualite", suffixe=" :"))
        self.label_qualite_max.setText(self.traduire_depuis_id("qualite_elevee"))
        self.label_qualite_min.setText(self.traduire_depuis_id("qualite_faible"))
        self.label_nb_copies_cartes.setText(
            self.traduire_depuis_id("nombre_exemplaires_cartes", suffixe=" : ")
        )
        self.label_nb_copies_cartes.setToolTip(
            self.traduire_depuis_id("description_nombre_exemplaires_cartes", suffixe=".")
        )
        self.radio_carte_1.setText(self.traduire_depuis_id("cinq_cartes"))
        self.radio_carte_2.setText(self.traduire_depuis_id("dix_cartes"))
        self.radio_carte_3.setText(self.traduire_depuis_id("quinze_cartes"))
        self.radio_carte_sans_limite.setText(self.traduire_depuis_id("pas_de_limite_de_cartes"))

        # Boutons en bas de l'onglet 1
        self.reinit_parametres.setText(self.traduire_depuis_id("reinitialisation_interface"))
        self.reinit_parametres.setToolTip(
            self.traduire_depuis_id("description_bouton_reinitialisation_interface", suffixe=".")
        )
        self.creation_cartes_bouton.setText(self.traduire_depuis_id("bouton_publier_cartes"))
        self.creation_cartes_bouton.setToolTip(
            self.traduire_depuis_id("description_bouton_publier_cartes", suffixe=".")
        )
        self.bouton_sauvegarde.setText("💾")
        self.bouton_sauvegarde.setToolTip(
            self.traduire_depuis_id("sauvegarder_profil", suffixe=".")
        )

        # Onglet 2
        self.selection_destinations.set_langue(langue=langue_actuelle)

        # Onglet 3
        self.onglet_resume_pays.set_langue(nouvelle_langue=langue_actuelle)

        # Onglet 4
        self.onglet_top_pays_visites.set_entetes(
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

        self.onglet_top_pays_visites.set_langue(nouvelle_langue=langue_actuelle)

        # # Onglet 5
        self.onglet_description_application.set_description(
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

            # Mise à jour des granularités
            liste_granularite = [
                constantes.parametres_traduits["granularite"][langue_actuelle][k]
                for k in ["Pays", "Région", "Département", "Amusant"]
            ]
            fonctions_utiles_2_0.reset_combo(self.granularite_visite, liste_granularite)
            fonctions_utiles_2_0.reset_combo(
                self.granularite_fond, liste_granularite[:-1], set_index=False
            )

            # Mise à jour des teintes
            fonctions_utiles_2_0.reset_combo(
                self.color_combo,
                sorted(
                    constantes.parametres_traduits["teintes_couleurs"]
                    .get(langue_actuelle, {})
                    .values()
                ),
            )

            # Mise à jour de l'ambiance
            fonctions_utiles_2_0.reset_combo(
                self.theme_combo,
                sorted(
                    constantes.parametres_traduits["themes_cartes"]
                    .get(langue_actuelle, {})
                    .values()
                ),
            )

    def traduire_depuis_id(
        self,
        clef: str,
        langue: str | None = None,
        prefixe: str = "",
        suffixe: str = "",
        depuis_id: bool = True,
        largeur_max: int | None = None,
    ) -> str:
        """
        Traduit une clé ou un ID de phrase selon la langue spécifiée.

        Args:
            clef: La clé ou l'ID de la phrase à traduire.
            langue: La langue cible. Si None, utilise la langue courante.
            prefixe: Préfixe à ajouter avant la traduction.
            suffixe: Suffixe à ajouter après la traduction.
            depuis_id: Si True, traite `cle` comme un ID à chercher dans `constantes.phrases_interface`.
            largeur_max: Si spécifié, tronque le texte à cette largeur maximale.

        Returns:
            str: La traduction formatée.
        """
        if langue is None:
            langue = fonctions_utiles_2_0.obtenir_clef_par_valeur(
                dictionnaire=constantes.dict_langues_dispo,
                valeur=self.langue_utilisee.currentText(),
            )

        # Résolution de la clé si on part d'un ID
        if depuis_id:
            clef = constantes.phrases_interface.get(clef, clef)

        # Récupération de la traduction
        traduction = (
            prefixe + constantes.outil_differentes_langues.get(clef, {}).get(langue, clef) + suffixe
        )

        # Troncature si nécessaire
        if largeur_max is not None:

            traduction = textwrap.wrap(
                traduction,
                width=largeur_max,
                break_long_words=False,
                break_on_hyphens=False,
            )[0]

        return traduction

    def maj_style(self):

        # Récupération de la langue sélectionnée
        langue_l = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            dictionnaire=constantes.dict_langues_dispo,
            valeur=self.langue_utilisee.currentText(),
        )

        try:

            # Récupération de l'ambiance
            liste_theme_temp = constantes.liste_ambiances.get(
                fonctions_utiles_2_0.obtenir_clef_par_valeur(
                    dictionnaire=constantes.parametres_traduits["themes_cartes"].get(langue_l, {}),
                    valeur=self.theme_combo.currentText(),
                )
            )

            # Récupération des teintes utilisées
            liste_teintes_temp = constantes.liste_couleurs.get(
                fonctions_utiles_2_0.obtenir_clef_par_valeur(
                    dictionnaire=constantes.parametres_traduits["teintes_couleurs"].get(
                        langue_l, {}
                    ),
                    valeur=self.color_combo.currentText(),
                )
            )

        except:
            return

        # Sortie si une valeur n'existe pas
        if liste_theme_temp is None or liste_teintes_temp is None:
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
            self.selection_destinations.set_dossier(dossier=dossier)

    def creer_liste_parametres(self):

        langue = fonctions_utiles_2_0.obtenir_clef_par_valeur(
            valeur=self.langue_utilisee.currentText(),
            dictionnaire=constantes.dict_langues_dispo,
        )

        return {
            "nom": self.nom_individu.currentText(),
            "granularite": fonctions_utiles_2_0.obtenir_clef_par_valeur(
                valeur=self.granularite_visite.currentText(),
                dictionnaire=constantes.parametres_traduits["granularite"][langue],
            ),
            "granularite_fond": fonctions_utiles_2_0.obtenir_clef_par_valeur(
                valeur=self.granularite_fond.currentText(),
                dictionnaire=constantes.parametres_traduits["granularite"][langue],
            ),
            "langue": langue,
            "couleur": fonctions_utiles_2_0.obtenir_clef_par_valeur(
                valeur=self.color_combo.currentText(),
                dictionnaire=constantes.parametres_traduits["teintes_couleurs"][langue],
            ),
            "couleur_fond_carte": self.couleur_fond_checkbox.isChecked(),
            "theme": fonctions_utiles_2_0.obtenir_clef_par_valeur(
                valeur=self.theme_combo.currentText(),
                dictionnaire=constantes.parametres_traduits["themes_cartes"][langue],
            ),
            "qualite": self.curseur_qualite.value(),
            "format": self.format_cartes.currentText(),
            "dossier_stockage": self.dossier_stockage,
            "carte_du_monde": self.carte_monde.isChecked(),
            "europe": self.europe.isChecked(),
            "asie": self.asie.isChecked(),
            "amerique": self.amerique.isChecked(),
            "afrique": self.afrique.isChecked(),
            "moyen_orient": self.moyen_orient.isChecked(),
            "autres_regions": self.autres_regions.isChecked(),
            "sortir_cartes_granu_inf": self.sortir_cartes_granu_inf.isChecked(),
            "cartes_des_pays": self.carte_pays.isChecked(),
            "max_cartes_additionnelles": {
                self.radio_carte_1: 5,
                self.radio_carte_2: 10,
                self.radio_carte_3: 15,
            }.get(self.groupe_radio_max_cartes.checkedButton(), None),
            "dictionnaire_regions": (
                self.dicts_granu["region"] if self.dicts_granu["region"] != {} else None
            ),
            "dictionnaire_departements": (
                self.dicts_granu["dep"] if self.dicts_granu["dep"] != {} else None
            ),
            "format_onglet_3": self.onglet_resume_pays.mise_en_forme.isChecked(),
        }

    def exporter_liste_parametres(self):

        parametres = self.creer_liste_parametres()
        if parametres["nom"] is None or parametres["nom"] in [""]:
            parametres["nom"] = fonctions_utiles_2_0.formater_temps_actuel()
        sauvegarde[parametres["nom"]] = copy.deepcopy(parametres)

        # Ajout à la liste déroulante
        if parametres["nom"] not in [
            self.nom_individu.itemText(i) for i in range(self.nom_individu.count())
        ]:
            self.nom_individu.addItem(parametres["nom"])

        # Export sous forme de YAML
        fonctions_utiles_2_0.exporter_fichier(
            objet=sauvegarde,
            direction_fichier=constantes.direction_donnees_application,
            nom_fichier="sauvegarde_utilisateurs.yaml",
            sort_keys=True,
        )

        # Gestion des autres onglets
        self.selection_destinations.set_nom_individu(nom=parametres["nom"])

        # Visualisation de la sauvegarde
        self.bouton_sauvegarde.setText("💾✅")
        self.selection_destinations.set_emoji_sauvegarde()
        QTimer.singleShot(3000, lambda: self.bouton_sauvegarde.setText("💾"))

    def fonction_principale(self):

        settings = self.creer_liste_parametres()

        if (
            settings["dictionnaire_regions"] is None
            and settings["dictionnaire_departements"] is None
        ):

            self.montrer_popup(
                contenu=self.traduire_depuis_id("pop_up_aucun_lieu_coche", suffixe="."),
                titre=self.traduire_depuis_id("pop_up_probleme_titre", suffixe="."),
                temps_max=10000,
            )

        elif settings["dossier_stockage"] is None:

            self.montrer_popup(
                contenu=self.traduire_depuis_id(
                    "pop_up_pas_de_dossier_de_stockage",
                    suffixe=".",
                ),
                titre=self.traduire_depuis_id("pop_up_probleme_titre", suffixe="."),
                temps_max=10000,
            )

        else:

            self.exporter_liste_parametres()  # Export des paramètres
            self.publier_cartes(settings | {"liste_dfs": liste_gdfs})  # Publication des cartes

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
            msg.addButton(self.traduire_depuis_id(clef="oui"), QMessageBox.ButtonRole.YesRole)
            msg.addButton(self.traduire_depuis_id(clef="non"), QMessageBox.ButtonRole.NoRole)
            msg.setIcon(QMessageBox.Icon.Question)

        # Timer pour fermer le message box après 3 secondes (3000 ms)
        if temps_max is not None and not boutons_oui_non:
            QTimer.singleShot(max(3000, temps_max), msg.close)

        if renvoyer_popup == False:
            msg.exec()  # Affiche le message box
        else:
            return msg

    def maj_dict_granu(self, dictionnaire: dict):
        self.dicts_granu = dictionnaire
        self.onglet_resume_pays.set_dicts_granu(dict_nv=self.dicts_granu)
        self.onglet_top_pays_visites.set_dicts_granu(dict_nv=self.dicts_granu)

    def publier_cartes(self, parametres):

        # Initialisation de l'objet et de la barre de progression
        self.creation_cartes = onglet_1.CreerCartes(params=parametres, constantes=constantes)
        self.creation_cartes.nb_graphes.connect(self.initialiser_progression)
        self.creation_cartes.tracker_signal.connect(self.afficher_avancement)

        self.thread_temp = QThread()
        self.creation_cartes.moveToThread(self.thread_temp)

        self.creation_cartes.finished.connect(self.thread_temp.quit)
        self.creation_cartes.finished.connect(self.creation_cartes.deleteLater)
        self.thread_temp.finished.connect(self.thread_temp.deleteLater)
        self.thread_temp.finished.connect(lambda: self.debut_fin_creation_cartes(debut=False))

        self.thread_temp.started.connect(self.creation_cartes.run)
        self.thread_temp.start()

    def initialiser_progression(self, nb_cartes: int):

        # Initialisation de la barre de progression
        self.barre_progression.setMaximum(nb_cartes)
        self.barre_progression.setValue(0)
        self.nb_total_graphes = nb_cartes
        self.graphique_i = 0

        # Affichage de la barre de progression
        self.debut_fin_creation_cartes(debut=True)

    def afficher_avancement(self, libelle_pays):
        self.graphique_i = self.graphique_i + 1
        self.barre_progression.setValue(self.graphique_i)
        self.barre_progression.setFormat(
            f"{self.graphique_i}/{self.nb_total_graphes} : {libelle_pays}"
        )

    def debut_fin_creation_cartes(self, debut):

        self.creation_cartes_bouton.setVisible(not debut)
        self.barre_progression.setVisible(debut)

        self.montrer_popup(
            contenu=self.traduire_depuis_id(
                clef=("debut_publication_cartes" if debut else "publication_cartes_reussie"),
                suffixe="." if debut else " ✅​",
            ),
            temps_max=5000 if debut else None,
            titre=self.traduire_depuis_id(clef="titre_pop_up_publication_cartes"),
        )

    def initialiser_sauvegarde(self, sauvegarde_complete):

        self.reinitialisation_parametres(nom_aussi=False)
        sauv = sauvegarde_complete.get(self.nom_individu.currentText(), {})

        # Nom
        if sauv.get("nom") is not None:

            # Dossier de publication
            if sauv.get("dossier_stockage") is not None:
                self.dossier_stockage = sauv.get("dossier_stockage")
                self.selection_destinations.set_dossier(dossier=self.dossier_stockage)

            # Langue
            if sauv.get("langue") is not None:
                self.langue_utilisee.setCurrentText(
                    constantes.dict_langues_dispo[sauv.get("langue")]
                )
                self.onglet_top_pays_visites.set_langue(nouvelle_langue=sauv.get("langue"))

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
                "sortir_cartes_granu_inf": self.sortir_cartes_granu_inf,
            }
            for nom_cle, checkbox in checkboxes.items():
                if sauv.get(nom_cle) is not None:
                    checkbox.setChecked(sauv.get(nom_cle))

            # Qualité
            if sauv.get("qualite") is not None:
                self.curseur_qualite.setValue(sauv.get("qualite"))

            # Format
            if sauv.get("format") is not None:
                self.format_cartes.setCurrentText(sauv.get("format"))

            # Récupération des régions
            if sauv.get("dictionnaire_regions") is not None:
                self.dicts_granu["region"] = sauv.get("dictionnaire_regions")
            else:
                self.dicts_granu["region"] = {}

            # Récupération des départements
            if sauv.get("dictionnaire_departements") is not None:
                self.dicts_granu["dep"] = sauv.get("dictionnaire_departements")
            else:
                self.dicts_granu["dep"] = {}

            # Affectation du dictionnaire au deuxième onglet également
            self.selection_destinations.set_dict_granu(dictionnaire=self.dicts_granu)

            # Limite de cartes
            if sauv.get("max_cartes_additionnelles") is not None:
                if sauv.get("max_cartes_additionnelles") == 5:
                    self.radio_carte_1.setChecked(True)
                elif sauv.get("max_cartes_additionnelles") == 10:
                    self.radio_carte_2.setChecked(True)
                elif sauv.get("max_cartes_additionnelles") == 15:
                    self.radio_carte_3.setChecked(True)
                else:
                    self.radio_carte_sans_limite.setChecked(True)

            if sauv.get("format_onglet_3") is not None:
                self.onglet_resume_pays.mise_en_forme.setChecked(sauv.get("format_onglet_3"))

            if sauv.get("couleur_fond_carte") is not None:
                self.couleur_fond_checkbox.setChecked(sauv.get("couleur_fond_carte"))

            self.selection_destinations.reset_yaml()
            self.onglet_top_pays_visites.set_dicts_granu(dict_nv=self.dicts_granu)
            self.onglet_resume_pays.set_dicts_granu(dict_nv=self.dicts_granu)

    def reinitialisation_parametres(self, nom_aussi=True):

        # Paramètres individuels
        if nom_aussi == True:
            self.nom_individu.setCurrentText("")
            self.nom_individu.blockSignals(True)
            self.nom_individu.setCurrentIndex(-1)
            self.nom_individu.blockSignals(False)

        self.dicts_granu = {"region": {}, "dep": {}}
        self.selection_destinations.set_dict_granu(dictionnaire=self.dicts_granu)

        self.dossier_stockage = None
        self.selection_destinations.set_dossier(dossier=self.dossier_stockage)
        self.radio_carte_2.setChecked(True)
        self.langue_utilisee.setCurrentIndex(0)

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

        # Autres paramètres
        self.sortir_cartes_granu_inf.setChecked(False)
        self.utiliser_theme.setChecked(False)

        self.selection_destinations.reset_yaml()
        self.onglet_resume_pays.mise_en_forme.setChecked(False)
        self.onglet_resume_pays.set_dicts_granu(dict_nv=self.dicts_granu)
        self.onglet_top_pays_visites.set_dicts_granu(dict_nv=self.dicts_granu)

    def supprimer_clef(self, clef):
        global sauvegarde

        # Pop-up afin de s'assurer de la décision
        message = self.montrer_popup(
            titre=self.traduire_depuis_id(clef="titre_pop_up_suppression"),
            contenu=self.traduire_depuis_id(clef="contenu_pop_up_suppression", suffixe="."),
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
            fonctions_utiles_2_0.exporter_fichier(
                objet=sauvegarde,
                direction_fichier=constantes.direction_donnees_application,
                nom_fichier="sauvegarde_utilisateurs.yaml",
                sort_keys=True,
            )

            # Réinitialisation des paramètres
            self.reinitialisation_parametres(True)
            self.dicts_granu = {"region": {}, "dep": {}}
            self.maj_langue_interface(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Création d'une liste vide pour stocker les GDF
    liste_gdfs = [None] * 3

    # Lancement du thread de chargement
    threading.Thread(
        target=fonctions_utiles_2_0.charger_gdfs,
        args=(liste_gdfs, constantes.direction_donnees_pickle, 3),
        daemon=True,
    ).start()

    # Lancement de l'application
    window = MesVoyagesApplication()
    window.show()

    sys.exit(app.exec())
