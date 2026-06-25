################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Sélection des destinations                                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import yaml
from datetime import datetime

# PyQt6
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6 import QtGui

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QPushButton,
    QFileDialog,
    QSizePolicy,
    QDialog,
    QScrollArea,
    QTreeWidgetItem,
    QTreeWidget,
    QComboBox,
)

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    exporter_fichier,
    formater_temps_actuel,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    set_emoji_sauvegarde,
    vider_layout,
    reset_combo,
    creer_ligne_verticale,
)
from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_widget,
)
from _0_Utilitaires._0_7_fonctions_voyages import (
    detecter_type_yaml,
    voyage_id,
    creer_voyage,
    trier_voyages,
)
from _0_Utilitaires._0_11_classes_pop_up import PopupInfo
from _4_Interface._4_1_Onglets.onglet_2.onglet_2_ajout_voyage import CreerVoyage

# 1 -- Classe de sélection des destinations ------------------------------------


class OngletSelectionnerDestinations(QWidget):

    # Signal de modification des lieux visités
    dict_modif = pyqtSignal(dict)

    def __init__(self, constantes, fct_sauvegarde, fct_traduire, longueur=10):
        super().__init__()

        # Variables globales de la classe
        self.voyages = {}
        self.dossier_stockage = None
        self.langue = "français"
        self.nom_individu = ""
        self.style = 0
        self.longueur = longueur

        # Fonctions et constantes
        self.constantes = constantes
        self.fonction_traduire = fct_traduire

        # Layout de l'onglet
        layout = QVBoxLayout()

        # Avertissement
        self.avertissement_prio = QLabel()
        self.avertissement_prio.setWordWrap(True)
        layout.addWidget(self.avertissement_prio)

        # Bouton d'ajout de voyages
        self.ajouter_voyage_bouton = QPushButton()
        self.ajouter_voyage_bouton.clicked.connect(
            lambda x: self.creer_voyage_ui(clef=None)
        )

        # Liste des options de tri
        self.options_tri = QComboBox()
        self.options_tri.currentTextChanged.connect(
            lambda x: self.afficher_voyages(vbox=self.liste_voyage_layout)
        )

        # Bouton d'export des YAML
        self.telecharger_lieux_visites = QPushButton()
        self.telecharger_lieux_visites.clicked.connect(self.exporter_yamls_visites)

        # Bouton d'import d'un YAML
        self.chargement_yaml_bouton = QPushButton()
        self.chargement_yaml_bouton.clicked.connect(self.charger_yaml)

        # Bouton de sauvegarde
        self.bouton_sauvegarde = QPushButton()
        self.bouton_sauvegarde.clicked.connect(
            lambda: fct_sauvegarde(date_publication=False)
        )
        self.bouton_sauvegarde.clicked.connect(
            lambda: set_emoji_sauvegarde(self.bouton_sauvegarde, 3000)
        )

        # Ligne des boutons
        layout_boutons = QHBoxLayout()
        layout_boutons.addWidget(self.ajouter_voyage_bouton, stretch=3)
        layout_boutons.addWidget(self.options_tri, stretch=3)
        layout_boutons.addWidget(self.bouton_sauvegarde, stretch=1)
        layout_boutons.addWidget(creer_ligne_verticale())
        layout_boutons.addWidget(self.telecharger_lieux_visites, stretch=1)
        layout_boutons.addWidget(self.chargement_yaml_bouton, stretch=1)

        # Voyages effectués
        self.liste_voyage_groupbox = QGroupBox()
        self.liste_voyage_layout = QVBoxLayout()
        self.liste_voyage_groupbox.setLayout(self.liste_voyage_layout)
        self.liste_voyage_groupbox.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )

        self.liste_voyage = self._creer_scroll()
        self.liste_voyage_layout.addWidget(self.liste_voyage)

        # Layout complet
        layout.addLayout(layout_boutons)
        layout.addWidget(self.liste_voyage_groupbox)

        self.setLayout(layout)

    def charger_yaml(self):

        chemin_yaml, _ = QFileDialog.getOpenFileName(
            self,
            self.fonction_traduire("pop_up_yaml"),
            "",
            "YAML Files (*.yaml *.yml)",
        )

        if chemin_yaml:

            with open(chemin_yaml, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

            type = detecter_type_yaml(dictionnaire=data)
            # Ce sont des voyages
            if type == True:
                for clef in data.keys():
                    self.ajouter_voyage(voyage=data.get(clef), clef=None)

            elif type in ["region", "dep"]:
                for clef in data.keys():
                    self.ajouter_voyage(
                        voyage=creer_voyage(
                            nom=None,
                            date_deb=None,
                            date_fin=None,
                            regions={clef: data.get(clef)} if type == "region" else {},
                            departements=(
                                {clef: data.get(clef)} if type == "dep" else {}
                            ),
                            langue=self.langue,
                        ),
                        clef=None,
                    )

                # separer_combinaisons(
                #         dico1=data,
                #         dico2=tronquer_dict(d=self.constantes.hierarchie_par_pays, n=2),
                #     )

                # if dict_sep[False]:

                #     for pays in dict_sep[False]:

                #         temp = (
                #             ", ".join(dict_sep[False][pays])
                #             if dict_sep[False][pays]
                #             else ""
                #         )
                #         dict_sep[False][
                #             pays
                #         ] = f"– <b>{pays}</b>{(f' ({temp})' if temp else '')}"

                # PopupInfo(parent=self).montrer(
                #     titre=self.fonction_traduire("pop_up_attention_titre"),
                #     contenu=self.fonction_traduire(
                #         "lieux_sans_correspondance",
                #         suffixe=f" :<br>{f' ; <br>'.join(list(dict_sep[False].values()))}.",
                #     ),
                #     temps_max=None,
                # )

            self.dict_modif.emit(self.voyages)
            self.set_langue(langue=None)

    def exporter_yamls_visites(self):

        if self.dossier_stockage is None:

            PopupInfo(parent=self).montrer(
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

            nom = (
                f"{nom}{' – '}{self.fonction_traduire(clef='titre_liste_voyages')}.yaml"
            )

            try:

                # Export des régions
                if self.voyages:
                    exporter_fichier(
                        objet=self.voyages,
                        direction_fichier=self.dossier_stockage,
                        nom_fichier=nom,
                        sort_keys=True,
                    )

                self.telecharger_lieux_visites.setText("📥✅")
                QTimer.singleShot(
                    3000, lambda: self.telecharger_lieux_visites.setText("📥")
                )

            except Exception as e:

                PopupInfo(parent=self).montrer(
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

    def set_voyages(self, dictionnaire: dict):
        self.voyages = dictionnaire
        self.afficher_voyages(vbox=self.liste_voyage_layout)

    def set_langue(self, langue):

        # Mise à jour de la langue
        if langue is not None:
            self.langue = langue

        # Mise à jour de l'interface
        self.liste_voyage_groupbox.setTitle(
            self.fonction_traduire("titre_liste_voyages")
        )

        # Avertissement
        self.avertissement_prio.setText(
            self.fonction_traduire("avertissement_onglet_2", prefixe="⚠️ ", suffixe=".")
        )

        # Boutons
        self.ajouter_voyage_bouton.setText(
            self.fonction_traduire("bouton_ajouter_voyage")
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
        self.chargement_yaml_bouton.setToolTip(
            self.fonction_traduire("description_titre_chargement_yaml", suffixe=".")
        )
        self.chargement_yaml_bouton.setText("📂")

        # Options de tri
        self.dict_correspondances_tri = {
            self.fonction_traduire(clef): corresp
            for clef, corresp in {
                "tri_ordre_creation_voyages": "clef",
                "tri_nom_voyages": "nom",
                "tri_dates_debut_voyages": "date",
            }.items()
        }
        reset_combo(
            self.options_tri,
            list(self.dict_correspondances_tri.keys()),
        )

        self.afficher_voyages(vbox=self.liste_voyage_layout)

    def set_style(self, style, teinte, nuances):

        self.style = style

        self.couleurs = {
            1: renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#C1D9EE",
                sombre="#1A3B9B",
            ),
            2: renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#D6E4F0",
                sombre="#2A5BB8",
            ),
            3: renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#E2F0FD",
                sombre="#3A7BD5",
            ),
        }

        self.afficher_voyages(vbox=self.liste_voyage_layout)

    def initialiser_onglet(self, nom: str | None):

        # Mise à jour du nom
        self.set_nom_individu(nom=nom or "")

    def ajouter_voyage(self, voyage: dict, clef: str | None):

        clef = voyage_id(voyages=self.voyages, clef=clef, longueur=self.longueur)
        self.voyages[clef] = voyage

    def creer_voyage_ui(self, clef):

        objet = CreerVoyage(
            visites=self.voyages,
            clef=clef,
            constantes=self.constantes,
            fct_traduction=self.fonction_traduire,
            parent=self,
            longueur=self.longueur,
            langue=self.langue,
            style=self.style,
        )

        if objet.exec() == QDialog.DialogCode.Accepted:
            if objet.ajouter:
                clef, voyage = objet.resultat
                self.ajouter_voyage(voyage=voyage, clef=clef)
            else:
                clef = objet.clef
                if clef in self.voyages:
                    del self.voyages[clef]

            self.dict_modif.emit(self.voyages)

        self.afficher_voyages(vbox=self.liste_voyage_layout)

    def _creer_scroll(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Layout interne propre pour le scroll
        container = QWidget()
        container_layout = QVBoxLayout(container)
        scroll.setWidget(container)

        # On garde une référence vers container si besoin pour ajouter dynamiquement
        scroll.container_layout = container_layout
        scroll.container_widget = container

        return scroll

    def afficher_voyages(self, vbox):
        """Affiche self.voyages dans un QTreeWidget avec un affichage simplifié."""

        def ajouter_voyage_elements(parent_item, data, niveau=1):
            """Ajoute récursivement les éléments de self.voyages à l'arbre."""
            if isinstance(data, dict):
                for cle, valeur in data.items():

                    if cle in ["nom"]:
                        pass
                    elif cle in ["date_debut", "date_fin"]:
                        if valeur:
                            child = QTreeWidgetItem(
                                parent_item,
                                [
                                    f"{self.fonction_traduire(f'voyage_{cle}')} : "
                                    f"{datetime.strptime(str(valeur), '%Y-%m-%d').strftime('%d/%m/%Y')}"
                                ],
                            )
                            child.setBackground(
                                0,
                                QtGui.QBrush(
                                    QtGui.QColor(self.couleurs.get(niveau, "#FFFFFF"))
                                ),
                            )
                    # Pour "region" et "dep", garder le comportement complexe
                    elif cle in ["region", "dep"]:
                        if valeur:
                            child = QTreeWidgetItem(
                                parent_item,
                                [
                                    self.constantes.parametres_traduits.get(
                                        "granularite", {}
                                    )
                                    .get(self.langue, {})
                                    .get(
                                        "Départements"
                                        if str(cle) == "dep"
                                        else "Régions"
                                    )
                                ],
                            )
                            child.setBackground(
                                0,
                                QtGui.QBrush(
                                    QtGui.QColor(self.couleurs.get(niveau, "#FFFFFF"))
                                ),
                            )
                            ajouter_voyage_elements(child, valeur, niveau + 1)
                    else:
                        # Pour les autres clés (si jamais il y en a)
                        child = QTreeWidgetItem(parent_item, [str(cle)])
                        child.setBackground(
                            0,
                            QtGui.QBrush(
                                QtGui.QColor(self.couleurs.get(niveau, "#FFFFFF"))
                            ),
                        )
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

        # Création de l'arbre
        if self.voyages:
            tree = QTreeWidget()
            tree.setHeaderHidden(True)
            tree.setColumnCount(1)
            tree.setIndentation(20)
            tree.setExpandsOnDoubleClick(True)

            # Connecte le signal de double-clic
            tree.itemDoubleClicked.connect(self.voyage_double_clique)

            clefs_temp = trier_voyages(
                dictionnaire=self.voyages,
                tri=self.dict_correspondances_tri.get(self.options_tri.currentText()),
            )

            # Remplit l'arbre avec les données
            for voyage_ident in clefs_temp:

                voyage_temp = self.voyages.get(voyage_ident, {})
                # Crée un item pour chaque voyage (ex: "Voyage 1")
                voyage_item = QTreeWidgetItem(
                    tree.invisibleRootItem(),
                    [voyage_temp.get("nom") or voyage_ident],
                )
                voyage_item.setBackground(
                    0, QtGui.QBrush(QtGui.QColor(self.couleurs.get(1, "#FFFFFF")))
                )
                voyage_item.setData(0, Qt.ItemDataRole.UserRole, voyage_ident)
                ajouter_voyage_elements(voyage_item, voyage_temp, niveau=2)

            # Affiche tout replié
            tree.collapseAll()

            vbox.addWidget(tree)

    def voyage_double_clique(self, item, column):
        """Gère le double-clic sur un voyage."""
        # Récupère la clé du voyage stockée dans UserRole
        voyage_identifiant = item.data(column, Qt.ItemDataRole.UserRole)
        if voyage_identifiant:
            # Appelle creer_voyage_ui avec la clé du voyage
            self.creer_voyage_ui(voyage_identifiant)
