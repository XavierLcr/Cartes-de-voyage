################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Sélection des destinations                                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import re


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

from _4_Interface._4_1_Onglets.onglet_2.onglet_2_date import SelecteurMoisAnnee

from _0_Utilitaires._0_1_fonctions_utiles_gen import obtenir_clef_par_valeur
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import reset_combo
from _4_Interface._4_2_Style._4_2_2_styles_complementaires import (
    style_bouton_de_suppression,
)


# 1 -- Fonctions utiles --------------------------------------------------------


## 1.1 -- Fonction de renvoi de l'identifiant formaté du voyage ----------------


def identifiant_voyage(n: int, longueur: int):

    return f"voyage_{n:0{longueur}d}"


# 2 -- Pop-up d'ajout d'un voyage ----------------------------------------------


class CreerVoyage(QDialog):

    def __init__(
        self,
        visites: dict,
        clef: str | None,
        constantes,
        fct_traduction,
        parent=None,
        style: int = 1,
    ):
        super().__init__(parent)

        self.constantes = constantes
        self.clef = clef
        self.visites = visites
        self.langue = "français"
        self.fct_traduction = fct_traduction
        self.resultat = None
        self.id_longueur = 10

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
        self.debut_voyage = SelecteurMoisAnnee(parent=self)

        # Fin du voyage
        self.fin_voyage_label = QLabel()
        self.fin_voyage = SelecteurMoisAnnee(parent=self)

        # Ne pas utiliser de dates
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

        # Menus déroulants
        self.liste_des_pays = QComboBox()
        self.liste_des_pays.addItems(self.constantes.hierarchie_par_pays.keys())
        self.liste_des_pays.currentIndexChanged.connect(self.maj_liste_reg_dep_pays)
        self.liste_niveaux = QComboBox()
        self.liste_niveaux.currentIndexChanged.connect(self.maj_liste_reg_dep_pays)

        layout_selection_params = QHBoxLayout()
        layout_selection_params.addWidget(self.liste_des_pays)
        layout_selection_params.addWidget(self.liste_niveaux)
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
        self.utiliser_date.setText(self.fct_traduction("general_voyage_utiliser_date"))
        self.liste_des_pays.setToolTip(
            self.fct_traduction("precision_diplomatique_onglet_2", suffixe=".")
        )

        reset_combo(
            self.liste_niveaux,
            [
                self.constantes.parametres_traduits["granularite"][self.langue][k]
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

    def voyage_id(self, longueur: int):

        if self.clef is not None:
            return self.clef
        else:
            clefs_actu = sorted(list(self.visites.keys()))

            if len(clefs_actu) == 0:
                return identifiant_voyage(n=1, longueur=longueur)
            else:

                return identifiant_voyage(
                    n=int(re.search(r"\d+$", clefs_actu[-1]).group()) + 1,
                    longueur=longueur,
                )

    def get_voyage(self):

        clef = self.voyage_id(longueur=self.id_longueur)

        if self.utiliser_date.isChecked():
            date_debut = self.debut_voyage.obtenir_premier_jour_mois()
            date_fin = max(date_debut, self.fin_voyage.obtenir_premier_jour_mois())
        else:
            date_debut = None
            date_fin = None

        voyage = {
            "nom": self.nom_voyage.text(),
            "date_debut": date_debut,
            "date_fin": date_fin,
            "region": self.dicts_granu.get("region", {}),
            "dep": self.dicts_granu.get("dep", {}),
        }

        if not voyage.get("nom"):
            nom_temp = list((voyage.get("region", {})).keys()) + list(
                (voyage.get("dep", {})).keys()
            )
            nom_temp = list(set(nom_temp))

            voyage["nom"] = ", ".join(
                [
                    self.constantes.pays_differentes_langues.get(pays, {}).get(
                        self.langue, pays
                    )
                    for pays in nom_temp
                ]
            )

        return (clef, voyage)

    def valider(self):
        self.ajouter = True
        self.resultat = self.get_voyage()
        self.accept()

    def supprimer_voyage(self):
        self.ajouter = False
        self.accept()
