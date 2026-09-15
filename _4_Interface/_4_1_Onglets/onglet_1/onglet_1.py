################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1 – Création de l'onglet complet                                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, multiprocessing
from functools import partial
from queue import Empty

from PyQt6.QtCore import pyqtSignal, QObject, QSize, Qt, QThread, QTimer
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
    QSpacerItem,
    QSizePolicy,
    QStackedLayout,
)

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    charger_gdfs,
    obtenir_clef_par_valeur,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    reset_combo,
    creer_QLabel_centre,
    creer_ligne_horizontale,
    creer_ligne_verticale,
    restaurer_valeur_combo,
    creer_icone,
)
from _0_Utilitaires._0_11_classes_pop_up import PopupInfo
from _0_Utilitaires._0_12_toggle_checkbox import ToggleSwitch
from _0_Utilitaires._0_14_QPushButton_QIcon import QPushButtonSauvegarde
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_1_creation_cartes import CreerCartes
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_4_processus_cartes import (
    executer_creation_cartes,
)
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_2_combobox_coloree import (
    FondCarteCombo,
)
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_3_barre_progression import (
    AnimationTrainPublication,
)
from _4_Interface._4_3_Icones._4_3_30_stylo import _dessiner_icone_stylo_plume
from _4_Interface._4_3_Icones._4_3_29_email import _dessiner_icone_email

# 1 -- Classe de chargement des GeoDataFrames ----------------------------------


class WorkerChargement(QObject):
    finished = pyqtSignal()
    erreur = pyqtSignal(str)

    def __init__(self, parent, direction):
        super().__init__()
        self.parent = parent
        self.direction = direction

    def run(self):
        try:
            # Chargement lourd
            self.parent.liste_gdfs = charger_gdfs(
                direction_base=self.direction,
                max_niveau=2,
            )

            self.finished.emit()

        except Exception as e:
            self.erreur.emit(str(e))


# 2 -- Classe de l'onglet des paramètres de cartes -----------------------------


class OngletParametres(QWidget):

    def __init__(self, constantes, fct_traduction):

        super().__init__()

        self.constantes = constantes
        self.fonction_traduction = fct_traduction
        self.langue = "français"
        self.liste_gdfs = []

        # --------------------------------------------------------------------------
        # Processus de création des cartes
        # --------------------------------------------------------------------------

        self.processus_creation = None
        self.file_messages_creation = None

        self.timer_messages_creation = QTimer(self)
        self.timer_messages_creation.setInterval(30)
        self.timer_messages_creation.timeout.connect(self._lire_messages_creation)

        # --------------------------------------------------------------------------
        # Pages de l'onglet
        # --------------------------------------------------------------------------

        self.layout_principal = QStackedLayout()
        self.setLayout(self.layout_principal)

        # --------------------------------------------------------------------------
        # Page 1 : paramètres des cartes
        # --------------------------------------------------------------------------

        self.page_parametres = QWidget()

        layout = QVBoxLayout(self.page_parametres)
        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.layout_principal.addWidget(self.page_parametres)

        # --------------------------------------------------------------------------
        # Page 2 : animation de publication
        # --------------------------------------------------------------------------

        self.page_animation = QWidget()
        self.layout_animation = QVBoxLayout(self.page_animation)
        self.layout_animation.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.layout_principal.addWidget(self.page_animation)

        # La page normale est affichée au lancement.
        self.layout_principal.setCurrentWidget(self.page_parametres)

        self.animation_publication = None
        self._indice_publication = 0

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
        layout_theme_couleurs = QVBoxLayout(self.groupe_couleurs)

        # Choix du thème
        self.theme_label = creer_QLabel_centre()
        self.theme_combo = QComboBox()
        layout_theme = QHBoxLayout()
        layout_theme.addWidget(self.theme_label)
        layout_theme.addWidget(self.theme_combo)

        # Choix des couleurs
        self.color_label = creer_QLabel_centre()
        self.color_combo = QComboBox()
        layout_couleurs = QHBoxLayout()
        layout_couleurs.addWidget(self.color_label)
        layout_couleurs.addWidget(self.color_combo)

        # Utilisation ou non du thème dans l'interface
        self.utiliser_theme = ToggleSwitch()

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
        self.email_checkbox = ToggleSwitch()
        self.email_checkbox.setIcon(
            creer_icone(
                fonction_dessin=partial(
                    _dessiner_icone_email,
                    arobase=False,
                    couleur="#B9C6F5",
                    couleur_badge="#000000",
                ),
                taille_px=40,
            ),
        )
        self.email_checkbox.setIconSize(QSize(40, 40))

        # Possibilité d'écrire le nom du territoire sur la carte
        self.labellisation_checkbox = ToggleSwitch()
        self.labellisation_checkbox.setIcon(
            creer_icone(fonction_dessin=_dessiner_icone_stylo_plume, taille_px=40),
        )
        self.labellisation_checkbox.setIconSize(QSize(40, 40))

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
        layout_format_qualite.addWidget(creer_ligne_verticale())
        layout_mail_texte = QVBoxLayout()
        layout_mail_texte.addWidget(self.labellisation_checkbox)
        layout_mail_texte.addWidget(self.email_checkbox)
        layout_format_qualite.addLayout(layout_mail_texte)

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

        # Bouton de sauvegarde
        self.bouton_sauvegarde = QPushButtonSauvegarde()

        # Ajouter les widgets dans la grille
        layout_valid_reinit.addWidget(self.creation_cartes_bouton, 0, 0)
        layout_valid_reinit.addWidget(self.bouton_sauvegarde, 0, 1)

        # Ajuster les proportions : colonne 1 (droite) prend plus de place
        layout_valid_reinit.setColumnStretch(0, 4)  # plus grande colonne au milieu
        layout_valid_reinit.setColumnStretch(1, 1)  # petite colonne à gauche

        layout.addLayout(layout_valid_reinit, stretch=1)

    def set_langue(self, langue: str | None):

        # Récupération de la langue
        self.langue = langue

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
        self.email_checkbox.setText(self.fonction_traduction("email_checkbox"))
        self.email_checkbox.setToolTip(
            self.fonction_traduction("email_checkbox_tooltip", suffixe=".")
        )

        # Nom du territoire écrit
        self.labellisation_checkbox.setText(
            self.fonction_traduction("ecrire_nom_checkbox")
        )
        self.labellisation_checkbox.setToolTip(
            self.fonction_traduction("ecrire_nom_checkbox_tooltip", suffixe=".")
        )

        # Boutons en bas de l'onglet 1
        self.creation_cartes_bouton.setText(
            self.fonction_traduction("bouton_publier_cartes")
        )
        self.creation_cartes_bouton.setToolTip(
            self.fonction_traduction("description_bouton_publier_cartes", suffixe=".")
        )
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

    def set_style(self, style, preset, teintes):

        # Bouton de style
        self.utiliser_theme.set_style(style=style, preset=preset, teintes=teintes)

        # Paramètres de cartes
        self.email_checkbox.set_style(style=style, preset=preset, teintes=teintes)
        self.labellisation_checkbox.set_style(
            style=style, preset=preset, teintes=teintes
        )

        self.creation_cartes_bouton.setStyleSheet("""
            QPushButton {
                font-weight: 600;
            }
            """)

    def initialiser_animation_publication(
        self,
        n: int,
    ) -> None:
        """
        Crée l'animation de publication et remplace temporairement
        les paramètres par celle-ci.
        """

        self._indice_publication = 0

        # Suppression éventuelle d'une ancienne animation.
        if self.animation_publication is not None:

            self.layout_animation.removeWidget(self.animation_publication)
            self.animation_publication.deleteLater()

        # Nouvelle animation.
        self.animation_publication = AnimationTrainPublication(
            n=n,
            vitesse=130.0,
        )

        # Bouton final de l'animation.
        self.animation_publication.retour_parametres.connect(
            self.revenir_aux_parametres
        )

        # L'animation remplit toute sa page.
        self.layout_animation.addWidget(self.animation_publication)

        # On change simplement de "page".
        self.layout_principal.setCurrentWidget(self.page_animation)

    def revenir_aux_parametres(
        self,
    ) -> None:
        """Revient à l'écran de paramétrage des cartes."""

        self.layout_principal.setCurrentWidget(self.page_parametres)
        self.creation_cartes_bouton.setEnabled(True)

        if self.animation_publication is not None:

            self.layout_animation.removeWidget(self.animation_publication)
            self.animation_publication.deleteLater()
            self.animation_publication = None

    def afficher_avancement(
        self,
        libelle_pays: str,
    ) -> None:
        """Transmet la progression au train."""

        if self.animation_publication is None:
            return

        self._indice_publication += 1

        self.animation_publication.recevoir_signal(
            i=self._indice_publication,
            nom_pays=libelle_pays,
        )

    def soulever_probleme(self, dict_voyages: dict, dossier_stockage: str):

        # Pas de problème au départ
        probleme = False

        # Initialisation du message
        message = PopupInfo(parent=self)
        temps_max = 10**4

        # Pas de voyages effectués
        if not dict_voyages:

            message.montrer(
                titre=self.fonction_traduction("pop_up_probleme_titre", suffixe="."),
                contenu=self.fonction_traduction("pop_up_aucun_lieu_coche"),
                temps_max=temps_max,
            )
            probleme = True

        # Dossier de stockage inexistant
        elif dossier_stockage is None:

            message.montrer(
                titre=self.fonction_traduction("pop_up_probleme_titre", suffixe="."),
                contenu=self.fonction_traduction(
                    "pop_up_pas_de_dossier_de_stockage",
                    suffixe=".",
                ),
                temps_max=temps_max,
            )
            probleme = True

        # Dossier de stockage invalide
        elif not os.path.exists(dossier_stockage):

            message.montrer(
                titre=self.fonction_traduction("pop_up_probleme_titre", suffixe="."),
                contenu=self.fonction_traduction(
                    "pop_up_dossier_de_stockage_faux",
                    suffixe=".",
                ),
                temps_max=temps_max,
            )
            probleme = True

        # Renvoi
        return probleme

    def lancer_chargement_gdfs(self, callback=None):

        # Création du thread
        self.thread_chargement = QThread()

        # Worker
        self.worker_chargement = WorkerChargement(
            parent=self, direction=self.constantes.direction_donnees_geographiques
        )

        # Déplacement dans le thread
        self.worker_chargement.moveToThread(self.thread_chargement)

        # Lancement
        self.thread_chargement.started.connect(self.worker_chargement.run)

        # Fin normale
        self.worker_chargement.finished.connect(self.thread_chargement.quit)
        self.worker_chargement.finished.connect(self.worker_chargement.deleteLater)
        self.thread_chargement.finished.connect(self.thread_chargement.deleteLater)

        # Callback optionnel
        if callback:
            self.worker_chargement.finished.connect(callback)

        # Gestion erreurs
        self.worker_chargement.erreur.connect(
            lambda e: print(f"Erreur chargement : {e}")
        )

        # Start
        self.thread_chargement.start()

    def lancer_creation_cartes_processus(self, settings) -> None:
        """Lance la création des cartes dans un processus indépendant."""

        contexte = multiprocessing.get_context("spawn")

        self.file_messages_creation = contexte.Queue()

        self.processus_creation = contexte.Process(
            target=executer_creation_cartes,
            args=(
                settings,
                self.constantes.__name__,
                self.file_messages_creation,
            ),
        )

        self.processus_creation.start()

        self.timer_messages_creation.start()

    def _lire_messages_creation(
        self,
    ) -> None:
        """Traite les messages reçus du processus de création."""

        if self.file_messages_creation is None:
            return

        while True:

            try:

                type_message, valeur = self.file_messages_creation.get_nowait()

            except Empty:

                break

            if type_message == "nb_graphes":

                self.initialiser_animation_publication(n=valeur)

            elif type_message == "progression":

                self.afficher_avancement(libelle_pays=valeur)

            elif type_message == "finished":

                self._terminer_processus_creation()

                return

            elif type_message == "erreur":

                print(valeur)

                self._terminer_processus_creation()

                return

    def _terminer_processus_creation(
        self,
    ) -> None:
        """Nettoie le processus lorsque le calcul est terminé."""

        self.timer_messages_creation.stop()

        if self.processus_creation is not None:

            self.processus_creation.join(timeout=0.1)
            self.processus_creation = None

        if self.file_messages_creation is not None:

            self.file_messages_creation.close()
            self.file_messages_creation = None

    def fonction_principale(
        self,
        settings,
    ):

        # ----------------------------------------------------------------------
        # Vérification des paramètres
        # ----------------------------------------------------------------------

        if self.soulever_probleme(
            dict_voyages=settings["dictionnaire_voyages"],
            dossier_stockage=settings["dossier_stockage"],
        ):
            return

        # Évite plusieurs clics pendant le travail.
        self.creation_cartes_bouton.setEnabled(False)

        # ----------------------------------------------------------------------
        # Chargement préalable des données géographiques
        # ----------------------------------------------------------------------

        if not self.liste_gdfs:

            self.lancer_chargement_gdfs(
                callback=lambda: self.fonction_principale(settings=settings)
            )

            return

        # ----------------------------------------------------------------------
        # Création des cartes
        # ----------------------------------------------------------------------

        settings["liste_dfs"] = self.liste_gdfs
        self.lancer_creation_cartes_processus(settings=settings)

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
            # Labellisation du territoire
            "labelliser_territoires": self.labellisation_checkbox,
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

        # Menus déroulants
        combo_configs = {
            # Granularité des pays visités
            self.granularite_visite: {
                "dict_key": "granularite",
                "valeur": kwargs.get("granularite"),
            },
            # Granularités des pays non visités
            self.granularite_fond: {
                "dict_key": "granularite",
                "valeur": kwargs.get("granularite_fond"),
            },
            # Thème
            self.theme_combo: {
                "dict_key": "themes_cartes",
                "valeur": kwargs.get("theme"),
            },
            # Teintes
            self.color_combo: {
                "dict_key": "teintes_couleurs",
                "valeur": kwargs.get("couleur"),
            },
            # Couleur de la mer
            self.combo_couleur_fond: {
                "dict_key": "arrière_plans",
                "valeur": kwargs.get("couleur_fond_carte"),
            },
        }

        # Boucle pour restaurer les valeurs
        trads = self.constantes.parametres_traduits
        for combo, config in combo_configs.items():
            restaurer_valeur_combo(
                combo=combo,
                dict_parent=trads.get(config["dict_key"], {}),
                langue=self.langue,
                valeur=config["valeur"] or None,
                defaut_index=0,
            )

    def creer_dict_parametres(self):

        langue = self.langue
        params_traduits = self.constantes.parametres_traduits.copy()

        return {
            "granularite": obtenir_clef_par_valeur(
                valeur=self.granularite_visite.currentText(),
                dictionnaire=params_traduits["granularite"][langue],
            ),
            "granularite_fond": obtenir_clef_par_valeur(
                valeur=self.granularite_fond.currentText(),
                dictionnaire=params_traduits["granularite"][langue],
            ),
            "couleur": obtenir_clef_par_valeur(
                valeur=self.color_combo.currentText(),
                dictionnaire=params_traduits["teintes_couleurs"][langue],
            ),
            "theme": obtenir_clef_par_valeur(
                valeur=self.theme_combo.currentText(),
                dictionnaire=params_traduits["themes_cartes"][langue],
            ),
            "couleur_fond_carte": self.combo_couleur_fond.valeur_en_francais(),
            "qualite": self.curseur_qualite.value(),
            "format": self.format_cartes.currentText(),
            "envoi_email": self.email_checkbox.isChecked(),
            # Cartes à publier
            "carte_du_monde": self.carte_monde.isChecked(),
            "europe": self.europe.isChecked(),
            "asie": self.asie.isChecked(),
            "amerique": self.amerique.isChecked(),
            "afrique": self.afrique.isChecked(),
            "moyen_orient": self.moyen_orient.isChecked(),
            "autres_regions": self.autres_regions.isChecked(),
            "cartes_des_pays": self.carte_pays.isChecked(),
            # Labelliser les territoires
            "labelliser_territoires": self.labellisation_checkbox.isChecked(),
        }
