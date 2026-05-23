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
    QCheckBox,
)
from PyQt6.QtCore import Qt, QSize

from _4_Interface._4_1_Onglets.onglet_2.onglet_2_date import SelecteurDate

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    obtenir_clef_par_valeur,
    construire_dictionnaire_imbrique,
    tronquer_dict,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import reset_combo
from _0_Utilitaires._0_7_fonctions_voyages import creer_voyage, voyage_id
from _4_Interface._4_2_Style._4_2_2_styles_complementaires import (
    style_bouton_de_suppression,
)

# 1 -- Fonctions utiles --------------------------------------------------------


## 1.1 -- Fonction de filtrage de la table -------------------------------------


def filtrer_df(df: pd.DataFrame, pays: str, pattern: str | None):

    # Filtre sur le pays
    df_temp = df.copy()[df["name_0"] == pays]

    # Filtre sur la valeur (si souhaité)
    if pattern:

        # masque initial à False
        mask_global = False

        for i in range(1, 6):

            mask = df_temp[f"name_{i}"].str.contains(
                pat=pattern, case=False, regex=False, na=False
            )

            # OU logique
            mask_global |= mask

        df_temp = df_temp[mask_global]

    return df_temp


## 1.2 -- Fonction de création du dictionnaire de destinations -----------------


def creer_dictionnaire(
    df: pd.DataFrame, pays: str, pattern: str | None, niveau_tronc: int
):

    return tronquer_dict(
        d=construire_dictionnaire_imbrique(
            df=filtrer_df(df=df, pays=pays, pattern=pattern).drop(columns=["name_0"]),
            niveaux=[f"name_{i}" for i in range(1, 5)],
            colonne_valeur="name_5",
        ),
        n=niveau_tronc,
    )


# 2 -- Pop-up d'ajout d'un voyage ----------------------------------------------


class CreerVoyage(QDialog):

    def __init__(
        self,
        visites: dict,
        clef: str | None,
        constantes,
        fct_traduction,
        fct_popup,
        parent=None,
        style: int = 1,
        longueur: int = 10,
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
        self.langue = "français"
        self.fct_traduction = fct_traduction
        self.fct_popup = fct_popup
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
        self.utiliser_date = QCheckBox()
        self.utiliser_date.setChecked(True)

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
        layout.addLayout(layout_selection_params)

        # Liste des lieux
        self.liste_endroits = QListWidget()
        self.liste_endroits.setWrapping(True)
        self.liste_endroits.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.liste_endroits.setGridSize(QSize(220, 27))
        self.liste_endroits.itemChanged.connect(self.changer_item_liste_pays)

        layout_selection_lieux.addLayout(layout_selection_params)
        layout_selection_lieux.addWidget(self.liste_endroits)
        self.groupe_selection_lieux.setLayout(layout_selection_lieux)
        layout.addWidget(self.groupe_selection_lieux)

        # Bouton de validation
        bouton_valider = QPushButton(self.fct_traduction("valider", suffixe=""))
        bouton_valider.clicked.connect(self.valider)
        layout.addWidget(bouton_valider)

        # Bouton de suppression
        self.bouton_supprimer = QPushButton(
            self.fct_traduction("supprimer", suffixe="")
        )
        self.bouton_supprimer.clicked.connect(self.supprimer_voyage)
        self.bouton_supprimer.setStyleSheet(
            style_bouton_de_suppression(sombre=style > 1)
        )
        if clef is None:
            self.bouton_supprimer.hide()
        layout.addWidget(self.bouton_supprimer)

        self.setLayout(layout)

        self.set_langue(langue=None)
        self.maj_liste_reg_dep_pays()

    def set_langue(self, langue: str | None):

        # Màj langue
        if langue is not None:
            self.langue = langue

        # Groupbox des infos générales
        self.general_groupbox.setTitle(self.fct_traduction("general_voyage_groupbox"))
        self.nom_voyage.setPlaceholderText(self.fct_traduction("general_voyage_nom"))
        self.debut_voyage_label.setText(
            self.fct_traduction("general_voyage_debut", suffixe=" :")
        )
        self.fin_voyage_label.setText(
            self.fct_traduction("general_voyage_fin", suffixe=" :")
        )
        self.groupe_selection_lieux.setTitle(
            self.fct_traduction("titre_choix_destinations_visitees")
        )
        self.filtre_pattern.setPlaceholderText(
            self.fct_traduction("onglet_2_filtre_pattern", suffixe="...")
        )

        self.utiliser_date.setText(self.fct_traduction("general_voyage_utiliser_date"))
        self.liste_des_pays.setToolTip(
            self.fct_traduction("precision_diplomatique_onglet_2", suffixe=".")
        )

        reset_combo(
            self.liste_niveaux,
            [
                self.granularite_traductions[self.langue][k]
                for k in ["Régions", "Départements"]
            ],
        )

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

        self.liste_endroits.blockSignals(True)
        self.liste_endroits.clear()

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

            # liste plate de régions cochables
            for region in data:

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
                    dep_item = QListWidgetItem(dep)
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
            self.fct_popup(
                titre=self.fct_traduction("pop_up_probleme_titre"),
                contenu=self.fct_traduction("pop_up_aucun_lieu_coche_2", suffixe=" !"),
                temps_max=10000,
            )

    def supprimer_voyage(self):
        self.ajouter = False
        self.accept()

    def supprimer_filtre_pattern(self):
        self.filtre_pattern.setText("")
