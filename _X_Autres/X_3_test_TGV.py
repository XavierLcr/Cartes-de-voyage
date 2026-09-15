################################################################################
# Projet de cartes de voyage                                                   #
# _X_Autres/                                                                   #
# X.3 – Visualisation du TGV                                                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys, random

sys.path.append(os.getcwd())

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from _4_Interface._4_3_Icones._4_3_49_TGV._4_3_49_3_TGV import TGV

# 1 -- Zone d'aperçu -----------------------------------------------------------


class ApercuTGV(QWidget):

    def __init__(self):
        super().__init__()

        self.nb_pays = 17
        self.nb_wagons = 4
        self.duplex = False
        self.halo_fenetres = True

        self.perspective = 0.07

        # Fenêtres
        self.couleur_fenetres = "#9A0EE6"

        # Halo des fenêtres
        self.halo_fenetres = False
        self.intensite_halo = 0.0

        self.pays_allumes = self._generer_etats()

        self.setMinimumHeight(480)

    # --------------------------------------------------------------------------
    # États
    # --------------------------------------------------------------------------

    def _generer_etats(self):

        return [random.random() > 0.38 for _ in range(self.nb_pays)]

    def regenerer_etats(self):

        self.pays_allumes = self._generer_etats()
        self.update()

    # --------------------------------------------------------------------------
    # Dessin
    # --------------------------------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fond
        painter.fillRect(
            self.rect(),
            QColor("#DDE3E7"),
        )

        # ----------------------------------------------------------------------
        # Sécurité sur le nombre de wagons
        # ----------------------------------------------------------------------

        nb_wagons = min(
            self.nb_wagons,
            self.nb_pays,
        )

        # ----------------------------------------------------------------------
        # Création du TGV
        # ----------------------------------------------------------------------

        tgv = TGV(
            nb_pays=self.nb_pays,
            nb_wagons=nb_wagons,
            duplex=self.duplex,
            couleur_fenetres=self.couleur_fenetres,
            pays_allumes=self.pays_allumes,
            halo_fenetres=self.halo_fenetres,
        )

        # ----------------------------------------------------------------------
        # Zone disponible
        # ----------------------------------------------------------------------

        marge_x = self.width() * 0.035
        marge_y = self.height() * 0.12

        rect_tgv = QRectF(
            marge_x,
            marge_y,
            self.width() - 2 * marge_x,
            self.height() - 2 * marge_y,
        )

        # ----------------------------------------------------------------------
        # Dessin
        # ----------------------------------------------------------------------

        tgv.peindre(
            painter=painter,
            rect=rect_tgv,
            perspective=self.perspective,
            adapter=True,
        )

        # ----------------------------------------------------------------------
        # Informations
        # ----------------------------------------------------------------------

        painter.setPen(QColor("#24292C"))

        texte = (
            f"{self.nb_pays} pays  |  "
            f"{nb_wagons} wagons  |  "
            f"répartition : {tgv.repartition}"
        )

        painter.drawText(
            15,
            25,
            texte,
        )


# 2 -- Fenêtre principale ------------------------------------------------------


class FenetreTest(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Test – TGV complet")

        self.resize(
            1450,
            700,
        )

        layout_principal = QVBoxLayout(self)

        # ----------------------------------------------------------------------
        # Aperçu
        # ----------------------------------------------------------------------

        self.apercu = ApercuTGV()

        layout_principal.addWidget(
            self.apercu,
            stretch=1,
        )

        # ----------------------------------------------------------------------
        # Première ligne de contrôles
        # ----------------------------------------------------------------------

        controles_1 = QHBoxLayout()

        # Nombre de pays
        controles_1.addWidget(QLabel("Pays"))

        self.spin_pays = QSpinBox()

        self.spin_pays.setRange(
            1,
            70,
        )

        self.spin_pays.setValue(self.apercu.nb_pays)

        self.spin_pays.valueChanged.connect(self._changer_nb_pays)

        controles_1.addWidget(self.spin_pays)

        # Nombre de wagons
        controles_1.addSpacing(15)

        controles_1.addWidget(QLabel("Wagons"))

        self.spin_wagons = QSpinBox()

        self.spin_wagons.setRange(
            1,
            10,
        )

        self.spin_wagons.setValue(self.apercu.nb_wagons)

        self.spin_wagons.valueChanged.connect(self._changer_nb_wagons)

        controles_1.addWidget(self.spin_wagons)

        # Duplex
        controles_1.addSpacing(15)

        self.check_duplex = QCheckBox("Duplex")

        self.check_duplex.setChecked(self.apercu.duplex)

        self.check_duplex.toggled.connect(self._changer_duplex)

        controles_1.addWidget(self.check_duplex)

        # Nouveaux états
        controles_1.addSpacing(20)

        self.bouton_etats = QPushButton("Nouveaux états")

        self.bouton_etats.clicked.connect(self.apercu.regenerer_etats)

        controles_1.addWidget(self.bouton_etats)

        # Tout allumer
        self.check_tout_allume = QCheckBox("Tout allumé")

        self.check_tout_allume.toggled.connect(self._changer_tout_allume)

        controles_1.addWidget(self.check_tout_allume)

        controles_1.addStretch()

        layout_principal.addLayout(controles_1)

        # ----------------------------------------------------------------------
        # Deuxième ligne : perspective + couleur des fenêtres
        # ----------------------------------------------------------------------

        controles_2 = QHBoxLayout()

        # Perspective
        controles_2.addWidget(QLabel("Perspective"))

        self.slider_perspective = QSlider(Qt.Orientation.Horizontal)

        self.slider_perspective.setRange(
            0,
            18,
        )

        self.slider_perspective.setValue(7)

        self.slider_perspective.setMinimumWidth(250)

        self.slider_perspective.valueChanged.connect(self._changer_perspective)

        controles_2.addWidget(self.slider_perspective)

        self.label_perspective = QLabel("7 %")

        controles_2.addWidget(self.label_perspective)

        # Couleur des fenêtres
        controles_2.addSpacing(30)

        controles_2.addWidget(QLabel("Fenêtres"))

        self.bouton_couleur = QPushButton()

        self.bouton_couleur.setFixedSize(
            36,
            24,
        )

        self.bouton_couleur.clicked.connect(self._choisir_couleur_fenetres)

        controles_2.addWidget(self.bouton_couleur)

        self.label_couleur = QLabel(self.apercu.couleur_fenetres)

        controles_2.addWidget(self.label_couleur)

        self._actualiser_bouton_couleur()

        # Halo des fenêtres
        controles_2.addSpacing(25)

        self.check_halo = QCheckBox("Halo fenêtres")
        self.check_halo.setChecked(self.apercu.halo_fenetres)
        self.check_halo.toggled.connect(self._changer_halo)

        controles_2.addWidget(self.check_halo)

        controles_2.addStretch()

        layout_principal.addLayout(controles_2)

    # --------------------------------------------------------------------------
    # Contrôles
    # --------------------------------------------------------------------------

    def _changer_nb_pays(
        self,
        valeur,
    ):

        self.apercu.nb_pays = valeur

        # Le nombre de wagons ne peut pas dépasser le nombre de pays
        self.spin_wagons.setMaximum(max(valeur, 1))

        if self.spin_wagons.value() > valeur:
            self.spin_wagons.setValue(valeur)

        self.apercu.pays_allumes = self.apercu._generer_etats()

        self.apercu.update()

    def _changer_nb_wagons(
        self,
        valeur,
    ):

        self.apercu.nb_wagons = valeur
        self.apercu.update()

    def _changer_duplex(
        self,
        valeur,
    ):

        self.apercu.duplex = valeur
        self.apercu.update()

    def _changer_perspective(
        self,
        valeur,
    ):

        self.apercu.perspective = valeur / 100

        self.label_perspective.setText(f"{valeur} %")

        self.apercu.update()

    def _changer_tout_allume(
        self,
        valeur,
    ):

        if valeur:

            self.apercu.pays_allumes = [True for _ in range(self.apercu.nb_pays)]

        else:

            self.apercu.pays_allumes = self.apercu._generer_etats()

        self.apercu.update()

    # --------------------------------------------------------------------------
    # Couleur des fenêtres
    # --------------------------------------------------------------------------

    def _choisir_couleur_fenetres(self):

        couleur_initiale = QColor(self.apercu.couleur_fenetres)

        couleur = QColorDialog.getColor(
            couleur_initiale,
            self,
            "Couleur des fenêtres",
        )

        if not couleur.isValid():
            return

        self.apercu.couleur_fenetres = couleur.name()

        self.label_couleur.setText(couleur.name().upper())

        self._actualiser_bouton_couleur()

        self.apercu.update()

    def _actualiser_bouton_couleur(self):

        couleur = self.apercu.couleur_fenetres

        self.bouton_couleur.setStyleSheet(f"""
            QPushButton {{
                background-color: {couleur};
                border: 1px solid #666666;
                border-radius: 5px;
            }}

            QPushButton:hover {{
                border: 2px solid #333333;
            }}
            """)

    # --------------------------------------------------------------------------
    # Halo des fenêtres
    # --------------------------------------------------------------------------

    def _changer_halo(
        self,
        valeur,
    ):

        self.apercu.halo_fenetres = valeur
        self.apercu.update()


# 3 -- Lancement ---------------------------------------------------------------


if __name__ == "__main__":

    app = QApplication(sys.argv)

    fenetre = FenetreTest()
    fenetre.show()

    sys.exit(app.exec())
