################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1.7 – Barre de progression classique                                  #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import sys

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QLinearGradient,
    QPainter,
    QPainterPath,
)
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

# 1 -- Classe de la barre de progression ---------------------------------------


class BarreProgressionVoyage(QWidget):
    """
    Barre de progression compacte, dessinée intégralement avec QPainter.

    Les quatre méthodes publiques permettent de modifier :
        - le texte supérieur ;
        - le texte inférieur ;
        - la valeur maximale ;
        - la valeur actuelle.

    Le thème est choisi à l'instanciation : "clair" ou "sombre".
    """

    HAUTEUR = 76

    PALETTES = {
        "clair": {
            "fond": "#F5F5FA",
            "texte_haut": "#34465A",
            "texte_bas": "#8293A5",
            "ratio": "#31566D",
            "fond_ratio": "#D6E4F0",
            "piste": "#DCE3EC",
            "progression_debut": "#72BAD6",
            "progression_fin": "#91C9D8",
            "repere": "#F5F5FA",
            "repere_bord": "#72BAD6",
        },
        "sombre": {
            "fond": "#10141C",
            "texte_haut": "#E6EDF5",
            "texte_bas": "#7D91A5",
            "ratio": "#D7F3F5",
            "fond_ratio": "#1C3545",
            "piste": "#27364D",
            "progression_debut": "#26C6DA",
            "progression_fin": "#38AFC5",
            "repere": "#10141C",
            "repere_bord": "#26C6DA",
        },
    }

    def __init__(
        self,
        texte_haut="",
        texte_bas="",
        maximum=100,
        valeur=0,
        theme="clair",
        parent=None,
    ):
        super().__init__(parent)

        if theme not in self.PALETTES:
            raise ValueError("Le thème doit être 'clair' ou 'sombre'.")
        if maximum < 0:
            raise ValueError("Le maximum doit être positif ou nul.")

        self._texte_haut = str(texte_haut)
        self._texte_bas = str(texte_bas)
        self._maximum = int(maximum)
        self._valeur = max(0, min(int(valeur), self._maximum))
        self._theme = theme

        self.setFixedHeight(self.HAUTEUR)
        self.setMinimumWidth(180)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    # 1.1 -- API publique : textes ---------------------------------------------

    def set_texte_haut(self, texte):
        """Modifie le texte affiché au-dessus de la barre."""
        texte = str(texte)
        if texte != self._texte_haut:
            self._texte_haut = texte
            self.update()

    def set_texte_bas(self, texte):
        """Modifie le texte affiché sous la barre."""
        texte = str(texte)
        if texte != self._texte_bas:
            self._texte_bas = texte
            self.update()

    # 1.2 -- API publique : progression ----------------------------------------

    def set_maximum(self, maximum):
        """Modifie la valeur maximale et ajuste la valeur actuelle si nécessaire."""
        maximum = int(maximum)
        if maximum < 0:
            raise ValueError("Le maximum doit être positif ou nul.")

        if maximum != self._maximum:
            self._maximum = maximum
            self._valeur = min(self._valeur, self._maximum)
            self.update()

    def set_valeur(self, valeur):
        """Modifie la valeur actuelle, automatiquement bornée entre 0 et le maximum."""
        valeur = int(valeur)
        valeur = max(0, min(valeur, self._maximum))

        if valeur != self._valeur:
            self._valeur = valeur
            self.update()

    # 1.3 -- Dessin -------------------------------------------------------------

    def paintEvent(self, event):
        palette = self.PALETTES[self._theme]

        largeur = self.width()
        hauteur = self.height()

        marge_x = 13
        largeur_utile = max(0, largeur - 2 * marge_x)

        # Dimensions verticales
        y_haut = 7
        hauteur_ligne = 17
        y_barre = 29
        hauteur_barre = 23
        y_bas = 59

        ratio = f"{self._valeur} / {self._maximum}"

        # Ratio présenté dans une petite capsule
        police_ratio = QFont(self.font())
        police_ratio.setPointSizeF(max(8.0, self.font().pointSizeF() - 0.5))
        police_ratio.setWeight(QFont.Weight.DemiBold)
        mesures_ratio = QFontMetricsF(police_ratio)
        largeur_ratio = mesures_ratio.horizontalAdvance(ratio) + 18
        hauteur_ratio = 18

        # Zone disponible pour le texte supérieur
        espace = 10
        largeur_texte_haut = max(0, largeur_utile - largeur_ratio - espace)

        police_haut = QFont(self.font())
        police_haut.setWeight(QFont.Weight.DemiBold)
        mesures_haut = QFontMetricsF(police_haut)
        texte_haut = mesures_haut.elidedText(
            self._texte_haut,
            Qt.TextElideMode.ElideRight,
            int(largeur_texte_haut),
        )

        # Préparation du peintre
        peintre = QPainter(self)
        peintre.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        peintre.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        # Fond général
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(QColor(palette["fond"]))
        peintre.drawRoundedRect(QRectF(0.5, 0.5, largeur - 1, hauteur - 1), 12, 12)

        # Texte supérieur
        peintre.setFont(police_haut)
        peintre.setPen(QColor(palette["texte_haut"]))
        peintre.drawText(
            QRectF(marge_x, y_haut, largeur_texte_haut, hauteur_ligne),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            texte_haut,
        )

        # Capsule du ratio
        x_ratio = largeur - marge_x - largeur_ratio
        rect_ratio = QRectF(
            x_ratio,
            y_haut - 1,
            largeur_ratio,
            hauteur_ratio,
        )
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(QColor(palette["fond_ratio"]))
        peintre.drawRoundedRect(rect_ratio, 7, 7)

        peintre.setFont(police_ratio)
        peintre.setPen(QColor(palette["ratio"]))
        peintre.drawText(
            rect_ratio,
            Qt.AlignmentFlag.AlignCenter,
            ratio,
        )

        # Piste de progression
        rect_piste = QRectF(
            marge_x,
            y_barre,
            largeur_utile,
            hauteur_barre,
        )
        rayon = hauteur_barre / 2

        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(QColor(palette["piste"]))
        peintre.drawRoundedRect(rect_piste, rayon, rayon)

        # Partie remplie
        if self._maximum > 0 and self._valeur > 0 and largeur_utile > 0:
            progression = min(1.0, self._valeur / self._maximum)
            largeur_remplie = largeur_utile * progression
            rect_rempli = QRectF(
                marge_x,
                y_barre,
                largeur_remplie,
                hauteur_barre,
            )

            # Dégradé horizontal discret
            degrade = QLinearGradient(
                rect_rempli.left(),
                rect_rempli.top(),
                rect_rempli.right(),
                rect_rempli.bottom(),
            )
            degrade.setColorAt(0.0, QColor(palette["progression_debut"]))
            degrade.setColorAt(1.0, QColor(palette["progression_fin"]))

            chemin = QPainterPath()
            chemin.addRoundedRect(rect_rempli, rayon, rayon)

            # Empêche le remplissage de dépasser de la piste
            chemin_piste = QPainterPath()
            chemin_piste.addRoundedRect(rect_piste, rayon, rayon)

            peintre.save()
            peintre.setClipPath(chemin_piste)
            peintre.fillPath(chemin, degrade)

            # Petit repère circulaire à l'extrémité de la progression
            diametre = 13
            centre_x = largeur_remplie  # - 0.05 * largeur_utile
            centre_y = y_barre + hauteur_barre / 2

            # À 100 %, le repère reste légèrement à l'intérieur de la piste
            centre_x = min(
                max(centre_x, marge_x + diametre / 2),
                marge_x + largeur_utile - diametre / 2,
            )

            peintre.setBrush(QColor(palette["repere"]))
            peintre.setPen(QColor(palette["repere_bord"]))
            peintre.setPen(QColor(palette["repere_bord"]))
            peintre.setBrush(QColor(palette["repere"]))
            peintre.drawEllipse(
                QRectF(
                    centre_x - diametre / 2,
                    centre_y - diametre / 2,
                    diametre,
                    diametre,
                )
            )
            peintre.restore()

        # Texte inférieur
        police_bas = QFont(self.font())
        police_bas.setPointSizeF(max(8.0, self.font().pointSizeF() - 1))
        mesures_bas = QFontMetricsF(police_bas)
        texte_bas = mesures_bas.elidedText(
            self._texte_bas,
            Qt.TextElideMode.ElideRight,
            int(largeur_utile),
        )

        peintre.setFont(police_bas)
        peintre.setPen(QColor(palette["texte_bas"]))
        peintre.drawText(
            QRectF(marge_x, y_bas, largeur_utile, 13),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            texte_bas,
        )

        peintre.end()


# 2 -- Démonstration ------------------------------------------------------------


if __name__ == "__main__":
    app = QApplication(sys.argv)

    fenetre = QWidget()
    fenetre.setWindowTitle("Test – Barre de progression")
    fenetre.resize(520, 260)

    layout = QVBoxLayout(fenetre)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(12)

    barre_claire = BarreProgressionVoyage(
        texte_haut="Belgique · Pays-Bas · Allemagne",
        texte_bas="Génération des cartes en cours",
        maximum=18,
        valeur=12,
        theme="clair",
    )

    barre_sombre = BarreProgressionVoyage(
        texte_haut="France · Espagne",
        texte_bas="Préparation des données géographiques",
        maximum=10,
        valeur=7,
        theme="sombre",
    )

    layout.addWidget(barre_claire)
    layout.addWidget(barre_sombre)

    # Exemple d'utilisation des quatre API publiques
    barre_claire.set_texte_haut("Belgique · Pays-Bas")
    barre_claire.set_texte_bas("Publication des cartes")
    barre_claire.set_maximum(20)
    barre_claire.set_valeur(4)

    fenetre.show()
    sys.exit(app.exec())
