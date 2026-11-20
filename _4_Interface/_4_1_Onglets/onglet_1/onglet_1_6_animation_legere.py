################################################################################
# Projet de cartes de voyage
# _4_Interface/_4_3_Icones/
# Animation légère de création des cartes
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


if __name__ == "__main__":

    import sys, os

    sys.path.append(os.getcwd())

from PyQt6.QtCore import Qt, QTimer, QElapsedTimer
from PyQt6.QtGui import QPainter, QFont, QColor, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QGroupBox,
)


from _4_Interface._4_3_Icones._4_3_48_avion._4_3_48_X_avion import Avion
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import _QColor_avec_alpha

# 1 -- Constantes --------------------------------------------------------------


HAUTEUR_WIDGET = 76

HAUTEUR_BANDEAU = 20
HAUTEUR_AVION = 36

COULEUR_FOND = "#EAF1F3"

COULEUR_BANDEAU_HAUT = "#DCEAF0"
COULEUR_BANDEAU_BAS = "#E9E2D6"

COULEUR_TEXTE = "#294B5A"
COULEUR_TEXTE_SECONDAIRE = "#806D5B"

COULEUR_RATIO_FOND = "#ECEA9A"
COULEUR_RATIO_TEXTE = "#66502E"

COULEUR_ACCOTEMENT = "#87949C"
COULEUR_PISTE = "#465159"
COULEUR_BORD_PISTE = "#65727B"
COULEUR_MARQUAGE = "#F6F5EC"
COULEUR_LIGNE_CENTRALE = "#EBD182"


# 2 -- Avion horizontal --------------------------------------------------------


class AvionHorizontal(Avion):
    """
    Variante de l'avion dont la trajectoire reste parfaitement horizontale.
    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self._y_entree = 0.50
        self._y_sortie = 0.50

    def _nouveau_passage(self):

        self._distance = 0.0
        self._y_entree = 0.50
        self._y_sortie = 0.50


# 3 -- Zone d'animation de l'avion --------------------------------------------


class ZoneAvion(QWidget):
    """
    Zone centrale dans laquelle l'avion effectue son trajet en boucle.

    L'avion démarre toujours au même endroit, indépendamment de la
    progression de la création des cartes.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setFixedHeight(HAUTEUR_AVION)

        # Avion
        self.avion = AvionHorizontal(
            avion="ligne",
            taille=34,
            vitesse=75,
            marge_sortie=18,
            anticipation_rotation=20,
            tension=0.0,
            lumieres=True,
        )

        self.avion.repeter_en_boucle = True

        # Animation
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._actualiser)

        self.chronometre = QElapsedTimer()

    # -------------------------------------------------------------------------

    def demarrer(self):

        if self.timer.isActive():
            return

        self.chronometre.start()
        self.timer.start()

    # -------------------------------------------------------------------------

    def arreter(self):

        self.timer.stop()

    # -------------------------------------------------------------------------

    def _actualiser(self):

        delta = min(self.chronometre.restart() / 1000, 0.05)

        self.avion.animer(delta)

        self.update()

    # -------------------------------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Accotements de la piste
        painter.fillRect(self.rect(), QColor(COULEUR_ACCOTEMENT))

        # 2. Surface asphaltée
        x_piste = 3
        y_piste = 2
        largeur_piste = self.width() - 6
        hauteur_piste = self.height() - 4

        painter.setPen(QPen(QColor(COULEUR_BORD_PISTE), 1))
        painter.setBrush(QColor(COULEUR_PISTE))

        painter.drawRoundedRect(
            x_piste,
            y_piste,
            largeur_piste,
            hauteur_piste,
            4,
            4,
        )

        # 3. Lignes blanches de délimitation
        painter.setPen(QPen(_QColor_avec_alpha(COULEUR_MARQUAGE, alpha=200), 1.2))

        y_ligne_haute = y_piste + 4
        y_ligne_basse = y_piste + hauteur_piste - 4

        painter.drawLine(
            x_piste + 7,
            y_ligne_haute,
            x_piste + largeur_piste - 7,
            y_ligne_haute,
        )

        painter.drawLine(
            x_piste + 7,
            y_ligne_basse,
            x_piste + largeur_piste - 7,
            y_ligne_basse,
        )

        # 4. Marquages de seuil : les bandes blanches au début de piste
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_QColor_avec_alpha(COULEUR_MARQUAGE, alpha=220))

        for decalage in (0, 6, 12, 18):
            painter.drawRoundedRect(
                x_piste + 8 + decalage,
                y_piste + 8,
                3,
                hauteur_piste - 16,
                1,
                1,
            )

        # 5. Ligne centrale discontinue, légèrement dorée
        painter.setBrush(_QColor_avec_alpha(COULEUR_LIGNE_CENTRALE, alpha=170))

        y_centre = self.height() // 2

        for x in range(x_piste + 38, x_piste + largeur_piste - 8, 20):
            painter.drawRoundedRect(
                x,
                y_centre - 1,
                10,
                2,
                1,
                1,
            )

        # 6. L'avion démarre toujours à 12 % et peut atteindre l'extrémité.
        marge_gauche = int(self.width() * 0.12)
        marge_droite = 0

        rect_zone = self.rect().adjusted(
            marge_gauche,
            0,
            -marge_droite,
            0,
        )

        self.avion.dessiner(
            painter=painter,
            points_passage=[],
            rect_zone=rect_zone,
        )

        painter.end()


# 4 -- Animation légère -------------------------------------------------------


class AnimationCreationLegere(QWidget):
    """
    Animation de création des cartes avec trois zones distinctes :

    - Bandeau supérieur : texte principal et progression.
    - Zone centrale : avion animé.
    - Bandeau inférieur : texte secondaire en italique.

    API publique :
        set_texte_haut(texte)
        set_texte_bas(texte)
        set_maximum(maximum)
        set_valeur(valeur)

    Animation :
        demarrer()
        arreter()
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self._maximum = 100
        self._valeur = 0

        self.setFixedHeight(HAUTEUR_WIDGET)

        self._creer_interface()
        self._appliquer_style()

    # 4.1 -- Interface ---------------------------------------------------------

    def _creer_interface(self):

        layout_principal = QVBoxLayout(self)

        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # ---------------------------------------------------------------------
        # Bandeau supérieur
        # ---------------------------------------------------------------------

        self.bandeau_haut = QWidget()

        self.bandeau_haut.setFixedHeight(HAUTEUR_BANDEAU)

        layout_haut = QHBoxLayout(self.bandeau_haut)

        layout_haut.setContentsMargins(12, 0, 10, 0)
        layout_haut.setSpacing(8)

        self.label_haut = QLabel("Préparation des destinations")

        police_haut = QFont()
        police_haut.setPointSize(9)
        police_haut.setWeight(QFont.Weight.DemiBold)

        self.label_haut.setFont(police_haut)
        self.label_haut.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )

        layout_haut.addWidget(self.label_haut, 1)

        # Ratio de progression
        self.label_ratio = QLabel("0 / 100")

        self.label_ratio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_ratio.setFixedHeight(HAUTEUR_BANDEAU - 4)
        self.label_ratio.setMinimumWidth(50)

        police_ratio = QFont()
        police_ratio.setPointSize(8)
        police_ratio.setWeight(QFont.Weight.DemiBold)

        self.label_ratio.setFont(police_ratio)

        layout_haut.addWidget(self.label_ratio)

        # ---------------------------------------------------------------------
        # Zone centrale : avion
        # ---------------------------------------------------------------------

        self.zone_avion = ZoneAvion()

        # ---------------------------------------------------------------------
        # Bandeau inférieur
        # ---------------------------------------------------------------------

        self.bandeau_bas = QWidget()

        self.bandeau_bas.setFixedHeight(HAUTEUR_BANDEAU)

        layout_bas = QHBoxLayout(self.bandeau_bas)

        layout_bas.setContentsMargins(12, 0, 12, 0)
        layout_bas.setSpacing(0)

        self.label_bas = QLabel("Création des cartes en cours…")

        police_bas = QFont()
        police_bas.setPointSize(8)
        police_bas.setItalic(True)

        self.label_bas.setFont(police_bas)
        self.label_bas.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )

        layout_bas.addWidget(self.label_bas)

        # ---------------------------------------------------------------------

        layout_principal.addWidget(self.bandeau_haut)
        layout_principal.addWidget(self.zone_avion)
        layout_principal.addWidget(self.bandeau_bas)

    # 4.2 -- Style -------------------------------------------------------------

    def _appliquer_style(self):

        self.setStyleSheet(f"""
            AnimationCreationLegere {{
                background-color: {COULEUR_FOND};
                border-radius: 8px;
            }}
        """)

        self.bandeau_haut.setStyleSheet(f"""
            QWidget {{
                background-color: {COULEUR_BANDEAU_HAUT};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
        """)

        self.bandeau_bas.setStyleSheet(f"""
            QWidget {{
                background-color: {COULEUR_BANDEAU_BAS};
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
        """)

        self.label_haut.setStyleSheet(f"""
            QLabel {{
                color: {COULEUR_TEXTE};
                background: transparent;
                border: none;
            }}
        """)

        self.label_bas.setStyleSheet(f"""
            QLabel {{
                color: {COULEUR_TEXTE_SECONDAIRE};
                background: transparent;
                border: none;
            }}
        """)

        self.label_ratio.setStyleSheet(f"""
            QLabel {{
                color: {COULEUR_RATIO_TEXTE};
                background-color: {COULEUR_RATIO_FOND};
                border-radius: 7px;
                padding-left: 6px;
                padding-right: 6px;
            }}
        """)

    # 4.3 -- API publique : textes --------------------------------------------

    def set_texte_haut(self, texte):

        self.label_haut.setText(str(texte))

    # -------------------------------------------------------------------------

    def set_texte_bas(self, texte):

        self.label_bas.setText(str(texte))

    # 4.4 -- API publique : progression ---------------------------------------

    def set_maximum(self, maximum):

        self._maximum = max(0, int(maximum))

        self._valeur = min(self._valeur, self._maximum)

        self._actualiser_ratio()

    # -------------------------------------------------------------------------

    def set_valeur(self, valeur):

        valeur = max(0, int(valeur))

        if self._maximum > 0:
            self._valeur = min(valeur, self._maximum)
        else:
            self._valeur = 0

        self._actualiser_ratio()

    # -------------------------------------------------------------------------

    def _actualiser_ratio(self):

        self.label_ratio.setText(f"{self._valeur} / {self._maximum}")

    # 4.5 -- Contrôle de l'animation ------------------------------------------

    def demarrer(self):

        self.zone_avion.demarrer()

    # -------------------------------------------------------------------------

    def arreter(self):

        self.zone_avion.arreter()


# 5 -- Test autonome -----------------------------------------------------------


if __name__ == "__main__":

    app = QApplication(sys.argv)

    fenetre = QWidget()
    fenetre.setWindowTitle("Test – Animation légère")
    fenetre.resize(560, 280)

    layout = QVBoxLayout(fenetre)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(16)

    # Widget à tester
    animation = AnimationCreationLegere()

    animation.set_texte_haut("France · Allemagne · Autriche")
    animation.set_texte_bas("Préparation des cartes de voyage")
    animation.set_maximum(24)
    animation.set_valeur(8)

    layout.addWidget(animation)

    # -------------------------------------------------------------------------
    # Contrôles de test
    # -------------------------------------------------------------------------

    groupe = QGroupBox("Paramètres de test")

    layout_groupe = QVBoxLayout(groupe)

    champ_haut = QLineEdit()
    champ_haut.setPlaceholderText("Texte supérieur")

    champ_bas = QLineEdit()
    champ_bas.setPlaceholderText("Texte inférieur")

    spin_maximum = QSpinBox()
    spin_maximum.setRange(0, 10000)
    spin_maximum.setValue(24)

    spin_valeur = QSpinBox()
    spin_valeur.setRange(0, 10000)
    spin_valeur.setValue(8)

    layout_groupe.addWidget(champ_haut)
    layout_groupe.addWidget(champ_bas)
    layout_groupe.addWidget(QLabel("Maximum"))
    layout_groupe.addWidget(spin_maximum)
    layout_groupe.addWidget(QLabel("Valeur"))
    layout_groupe.addWidget(spin_valeur)

    # Connexions
    champ_haut.textChanged.connect(animation.set_texte_haut)
    champ_bas.textChanged.connect(animation.set_texte_bas)

    spin_maximum.valueChanged.connect(animation.set_maximum)
    spin_valeur.valueChanged.connect(animation.set_valeur)

    layout.addWidget(groupe)

    # -------------------------------------------------------------------------
    # Boutons
    # -------------------------------------------------------------------------

    layout_boutons = QHBoxLayout()

    bouton_demarrer = QPushButton("Démarrer")
    bouton_arreter = QPushButton("Arrêter")

    bouton_demarrer.clicked.connect(animation.demarrer)
    bouton_arreter.clicked.connect(animation.arreter)

    layout_boutons.addWidget(bouton_demarrer)
    layout_boutons.addWidget(bouton_arreter)

    layout.addLayout(layout_boutons)

    fenetre.show()

    animation.demarrer()

    sys.exit(app.exec())
