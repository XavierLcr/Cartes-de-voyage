################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Résumé des destinations visitées                                  #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QGroupBox,
)

from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_widget,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    creer_QLabel_centre,
    vider_layout,
)
from _0_Utilitaires._0_7_fonctions_voyages import creer_liste_destinations

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


class ArbreDestinations(QGroupBox):
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
        self.liste_pays = constantes.hierarchie_par_pays
        self.dicts_granu = {"region": {}, "dep": {}}
        self.langue_utilisee = "français"

        # Layout des pays visités
        self.layout_resume_pays = QHBoxLayout()

        # Layout final (directement sur self, qui EST le groupbox)
        layout = QVBoxLayout(self)
        layout.addLayout(self.layout_resume_pays)

    def set_dicts_granu(self, dict_nv: dict):
        """Permet de mettre à jour les sélections de destinations."""
        self.dicts_granu = dict_nv
        self.maj_layout_resume()

    def set_langue(self, nouvelle_langue):
        """Permet de mettre à jour la langue."""
        self.langue_utilisee = nouvelle_langue
        self.setTitle(self.traduire_depuis_id("titre_onglet_3"))
        self.maj_layout_resume()

    def set_style(self, style, teinte, nuances):

        self.couleurs = {
            1: renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#EDE5FF",
                sombre="#1221C1",
            ),
            2: renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#DCF5FF",
                sombre="#7E0E5C",
            ),
        }

        self.maj_layout_resume()

    def ajouter_partie_a_layout(self, vbox, pays_donnees):
        """Affiche les données hiérarchiques (pays_donnees) dans un QTreeWidget.

        Args:
            granu (str): Nom de la granularité (ex: 'régions', 'départements', etc.)
            pays_donnees (dict): Dictionnaire hiérarchique {pays: {région: [lieux], ...}}
            vbox (QVBoxLayout): Layout dans lequel insérer le widget.
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

            vbox.addWidget(tree)
        else:
            vbox.addWidget(creer_QLabel_centre(text="⏳🚝"))
            vbox.addStretch()

        # Renvoi
        return vbox

    def maj_layout_resume(self):

        vider_layout(self.layout_resume_pays)

        liste_temp = creer_liste_destinations(
            dict_regions=self.dicts_granu.get("region", {}),
            dict_dep=self.dicts_granu.get("dep", {}),
        )

        dict_temp = (liste_temp[0] or {}) | filtrer_hierarchie(
            dico_plat=(liste_temp[1] or {}),
            dico_hier=self.liste_pays,
        )

        if dict_temp:
            self.ajouter_partie_a_layout(
                vbox=self.layout_resume_pays,
                pays_donnees=dict_temp,
            )
