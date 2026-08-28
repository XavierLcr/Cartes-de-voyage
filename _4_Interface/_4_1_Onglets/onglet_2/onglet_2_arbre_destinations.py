################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Résumé des destinations visitées                                  #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem

from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_widget,
)
from _0_Utilitaires._0_07_fonctions_voyages import creer_liste_destinations

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


class ArbreDestinations(QTreeWidget):
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
        self.couleurs = {}

        # Configuration de l'arbre
        self.setHeaderHidden(True)
        self.setAlternatingRowColors(False)
        self.setColumnCount(1)
        self.setIndentation(20)
        self.setExpandsOnDoubleClick(True)
        self.setAnimated(True)

    def set_dicts_granu(self, dict_nv: dict):
        """Met à jour les destinations sélectionnées."""
        self.dicts_granu = dict_nv
        self.maj_layout_resume()

    def set_langue(self, nouvelle_langue):
        """Met à jour la langue."""
        self.langue_utilisee = nouvelle_langue

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

    def remplir_arbre(self, pays_donnees):
        """Construit l'arbre des destinations."""

        self.clear()

        def ajouter_elements(parent_item, data, niveau=1):
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
                    nom = str(cle)

                    if niveau == 1:
                        nom = self.noms_pays.get(cle, {}).get(self.langue_utilisee, nom)

                    if cle in self.emojis_pays:
                        nom += f" {self.emojis_pays[cle]}"

                    child = QTreeWidgetItem(parent_item, [nom])

                    child.setBackground(
                        0,
                        QtGui.QBrush(
                            QtGui.QColor(self.couleurs.get(niveau, "#FFFFFF"))
                        ),
                    )

                    ajouter_elements(child, valeur, niveau + 1)

            elif isinstance(data, list):
                for item in data:
                    nom = f"• {item}"

                    if item in self.emojis_pays:
                        nom += f" {self.emojis_pays[item]}"

                    child = QTreeWidgetItem(parent_item, [nom])
                    child.setBackground(
                        0,
                        QtGui.QBrush(QtGui.QColor(QtCore.Qt.GlobalColor.transparent)),
                    )

            else:
                child = QTreeWidgetItem(parent_item, [str(data)])
                child.setBackground(
                    0,
                    QtGui.QBrush(QtGui.QColor(QtCore.Qt.GlobalColor.transparent)),
                )

        if pays_donnees:
            ajouter_elements(self.invisibleRootItem(), pays_donnees)

    def maj_layout_resume(self):
        liste_temp = creer_liste_destinations(
            dict_regions=self.dicts_granu.get("region", {}),
            dict_dep=self.dicts_granu.get("dep", {}),
        )

        dict_temp = (liste_temp[0] or {}) | filtrer_hierarchie(
            dico_plat=(liste_temp[1] or {}),
            dico_hier=self.liste_pays,
        )

        self.remplir_arbre(dict_temp)
