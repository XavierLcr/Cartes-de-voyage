################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Sélection des destinations                                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QLineEdit, QWidget
from PyQt6.QtCore import Qt

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import creer_scroll
from _4_Interface._4_2_Style._4_2_2_styles_complementaires import (
    style_qscroll_compagnons,
)

# 1 -- Liste des compagnons de voyage ------------------------------------------


class SaisieTags(QWidget):
    def __init__(self, fct_traduction, tags_initiaux=None):
        """Initialise le widget de saisie de tags.
        Args:
            tags_initiaux: Liste de chaînes à importer au démarrage (ex: ["Alice", "Bob"]).
        """
        super().__init__()
        self.fct_traduction = fct_traduction

        # --- Layout principal ---
        layout = QHBoxLayout(self)
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
        scroll_temp = creer_scroll(self.conteneur_tags)
        scroll_temp.setStyleSheet(style_qscroll_compagnons())
        layout.addWidget(scroll_temp)

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
