################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# 4.0 – Menu de navigation de l'onglet de statistiques                         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math
from typing import Callable, Union

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPixmap, QPainter, QPen
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QButtonGroup,
)

# Type d'une fonction de dessin d'icône maison, ex: _dessiner_icone_flocon
FonctionDessinIcone = Callable[[QPainter, QPointF, float], None]
IconeType = Union[str, QPixmap, FonctionDessinIcone]


class BoutonNav(QPushButton):
    """Bouton de navigation composé d'une icône (à gauche, largeur fixe) et
    d'un libellé (à droite, extensible).

    L'icône peut être :
      - une chaîne (emoji ou caractère unicode) : "🗺️"
      - un QPixmap déjà rendu
      - une fonction de dessin `f(painter, centre, taille)` (ex: un flocon
        vectoriel dessiné à la main), qui sera exécutée sur un pixmap
        transparent créé automatiquement.
    """

    TAILLE_ICONE = 22  # taille de base en px, utilisée pour les icônes dessinées

    def __init__(self, icone: IconeType = "", texte: str = "", parent=None):
        super().__init__(parent)

        self.setObjectName("bouton_nav")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(38)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)

        # Icône : largeur fixe pour que tous les libellés démarrent alignés
        self.label_icone = QLabel()
        self.label_icone.setObjectName("icone_nav")
        self.label_icone.setFixedWidth(22)
        self.label_icone.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )

        # Texte : ne doit jamais être tronqué.
        self.label_texte = QLabel()
        self.label_texte.setObjectName("texte_nav")
        self.label_texte.setWordWrap(True)

        layout.addWidget(self.label_icone)
        layout.addWidget(self.label_texte, 1)

        self.label_icone.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.label_texte.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Mémorise la fonction de dessin courante (utile si l'on veut la
        # re-rendre plus tard, par ex. après un changement de résolution)
        self._icone_fn: FonctionDessinIcone | None = None

        self.set_icone(icone=icone)

    def set_icone(self, icone: IconeType):
        """Accepte un str (emoji/texte), un QPixmap, ou une fonction de
        dessin `f(painter, centre, taille)` façon `_dessiner_icone_flocon`."""

        if isinstance(icone, str) or icone is None:
            self._icone_fn = None
            self.label_icone.setPixmap(QPixmap())
            self.label_icone.setText(icone or "")

        elif isinstance(icone, QPixmap):
            self._icone_fn = None
            self.label_icone.setPixmap(icone)
            self.label_icone.setText("")

        elif callable(icone):
            # Fonction de dessin maison (vectorielle)
            self._icone_fn = icone
            self.label_icone.setPixmap(self._rendre_icone_vectorielle(icone))
            self.label_icone.setText("")

        else:
            raise TypeError(
                f"Type d'icône non supporté pour BoutonNav : {type(icone)!r}"
            )

    def _rendre_icone_vectorielle(
        self, fonction_dessin: FonctionDessinIcone, taille: int = None
    ) -> QPixmap:
        """Exécute `fonction_dessin(painter, centre, taille)` sur un QPixmap
        transparent, et renvoie le résultat. Gère le devicePixelRatio pour
        rester net sur les écrans haute résolution."""

        taille = taille or self.TAILLE_ICONE
        ratio = self.devicePixelRatioF()

        pixmap = QPixmap(int(taille * ratio), int(taille * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        centre = QPointF(taille / 2, taille / 2)
        fonction_dessin(painter, centre, float(taille))

        painter.end()
        return pixmap

    def set_texte(self, texte: str):
        self.label_texte.setText(texte)

    def set_couleur_texte(self, couleur: str, gras: bool = False):
        poids = "600" if gras else "400"
        self.label_texte.setStyleSheet(f"color: {couleur}; font-weight: {poids};")
