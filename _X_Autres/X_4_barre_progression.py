################################################################################
# Projet de cartes de voyage                                                   #
# _X_Autres/                                                                   #
# X.4 – Visualisation de la barre de progression                               #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os
import random
import sys

sys.path.append(os.getcwd())

from PyQt6.QtCore import (
    QTimer,
    Qt,
)
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from _4_Interface._4_1_Onglets.onglet_1.onglet_1_3_barre_progression import (
    AnimationTrainPublication,
)

# 1 -- Données de test ---------------------------------------------------------


PAYS_TEST = [
    "France",
    "Belgique",
    "Allemagne",
    "Autriche",
    "Tchéquie",
    "Pologne",
    "Hongrie",
    "Croatie",
    "Italie",
    "Suisse",
    "Pays-Bas",
    "Danemark",
]


# 2 -- Démonstration -----------------------------------------------------------


if __name__ == "__main__":

    class FenetreTestTrain(QMainWindow):
        """
        Fenêtre de test de l'animation de publication.

        Les signaux de publication sont envoyés automatiquement avec des
        délais aléatoires afin de tester :

            - les arrivées normales en gare ;
            - les arrêts complets ;
            - les arrivées rapprochées ;
            - les passages en gare sans arrêt ;
            - l'enchaînement de plusieurs signaux.
        """

        def __init__(self):
            super().__init__()

            self.setWindowTitle("Test – Animation du train de publication")

            self.resize(
                1150,
                500,
            )

            # ------------------------------------------------------------------
            # Simulation
            # ------------------------------------------------------------------

            self.pays = list(PAYS_TEST)

            self.n = len(self.pays)

            # Prochain pays à publier.
            self.index_signal = 0

            # Envoi automatique des signaux.
            self.signaux_automatiques = True

            # Générateur indépendant afin de faciliter les tests.
            self.rng = random.Random()

            # Timer à intervalle variable.
            self.timer_signal = QTimer(self)

            self.timer_signal.setSingleShot(True)

            self.timer_signal.timeout.connect(self._envoyer_signal_suivant)

            # ------------------------------------------------------------------
            # Widget central
            # ------------------------------------------------------------------

            widget = QWidget()

            self.setCentralWidget(widget)

            layout = QVBoxLayout(widget)

            layout.setContentsMargins(
                20,
                20,
                20,
                20,
            )

            layout.setSpacing(14)

            # ------------------------------------------------------------------
            # Animation
            # ------------------------------------------------------------------

            self.animation = AnimationTrainPublication(
                n=self.n,
                vitesse=130.0,
                delai_arret=1.0,
            )

            self.animation.setMinimumHeight(320)

            layout.addWidget(
                self.animation,
                stretch=1,
            )

            # ------------------------------------------------------------------
            # Informations sur la simulation
            # ------------------------------------------------------------------

            ligne_infos = QHBoxLayout()

            self.label_progression = QLabel(f"Signal : 0 / {self.n}")

            ligne_infos.addWidget(self.label_progression)

            self.label_pays = QLabel("En attente du premier signal...")

            ligne_infos.addWidget(self.label_pays)

            ligne_infos.addStretch()

            self.label_prochain = QLabel("")

            ligne_infos.addWidget(self.label_prochain)

            layout.addLayout(ligne_infos)

            # ------------------------------------------------------------------
            # Contrôles de vitesse
            # ------------------------------------------------------------------

            controles_vitesse = QHBoxLayout()

            controles_vitesse.addWidget(QLabel("Vitesse :"))

            self.slider_vitesse = QSlider(Qt.Orientation.Horizontal)

            self.slider_vitesse.setRange(
                0,
                350,
            )

            self.slider_vitesse.setValue(
                130,
            )

            self.slider_vitesse.setMinimumWidth(
                300,
            )

            controles_vitesse.addWidget(self.slider_vitesse)

            self.label_valeur = QLabel("130 px/s")

            self.label_valeur.setMinimumWidth(80)

            controles_vitesse.addWidget(self.label_valeur)

            controles_vitesse.addStretch()

            layout.addLayout(controles_vitesse)

            # ------------------------------------------------------------------
            # Contrôles de l'animation
            # ------------------------------------------------------------------

            controles = QHBoxLayout()

            self.bouton_pause = QPushButton("Pause train")

            controles.addWidget(self.bouton_pause)

            self.bouton_reprendre = QPushButton("Reprendre train")

            controles.addWidget(self.bouton_reprendre)

            self.bouton_signal = QPushButton("Envoyer le prochain signal")

            controles.addWidget(self.bouton_signal)

            self.bouton_auto = QPushButton("Arrêter les signaux automatiques")

            controles.addWidget(self.bouton_auto)

            self.bouton_reset = QPushButton("Réinitialiser")

            controles.addWidget(self.bouton_reset)

            controles.addStretch()

            layout.addLayout(controles)

            # ------------------------------------------------------------------
            # Connexions
            # ------------------------------------------------------------------

            self.slider_vitesse.valueChanged.connect(self._changer_vitesse)

            self.bouton_pause.clicked.connect(self.animation.arreter)

            self.bouton_reprendre.clicked.connect(self.animation.demarrer)

            self.bouton_signal.clicked.connect(self._envoyer_signal_suivant)

            self.bouton_auto.clicked.connect(self._basculer_signaux_automatiques)

            self.bouton_reset.clicked.connect(self._reinitialiser)

            # ------------------------------------------------------------------
            # Style de test
            # ------------------------------------------------------------------

            self.setStyleSheet("""
                QMainWindow {
                    background-color: #EAF2F7;
                }

                QLabel {
                    color: #35444D;
                    font-size: 14px;
                }

                QPushButton {
                    padding: 7px 14px;
                    border: 1px solid #B8C8D2;
                    border-radius: 8px;
                    background-color: #F8FBFC;
                    color: #35444D;
                }

                QPushButton:hover {
                    background-color: #FFFFFF;
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

            # ------------------------------------------------------------------
            # Premier signal
            # ------------------------------------------------------------------

            self._planifier_prochain_signal(premier=True)

        # ----------------------------------------------------------------------
        # Vitesse du train
        # ----------------------------------------------------------------------

        def _changer_vitesse(
            self,
            valeur: int,
        ) -> None:
            """Modifie la vitesse de croisière du train."""

            self.animation.definir_vitesse(valeur)

            self.label_valeur.setText(f"{valeur} px/s")

        # ----------------------------------------------------------------------
        # Temporisation aléatoire
        # ----------------------------------------------------------------------

        def _tirer_delai_signal(self) -> int:
            """Tire un délai réaliste entre deux publications."""

            tirage = self.rng.random()

            # 10 % : résultat exceptionnellement rapide.
            if tirage < 0.10:
                return self.rng.randint(
                    1200,
                    3500,
                )

            # 70 % : cas courant.
            if tirage < 0.80:
                return self.rng.randint(
                    5000,
                    12000,
                )

            # 20 % : traitement plus lourd.
            return self.rng.randint(
                12000,
                20000,
            )

        def _planifier_prochain_signal(
            self,
            premier: bool = False,
        ) -> None:
            """Programme le prochain signal automatique."""

            if not self.signaux_automatiques:
                return

            if self.index_signal >= self.n:

                self.label_prochain.setText("Publication terminée")

                return

            if premier:

                delai = 1000

            else:

                delai = self._tirer_delai_signal()

            self.label_prochain.setText(f"Prochain signal dans {delai / 1000:.1f} s")

            self.timer_signal.start(delai)

        # ----------------------------------------------------------------------
        # Envoi des signaux
        # ----------------------------------------------------------------------

        def _envoyer_signal_suivant(self) -> None:
            """Envoie au widget le prochain signal de publication."""

            # Un clic manuel annule le timer actuellement programmé afin
            # d'éviter qu'un second signal parte quelques millisecondes après.
            if self.timer_signal.isActive():
                self.timer_signal.stop()

            if self.index_signal >= self.n:

                self.label_prochain.setText("Tous les signaux ont été envoyés")

                return

            i = self.index_signal + 1

            nom_pays = self.pays[self.index_signal]

            # Signal envoyé à l'animation.
            self.animation.recevoir_signal(
                i=i,
                nom_pays=nom_pays,
            )

            self.index_signal += 1

            # Informations de test.
            self.label_progression.setText(f"Signal : {i} / {self.n}")

            self.label_pays.setText(f"Carte publiée : {nom_pays}")

            # Programmation du suivant.
            self._planifier_prochain_signal()

        # ----------------------------------------------------------------------
        # Mode automatique
        # ----------------------------------------------------------------------

        def _basculer_signaux_automatiques(
            self,
        ) -> None:
            """Active ou désactive l'envoi automatique des signaux."""

            self.signaux_automatiques = not self.signaux_automatiques

            if self.signaux_automatiques:

                self.bouton_auto.setText("Arrêter les signaux automatiques")

                self._planifier_prochain_signal()

            else:

                self.timer_signal.stop()

                self.bouton_auto.setText("Reprendre les signaux automatiques")

                self.label_prochain.setText("Signaux automatiques en pause")

        # ----------------------------------------------------------------------
        # Réinitialisation
        # ----------------------------------------------------------------------

        def _reinitialiser(
            self,
        ) -> None:
            """Recommence entièrement la simulation."""

            self.timer_signal.stop()

            self.index_signal = 0

            self.animation.reinitialiser()

            self.label_progression.setText(f"Signal : 0 / {self.n}")

            self.label_pays.setText("En attente du premier signal...")

            if self.signaux_automatiques:

                self._planifier_prochain_signal(premier=True)

            else:

                self.label_prochain.setText("Signaux automatiques en pause")

    # 3 -- Lancement -----------------------------------------------------------

    app = QApplication(sys.argv)

    fenetre = FenetreTestTrain()
    fenetre.show()

    sys.exit(app.exec())
