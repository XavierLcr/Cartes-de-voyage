################################################################################
# Projet de cartes de voyage                                                   #
# application/classes                                                          #
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
)

from application.fonctions_utiles_2_0 import obtenir_clef_par_valeur, reset_combo, exporter_fichier


class OngletSelectionnerDestinations(QWidget):

    # Signal de modification des lieux visités
    dict_modif = pyqtSignal(dict)

    def __init__(self, constantes, fct_principale, fct_traduire, fct_pop_up):
        super().__init__()

        # Variables globales de la classe
        self.dicts_granu = {"region": {}, "dep": {}}
        self.dossier_stockage = None
        self.langue = "français"
        self.nom_individu = ""

        # Fonctions et constantes
        self.constantes = constantes
        self.fonction_principale = fct_principale
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
        self.liste_endroits.setGridSize(QSize(250, 25))
        self.telecharger_lieux_visites = QPushButton()
        self.telecharger_lieux_visites.clicked.connect(self.exporter_yamls_visites)
        self.bouton_sauvegarde2 = QPushButton()
        self.bouton_sauvegarde2.clicked.connect(lambda: self.fonction_principale(True))

        # Remplir les déroulés
        self.liste_des_pays.addItems(self.constantes.regions_par_pays.keys())
        self.liste_des_pays.currentTextChanged.connect(self.maj_liste_reg_dep_pays)
        self.liste_niveaux.currentTextChanged.connect(self.maj_liste_reg_dep_pays)
        self.liste_endroits.itemChanged.connect(self.changer_item_liste_pays)

        layout_selection_params = QHBoxLayout()
        layout_selection_params.addWidget(self.liste_des_pays)
        layout_selection_params.addWidget(self.liste_niveaux)
        layout_selection_params.addWidget(self.telecharger_lieux_visites)
        layout_selection_params.addWidget(self.bouton_sauvegarde2)
        layout_selection_params.setStretch(0, 3)  # Le premier widget prend plus de place
        layout_selection_params.setStretch(1, 3)  # Le deuxième widget prend plus de place
        layout_selection_params.setStretch(2, 1)  # Le troisième widget prend moins de place
        layout_selection_params.setStretch(3, 1)  # Le troisième widget prend moins de place

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
        self.groupe_chargement_yaml = QGroupBox()
        layout_groupe_chargement_yaml = QHBoxLayout()
        layout_groupe_chargement_yaml.addWidget(self.fichier_yaml_1_bouton)
        layout_groupe_chargement_yaml.addWidget(self.fichier_yaml_2_bouton)
        self.groupe_chargement_yaml.setLayout(layout_groupe_chargement_yaml)

        layout.addWidget(self.groupe_selection_lieux)
        layout.addWidget(self.groupe_chargement_yaml)

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
                    self.fichier_yaml_1 = data  # Stocke les données du YAML 1
                    self.dicts_granu["region"] = data

                else:
                    self.chemin_fichier_yaml_2 = chemin_yaml
                    self.fichier_yaml_2 = data  # Stocke les données du YAML 2
                    self.dicts_granu["dep"] = data

            self.dict_modif.emit(self.dicts_granu)
            self.maj_liste_reg_dep_pays()
            self.set_langue(langue=None)

    def exporter_yamls_visites(self):

        self.fonction_principale(True)

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
            if nom is None:
                nom = ""

            gran = self.constantes.parametres_traduits["granularite"][self.langue]
            nom = f"{nom}{' – ' if nom != '' else nom}{self.fonction_traduire(clef='granularite_pays_visites')}"

            nom_yaml_regions = f"{nom} – {gran['Régions']}.yaml"
            nom_yaml_departements = f"{nom} – {gran['Départements']}.yaml"

            try:

                # Export des régions
                exporter_fichier(
                    objet=self.dicts_granu["region"],
                    direction_fichier=self.dossier_stockage,
                    nom_fichier=nom_yaml_regions,
                    sort_keys=True,
                )

                # Export des départements
                exporter_fichier(
                    objet=self.dicts_granu["dep"],
                    direction_fichier=self.dossier_stockage,
                    nom_fichier=nom_yaml_departements,
                    sort_keys=True,
                )

                self.telecharger_lieux_visites.setText("📥✅")
                QTimer.singleShot(3000, lambda: self.telecharger_lieux_visites.setText("📥"))

            except:

                self.fonction_pop_up(
                    titre=self.fonction_traduire("pop_up_probleme_titre", suffixe="."),
                    contenu=self.fonction_traduire(
                        "export_pas_fonctionnel",
                        suffixe=".",
                    ),
                    temps_max=10000,
                )

    def set_dossier(self, dossier):
        self.dossier_stockage = dossier

    def set_nom_individu(self, nom):
        self.nom_individu = nom

    def set_dict_granu(self, dictionnaire: dict):
        self.dicts_granu = dictionnaire

    def set_emoji_sauvegarde(self):
        self.bouton_sauvegarde2.setText("💾✅")
        QTimer.singleShot(3000, lambda: self.bouton_sauvegarde2.setText("💾"))

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
        self.bouton_sauvegarde2.setText("💾")
        self.bouton_sauvegarde2.setToolTip(
            self.fonction_traduire("sauvegarder_profil", suffixe=".")
        )

        # Chargement des YAMLs
        self.groupe_chargement_yaml.setTitle(
            self.fonction_traduire("titre_chargement_yamls", prefixe="... ")
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

        pays_i = self.liste_des_pays.currentText()
        niveau_i = obtenir_clef_par_valeur(
            valeur=self.liste_niveaux.currentText(),
            dictionnaire=self.constantes.parametres_traduits["granularite"][self.langue],
        )

        self.liste_endroits.blockSignals(True)  # ⚠️ Empêche les signaux pendant le remplissage
        self.liste_endroits.clear()

        if niveau_i == "Régions":
            liste_end = self.constantes.regions_par_pays.get(pays_i, [])
        elif niveau_i == "Départements":
            liste_end = self.constantes.departements_par_pays.get(pays_i, [])
        else:
            liste_end = []

        for item in liste_end:
            liste_item = QListWidgetItem(item)
            liste_item.setFlags(liste_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)

            # Si déjà sélectionné dans le dict, on coche
            clef = "region" if niveau_i == "Régions" else "dep"
            est_coche = item in self.dicts_granu.get(clef, {}).get(pays_i, [])
            liste_item.setCheckState(
                Qt.CheckState.Checked if est_coche else Qt.CheckState.Unchecked
            )
            self.liste_endroits.addItem(liste_item)

        self.liste_endroits.blockSignals(False)

        # Connecte le signal (une seule fois idéalement)
        try:
            self.liste_endroits.itemChanged.disconnect()
        except TypeError:
            pass
        self.liste_endroits.itemChanged.connect(self.changer_item_liste_pays)

    def changer_item_liste_pays(self, item):

        pays_i = self.liste_des_pays.currentText()
        niveau_i = obtenir_clef_par_valeur(
            valeur=self.liste_niveaux.currentText(),
            dictionnaire=self.constantes.parametres_traduits["granularite"][self.langue],
        )
        texte = item.text()

        # Détermine la clé du dictionnaire selon le niveau
        clef = "region" if niveau_i == "Régions" else "dep"

        # Initialise le dictionnaire pour le pays s’il n’existe pas
        if pays_i not in self.dicts_granu[clef]:
            self.dicts_granu[clef][pays_i] = []

        # Ajoute ou retire l’élément selon son état
        if item.checkState() == Qt.CheckState.Checked:
            if texte not in self.dicts_granu[clef][pays_i]:
                self.dicts_granu[clef][pays_i].append(texte)
                self.dicts_granu[clef][pays_i].sort()
                self.dicts_granu[clef] = {
                    pays: self.dicts_granu[clef][pays] for pays in sorted(self.dicts_granu[clef])
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
