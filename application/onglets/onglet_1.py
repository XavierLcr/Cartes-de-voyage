################################################################################
# Projet de cartes de voyage                                                   #
# application/classes                                                          #
# Onglet 1 – Paramètres et création des cartes                                 #
################################################################################


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
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
from production_cartes.carte_main_1_3 import cree_graphe_depuis_debut
from application.fonctions_utiles_2_0 import (
    creer_ligne_verticale,
    creer_ligne_separation,
    creer_QLabel_centre,
    style_bouton_de_suppression,
)


# Classe de suivi du pays en cours de cartographie
class TrackerPays(QObject):
    tracker_pays_en_cours = pyqtSignal(str)

    def notify(self, libelle_pays: str):
        self.tracker_pays_en_cours.emit(libelle_pays)


# Classe de création des cartes
class CreerCartes(QObject):
    finished = pyqtSignal()
    tracker_signal = pyqtSignal(str)
    nb_graphes = pyqtSignal(int)

    def __init__(self, params, constantes):
        super().__init__()
        self.parametres = params
        self.constantes = constantes

    def run(self):

        # --- Partie déplacée de publier_cartes ---
        granularite = {"Pays": 0, "Région": 1, "Département": 2}.get(
            self.parametres.get("granularite"), -1
        )

        self.liste_regions_temp = {
            region: self.constantes.liste_regions_monde[region]
            for cle_param, regions in {
                "moyen_orient": ["Middle East"],
                "europe": ["Europe"],
                "amerique": ["South America", "North America"],
                "afrique": ["Africa"],
                "asie": ["Asia"],
            }.items()
            if self.parametres.get(cle_param, False)
            for region in regions
        }

        if self.parametres.get("autres_regions", False):
            self.liste_regions_temp.update(
                {
                    k: v
                    for k, v in self.constantes.liste_regions_monde.items()
                    if k not in set(self.liste_regions_temp.keys())
                }
            )

        dict_regions = self.parametres["dictionnaire_regions"]
        if self.parametres["dictionnaire_departements"] is not None:
            if self.parametres["dictionnaire_departements"] != {} and dict_regions is not None:
                dict_regions = {
                    k: v
                    for k, v in self.parametres["dictionnaire_regions"].items()
                    if k not in self.parametres["dictionnaire_departements"]
                }

        if self.parametres["dictionnaire_departements"] == {}:
            self.parametres["dictionnaire_departements"] = None
        if dict_regions == {}:
            dict_regions = None

        self.nb_graphes.emit(
            self.calculer_nb_total_graphes(
                dict_regions=dict_regions,
                dict_departement=self.parametres["dictionnaire_departements"],
            )
        )

        # --- Partie calcul cartes ---
        tracker = TrackerPays()
        tracker.tracker_pays_en_cours.connect(self.tracker_signal.emit)

        cree_graphe_depuis_debut(
            liste_dfs=self.parametres["liste_dfs"],
            liste_dicts=[dict_regions, self.parametres["dictionnaire_departements"]],
            gdf_eau=self.constantes.gdf_lacs,
            noms_pays=self.constantes.pays_differentes_langues,
            dictionnaire_pays_unis=self.constantes.liste_pays_groupes,
            nom_indiv=self.parametres["nom"],
            direction_resultat=self.parametres["dossier_stockage"],
            langue=self.parametres["langue"],
            granularite_visite=granularite,
            granularite_reste={"Pays": 0, "Région": 1}.get(
                self.parametres.get("granularite_fond"), 2
            ),
            theme=self.constantes.liste_ambiances[self.parametres["theme"]],
            teinte=self.constantes.liste_couleurs[self.parametres["couleur"]],
            couleur_fond="#CDEAF7" if self.parametres["couleur_fond_carte"] else "#FFFFFF",
            couleur_non_visites="#ECEBED",
            couleur_lacs="#CEE3F5",
            format=self.parametres["format"],
            qualite=self.parametres["qualite"],
            carte_du_monde=self.parametres["carte_du_monde"],
            liste_regions=self.liste_regions_temp,
            pays_individuel=self.parametres["cartes_des_pays"],
            max_cartes_additionnelles=self.parametres["max_cartes_additionnelles"],
            sortir_cartes_granu_inf=self.parametres["sortir_cartes_granu_inf"],
            tracker=tracker,
            blabla=False,
            afficher_nom_lieu=False,
        )

        self.finished.emit()

    def calculer_nb_total_graphes(self, dict_regions, dict_departement):

        return (
            (
                (len(list(dict_regions.keys())) if dict_regions is not None else 0)
                + (len(list(dict_departement.keys())) if dict_departement is not None else 0)
            )
            * self.parametres["cartes_des_pays"]
            * (
                {"Pays": 0, "Région": 1, "Département": 2}.get(
                    self.parametres.get("granularite"), -1
                )
                != 0
            )
            + len(self.liste_regions_temp)
            + int(self.parametres["carte_du_monde"])
        )


# class OngletParametres(QWidget):

#     def __init__(self, sauvegarde):

#         super().__init__()

#         layout = QVBoxLayout()

#         # Créer un label comme titre
#         self.titre = QLabel()
#         self.titre.setStyleSheet(
#             "font-size: 24px; font-weight: bold; text-align: center; font-family: Vivaldi, sans-serif;"
#         )

#         # Layout vertical
#         layout.addWidget(self.titre)  # Ajouter le titre en haut

#         self.setLayout(layout)

#         self.groupe_params_individu = QGroupBox()

#         # Layout horizontal pour organiser les éléments dans la boîte
#         layout_params_individu = QHBoxLayout()

#         # Champ de texte pour le nom de l'individu
#         self.nom_individu = QComboBox(self)
#         self.nom_individu.setEditable(True)
#         self.nom_individu.setPlaceholderText(" ")
#         self.nom_individu.addItems(list(sauvegarde.keys()))
#         layout_params_individu.addWidget(self.nom_individu)

#         # Bouton pour choisir le dossier de stockage
#         self.dossier_stockage = None
#         self.dossier_stockage_bouton = QPushButton()
#         self.dossier_stockage_bouton.clicked.connect(self.choisir_dossier)
#         self.dossier_stockage_bouton.clicked.connect(lambda: self.maj_langue_interface(False))
#         layout_params_individu.addWidget(self.dossier_stockage_bouton)

#         # Choix de la langue
#         self.label_langue = creer_QLabel_centre()
#         self.langue_utilisee = QComboBox()
#         self.langue_utilisee.addItems(
#             ["Français", "English"]
#             + sorted(
#                 langue
#                 for langue in constantes.dict_langues_dispo.values()
#                 if langue not in {"Français", "English"}
#             )
#         )
#         layout_params_individu.addWidget(self.label_langue)
#         layout_params_individu.addWidget(self.langue_utilisee)
#         self.langue_utilisee.currentIndexChanged.connect(lambda: self.maj_langue_interface(True))

#         # Ajout de la possibilité de supprimer un profil
#         layout_params_individu.addWidget(creer_ligne_verticale())
#         self.suppression_profil = QPushButton()
#         self.suppression_profil.clicked.connect(
#             lambda: self.supprimer_clef(self.nom_individu.currentText())
#         )
#         self.suppression_profil.setStyleSheet(
#             style_bouton_de_suppression(
#                 sombre=constantes.parametres_application["interface_foncee"]
#             )
#         )
#         layout_params_individu.addWidget(self.suppression_profil)

#         # Ajouter le layout à la group box et la group box au layout général
#         self.groupe_params_individu.setLayout(layout_params_individu)
#         layout.addWidget(self.groupe_params_individu)

#         # Créer un QGroupBox pour les choix de granularité
#         self.groupe_granularite = QGroupBox()

#         # Choix de la granularité
#         self.label_granularite_visite = creer_QLabel_centre()

#         self.granularite_visite = QComboBox()
#         layout_granularite_visite = QHBoxLayout()
#         layout_granularite_visite.addWidget(self.label_granularite_visite)
#         layout_granularite_visite.addWidget(self.granularite_visite)
#         layout_granularite_visite.addWidget(creer_ligne_verticale())

#         # Granularité de fond
#         self.label_granularite_fond = creer_QLabel_centre()
#         self.granularite_fond = QComboBox()
#         layout_granularite_fond = QHBoxLayout()
#         layout_granularite_fond.addWidget(self.label_granularite_fond)
#         layout_granularite_fond.addWidget(self.granularite_fond)

#         # Ajouter le layout horizontal à la group box
#         layout_granularite = QHBoxLayout()
#         layout_granularite.addLayout(layout_granularite_visite)
#         layout_granularite.addLayout(layout_granularite_fond)
#         self.groupe_granularite.setLayout(layout_granularite)
#         layout.addWidget(self.groupe_granularite)

#         # Création des cases à cocher
#         self.groupe_cartes_a_creer = QGroupBox()
#         self.carte_monde = QCheckBox()
#         self.carte_pays = QCheckBox()

#         self.europe = QCheckBox()
#         self.asie = QCheckBox()
#         self.amerique = QCheckBox()

#         self.afrique = QCheckBox()
#         self.moyen_orient = QCheckBox()
#         self.autres_regions = QCheckBox()

#         self.sortir_cartes_granu_inf = QCheckBox()

#         self.carte_pays.setChecked(True)
#         self.europe.setChecked(True)

#         # Création du layout des cartes à créer et des couleurs
#         layout_cartes_et_couleurs = QHBoxLayout()

#         # Layout des cartes à créer
#         layout_cartes_a_creer = QGridLayout()
#         layout_cartes_a_creer.addWidget(
#             self.carte_monde, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter
#         )
#         layout_cartes_a_creer.addWidget(
#             self.carte_pays, 0, 3, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter
#         )

#         layout_cartes_a_creer.addLayout(
#             creer_ligne_separation(lStretch=0, ligne_largeur=1, rStretch=0),
#             1,
#             0,
#             1,
#             6,
#         )

#         ligne_regions_1 = 2
#         layout_cartes_a_creer.addWidget(self.afrique, ligne_regions_1, 0, 1, 2)
#         layout_cartes_a_creer.addWidget(self.amerique, ligne_regions_1, 2, 1, 2)
#         layout_cartes_a_creer.addWidget(self.asie, ligne_regions_1, 4, 1, 2)

#         ligne_regions_1 = 3
#         layout_cartes_a_creer.addWidget(self.europe, ligne_regions_1, 0, 1, 2)
#         layout_cartes_a_creer.addWidget(self.moyen_orient, ligne_regions_1, 2, 1, 2)
#         layout_cartes_a_creer.addWidget(self.autres_regions, ligne_regions_1, 4, 1, 2)

#         layout_cartes_a_creer.addLayout(
#             creer_ligne_separation(lStretch=0, ligne_largeur=1, rStretch=0),
#             4,
#             0,
#             1,
#             6,
#         )

#         layout_cartes_a_creer.addWidget(
#             self.sortir_cartes_granu_inf,
#             5,
#             0,
#             1,
#             6,
#             alignment=Qt.AlignmentFlag.AlignCenter,
#         )

#         widget_nb_copies_cartes = QWidget()
#         radio_layout = QHBoxLayout()
#         radio_layout.setContentsMargins(0, 0, 0, 0)
#         radio_layout.setSpacing(10)
#         widget_nb_copies_cartes.setLayout(radio_layout)

#         # Titre (centré verticalement)
#         self.label_nb_copies_cartes = creer_QLabel_centre()

#         # Création des boutons radio avec noms clairs
#         self.radio_carte_1 = QRadioButton()
#         self.radio_carte_2 = QRadioButton()
#         self.radio_carte_3 = QRadioButton()
#         self.radio_carte_sans_limite = QRadioButton()

#         # Option par défaut
#         self.radio_carte_2.setChecked(True)

#         # Groupe exclusif
#         self.groupe_radio_max_cartes = QButtonGroup(self)
#         self.groupe_radio_max_cartes.addButton(self.radio_carte_1, 1)
#         self.groupe_radio_max_cartes.addButton(self.radio_carte_2, 2)
#         self.groupe_radio_max_cartes.addButton(self.radio_carte_3, 3)
#         self.groupe_radio_max_cartes.addButton(self.radio_carte_sans_limite, -1)

#         # Ajout au layout horizontal
#         radio_layout.addWidget(self.label_nb_copies_cartes)
#         radio_layout.addWidget(self.radio_carte_1)
#         radio_layout.addWidget(self.radio_carte_2)
#         radio_layout.addWidget(self.radio_carte_3)
#         radio_layout.addWidget(self.radio_carte_sans_limite)

#         # Ajout du layout au QGroupBox puis ajout au layout principal
#         self.groupe_cartes_a_creer.setLayout(layout_cartes_a_creer)
#         layout_granu_cartes_a_creer = QVBoxLayout()
#         layout_granu_cartes_a_creer.addWidget(self.groupe_granularite)
#         layout_granu_cartes_a_creer.addWidget(self.groupe_cartes_a_creer)
#         # layout.addWidget(self.groupe_cartes_a_creer)

#         # Boîte des couleurs
#         self.groupe_couleurs = QGroupBox()
#         layout_theme_couleurs = QVBoxLayout()

#         # Choix du thème
#         self.theme_label = creer_QLabel_centre()
#         self.theme_combo = QComboBox()
#         self.theme_combo.currentTextChanged.connect(self.maj_style)
#         layout_theme = QHBoxLayout()
#         layout_theme.addWidget(self.theme_label)
#         layout_theme.addWidget(self.theme_combo)

#         # Choix des couleurs
#         self.color_label = creer_QLabel_centre()
#         self.color_combo = QComboBox()
#         self.color_combo.currentTextChanged.connect(self.maj_style)
#         layout_couleurs = QHBoxLayout()
#         layout_couleurs.addWidget(self.color_label)
#         layout_couleurs.addWidget(self.color_combo)

#         # Utilisation ou non du thème dans l'interface
#         self.utiliser_theme = QCheckBox()
#         self.utiliser_theme.stateChanged.connect(self.maj_style)

#         # Choix de la couleur de fond
#         self.couleur_fond_checkbox = QCheckBox()

#         # Ajout des widgets au layout vertical
#         layout_theme_couleurs.addLayout(layout_theme)
#         layout_theme_couleurs.addLayout(layout_couleurs)
#         layout_theme_couleurs.addWidget(self.utiliser_theme)
#         layout_theme_couleurs.addLayout(
#             creer_ligne_separation(lStretch=0, ligne_largeur=1, rStretch=0)
#         )
#         layout_theme_couleurs.addWidget(
#             self.couleur_fond_checkbox, alignment=Qt.AlignmentFlag.AlignHCenter
#         )

#         # Ajout du layout de couleurs au groupbox et ajout du groupbox au layout principal
#         self.groupe_couleurs.setLayout(layout_theme_couleurs)

#         # # Ajout des groupbox des cartes et des couleurs
#         layout_cartes_et_couleurs.addLayout(layout_granu_cartes_a_creer)
#         layout_cartes_et_couleurs.addWidget(self.groupe_couleurs)

#         # # Ajouter ce layout horizontal au layout principal
#         layout.addLayout(layout_cartes_et_couleurs)

#         # Group box et layout des paramètres de publication
#         self.groupe_params_publication = QGroupBox()
#         layout_params_publication = QVBoxLayout()

#         # Layout horizontal pour la qualité de l'image et le format
#         layout_format_qualite = QHBoxLayout()

#         # Curseur pour la qualité de l’image
#         self.label_qualite = creer_QLabel_centre()
#         self.label_qualite_min = creer_QLabel_centre()
#         self.label_qualite_max = creer_QLabel_centre()
#         self.curseur_qualite = QSlider(Qt.Orientation.Horizontal)
#         self.curseur_qualite.setMinimum(constantes.parametres_application["qualite_min"])
#         self.curseur_qualite.setMaximum(constantes.parametres_application["qualite_max"])
#         self.curseur_qualite.setValue(
#             int(
#                 (
#                     constantes.parametres_application["qualite_min"]
#                     + constantes.parametres_application["qualite_max"]
#                 )
#                 / 2
#             )
#         )

#         # Choix du format d'image
#         self.label_format = creer_QLabel_centre()
#         self.format_cartes = QComboBox()
#         self.format_cartes.addItems(["png", "jpg", "svg", "pdf", "tif", "webp", "raw", "ps"])

#         # Ajout des widgets au layout horizontal
#         layout_format_qualite.addWidget(self.label_format)
#         layout_format_qualite.addWidget(self.format_cartes)
#         layout_format_qualite.addItem(
#             QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
#         )
#         layout_format_qualite.addWidget(self.label_qualite)
#         layout_format_qualite.addWidget(self.label_qualite_min)
#         layout_format_qualite.addWidget(self.curseur_qualite)
#         layout_format_qualite.addWidget(self.label_qualite_max)

#         # Ajouter le layout horizontal au layout principal
#         layout_params_publication.addLayout(layout_format_qualite)
#         layout_params_publication.addWidget(widget_nb_copies_cartes)
#         # Ajouter le layout principal à la group box
#         self.groupe_params_publication.setLayout(layout_params_publication)

#         # Ajouter le QGroupBox au layout principal
#         layout.addWidget(self.groupe_params_publication)

#         # Bouton de validation
#         layout_valid_reinit = QGridLayout()

#         # Création du bouton "Créer cartes"
#         self.creation_cartes_bouton = QPushButton()
#         self.creation_cartes_bouton.clicked.connect(lambda: self.fonction_principale(False))
#         self.barre_progression = QProgressBar()
#         self.barre_progression.setMinimum(0)
#         self.barre_progression.setValue(0)
#         self.barre_progression.setFormat("")

#         # Bouton de sauvegarde
#         self.bouton_sauvegarde = QPushButton()
#         self.bouton_sauvegarde.clicked.connect(lambda: self.fonction_principale(True))

#         # Bouton de réinitialisation
#         self.reinit_parametres = QPushButton()
#         self.reinit_parametres.clicked.connect(lambda: self.reinitialisation_parametres(True))
#         self.reinit_parametres.clicked.connect(lambda: self.maj_langue_interface(True))
#         self.reinit_parametres.setStyleSheet(
#             style_bouton_de_suppression(
#                 sombre=constantes.parametres_application["interface_foncee"]
#             )
#         )

#         # Ajouter les widgets dans la grille
#         layout_valid_reinit.addWidget(self.reinit_parametres, 0, 0)
#         layout_valid_reinit.addWidget(self.creation_cartes_bouton, 0, 1)
#         layout_valid_reinit.addWidget(self.barre_progression, 0, 1)
#         self.barre_progression.setVisible(False)
#         layout_valid_reinit.addWidget(self.bouton_sauvegarde, 0, 2)

#         # Ajuster les proportions : colonne 1 (droite) prend plus de place
#         layout_valid_reinit.setColumnStretch(0, 1)  # petite colonne gauche
#         layout_valid_reinit.setColumnStretch(1, 4)  # plus grande colonne au milieu
#         layout_valid_reinit.setColumnStretch(2, 1)  # petite colonne à gauche

#         layout.addLayout(layout_valid_reinit)
#         self.setLayout(layout)
