################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Sélection des destinations                                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import yaml

# PyQt6
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QFileDialog,
    QSizePolicy,
    QDialog,
    QComboBox,
    QToolBar,
)

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    exporter_fichier,
    formater_temps_actuel,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    set_emoji_sauvegarde,
    reset_combo,
)
from _0_Utilitaires._0_7_fonctions_voyages import (
    detecter_type_yaml,
    voyage_id,
    creer_voyage,
    trier_voyages,
)
from _0_Utilitaires._0_11_classes_pop_up import PopupInfo
from _4_Interface._4_1_Onglets.onglet_2.onglet_2_ajout_voyage import CreerVoyage
from _4_Interface._4_1_Onglets.onglet_2.onglet_2_arbre_voyages import ArbreVoyages
from _4_Interface._4_1_Onglets.onglet_2.onglet_2_arbre_destinations import (
    ArbreDestinations,
)

# 1 -- Ajustements du style des QGroupBox --------------------------------------


def style_QGroupBox_ajustements():

    return """QGroupBox {
                padding: 5px 4px 4px 4px;
            }"""


# 2 -- Classe de sélection des destinations ------------------------------------


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
        self.ajouter_voyage_bouton = QAction("Ajouter voyages", self)
        self.ajouter_voyage_bouton.triggered.connect(
            lambda x: self.creer_voyage_ui(clef=None)
        )

        # Liste des options de tri
        self.options_tri = QComboBox()
        self.options_tri.currentTextChanged.connect(lambda x: self.afficher_voyages())

        # Bouton d'export des YAML
        self.telecharger_lieux_visites = QAction("Exporter", self)
        self.telecharger_lieux_visites.triggered.connect(self.exporter_yamls_visites)

        # Bouton d'import d'un YAML
        self.chargement_yaml_bouton = QAction("Importer", self)
        self.chargement_yaml_bouton.triggered.connect(self.charger_yaml)

        # Bouton de sauvegarde
        self.bouton_sauvegarde = QAction("Sauvegarder", self)
        self.bouton_sauvegarde.triggered.connect(
            lambda: fct_sauvegarde(date_publication=False)
        )
        self.bouton_sauvegarde.triggered.connect(
            lambda: set_emoji_sauvegarde(self.bouton_sauvegarde, 3000)
        )

        # Bouton de dépliage
        self.deplier = QAction("Déplier", self)
        self.deplier.triggered.connect(lambda: self.replier_deplier_arbres(False))
        self.replier = QAction("Replier", self)
        self.replier.triggered.connect(lambda: self.replier_deplier_arbres(True))

        # Barre d'outils
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar_temp = QToolBar()
        toolbar_temp.setMovable(False)  # On ne peut pas la déplacer
        toolbar_temp.setFloatable(False)
        toolbar_temp.addAction(self.ajouter_voyage_bouton)
        toolbar_temp.addAction(self.bouton_sauvegarde)
        toolbar_temp.addAction(self.telecharger_lieux_visites)
        toolbar_temp.addAction(self.chargement_yaml_bouton)
        toolbar_temp.addWidget(spacer)
        toolbar_temp.addWidget(self.options_tri)
        toolbar_temp.addAction(self.deplier)
        toolbar_temp.addAction(self.replier)

        # Voyages effectués
        self.liste_voyage_groupbox = QGroupBox()
        self.liste_voyage_groupbox.setStyleSheet(style_QGroupBox_ajustements())
        liste_voyage_layout = QVBoxLayout(self.liste_voyage_groupbox)
        self.liste_voyage_groupbox.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )

        self.arbre_voyages = ArbreVoyages(
            constantes=self.constantes,
            fonction_traduire=self.fonction_traduire,
            parent=self,
        )
        self.arbre_voyages.voyage_double_clique.connect(self.creer_voyage_ui)
        liste_voyage_layout.addWidget(self.arbre_voyages)

        # Destinations visitées
        self.liste_destinations_groupbox = QGroupBox()
        self.liste_destinations_groupbox.setStyleSheet(style_QGroupBox_ajustements())
        layout_liste_destinations = QHBoxLayout(self.liste_destinations_groupbox)
        self.arbre_destinations = ArbreDestinations(
            traduire_depuis_id=self.fonction_traduire,
            constantes=constantes,
            parent=self,
        )
        layout_liste_destinations.addWidget(self.arbre_destinations)

        # Layout des voyages et destinations
        layout_temp = QHBoxLayout()
        layout_temp.addWidget(self.liste_voyage_groupbox, stretch=1)
        layout_temp.addWidget(self.liste_destinations_groupbox, stretch=1)

        # Layout complet
        layout.addWidget(toolbar_temp)
        layout.addLayout(layout_temp)

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
        self.afficher_voyages()

    def set_langue(self, langue):

        # Mise à jour de la langue
        if langue is not None:
            self.langue = langue

        # Mise à jour de l'interface
        self.liste_voyage_groupbox.setTitle(
            self.fonction_traduire("titre_liste_voyages")
        )
        self.liste_destinations_groupbox.setTitle(
            self.fonction_traduire("titre_liste_destinations")
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

        # Dépliage et repliage des arbres
        self.deplier.setText("📖​")
        self.replier.setText("📘​")

        # Arbre des voyages
        self.arbre_voyages.set_langue(self.langue)
        self.afficher_voyages()

        # Arbre de destinations
        self.arbre_destinations.set_langue(nouvelle_langue=self.langue)

    def set_style(self, style, teinte, nuances):

        self.style = style
        self.teinte = teinte
        self.nuances = nuances

        # Arbre des voyages
        self.arbre_voyages.set_style(style=style, teinte=teinte, nuances=nuances)
        self.afficher_voyages()

        # Arbre de destinations
        self.arbre_destinations.set_style(style=style, teinte=teinte, nuances=nuances)

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

        self.afficher_voyages()

    def afficher_voyages(self):
        """Met à jour l'arbre avec le contenu de self.voyages."""

        clefs_temp = trier_voyages(
            dictionnaire=self.voyages,
            tri=self.dict_correspondances_tri.get(self.options_tri.currentText()),
        )

        self.arbre_voyages.peupler(voyages=self.voyages, ordre_clefs=clefs_temp)
        self.arbre_voyages.setVisible(bool(self.voyages))

    def voyage_double_clique(self, item, column):
        """Gère le double-clic sur un voyage."""
        # Récupère la clé du voyage stockée dans UserRole
        voyage_identifiant = item.data(column, Qt.ItemDataRole.UserRole)
        if voyage_identifiant:
            # Appelle creer_voyage_ui avec la clé du voyage
            self.creer_voyage_ui(voyage_identifiant)

    def replier_deplier_arbre(self, arbre, replier: bool):
        arbre.collapseAll() if replier else arbre.expandAll()

    def replier_deplier_arbres(self, replier: bool):

        self.replier_deplier_arbre(arbre=self.arbre_voyages, replier=replier)
