################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Sélection des destinations                                        #
################################################################################


import os, yaml

# PyQt6
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QComboBox,
    QPushButton,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
)

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    obtenir_clef_par_valeur,
    exporter_fichier,
    formater_temps_actuel,
    separer_combinaisons,
    aplanir_dictionnaire,
    tronquer_dict,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import reset_combo, set_emoji_sauvegarde
from _4_Interface._4_2_Style._4_2_2_styles_complementaires import style_bouton_yaml


# 1 -- Classe de sélection des destinations ------------------------------------


class OngletSelectionnerDestinations(QWidget):

    # Signal de modification des lieux visités
    dict_modif = pyqtSignal(dict)

    def __init__(self, constantes, fct_sauvegarde, fct_traduire, fct_pop_up):
        super().__init__()

        # Variables globales de la classe
        self.dicts_granu = {"region": {}, "dep": {}}
        self.dossier_stockage = None
        self.langue = "français"
        self.nom_individu = ""

        # Fonctions et constantes
        self.constantes = constantes
        self.fonction_traduire = fct_traduire
        self.fonction_pop_up = fct_pop_up

        # Ajouter un layout et un label au deuxième onglet
        layout = QVBoxLayout()
        self.groupe_selection_lieux = QGroupBox()
        layout_selection_lieux = QVBoxLayout()

        self.liste_des_pays = QComboBox()
        self.liste_niveaux = QComboBox()
        self.avertissement_prio = QLabel()
        self.avertissement_prio.setWordWrap(True)
        self.liste_endroits = QListWidget()
        self.liste_endroits.setWrapping(True)
        self.liste_endroits.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.liste_endroits.setGridSize(QSize(220, 22))
        self.telecharger_lieux_visites = QPushButton()
        self.telecharger_lieux_visites.clicked.connect(self.exporter_yamls_visites)
        self.bouton_sauvegarde = QPushButton()
        self.bouton_sauvegarde.clicked.connect(fct_sauvegarde)
        self.bouton_sauvegarde.clicked.connect(
            lambda: set_emoji_sauvegarde(self.bouton_sauvegarde, 3000)
        )

        # Remplir les déroulés
        self.liste_des_pays.addItems(self.constantes.hierarchie_par_pays.keys())
        self.liste_des_pays.currentIndexChanged.connect(self.maj_liste_reg_dep_pays)
        self.liste_niveaux.currentIndexChanged.connect(self.maj_liste_reg_dep_pays)
        self.liste_endroits.itemChanged.connect(self.changer_item_liste_pays)

        layout_selection_params = QHBoxLayout()
        layout_selection_params.addWidget(self.liste_des_pays)
        layout_selection_params.addWidget(self.liste_niveaux)
        layout_selection_params.addWidget(self.telecharger_lieux_visites)
        layout_selection_params.addWidget(self.bouton_sauvegarde)
        layout_selection_params.setStretch(
            0, 3
        )  # Le premier widget prend plus de place
        layout_selection_params.setStretch(
            1, 3
        )  # Le deuxième widget prend plus de place
        layout_selection_params.setStretch(
            2, 1
        )  # Le troisième widget prend moins de place
        layout_selection_params.setStretch(
            3, 1
        )  # Le troisième widget prend moins de place

        layout_selection_lieux.addLayout(layout_selection_params)
        layout_selection_lieux.addWidget(self.avertissement_prio)
        layout_selection_lieux.addWidget(self.liste_endroits)
        self.groupe_selection_lieux.setLayout(layout_selection_lieux)

        # Téléchargement des YAMLs

        ## Stockage des données YAML
        self.fichier_yaml_1 = None
        self.fichier_yaml_2 = None

        ## Création des boutons pour charger les YAML
        self.chemin_fichier_yaml_1 = None
        self.chemin_fichier_yaml_2 = None
        self.fichier_yaml_1_bouton = QPushButton()
        self.fichier_yaml_1_bouton.clicked.connect(lambda: self.charger_yaml(1))

        self.fichier_yaml_2_bouton = QPushButton()
        self.fichier_yaml_2_bouton.clicked.connect(lambda: self.charger_yaml(2))

        ## Layout et Groupbox
        self.bouton_afficher_option_yaml = QPushButton()
        self.bouton_afficher_option_yaml.clicked.connect(
            self.afficher_option_alternative
        )
        self.groupe_chargement_yaml = QGroupBox()
        self.groupe_chargement_yaml.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout_groupe_chargement_yaml = QHBoxLayout()
        layout_groupe_chargement_yaml.addWidget(self.fichier_yaml_1_bouton)
        layout_groupe_chargement_yaml.addWidget(self.fichier_yaml_2_bouton)
        self.groupe_chargement_yaml.setLayout(layout_groupe_chargement_yaml)
        self.groupe_chargement_yaml.setVisible(False)
        layout_yaml = QHBoxLayout()
        layout_yaml.addWidget(
            self.bouton_afficher_option_yaml, alignment=Qt.AlignmentFlag.AlignLeft
        )
        layout_yaml.addWidget(self.groupe_chargement_yaml)

        layout.addWidget(self.groupe_selection_lieux)
        layout.addLayout(layout_yaml)

        self.setLayout(layout)

    def charger_yaml(self, num):

        chemin_yaml, _ = QFileDialog.getOpenFileName(
            self,
            self.fonction_traduire("pop_up_yaml"),
            "",
            "YAML Files (*.yaml *.yml)",
        )
        if chemin_yaml:

            with open(chemin_yaml, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

            if num == 1:

                self.chemin_fichier_yaml_1 = chemin_yaml
                # Séparation des lieux existants ou non
                dict_sep = separer_combinaisons(
                    dico1=data,
                    dico2=tronquer_dict(d=self.constantes.hierarchie_par_pays, n=2),
                )
                self.fichier_yaml_1 = dict_sep[True]  # Stocke les données du YAML 1
                self.dicts_granu["region"] = dict_sep[True]

            else:

                self.chemin_fichier_yaml_2 = chemin_yaml
                dict_sep = separer_combinaisons(
                    dico1=data,
                    dico2=aplanir_dictionnaire(self.constantes.hierarchie_par_pays),
                )
                self.fichier_yaml_2 = dict_sep[True]  # Stocke les données du YAML 2
                self.dicts_granu["dep"] = dict_sep[True]

            if dict_sep[False]:

                for pays in dict_sep[False]:

                    temp = (
                        ", ".join(dict_sep[False][pays])
                        if dict_sep[False][pays]
                        else ""
                    )
                    dict_sep[False][
                        pays
                    ] = f"– <b>{pays}</b>{(f' ({temp})' if temp else '')}"

                self.fonction_pop_up(
                    titre=self.fonction_traduire("pop_up_attention_titre"),
                    contenu=self.fonction_traduire(
                        "lieux_sans_correspondance",
                        suffixe=f" :<br>{f' ; <br>'.join(list(dict_sep[False].values()))}.",
                    ),
                    temps_max=None,
                    bouton_ok=True,
                    boutons_oui_non=False,
                    renvoyer_popup=False,
                )

            self.dict_modif.emit(self.dicts_granu)
            self.maj_liste_reg_dep_pays()
            self.set_langue(langue=None)

    def exporter_yamls_visites(self):

        if self.dossier_stockage is None:

            self.fonction_pop_up(
                contenu=self.fonction_traduire(
                    "pop_up_pas_de_dossier_de_stockage",
                    suffixe=".",
                ),
                titre=self.fonction_traduire("pop_up_probleme_titre", suffixe="."),
                temps_max=10000,
            )

        else:

            nom = self.nom_individu
            if nom is None or nom in [""]:
                nom = formater_temps_actuel()

            gran = self.constantes.parametres_traduits["granularite"][self.langue]
            nom = (
                f"{nom}{' – '}{self.fonction_traduire(clef='granularite_pays_visites')}"
            )

            nom_yaml_regions = f"{nom} – {gran['Régions']}.yaml"
            nom_yaml_departements = f"{nom} – {gran['Départements']}.yaml"

            try:

                # Export des régions
                if self.dicts_granu["region"] != {}:
                    exporter_fichier(
                        objet=self.dicts_granu["region"],
                        direction_fichier=self.dossier_stockage,
                        nom_fichier=nom_yaml_regions,
                        sort_keys=True,
                    )

                # Export des départements
                if self.dicts_granu["dep"] != {}:
                    exporter_fichier(
                        objet=self.dicts_granu["dep"],
                        direction_fichier=self.dossier_stockage,
                        nom_fichier=nom_yaml_departements,
                        sort_keys=True,
                    )

                self.telecharger_lieux_visites.setText("📥✅")
                QTimer.singleShot(
                    3000, lambda: self.telecharger_lieux_visites.setText("📥")
                )

            except Exception as e:

                self.fonction_pop_up(
                    titre=self.fonction_traduire("pop_up_probleme_titre", suffixe="."),
                    contenu=self.fonction_traduire(
                        "export_pas_fonctionnel",
                        suffixe=f".\n[{e}]",
                    ),
                    temps_max=10000,
                )

    def set_dossier(self, dossier):
        self.dossier_stockage = dossier

    def set_nom_individu(self, nom):
        self.nom_individu = nom

    def set_dict_granu(self, dictionnaire: dict):
        self.dicts_granu = dictionnaire

    def set_langue(self, langue):

        # Mise à jour de la langue
        if langue is not None:
            self.langue = langue

        # Mise à jour de l'interface
        self.groupe_selection_lieux.setTitle(
            self.fonction_traduire("titre_choix_destinations_visitees")
        )
        self.avertissement_prio.setText(
            self.fonction_traduire("avertissement_onglet_2", prefixe="⚠️ ", suffixe=".")
        )

        if self.groupe_chargement_yaml.isVisible():

            self.bouton_afficher_option_yaml.setText(
                self.fonction_traduire("masquer_option_yaml", prefixe="", suffixe="")
            )

        else:

            self.bouton_afficher_option_yaml.setText(
                self.fonction_traduire("montrer_option_yaml", prefixe="", suffixe="")
            )

        reset_combo(
            self.liste_niveaux,
            [
                self.constantes.parametres_traduits["granularite"][self.langue][k]
                for k in ["Régions", "Départements"]
            ],
        )
        self.telecharger_lieux_visites.setText("📥")
        self.telecharger_lieux_visites.setToolTip(
            self.fonction_traduire("telecharger_lieux_visites", suffixe=".")
        )
        self.bouton_sauvegarde.setText("💾")
        self.bouton_sauvegarde.setToolTip(
            self.fonction_traduire("sauvegarder_profil", suffixe=".")
        )
        self.liste_des_pays.setToolTip(
            self.fonction_traduire("precision_diplomatique_onglet_2", suffixe=".")
        )

        # Chargement des YAMLs
        self.groupe_chargement_yaml.setTitle(
            self.fonction_traduire("titre_chargement_yamls")
        )
        self.groupe_chargement_yaml.setToolTip(
            self.fonction_traduire("description_titre_chargement_yamls", suffixe=".")
        )
        self.fichier_yaml_1_bouton.setText(
            self.fonction_traduire("yaml_regions")
            if self.fichier_yaml_1 is None
            else os.path.basename(self.chemin_fichier_yaml_1)
        )
        self.fichier_yaml_2_bouton.setText(
            self.fonction_traduire("yaml_departements")
            if self.fichier_yaml_2 is None
            else os.path.basename(self.chemin_fichier_yaml_2)
        )

    def maj_liste_reg_dep_pays(self):
        """
        Remplit self.liste_endroits (QListWidget) selon la granularité choisie.
        - Si niveau == "Régions" : on affiche une liste de régions cochables.
        - Si niveau == "Départements" : on affiche les régions (non cochables) puis
        les départements (cochables) sous chaque région.
        """

        pays_i = self.liste_des_pays.currentText()
        niveau_i = obtenir_clef_par_valeur(
            valeur=self.liste_niveaux.currentText(),
            dictionnaire=self.constantes.parametres_traduits["granularite"][
                self.langue
            ],
        )

        self.liste_endroits.blockSignals(True)
        self.liste_endroits.clear()

        data = self.constantes.hierarchie_par_pays.get(pays_i, {})

        if not data:
            self.liste_endroits.blockSignals(False)
            return

        if niveau_i == "Régions":

            # liste plate de régions cochables
            for region in sorted(data.keys()):

                item = QListWidgetItem(region)
                # cochable + sélectionnable
                item.setFlags(
                    item.flags()
                    | Qt.ItemFlag.ItemIsUserCheckable
                    | Qt.ItemFlag.ItemIsSelectable
                    | Qt.ItemFlag.ItemIsEnabled
                )
                est_coche = region in (
                    self.dicts_granu.get("region", {}).get(pays_i, [])
                )
                item.setCheckState(
                    Qt.CheckState.Checked if est_coche else Qt.CheckState.Unchecked
                )

                # style visuel pour distinguer
                font = item.font()
                font.setBold(False)
                item.setFont(font)
                self.liste_endroits.addItem(item)

        else:  # niveau_i == "Départements"

            # Afficher régions (non cochables) puis départements cochables
            for i, region in enumerate(sorted(data.keys())):

                # deps = sorted(data[region])
                # nb_total = len(deps)
                # nb_checked = sum(
                #     dep in (self.dicts_granu.get("dep", {}).get(pays_i, []) or [])
                #     for dep in deps
                # )

                # region_item = QListWidgetItem(f"{region} ({nb_checked}/{nb_total})")
                region_item = QListWidgetItem(region)

                # Item région
                region_item.setFlags(
                    Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
                )
                font = region_item.font()
                font.setBold(True)
                font.setUnderline(True)
                font.setKerning(False)
                region_item.setFont(font)
                region_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.liste_endroits.addItem(region_item)

                for dep in sorted(data[region]):
                    dep_item = QListWidgetItem(dep)  # indentation visuelle
                    dep_item.setFlags(
                        dep_item.flags()
                        | Qt.ItemFlag.ItemIsUserCheckable
                        | Qt.ItemFlag.ItemIsEnabled
                        | Qt.ItemFlag.ItemIsSelectable
                    )
                    est_coche = dep in (
                        (self.dicts_granu.get("dep") or {}).get(pays_i, [])
                    )
                    dep_item.setCheckState(
                        Qt.CheckState.Checked if est_coche else Qt.CheckState.Unchecked
                    )
                    self.liste_endroits.addItem(dep_item)

                # optionnel : ligne vide pour lisibilité
                spacer = QListWidgetItem("")
                spacer.setFlags(Qt.ItemFlag.NoItemFlags)
                spacer.setSizeHint(QSize(0, 4))
                self.liste_endroits.addItem(spacer)

        self.liste_endroits.blockSignals(False)

        # reconnecte proprement le signal itemChanged
        try:
            self.liste_endroits.itemChanged.disconnect()
        except TypeError:
            pass
        self.liste_endroits.itemChanged.connect(self.changer_item_liste_pays)

    def changer_item_liste_pays(self, item):

        pays_i = self.liste_des_pays.currentText()
        texte = item.text()

        # Détermine la clé du dictionnaire selon le niveau
        clef = (
            "region"
            if obtenir_clef_par_valeur(
                valeur=self.liste_niveaux.currentText(),
                dictionnaire=self.constantes.parametres_traduits["granularite"][
                    self.langue
                ],
            )
            == "Régions"
            else "dep"
        )

        # Initialise le dictionnaire pour le pays s’il n’existe pas
        self.dicts_granu[clef] = self.dicts_granu.get(clef) or {}
        self.dicts_granu[clef][pays_i] = self.dicts_granu[clef].get(pays_i) or []

        # Ajoute ou retire l’élément selon son état
        if item.checkState() == Qt.CheckState.Checked:
            if texte not in self.dicts_granu[clef][pays_i]:
                self.dicts_granu[clef][pays_i].append(texte)
                self.dicts_granu[clef][pays_i].sort()
                self.dicts_granu[clef] = {
                    pays: self.dicts_granu[clef][pays]
                    for pays in sorted(self.dicts_granu[clef])
                }
        else:
            if texte in self.dicts_granu[clef][pays_i]:
                self.dicts_granu[clef][pays_i].remove(texte)
                if self.dicts_granu[clef][pays_i] == []:
                    del self.dicts_granu[clef][pays_i]

        self.dict_modif.emit(self.dicts_granu)

    def reset_yaml(self):
        self.fichier_yaml_1 = None
        self.fichier_yaml_2 = None
        self.set_langue(langue=None)

    def afficher_option_alternative(self):

        (
            self.groupe_chargement_yaml.hide()
            if self.groupe_chargement_yaml.isVisible()
            else self.groupe_chargement_yaml.show()
        )

        self.set_langue(langue=None)

    def set_style(self, style, teinte, nuances):

        self.bouton_afficher_option_yaml.setStyleSheet(
            style_bouton_yaml(style=style, teinte=teinte, nuances=nuances)
        )

    def initialiser_onglet(self, nom: str | None, reinitialiser: bool):

        # Reset des YAMLs et masquage de la partie correspondante
        self.reset_yaml()
        self.groupe_chargement_yaml.hide()

        # Mise à jour du nom
        self.set_nom_individu(nom=nom or "")

        if reinitialiser:

            # Mise à jour forcée de l'index
            self.liste_niveaux.setCurrentIndex(0)
            self.liste_des_pays.setCurrentIndex(1)
            QTimer.singleShot(
                0,
                lambda: self.liste_des_pays.setCurrentIndex(0),
            )
