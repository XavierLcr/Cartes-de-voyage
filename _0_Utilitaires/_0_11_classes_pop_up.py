################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# _0_11_classes_pop_up                                                         #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer, Qt

# 1 -- Pop-up infromatif -------------------------------------------------------


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
