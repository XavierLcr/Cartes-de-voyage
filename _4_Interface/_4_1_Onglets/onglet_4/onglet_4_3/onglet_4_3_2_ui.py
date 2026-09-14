################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_3                                #
# Onglet 4.3.2 – Suggestions de nouvelles destinations (partie graphique)      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import Qt, QRectF, QSize
from PyQt6.QtGui import QPainter, QColor, QPainterPath
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLayout,
    QLabel,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)

from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)

# 1 -- Thème de couleurs des cartes de recommandation --------------------------


class ThemeRecommandation:
    """
    Palette de couleurs des cartes de recommandation, propre à l'onglet
    4.3. Le style clair garde une tonalité "nouvelle destination" :
    fond sauge apaisant, dégradé badge/bannière vert -> or. Le style
    sombre évoque un ciel de fin de journée : fond ardoise profond et
    neutre, avec un dégradé "soleil couchant" corail -> orange ambré en
    accent. L'ombre portée est toujours sombre (indépendante de la
    couleur du texte) : une ombre reprenant la couleur du texte
    devenait blanchâtre en mode sombre, ce qui cassait l'effet de
    profondeur recherché.
    """

    def __init__(
        self,
        style,
        teinte=[i / 360 for i in range(0, 360, 45)],
        nuances={
            "min_luminosite": 0.8,
            "max_luminosite": 0.95,
            "min_saturation": 0.2,
            "max_saturation": 0.4,
        },
        limite_essais=20,
    ):
        # Fond de carte : sauge doux en clair, ardoise bleu-gris neutre
        # en sombre — reste discret pour laisser le dégradé "coucher de
        # soleil" du badge être le vrai point d'accent chaud.
        self.fond = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#F3E6A5",
                sombre="#050505",
            )
        )
        self.texte = QColor(
            str(renvoyer_couleur_texte(style=style, couleur=self.fond.name()))
        )
        self.sous_texte = QColor(self.texte)
        self.sous_texte.setAlpha(140)

        # Dégradé badge/bannière : vert tendre -> or en clair,
        # corail -> orange ambré ("soleil couchant") en sombre.
        self.badge_debut = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#F8D136",
                sombre="#E0607E",  # rose-corail
            )
        )
        self.badge_fin = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#E84A4A",
                sombre="#F0954A",  # orange ambré
                reference=self.badge_debut.name(),
                essais=limite_essais,
            )
        )

        # Chips de région : version plus douce/sombre du fond, pour
        # rester lisible sans concurrencer le dégradé du badge.
        self.fond_chip = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#C2D76D",
                sombre="#7E2102",
            )
        )
        self.texte_chip = QColor(
            str(renvoyer_couleur_texte(style=style, couleur=self.fond_chip.name()))
        )

        # Ombre portée : toujours sombre, quel que soit le style —
        # contrairement à une ombre dérivée de `self.texte`, qui
        # devient claire (donc peu naturelle) en mode sombre.
        self.ombre = QColor("#000000")
        self.ombre.setAlpha(70 if style == 1 else 130)


# 2 -- Classes associées au classement par pays --------------------------------


## 2.1 -- Layout à retour à la ligne automatique (pour les "chips" de région) --


class FlowLayout(QLayout):
    """
    Layout qui aligne ses éléments horizontalement et passe à la ligne
    automatiquement lorsque la largeur disponible est dépassée. Utilisé
    pour les "chips" de régions d'un pays, dont le nombre est variable
    et ne se prête pas à une grille de taille fixe.
    """

    def __init__(self, parent=None, marge: int = 0, espacement: int = 6):
        super().__init__(parent)
        self._items = []
        self._espacement = espacement
        if parent is not None:
            self.setContentsMargins(marge, marge, marge, marge)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._faire_layout(QRectF(0, 0, width, 0).toRect(), test_seulement=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._faire_layout(rect, test_seulement=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        taille = QSize()
        for item in self._items:
            taille = taille.expandedTo(item.minimumSize())
        marges = self.contentsMargins()
        taille += QSize(marges.left() + marges.right(), marges.top() + marges.bottom())
        return taille

    def _faire_layout(self, rect, test_seulement: bool):
        marges = self.contentsMargins()
        x = rect.x() + marges.left()
        y = rect.y() + marges.top()
        largeur_max = rect.right() - marges.right()
        hauteur_ligne = 0

        for item in self._items:
            taille_item = item.sizeHint()
            x_suivant = x + taille_item.width() + self._espacement

            if x_suivant - self._espacement > largeur_max and hauteur_ligne > 0:
                x = rect.x() + marges.left()
                y = y + hauteur_ligne + self._espacement
                x_suivant = x + taille_item.width() + self._espacement
                hauteur_ligne = 0

            if not test_seulement:
                item.setGeometry(
                    QRectF(x, y, taille_item.width(), taille_item.height()).toRect()
                )

            x = x_suivant
            hauteur_ligne = max(hauteur_ligne, taille_item.height())

        return y + hauteur_ligne - rect.y() + marges.bottom()


## 2.2 -- Chip de région -------------------------------------------------------


def creer_chip_region(texte: str, theme: ThemeRecommandation) -> QLabel:
    """Petite pastille arrondie pour afficher le nom d'une région."""
    label = QLabel(texte)
    label.setStyleSheet(f"""
        QLabel {{
            background-color: {theme.fond_chip.name()};
            color: {theme.texte_chip.name()};
            border-radius: 9px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 500;
        }}
        """)
    label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    return label


## 2.3 -- Carte "pays" (mode groupé) -------------------------------------------


class CarteRecommandationPays(QWidget):
    """
    Carte pour un pays recommandé (mode groupé par pays) : nom du pays
    (avec emoji) en en-tête, suivi des régions recommandées sous forme
    de "chips" qui s'enchaînent et passent à la ligne automatiquement.
    """

    def __init__(
        self, pays_nom: str, emoji: str, regions: list[str], style, parent=None
    ):
        super().__init__(parent)
        self.theme = style

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(20)
        self._ombre_effet.setOffset(0, 5)
        self._ombre_effet.setColor(self.theme.ombre)
        self.setGraphicsEffect(self._ombre_effet)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(8)

        entete = QLabel(f"{emoji} {pays_nom} {emoji}".strip())
        entete.setStyleSheet(
            f"color: {self.theme.texte.name()}; font-weight: 600; "
            f"font-size: 14px; background: transparent;"
        )
        layout.addWidget(entete)

        conteneur_chips = QWidget()
        conteneur_chips.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        flow = FlowLayout(conteneur_chips, marge=0, espacement=6)
        for region in regions:
            flow.addWidget(creer_chip_region(region, self.theme))
        layout.addWidget(conteneur_chips)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(0, 0, self.width(), self.height()).adjusted(1, 1, -1, -1)
        rayon = min(16, min(self.width(), self.height()) * 0.1)
        chemin = QPainterPath()
        chemin.addRoundedRect(rect, rayon, rayon)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.theme.fond)
        painter.drawPath(chemin)

        super().paintEvent(event)
