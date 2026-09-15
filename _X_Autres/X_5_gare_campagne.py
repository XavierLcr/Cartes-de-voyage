################################################################################
# Projet de cartes de voyage                                                   #
# _X_Autres/                                                                   #
# X.5 – Visualisation de la gare de campagne                                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math
import os
import sys

sys.path.append(os.getcwd())

from PyQt6.QtCore import (
    QElapsedTimer,
    QRectF,
    Qt,
    QTimer,
)
from PyQt6.QtGui import (
    QColor,
    QPainter,
)
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from _4_Interface._4_3_Icones._4_3_50_vieux_train import TrainRegional
from _4_Interface._4_3_Icones._4_3_51_rails import Rails
from _4_Interface._4_3_Icones._4_3_52_gare_campagne import GareCampagne

# 1 -- Widget de visualisation -------------------------------------------------


class VisualisationGareCampagne(QWidget):
    """Affiche le train, les rails et une petite gare de campagne."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # ----------------------------------------------------------------------
        # Objets graphiques
        # ----------------------------------------------------------------------

        self.train = TrainRegional(
            avec_motrice=True,
            nb_fenetres_wagon=4,
        )

        self.rails = Rails(
            espacement_traverses=46.0,
            ballast=True,
            boulons=True,
            texture_bois=True,
        )

        self.gare = GareCampagne(
            avec_maison=True,
            maison_a_gauche=True,
        )

        # ----------------------------------------------------------------------
        # Paramètres de la gare
        # ----------------------------------------------------------------------

        self.nom_pays = "Autriche"
        self.i = 7
        self.n = 18

        self.ouverture_barriere = 0.0

        # ----------------------------------------------------------------------
        # Animation du train
        # ----------------------------------------------------------------------

        self.animation_active = True
        self.vitesse = 110.0
        self.distance_parcourue = 0.0

        self.horloge = QElapsedTimer()
        self.horloge.start()

        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._actualiser_animation)
        self.timer.start()

        self.setMinimumHeight(320)

    # --------------------------------------------------------------------------
    # Paramètres
    # --------------------------------------------------------------------------

    def definir_nom_pays(self, nom: str) -> None:
        """Modifie le nom affiché sur le panneau de gare."""
        self.nom_pays = nom.strip() or "..."
        self.update()

    def definir_progression(
        self,
        i: int,
        n: int,
    ) -> None:
        """Modifie la progression affichée sur la borne."""
        self.i = i
        self.n = n
        self.update()

    def definir_ouverture_barriere(
        self,
        ouverture: float,
    ) -> None:
        """Définit l'ouverture de la barrière entre 0 et 1."""
        self.ouverture_barriere = max(
            0.0,
            min(1.0, ouverture),
        )
        self.update()

    def definir_maison(
        self,
        visible: bool,
    ) -> None:
        """Affiche ou masque la maisonnette."""
        self.gare.avec_maison = visible
        self.update()

    def definir_cote_maison(
        self,
        gauche: bool,
    ) -> None:
        """Place la maisonnette à gauche ou à droite."""
        self.gare.maison_a_gauche = gauche
        self.update()

    def definir_animation(
        self,
        active: bool,
    ) -> None:
        """Active ou désactive le mouvement du train."""
        self.animation_active = active
        self.horloge.restart()
        self.update()

    def definir_vitesse(
        self,
        vitesse: float,
    ) -> None:
        """Modifie la vitesse visuelle du train."""
        self.vitesse = max(0.0, float(vitesse))

    # --------------------------------------------------------------------------
    # Animation
    # --------------------------------------------------------------------------

    def _actualiser_animation(self) -> None:
        """Actualise le défilement des rails et la rotation des roues."""
        temps_ms = self.horloge.restart()

        if not self.animation_active:
            return

        temps_s = min(
            temps_ms / 1000.0,
            0.050,
        )

        self.distance_parcourue += self.vitesse * temps_s

        if self.distance_parcourue > 1_000_000:
            self.distance_parcourue %= 10_000

        self.update()

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    def _rect_scene(self) -> QRectF:
        """Zone complète de dessin."""
        return QRectF(
            0,
            0,
            self.width(),
            self.height(),
        )

    def _rect_rails(self) -> QRectF:
        """Zone occupée par la voie ferrée."""
        hauteur = max(
            65.0,
            min(
                95.0,
                self.height() * 0.25,
            ),
        )

        return QRectF(
            0,
            self.height() * 0.70,
            self.width(),
            hauteur,
        )

    def _rect_gare(
        self,
        rect_scene: QRectF,
    ) -> QRectF:
        """Zone utilisée par la petite gare."""
        largeur = min(
            rect_scene.width() * 0.58,
            rect_scene.height() * 1.85,
        )

        return QRectF(
            rect_scene.right() - largeur - rect_scene.width() * 0.025,
            rect_scene.top(),
            largeur,
            rect_scene.height(),
        )

    def _rect_train(
        self,
        rect_rails: QRectF,
    ) -> QRectF:
        """Positionne le train avec ses roues sur les rails."""
        largeur_ref = self.train.largeur_recommandee()
        hauteur_ref = 140.0

        largeur_max = self.width() * 0.60
        hauteur_max = self.height() * 0.53

        echelle = min(
            largeur_max / largeur_ref,
            hauteur_max / hauteur_ref,
        )

        largeur = largeur_ref * echelle
        hauteur = hauteur_ref * echelle

        y_rail = self.rails.y_roulement(rect_rails)

        bas_train = y_rail + hauteur * 0.03

        haut_train = bas_train - hauteur

        # Train volontairement un peu décalé vers la gauche.
        centre_x = self.width() * 0.39

        return QRectF(
            centre_x - largeur / 2,
            haut_train,
            largeur,
            hauteur,
        )

    def _phase_roues(
        self,
        rect_train: QRectF,
    ) -> float:
        """Calcule la phase de rotation des roues."""
        rayon = rect_train.height() * 0.11

        if rayon <= 0:
            return 0.0

        circonference = 2 * math.pi * rayon

        return (self.distance_parcourue / circonference) % 1.0

    # --------------------------------------------------------------------------
    # Dessin
    # --------------------------------------------------------------------------

    def paintEvent(self, event) -> None:
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        # Fond volontairement simple pour le moment.
        painter.fillRect(
            self.rect(),
            QColor("#DDECF2"),
        )

        rect_scene = self._rect_scene()
        rect_rails = self._rect_rails()
        rect_gare = self._rect_gare(rect_scene)
        rect_train = self._rect_train(rect_rails)

        y_rail = self.rails.y_roulement(rect_rails)

        # ------------------------------------------------------------------
        # Gare derrière le train
        # ------------------------------------------------------------------

        self.gare.peindre_arriere(
            painter=painter,
            rect=rect_gare,
            nom_pays=self.nom_pays,
            i=self.i,
            n=self.n,
            y_rail=y_rail,
        )

        # ------------------------------------------------------------------
        # Rails
        # ------------------------------------------------------------------

        decalage_rails = (
            self.distance_parcourue
            if self.animation_active
            else self.distance_parcourue
        )

        self.rails.peindre(
            painter,
            rect_rails,
            decalage=decalage_rails,
        )

        # ------------------------------------------------------------------
        # Train
        # ------------------------------------------------------------------

        phase_roues = self._phase_roues(rect_train)

        self.train.peindre(
            painter,
            rect_train,
            sens=1,
            phase_roues=phase_roues,
        )

        # ------------------------------------------------------------------
        # Éléments de gare devant le train
        # ------------------------------------------------------------------

        self.gare.peindre_avant(
            painter=painter,
            rect=rect_gare,
            ouverture_barriere=self.ouverture_barriere,
            y_rail=y_rail,
        )

        painter.end()


# 2 -- Fenêtre de test ---------------------------------------------------------


class FenetreVisualisationGare(QMainWindow):
    """Fenêtre permettant de modifier les paramètres de la gare."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("X.5 – Visualisation de la gare de campagne")

        self.resize(
            1200,
            560,
        )

        # ----------------------------------------------------------------------
        # Widget principal
        # ----------------------------------------------------------------------

        widget = QWidget()
        self.setCentralWidget(widget)

        layout = QVBoxLayout(widget)

        layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )

        layout.setSpacing(14)

        # ----------------------------------------------------------------------
        # Scène
        # ----------------------------------------------------------------------

        self.visualisation = VisualisationGareCampagne()

        layout.addWidget(
            self.visualisation,
            stretch=1,
        )

        # ----------------------------------------------------------------------
        # Ligne 1 : gare
        # ----------------------------------------------------------------------

        ligne_gare = QHBoxLayout()

        ligne_gare.addWidget(QLabel("Pays :"))

        self.nom_pays = QLineEdit("Autriche")

        self.nom_pays.setMaximumWidth(180)

        ligne_gare.addWidget(self.nom_pays)

        ligne_gare.addSpacing(15)

        ligne_gare.addWidget(QLabel("Progression :"))

        self.spin_i = QSpinBox()
        self.spin_i.setRange(0, 100)
        self.spin_i.setValue(7)

        self.spin_n = QSpinBox()
        self.spin_n.setRange(1, 100)
        self.spin_n.setValue(18)

        ligne_gare.addWidget(self.spin_i)

        ligne_gare.addWidget(QLabel("/"))

        ligne_gare.addWidget(self.spin_n)

        ligne_gare.addSpacing(20)

        self.checkbox_maison = QCheckBox("Maisonnette")
        self.checkbox_maison.setChecked(True)

        ligne_gare.addWidget(self.checkbox_maison)

        self.checkbox_gauche = QCheckBox("Maison à gauche")
        self.checkbox_gauche.setChecked(True)

        ligne_gare.addWidget(self.checkbox_gauche)

        ligne_gare.addStretch()

        layout.addLayout(ligne_gare)

        self.checkbox_lampe = QCheckBox("Lampadaire allumé")

        self.checkbox_lampe.setChecked(False)

        ligne_gare.addWidget(self.checkbox_lampe)

        self.checkbox_lampe.toggled.connect(self._modifier_lampadaire)

        # ----------------------------------------------------------------------
        # Ligne 2 : animation
        # ----------------------------------------------------------------------

        ligne_animation = QHBoxLayout()

        ligne_animation.addWidget(QLabel("Barrière :"))

        self.slider_barriere = QSlider(Qt.Orientation.Horizontal)

        self.slider_barriere.setRange(
            0,
            100,
        )

        self.slider_barriere.setValue(0)

        self.slider_barriere.setMinimumWidth(230)

        ligne_animation.addWidget(self.slider_barriere)

        self.label_barriere = QLabel("0 %")
        self.label_barriere.setMinimumWidth(45)

        ligne_animation.addWidget(self.label_barriere)

        ligne_animation.addSpacing(25)

        self.checkbox_animation = QCheckBox("Train en mouvement")

        self.checkbox_animation.setChecked(True)

        ligne_animation.addWidget(self.checkbox_animation)

        ligne_animation.addSpacing(15)

        ligne_animation.addWidget(QLabel("Vitesse :"))

        self.slider_vitesse = QSlider(Qt.Orientation.Horizontal)

        self.slider_vitesse.setRange(
            0,
            300,
        )

        self.slider_vitesse.setValue(
            110,
        )

        self.slider_vitesse.setMinimumWidth(220)

        ligne_animation.addWidget(self.slider_vitesse)

        self.label_vitesse = QLabel("110 px/s")

        self.label_vitesse.setMinimumWidth(80)

        ligne_animation.addWidget(self.label_vitesse)

        ligne_animation.addStretch()

        layout.addLayout(ligne_animation)

        # ----------------------------------------------------------------------
        # Connexions
        # ----------------------------------------------------------------------

        self.nom_pays.textChanged.connect(self.visualisation.definir_nom_pays)

        self.spin_i.valueChanged.connect(self._modifier_progression)

        self.spin_n.valueChanged.connect(self._modifier_progression)

        self.checkbox_maison.toggled.connect(self.visualisation.definir_maison)

        self.checkbox_gauche.toggled.connect(self.visualisation.definir_cote_maison)

        self.slider_barriere.valueChanged.connect(self._modifier_barriere)

        self.checkbox_animation.toggled.connect(self.visualisation.definir_animation)

        self.slider_vitesse.valueChanged.connect(self._modifier_vitesse)

        # ----------------------------------------------------------------------
        # Style léger
        # ----------------------------------------------------------------------

        self.setStyleSheet("""
            QMainWindow {
                background-color: #EEF3F5;
            }

            QLabel,
            QCheckBox {
                color: #35424A;
                font-size: 13px;
            }

            QLineEdit,
            QSpinBox {
                padding: 5px 7px;
                border: 1px solid #B9C8D0;
                border-radius: 6px;
                background-color: white;
                color: #35424A;
            }

            QSlider::groove:horizontal {
                height: 5px;
                border-radius: 2px;
                background-color: #CBD7DD;
            }

            QSlider::handle:horizontal {
                width: 15px;
                margin: -5px 0;
                border-radius: 7px;
                background-color: #6C8795;
            }
            """)

    # --------------------------------------------------------------------------
    # Slots
    # --------------------------------------------------------------------------

    def _modifier_progression(self) -> None:
        """Met à jour la borne de progression."""
        n = self.spin_n.value()
        i = min(
            self.spin_i.value(),
            n,
        )

        if self.spin_i.value() != i:
            self.spin_i.setValue(i)

        self.visualisation.definir_progression(
            i,
            n,
        )

    def _modifier_barriere(
        self,
        valeur: int,
    ) -> None:
        """Modifie manuellement l'ouverture de la barrière."""
        self.label_barriere.setText(f"{valeur} %")

        self.visualisation.definir_ouverture_barriere(valeur / 100.0)

    def _modifier_vitesse(
        self,
        valeur: int,
    ) -> None:
        """Modifie la vitesse du train."""
        self.label_vitesse.setText(f"{valeur} px/s")

        self.visualisation.definir_vitesse(valeur)

    def _modifier_lampadaire(
        self,
        valeur: bool,
    ) -> None:

        self.visualisation.gare.lampadaire_allume = valeur
        self.visualisation.update()


# 3 -- Lancement ---------------------------------------------------------------


if __name__ == "__main__":

    app = QApplication(sys.argv)

    fenetre = FenetreVisualisationGare()
    fenetre.show()

    sys.exit(app.exec())
