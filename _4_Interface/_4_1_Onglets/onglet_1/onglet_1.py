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
    QSlider,
    QGroupBox,
    QProgressBar,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QThread

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    charger_gdfs,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    reset_combo,
    creer_QLabel_centre,
    creer_ligne_horizontale,
    creer_ligne_verticale,
    restaurer_valeur_combo,
    set_emoji_sauvegarde,
)
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_1_creation_cartes import CreerCartes
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_2_combobox_coloree import (
    FondCarteCombo,
)
from _4_Interface._4_2_Style._4_2_2_styles_complementaires import (
    style_bouton_de_suppression,
)


class OngletParametres(QWidget):

    def __init__(self, constantes, fct_traduction, fct_pop_up):

        super().__init__()

        self.constantes = constantes
        self.fonction_traduction = fct_traduction
        self.fonction_pop_up = fct_pop_up
        self.langue = "français"
        self.liste_gdfs = []

        layout = QVBoxLayout()

        # Créer un label comme titre
        self.titre = QLabel()
        self.set_style_titre(taille=24)

        # Layout vertical
        layout.addWidget(self.titre, stretch=2)  # Ajouter le titre en haut

        self.setLayout(layout)

        # Ajouter le layout à la group box et la group box au layout général

        # Créer un QGroupBox pour les choix de granularité
        self.groupe_granularite = QGroupBox()

        # Choix de la granularité
        self.label_granularite_visite = creer_QLabel_centre()

        self.granularite_visite = QComboBox()
        layout_granularite_visite = QHBoxLayout()
        layout_granularite_visite.addWidget(self.label_granularite_visite, stretch=2)
        layout_granularite_visite.addWidget(self.granularite_visite, stretch=4)

        # Granularité de fond
        self.label_granularite_fond = creer_QLabel_centre()
        self.granularite_fond = QComboBox()
        layout_granularite_fond = QHBoxLayout()
        layout_granularite_fond.addWidget(self.label_granularite_fond, stretch=2)
        layout_granularite_fond.addWidget(self.granularite_fond, stretch=4)

        # Ajouter le layout horizontal à la group box
        layout_granularite = QHBoxLayout()
        layout_granularite.addLayout(layout_granularite_visite, stretch=5)
        layout_granularite.addWidget(creer_ligne_verticale(), stretch=2)
        layout_granularite.addLayout(layout_granularite_fond, stretch=5)
        self.groupe_granularite.setLayout(layout_granularite)
        layout.addWidget(self.groupe_granularite, stretch=3)

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

        layout_cartes_a_creer.addWidget(
            creer_ligne_horizontale(lStretch=0, ligne_largeur=1, rStretch=0),
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

        # Ajout du layout au QGroupBox puis ajout au layout principal
        self.groupe_cartes_a_creer.setLayout(layout_cartes_a_creer)
        layout_granu_cartes_a_creer = QVBoxLayout()
        layout_granu_cartes_a_creer.addWidget(self.groupe_granularite, stretch=3)
        layout_granu_cartes_a_creer.addWidget(self.groupe_cartes_a_creer, stretch=5)
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
        layout_couleur_fond = QHBoxLayout()
        self.couleur_fond_label = QLabel()
        self.combo_couleur_fond = FondCarteCombo(constantes=self.constantes)
        layout_couleur_fond.addWidget(
            self.couleur_fond_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        layout_couleur_fond.addWidget(
            self.combo_couleur_fond, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        # Ajout des widgets au layout vertical
        layout_theme_couleurs.addLayout(layout_theme)
        layout_theme_couleurs.addLayout(layout_couleurs)
        layout_theme_couleurs.addWidget(
            self.utiliser_theme, alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout_theme_couleurs.addWidget(
            creer_ligne_horizontale(lStretch=0, ligne_largeur=1, rStretch=0)
        )
        layout_theme_couleurs.addLayout(layout_couleur_fond)

        # Ajout du layout de couleurs au groupbox et ajout du groupbox au layout principal
        self.groupe_couleurs.setLayout(layout_theme_couleurs)

        # # Ajout des groupbox des cartes et des couleurs
        layout_cartes_et_couleurs.addLayout(layout_granu_cartes_a_creer)
        layout_cartes_et_couleurs.addWidget(self.groupe_couleurs)

        # # Ajouter ce layout horizontal au layout principal
        layout.addLayout(layout_cartes_et_couleurs, stretch=8)

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
        self.curseur_qualite_min = self.constantes.parametres_application.get(
            "qualite_min", 100
        )
        self.curseur_qualite_max = self.constantes.parametres_application.get(
            "qualite_max", 4500
        )
        self.curseur_qualite.setMinimum(self.curseur_qualite_min)
        self.curseur_qualite.setMaximum(self.curseur_qualite_max)
        self.curseur_qualite.setValue(
            int((self.curseur_qualite_min + self.curseur_qualite_max) / 2)
        )

        # Choix du format d'image
        self.label_format = creer_QLabel_centre()
        self.format_cartes = QComboBox()
        self.format_cartes.addItems(
            ["png", "jpg", "svg", "pdf", "tif", "webp", "raw", "ps"]
        )

        # Possibilité d'envoi par e-mail
        self.email_checkbox = QCheckBox()

        # Ajout des widgets au layout horizontal
        layout_format_qualite.addWidget(self.label_format)
        layout_format_qualite.addWidget(self.format_cartes)
        layout_format_qualite.addItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )
        layout_format_qualite.addWidget(self.label_qualite)
        layout_format_qualite.addWidget(self.label_qualite_min)
        layout_format_qualite.addWidget(self.curseur_qualite)
        layout_format_qualite.addWidget(self.label_qualite_max)
        layout_format_qualite.addItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )
        layout_format_qualite.addWidget(self.email_checkbox)

        # Ajouter le layout horizontal au layout principal
        layout_params_publication.addLayout(layout_format_qualite)
        # Ajouter le layout principal à la group box
        self.groupe_params_publication.setLayout(layout_params_publication)

        # Ajouter le QGroupBox au layout principal
        layout.addWidget(self.groupe_params_publication, stretch=3)

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
        self.bouton_sauvegarde.clicked.connect(
            lambda: set_emoji_sauvegarde(self.bouton_sauvegarde, 3000)
        )

        # Bouton de réinitialisation
        self.reinit_parametres = QPushButton()

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

        layout.addLayout(layout_valid_reinit, stretch=1)
        self.setLayout(layout)

    def set_langue(self, langue: str | None):

        # Récupération de la langue
        self.langue = langue

        # Titre
        self.titre.setText(
            self.fonction_traduction(
                clef="titre_application",
                suffixe=self.constantes.dict_themes_temporaires.get("emoji", ""),
            )
        )

        if self.langue is None:
            return

        # Granularité des cartes
        self.groupe_granularite.setTitle(self.fonction_traduction("titre_granularite"))
        self.label_granularite_visite.setText(
            self.fonction_traduction("granularite_pays_visites", suffixe=" :")
        )
        self.label_granularite_fond.setText(
            self.fonction_traduction("granularite_pays_non_visites", suffixe=" :")
        )

        # Choix des cartes à publier
        self.groupe_cartes_a_creer.setTitle(
            self.fonction_traduction("titre_cartes_a_publier")
        )
        self.carte_pays.setText(self.fonction_traduction("cartes_pays_visites"))
        self.carte_monde.setText(self.fonction_traduction("carte_du_monde"))
        self.afrique.setText(self.fonction_traduction("afrique"))
        self.amerique.setText(self.fonction_traduction("amerique"))
        self.asie.setText(self.fonction_traduction("asie"))
        self.europe.setText(self.fonction_traduction("europe"))
        self.moyen_orient.setText(self.fonction_traduction("moyen_orient"))
        self.autres_regions.setText(self.fonction_traduction("autres_regions_monde"))

        # Paramètres visuels
        self.groupe_couleurs.setTitle(
            self.fonction_traduction("titre_params_esthetiques")
        )
        self.color_label.setText(
            self.fonction_traduction(clef="cartes_couleurs", suffixe=" :")
        )
        self.theme_label.setText(
            self.fonction_traduction(clef="cartes_theme", suffixe=" :")
        )
        self.utiliser_theme.setText(self.fonction_traduction("tick_style_dans_app"))
        self.utiliser_theme.setToolTip(
            self.fonction_traduction("description_tick_style_dans_app", suffixe=".")
        )

        self.couleur_fond_label.setText(
            self.fonction_traduction("cartes_couleurs_fond", suffixe=" :")
        )
        self.couleur_fond_label.setToolTip(
            self.fonction_traduction(clef="cartes_couleurs_fond_tool_tip", suffixe=".")
        )
        self.combo_couleur_fond.set_langue(langue=self.langue, taille=20)

        # Paramètres de format et de qualité
        self.groupe_params_publication.setTitle(
            self.fonction_traduction("titre_params_techniques")
        )
        self.label_format.setText(
            self.fonction_traduction("cartes_format", suffixe=" :")
        )
        self.label_qualite.setText(
            self.fonction_traduction("cartes_qualite", suffixe=" :")
        )
        self.label_qualite_max.setText(self.fonction_traduction("qualite_elevee"))
        self.label_qualite_min.setText(self.fonction_traduction("qualite_faible"))

        # Envoi par e-mail
        self.email_checkbox.setText("✉️​")
        self.email_checkbox.setToolTip(
            self.fonction_traduction("email_checkbox_tooltip", suffixe=".")
        )

        # Boutons en bas de l'onglet 1
        self.reinit_parametres.setText(
            self.fonction_traduction("reinitialisation_interface")
        )
        self.reinit_parametres.setToolTip(
            self.fonction_traduction(
                "description_bouton_reinitialisation_interface", suffixe="."
            )
        )
        self.creation_cartes_bouton.setText(
            self.fonction_traduction("bouton_publier_cartes")
        )
        self.creation_cartes_bouton.setToolTip(
            self.fonction_traduction("description_bouton_publier_cartes", suffixe=".")
        )
        self.bouton_sauvegarde.setText("💾")
        self.bouton_sauvegarde.setToolTip(
            self.fonction_traduction("sauvegarder_profil", suffixe=".")
        )

        # Mise à jour des listes déroulantes
        liste_granularite = [
            self.constantes.parametres_traduits["granularite"][self.langue][k]
            for k in ["Pays", "Région", "Département", "Amusant"]
        ]

        reset_combo(combo=self.granularite_visite, items=liste_granularite)
        reset_combo(combo=self.granularite_fond, items=liste_granularite[:-1])

        # Mise à jour des teintes
        reset_combo(
            combo=self.color_combo,
            items=sorted(
                self.constantes.parametres_traduits.get("teintes_couleurs", {})
                .get(self.langue, {})
                .values()
            ),
        )

        # Mise à jour de l'ambiance
        reset_combo(
            self.theme_combo,
            sorted(
                self.constantes.parametres_traduits.get("themes_cartes", {})
                .get(self.langue, {})
                .values()
            ),
        )

    def set_style(self, style: bool):
        self.reinit_parametres.setStyleSheet(style_bouton_de_suppression(sombre=style))

    def initialiser_progression(self, nb_cartes: int):

        # Initialisation de la barre de progression
        self.barre_progression.setMaximum(nb_cartes)
        self.barre_progression.setValue(0)

        # Affichage de la barre de progression
        self.debut_fin_creation_cartes(debut=True)

    def afficher_avancement(self, libelle_pays):
        self.barre_progression.setValue(self.barre_progression.value() + 1)
        self.barre_progression.setFormat(libelle_pays)

    def debut_fin_creation_cartes(self, debut):

        self.creation_cartes_bouton.setVisible(not debut)
        self.barre_progression.setVisible(debut)

        self.fonction_pop_up(
            contenu=self.fonction_traduction(
                clef=(
                    "debut_publication_cartes"
                    if debut
                    else "publication_cartes_reussie"
                ),
                suffixe="." if debut else " ✅​",
            ),
            temps_max=5000 if debut else None,
            titre=self.fonction_traduction(clef="titre_pop_up_publication_cartes"),
        )

    def fonction_principale(self, settings):

        if not settings["dictionnaire_voyages"]:

            self.fonction_pop_up(
                contenu=self.fonction_traduction(
                    "pop_up_aucun_lieu_coche", suffixe="."
                ),
                titre=self.fonction_traduction("pop_up_probleme_titre", suffixe="."),
                temps_max=10000,
            )

        elif settings["dossier_stockage"] is None:

            self.fonction_pop_up(
                titre=self.fonction_traduction("pop_up_probleme_titre", suffixe="."),
                contenu=self.fonction_traduction(
                    "pop_up_pas_de_dossier_de_stockage",
                    suffixe=".",
                ),
                temps_max=10000,
            )

        elif not os.path.exists(settings["dossier_stockage"]):

            self.fonction_pop_up(
                titre=self.fonction_traduction("pop_up_probleme_titre", suffixe="."),
                contenu=self.fonction_traduction(
                    "pop_up_dossier_de_stockage_faux",
                    suffixe=".",
                ),
                temps_max=10000,
            )

        else:

            if not self.liste_gdfs:
                self.liste_gdfs = charger_gdfs(
                    direction_base=self.constantes.direction_donnees_geographiques,
                    max_niveau=2,
                )

            # Ajout des tables géographiques
            settings["liste_dfs"] = self.liste_gdfs

            # Initialisation de l'objet et de la barre de progression
            self.creation_cartes = CreerCartes(
                params=settings, constantes=self.constantes
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

    def set_style_titre(self, taille=24):

        self.titre.setStyleSheet(
            f"font-size: {taille * self.constantes.dict_themes_temporaires.get('titre_police_coeff', 1)}px;"
            f"font-weight: bold;"
            f"text-align: center;"
            f"font-family: {self.constantes.dict_themes_temporaires.get('titre_police', 'Vivaldi')}, sans-serif;"
        )

    def initialiser_onglet(self, **kwargs):

        # Indicatrices
        checkboxes = {
            # cartes à publier
            "carte_du_monde": self.carte_monde,
            "cartes_des_pays": self.carte_pays,
            "asie": self.asie,
            "amerique": self.amerique,
            "afrique": self.afrique,
            "europe": self.europe,
            "moyen_orient": self.moyen_orient,
            "autres_regions": self.autres_regions,
            # Utilisation du thème
            "utiliser_theme": self.utiliser_theme,
            # Envoi par e-mail
            "envoi_email": self.email_checkbox,
        }
        for nom_cle, checkbox in checkboxes.items():
            checkbox.setChecked(
                kwargs.get(nom_cle)
                if kwargs.get(nom_cle) is not None
                else (nom_cle in ["europe", "cartes_des_pays"])
            )

        # Paramètres de stockage
        self.curseur_qualite.setValue(
            # Valeur passée
            kwargs.get("qualite")
            or int((self.curseur_qualite_min + self.curseur_qualite_max) / 2)
        )
        self.format_cartes.setCurrentText(kwargs.get("format") or "png")

        # Chargement de la granularité
        restaurer_valeur_combo(
            combo=self.granularite_visite,
            dict_parent=self.constantes.parametres_traduits.get("granularite", {}),
            langue=self.langue,
            valeur=kwargs.get("granularite"),
            defaut_index=0,
        )

        # Chargement de la granularité de fond
        restaurer_valeur_combo(
            combo=self.granularite_fond,
            dict_parent=self.constantes.parametres_traduits.get("granularite", {}),
            langue=self.langue,
            valeur=kwargs.get("granularite_fond"),
            defaut_index=0,
        )

        # Chargement du thème
        restaurer_valeur_combo(
            combo=self.theme_combo,
            dict_parent=self.constantes.parametres_traduits.get("themes_cartes", {}),
            langue=self.langue,
            valeur=kwargs.get("theme"),
            defaut_index=0,
        )

        # Chargement de la teinte
        restaurer_valeur_combo(
            combo=self.color_combo,
            dict_parent=self.constantes.parametres_traduits.get("teintes_couleurs", {}),
            langue=self.langue,
            valeur=kwargs.get("couleur") or None,
            defaut_index=0,
        )

        # Couleur de fond de cartes
        restaurer_valeur_combo(
            combo=self.combo_couleur_fond,
            dict_parent=self.constantes.parametres_traduits.get("arrière_plans", {}),
            langue=self.langue,
            valeur=kwargs.get("couleur_fond_carte") or None,
            defaut_index=0,
        )
