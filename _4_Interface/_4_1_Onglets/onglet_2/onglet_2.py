################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Sélection des destinations                                        #
################################################################################


import os, yaml

# PyQt6
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6 import QtGui

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
    QDialog,
    QScrollArea,
    QTreeWidgetItem,
    QTreeWidget,
)

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    obtenir_clef_par_valeur,
    exporter_fichier,
    formater_temps_actuel,
    separer_combinaisons,
    aplanir_dictionnaire,
    tronquer_dict,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    reset_combo,
    set_emoji_sauvegarde,
    creer_QLabel_centre,
    creer_ligne_horizontale,
    vider_layout,
)
from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
)
from _4_Interface._4_1_Onglets.onglet_2.onglet_2_ajout_voyage import CreerVoyage
from _4_Interface._4_2_Style._4_2_2_styles_complementaires import style_bouton_yaml


# 1 -- Classe de sélection des destinations ------------------------------------


class OngletSelectionnerDestinations(QWidget):

    # Signal de modification des lieux visités
    dict_modif = pyqtSignal(dict)

    def __init__(self, constantes, fct_sauvegarde, fct_traduire, fct_pop_up):
        super().__init__()

        # Variables globales de la classe
        self.voyages = {}
        self.dicts_granu = {"region": {}, "dep": {}}
        self.dossier_stockage = None
        self.langue = "français"
        self.nom_individu = ""

        # Fonctions et constantes
        self.constantes = constantes
        self.fonction_traduire = fct_traduire
        self.fonction_pop_up = fct_pop_up

        # Layout de l'onglet
        layout = QVBoxLayout()

        # Avertissement
        self.avertissement_prio = QLabel()
        self.avertissement_prio.setWordWrap(True)
        layout.addWidget(self.avertissement_prio)

        # Boutons
        layout_boutons = QHBoxLayout()
        self.ajouter_voyage_bouton = QPushButton()
        self.ajouter_voyage_bouton.clicked.connect(self.ajouter_voyage)
        layout_boutons.addWidget(self.ajouter_voyage_bouton, stretch=5)

        self.telecharger_lieux_visites = QPushButton()
        self.telecharger_lieux_visites.clicked.connect(self.exporter_yamls_visites)
        layout_boutons.addWidget(self.telecharger_lieux_visites, stretch=1)
        self.bouton_sauvegarde = QPushButton()
        self.bouton_sauvegarde.clicked.connect(fct_sauvegarde)
        self.bouton_sauvegarde.clicked.connect(
            lambda: set_emoji_sauvegarde(self.bouton_sauvegarde, 3000)
        )
        layout_boutons.addWidget(self.bouton_sauvegarde, stretch=1)

        # Voyages effectués
        self.liste_voyage_groupbox = QGroupBox()
        self.liste_voyage_layout = QVBoxLayout()
        self.liste_voyage_groupbox.setLayout(self.liste_voyage_layout)

        self.liste_voyage = self._creer_scroll()
        self.liste_voyage_layout.addWidget(self.liste_voyage)

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

        layout.addLayout(layout_boutons)
        layout.addWidget(self.liste_voyage_groupbox)
        layout.addStretch()
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
        self.liste_voyage_groupbox.setTitle(
            self.fonction_traduire("titre_choix_destinations_visitees")
        )
        self.avertissement_prio.setText(
            self.fonction_traduire("avertissement_onglet_2", prefixe="⚠️ ", suffixe=".")
        )

        self.ajouter_voyage_bouton.setText(
            self.fonction_traduire("bouton_ajouter_voyage")
        )

        if self.groupe_chargement_yaml.isVisible():

            self.bouton_afficher_option_yaml.setText(
                self.fonction_traduire("masquer_option_yaml", prefixe="", suffixe="")
            )

        else:

            self.bouton_afficher_option_yaml.setText(
                self.fonction_traduire("montrer_option_yaml", prefixe="", suffixe="")
            )

        self.telecharger_lieux_visites.setText("📥")
        self.telecharger_lieux_visites.setToolTip(
            self.fonction_traduire("telecharger_lieux_visites", suffixe=".")
        )
        self.bouton_sauvegarde.setText("💾")
        self.bouton_sauvegarde.setToolTip(
            self.fonction_traduire("sauvegarder_profil", suffixe=".")
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

        self.couleurs = {
            1: renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#C8E6C9",
                sombre="#512B52",
            ),
            2: renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#f2f0a5",
                sombre="#856039",
            ),
            3: renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#EDE5FF",
                sombre="#1221C1",
            ),
            4: renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#DCF5FF",
                sombre="#7E0E5C",
            ),
        }

    def initialiser_onglet(self, nom: str | None):

        # Reset des YAMLs et masquage de la partie correspondante
        self.reset_yaml()
        self.groupe_chargement_yaml.hide()

        # Mise à jour du nom
        self.set_nom_individu(nom=nom or "")

    def ajouter_voyage(self):

        objet = CreerVoyage(
            visites={},
            clef=None,
            constantes=self.constantes,
            fct_traduction=self.fonction_traduire,
            parent=self,
        )

        if objet.exec() == QDialog.DialogCode.Accepted:
            clef, voyage = objet.resultat
            self.voyages[clef] = voyage
        print(self.voyages)
        self.afficher_voyages(vbox=self.liste_voyage_layout)

    def _creer_scroll(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Layout interne propre pour le scroll
        container = QWidget()
        container_layout = QVBoxLayout(
            container
        )  # ⚡ différent de self.liste_voyage_layout
        scroll.setWidget(container)

        # On garde une référence vers container si besoin pour ajouter dynamiquement
        scroll.container_layout = container_layout
        scroll.container_widget = container

        return scroll

    def afficher_voyages(self, vbox):
        """Affiche self.voyages dans un QTreeWidget."""

        def ajouter_voyage_elements(parent_item, data, niveau=1):
            """Ajoute récursivement les éléments de self.voyages à l'arbre."""
            if isinstance(data, dict):
                for cle, valeur in data.items():
                    # Crée un item pour la clé (ex: "Voyage 1", "Destination", etc.)
                    child = QTreeWidgetItem(parent_item, [str(cle)])
                    # Applique une couleur de fond selon le niveau
                    child.setBackground(
                        0,
                        QtGui.QBrush(
                            QtGui.QColor(self.couleurs.get(niveau, "#FFFFFF"))
                        ),
                    )
                    # Récursion pour les sous-niveaux
                    ajouter_voyage_elements(child, valeur, niveau + 1)
            elif isinstance(data, list):
                # Pour les listes (ex: ["Alice", "Bob"])
                for item in data:
                    child = QTreeWidgetItem(parent_item, [f"• {str(item)}"])
                    child.setBackground(
                        0, QtGui.QBrush(QtGui.QColor(Qt.GlobalColor.transparent))
                    )
            else:
                # Pour les valeurs simples (ex: "Paris", "01/01/2026")
                child = QTreeWidgetItem(parent_item, [str(data)])
                child.setBackground(
                    0, QtGui.QBrush(QtGui.QColor(Qt.GlobalColor.transparent))
                )

        # Nettoie le layout
        vider_layout(vbox)

        # Titre de section
        vbox.addWidget(creer_QLabel_centre(text="<b>Liste des Voyages</b>"))
        vbox.addWidget(creer_ligne_horizontale())

        # Création de l'arbre
        if self.voyages:
            tree = QTreeWidget()
            tree.setHeaderHidden(True)
            tree.setColumnCount(1)
            tree.setIndentation(20)
            tree.setExpandsOnDoubleClick(True)

            # Remplit l'arbre avec les données
            ajouter_voyage_elements(tree.invisibleRootItem(), self.voyages, niveau=1)

            # Affiche tout replié ou déployé
            tree.collapseAll()  # ou tree.expandAll()

            vbox.addWidget(tree)
        else:
            vbox.addWidget(creer_QLabel_centre(text="Aucun voyage disponible"))
