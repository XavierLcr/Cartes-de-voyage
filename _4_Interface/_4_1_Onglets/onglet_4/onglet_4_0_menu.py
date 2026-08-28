################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# 4.0 – Menu de navigation de l'onglet de statistiques                         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from typing import Callable, Optional, Union

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QColor, QPixmap, QPainter, QBrush
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QPushButton

FonctionDessinIcone = Callable[[QPainter, QPointF, float], None]
IconeType = Union[str, QPixmap, FonctionDessinIcone]

# Formes de fond disponibles pour les icônes vectorielles
FormeFond = str  # "cercle" | "carre" | "carre_arrondi"


# 1 -- Classe du menu ----------------------------------------------------------


class BoutonNav(QPushButton):
    """Bouton de navigation composé d'une icône (à gauche, largeur fixe) et
    d'un libellé (à droite, extensible).

    L'icône peut être :
      - une chaîne (emoji ou caractère unicode) : "🗺️"
      - un QPixmap déjà rendu
      - une fonction de dessin `f(painter, centre, taille)` (ex: un flocon
        vectoriel), qui sera exécutée sur un pixmap transparent créé
        automatiquement. Dans ce cas, un `fond` optionnel peut être fourni
        (couleur + forme) pour habiller l'icône, ex: un disque bleu nuit
        derrière un flocon blanc.
    """

    def __init__(
        self,
        icone: IconeType = "",
        icone_taille: int = 35,
        parent=None,
        fond: Optional[Union[str, QColor]] = None,
        fond_forme: FormeFond = "cercle",
        fond_marge: float = 0.0,
    ):
        super().__init__(parent)

        self.setObjectName("bouton_nav")
        self.TAILLE_ICONE = icone_taille
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(38)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)

        self.label_icone = QLabel()
        self.label_icone.setObjectName("icone_nav")
        self.label_icone.setFixedWidth(self.TAILLE_ICONE + 2)
        self.label_icone.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )

        self.label_texte = QLabel()
        self.label_texte.setObjectName("texte_nav")
        self.label_texte.setWordWrap(True)

        layout.addWidget(self.label_icone)
        layout.addWidget(self.label_texte, 1)

        self.label_icone.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.label_texte.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self._icone_fn: Optional[FonctionDessinIcone] = None

        self.set_icone(
            icone=icone,
            fond=fond,
            fond_forme=fond_forme,
            fond_marge=fond_marge,
        )

    def set_icone(
        self,
        icone: IconeType,
        fond: Optional[Union[str, QColor]] = None,
        fond_forme: FormeFond = "cercle",
        fond_marge: float = 0.0,
    ):
        """Accepte un str (emoji/texte), un QPixmap, ou une fonction de
        dessin `f(painter, centre, taille)`.

        `fond`, `fond_forme` et `fond_marge` ne s'appliquent qu'au cas
        « fonction de dessin » :
          - fond : couleur du fond ("#0B1D3A", QColor(...), etc.). None = pas de fond.
          - fond_forme : "cercle" | "carre" | "carre_arrondi"
          - fond_marge : espace (en px, à l'échelle TAILLE_ICONE) laissé entre
            le bord du pixmap et le bord du fond, pour éviter que le disque
            touche les bords du label.
        """

        if isinstance(icone, str) or icone is None:
            self._icone_fn = None
            self.label_icone.setPixmap(QPixmap())
            self.label_icone.setText(icone or "")

        elif isinstance(icone, QPixmap):
            self._icone_fn = None
            self.label_icone.setPixmap(icone)
            self.label_icone.setText("")

        elif callable(icone):
            self._icone_fn = icone
            self.label_icone.setPixmap(
                self._rendre_icone_vectorielle(
                    icone,
                    fond=fond,
                    fond_forme=fond_forme,
                    fond_marge=fond_marge,
                )
            )
            self.label_icone.setText("")

        else:
            raise TypeError(
                f"Type d'icône non supporté pour BoutonNav : {type(icone)!r}"
            )

    def _dessiner_fond(
        self,
        painter: QPainter,
        taille: float,
        fond: Union[str, QColor],
        forme: FormeFond,
        marge: float,
    ):
        """Dessine la forme de fond derrière l'icône."""
        couleur = fond if isinstance(fond, QColor) else QColor(fond)

        rect = QRectF(marge, marge, taille - 2 * marge, taille - 2 * marge)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(couleur))

        if forme == "cercle":
            painter.drawEllipse(rect)
        elif forme == "carre":
            painter.drawRect(rect)
        elif forme == "carre_arrondi":
            rayon_coin = taille * 0.22
            painter.drawRoundedRect(rect, rayon_coin, rayon_coin)
        else:
            raise ValueError(f"Forme de fond inconnue : {forme!r}")

    def _rendre_icone_vectorielle(
        self,
        fonction_dessin: FonctionDessinIcone,
        taille: int = None,
        fond: Optional[Union[str, QColor]] = None,
        fond_forme: FormeFond = "cercle",
        fond_marge: float = 0.0,
    ) -> QPixmap:
        """Exécute `fonction_dessin(painter, centre, taille)` sur un QPixmap
        transparent (avec fond optionnel dessiné en premier), et renvoie le
        résultat. Gère le devicePixelRatio pour rester net sur les écrans
        haute résolution."""

        taille = taille or self.TAILLE_ICONE
        ratio = self.devicePixelRatioF()

        pixmap = QPixmap(int(taille * ratio), int(taille * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if fond is not None:
            self._dessiner_fond(
                painter, taille=taille, fond=fond, forme=fond_forme, marge=fond_marge
            )

        centre = QPointF(taille / 2, taille / 2)
        fonction_dessin(painter, centre, float(taille))

        painter.end()
        return pixmap

    def set_texte(self, texte: str):
        self.label_texte.setText(texte)

    def set_couleur_texte(self, couleur: str, gras: bool = False):
        poids = "600" if gras else "400"
        self.label_texte.setStyleSheet(f"color: {couleur}; font-weight: {poids};")
