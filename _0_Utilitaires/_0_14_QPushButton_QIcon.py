################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# 0.14 – QPushButton sans texte, avec seulement une icône                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import inspect

from PyQt6.QtCore import QPointF, QTimer
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QPushButton, QStyle, QStyleOptionButton

from _4_Interface._4_3_Icones._4_3_25_disquette import _dessiner_icone_disquette

# 1 -- Fonction générale -------------------------------------------------------


class QPushButtonIcone(QPushButton):
    """
    QPushButton affichant uniquement un dessin vectoriel.

    Le dessin est effectué directement dans paintEvent afin d'éviter
    l'intermédiaire QPixmap -> QIcon, qui peut provoquer un léger flou
    lors du rendu ou du redimensionnement par Qt.

    Supporte également une pastille de validation optionnelle si la
    fonction de dessin accepte le paramètre "validee".
    """

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
        self._padding = padding

        self._validee = False

        # Détecte une seule fois si la fonction de dessin accepte "validee"
        self._accepte_validee = (
            "validee" in inspect.signature(fonction_dessin).parameters
        )

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

    # -- Rendu interne ---------------------------------------------------------

    def paintEvent(self, event) -> None:
        """
        Dessine le bouton puis l'icône directement dessus.

        On laisse d'abord Qt dessiner le fond du QPushButton
        (hover, pressed, etc.), puis on ajoute notre dessin vectoriel.
        """

        # ----------------------------------------------------------------------
        # 1. Dessin standard du QPushButton
        # ----------------------------------------------------------------------

        option = QStyleOptionButton()
        self.initStyleOption(option)

        painter = QPainter(self)

        self.style().drawControl(
            QStyle.ControlElement.CE_PushButton,
            option,
            painter,
            self,
        )

        # ----------------------------------------------------------------------
        # 2. Dessin de l'icône
        # ----------------------------------------------------------------------

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        painter.setRenderHint(
            QPainter.RenderHint.TextAntialiasing,
            True,
        )

        # Le padding réduit directement la zone réellement dessinée.
        taille_dessin = max(
            1,
            min(self.width(), self.height()) - 2 * self._padding,
        )

        centre = QPointF(
            self.width() / 2,
            self.height() / 2,
        )

        if self._accepte_validee:

            self._fonction_dessin(
                painter,
                centre,
                taille_dessin,
                validee=self._validee,
            )

        else:

            self._fonction_dessin(
                painter,
                centre,
                taille_dessin,
            )

        painter.end()

    # -- API publique ----------------------------------------------------------

    def definir_validee(self, validee: bool) -> None:
        """Active ou désactive la pastille verte de validation."""

        if validee != self._validee:

            self._validee = validee
            self.update()

    def basculer_validee(self) -> None:
        """Inverse l'état actuel de la pastille de validation."""

        self.definir_validee(not self._validee)

    def est_validee(self) -> bool:
        """Renvoie l'état actuel de validation."""

        return self._validee

    def valider_temporairement(self, temps_ms: int):
        """
        Affiche la pastille verte de validation pendant temps_ms,
        puis la retire.
        """

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
