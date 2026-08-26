################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Sélection des destinations                                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import pandas as pd

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QComboBox,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QWidget,
)
from PyQt6.QtCore import Qt, QSize

from _0_Utilitaires._0_10_selecteur_date import SelecteurDate
from _0_Utilitaires._0_12_toggle_checkbox import ToggleSwitch

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    obtenir_clef_par_valeur,
    construire_dictionnaire_imbrique,
    tronquer_dict,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import reset_combo
from _0_Utilitaires._0_7_fonctions_voyages import creer_voyage, voyage_id
from _0_Utilitaires._0_11_classes_pop_up import PopupInfo
from _4_Interface._4_2_Style._4_2_2_styles_complementaires import (
    style_bouton_de_suppression,
)

# 1 -- Fonctions utiles --------------------------------------------------------


## 1.1 -- Fonction de filtrage de la table -------------------------------------


def filtrer_df(df: pd.DataFrame, pays: str, pattern: str | None):

    # Filtre sur le pays
    df_temp = df[df["name_0"] == pays].copy().drop(columns=["name_0"])

    # Filtre sur la valeur (si souhaité)
    if pattern:

        mask = (
            # Sélection des colonnes
            df_temp[[f"name_{i}" for i in range(1, 6)]].fillna("")
            # Agrégation des colonnes
            .agg(" ".join, axis=1)
            # Détection
            .str.contains(pattern, case=False, regex=False)
        )

        # Filtre
        df_temp = df_temp[mask]

    # Renvoi
    return df_temp.copy()


## 1.2 -- Fonction de création du dictionnaire de destinations -----------------


def creer_dictionnaire(
    df: pd.DataFrame, pays: str, pattern: str | None, niveau_tronc: int
):

    return tronquer_dict(
        d=construire_dictionnaire_imbrique(
            df=filtrer_df(df=df, pays=pays, pattern=pattern)[
                ["name_1", "name_2", "name_3"]
            ],
            niveaux=[f"name_{i}" for i in range(1, 3)],
            colonne_valeur="name_3",
        ),
        n=niveau_tronc,
    )


# 2 -- Liste des compagnons de voyage ------------------------------------------


class SaisieTags(QWidget):
    def __init__(self, fct_traduction, tags_initiaux=None):
        """Initialise le widget de saisie de tags.
        Args:
            tags_initiaux: Liste de chaînes à importer au démarrage (ex: ["Alice", "Bob"]).
        """
        super().__init__()
        self.fct_traduction = fct_traduction

        # --- Layout principal ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Champ de saisie
        self.champ_saisie = QLineEdit()
        self.champ_saisie.setPlaceholderText("Ajouter un voyageur...")
        self.champ_saisie.returnPressed.connect(self.ajouter_tag)
        layout.addWidget(self.champ_saisie)

        # Conteneur pour les tags (horizontal)
        self.conteneur_tags = QHBoxLayout()
        self.conteneur_tags.setSpacing(6)
        self.conteneur_tags.setContentsMargins(0, 4, 0, 0)
        self.conteneur_tags.addStretch()  # pousse les tags à gauche
        layout.addLayout(self.conteneur_tags)

        # Import des tags initiaux (si fournis)
        if tags_initiaux:
            for tag in tags_initiaux:
                self.ajouter_tag_manuel(tag)

    def ajouter_tag_manuel(self, texte):
        """Ajoute un tag sans vider le champ de saisie (pour l'import initial)."""
        texte = texte.strip()
        if not texte:
            return

        # --- Widget "pilule" englobant le tag ---
        tag_widget = QWidget()
        tag_widget.setStyleSheet("""
            QWidget {
                background-color: #e8e8e8;
                border-radius: 10px;
            }
            """)

        tag_layout = QHBoxLayout(tag_widget)
        tag_layout.setContentsMargins(8, 2, 4, 2)
        tag_layout.setSpacing(4)

        # Label du nom
        label = QLabel(texte)
        label.setStyleSheet("background: transparent; border: none;")
        tag_layout.addWidget(label)

        # Bouton de suppression (plat, collé au texte)
        btn_supprimer = QPushButton("✕")
        btn_supprimer.setFlat(True)
        btn_supprimer.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_supprimer.setFixedSize(16, 16)
        btn_supprimer.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: #555;
                font-weight: bold;
                padding: 1px 1px;
            }
            QPushButton:hover {
                color: #c0392b;
            }
            """)
        btn_supprimer.clicked.connect(lambda: self.supprimer_tag(tag_widget))
        tag_layout.addWidget(btn_supprimer)

        # Insère le tag juste avant le stretch final
        self.conteneur_tags.insertWidget(self.conteneur_tags.count() - 1, tag_widget)

    def ajouter_tag(self):
        """Ajoute un tag depuis le champ de saisie."""
        texte = self.champ_saisie.text().strip()
        if texte:
            self.ajouter_tag_manuel(texte)
            self.champ_saisie.clear()  # Vide le champ après ajout

    def supprimer_tag(self, tag_widget):
        """Supprime un tag du conteneur."""
        self.conteneur_tags.removeWidget(tag_widget)
        tag_widget.deleteLater()

    def obtenir_liste(self):
        """Renvoie la liste des valeurs saisies (ex: ["Alice", "Bob", "Charlie"])."""

        # Ajout du nom saisi actuel
        self.ajouter_tag()

        valeurs = []
        for i in range(self.conteneur_tags.count()):
            item = self.conteneur_tags.itemAt(i)
            widget = item.widget()
            if widget:  # ignore le stretch (qui n'a pas de widget)
                label = widget.findChild(QLabel)
                if label:
                    valeurs.append(label.text())
        return valeurs

    def set_langue(self):

        self.champ_saisie.setPlaceholderText(
            self.fct_traduction("compagnons_liste_placeholder")
        )
        self.champ_saisie.setToolTip(
            self.fct_traduction("compagnons_liste_tooltip", suffixe=".")
        )


# 3 -- Pop-up d'ajout d'un voyage ----------------------------------------------


class CreerVoyage(QDialog):

    def __init__(
        self,
        visites: dict,
        clef: str | None,
        constantes,
        fct_traduction,
        parent=None,
        style: int = 1,
        longueur: int = 10,
        langue: str = "français",
    ):
        super().__init__(parent)

        self.resize(900, 500)

        self.granularite_traductions = constantes.parametres_traduits.get(
            "granularite", {}
        )
        self.liste_pays = list(constantes.hierarchie_par_pays.keys())
        self.df_hierarchie = constantes.hierarchie_complete_par_pays
        self.granularite_max_pays = constantes.granularite_max_pays
        self.clef = clef
        self.visites = visites
        self.langue = langue
        self.fct_traduction = fct_traduction
        self.resultat = None
        self.id_longueur = longueur

        layout = QVBoxLayout(self)

        if clef is not None:
            self.visite_temp = visites.get(clef, {})
        else:
            self.visite_temp = {}

        self.dicts_granu = {
            "region": self.visite_temp.get("region", {}),
            "dep": self.visite_temp.get("dep", {}),
        }

        # Nom du voyage
        self.nom_voyage = QLineEdit()
        self.nom_voyage.setText(self.visite_temp.get("nom", ""))
        self.nom_voyage.setPlaceholderText("...")

        # Début du voyage
        self.debut_voyage_label = QLabel()
        self.debut_voyage = SelecteurDate(
            parent=self, date=self.visite_temp.get("date_debut")
        )

        # Fin du voyage
        self.fin_voyage_label = QLabel()
        self.fin_voyage = SelecteurDate(
            parent=self, date=self.visite_temp.get("date_fin")
        )

        # Utilisation des dates
        self.utiliser_date = ToggleSwitch(style=style)
        self.utiliser_date.setChecked(self.visite_temp.get("date_fin") is not None)

        # Ajout de compagnons de voyages
        self.compagnons_liste = SaisieTags(
            fct_traduction=self.fct_traduction,
            tags_initiaux=self.visite_temp.get("compagnons"),
        )

        # Layout principal du groupbox
        self.general_groupbox = QGroupBox()
        general_layout = QVBoxLayout()
        general_layout.setSpacing(12)
        general_layout.setContentsMargins(15, 15, 15, 15)

        # --- Ligne 1 : Nom du voyage ---
        ligne_nom = QHBoxLayout()
        label_nom = QLabel()
        ligne_nom.addWidget(label_nom)
        ligne_nom.addWidget(self.nom_voyage)

        # --- Ligne 2 : Dates ---
        ligne_dates = QHBoxLayout()
        ligne_dates.setSpacing(10)

        ligne_dates.addWidget(self.debut_voyage_label)
        ligne_dates.addWidget(self.debut_voyage)

        ligne_dates.addSpacing(20)  # espace entre début et fin

        ligne_dates.addWidget(self.fin_voyage_label)
        ligne_dates.addWidget(self.fin_voyage)
        ligne_dates.addWidget(self.utiliser_date)

        ligne_dates.addStretch()  # pousse tout à gauche proprement

        # Ajout au layout principal
        general_layout.addLayout(ligne_nom)
        general_layout.addLayout(ligne_dates)
        general_layout.addWidget(self.compagnons_liste)

        self.general_groupbox.setLayout(general_layout)
        layout.addWidget(self.general_groupbox)

        # Sélection des lieux de destination
        self.groupe_selection_lieux = QGroupBox()
        layout_selection_lieux = QVBoxLayout()

        # Périmètre de sélection
        self.liste_des_pays = QComboBox()
        self.liste_des_pays.addItems(self.liste_pays)
        self.liste_des_pays.currentIndexChanged.connect(self.supprimer_filtre_pattern)
        self.liste_des_pays.currentIndexChanged.connect(self.maj_liste_reg_dep_pays)
        self.liste_niveaux = QComboBox()
        self.liste_niveaux.currentIndexChanged.connect(self.supprimer_filtre_pattern)
        self.liste_niveaux.currentIndexChanged.connect(self.maj_liste_reg_dep_pays)
        self.filtre_pattern = QLineEdit()
        self.filtre_pattern.setPlaceholderText("...")
        self.filtre_pattern.textChanged.connect(self.maj_liste_reg_dep_pays)

        layout_selection_params = QHBoxLayout()
        layout_selection_params.addWidget(self.liste_des_pays, stretch=3)
        layout_selection_params.addWidget(self.liste_niveaux, stretch=3)
        layout_selection_params.addWidget(self.filtre_pattern, stretch=4)

        # Liste des lieux
        self.liste_endroits = QListWidget()
        self.liste_endroits.setWrapping(True)
        self.liste_endroits.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.liste_endroits.setGridSize(QSize(200, 25))
        self.liste_endroits.itemChanged.connect(self.changer_item_liste_pays)

        layout_selection_lieux.addLayout(layout_selection_params)
        layout_selection_lieux.addWidget(self.liste_endroits)
        self.groupe_selection_lieux.setLayout(layout_selection_lieux)
        layout.addWidget(self.groupe_selection_lieux)

        # Bouton de validation
        bouton_valider = QPushButton(self.fct_traduction("valider", suffixe=""))
        bouton_valider.setAutoDefault(False)
        bouton_valider.setDefault(False)
        bouton_valider.clicked.connect(self.valider)
        layout.addWidget(bouton_valider)

        # Bouton de suppression
        self.bouton_supprimer = QPushButton(
            self.fct_traduction("supprimer", suffixe="")
        )
        bouton_valider.setAutoDefault(False)
        bouton_valider.setDefault(False)
        self.bouton_supprimer.clicked.connect(self.supprimer_voyage)
        self.bouton_supprimer.setStyleSheet(
            style_bouton_de_suppression(sombre=style > 1)
        )
        if clef is None:
            self.bouton_supprimer.hide()
        layout.addWidget(self.bouton_supprimer)

        self.setLayout(layout)

        self.set_langue(langue=None)

        self.liste_des_pays.setCurrentIndex(
            self.liste_pays.index(
                (
                    sorted(
                        [
                            cle
                            for granu in ["region", "dep"]
                            for cle in self.visite_temp.get(granu, {}).keys()
                        ]
                    )
                    + [self.liste_pays[0]]
                )[0]
            )
        )
        self.maj_liste_reg_dep_pays()

    def set_langue(self, langue: str | None):

        # Màj langue
        if langue is not None:
            self.langue = langue

        # Groupbox des infos générales
        self.general_groupbox.setTitle(self.fct_traduction("general_voyage_groupbox"))
        self.nom_voyage.setPlaceholderText(self.fct_traduction("general_voyage_nom"))

        # Dates
        self.debut_voyage_label.setText(
            self.fct_traduction("general_voyage_debut", suffixe=" :")
        )
        self.fin_voyage_label.setText(
            self.fct_traduction("general_voyage_fin", suffixe=" :")
        )
        self.utiliser_date.setText(self.fct_traduction("general_voyage_utiliser_date"))

        # Compagnons de voyage
        self.compagnons_liste.set_langue()

        # Sélection des lieux
        self.groupe_selection_lieux.setTitle(
            self.fct_traduction("titre_choix_destinations_visitees")
        )
        reset_combo(
            self.liste_niveaux,
            [
                self.granularite_traductions[self.langue][k]
                for k in ["Régions", "Départements"]
            ],
        )
        self.filtre_pattern.setPlaceholderText(
            self.fct_traduction("onglet_2_filtre_pattern", suffixe="...")
        )
        self.liste_des_pays.setToolTip(
            self.fct_traduction("precision_diplomatique_onglet_2", suffixe=".")
        )

    def creer_item(
        self,
        texte: str,
        coche: bool | None = None,
        gras: bool = False,
        souligne: bool = False,
        selectable: bool = True,
        enabled: bool = True,
    ):
        item = QListWidgetItem(texte)

        flags = item.flags()

        if selectable:
            flags |= Qt.ItemFlag.ItemIsSelectable

        if enabled:
            flags |= Qt.ItemFlag.ItemIsEnabled

        if coche is not None:
            flags |= Qt.ItemFlag.ItemIsUserCheckable

        item.setFlags(flags)

        if coche is not None:
            item.setCheckState(
                Qt.CheckState.Checked if coche else Qt.CheckState.Unchecked
            )

        if gras or souligne:

            font = item.font()

            if font.pointSize() <= 0:
                font.setPointSize(9)

            font.setBold(gras)
            font.setUnderline(souligne)

            item.setFont(font)

        return item

    def maj_liste_reg_dep_pays(self):
        """
        Remplit self.liste_endroits (QListWidget) selon la granularité choisie.
        - Si niveau == "Régions" : on affiche une liste de régions cochables.
        - Si niveau == "Départements" : on affiche les régions (non cochables) puis
        les départements (cochables) sous chaque région.
        """

        # Récupération du pays
        pays_i = self.liste_des_pays.currentText()

        # Si le pays a moins de deux niveaux de granularité, mise automatique sur la Région
        if self.granularite_max_pays.get(pays_i, 2) < 2:
            self.liste_niveaux.blockSignals(True)
            self.liste_niveaux.setCurrentIndex(0)
            self.liste_niveaux.setEnabled(False)
            self.liste_niveaux.blockSignals(False)
        else:
            self.liste_niveaux.setEnabled(True)

        # Récupération du niveau de granularité
        niveau_i = obtenir_clef_par_valeur(
            valeur=self.liste_niveaux.currentText(),
            dictionnaire=self.granularite_traductions[self.langue],
        )

        # Liste vidée
        self.liste_endroits.blockSignals(True)
        self.liste_endroits.clear()

        # Création des données à utiliser
        data = creer_dictionnaire(
            df=self.df_hierarchie,
            pays=pays_i,
            pattern=self.filtre_pattern.text(),
            niveau_tronc=2 - (niveau_i == "Régions"),
        )

        if not data:
            self.liste_endroits.blockSignals(False)
            return

        if niveau_i == "Régions":

            # Liste plate de régions cochables
            for region in data:

                self.liste_endroits.addItem(
                    self.creer_item(
                        texte=region,
                        coche=region
                        in (self.dicts_granu.get("region", {}).get(pays_i, [])),
                        gras=False,
                        souligne=False,
                        selectable=True,
                        enabled=True,
                    )
                )

        else:

            # Afficher régions (non cochables) puis départements cochables
            for i, region in enumerate(sorted(data.keys())):

                self.liste_endroits.addItem(
                    self.creer_item(
                        texte=region,
                        coche=None,
                        gras=True,
                        souligne=True,
                        selectable=False,
                        enabled=True,
                    )
                )

                for dep in sorted(data[region]):

                    self.liste_endroits.addItem(
                        self.creer_item(
                            texte=dep,
                            coche=dep
                            in (self.dicts_granu.get("dep", {}).get(pays_i, [])),
                            gras=False,
                            souligne=False,
                            selectable=True,
                            enabled=True,
                        )
                    )

                # Ligne vide pour lisibilité
                if i < len(data.keys()) - 1:
                    spacer = QListWidgetItem()
                    spacer.setFlags(Qt.ItemFlag.NoItemFlags)
                    spacer.setSizeHint(QSize(0, 3))
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
                dictionnaire=self.granularite_traductions[self.langue],
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

    def get_voyage(self):

        # Création de l'identifiant
        clef = voyage_id(
            voyages=self.visites, clef=self.clef, longueur=self.id_longueur
        )

        # Récupération de la date si utilisée
        if self.utiliser_date.isChecked():
            date_debut = self.debut_voyage.obtenir_date_str()
            date_fin = max(date_debut, self.fin_voyage.obtenir_date_str())
        else:
            date_debut = None
            date_fin = None

        # Création du voyage
        voyage = creer_voyage(
            nom=self.nom_voyage.text(),
            date_deb=date_debut,
            date_fin=date_fin,
            compagnons=self.compagnons_liste.obtenir_liste(),
            regions=self.dicts_granu.get("region", {}),
            departements=self.dicts_granu.get("dep", {}),
            langue=self.langue,
        )

        # Renvoi
        return (clef, voyage)

    def valider(self):

        clef, voyage = self.get_voyage()
        if voyage.get("region", {}) or voyage.get("dep", {}):

            self.ajouter = True
            self.resultat = (clef, voyage)
            self.accept()

        else:

            PopupInfo(parent=self).montrer(
                titre=self.fct_traduction("pop_up_probleme_titre"),
                contenu=self.fct_traduction("pop_up_aucun_lieu_coche_2", suffixe=" !"),
                temps_max=10000,
            )

    def supprimer_voyage(self):
        self.ajouter = False
        self.accept()

    def supprimer_filtre_pattern(self):
        self.filtre_pattern.setText("")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # On bloque le traitement par défaut de QDialog (qui cliquerait sur un bouton)
            event.ignore()
            return
        super().keyPressEvent(event)
