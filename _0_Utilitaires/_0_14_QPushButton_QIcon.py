################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# 0.14 – QPushButton sans texte, avec seulement une icône                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import inspect
from PyQt6.QtCore import QPointF, QSize, Qt, QTimer
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QPushButton

from _4_Interface._4_3_Icones._4_3_25_disquette import _dessiner_icone_disquette
from _4_Interface._4_3_Icones._4_3_27_CD import _dessiner_icone_cd

# 1 -- Fonction générale -------------------------------------------------------


class QPushButtonIcone(QPushButton):
    """QPushButton affichant uniquement une icône, avec support optionnel
    d'une pastille de validation (verte) ajoutable/retirable dynamiquement."""

    def __init__(
        self,
        fonction_dessin,
        taille: int = 32,
        padding: int = 0,
        parent=None,
    ):
        super().__init__(parent)

        self._fonction_dessin = fonction_dessin
        self._taille = taille
        self._validee = False

        # Détecte une seule fois si la fonction de dessin accepte "validee"
        self._accepte_validee = (
            "validee" in inspect.signature(fonction_dessin).parameters
        )

        self.setIconSize(QSize(taille, taille))
        self.setFixedSize(taille, taille)

        self.setStyleSheet(f"""
            QPushButton {{
                border: none;
                padding: {padding}px;
                margin: 0px;
                background: transparent;
            }}
            QPushButton:hover {{
                background: rgba(128, 128, 128, 30);
                border-radius: 4px;
            }}
            QPushButton:pressed {{
                background: rgba(128, 128, 128, 60);
                border-radius: 4px;
            }}
        """)

        self._mettre_a_jour_icone()

    # -- Rendu interne --------------------------------------------------

    def _mettre_a_jour_icone(self) -> None:
        """Régénère le pixmap selon l'état actuel et l'applique au bouton."""
        pixmap = QPixmap(self._taille, self._taille)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        centre = QPointF(self._taille / 2, self._taille / 2)

        if self._accepte_validee:
            self._fonction_dessin(painter, centre, self._taille, validee=self._validee)
        else:
            self._fonction_dessin(painter, centre, self._taille)

        painter.end()
        self.setIcon(QIcon(pixmap))

    # -- API publique -----------------------------------------------------

    def definir_validee(self, validee: bool) -> None:
        """Active ou désactive la pastille verte de validation."""
        if validee != self._validee:
            self._validee = validee
            self._mettre_a_jour_icone()

    def basculer_validee(self) -> None:
        """Inverse l'état actuel de la pastille de validation."""
        self.definir_validee(not self._validee)

    def est_validee(self) -> bool:
        return self._validee

    def valider_temporairement(self, temps_ms: int):
        """Affiche la pastille verte de validation pendant temps_ms, puis la retire."""
        self.definir_validee(True)

        QTimer.singleShot(
            temps_ms,
            lambda: self.definir_validee(False),
        )


# 2 -- Application -------------------------------------------------------------


## 2.1 -- Bouton de sauvegarde -------------------------------------------------


class QPushButtonSauvegarde(QPushButtonIcone):

    def __init__(self, taille=32, parent=None):

        super().__init__(
            fonction_dessin=_dessiner_icone_disquette,
            taille=taille,
            parent=parent,
            padding=2,
        )

        self.clicked.connect(lambda: self.valider_temporairement(temps_ms=3000))
