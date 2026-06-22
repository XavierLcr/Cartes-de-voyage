################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# _0_11_classes_pop_up                                                         #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


from PyQt6.QtWidgets import QMessageBox, QLineEdit, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt

# 1 -- Pop-up informatif -------------------------------------------------------


class PopupInfo:
    def __init__(self, parent=None):
        self.parent = parent  # Widget parent (ex: self dans ta classe principale)

    def montrer(
        self,
        titre: str,
        contenu: str,
        temps_max: int | None = 5000,
        icone: QMessageBox.Icon = QMessageBox.Icon.Information,
    ) -> None:
        """
        Affiche une pop-up avec les options spécifiées.

        Args:
            titre: Titre de la pop-up.
            contenu: Contenu (texte) de la pop-up.
            temps_max: Temps en ms avant fermeture automatique (None = pas de timer).
            icone: Icône de la pop-up (Information, Question, Warning, etc.).
        """
        msg = QMessageBox(self.parent)
        msg.setWindowTitle(titre)
        msg.setText(contenu)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setIcon(icone)

        # Configuration des boutons
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)

        # Timer pour fermeture automatique
        if temps_max is not None:
            QTimer.singleShot(max(temps_max, 3000), msg.close)

        msg.exec()  # Affiche la pop-up


# 2 -- Pop-up de choix de type Oui/Non -----------------------------------------


class PopupOuiNon:

    def __init__(self, traducteur, parent=None):
        """
        Args:
            parent: Widget parent (ex: self dans ta classe principale).
            traducteur: Fonction de traduction (ex: self.traduire_depuis_id).
                       Si None, utilise les textes par défaut.
        """
        self.parent = parent
        self.traducteur = traducteur

    def montrer(
        self,
        titre: str,
        contenu: str,
    ) -> bool:
        """
        Affiche une pop-up avec boutons Oui/Non et retourne le choix de l'utilisateur.

        Args:
            titre: Titre de la pop-up.
            contenu: Contenu (texte) de la pop-up.
            icone: Icône de la pop-up (Question par défaut).

        Returns:
            True si l'utilisateur clique sur Oui, False sinon.
        """
        msg = QMessageBox(self.parent)
        msg.setWindowTitle(titre)
        msg.setText(contenu)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setIcon(QMessageBox.Icon.Question)

        # Utilise le traducteur si disponible
        bouton_oui = msg.addButton(
            self.traducteur(clef="oui"),
            QMessageBox.ButtonRole.YesRole,
        )
        bouton_non = msg.addButton(
            self.traducteur(clef="non"),
            QMessageBox.ButtonRole.NoRole,
        )

        msg.exec()  # Affiche la pop-up

        # Retourne True si le bouton Oui est cliqué
        return msg.clickedButton() == bouton_oui


# 3 -- Pop-up de saisie de texte -----------------------------------------------


class PopupSaisieTexte:

    def __init__(self, traducteur, parent=None):
        """
        Args:
            parent: Widget parent (ex: self dans ta classe principale).
            traducteur: Fonction de traduction (ex: self.traduire_depuis_id).
                       Si None, utilise les textes par défaut.
        """

        self.parent = parent
        self.traducteur = traducteur

    def montrer(
        self,
        titre: str,
        texte: str,
        placeholder: str = "",
        largeur: int = 250,
    ) -> str | None:
        """
        Affiche une pop-up avec un champ de saisie et un bouton Valider.

        Args:
            titre: Titre de la pop-up.
            texte: Texte affiché dans la pop-up.
            placeholder: Texte d'aide dans le champ de saisie.
            largeur: Largeur du champ de saisie.

        Returns:
            Le texte saisi par l'utilisateur, ou None si annulé.
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setMinimumWidth(300)
        msg_box.setWindowTitle(titre)
        msg_box.setText(texte)
        msg_box.setTextFormat(Qt.TextFormat.RichText)

        # Champ de saisie
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setFixedWidth(largeur)

        # Widget pour intégrer le champ de saisie
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(line_edit)
        widget.setLayout(layout)

        # Ajout du widget dans la QMessageBox
        msg_box.layout().addWidget(widget, 1, 0, 1, msg_box.layout().columnCount())

        # Bouton Valider
        bouton_valider = msg_box.addButton(
            self.traducteur(clef="valider"),
            QMessageBox.ButtonRole.AcceptRole,
        )

        # Affichage et récupération du résultat
        result = msg_box.exec()

        # Si l'utilisateur clique sur Valider, retourne le texte saisi
        if msg_box.clickedButton() == bouton_valider:
            return line_edit.text().strip()
        return None
