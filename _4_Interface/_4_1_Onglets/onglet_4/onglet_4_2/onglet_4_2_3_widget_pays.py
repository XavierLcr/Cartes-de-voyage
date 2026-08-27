################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_2                                #
# Onglet 4.2.3 – Partie classement des pays visités                            #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QFont,
    QLinearGradient,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import (
    QWidget,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import _trouver_police_disponible
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_2.onglet_4_2_1_style_visuel import (
    ThemeCarteClassement,
)

# 1 -- Widget de création de la bulle associée à un pays donné -----------------


class CarteClassementPays(QWidget):
    """
    Carte compacte pour une ligne du classement (rang 4 et plus) :
    badge de rang, nom du pays, pourcentage de superficie visitée.

    Reprend le vocabulaire visuel des widgets du tableau de bord et du
    podium voisin (onglet 4.2.1) : carte à coins arrondis, ombre douce,
    même police "joyeuse" que le podium (avec repli automatique), et un
    thème de couleurs (`ThemeCarteClassement`) construit sur les mêmes
    appels de style que le reste du tableau de bord.

    Améliorations visuelles par rapport à la version précédente :
    - léger liseré (bordure) autour de la carte pour la détacher du fond
    - reflet "glacé" en haut de la carte pour un effet plus premium
    - badge de rang avec ombre portée propre et anneau de contour
    - mini barre de progression sous le pourcentage, pour visualiser
      la superficie visitée d'un coup d'œil
    - séparateur discret entre le nom du pays et le pourcentage
    """

    def __init__(
        self,
        classement: str,
        nom_pays: str,
        pct_label: str,
        style,
        parent=None,
    ) -> None:

        super().__init__(parent)

        self.classement = classement
        self.nom_pays = nom_pays
        self.pct_label = pct_label

        # Valeur numérique du pourcentage, utilisée pour la mini barre de
        # progression. On tente de la déduire de `pct_label` (ex: "42 %"),
        # et on retombe sur 0 si l'extraction échoue.
        self._pct_valeur = self._extraire_pourcentage(pct_label)

        # Thème par défaut (clair) — mis à jour via `set_style` si le
        # widget parent (ClassementPays / OngletTopPays) est un jour
        # branché sur le système de thème clair/sombre de l'appli.
        self.theme = style

        # Même police que le podium (méthode réutilisée depuis Podium
        # pour ne pas dupliquer la liste de polices candidates).
        self.police_principale = _trouver_police_disponible(
            [
                "CormorantGaramond",
                "Fredoka",
                "Quicksand",
                "Century Gothic",
                "Segoe UI",
            ]
        )

        self.setMinimumSize(80, 90)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(28)
        self._ombre_effet.setOffset(0, 8)
        self._ombre_effet.setColor(self.theme.ombre)
        self.setGraphicsEffect(self._ombre_effet)

    @staticmethod
    def _extraire_pourcentage(pct_label: str) -> float:
        """Extrait la valeur numérique d'un label du type '42 %' ou '3.5%'."""
        chiffres = ""
        for c in pct_label:
            if c.isdigit() or c == ".":
                chiffres += c
            elif chiffres:
                break
        try:
            return max(0.0, min(100.0, float(chiffres)))
        except ValueError:
            return 0.0

    def set_style(self, style, nuances, teintes):
        """Met à jour le thème de couleurs (même signature que les autres
        widgets du tableau de bord : `set_style(style, nuances, teintes)`)."""
        self.theme = ThemeCarteClassement(
            style=style, nuances=nuances, teinte=teintes, limite_essais=20
        )
        self._ombre_effet.setColor(self.theme.ombre)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()

        # --- carte à coins arrondis ---
        rect_carte = QRectF(0, 0, w, h).adjusted(2, 2, -2, -2)
        rayon = min(20, min(w, h) * 0.14)
        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(rect_carte, rayon, rayon)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.theme.fond)
        painter.drawPath(chemin_carte)

        # léger liseré pour détacher la carte du fond
        pen_contour = QPen(self.theme.badge_debut)
        pen_contour.setWidthF(1.1)
        pen_contour.setColor(self._avec_alpha(self.theme.badge_debut, 60))
        painter.setPen(pen_contour)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(chemin_carte)

        painter.setClipPath(chemin_carte)

        # reflet "glacé" discret en haut de la carte
        degrade_reflet = QLinearGradient(0, 0, 0, h * 0.5)
        degrade_reflet.setColorAt(0.0, self._avec_alpha(QColor("#FFFFFF"), 40))
        degrade_reflet.setColorAt(1.0, self._avec_alpha(QColor("#FFFFFF"), 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade_reflet)
        painter.drawRect(QRectF(0, 0, w, h * 0.5))

        cote = min(w, h)

        # --- badge de rang ---
        rayon_badge = cote * 0.17
        centre_badge_y = h * 0.24
        rect_badge = QRectF(
            w / 2 - rayon_badge,
            centre_badge_y - rayon_badge,
            rayon_badge * 2,
            rayon_badge * 2,
        )

        # petite ombre propre au badge, pour le détacher du fond de carte
        rect_ombre_badge = rect_badge.translated(0, rayon_badge * 0.12)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._avec_alpha(QColor("#000000"), 35))
        painter.drawEllipse(rect_ombre_badge)

        degrade = QLinearGradient(rect_badge.topLeft(), rect_badge.bottomRight())
        degrade.setColorAt(0.0, self.theme.badge_debut)
        degrade.setColorAt(1.0, self.theme.badge_fin)
        painter.setBrush(degrade)
        painter.drawEllipse(rect_badge)

        # fin anneau clair sur le pourtour du badge, effet "médaille"
        pen_anneau = QPen(self._avec_alpha(QColor("#FFFFFF"), 90))
        pen_anneau.setWidthF(max(1.0, rayon_badge * 0.06))
        painter.setPen(pen_anneau)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect_badge.adjusted(1, 1, -1, -1))

        police_badge = QFont(
            self.police_principale, max(7, int(rayon_badge * 0.62)), QFont.Weight.Bold
        )
        painter.setFont(police_badge)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(rect_badge, Qt.AlignmentFlag.AlignCenter, self.classement)

        # --- nom du pays ---
        police_nom = QFont(
            self.police_principale, max(8, int(cote * 0.09)), QFont.Weight.DemiBold
        )
        painter.setFont(police_nom)
        painter.setPen(self.theme.texte)
        rect_nom = QRectF(w * 0.06, h * 0.46, w * 0.88, h * 0.26)
        self._dessiner_texte_wrap(painter, rect_nom, self.nom_pays)

        # --- pourcentage ---
        police_pct = QFont(self.police_principale, max(7, int(cote * 0.075)))
        painter.setFont(police_pct)
        painter.setPen(self.theme.sous_texte)
        rect_pct = QRectF(w * 0.06, h * 0.77, w * 0.88, h * 0.13)
        painter.drawText(rect_pct, Qt.AlignmentFlag.AlignCenter, self.pct_label)

        # --- mini barre de progression ---
        largeur_barre = w * 0.7
        hauteur_barre = max(3.0, h * 0.028)
        x_barre = (w - largeur_barre) / 2
        y_barre = h * 0.92

        rect_barre_fond = QRectF(x_barre, y_barre, largeur_barre, hauteur_barre)
        chemin_fond = QPainterPath()
        chemin_fond.addRoundedRect(
            rect_barre_fond, hauteur_barre / 2, hauteur_barre / 2
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._avec_alpha(self.theme.sous_texte, 45))
        painter.drawPath(chemin_fond)

        largeur_remplie = largeur_barre * (self._pct_valeur / 100.0)
        if largeur_remplie > 0:
            rect_barre_remplie = QRectF(
                x_barre, y_barre, largeur_remplie, hauteur_barre
            )
            chemin_remplie = QPainterPath()
            chemin_remplie.addRoundedRect(
                rect_barre_remplie, hauteur_barre / 2, hauteur_barre / 2
            )
            degrade_barre = QLinearGradient(
                rect_barre_remplie.topLeft(), rect_barre_remplie.topRight()
            )
            degrade_barre.setColorAt(0.0, self.theme.badge_debut)
            degrade_barre.setColorAt(1.0, self.theme.badge_fin)
            painter.setBrush(degrade_barre)
            painter.drawPath(chemin_remplie)

    @staticmethod
    def _avec_alpha(couleur: QColor, alpha: int) -> QColor:
        """Retourne une copie de `couleur` avec un canal alpha donné (0-255)."""
        c = QColor(couleur)
        c.setAlpha(alpha)
        return c

    def _dessiner_texte_wrap(self, painter, rect, texte):
        """Découpe `texte` en lignes qui tiennent dans la largeur de `rect`
        (même logique que le podium voisin)."""
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
