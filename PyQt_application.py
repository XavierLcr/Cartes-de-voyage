################################################################################
# Projet de cartes de voyage                                                   #
# Application principale                                                       #
################################################################################


import os, sys, warnings, copy, textwrap

# PyQt6
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QTabWidget,
    QSplashScreen,
    QComboBox,
    QPushButton,
    QLineEdit,
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QTimer, Qt

# Scripts et fonctions du projet
import constantes
from _0_Utilitaires import _0_1_fonctions_utiles_gen, _0_3_fonctions_utiles_pyqt6
from _0_Utilitaires._0_2_fonctions_graphiques import renvoyer_couleur_texte
from _4_Interface._4_1_Onglets.onglet_1 import onglet_1
from _4_Interface._4_1_Onglets.onglet_2 import onglet_2
from _4_Interface._4_1_Onglets.onglet_4 import onglet_4
from _4_Interface._4_1_Onglets import onglet_3, onglet_info
from _4_Interface._4_1_Onglets.onglet_param_profil import onglet_param_profil
from _4_Interface._4_2_Style._4_2_1_style_principal import style_dynamique_application
from _4_Interface._4_2_Style._4_2_4_pluie_emojis import VuePluieEmojis

# from _4_Interface._4_2_Style._4_2_3_musique import MusicPlayer


# Suppression d'alertes, d'avis et de messages additionnels
warnings.filterwarnings("ignore")
os.environ["QT_LOGGING_RULES"] = "qt.text.font.db=false"


# 1 -- Import des données ------------------------------------------------------


## 1.1 -- Import de la sauvegarde ----------------------------------------------


sauvegarde = _0_1_fonctions_utiles_gen.ouvrir_fichier(
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="sauvegarde_utilisateurs.yaml",
    defaut={},
)


# 2 -- Classe principale -------------------------------------------------------


class MesVoyagesApplication(QWidget):
    def __init__(self):
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

        self.liste_onglets = QTabWidget()
        self.liste_onglets.setUsesScrollButtons(False)

        # Variables globales
        self.langue = "français"
        self.theme_application = True

        # === Profil sélectionné ===

        profile_container = QWidget()
        profile_layout = QHBoxLayout(profile_container)
        profile_layout.setContentsMargins(8, 0, 8, 0)
        self.nom_individu = QComboBox(self)
        self.nom_individu.setEditable(False)
        self.nom_individu.setPlaceholderText("")
        self.nom_individu_label = _0_3_fonctions_utiles_pyqt6.creer_QLabel_centre()
        profile_layout.addWidget(self.nom_individu_label)
        self.nom_individu.addItems(list(sauvegarde.keys()))
        profile_layout.addWidget(self.nom_individu)
        self.liste_onglets.setCornerWidget(profile_container, Qt.Corner.TopRightCorner)
        bouton_ajout = QPushButton()
        bouton_ajout.setText("➕")
        bouton_ajout.setStyleSheet(
            """
            QPushButton {
                font-weight: bold;
                background-color: transparent;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color:#D6F0EE
            }
        """
        )
        bouton_ajout.setFixedWidth(40)
        bouton_ajout.clicked.connect(self.ajouter_profil)
        profile_layout.addWidget(bouton_ajout)

        # === Premier onglet ===

        self.onglet_parametres = onglet_1.OngletParametres(
            constantes=constantes,
            fct_traduction=self.traduire_depuis_id,
            fct_pop_up=self.montrer_popup,
        )
        self.liste_onglets.addTab(self.onglet_parametres, "Paramètres")
        # Chargement d'un individu
        self.nom_individu.currentIndexChanged.connect(
            lambda: self.initialiser_sauvegarde(reinitialiser=False)
        )
        # Réinitialisation
        self.onglet_parametres.reinit_parametres.clicked.connect(
            lambda: self.initialiser_sauvegarde(reinitialiser=True)
        )
        # Export
        self.onglet_parametres.bouton_sauvegarde.clicked.connect(
            self.exporter_liste_parametres
        )
        # Publication des cartes
        self.onglet_parametres.creation_cartes_bouton.clicked.connect(
            self.publier_cartes
        )
        # Mise à jour du style
        self.onglet_parametres.utiliser_theme.stateChanged.connect(self.set_style)
        self.onglet_parametres.color_combo.currentTextChanged.connect(self.set_style)
        self.onglet_parametres.theme_combo.currentTextChanged.connect(self.set_style)

        # === Deuxième onglet ===

        self.dicts_granu = {"region": {}, "dep": {}}
        self.onglet_selection_destinations = onglet_2.OngletSelectionnerDestinations(
            constantes=constantes,
            fct_traduire=self.traduire_depuis_id,
            fct_sauvegarde=self.exporter_liste_parametres,
            fct_pop_up=self.montrer_popup,
        )
        self.liste_onglets.addTab(
            self.onglet_selection_destinations, "Sélection des pays visités"
        )
        self.onglet_selection_destinations.dict_modif.connect(
            self.set_dictionnaire_destinations
        )

        # === Troisième onglet ===

        self.onglet_resume_destinations = onglet_3.OngletResumeDestinations(
            traduire_depuis_id=self.traduire_depuis_id,
            constantes=constantes,
            parent=None,
        )
        self.liste_onglets.addTab(self.onglet_resume_destinations, "📊")

        # === Quatrième onglet ===

        self.onglet_statistiques = onglet_4.OngletTopPays(
            constantes=constantes,
            table_superficie=_0_1_fonctions_utiles_gen.ouvrir_fichier(
                direction_fichier=constantes.direction_donnees_application,
                nom_fichier="table_superficie.parquet",
                defaut=None,
                afficher_erreur="Problème avec la table de superficie.",
            ),
            parent=None,
            fct_traduction=self.traduire_depuis_id,
        )
        self.liste_onglets.addTab(self.onglet_statistiques, "Pays les plus visités")

        # === Cinquième onglet ===

        self.onglet_param_profil = onglet_param_profil.OngletParametresProfil(
            constantes=constantes, fct_traduction=self.traduire_depuis_id
        )
        self.liste_onglets.addTab(self.onglet_param_profil, "⚙️")

        # Langue
        self.onglet_param_profil.signal_langue.connect(self.set_langue_interface)

        # Dossier de stockage
        self.onglet_param_profil.signal_dossier.connect(self.set_dossier)

        # Sauvegarde d'un individu
        self.onglet_param_profil.bouton_sauvegarde.clicked.connect(
            self.exporter_liste_parametres
        )

        # Suppression d'un individu
        self.onglet_param_profil.suppression_profil.clicked.connect(
            lambda: self.supprimer_clef(self.nom_individu.currentText())
        )

        # == Sixième onglet ===

        self.onglet_description_application = onglet_info.OngletInformations(
            fct_traduire=self.traduire_depuis_id,
            version_logiciel=constantes.version_logiciel,
        )
        self.liste_onglets.addTab(self.onglet_description_application, "ℹ️")

        # === Mise en forme === #

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.liste_onglets)
        self.setLayout(main_layout)
        self.liste_onglets.setCurrentIndex(0 if sauvegarde else 4)

        self.initialiser_sauvegarde(reinitialiser=True)

        if "pluie_emojis" in constantes.dict_themes_temporaires.keys():
            self.vue_pluie = VuePluieEmojis(
                constantes=constantes,
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

        # Profil sélectionné
        self.nom_individu_label.setText("👤")
        self.nom_individu.setPlaceholderText(
            self.traduire_depuis_id("nom_individu_placeholder", suffixe="...")
        )

        # Onglet 1
        self.liste_onglets.setTabText(
            self.liste_onglets.indexOf(self.onglet_parametres),
            self.traduire_depuis_id(
                "titre_onglet_1",
                suffixe=(" 🎨"),
            ),
        )
        self.onglet_parametres.set_langue(langue=self.langue)

        # Onglet 2
        self.liste_onglets.setTabText(
            self.liste_onglets.indexOf(self.onglet_selection_destinations),
            self.traduire_depuis_id(
                "titre_onglet_2",
                suffixe=(" 📌"),
            ),
        )
        self.onglet_selection_destinations.set_langue(langue=self.langue)

        # Onglet 3
        self.liste_onglets.setTabText(
            self.liste_onglets.indexOf(self.onglet_resume_destinations),
            self.traduire_depuis_id(
                "titre_onglet_3",
                suffixe=(" 🧭"),
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
            depuis_id: Si True, traite `cle` comme un ID à chercher dans `constantes.phrases_interface`.
            largeur_max: Si spécifié, tronque le texte à cette largeur maximale.

        Returns:
            str: La traduction formatée.
        """

        # Résolution de la clé si on part d'un ID
        clef = constantes.phrases_interface.get(clef, clef) if depuis_id else clef

        # Récupération de la traduction
        traduction = (
            prefixe
            + constantes.outil_differentes_langues.get(clef, {}).get(self.langue, clef)
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
            theme_temp = constantes.liste_ambiances.get(
                _0_1_fonctions_utiles_gen.obtenir_clef_par_valeur(
                    dictionnaire=constantes.parametres_traduits["themes_cartes"].get(
                        self.langue, {}
                    ),
                    valeur=self.onglet_parametres.theme_combo.currentText(),
                )
            )

            # Récupération des teintes utilisées
            teinte_temp = constantes.liste_couleurs.get(
                _0_1_fonctions_utiles_gen.obtenir_clef_par_valeur(
                    dictionnaire=constantes.parametres_traduits["teintes_couleurs"].get(
                        self.langue, {}
                    ),
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

        # Onglet 2
        self.onglet_selection_destinations.set_style(
            style=style_temp, teinte=teinte_temp, nuances=theme_temp
        )

        # Onglet 4.1
        self.onglet_statistiques.hemicycle.set_style(
            couleur=renvoyer_couleur_texte(
                style=style_temp,
                couleur=self.palette().color(self.backgroundRole()).name(),
            )
        )

        # Onglet 4.3
        self.onglet_statistiques.recommandations.set_bouton_recommandation(
            style=style_temp, teinte=teinte_temp, nuances=theme_temp
        )

    def creer_liste_parametres(self):

        langue = self.langue

        return {
            # Paramètres individuels
            "nom": self.nom_individu.currentText(),
            "granularite": _0_1_fonctions_utiles_gen.obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.granularite_visite.currentText(),
                dictionnaire=constantes.parametres_traduits["granularite"][langue],
            ),
            "granularite_fond": _0_1_fonctions_utiles_gen.obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.granularite_fond.currentText(),
                dictionnaire=constantes.parametres_traduits["granularite"][langue],
            ),
            "langue": langue,
            "adresse_email": self.onglet_param_profil.get_email(),
            "couleur": _0_1_fonctions_utiles_gen.obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.color_combo.currentText(),
                dictionnaire=constantes.parametres_traduits["teintes_couleurs"][langue],
            ),
            "couleur_fond_carte": self.onglet_parametres.combo_couleur_fond.valeur_en_francais(),
            "theme": _0_1_fonctions_utiles_gen.obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.theme_combo.currentText(),
                dictionnaire=constantes.parametres_traduits["themes_cartes"][langue],
            ),
            "qualite": self.onglet_parametres.curseur_qualite.value(),
            "format": self.onglet_parametres.format_cartes.currentText(),
            "dossier_stockage": self.onglet_param_profil.get_dossier(),
            "ouvrir_dossier_stockage": self.onglet_param_profil.get_ouvrir_dossier(),
            "theme_application": self.onglet_param_profil.get_theme_application(),
            "carte_du_monde": self.onglet_parametres.carte_monde.isChecked(),
            "europe": self.onglet_parametres.europe.isChecked(),
            "asie": self.onglet_parametres.asie.isChecked(),
            "amerique": self.onglet_parametres.amerique.isChecked(),
            "afrique": self.onglet_parametres.afrique.isChecked(),
            "moyen_orient": self.onglet_parametres.moyen_orient.isChecked(),
            "autres_regions": self.onglet_parametres.autres_regions.isChecked(),
            "sortir_cartes_granu_inf": self.onglet_param_profil.get_sortir_cartes_granu_inf(),
            "cartes_des_pays": self.onglet_parametres.carte_pays.isChecked(),
            "limite_n_cartes": self.onglet_param_profil.get_limite_de_cartes(),
            # Lieux visités
            "dictionnaire_regions": (
                self.dicts_granu["region"] if self.dicts_granu["region"] != {} else None
            ),
            "dictionnaire_departements": (
                self.dicts_granu["dep"] if self.dicts_granu["dep"] != {} else None
            ),
        }

    def exporter_liste_parametres(self):

        parametres = self.creer_liste_parametres()
        if parametres["nom"] is None or parametres["nom"] in [""]:
            parametres["nom"] = _0_1_fonctions_utiles_gen.formater_temps_actuel(n=0)
        sauvegarde[parametres["nom"]] = copy.deepcopy(parametres) | {
            "date_publication": sauvegarde.get(parametres["nom"], {}).get(
                "date_publication", []
            )
            + [_0_1_fonctions_utiles_gen.formater_temps_actuel(n=1)]
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

        _0_1_fonctions_utiles_gen.exporter_fichier(
            objet=sauvegarde,
            direction_fichier=constantes.direction_donnees_application,
            nom_fichier="sauvegarde_utilisateurs.yaml",
            sort_keys=True,
        )

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
        msg.setTextFormat(Qt.TextFormat.RichText)
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

    def set_dictionnaire_destinations(self, dictionnaire: dict):
        self.dicts_granu = dictionnaire
        self.onglet_selection_destinations.set_dict_granu(dictionnaire=self.dicts_granu)

        self.liste_onglets.setTabVisible(
            self.liste_onglets.indexOf(self.onglet_resume_destinations),
            self.dicts_granu != {"region": {}, "dep": {}},
        )
        self.liste_onglets.setTabVisible(
            self.liste_onglets.indexOf(self.onglet_statistiques),
            self.dicts_granu != {"region": {}, "dep": {}},
        )

        self.onglet_resume_destinations.set_dicts_granu(
            dict_nv=copy.deepcopy(self.dicts_granu)
        )
        self.onglet_statistiques.set_dicts_granu(
            dict_nv=copy.deepcopy(self.dicts_granu)
        )

    def publier_cartes(self):

        # Export
        self.exporter_liste_parametres()

        # Publication des cartes
        self.onglet_parametres.fonction_principale(
            settings=self.creer_liste_parametres()
            | {
                "liste_dfs": liste_gdfs,
                "gdf_eau": _0_1_fonctions_utiles_gen.ouvrir_fichier(
                    direction_fichier=constantes.direction_donnees_geographiques,
                    nom_fichier="carte_monde_lacs.pkl",
                    defaut=None,
                ),
            }
        )

    def initialiser_sauvegarde(self, reinitialiser: bool):

        if not reinitialiser:
            nom = self.nom_individu.currentText()
            sauv = sauvegarde.get(nom, {})
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
        self.onglet_selection_destinations.initialiser_onglet(
            nom=nom, reinitialiser=reinitialiser
        )

        # Récupération des destinations
        self.set_dictionnaire_destinations(
            dictionnaire={
                "region": sauv.get("dictionnaire_regions") or {},
                "dep": sauv.get("dictionnaire_departements") or {},
            }
        )

        self.set_style()

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
            _0_1_fonctions_utiles_gen.exporter_fichier(
                objet=sauvegarde,
                direction_fichier=constantes.direction_donnees_application,
                nom_fichier="sauvegarde_utilisateurs.yaml",
                sort_keys=True,
            )

            # Réinitialisation des paramètres
            self.initialiser_sauvegarde(reinitialiser=True)

    def set_dossier(self, dossier):
        self.dossier = dossier
        self.onglet_selection_destinations.set_dossier(dossier=dossier)

    def ajouter_profil(self):

        # création de la boîte
        msg_box = QMessageBox(self)
        msg_box.setMinimumWidth(300)
        msg_box.setWindowTitle(self.traduire_depuis_id("nom_individu_pop_up_titre"))
        msg_box.setText(
            self.traduire_depuis_id("nom_individu_pop_up_texte", suffixe=" :")
        )

        # Ajout d'un champ de saisie
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(
            self.traduire_depuis_id("nom_individu_pop_up_placeholder", suffixe="...")
        )
        line_edit.setFixedWidth(250)

        # Ouverture du pop-up
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(line_edit)
        widget.setLayout(layout)

        # Ajout du widget dans le QMessageBox, sous le texte
        msg_box.layout().addWidget(widget, 1, 0, 1, msg_box.layout().columnCount())

        # Bouton "Valider"
        bouton_valider = msg_box.addButton(
            self.traduire_depuis_id("valider", suffixe=""),
            QMessageBox.ButtonRole.AcceptRole,
        )

        # Affichage
        msg_box.exec()

        if msg_box.clickedButton() == bouton_valider:

            # Récupération du nom
            nouveau_profil = line_edit.text()

            if nouveau_profil:

                if nouveau_profil not in list(sauvegarde.keys()):

                    # Ajout du nom à la liste existante
                    self.nom_individu.addItem(nouveau_profil)

                    # Export sous forme de YAML
                    parametres_actuels = self.creer_liste_parametres()
                    parametres_actuels["nom"] = nouveau_profil
                    sauvegarde[nouveau_profil] = parametres_actuels
                    self.exporter_sauvegarde()

                    # Pop-up de fin
                    self.montrer_popup(
                        titre=self.traduire_depuis_id("nom_individu_pop_up_titre"),
                        contenu=self.traduire_depuis_id(
                            "nom_individu_pop_up_reussite", suffixe=" !"
                        ),
                        temps_max=8000,
                        bouton_ok=True,
                        boutons_oui_non=False,
                        renvoyer_popup=False,
                    )

                    # Utilisation du profil en question
                    self.nom_individu.setCurrentText(nouveau_profil)
                    self.initialiser_sauvegarde(reinitialiser=False)

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


# 3 -- Lancement de la classe principale ---------------------------------------


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Affichage du logo en splash screen
    splash = QSplashScreen(
        QPixmap(
            os.path.join(
                constantes.direction_donnees_application, "icone_application.ico"
            )
        ),
        Qt.WindowType.WindowStaysOnTopHint,
    )
    splash.show()
    app.processEvents()  # force l'affichage du splash avant de charger les GDF

    # Chargement des GDF
    liste_gdfs = _0_1_fonctions_utiles_gen.charger_gdfs(
        direction_base=constantes.direction_donnees_geographiques, max_niveau=2
    )
    # liste_gdfs = []

    # Lancement de la fenêtre principale
    window = MesVoyagesApplication()
    window.show()

    # Fermeture du splash
    splash.finish(window)

    sys.exit(app.exec())
