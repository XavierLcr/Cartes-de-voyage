################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Arbre d'affichage des voyages                                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6 import QtGui
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem

# 1 -- Classe de création de l'arbre des voyages -------------------------------


class ArbreVoyages(QTreeWidget):
    """QTreeWidget spécialisé pour afficher la liste des voyages effectués."""

    # Émis avec l'identifiant du voyage lors d'un double-clic
    voyage_double_clique = pyqtSignal(str)

    def __init__(self, constantes, fonction_traduire, parent=None):
        super().__init__(parent)

        self.constantes = constantes
        self.fonction_traduire = fonction_traduire
        self.langue = "français"
        self.couleurs = {}

        # Configuration de l'arbre
        self.setHeaderHidden(True)
        self.setColumnCount(1)
        self.setIndentation(20)
        self.setExpandsOnDoubleClick(True)
        self.setAlternatingRowColors(False)
        self.setAnimated(True)

        self.itemDoubleClicked.connect(self._on_double_clique)

    # -- Configuration -------------------------------------------------

    def set_langue(self, langue):
        self.langue = langue

    def set_couleurs(self, couleurs: dict):
        self.couleurs = couleurs

    # -- Interactions ----------------------------------------------------

    def _on_double_clique(self, item, column):
        voyage_identifiant = item.data(column, Qt.ItemDataRole.UserRole)
        if voyage_identifiant:
            self.voyage_double_clique.emit(voyage_identifiant)

    # -- Remplissage de l'arbre -------------------------------------------

    def peupler(self, voyages: dict, ordre_clefs: list):
        """Vide puis reconstruit l'arbre à partir de `voyages`, dans l'ordre donné."""

        self.clear()

        for voyage_ident in ordre_clefs:

            voyage_temp = voyages.get(voyage_ident, {})

            voyage_item = QTreeWidgetItem(
                self.invisibleRootItem(),
                [voyage_temp.get("nom") or voyage_ident],
            )
            voyage_item.setBackground(
                0, QtGui.QBrush(QtGui.QColor(self.couleurs.get(1, "#FFFFFF")))
            )
            voyage_item.setData(0, Qt.ItemDataRole.UserRole, voyage_ident)

            self._ajouter_elements(voyage_item, voyage_temp, niveau=2)

        self.collapseAll()

    def _ajouter_elements(self, parent_item, data, niveau=1):
        """Ajoute récursivement les éléments d'un voyage à l'arbre."""

        if isinstance(data, dict):
            for cle, valeur in data.items():

                if cle in ["nom"]:
                    continue

                elif cle in ["date_debut", "date_fin"]:
                    if valeur:
                        child = QTreeWidgetItem(
                            parent_item,
                            [
                                f"{self.fonction_traduire(f'voyage_{cle}')} : "
                                f"{datetime.strptime(str(valeur), '%Y-%m-%d').strftime('%d/%m/%Y')}"
                            ],
                        )
                        child.setBackground(
                            0,
                            QtGui.QBrush(
                                QtGui.QColor(self.couleurs.get(niveau, "#FFFFFF"))
                            ),
                        )

                elif cle in ["region", "dep"]:
                    if valeur:
                        child = QTreeWidgetItem(
                            parent_item,
                            [
                                self.constantes.parametres_traduits.get(
                                    "granularite", {}
                                )
                                .get(self.langue, {})
                                .get("Départements" if str(cle) == "dep" else "Régions")
                            ],
                        )
                        child.setBackground(
                            0,
                            QtGui.QBrush(
                                QtGui.QColor(self.couleurs.get(niveau, "#FFFFFF"))
                            ),
                        )
                        self._ajouter_elements(child, valeur, niveau + 1)

                else:
                    child = QTreeWidgetItem(parent_item, [str(cle)])
                    child.setBackground(
                        0,
                        QtGui.QBrush(
                            QtGui.QColor(self.couleurs.get(niveau, "#FFFFFF"))
                        ),
                    )
                    self._ajouter_elements(child, valeur, niveau + 1)

        elif isinstance(data, list):
            for item in data:
                child = QTreeWidgetItem(parent_item, [f"• {str(item)}"])
                child.setBackground(
                    0, QtGui.QBrush(QtGui.QColor(Qt.GlobalColor.transparent))
                )

        else:
            child = QTreeWidgetItem(parent_item, [str(data)])
            child.setBackground(
                0, QtGui.QBrush(QtGui.QColor(Qt.GlobalColor.transparent))
            )
