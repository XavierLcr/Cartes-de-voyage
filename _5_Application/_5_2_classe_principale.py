################################################################################
# Projet de cartes de voyage                                                   #
# _5_Application/                                                              #
# 5.2 – Classe principale de l'application                                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, warnings, copy, textwrap

# PyQt6
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QTabWidget,
    QComboBox,
    QPushButton,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Scripts et fonctions du projet
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_fichier,
    exporter_fichier,
    voyages_vers_destinations,
    obtenir_clef_par_valeur,
    formater_temps_actuel,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import creer_QLabel_centre
from _0_Utilitaires._0_7_fonctions_voyages import voyage_id, creer_voyage
from _0_Utilitaires._0_11_classes_pop_up import PopupInfo, PopupOuiNon, PopupSaisieTexte
from _4_Interface._4_1_Onglets.onglet_1 import onglet_1
from _4_Interface._4_1_Onglets.onglet_2 import onglet_2
from _4_Interface._4_1_Onglets.onglet_4 import onglet_4
from _4_Interface._4_1_Onglets import onglet_3, onglet_info
from _4_Interface._4_1_Onglets.onglet_param_profil import onglet_param_profil
from _4_Interface._4_2_Style._4_2_1_style_principal import style_dynamique_application
from _4_Interface._4_2_Style._4_2_2_styles_complementaires import (
    style_bouton_ajout_profil,
    style_bouton_de_suppression,
)
from _4_Interface._4_2_Style._4_2_4_pluie_emojis import VuePluieEmojis

# from _4_Interface._4_2_Style._4_2_3_musique import MusicPlayer


# Suppression d'alertes, d'avis et de messages additionnels
warnings.filterwarnings("ignore")
os.environ["QT_LOGGING_RULES"] = "qt.text.font.db=false"


# 1 -- Classe principale -------------------------------------------------------


class MesVoyagesApplication(QWidget):

    def __init__(self, constantes, sauvegarde={}):

        super().__init__()

        self.setWindowTitle("Cartes de voyage")
        self.setGeometry(
            constantes.parametres_application.get("application_position_largeur", 100),
            constantes.parametres_application.get("application_position_hauteur", 100),
            constantes.parametres_application.get("application_largeur", 800),
            constantes.parametres_application.get("application_hauteur", 600),
        )
        self.setWindowIcon(
            QIcon(
                os.path.join(
                    constantes.direction_donnees_application, "icone_application.ico"
                )
            )
        )

        # Variables globales
        self.constantes = constantes
        self.sauvegarde = sauvegarde
        self.langue = "français"
        self.theme_application = True
        self.voyages = {}
        self.longueur_id_voyage = 10

        self.titre = creer_QLabel_centre(alignement=Qt.AlignmentFlag.AlignLeft)
        self.set_style_titre(taille=24)

        # === Profil sélectionné ===

        profile_container = QWidget()
        profile_layout = QHBoxLayout(profile_container)
        profile_layout.setContentsMargins(8, 0, 8, 0)
        self.nom_individu = QComboBox(self)
        self.nom_individu.setEditable(False)
        self.nom_individu.setPlaceholderText("")
        self.nom_individu_label = creer_QLabel_centre()
        profile_layout.addWidget(self.nom_individu_label)
        self.nom_individu.addItems(list(self.sauvegarde.keys()))
        profile_layout.addWidget(self.nom_individu)
        # Bouton d'ajout d'un profil
        self.bouton_ajout = QPushButton()
        self.bouton_ajout.setText("➕")
        self.bouton_ajout.setFixedWidth(40)
        self.bouton_ajout.clicked.connect(self.ajouter_profil)
        profile_layout.addWidget(self.bouton_ajout)
        # Bouton de réinitialisation
        self.reinit_parametres = QPushButton()
        self.reinit_parametres.setText("🧹")
        self.reinit_parametres.setFixedWidth(40)
        self.reinit_parametres.clicked.connect(
            lambda: self.initialiser_sauvegarde(reinitialiser=True)
        )
        profile_layout.addWidget(self.reinit_parametres)

        # === Premier onglet ===

        self.onglet_parametres = onglet_1.OngletParametres(
            constantes=self.constantes,
            fct_traduction=self.traduire_depuis_id,
        )
        # Chargement d'un individu
        self.nom_individu.currentIndexChanged.connect(
            lambda: self.initialiser_sauvegarde(reinitialiser=False)
        )
        # Export
        self.onglet_parametres.bouton_sauvegarde.clicked.connect(
            lambda: self.exporter_liste_parametres(date_publication=False)
        )
        # Publication des cartes
        self.onglet_parametres.creation_cartes_bouton.clicked.connect(
            self.publier_cartes
        )
        # Mise à jour du style
        self.onglet_parametres.utiliser_theme.stateChanged.connect(
            lambda: self.set_style(theme_application=None)
        )
        self.onglet_parametres.color_combo.currentTextChanged.connect(
            lambda: self.set_style(theme_application=None)
        )
        self.onglet_parametres.theme_combo.currentTextChanged.connect(
            lambda: self.set_style(theme_application=None)
        )

        # === Deuxième onglet ===

        self.onglet_selection_destinations = onglet_2.OngletSelectionnerDestinations(
            constantes=self.constantes,
            fct_traduire=self.traduire_depuis_id,
            fct_sauvegarde=self.exporter_liste_parametres,
            longueur=self.longueur_id_voyage,
        )
        self.onglet_selection_destinations.dict_modif.connect(
            self.set_dictionnaire_destinations
        )

        # === Troisième onglet ===

        self.onglet_resume_destinations = onglet_3.OngletResumeDestinations(
            traduire_depuis_id=self.traduire_depuis_id,
            constantes=self.constantes,
            parent=None,
        )

        # === Quatrième onglet ===

        self.onglet_statistiques = onglet_4.OngletTopPays(
            constantes=self.constantes,
            table_superficie=ouvrir_fichier(
                direction_fichier=self.constantes.direction_donnees_application,
                nom_fichier="table_superficie.pkl",
                defaut=None,
                afficher_erreur="Problème avec la table de superficie.",
            ),
            parent=None,
            fct_traduction=self.traduire_depuis_id,
        )

        # === Cinquième onglet ===

        self.onglet_param_profil = onglet_param_profil.OngletParametresProfil(
            constantes=self.constantes, fct_traduction=self.traduire_depuis_id
        )

        # Langue
        self.onglet_param_profil.signal_langue.connect(self.set_langue_interface)

        # Dossier de stockage
        self.onglet_param_profil.signal_dossier.connect(self.set_dossier)

        # Sauvegarde d'un individu
        self.onglet_param_profil.bouton_sauvegarde.clicked.connect(
            lambda: self.exporter_liste_parametres(date_publication=False)
        )

        # Suppression d'un individu
        self.onglet_param_profil.suppression_profil.clicked.connect(
            lambda: self.supprimer_clef(self.nom_individu.currentText())
        )

        # Position des points de l'hémicycle
        self.onglet_param_profil.signal_hemicyle_position.connect(
            self.set_hemicycle_position
        )

        # Recommandations
        self.onglet_param_profil.signal_reco_par_pays.connect(
            self.set_recommandations_par_pays
        )
        self.onglet_param_profil.signal_reco_nb.connect(self.set_recommandations_nb)

        # == Sixième onglet ===

        self.onglet_description_application = onglet_info.OngletInformations(
            fct_traduire=self.traduire_depuis_id,
            version_logiciel=self.constantes.version_logiciel,
        )

        # === Mise en forme === #

        # Layout de la ligne générale
        layout_top = QHBoxLayout()
        layout_top.addWidget(self.titre)
        layout_top.addStretch()
        layout_top.addWidget(profile_container)

        # Création des onglets
        self.liste_onglets = QTabWidget()
        self.liste_onglets.setUsesScrollButtons(False)
        self.liste_onglets.setTabShape(QTabWidget.TabShape.Rounded)
        self.liste_onglets.setTabPosition(QTabWidget.TabPosition.North)
        self.liste_onglets.addTab(self.onglet_parametres, "Cartes")
        self.liste_onglets.addTab(self.onglet_selection_destinations, "Voyages")
        self.liste_onglets.addTab(
            self.onglet_resume_destinations, "Résumé des destinations"
        )
        self.liste_onglets.addTab(self.onglet_statistiques, "Statistiques")
        self.liste_onglets.addTab(self.onglet_param_profil, "⚙️")
        self.liste_onglets.addTab(self.onglet_description_application, "ℹ️")

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(layout_top)
        main_layout.addWidget(self.liste_onglets)
        self.liste_onglets.setCurrentIndex(0 if self.sauvegarde else 4)

        self.initialiser_sauvegarde(reinitialiser=True)

        if "pluie_emojis" in self.constantes.dict_themes_temporaires.keys():
            self.vue_pluie = VuePluieEmojis(
                constantes=self.constantes,
                duree_ms=15000,
                intervalle_timer_ms=30,
                force_vent_globale=1.5,
                parent=self,
            )
            self.vue_pluie.show()

    def set_langue_interface(self, langue: str | None = None):
        """Met à jour les textes des widgets selon la langue sélectionnée."""

        if langue is not None:
            self.langue = langue

        # Titres généraux
        self.setWindowTitle(self.traduire_depuis_id("titre_windows"))

        self.titre.setText(
            self.traduire_depuis_id(
                clef="titre_application",
                suffixe=self.constantes.dict_themes_temporaires.get("emoji", ""),
            )
        )

        # Profil sélectionné
        self.nom_individu_label.setText("👤")
        self.nom_individu.setPlaceholderText(
            self.traduire_depuis_id("nom_individu_placeholder", suffixe="...")
        )
        self.reinit_parametres.setText(
            "🧹"
            # self.traduire_depuis_id("reinitialisation_interface")
        )
        self.reinit_parametres.setToolTip(
            self.traduire_depuis_id(
                "description_bouton_reinitialisation_interface", suffixe="."
            )
        )

        # Onglet 1
        self.liste_onglets.setTabText(
            self.liste_onglets.indexOf(self.onglet_parametres),
            self.traduire_depuis_id(
                "titre_onglet_1",
                suffixe=(" 🎨"),
            ),
        )
        self.liste_onglets.setTabToolTip(
            self.liste_onglets.indexOf(self.onglet_parametres),
            self.traduire_depuis_id("description_onglet_1"),
        )
        self.onglet_parametres.set_langue(langue=self.langue)

        # Onglet 2
        self.liste_onglets.setTabText(
            self.liste_onglets.indexOf(self.onglet_selection_destinations),
            self.traduire_depuis_id(
                "titre_onglet_2",
                suffixe=(" 📌"),
            ),
        )
        self.onglet_selection_destinations.set_langue(langue=self.langue)

        # Onglet 3
        self.liste_onglets.setTabText(
            self.liste_onglets.indexOf(self.onglet_resume_destinations),
            self.traduire_depuis_id(
                "titre_onglet_3",
                suffixe=(" 🧭"),
            ),
        )
        self.onglet_resume_destinations.set_langue(nouvelle_langue=self.langue)

        # Onglet des statistiques
        self.liste_onglets.setTabText(
            self.liste_onglets.indexOf(self.onglet_statistiques),
            "📊",
        )
        self.liste_onglets.setTabToolTip(
            self.liste_onglets.indexOf(self.onglet_statistiques),
            self.traduire_depuis_id("titre_onglet_4"),
        )
        self.onglet_statistiques.set_langue(nouvelle_langue=self.langue)

        # Onglet des paramètres du profil
        self.liste_onglets.setTabToolTip(
            self.liste_onglets.indexOf(self.onglet_param_profil),
            self.traduire_depuis_id("titre_onglet_param_profil"),
        )
        self.onglet_param_profil.set_langue()
        self.onglet_param_profil.signal_theme_application.connect(self.set_style)

        # Onglet informationnel
        self.onglet_description_application.set_langue()

    def traduire_depuis_id(
        self,
        clef: str,
        prefixe: str = "",
        suffixe: str = "",
        depuis_id: bool = True,
        largeur_max: int | None = None,
    ) -> str:
        """
        Traduit une clé ou un ID de phrase selon la langue spécifiée.

        Args:
            clef: La clé ou l'ID de la phrase à traduire.
            prefixe: Préfixe à ajouter avant la traduction.
            suffixe: Suffixe à ajouter après la traduction.
            depuis_id: Si True, traite `cle` comme un ID à chercher dans `self.constantes.phrases_interface`.
            largeur_max: Si spécifié, tronque le texte à cette largeur maximale.

        Returns:
            str: La traduction formatée.
        """

        # Résolution de la clé si on part d'un ID
        clef = self.constantes.phrases_interface.get(clef, clef) if depuis_id else clef

        # Récupération de la traduction
        traduction = (
            prefixe
            + self.constantes.outil_differentes_langues.get(clef, {}).get(
                self.langue, clef
            )
            + suffixe
        )

        # Troncature si nécessaire
        return (
            textwrap.wrap(
                traduction,
                width=largeur_max,
                break_long_words=False,
                break_on_hyphens=False,
            )[0]
            if largeur_max is not None
            else traduction
        )

    def set_style(self, theme_application: bool | None = None):

        if theme_application is not None:
            self.theme_application = theme_application

        try:

            # Récupération de l'ambiance
            theme_temp = self.constantes.liste_ambiances.get(
                obtenir_clef_par_valeur(
                    dictionnaire=self.constantes.parametres_traduits[
                        "themes_cartes"
                    ].get(self.langue, {}),
                    valeur=self.onglet_parametres.theme_combo.currentText(),
                )
            )

            # Récupération des teintes utilisées
            teinte_temp = self.constantes.liste_couleurs.get(
                obtenir_clef_par_valeur(
                    dictionnaire=self.constantes.parametres_traduits[
                        "teintes_couleurs"
                    ].get(self.langue, {}),
                    valeur=self.onglet_parametres.color_combo.currentText(),
                )
            )

        except:
            return

        # Sortie si une valeur n'existe pas
        if theme_temp is None or teinte_temp is None:
            return

        # Appliquer les styles dynamiques
        style_temp = (
            0
            if self.onglet_parametres.utiliser_theme.isChecked()
            else 1 if self.theme_application else 2
        )

        # Cas général
        self.setStyleSheet(
            style_dynamique_application(
                style=style_temp,
                nuances=theme_temp,
                teinte=teinte_temp,
                limite_essais=50,
                font_size=13,
            )
        )

        # Sélection du profil
        self.bouton_ajout.setStyleSheet(
            style_bouton_ajout_profil(
                style=style_temp, teinte=teinte_temp, nuances=theme_temp
            )
        )
        self.reinit_parametres.setStyleSheet(
            style_bouton_de_suppression(sombre=not self.theme_application)
        )

        # Onglet 2
        self.onglet_selection_destinations.set_style(
            style=style_temp, teinte=teinte_temp, nuances=theme_temp
        )

        # Onglet 3
        self.onglet_resume_destinations.set_style(
            style=style_temp, teinte=teinte_temp, nuances=theme_temp
        )

        # Onglet de statistiques
        self.onglet_statistiques.set_style(
            style=style_temp, teinte=teinte_temp, nuances=theme_temp
        )

        # Onglet des paramètres de profil
        self.onglet_param_profil.set_style(theme=not self.theme_application)

    def creer_liste_parametres(self):

        langue = self.langue

        params_traduits = self.constantes.parametres_traduits.copy()

        return {
            # Paramètres individuels
            "nom": self.nom_individu.currentText(),
            "langue": langue,
            "adresse_email": self.onglet_param_profil.get_email(),
            "dossier_stockage": self.onglet_param_profil.get_dossier(),
            "ouvrir_dossier_stockage": self.onglet_param_profil.get_ouvrir_dossier(),
            "theme_application": self.onglet_param_profil.get_theme_application(),
            # Paramètres des cartes
            "sortir_cartes_granu_inf": self.onglet_param_profil.get_sortir_cartes_granu_inf(),
            "limite_n_cartes": self.onglet_param_profil.get_limite_de_cartes(),
            "granularite": obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.granularite_visite.currentText(),
                dictionnaire=params_traduits["granularite"][langue],
            ),
            "granularite_fond": obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.granularite_fond.currentText(),
                dictionnaire=params_traduits["granularite"][langue],
            ),
            "couleur": obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.color_combo.currentText(),
                dictionnaire=params_traduits["teintes_couleurs"][langue],
            ),
            "theme": obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.theme_combo.currentText(),
                dictionnaire=params_traduits["themes_cartes"][langue],
            ),
            "couleur_fond_carte": self.onglet_parametres.combo_couleur_fond.valeur_en_francais(),
            "qualite": self.onglet_parametres.curseur_qualite.value(),
            "format": self.onglet_parametres.format_cartes.currentText(),
            "envoi_email": self.onglet_parametres.email_checkbox.isChecked(),
            # Cartes à publier
            "carte_du_monde": self.onglet_parametres.carte_monde.isChecked(),
            "europe": self.onglet_parametres.europe.isChecked(),
            "asie": self.onglet_parametres.asie.isChecked(),
            "amerique": self.onglet_parametres.amerique.isChecked(),
            "afrique": self.onglet_parametres.afrique.isChecked(),
            "moyen_orient": self.onglet_parametres.moyen_orient.isChecked(),
            "autres_regions": self.onglet_parametres.autres_regions.isChecked(),
            "cartes_des_pays": self.onglet_parametres.carte_pays.isChecked(),
            # Lieux visités
            "dictionnaire_voyages": self.voyages,
            # Labelliser les territoires
            "labelliser_territoires": self.onglet_parametres.ecrire_nom_checkbox.isChecked(),
        } | self.onglet_statistiques.creer_dict_parametres()

    def exporter_liste_parametres(self, date_publication: bool = True):

        parametres = self.creer_liste_parametres()
        if parametres["nom"] is None or parametres["nom"] in [""]:
            parametres["nom"] = formater_temps_actuel(n=0)
        self.sauvegarde[parametres["nom"]] = copy.deepcopy(parametres) | {
            "date_publication": self.sauvegarde.get(parametres["nom"], {}).get(
                "date_publication", []
            )
            + ([formater_temps_actuel(n=1)] if date_publication else [])
        }

        # Ajout à la liste déroulante
        if parametres["nom"] not in [
            self.nom_individu.itemText(i) for i in range(self.nom_individu.count())
        ]:
            self.nom_individu.addItem(parametres["nom"])

        # Export sous forme de YAML
        self.exporter_sauvegarde()

        # Gestion des autres onglets
        self.onglet_selection_destinations.set_nom_individu(nom=parametres["nom"])

    def exporter_sauvegarde(self):

        exporter_fichier(
            objet=self.sauvegarde,
            direction_fichier=self.constantes.direction_donnees_application,
            nom_fichier="sauvegarde_utilisateurs.yaml",
            sort_keys=True,
        )

    def set_dictionnaire_destinations(self, dictionnaire: dict):
        self.voyages = dictionnaire
        self.onglet_selection_destinations.set_voyages(dictionnaire=self.voyages)

        dict_temp = voyages_vers_destinations(dict_voyages=self.voyages)
        bool_temp = dict_temp != {"region": {}, "dep": {}}

        self.liste_onglets.setTabVisible(
            self.liste_onglets.indexOf(self.onglet_resume_destinations),
            bool_temp,
        )
        self.liste_onglets.setTabVisible(
            self.liste_onglets.indexOf(self.onglet_statistiques),
            bool_temp,
        )

        self.onglet_resume_destinations.set_dicts_granu(
            dict_nv=copy.deepcopy(dict_temp)
        )
        self.onglet_statistiques.set_dicts_granu(dict_nv=copy.deepcopy(dictionnaire))

    def publier_cartes(self):

        # Export
        self.exporter_liste_parametres(date_publication=True)

        # Publication des cartes
        self.onglet_parametres.fonction_principale(
            settings=self.creer_liste_parametres()
            | {
                "gdf_eau": ouvrir_fichier(
                    direction_fichier=self.constantes.direction_donnees_geographiques,
                    nom_fichier="carte_monde_lacs.pkl",
                    defaut=None,
                ),
            }
        )

    def initialiser_sauvegarde(self, reinitialiser: bool):

        if not reinitialiser:
            nom = self.nom_individu.currentText()
            sauv = self.sauvegarde.get(nom, {})
        else:
            nom = ""
            self.nom_individu.setCurrentText(nom)
            self.nom_individu.blockSignals(True)
            self.nom_individu.setCurrentIndex(-1)
            self.nom_individu.blockSignals(False)
            sauv = {}

        # Onglet des paramètres du profil
        self.onglet_param_profil.initialiser_param_profil(**sauv)

        self.set_langue_interface()

        # Onglet des paramètres de cartes
        self.onglet_parametres.initialiser_onglet(**sauv)

        # Onglet de sélection des destinations
        self.onglet_selection_destinations.initialiser_onglet(nom=nom)

        # Onglet de statistiques
        self.onglet_statistiques.initialiser_onglet()

        # Récupération des destinations
        if "dictionnaire_voyages" in list(sauv.keys()):

            self.set_dictionnaire_destinations(
                dictionnaire=sauv.get("dictionnaire_voyages", {})
            )

        else:

            voyages_temp = {}
            reg_dict_temp = sauv.get("dictionnaire_regions") or {}
            dep_dict_temp = sauv.get("dictionnaire_departements") or {}

            for pays in list(reg_dict_temp.keys()):
                voyages_temp[
                    voyage_id(
                        voyages=voyages_temp,
                        clef=None,
                        longueur=self.longueur_id_voyage,
                    )
                ] = creer_voyage(
                    nom=None,
                    date_deb=None,
                    date_fin=None,
                    regions={pays: reg_dict_temp.get(pays)},
                    departements={},
                    langue=self.langue,
                )
            for pays in list(dep_dict_temp.keys()):
                voyages_temp[
                    voyage_id(
                        voyages=voyages_temp,
                        clef=None,
                        longueur=self.longueur_id_voyage,
                    )
                ] = creer_voyage(
                    nom=None,
                    date_deb=None,
                    date_fin=None,
                    regions={},
                    departements={pays: dep_dict_temp.get(pays)},
                    langue=self.langue,
                )

            self.set_dictionnaire_destinations(dictionnaire=voyages_temp)

        self.set_style()

    def supprimer_clef(self, clef):

        # Pop-up afin de s'assurer de la décision
        if not PopupOuiNon(traducteur=self.traduire_depuis_id).montrer(
            titre=self.traduire_depuis_id(clef="titre_pop_up_suppression"),
            contenu=self.traduire_depuis_id(
                clef="contenu_pop_up_suppression", suffixe="."
            ),
        ):
            return

        # Suppression de l'individu
        if clef in self.sauvegarde:
            del self.sauvegarde[clef]

            # Mise à jour de la liste déroulante
            self.nom_individu.clear()
            self.nom_individu.addItems(list(self.sauvegarde.keys()))

            # Sauvegarde
            exporter_fichier(
                objet=self.sauvegarde,
                direction_fichier=self.constantes.direction_donnees_application,
                nom_fichier="sauvegarde_utilisateurs.yaml",
                sort_keys=True,
            )

            # Réinitialisation des paramètres
            self.initialiser_sauvegarde(reinitialiser=True)

    def set_dossier(self, dossier):
        self.dossier = dossier
        self.onglet_selection_destinations.set_dossier(dossier=dossier)

    def set_hemicycle_position(self, val: int):
        self.onglet_statistiques.set_hemicycle_position(val=val)

    def set_recommandations_par_pays(self, val: bool):
        self.onglet_statistiques.set_recommandations_par_pays(val=val)

    def set_recommandations_nb(self, val: int):
        self.onglet_statistiques.set_recommandations_nb(val=val)

    def ajouter_profil(self):

        nouveau_profil = PopupSaisieTexte(
            traducteur=self.traduire_depuis_id, parent=self
        ).montrer(
            titre=self.traduire_depuis_id("nom_individu_pop_up_titre"),
            texte=self.traduire_depuis_id("nom_individu_pop_up_texte", suffixe=" :"),
            placeholder=self.traduire_depuis_id(
                "nom_individu_pop_up_placeholder", suffixe="..."
            ),
            largeur=250,
        )

        # Valeur cohérente
        if nouveau_profil:

            # Valeur non existante
            if nouveau_profil not in list(self.sauvegarde.keys()):

                # Ajout du nom à la liste existante
                self.nom_individu.addItem(nouveau_profil)

                # Export sous forme de YAML
                parametres_actuels = self.creer_liste_parametres()
                parametres_actuels["nom"] = nouveau_profil
                self.sauvegarde[nouveau_profil] = parametres_actuels
                self.exporter_sauvegarde()

                # Pop-up de fin
                PopupInfo(parent=self).montrer(
                    titre=self.traduire_depuis_id("nom_individu_pop_up_titre"),
                    contenu=self.traduire_depuis_id(
                        "nom_individu_pop_up_reussite", suffixe=" !"
                    ),
                    temps_max=8000,
                )

                # Utilisation du profil en question
                self.nom_individu.setCurrentText(nouveau_profil)
                self.initialiser_sauvegarde(reinitialiser=False)

    def set_style_titre(self, taille=24):

        self.titre.setStyleSheet(
            f"font-size: {taille * self.constantes.dict_themes_temporaires.get('titre_police_coeff', 1)}px;"
            f"font-weight: bold;"
            f"text-align: center;"
            f"font-family: {self.constantes.dict_themes_temporaires.get('titre_police', 'Vivaldi')}, sans-serif;"
        )

    # def jouer_musique(self, fichier):

    #     self.musique = MusicPlayer(
    #         path=fichier,
    #         volume=0.8,
    #         start_ms=0,
    #         max_duration_ms=15000,
    #         fade_out_ms=5000,
    #     )
    #     self.musique.play()

    # def closeEvent(self, event):
    #     # Arrête la musique quand la fenêtre est fermée
    #     if hasattr(self, "musique"):
    #         self.musique.stop()
    #         event.accept()
