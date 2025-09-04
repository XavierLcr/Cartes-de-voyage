################################################################################
# MesVoyages                                                                   #
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
from PyQt6.QtCore import QTimer

# Scripts et fonctions du projet
import constantes
from _3_Calculs._1_2_creer_graphique import utiliser_style_dynamique
from _0_Utilitaires import _0_1_Fonctions_utiles
from _4_Interface._4_1_Onglets.onglet_1 import onglet_1
from _4_Interface._4_1_Onglets import onglet_2, onglet_3, onglet_5
from _4_Interface._4_1_Onglets.onglet_4 import onglet_4


warnings.filterwarnings("ignore")


# Import de la sauvegarde
sauvegarde = _0_1_Fonctions_utiles.ouvrir_fichier(
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

        # Variables globales
        self.langue = "français"

        # === Premier onglet ===

        self.onglet_parametres = onglet_1.OngletParametres(
            gdf_eau=_0_1_Fonctions_utiles.ouvrir_fichier(
                direction_fichier=constantes.direction_donnees_geographiques,
                nom_fichier="carte_monde_lacs.pkl",
                defaut=None,
            ),
            constantes=constantes,
            liste_individus=list(sauvegarde.keys()),
            fct_traduction=self.traduire_depuis_id,
            fct_pop_up=self.montrer_popup,
        )
        self.tabs.addTab(self.onglet_parametres, "Paramètres")
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
        self.onglet_parametres.creation_cartes_bouton.clicked.connect(self.publier_cartes)
        # Mise à jour du style
        self.onglet_parametres.utiliser_theme.stateChanged.connect(self.set_style)
        self.onglet_parametres.color_combo.currentTextChanged.connect(self.set_style)
        self.onglet_parametres.theme_combo.currentTextChanged.connect(self.set_style)
        # Suppression d'un individu
        self.onglet_parametres.suppression_profil.clicked.connect(
            lambda: self.supprimer_clef(self.onglet_parametres.nom_individu.currentText())
        )
        # Dossier de stockage
        self.onglet_parametres.envoi_dossier.connect(self.set_dossier)

        # === Deuxième onglet ===

        self.dicts_granu = {"region": {}, "dep": {}}
        self.selection_destinations = onglet_2.OngletSelectionnerDestinations(
            constantes=constantes,
            fct_traduire=self.traduire_depuis_id,
            fct_sauvegarde=self.exporter_liste_parametres,
            fct_pop_up=self.montrer_popup,
        )
        self.tabs.addTab(self.selection_destinations, "Création de la liste des pays visités")
        self.selection_destinations.dict_modif.connect(self.set_dictionnaire_destinations)

        # === Troisième onglet ===
        self.onglet_resume_pays = onglet_3.OngletResumeDestinations(
            traduire_depuis_id=self.traduire_depuis_id,
            emojis_pays=constantes.emojis_pays,
            parent=None,
        )
        self.tabs.addTab(self.onglet_resume_pays, "📊")

        # === Quatrième onglet ===

        self.onglet_top_pays_visites = onglet_4.OngletTopPays(
            constantes=constantes,
            table_superficie=_0_1_Fonctions_utiles.ouvrir_fichier(
                direction_fichier=constantes.direction_donnees_application,
                nom_fichier="table_superficie.pkl",
                defaut=None,
            ),
            parent=None,
        )
        self.tabs.addTab(self.onglet_top_pays_visites, "Pays les plus visités")

        # === Cinquième onglet ===

        self.onglet_description_application = onglet_5.OngletInformations(
            fct_traduire=self.traduire_depuis_id, version_logiciel=constantes.version_logiciel
        )
        self.tabs.addTab(self.onglet_description_application, "ℹ️")

        # === Mise en forme ===

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        self.reinitialisation_parametres(nom_aussi=True, set_interface=True)

    def set_langue_interface(self):
        """Met à jour les textes des widgets selon la langue sélectionnée."""

        self.langue = _0_1_Fonctions_utiles.obtenir_clef_par_valeur(
            dictionnaire=constantes.dict_langues_dispo,
            valeur=self.onglet_parametres.langue_utilisee.currentText(),
        )

        # Titres généraux
        self.setWindowTitle(self.traduire_depuis_id("titre_windows"))
        self.onglet_parametres.titre.setText(self.traduire_depuis_id(clef="titre_application"))

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

        # Onglet 1
        self.tabs.setTabText(
            self.tabs.indexOf(self.onglet_parametres),
            self.traduire_depuis_id(
                "titre_onglet_1",
                suffixe=(" 🎨"),
            ),
        )
        self.onglet_parametres.set_langue()

        # Onglet 2
        self.selection_destinations.set_langue(langue=self.langue)

        # Onglet 3
        self.onglet_resume_pays.set_langue(nouvelle_langue=self.langue)

        # Onglet 4
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.onglet_top_pays_visites),
            self.traduire_depuis_id("description_onglet_4", suffixe="."),
        )
        self.onglet_top_pays_visites.set_entetes(
            texte_region=self.traduire_depuis_id(
                "classement_selon_regions", prefixe="<b>", suffixe="</b>"
            ),
            texte_departement=self.traduire_depuis_id(
                "classement_selon_departements", prefixe="<b>", suffixe="</b>"
            ),
            texte_onglet_1=self.traduire_depuis_id(
                "titre_sous_onglet_4_1",
                suffixe=(" 🗺️"),
            ),
            texte_onglet_2=self.traduire_depuis_id(
                "titre_sous_onglet_4_2",
                suffixe=(" 🏆"),
            ),
        )

        self.onglet_top_pays_visites.set_langue(nouvelle_langue=self.langue)

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
            _0_1_Fonctions_utiles.obtenir_clef_par_valeur(
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
            liste_theme_temp = constantes.liste_ambiances.get(
                _0_1_Fonctions_utiles.obtenir_clef_par_valeur(
                    dictionnaire=constantes.parametres_traduits["themes_cartes"].get(
                        self.langue, {}
                    ),
                    valeur=self.onglet_parametres.theme_combo.currentText(),
                )
            )

            # Récupération des teintes utilisées
            liste_teintes_temp = constantes.liste_couleurs.get(
                _0_1_Fonctions_utiles.obtenir_clef_par_valeur(
                    dictionnaire=constantes.parametres_traduits["teintes_couleurs"].get(
                        self.langue, {}
                    ),
                    valeur=self.onglet_parametres.color_combo.currentText(),
                )
            )

        except:
            return

        # Sortie si une valeur n'existe pas
        if liste_theme_temp is None or liste_teintes_temp is None:
            return

        # Appliquer les styles dynamiques
        self.setStyleSheet(
            utiliser_style_dynamique(
                style=(
                    0
                    if self.onglet_parametres.utiliser_theme.isChecked()
                    else int(constantes.parametres_application["interface_foncee"] + 1)
                ),
                nuances=liste_theme_temp,
                teinte=liste_teintes_temp,
                limite_essais=50,
            )
        )

    def creer_liste_parametres(self):

        langue = _0_1_Fonctions_utiles.obtenir_clef_par_valeur(
            valeur=self.onglet_parametres.langue_utilisee.currentText(),
            dictionnaire=constantes.dict_langues_dispo,
        )

        return {
            "nom": self.onglet_parametres.nom_individu.currentText(),
            "granularite": _0_1_Fonctions_utiles.obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.granularite_visite.currentText(),
                dictionnaire=constantes.parametres_traduits["granularite"][langue],
            ),
            "granularite_fond": _0_1_Fonctions_utiles.obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.granularite_fond.currentText(),
                dictionnaire=constantes.parametres_traduits["granularite"][langue],
            ),
            "langue": langue,
            "couleur": _0_1_Fonctions_utiles.obtenir_clef_par_valeur(
                valeur=self.onglet_parametres.color_combo.currentText(),
                dictionnaire=constantes.parametres_traduits["teintes_couleurs"][langue],
            ),
            "couleur_fond_carte": self.onglet_parametres.couleur_fond_checkbox.isChecked(),
            "theme": _0_1_Fonctions_utiles.obtenir_clef_par_valeur(
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
            "max_cartes_additionnelles": {
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
            "format_onglet_3": self.onglet_resume_pays.donner_mise_en_forme(),
        }

    def exporter_liste_parametres(self):

        parametres = self.creer_liste_parametres()
        if parametres["nom"] is None or parametres["nom"] in [""]:
            parametres["nom"] = _0_1_Fonctions_utiles.formater_temps_actuel()
        sauvegarde[parametres["nom"]] = copy.deepcopy(parametres)

        # Ajout à la liste déroulante
        if parametres["nom"] not in [
            self.onglet_parametres.nom_individu.itemText(i)
            for i in range(self.onglet_parametres.nom_individu.count())
        ]:
            self.onglet_parametres.nom_individu.addItem(parametres["nom"])

        # Export sous forme de YAML
        _0_1_Fonctions_utiles.exporter_fichier(
            objet=sauvegarde,
            direction_fichier=constantes.direction_donnees_application,
            nom_fichier="sauvegarde_utilisateurs.yaml",
            sort_keys=True,
        )

        # Gestion des autres onglets
        self.selection_destinations.set_nom_individu(nom=parametres["nom"])

        # Visualisation de la sauvegarde
        self.selection_destinations.set_emoji_sauvegarde()
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

    def set_dictionnaire_destinations(self, dictionnaire: dict):
        self.dicts_granu = dictionnaire
        self.selection_destinations.set_dict_granu(dictionnaire=self.dicts_granu)
        self.onglet_resume_pays.set_dicts_granu(dict_nv=copy.deepcopy(self.dicts_granu))
        self.onglet_top_pays_visites.set_dicts_granu(dict_nv=copy.deepcopy(self.dicts_granu))

    def publier_cartes(self):

        # Export
        self.exporter_liste_parametres()

        # Publication des cartes
        self.onglet_parametres.fonction_principale(
            settings=self.creer_liste_parametres() | {"liste_dfs": liste_gdfs}
        )

    def initialiser_sauvegarde(self, sauvegarde_complete):

        self.reinitialisation_parametres(nom_aussi=False, set_interface=False)
        sauv = sauvegarde_complete.get(self.onglet_parametres.nom_individu.currentText(), {})

        # Nom
        if sauv.get("nom") is not None:

            # Dossier de publication
            if sauv.get("dossier_stockage") is not None:
                self.set_dossier(dossier=sauv.get("dossier_stockage"), onglet_parametres=True)

            # Langue
            if sauv.get("langue") is not None:
                self.onglet_parametres.langue_utilisee.setCurrentIndex(
                    self.onglet_parametres.langue_utilisee.findText(
                        constantes.dict_langues_dispo.get(sauv.get("langue"), "Français")
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
                "couleur_fond_carte": self.onglet_parametres.couleur_fond_checkbox,
                # Onglet 3
                "format_onglet_3": self.onglet_resume_pays.mise_en_forme,
            }
            for nom_cle, checkbox in checkboxes.items():
                if sauv.get(nom_cle) is not None:
                    checkbox.setChecked(sauv.get(nom_cle))

            # Qualité
            if sauv.get("qualite") is not None:
                self.onglet_parametres.curseur_qualite.setValue(sauv.get("qualite"))

            # Format
            if sauv.get("format") is not None:
                self.onglet_parametres.format_cartes.setCurrentText(sauv.get("format"))

            # Récupération des destinations
            self.set_dictionnaire_destinations(
                dictionnaire={
                    "region": (sauv.get("dictionnaire_regions", {})),
                    "dep": sauv.get("dictionnaire_departements", {}),
                }
            )

            # Chargement de la granularité
            _0_1_Fonctions_utiles.restaurer_valeur_combo(
                combo=self.onglet_parametres.granularite_visite,
                dict_parent=constantes.parametres_traduits["granularite"],
                langue=self.langue,
                valeur=sauv.get("granularite"),
                defaut_index=0,
            )

            # Chargement de la granularité de fond
            _0_1_Fonctions_utiles.restaurer_valeur_combo(
                combo=self.onglet_parametres.granularite_fond,
                dict_parent=constantes.parametres_traduits["granularite"],
                langue=self.langue,
                valeur=sauv.get("granularite_fond"),
                defaut_index=0,
            )

            # Chargement du thème
            _0_1_Fonctions_utiles.restaurer_valeur_combo(
                combo=self.onglet_parametres.theme_combo,
                dict_parent=constantes.parametres_traduits["themes_cartes"],
                langue=self.langue,
                valeur=sauv.get("theme"),
                defaut_index=0,
            )

            # Chargement de la teinte
            _0_1_Fonctions_utiles.restaurer_valeur_combo(
                combo=self.onglet_parametres.color_combo,
                dict_parent=constantes.parametres_traduits["teintes_couleurs"],
                langue=self.langue,
                valeur=sauv.get("couleur"),
                defaut_index=0,
            )

            # Limite de cartes
            if sauv.get("max_cartes_additionnelles") is not None:
                {
                    5: self.onglet_parametres.radio_carte_1,
                    10: self.onglet_parametres.radio_carte_2,
                    15: self.onglet_parametres.radio_carte_3,
                }.get(
                    sauv.get("max_cartes_additionnelles"),
                    self.onglet_parametres.radio_carte_sans_limite,
                ).setChecked(
                    True
                )

            self.selection_destinations.reset_yaml()

    def reinitialisation_parametres(self, nom_aussi: bool = True, set_interface: bool = True):

        # Paramètres individuels
        if nom_aussi == True:
            self.onglet_parametres.nom_individu.setCurrentText("")
            self.onglet_parametres.nom_individu.blockSignals(True)
            self.onglet_parametres.nom_individu.setCurrentIndex(-1)
            self.onglet_parametres.nom_individu.blockSignals(False)

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
        self.onglet_parametres.couleur_fond_checkbox.setChecked(False)

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
        self.selection_destinations.liste_des_pays.setCurrentIndex(1)
        self.selection_destinations.liste_niveaux.setCurrentIndex(0)
        ## Changement forcé de l'index
        self.selection_destinations.liste_des_pays.setCurrentIndex(0)

        self.selection_destinations.reset_yaml()
        self.onglet_resume_pays.set_mise_en_forme(coche=False)

        if set_interface:
            # self.set_langue_interface()
            self.set_style()

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
            self.onglet_parametres.nom_individu.clear()
            self.onglet_parametres.nom_individu.addItems(list(sauvegarde.keys()))

            # sauvegarde
            _0_1_Fonctions_utiles.exporter_fichier(
                objet=sauvegarde,
                direction_fichier=constantes.direction_donnees_application,
                nom_fichier="sauvegarde_utilisateurs.yaml",
                sort_keys=True,
            )

            # Réinitialisation des paramètres
            self.reinitialisation_parametres(nom_aussi=True, set_interface=True)

    def set_dossier(self, dossier, onglet_parametres=False):
        self.dossier = dossier
        self.selection_destinations.set_dossier(dossier=dossier)
        if onglet_parametres:
            self.onglet_parametres.set_dossier(dossier=dossier)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Création d'une liste vide pour stocker les GDF
    liste_gdfs = [None] * 3

    # Lancement du thread de chargement
    threading.Thread(
        target=_0_1_Fonctions_utiles.charger_gdfs,
        args=(liste_gdfs, constantes.direction_donnees_geographiques, 3),
        daemon=True,
    ).start()

    # Lancement de l'application
    window = MesVoyagesApplication()
    window.show()

    sys.exit(app.exec())
