################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1 – Création de l'onglet complet                                      #
################################################################################


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
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_1_creation_cartes import CreerCartes
from _0_Utilitaires._0_1_Fonctions_utiles import (
    creer_ligne_verticale,
    creer_ligne_separation,
    creer_QLabel_centre,
    style_bouton_de_suppression,
    obtenir_clef_par_valeur,
    reset_combo,
)


class OngletParametres(QWidget):

    envoi_dossier = pyqtSignal(str)

    def __init__(self, gdf_eau, constantes, liste_individus, fct_traduction, fct_pop_up):

        super().__init__()

        self.gdf_eau = gdf_eau
        self.constantes = constantes
        self.fonction_traduction = fct_traduction
        self.fonction_pop_up = fct_pop_up

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
        self.nom_individu.addItems(liste_individus)
        layout_params_individu.addWidget(self.nom_individu)

        # Bouton pour choisir le dossier de stockage
        self.dossier_stockage = None
        self.dossier_stockage_bouton = QPushButton()
        self.dossier_stockage_bouton.clicked.connect(self.choisir_dossier)
        layout_params_individu.addWidget(self.dossier_stockage_bouton)

        # Choix de la langue
        self.label_langue = creer_QLabel_centre()
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

        # Ajout de la possibilité de supprimer un profil
        layout_params_individu.addWidget(creer_ligne_verticale())
        self.suppression_profil = QPushButton()
        self.suppression_profil.setStyleSheet(
            style_bouton_de_suppression(
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
        self.label_granularite_visite = creer_QLabel_centre()

        self.granularite_visite = QComboBox()
        layout_granularite_visite = QHBoxLayout()
        layout_granularite_visite.addWidget(self.label_granularite_visite)
        layout_granularite_visite.addWidget(self.granularite_visite)
        layout_granularite_visite.addWidget(creer_ligne_verticale())

        # Granularité de fond
        self.label_granularite_fond = creer_QLabel_centre()
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
            creer_ligne_separation(lStretch=0, ligne_largeur=1, rStretch=0),
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
            creer_ligne_separation(lStretch=0, ligne_largeur=1, rStretch=0),
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
        self.label_nb_copies_cartes = creer_QLabel_centre()

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
        self.theme_label = creer_QLabel_centre()
        self.theme_combo = QComboBox()
        # self.theme_combo.currentTextChanged.connect(self.maj_style)
        layout_theme = QHBoxLayout()
        layout_theme.addWidget(self.theme_label)
        layout_theme.addWidget(self.theme_combo)

        # Choix des couleurs
        self.color_label = creer_QLabel_centre()
        self.color_combo = QComboBox()
        # self.color_combo.currentTextChanged.connect(self.maj_style)
        layout_couleurs = QHBoxLayout()
        layout_couleurs.addWidget(self.color_label)
        layout_couleurs.addWidget(self.color_combo)

        # Utilisation ou non du thème dans l'interface
        self.utiliser_theme = QCheckBox()
        # self.utiliser_theme.stateChanged.connect(self.maj_style)

        # Choix de la couleur de fond
        self.couleur_fond_checkbox = QCheckBox()

        # Ajout des widgets au layout vertical
        layout_theme_couleurs.addLayout(layout_theme)
        layout_theme_couleurs.addLayout(layout_couleurs)
        layout_theme_couleurs.addWidget(self.utiliser_theme)
        layout_theme_couleurs.addLayout(
            creer_ligne_separation(lStretch=0, ligne_largeur=1, rStretch=0)
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
        self.label_qualite = creer_QLabel_centre()
        self.label_qualite_min = creer_QLabel_centre()
        self.label_qualite_max = creer_QLabel_centre()
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
        self.label_format = creer_QLabel_centre()
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
        self.barre_progression = QProgressBar()
        self.barre_progression.setMinimum(0)
        self.barre_progression.setValue(0)
        self.barre_progression.setFormat("")

        # Bouton de sauvegarde
        self.bouton_sauvegarde = QPushButton()

        # Bouton de réinitialisation
        self.reinit_parametres = QPushButton()
        self.reinit_parametres.setStyleSheet(
            style_bouton_de_suppression(
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
        self.setLayout(layout)

    def set_langue(self):

        # Récupération de la langue
        langue_actuelle = obtenir_clef_par_valeur(
            dictionnaire=self.constantes.dict_langues_dispo,
            valeur=self.langue_utilisee.currentText(),
        )

        if langue_actuelle is None:
            return

        # Paramètres de l'individu
        self.groupe_params_individu.setTitle(self.fonction_traduction("titre_params_individu"))
        # self.dossier_stockage_bouton.setText(
        #     self.fonction_traduction("dossier_stockage_individu")
        #     if self.dossier_stockage is None
        #     else os.sep.join(os.path.normpath(self.dossier_stockage).split(os.sep)[-3:])
        # )
        self.set_dossier(dossier=self.dossier_stockage)
        self.label_langue.setText(
            self.fonction_traduction(clef="langue_individu", suffixe=" :")
        )
        self.suppression_profil.setText(self.fonction_traduction("supprimer_profil"))

        # Granularité des cartes
        self.groupe_granularite.setTitle(self.fonction_traduction("titre_granularite"))
        self.label_granularite_visite.setText(
            self.fonction_traduction("granularite_pays_visites", suffixe=" :")
        )
        self.label_granularite_fond.setText(
            self.fonction_traduction("granularite_pays_non_visites", suffixe=" :")
        )

        # Choix des cartes à publier
        self.groupe_cartes_a_creer.setTitle(self.fonction_traduction("titre_cartes_a_publier"))
        self.carte_pays.setText(self.fonction_traduction("cartes_pays_visites"))
        self.carte_monde.setText(self.fonction_traduction("carte_du_monde"))
        self.afrique.setText(self.fonction_traduction("afrique"))
        self.amerique.setText(self.fonction_traduction("amerique"))
        self.asie.setText(self.fonction_traduction("asie"))
        self.europe.setText(self.fonction_traduction("europe"))
        self.moyen_orient.setText(self.fonction_traduction("moyen_orient"))
        self.autres_regions.setText(self.fonction_traduction("autres_regions_monde"))
        self.sortir_cartes_granu_inf.setText(
            self.fonction_traduction("publier_cartes_faible_granularite_uniquement")
        )
        self.sortir_cartes_granu_inf.setToolTip(
            self.fonction_traduction(
                clef="description_publier_cartes_faible_granularite_uniquement",
                largeur_max=None,
            )
        )

        # Paramètres visuels
        self.groupe_couleurs.setTitle(self.fonction_traduction("titre_params_esthetiques"))
        self.color_label.setText(
            self.fonction_traduction(clef="cartes_couleurs", suffixe=" :")
        )
        self.theme_label.setText(self.fonction_traduction(clef="cartes_theme", suffixe=" :"))
        self.utiliser_theme.setText(self.fonction_traduction("tick_style_dans_app"))
        self.utiliser_theme.setToolTip(
            self.fonction_traduction("description_tick_style_dans_app", suffixe=".")
        )

        self.couleur_fond_checkbox.setText(
            self.fonction_traduction(clef="cartes_couleurs_fond", suffixe="")
        )
        self.couleur_fond_checkbox.setToolTip(
            self.fonction_traduction(clef="cartes_couleurs_fond_tool_tip", suffixe=".")
        )

        # Paramètres de format et de qualité
        self.groupe_params_publication.setTitle(
            self.fonction_traduction("titre_params_techniques")
        )
        self.label_format.setText(self.fonction_traduction("cartes_format", suffixe=" :"))
        self.label_qualite.setText(self.fonction_traduction("cartes_qualite", suffixe=" :"))
        self.label_qualite_max.setText(self.fonction_traduction("qualite_elevee"))
        self.label_qualite_min.setText(self.fonction_traduction("qualite_faible"))
        self.label_nb_copies_cartes.setText(
            self.fonction_traduction("nombre_exemplaires_cartes", suffixe=" : ")
        )
        self.label_nb_copies_cartes.setToolTip(
            self.fonction_traduction("description_nombre_exemplaires_cartes", suffixe=".")
        )
        self.radio_carte_1.setText(self.fonction_traduction("cinq_cartes"))
        self.radio_carte_2.setText(self.fonction_traduction("dix_cartes"))
        self.radio_carte_3.setText(self.fonction_traduction("quinze_cartes"))
        self.radio_carte_sans_limite.setText(
            self.fonction_traduction("pas_de_limite_de_cartes")
        )

        # Boutons en bas de l'onglet 1
        self.reinit_parametres.setText(self.fonction_traduction("reinitialisation_interface"))
        self.reinit_parametres.setToolTip(
            self.fonction_traduction(
                "description_bouton_reinitialisation_interface", suffixe="."
            )
        )
        self.creation_cartes_bouton.setText(self.fonction_traduction("bouton_publier_cartes"))
        self.creation_cartes_bouton.setToolTip(
            self.fonction_traduction("description_bouton_publier_cartes", suffixe=".")
        )
        self.bouton_sauvegarde.setText("💾")
        self.bouton_sauvegarde.setToolTip(
            self.fonction_traduction("sauvegarder_profil", suffixe=".")
        )

        # Mise à jour des listes déroulantes
        liste_granularite = [
            self.constantes.parametres_traduits["granularite"][langue_actuelle][k]
            for k in ["Pays", "Région", "Département", "Amusant"]
        ]
        reset_combo(combo=self.granularite_visite, items=liste_granularite)
        reset_combo(combo=self.granularite_fond, items=liste_granularite[:-1])

        # Mise à jour des teintes
        reset_combo(
            combo=self.color_combo,
            items=sorted(
                self.constantes.parametres_traduits["teintes_couleurs"]
                .get(langue_actuelle, {})
                .values()
            ),
        )

        # Mise à jour de l'ambiance
        reset_combo(
            self.theme_combo,
            sorted(
                self.constantes.parametres_traduits["themes_cartes"]
                .get(langue_actuelle, {})
                .values()
            ),
        )

    def set_dossier(self, dossier):

        self.dossier_stockage = dossier
        self.dossier_stockage_bouton.setText(
            self.fonction_traduction("dossier_stockage_individu")
            if self.dossier_stockage is None
            else os.sep.join(os.path.normpath(self.dossier_stockage).split(os.sep)[-3:])
        )
        self.envoi_dossier.emit(self.dossier_stockage)

    def choisir_dossier(self):
        dossier = QFileDialog.getExistingDirectory(
            self, self.fonction_traduction("dossier_stockage_pop_up")
        )
        if dossier:
            self.set_dossier(dossier=dossier)
            self.set_langue()

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

        self.fonction_pop_up(
            contenu=self.fonction_traduction(
                clef=("debut_publication_cartes" if debut else "publication_cartes_reussie"),
                suffixe="." if debut else " ✅​",
            ),
            temps_max=5000 if debut else None,
            titre=self.fonction_traduction(clef="titre_pop_up_publication_cartes"),
        )

    def set_emoji_sauvegarde(self):
        self.bouton_sauvegarde.setText("💾✅")
        QTimer.singleShot(3000, lambda: self.bouton_sauvegarde.setText("💾"))

    def fonction_principale(self, settings):

        if (
            settings["dictionnaire_regions"] is None
            and settings["dictionnaire_departements"] is None
        ):

            self.fonction_pop_up(
                contenu=self.fonction_traduction("pop_up_aucun_lieu_coche", suffixe="."),
                titre=self.fonction_traduction("pop_up_probleme_titre", suffixe="."),
                temps_max=10000,
            )

        elif settings["dossier_stockage"] is None:

            self.fonction_pop_up(
                contenu=self.fonction_traduction(
                    "pop_up_pas_de_dossier_de_stockage",
                    suffixe=".",
                ),
                titre=self.fonction_traduction("pop_up_probleme_titre", suffixe="."),
                temps_max=10000,
            )

        else:

            # Initialisation de l'objet et de la barre de progression
            self.creation_cartes = CreerCartes(
                gdf_eau=self.gdf_eau, params=settings, constantes=self.constantes
            )
            self.creation_cartes.nb_graphes.connect(self.initialiser_progression)
            self.creation_cartes.tracker_signal.connect(self.afficher_avancement)

            self.thread_temp = QThread()
            self.creation_cartes.moveToThread(self.thread_temp)

            self.creation_cartes.finished.connect(self.thread_temp.quit)
            self.creation_cartes.finished.connect(self.creation_cartes.deleteLater)
            self.thread_temp.finished.connect(self.thread_temp.deleteLater)
            self.thread_temp.finished.connect(
                lambda: self.debut_fin_creation_cartes(debut=False)
            )

            self.thread_temp.started.connect(self.creation_cartes.run)
            self.thread_temp.start()
