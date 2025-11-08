################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/                                                   #
# Onglet 3 – Résumé des pays visités                                           #
################################################################################


from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
)

from _0_Utilitaires._0_1_Fonctions_utiles import (
    creer_ligne_separation,
    vider_layout,
    creer_QLabel_centre,
)


# 1 -- Fonctions utiles --------------------------------------------------------


## 1.1 -- Passe d'un dictionnaire Pays/Département à Pays/Région/Département ---


def filtrer_hierarchie(dico_plat, dico_hier):
    """
    Filtre le dictionnaire hiérarchique (pays -> régions -> départements)
    selon un dictionnaire plat (pays -> liste de départements).

    Args:
        dico_plat (dict[str, list[str]]): Dictionnaire pays -> départements
        dico_hier (dict[str, dict[str, list[str]]]): Dictionnaire pays -> régions -> départements

    Returns:
        dict[str, dict[str, list[str]]]: Dictionnaire hiérarchique filtré
    """
    dico_filtre = {}
    if dico_plat is None:
        dico_plat = {}
    dico_plat = {
        clef: valeur for clef, valeur in dico_plat.items() if valeur is not None
    }

    for pays, regions in dico_hier.items():
        if pays not in dico_plat:
            continue  # garder seulement les pays communs

        deps_a_garder = set(dico_plat[pays])
        nouvelles_regions = {}

        for region, deps in regions.items():
            # Intersection entre les départements de la région et ceux à garder
            deps_communs = [dep for dep in deps if dep in deps_a_garder]
            if deps_communs:
                nouvelles_regions[region] = deps_communs

        if nouvelles_regions:
            dico_filtre[pays] = nouvelles_regions

    return dico_filtre


# 2 -- Classe de l'onglet de récapitulation des pays visités -------------------


class OngletResumeDestinations(QWidget):
    def __init__(
        self,
        traduire_depuis_id,
        constantes,
        parent=None,
    ):
        super().__init__(parent)

        self.traduire_depuis_id = traduire_depuis_id
        self.emojis_pays = constantes.emojis_pays
        self.noms_pays = constantes.pays_differentes_langues
        self.constantes = constantes
        self.dicts_granu = {"region": {}, "dep": {}}
        self.langue_utilisee = "français"
        self.couleurs = {
            1: "#EDE5FF",
            2: "#DCF5FF",
        }

        self.layout_onglet_3 = QVBoxLayout()
        self.layout_resume_pays = QHBoxLayout()
        self.layout_boutons = QHBoxLayout()

        # Layout régions
        self.layout_resume_regions = QVBoxLayout()
        self.scroll_regions = self._creer_scroll(self.layout_resume_regions)

        # Layout départements
        self.layout_resume_departements = QVBoxLayout()
        self.scroll_departements = self._creer_scroll(self.layout_resume_departements)

        # Boutons de mise en forme
        self.arbre_groupe = True
        self.deplier = QPushButton()
        self.deplier.clicked.connect(lambda: self.replier_deplier(False))
        self.replier = QPushButton()
        self.replier.clicked.connect(lambda: self.replier_deplier(True))
        self.layout_boutons.addWidget(self.deplier, stretch=1)
        self.layout_boutons.addStretch(3)
        self.layout_boutons.addWidget(self.replier, stretch=1)

        # Assembler les widgets
        self.layout_resume_pays.addWidget(self.scroll_regions)
        self.layout_resume_pays.addWidget(self.scroll_departements)

        self.layout_onglet_3.addLayout(self.layout_resume_pays)
        self.layout_onglet_3.addLayout(self.layout_boutons)

        self.setLayout(self.layout_onglet_3)

    def set_dicts_granu(self, dict_nv: dict):
        """Permet de mettre à jour les sélections de destinations."""
        self.dicts_granu = dict_nv
        self.maj_layout_resume()

    def set_langue(self, nouvelle_langue):
        """Permet de mettre à jour la langue."""
        self.langue_utilisee = nouvelle_langue
        self.deplier.setText("📖​")
        self.replier.setText("📘​")
        self.maj_layout_resume()

    def _creer_scroll(self, vbox):
        widget = QWidget()
        widget.setLayout(vbox)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        return scroll

    def ajouter_partie_a_layout(self, granu, pays_donnees, vbox, affichage_groupe=True):
        """Affiche les données hiérarchiques (pays_donnees) dans un QTreeWidget.

        Args:
            granu (str): Nom de la granularité (ex: 'régions', 'départements', etc.)
            pays_donnees (dict): Dictionnaire hiérarchique {pays: {région: [lieux], ...}}
            vbox (QVBoxLayout): Layout dans lequel insérer le widget.
            affichage_groupe (bool): Si True, affiche les items regroupés sur une seule ligne quand c'est possible.
        """

        def ajouter_elements(parent_item, data, niveau=1):
            """
            Ajoute récursivement les éléments dans l'arbre avec couleurs de fond par niveau.
            Le dernier niveau (les listes) reste transparent.
            Coloration inclut le premier niveau (top-level) maintenant.
            """

            if isinstance(data, dict):

                for cle, valeur in sorted(
                    data.items(),
                    key=lambda x: (
                        self.noms_pays.get(x[0], {}).get(
                            self.langue_utilisee, str(x[0])
                        )
                        if niveau == 1
                        else str(x[0])
                    ),
                ):
                    # créer l'item pour ce niveau

                    nom = str(cle)
                    if niveau == 1:
                        nom = self.noms_pays.get(cle, {}).get(self.langue_utilisee, nom)
                    if cle in self.emojis_pays:
                        nom += f" {self.emojis_pays[cle]}"

                    child = QTreeWidgetItem(parent_item, [nom])

                    # colorier le fond si ce n'est pas une liste (dernier niveau)
                    child.setBackground(
                        0,
                        QtGui.QBrush(
                            QtGui.QColor(self.couleurs.get(niveau, "#FFFFFF"))
                        ),
                    )

                    # récursion pour les niveaux suivants
                    ajouter_elements(child, valeur, niveau + 1)

            elif isinstance(data, list):
                # dernier niveau → transparent
                for item in data:
                    nom = f"• {str(item)}"
                    if item in self.emojis_pays:
                        nom += f" {self.emojis_pays[item]}"
                    child = QTreeWidgetItem(parent_item, [nom])
                    child.setBackground(
                        0, QtGui.QBrush(QtGui.QColor(QtCore.Qt.GlobalColor.transparent))
                    )

            else:
                # valeur simple → feuille
                child = QTreeWidgetItem(parent_item, [str(data)])
                child.setBackground(
                    0, QtGui.QBrush(QtGui.QColor(QtCore.Qt.GlobalColor.transparent))
                )

        # --- Nettoyage de la zone ---
        vider_layout(vbox)

        # --- Titre de section ---
        vbox.addWidget(
            creer_QLabel_centre(
                text=self.traduire_depuis_id(clef=granu, prefixe="<b>", suffixe="</b>")
            )
        )
        vbox.addWidget(creer_ligne_separation())
        vbox.addWidget(QLabel(""))

        # --- Création de l'arbre ---
        if pays_donnees:
            tree = QTreeWidget()
            tree.setHeaderHidden(True)
            tree.setAlternatingRowColors(False)
            tree.setColumnCount(1)
            tree.setIndentation(20)
            tree.setExpandsOnDoubleClick(True)
            tree.setAnimated(True)

            ajouter_elements(tree.invisibleRootItem(), pays_donnees, niveau=1)

            tree.collapseAll() if affichage_groupe else tree.expandAll()
            vbox.addWidget(tree)
        else:
            vbox.addWidget(creer_QLabel_centre(text="⏳🚝"))
            vbox.addStretch()

    def maj_layout_resume(self):

        self.ajouter_partie_a_layout(
            granu="titre_regions_visitees",
            pays_donnees=self.dicts_granu.get("region", {}),
            vbox=self.layout_resume_regions,
            affichage_groupe=self.arbre_groupe,
        )

        self.ajouter_partie_a_layout(
            granu="titre_departements_visites",
            pays_donnees=filtrer_hierarchie(
                dico_plat=self.dicts_granu.get("dep", {}),
                dico_hier=self.constantes.hierarchie_par_pays,
            ),
            vbox=self.layout_resume_departements,
            affichage_groupe=self.arbre_groupe,
        )

    def replier_deplier(self, replier):
        self.arbre_groupe = replier
        self.maj_layout_resume()
