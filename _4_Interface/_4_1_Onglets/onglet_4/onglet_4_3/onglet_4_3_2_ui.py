################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_3                                #
# Onglet 4.3.1 – Suggestions de nouvelles destinations (partie graphique)      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import Qt, QRectF, QSize
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient, QPainterPath
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLayout,
    QLabel,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import _trouver_police_disponible
from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)

# 1 -- Mise en forme visuelle des recommandations ------------------------------


## 1.1 -- Thème de couleurs des cartes de recommandation -----------------------


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


## 1.2 -- Layout à retour à la ligne automatique (pour les "chips" de région) --


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


## 1.3 -- Bannière de titre ----------------------------------------------------


def creer_entete_recommandations(texte: str, theme: ThemeRecommandation) -> QLabel:
    """Bannière arrondie en dégradé, dans le même esprit que les titres
    de section de l'onglet 4.2 (`TitreClassement`)."""
    label = QLabel(texte)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setWordWrap(True)
    label.setStyleSheet(f"""
        QLabel {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {theme.badge_debut.name()}, stop:1 {theme.badge_fin.name()}
            );
            color: #FFFFFF;
            font-weight: 600;
            font-size: 15px;
            border-radius: 14px;
            padding: 10px 16px;
        }}
        """)
    return label


## 1.4 -- Chip de région -------------------------------------------------------


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


## 1.5 -- Carte "pays" (mode groupé) -------------------------------------------


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


## 1.6 -- Carte "ligne de classement" (mode non groupé) ------------------------


class CarteRecommandationSimple(QWidget):
    """
    Carte compacte pour une ligne de recommandation (mode non groupé) :
    badge de rang en dégradé, pays (avec emoji), région recommandée.
    Reprend le vocabulaire visuel de `CarteClassementPays` (onglet 4.2).
    """

    def __init__(
        self, rang: int, pays_nom: str, emoji: str, region: str, style, parent=None
    ):
        super().__init__(parent)
        self.theme = style
        self.rang = str(rang)
        self.pays_nom = pays_nom
        self.emoji = emoji
        self.region = region

        self.setMinimumSize(90, 100)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(20)
        self._ombre_effet.setOffset(0, 5)
        self._ombre_effet.setColor(self.theme.ombre)
        self.setGraphicsEffect(self._ombre_effet)

        self.police_principale = _trouver_police_disponible(
            ["CormorantGaramond", "Fredoka", "Quicksand", "Century Gothic", "Segoe UI"]
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()
        rect = QRectF(0, 0, w, h).adjusted(2, 2, -2, -2)
        rayon = min(18, min(w, h) * 0.14)
        chemin = QPainterPath()
        chemin.addRoundedRect(rect, rayon, rayon)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.theme.fond)
        painter.drawPath(chemin)
        painter.setClipPath(chemin)

        cote = min(w, h)

        # --- badge de rang ---
        rayon_badge = cote * 0.16
        centre_y = h * 0.22
        rect_badge = QRectF(
            w / 2 - rayon_badge,
            centre_y - rayon_badge,
            rayon_badge * 2,
            rayon_badge * 2,
        )
        degrade = QLinearGradient(rect_badge.topLeft(), rect_badge.bottomRight())
        degrade.setColorAt(0.0, self.theme.badge_debut)
        degrade.setColorAt(1.0, self.theme.badge_fin)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade)
        painter.drawEllipse(rect_badge)

        police_badge = QFont(
            self.police_principale, max(7, int(rayon_badge * 0.62)), QFont.Weight.Bold
        )
        painter.setFont(police_badge)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(rect_badge, Qt.AlignmentFlag.AlignCenter, self.rang)

        # --- pays ---
        police_pays = QFont(
            self.police_principale, max(8, int(cote * 0.085)), QFont.Weight.DemiBold
        )
        painter.setFont(police_pays)
        painter.setPen(self.theme.texte)
        rect_pays = QRectF(w * 0.05, h * 0.42, w * 0.9, h * 0.26)
        self._dessiner_texte_wrap(
            painter, rect_pays, f"{self.emoji} {self.pays_nom}".strip()
        )

        # --- région ---
        police_region = QFont(self.police_principale, max(7, int(cote * 0.07)))
        painter.setFont(police_region)
        painter.setPen(self.theme.sous_texte)
        rect_region = QRectF(w * 0.05, h * 0.7, w * 0.9, h * 0.26)
        self._dessiner_texte_wrap(painter, rect_region, self.region)

    def _dessiner_texte_wrap(self, painter, rect, texte):
        """Découpe `texte` en lignes qui tiennent dans la largeur de `rect`
        (même logique que `CarteClassementPays`, onglet 4.2)."""
        metrics = painter.fontMetrics()
        largeur_max = rect.width() - 0.2

        mots = texte.split()
        lignes = []
        ligne_courante = ""

        for mot in mots:
            essai = f"{ligne_courante} {mot}".strip()
            if metrics.horizontalAdvance(essai) <= largeur_max:
                ligne_courante = essai
            else:
                if ligne_courante:
                    lignes.append(ligne_courante)
                ligne_courante = mot
        if ligne_courante:
            lignes.append(ligne_courante)
        if not lignes:
            lignes = [""]

        hauteur_ligne = metrics.height()
        hauteur_totale = hauteur_ligne * len(lignes)
        y_depart = rect.y() + max(0.0, (rect.height() - hauteur_totale) / 2)

        for i, ligne in enumerate(lignes):
            rect_ligne = QRectF(
                rect.x(), y_depart + i * hauteur_ligne, rect.width(), hauteur_ligne
            )
            painter.drawText(rect_ligne, Qt.AlignmentFlag.AlignCenter, ligne)
