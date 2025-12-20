################################################################################
# Projet de cartes de voyage                                                   #
# Application principale                                                       #
################################################################################


import os, sys, warnings, copy, textwrap, threading

# PyQt6
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QTabWidget,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer, Qt

# Scripts et fonctions du projet
import constantes
from _0_Utilitaires import _0_1_fonctions_utiles_gen, _0_3_fonctions_utiles_pyqt6
from _0_Utilitaires._0_2_fonctions_graphiques import renvoyer_couleur_texte
from _4_Interface._4_1_Onglets.onglet_1 import onglet_1
from _4_Interface._4_1_Onglets.onglet_2 import onglet_2
from _4_Interface._4_1_Onglets.onglet_4 import onglet_4
from _4_Interface._4_1_Onglets import onglet_3, onglet_5
from _4_Interface._4_2_Style._4_2_1_style_principal import style_dynamique_application
from _4_Interface._4_2_Style._4_2_3_musique import MusicPlayer
from _4_Interface._4_2_Style._4_2_4_pluie_emojis import VuePluieEmojis


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
            constantes.parametres_application["application_position_largeur"],
            constantes.parametres_application["application_position_hauteur"],
            constantes.parametres_application["application_largeur"],
            constantes.parametres_application["application_hauteur"],
        )
        self.setWindowIcon(
            QIcon(
                os.path.join(
                    constantes.direction_donnees_application, "icone_application.ico"
                )
            )
        )

        self.liste_onglets = QTabWidget()

        # Variables globales
        self.langue = "français"

        # === Premier onglet ===

        self.onglet_parametres = onglet_1.OngletParametres(
            constantes=constantes,
            liste_individus=list(sauvegarde.keys()),
            fct_traduction=self.traduire_depuis_id,
            fct_pop_up=self.montrer_popup,
        )
        self.liste_onglets.addTab(self.onglet_parametres, "Paramètres")
        # Langue
        self.onglet_parametres.langue_utilisee.currentIndexChanged.connect(
            self.set_langue_interface
        )
        # Chargement d'un individu
        self.onglet_parametres.nom_individu.currentIndexChanged.connect(
            lambda: self.initialiser_sauvegarde(sauvegarde)
        )
        # Réinitialisation
        self.onglet_parametres.reinit_parametres.clicked.connect(
            lambda: self.reinitialisation_parametres(True)
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
        # Suppression d'un individu
        self.onglet_parametres.suppression_profil.clicked.connect(
            lambda: self.supprimer_clef(
                self.onglet_parametres.nom_individu.currentText()
            )
        )
        # Dossier de stockage
        self.onglet_parametres.envoi_dossier.connect(self.set_dossier)

        # === Deuxième onglet ===

        self.dicts_granu = {"region": {}, "dep": {}}
        self.onglet_selection_destinations = onglet_2.OngletSelectionnerDestinations(
            constantes=constantes,
            fct_traduire=self.traduire_depuis_id,
            fct_sauvegarde=self.exporter_liste_parametres,
            fct_pop_up=self.montrer_popup,
        )
        self.liste_onglets.addTab(
            self.onglet_selection_destinations, "Création de la liste des pays visités"
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
                nom_fichier="table_superficie.pkl",
                defaut=None,
            ),
            parent=None,
            fct_traduction=self.traduire_depuis_id,
        )
        self.liste_onglets.addTab(self.onglet_statistiques, "Pays les plus visités")

        # === Cinquième onglet ===

        self.onglet_description_application = onglet_5.OngletInformations(
            fct_traduire=self.traduire_depuis_id,
            version_logiciel=constantes.version_logiciel,
        )
        self.liste_onglets.addTab(self.onglet_description_application, "ℹ️")

        # === Mise en forme === #

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.liste_onglets)
        self.setLayout(main_layout)
        self.liste_onglets.setCurrentIndex(0 if sauvegarde else 4)

        self.reinitialisation_parametres(nom_aussi=True, set_interface=True)

        if "pluie_emojis" in constantes.dict_themes_temporaires.keys():
            self.vue_pluie = VuePluieEmojis(
                constantes=constantes,
                duree_ms=15000,
                intervalle_timer_ms=30,
                force_vent_globale=1.5,
                parent=self,
            )
            self.vue_pluie.show()

    def set_langue_interface(self):
        """Met à jour les textes des widgets selon la langue sélectionnée."""

        self.langue = _0_1_fonctions_utiles_gen.obtenir_clef_par_valeur(
            dictionnaire=constantes.dict_langues_dispo,
            valeur=self.onglet_parametres.langue_utilisee.currentText(),
        )

        # Titres généraux
        self.setWindowTitle(self.traduire_depuis_id("titre_windows"))

        # Onglet 1
        self.liste_onglets.setTabText(
            self.liste_onglets.indexOf(self.onglet_parametres),
            self.traduire_depuis_id(
                "titre_onglet_1",
                suffixe=(" 🎨"),
            ),
        )
        self.onglet_parametres.set_langue()

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

        # Onglet 4
        self.liste_onglets.setTabText(
            self.liste_onglets.indexOf(self.onglet_statistiques),
            self.traduire_depuis_id(
                "titre_onglet_4",
                suffixe=(" 📊"),
            ),
        )
        self.onglet_statistiques.set_langue(nouvelle_langue=self.langue)

        # Onglet 5
        self.onglet_description_application.set_langue()

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

        langue = (
            _0_1_fonctions_utiles_gen.obtenir_clef_par_valeur(
                dictionnaire=constantes.dict_langues_dispo,
                valeur=self.onglet_parametres.langue_utilisee.currentText(),
            )
            if langue is None
            else self.langue
        )

        # Résolution de la clé si on part d'un ID
        clef = constantes.phrases_interface.get(clef, clef) if depuis_id else clef

        # Récupération de la traduction
        traduction = (
            prefixe
            + constantes.outil_differentes_langues.get(clef, {}).get(langue, clef)
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

    def set_style(self):

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
            else int(constantes.parametres_application["interface_foncee"] + 1)
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

        langue = _0_1_fonctions_utiles_gen.obtenir_clef_par_valeur(
            valeur=self.onglet_parametres.langue_utilisee.currentText(),
            dictionnaire=constantes.dict_langues_dispo,
        )

        return {
            "nom": self.onglet_parametres.nom_individu.currentText(),
            "granularite": _0_1_fonctions_utiles_gen.obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.granularite_visite.currentText(),
                dictionnaire=constantes.parametres_traduits["granularite"][langue],
            ),
            "granularite_fond": _0_1_fonctions_utiles_gen.obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.granularite_fond.currentText(),
                dictionnaire=constantes.parametres_traduits["granularite"][langue],
            ),
            "langue": langue,
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
            "dossier_stockage": self.onglet_parametres.dossier_stockage,
            "carte_du_monde": self.onglet_parametres.carte_monde.isChecked(),
            "europe": self.onglet_parametres.europe.isChecked(),
            "asie": self.onglet_parametres.asie.isChecked(),
            "amerique": self.onglet_parametres.amerique.isChecked(),
            "afrique": self.onglet_parametres.afrique.isChecked(),
            "moyen_orient": self.onglet_parametres.moyen_orient.isChecked(),
            "autres_regions": self.onglet_parametres.autres_regions.isChecked(),
            "sortir_cartes_granu_inf": self.onglet_parametres.sortir_cartes_granu_inf.isChecked(),
            "cartes_des_pays": self.onglet_parametres.carte_pays.isChecked(),
            "limite_n_cartes": {
                self.onglet_parametres.radio_carte_1: 5,
                self.onglet_parametres.radio_carte_2: 10,
                self.onglet_parametres.radio_carte_3: 15,
            }.get(self.onglet_parametres.groupe_radio_max_cartes.checkedButton(), None),
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
            self.onglet_parametres.nom_individu.itemText(i)
            for i in range(self.onglet_parametres.nom_individu.count())
        ]:
            self.onglet_parametres.nom_individu.addItem(parametres["nom"])

        # Export sous forme de YAML
        _0_1_fonctions_utiles_gen.exporter_fichier(
            objet=sauvegarde,
            direction_fichier=constantes.direction_donnees_application,
            nom_fichier="sauvegarde_utilisateurs.yaml",
            sort_keys=True,
        )

        # Gestion des autres onglets
        self.onglet_selection_destinations.set_nom_individu(nom=parametres["nom"])

        # Visualisation de la sauvegarde
        self.onglet_selection_destinations.set_emoji_sauvegarde()
        self.onglet_parametres.set_emoji_sauvegarde()

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

    def initialiser_sauvegarde(self, sauvegarde_complete):

        self.reinitialisation_parametres(nom_aussi=False, set_interface=False)
        sauv = sauvegarde_complete.get(
            self.onglet_parametres.nom_individu.currentText(), {}
        )

        # Nom
        if sauv.get("nom") is not None:

            # Nom
            self.onglet_selection_destinations.set_nom_individu(nom=sauv.get("nom"))

            # Dossier de publication
            if sauv.get("dossier_stockage") is not None:
                self.set_dossier(
                    dossier=sauv.get("dossier_stockage"), onglet_parametres=True
                )

            # Langue
            if sauv.get("langue") is not None:
                self.onglet_parametres.langue_utilisee.setCurrentIndex(
                    self.onglet_parametres.langue_utilisee.findText(
                        constantes.dict_langues_dispo.get(
                            sauv.get("langue"), "Français"
                        )
                    )
                )

            # Cartes à publier
            checkboxes = {
                # Onglet principal
                "carte_du_monde": self.onglet_parametres.carte_monde,
                "cartes_des_pays": self.onglet_parametres.carte_pays,
                "asie": self.onglet_parametres.asie,
                "amerique": self.onglet_parametres.amerique,
                "afrique": self.onglet_parametres.afrique,
                "europe": self.onglet_parametres.europe,
                "moyen_orient": self.onglet_parametres.moyen_orient,
                "autres_regions": self.onglet_parametres.autres_regions,
                "sortir_cartes_granu_inf": self.onglet_parametres.sortir_cartes_granu_inf,
            }
            for nom_cle, checkbox in checkboxes.items():
                if sauv.get(nom_cle) is not None:
                    checkbox.setChecked(sauv.get(nom_cle))

            # Qualité
            if (val := sauv.get("qualite")) is not None:
                self.onglet_parametres.curseur_qualite.setValue(val)

            # Format
            if (fmt := sauv.get("format")) is not None:
                self.onglet_parametres.format_cartes.setCurrentText(fmt)

            # Récupération des destinations
            self.set_dictionnaire_destinations(
                dictionnaire={
                    "region": (sauv.get("dictionnaire_regions", {})),
                    "dep": sauv.get("dictionnaire_departements", {}),
                }
            )

            # Chargement de la granularité
            _0_3_fonctions_utiles_pyqt6.restaurer_valeur_combo(
                combo=self.onglet_parametres.granularite_visite,
                dict_parent=constantes.parametres_traduits.get("granularite", {}),
                langue=self.langue,
                valeur=sauv.get("granularite"),
                defaut_index=0,
            )

            # Chargement de la granularité de fond
            _0_3_fonctions_utiles_pyqt6.restaurer_valeur_combo(
                combo=self.onglet_parametres.granularite_fond,
                dict_parent=constantes.parametres_traduits.get("granularite", {}),
                langue=self.langue,
                valeur=sauv.get("granularite_fond"),
                defaut_index=0,
            )

            # Chargement du thème
            _0_3_fonctions_utiles_pyqt6.restaurer_valeur_combo(
                combo=self.onglet_parametres.theme_combo,
                dict_parent=constantes.parametres_traduits.get("themes_cartes", {}),
                langue=self.langue,
                valeur=sauv.get("theme"),
                defaut_index=0,
            )

            # Chargement de la teinte
            _0_3_fonctions_utiles_pyqt6.restaurer_valeur_combo(
                combo=self.onglet_parametres.color_combo,
                dict_parent=constantes.parametres_traduits.get("teintes_couleurs", {}),
                langue=self.langue,
                valeur=sauv.get("couleur"),
                defaut_index=0,
            )

            # Chargement de l'arrière plan
            _0_3_fonctions_utiles_pyqt6.restaurer_valeur_combo(
                combo=self.onglet_parametres.combo_couleur_fond,
                dict_parent=constantes.parametres_traduits.get("arrière_plans", {}),
                langue=self.langue,
                valeur=sauv.get("couleur_fond_carte"),
                defaut_index=0,
            )

            # Limite de cartes
            if sauv.get("limite_n_cartes") is not None:
                {
                    5: self.onglet_parametres.radio_carte_1,
                    10: self.onglet_parametres.radio_carte_2,
                    15: self.onglet_parametres.radio_carte_3,
                }.get(
                    sauv.get("limite_n_cartes"),
                    self.onglet_parametres.radio_carte_sans_limite,
                ).setChecked(
                    True
                )

            self.onglet_selection_destinations.reset_yaml()

    def reinitialisation_parametres(
        self, nom_aussi: bool = True, set_interface: bool = True
    ):

        # Paramètres individuels
        if nom_aussi == True:
            self.onglet_parametres.nom_individu.setCurrentText("")
            self.onglet_parametres.nom_individu.blockSignals(True)
            self.onglet_parametres.nom_individu.setCurrentIndex(-1)
            self.onglet_parametres.nom_individu.blockSignals(False)
            self.onglet_selection_destinations.set_nom_individu(nom="")

        # Destinations
        self.set_dictionnaire_destinations(dictionnaire={"region": {}, "dep": {}})

        # Dossier
        self.set_dossier(dossier=None, onglet_parametres=True)

        self.onglet_parametres.radio_carte_2.setChecked(True)

        # Paramètres de publication
        self.onglet_parametres.curseur_qualite.setValue(
            int(
                (
                    constantes.parametres_application["qualite_min"]
                    + constantes.parametres_application["qualite_max"]
                )
                / 2
            )
        )
        self.onglet_parametres.format_cartes.setCurrentText("png")
        self.onglet_parametres.combo_couleur_fond.setCurrentIndex(0)

        # Cartes à créer
        self.onglet_parametres.carte_monde.setChecked(False)
        self.onglet_parametres.carte_pays.setChecked(True)
        self.onglet_parametres.asie.setChecked(False)
        self.onglet_parametres.amerique.setChecked(False)
        self.onglet_parametres.afrique.setChecked(False)
        self.onglet_parametres.europe.setChecked(True)
        self.onglet_parametres.moyen_orient.setChecked(False)
        self.onglet_parametres.autres_regions.setChecked(False)

        # Autres paramètres
        self.onglet_parametres.sortir_cartes_granu_inf.setChecked(False)
        self.onglet_parametres.utiliser_theme.setChecked(False)

        if set_interface:
            self.set_langue_interface()

        # Onglet 2
        self.onglet_selection_destinations.liste_niveaux.setCurrentIndex(0)
        self.onglet_selection_destinations.liste_des_pays.setCurrentIndex(1)
        # self.onglet_selection_destinations.liste_des_pays.setCurrentIndex(0)
        QTimer.singleShot(
            0,
            lambda: self.onglet_selection_destinations.liste_des_pays.setCurrentIndex(
                0
            ),
        )
        ## Changement forcé de l'index

        self.onglet_selection_destinations.reset_yaml()

        if set_interface:
            # self.set_langue_interface()
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
            self.onglet_parametres.nom_individu.clear()
            self.onglet_parametres.nom_individu.addItems(list(sauvegarde.keys()))

            # sauvegarde
            _0_1_fonctions_utiles_gen.exporter_fichier(
                objet=sauvegarde,
                direction_fichier=constantes.direction_donnees_application,
                nom_fichier="sauvegarde_utilisateurs.yaml",
                sort_keys=True,
            )

            # Réinitialisation des paramètres
            self.reinitialisation_parametres(nom_aussi=True, set_interface=True)

    def set_dossier(self, dossier, onglet_parametres=False):
        self.dossier = dossier
        self.onglet_selection_destinations.set_dossier(dossier=dossier)
        if onglet_parametres:
            self.onglet_parametres.set_dossier(dossier=dossier)

    def jouer_musique(self, fichier):

        self.musique = MusicPlayer(
            path=fichier,
            volume=0.8,
            start_ms=0,
            max_duration_ms=15000,
            fade_out_ms=5000,
        )
        self.musique.play()

    def closeEvent(self, event):
        # Arrête la musique quand la fenêtre est fermée
        if hasattr(self, "musique"):
            self.musique.stop()
            event.accept()


# 3 -- Lancement de la classe principale ---------------------------------------


if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Création d'une liste vide pour stocker les GDF
    liste_gdfs = [None] * 3

    # Lancement du thread de chargement
    threading.Thread(
        target=_0_1_fonctions_utiles_gen.charger_gdfs,
        args=(liste_gdfs, constantes.direction_donnees_geographiques, 3),
        daemon=True,
    ).start()

    # Lancement de l'application
    window = MesVoyagesApplication()
    window.setMaximumSize(1200, 800)
    window.show()

    sys.exit(app.exec())
