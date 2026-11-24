################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1 – Création de l'onglet complet                                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, multiprocessing
from functools import partial
from queue import Empty

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QSlider,
    QGroupBox,
    QSpacerItem,
    QSizePolicy,
    QStackedLayout,
    QStackedWidget,
)

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    obtenir_clef_par_valeur,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    reset_combo,
    creer_QLabel_centre,
    creer_ligne_horizontale,
    creer_ligne_verticale,
    restaurer_valeur_combo,
    QHBoxLayout_centre,
)
from _0_Utilitaires._0_11_classes_pop_up import PopupInfo
from _0_Utilitaires._0_12_toggle_checkbox import ToggleSwitch
from _0_Utilitaires._0_14_QPushButton_QIcon import QPushButtonSauvegarde
from _0_Utilitaires._0_16_selecteur_valeurs import SelecteurValeurs
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_04_publication_cartes import (
    executer_creation_cartes,
)
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_03_bouton import BoutonCreationCartes
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_01_combobox_coloree import (
    FondCarteCombo,
)
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_08_animation_immersive import (
    AnimationTrainPublication,
)
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_07_progression_locale import (
    ProgressionCreationLocale,
)
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_02_chargment_gdf import (
    GestionnaireChargementGDFS,
)
from _4_Interface._4_3_Icones._4_3_30_stylo import _dessiner_icone_stylo_plume
from _4_Interface._4_3_Icones._4_3_29_email import _dessiner_icone_email

# 1 -- Classe de l'onglet des paramètres de cartes -----------------------------


class OngletParametres(QWidget):

    # Délai (ms) pendant lequel la progression locale reste visible à 100 %.
    DELAI_FIN_PROGRESSION_LOCALE = 800

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
        layout.setContentsMargins(0, 0, 0, 0)

        self.layout_principal.addWidget(self.page_parametres)

        # --------------------------------------------------------------------------
        # Page 2 : animation immersive (uniquement pour le mode "immersif")
        # --------------------------------------------------------------------------

        # Valeurs possibles : "immersif", "animation", "classique"
        self.mode_progression = "classique"

        self.page_animation = QWidget()
        self.layout_animation = QVBoxLayout(self.page_animation)
        self.layout_animation.setContentsMargins(0, 0, 0, 0)

        self.layout_principal.addWidget(self.page_animation)

        # La page normale est affichée au lancement.
        self.layout_principal.setCurrentWidget(self.page_parametres)

        self.animation_publication = None  # mode immersif (page entière)
        self.progression_locale = None  # mode local (remplace le bouton)
        self._indice_publication = 0

        # --------------------------------------------------------------------------
        # Granularité
        # --------------------------------------------------------------------------

        self.groupe_granularite = QGroupBox()

        # Granularité des pays visités
        self.label_granularite_visite = creer_QLabel_centre()
        self.granularite_visite = SelecteurValeurs(
            valeurs=["Pays", "Région", "Département", "Amusant"],
            layout_horizontal=False,
        )
        layout_granularite_visite = QVBoxLayout()
        layout_granularite_visite.addWidget(self.label_granularite_visite)
        layout_granularite_visite.addWidget(self.granularite_visite)

        # Granularité de fond
        self.label_granularite_fond = creer_QLabel_centre()
        self.granularite_fond = SelecteurValeurs(
            valeurs=["Pays", "Région", "Département"], layout_horizontal=False
        )
        layout_granularite_fond = QVBoxLayout()
        layout_granularite_fond.addWidget(self.label_granularite_fond)
        layout_granularite_fond.addWidget(self.granularite_fond)
        layout_granularite_fond.addStretch()

        # Possibilité d'écrire le nom du territoire sur la carte
        self.labellisation_checkbox = ToggleSwitch(
            fonction_dessin=_dessiner_icone_stylo_plume, taille_icone=40
        )

        # Ajouter les layouts horizontaux à la group box
        layout_granularite_temp = QHBoxLayout()
        layout_granularite = QVBoxLayout()
        layout_granularite_temp.addLayout(layout_granularite_visite, stretch=1)
        layout_granularite_temp.addLayout(layout_granularite_fond, stretch=1)
        layout_granularite.addLayout(layout_granularite_temp)
        layout_granularite.addLayout(QHBoxLayout_centre(self.labellisation_checkbox))
        self.groupe_granularite.setLayout(layout_granularite)

        # --------------------------------------------------------------------------
        # Cartes à créer
        # --------------------------------------------------------------------------

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

        ligne_regions_2 = 3
        layout_cartes_a_creer.addWidget(self.europe, ligne_regions_2, 0, 1, 2)
        layout_cartes_a_creer.addWidget(self.moyen_orient, ligne_regions_2, 2, 1, 2)
        layout_cartes_a_creer.addWidget(self.autres_regions, ligne_regions_2, 4, 1, 2)

        self.groupe_cartes_a_creer.setLayout(layout_cartes_a_creer)

        # Colonne de gauche : granularité + cartes à créer
        layout_granu_cartes_a_creer = QVBoxLayout()
        layout_granu_cartes_a_creer.addWidget(self.groupe_granularite)

        # --------------------------------------------------------------------------
        # Couleurs
        # --------------------------------------------------------------------------

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

        # Ajout des groupbox des cartes et des couleurs
        layout_cartes_et_couleurs = QHBoxLayout()
        layout_cartes_et_couleurs.addLayout(layout_granu_cartes_a_creer)
        layout_cartes_et_couleurs.addWidget(self.groupe_couleurs)

        layout.addLayout(layout_cartes_et_couleurs, stretch=8)

        # --------------------------------------------------------------------------
        # Paramètres de publication
        # --------------------------------------------------------------------------

        self.groupe_params_publication = QGroupBox()

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
        self.email_checkbox = ToggleSwitch(
            fonction_dessin=partial(
                _dessiner_icone_email,
                arobase=False,
                couleur="#B9C6F5",
                couleur_badge="#000000",
            ),
            taille_icone=40,
        )

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
        lauout_technique = QVBoxLayout()
        lauout_technique.addLayout(layout_format_qualite)
        lauout_technique.addWidget(creer_ligne_horizontale())
        lauout_technique.addWidget(self.email_checkbox)

        # Ajouter le layout horizontal au layout de la group box
        self.groupe_params_publication.setLayout(lauout_technique)

        # Ajouter le QGroupBox au layout principal
        layout_bas = QHBoxLayout()
        layout_bas.addWidget(self.groupe_cartes_a_creer)
        layout_bas.addWidget(self.groupe_params_publication)

        layout.addLayout(layout_bas)

        # --------------------------------------------------------------------------
        # Zone d'action : bouton « Créer cartes » OU progression locale
        # --------------------------------------------------------------------------

        # Bouton de création
        self.creation_cartes_bouton = BoutonCreationCartes(
            fonction_traduction=self.fonction_traduction, parent=self
        )

        # Conteneur qui accueillera la progression locale
        self.conteneur_progression_locale = QWidget()
        self.layout_progression_locale = QVBoxLayout(self.conteneur_progression_locale)
        self.layout_progression_locale.setContentsMargins(0, 0, 0, 0)

        # Pile : un seul des deux est visible à la fois
        self.zone_action = QStackedWidget()
        self.zone_action.addWidget(self.creation_cartes_bouton)  # index 0
        self.zone_action.addWidget(self.conteneur_progression_locale)  # index 1
        self.zone_action.setCurrentWidget(self.creation_cartes_bouton)

        # Bouton de sauvegarde
        self.bouton_sauvegarde = QPushButtonSauvegarde(taille=76)

        # Grille du bas : (zone d'action | sauvegarde)
        # IMPORTANT : le bouton « Créer cartes » n'est PAS ajouté ici. Il
        # appartient déjà à `zone_action` ; l'ajouter une seconde fois à une
        # grille l'en retirerait.
        layout_valid_reinit = QGridLayout()
        layout_valid_reinit.addWidget(self.zone_action, 0, 0)
        layout_valid_reinit.addWidget(self.bouton_sauvegarde, 0, 1)
        layout_valid_reinit.setColumnStretch(0, 1)

        layout.addLayout(layout_valid_reinit, stretch=2)

        # --------------------------------------------------------------------------
        # Chargement des données géographiques
        # --------------------------------------------------------------------------

        self.gestionnaire_chargement = GestionnaireChargementGDFS(self)
        self.gestionnaire_chargement.donnees_chargees.connect(self._recevoir_gdfs)
        self.gestionnaire_chargement.erreur.connect(self._gerer_erreur_chargement)
        self._callback_chargement = None

    # 2 -- Langue et style -------------------------------------------------------

    def set_langue(self, langue: str | None):

        # Récupération de la langue
        self.langue = langue

        if self.langue is None:
            return

        # Granularité des cartes
        self.groupe_granularite.setTitle(self.fonction_traduction("titre_granularite"))
        self.label_granularite_visite.setText(
            self.fonction_traduction("granularite_pays_visites")
        )
        self.label_granularite_fond.setText(
            self.fonction_traduction("granularite_pays_non_visites")
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
            self.fonction_traduction(clef="cartes_couleurs", suffixe=" :")
        )
        self.theme_label.setText(
            self.fonction_traduction(clef="cartes_theme", suffixe=" :")
        )
        self.utiliser_theme.setText(self.fonction_traduction("tick_style_dans_app"))
        self.utiliser_theme.setToolTip(
            self.fonction_traduction("description_tick_style_dans_app", suffixe=".")
        )

        self.couleur_fond_label.setText(
            self.fonction_traduction("cartes_couleurs_fond", suffixe=" :")
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
            self.fonction_traduction("cartes_format", suffixe=" :")
        )
        self.label_qualite.setText(
            self.fonction_traduction("cartes_qualite", suffixe=" :")
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
        self.creation_cartes_bouton.set_langue()
        self.bouton_sauvegarde.setToolTip(
            self.fonction_traduction("sauvegarder_profil", suffixe=".")
        )

        # Mise à jour des listes déroulantes
        liste_granularite = [
            self.constantes.parametres_traduits["granularite"][self.langue][k]
            for k in ["Pays", "Région", "Département", "Amusant"]
        ]

        self.granularite_visite.definir_valeurs(
            valeurs=liste_granularite, valeur_initiale_index=None
        )
        self.granularite_fond.definir_valeurs(
            valeurs=liste_granularite[:-1], valeur_initiale_index=None
        )

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
        self.style = style
        # Bouton de style
        self.utiliser_theme.set_style(style=style, preset=preset, teintes=teintes)

        # Paramètres de cartes
        self.email_checkbox.set_style(style=style, preset=preset, teintes=teintes)
        self.labellisation_checkbox.set_style(
            style=style, preset=preset, teintes=teintes
        )

        # Granularité
        self.granularite_visite.set_style(style="clair" if style == 1 else "sombre")
        self.granularite_fond.set_style(style="clair" if style == 1 else "sombre")

        self.creation_cartes_bouton.setStyleSheet("""
            QPushButton {
                font-weight: 600;
            }
            """)

    # 3 -- Progression de la création --------------------------------------------

    def _activer_boutons_action(self, actif: bool) -> None:
        """Active ou désactive les boutons d'action (création et sauvegarde)."""

        self.creation_cartes_bouton.setEnabled(actif)
        self.bouton_sauvegarde.setEnabled(actif)

    def initialiser_animation_publication(self, n: int) -> None:
        """Affiche la progression adaptée au mode choisi."""

        self._indice_publication = 0
        self._nettoyer_progression()  # sécurité si un ancien widget traîne

        # Les boutons restent bloqués pendant toute la création.
        self._activer_boutons_action(False)

        if self.mode_progression == "immersif":
            self._demarrer_progression_immersive(n)
        else:
            self._demarrer_progression_locale(n)

    def _demarrer_progression_immersive(self, n: int) -> None:
        """Remplace toute la page des paramètres (train)."""

        self.animation_publication = AnimationTrainPublication(n=n, vitesse=130.0)
        self.animation_publication.retour_parametres.connect(
            self.revenir_aux_parametres
        )

        self.layout_animation.addWidget(self.animation_publication)
        self.layout_principal.setCurrentWidget(self.page_animation)

    def _demarrer_progression_locale(self, n: int) -> None:
        """Remplace uniquement le bouton « Créer cartes » (barre / avion)."""

        self.progression_locale = ProgressionCreationLocale(
            mode=self.mode_progression,
            theme="clair" if self.style == 1 else "sombre",
        )

        # Évite une zone d'action plus petite que le bouton qu'elle remplace.
        self.progression_locale.setMinimumHeight(
            self.creation_cartes_bouton.sizeHint().height()
        )

        self.progression_locale.set_texte_haut("Création de vos cartes de voyage")
        self.progression_locale.set_texte_bas("Préparation des destinations…")
        self.progression_locale.set_maximum(n)
        self.progression_locale.set_valeur(0)
        self.progression_locale.demarrer()

        self.layout_progression_locale.addWidget(self.progression_locale)
        self.zone_action.setCurrentWidget(self.conteneur_progression_locale)
        # La page des paramètres reste affichée : layout_principal n'est pas touché.

    def _nettoyer_progression(self) -> None:
        """Détruit tout widget de progression et restaure l'état normal."""

        if self.progression_locale is not None:
            self.progression_locale.arreter()
            self.layout_progression_locale.removeWidget(self.progression_locale)
            self.progression_locale.deleteLater()
            self.progression_locale = None

        if self.animation_publication is not None:
            self.layout_animation.removeWidget(self.animation_publication)
            self.animation_publication.deleteLater()
            self.animation_publication = None

        self.layout_principal.setCurrentWidget(self.page_parametres)
        self.zone_action.setCurrentWidget(self.creation_cartes_bouton)
        self._activer_boutons_action(True)

    def revenir_aux_parametres(self) -> None:
        """Slot du signal `retour_parametres` de l'animation immersive."""

        self._nettoyer_progression()

    def afficher_avancement(self, libelle_pays: str) -> None:
        """Transmet l'avancement au widget de progression actif."""

        self._indice_publication += 1

        if self.progression_locale is not None:
            self.progression_locale.set_valeur(self._indice_publication)
            self.progression_locale.set_texte_bas(
                f"Création de la carte : {libelle_pays}"
            )

        elif self.animation_publication is not None:
            self.animation_publication.recevoir_signal(
                i=self._indice_publication,
                nom_pays=libelle_pays,
            )

    # 4 -- Vérifications et chargement des données ------------------------------

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
        """Lance le chargement des GeoDataFrames."""

        self._callback_chargement = callback

        self.gestionnaire_chargement.lancer(
            direction=self.constantes.direction_donnees_geographiques
        )

    def _recevoir_gdfs(self, liste_gdfs):
        """Récupère les données chargées dans le thread principal."""

        self.liste_gdfs = liste_gdfs

        # Exécuter le callback une fois les données disponibles
        callback = self._callback_chargement
        self._callback_chargement = None

        if callback is not None:
            callback()

    def _gerer_erreur_chargement(self, message):
        """Gère les erreurs survenues pendant le chargement."""

        print(f"Erreur chargement des GeoDataFrames : {message}")

        self._callback_chargement = None

        # Sans cela, les boutons resteraient bloqués indéfiniment.
        self._activer_boutons_action(True)

    # 5 -- Processus de création -------------------------------------------------

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

    def _vider_file_messages(self) -> bool:
        """Traite les messages en attente.

        Renvoie True si un message final (« finished » ou « erreur ») a été
        traité, c'est-à-dire si la lecture doit s'arrêter.
        """

        while self.file_messages_creation is not None:

            try:
                type_message, valeur = self.file_messages_creation.get_nowait()
            except Empty:
                return False

            if type_message == "nb_graphes":
                self.initialiser_animation_publication(n=valeur)

            elif type_message == "progression":
                self.afficher_avancement(libelle_pays=valeur)

            elif type_message == "finished":
                self._terminer_processus_creation()
                self._fin_creation()
                return True

            elif type_message == "erreur":
                print(f"Erreur pendant la création des cartes : {valeur}")
                self._terminer_processus_creation()
                self._nettoyer_progression()
                return True

        return True

    def _lire_messages_creation(self) -> None:
        """Appelée par le timer : lit les messages du processus de création."""

        if self.file_messages_creation is None:
            return

        if self._vider_file_messages():
            return

        # Le processus est mort sans avoir envoyé de message final (plantage) :
        # on relit une dernière fois la file, puis on débloque l'interface.
        if (
            self.processus_creation is not None
            and not self.processus_creation.is_alive()
        ):

            if self._vider_file_messages():
                return

            print("Le processus de création des cartes s'est arrêté prématurément.")
            self._terminer_processus_creation()
            self._nettoyer_progression()

    def _fin_creation(self) -> None:
        """Fin normale : le retour à l'état initial dépend du mode."""

        # Immersif : on attend que l'utilisateur clique sur « retour ».
        if self.animation_publication is not None:
            return

        # Local : on laisse 100 % visible un instant, puis on remet le bouton.
        # Aucun widget (ex. 0 carte à créer) : retour immédiat.
        delai = self.DELAI_FIN_PROGRESSION_LOCALE if self.progression_locale else 0
        QTimer.singleShot(delai, self._nettoyer_progression)

    def _terminer_processus_creation(self) -> None:
        """Nettoie le processus lorsque le calcul est terminé."""

        self.timer_messages_creation.stop()

        if self.processus_creation is not None:

            self.processus_creation.join(timeout=0.1)
            self.processus_creation = None

        if self.file_messages_creation is not None:

            self.file_messages_creation.close()
            self.file_messages_creation = None

    def fonction_principale(self, settings):

        # Modification du type d'animation
        self.set_mode_progression(mode=settings.get("type_animation", 0))

        # ----------------------------------------------------------------------
        # Vérification des paramètres
        # ----------------------------------------------------------------------

        if self.soulever_probleme(
            dict_voyages=settings["dictionnaire_voyages"],
            dossier_stockage=settings["dossier_stockage"],
        ):
            return

        # Évite plusieurs clics pendant le travail.
        self._activer_boutons_action(False)

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

    # 6 -- Initialisation et export des paramètres -------------------------------

    def initialiser_onglet(self, **kwargs):

        # Indicatrices
        checkboxes = {
            # Cartes à publier
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

        # Sélecteurs
        select_configs = {
            # Granularité des pays visités
            self.granularite_visite: {
                "dict_key": "granularite",
                "valeur": kwargs.get("granularite"),
            },
            # Granularités des pays non visités
            self.granularite_fond: {
                "dict_clef": "granularite",
                "valeur": kwargs.get("granularite_fond") or 0,
            },
        }
        for clef, config in select_configs.items():
            val_temp = config["valeur"]
            if not isinstance(val_temp, int):
                val_temp = 0
            clef.definir_valeur(index=val_temp)

        # Menus déroulants
        combo_configs = {
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
            "granularite": self.granularite_visite.obtenir_valeur(index=True),
            "granularite_fond": self.granularite_fond.obtenir_valeur(index=True),
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

    def set_mode_progression(self, mode: int):

        self.mode_progression = {
            0: "classique",
            1: "animation",
            2: "immersif",
        }.get(mode, "classique")
