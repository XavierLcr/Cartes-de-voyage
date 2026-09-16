################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1.3 – Animation de publication des cartes                             #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math
import random
import time

from collections import deque

from PyQt6.QtCore import QElapsedTimer, QRectF, QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QWidget, QPushButton

from _4_Interface._4_3_Icones._4_3_50_vieux_train import TrainRegional
from _4_Interface._4_3_Icones._4_3_51_rails import Rails
from _4_Interface._4_3_Icones._4_3_52_gare_campagne import GareCampagne
from _4_Interface._4_3_Icones._4_3_53_campagne import PaysageCampagne
from _4_Interface._4_3_Icones._4_3_54_gare_ancienne import GareAncienne
from _4_Interface._4_3_Icones._4_3_55_foret import PaysageForet
from _4_Interface._4_3_Icones._4_3_56_gare_depart import GareDepartArrivee
from _4_Interface._4_3_Icones._4_3_57_montagnes_neige import PaysageMontagneEnneigee
from _4_Interface._4_3_Icones._4_3_58_gare_moderne import GareModerne

# 1 -- Génération des gares et paysages ---------------------------------------


### Gares ---------------------------------------------------------------------


POIDS_GARES = {
    "campagne": 0.4,
    "ancienne": 0.3,
    "moderne": 0.3,
}


def generer_gares(
    n: int,
    graine: int = 24,
):
    """
    Génère les `n + 1` gares de l'animation.

    Organisation :
        - gares[0] : gare de départ ;
        - gares[1] à gares[n - 1] : gares intermédiaires ;
        - gares[n] : gare d'arrivée.
    """

    rng = random.Random(graine)

    # ----------------------------------------------------------------------
    # Gare de départ
    # ----------------------------------------------------------------------

    gares = [
        GareDepartArrivee(
            sens=1,
            lampes_allumees=True,
            etat_feu="rouge",
        )
    ]

    # ----------------------------------------------------------------------
    # Gares intermédiaires
    # ----------------------------------------------------------------------

    types_gares = list(POIDS_GARES)
    poids_gares = list(POIDS_GARES.values())

    for _ in range(max(0, n - 1)):

        type_gare = rng.choices(
            types_gares,
            weights=poids_gares,
            k=1,
        )[0]

        if type_gare == "campagne":

            gare = GareCampagne(
                avec_maison=rng.random() < 0.7,
                maison_a_gauche=rng.choice((True, False)),
                lampadaire_allume=False,
            )

        elif type_gare == "ancienne":

            gare = GareAncienne(
                lampes_allumees=True,
                etat_feu="rouge",
            )

        elif type_gare == "moderne":

            gare = GareModerne(
                lampes_allumees=True,
                etat_feu="rouge",
            )

        gares.append(gare)

    # ----------------------------------------------------------------------
    # Gare d'arrivée
    # ----------------------------------------------------------------------

    gares.append(
        GareDepartArrivee(
            sens=-1,
            lampes_allumees=True,
            etat_feu="rouge",
        )
    )

    return gares


### Paysages ------------------------------------------------------------------


PAYSAGES_DISPONIBLES = {
    "campagne": {
        "poids": 1.0,
        "fabrique": lambda graine: PaysageCampagne(
            graine=graine,
        ),
    },
    "foret": {
        "poids": 1.0,
        "fabrique": lambda graine: PaysageForet(
            graine=graine,
        ),
    },
    "montagnes": {
        "poids": 1.0,
        "fabrique": lambda graine: PaysageMontagneEnneigee(
            graine=graine, avec_brume=True
        ),
    },
}


def _tirer_paysage(
    rng: random.Random,
    graine: int,
    type_precedent: str | None = None,
):
    """
    Tire un nouveau paysage parmi ceux enregistrés.

    Si plusieurs types existent, évite si possible de reprendre immédiatement
    le même type afin qu'un changement de décor soit réellement perceptible.
    """

    types = list(PAYSAGES_DISPONIBLES)

    types_valides = [
        type_paysage for type_paysage in types if type_paysage != type_precedent
    ]

    if not types_valides:
        types_valides = types

    poids = [
        PAYSAGES_DISPONIBLES[type_paysage]["poids"] for type_paysage in types_valides
    ]

    type_paysage = rng.choices(
        population=types_valides,
        weights=poids,
        k=1,
    )[0]

    paysage = PAYSAGES_DISPONIBLES[type_paysage]["fabrique"](graine)

    return type_paysage, paysage


def generer_paysages(
    gares: list,
    graine: int = 124,
) -> list:
    """
    Génère les paysages des trajets.

    Avec `n + 1` gares, il existe exactement `n` trajets :

        gare départ -> gare 1
        gare 1      -> gare 2
        ...
        gare n - 1  -> gare arrivée

    Il faut donc `len(gares) - 1` paysages.

    Une gare intermédiaire ne change le paysage suivant que si son attribut
    `masque_paysage` vaut True. Une petite gare de campagne conserve ainsi
    exactement le même objet paysage.
    """

    n_trajets = max(
        0,
        len(gares) - 1,
    )

    if n_trajets == 0:
        return []

    rng = random.Random(graine)

    paysages = []

    # ----------------------------------------------------------------------
    # Premier trajet : départ -> pays 1
    # ----------------------------------------------------------------------

    type_courant, paysage_courant = _tirer_paysage(
        rng=rng,
        graine=graine,
    )

    paysages.append(paysage_courant)

    # ----------------------------------------------------------------------
    # Trajets suivants
    # ----------------------------------------------------------------------

    # La gare d'indice i sépare :
    #
    #     paysages[i - 1] -> gare[i] -> paysages[i]
    #
    # La gare finale n'a aucun paysage après elle, donc elle n'est pas
    # parcourue ici.
    for i in range(
        1,
        n_trajets,
    ):

        gare = gares[i]

        if getattr(
            gare,
            "masque_paysage",
            False,
        ):

            type_courant, paysage_courant = _tirer_paysage(
                rng=rng,
                graine=graine + i * 37,
                type_precedent=type_courant,
            )

        paysages.append(paysage_courant)

    return paysages


# 2 -- Classe d'animation ------------------------------------------------------


class AnimationTrainPublication(QWidget):
    """
    Animation affichée pendant la publication des cartes.

    Déroulement
    -----------
    Au lancement :
        - le train est déjà dans la gare de départ ;
        - le feu est rouge ;
        - après quelques secondes, le feu passe au vert ;
        - le train quitte la gare.

    Ensuite, chaque appel à :

        recevoir_signal(i, nom_pays)

    déclenche l'arrivée de la gare correspondant au pays `i`.

    Si les résultats arrivent trop rapidement, les gares intermédiaires peuvent
    être traversées sans arrêt et le train accélère pour rattraper son retard.

    La gare `n` est toujours la gare d'arrivée :
        - elle ne peut jamais être traversée ;
        - le train s'y immobilise ;
        - l'animation s'arrête définitivement en conservant la scène affichée.
    """

    retour_parametres = pyqtSignal()

    def __init__(
        self,
        n: int,
        parent=None,
        vitesse: float = 130.0,
        avec_motrice: bool = True,
        anime: bool = True,
        delai_arret: float = 2.0,
    ):
        super().__init__(parent)

        self.n = max(
            1,
            int(n),
        )

        # ------------------------------------------------------------------
        # Train
        # ------------------------------------------------------------------

        self.train = TrainRegional(
            avec_motrice=avec_motrice,
            nb_fenetres_wagon=4,
            couleur_caisse="#7A2032",
            couleur_bandeau="#E6DDCF",
            couleur_toit="#58636B",
            couleur_bas="#2A3035",
            couleur_bois="#8A6445",
            couleur_filet="#C9A86A",
        )

        # ------------------------------------------------------------------
        # Rails
        # ------------------------------------------------------------------

        self.rails = Rails(
            couleur_rail="#515A60",
            couleur_traverse="#70513A",
            couleur_ballast="#A6A7A3",
            espacement_traverses=46.0,
            ballast=True,
            boulons=True,
            texture_bois=True,
        )

        # ------------------------------------------------------------------
        # Gares et paysages
        # ------------------------------------------------------------------

        self.gares = generer_gares(self.n)

        self.paysages = generer_paysages(gares=self.gares)

        self._index_paysage = 0

        self._paysage_courant = self.paysages[0]

        self._paysage_suivant = None

        self._fondu_paysage = 0.0

        # ------------------------------------------------------------------
        # Animation générale
        # ------------------------------------------------------------------

        self.vitesse = max(
            0.0,
            float(vitesse),
        )

        # Le train commence à l'arrêt.
        self.vitesse_courante = 0.0

        self.distance_parcourue = 0.0

        self._anime = anime

        self._horloge = QElapsedTimer()
        self._horloge.start()

        self._timer = QTimer(self)
        self._timer.setInterval(33)

        self._timer.timeout.connect(self._actualiser_animation)

        if self._anime:
            self._timer.start()

        # ------------------------------------------------------------------
        # Signaux reçus
        # ------------------------------------------------------------------

        # Chaque élément vaut :
        #
        #     (i, nom_pays, signal_rapide)
        #
        self._file_signaux = deque()

        self._dernier_signal = None

        self.delai_arret = max(
            0.0,
            float(delai_arret),
        )

        # ------------------------------------------------------------------
        # Gare active
        # ------------------------------------------------------------------

        # Au lancement, la gare de départ est déjà présente.
        self._gare_active = self.gares[0]
        self._index_gare_active = 0

        self._i_actuel = 0
        self._nom_pays_actuel = None

        self._x_gare = 0.0
        self._x_gare_depart = 0.0

        # La vraie taille du widget n'est pas encore forcément connue dans
        # __init__. La gare sera centrée sur le train à la première frame.
        self._gare_depart_positionnee = False

        self._passage_sans_arret = False

        # États :
        #
        #     depart_attente
        #     depart_feu_vert
        #     depart_initial
        #
        #     trajet
        #     approche
        #     arret
        #     passage
        #     depart_gare
        #
        #     arrivee
        #     termine
        #
        self._etat = "depart_attente"

        self._temps_etat = 0.0

        # ------------------------------------------------------------------
        # Gare de départ
        # ------------------------------------------------------------------

        self.duree_attente_depart = 2.3
        self.duree_feu_vert_depart = 0.7

        self._definir_feu_gare("rouge")

        # ------------------------------------------------------------------
        # Arrêts intermédiaires
        # ------------------------------------------------------------------

        self._ouverture_barriere = 0.0

        self.duree_attente_gare = 0.55
        self.duree_ouverture_barriere = 0.75

        # ------------------------------------------------------------------
        # Transition de paysage
        # ------------------------------------------------------------------

        self.duree_transition_paysage = 0.90

        # ------------------------------------------------------------------
        # Affichage
        # ------------------------------------------------------------------

        self.setMinimumHeight(160)

        # ------------------------------------------------------------------
        # Bouton de fin
        # ------------------------------------------------------------------

        self.bouton_retour = QPushButton("Revenir aux paramètres de carte", self)
        self.bouton_retour.setStyleSheet("""
            QPushButton {
                background-color: rgba(232, 222, 204, 235);
                color: #353B3E;

                border: 2px solid #647076;
                border-radius: 7px;

                padding: 8px 18px;

                font-weight: 600;
            }

            QPushButton:hover {
                background-color: rgba(244, 238, 226, 245);
                border-color: #495257;
            }

            QPushButton:pressed {
                background-color: rgba(210, 200, 182, 245);
            }
        """)

        self.bouton_retour.setVisible(False)
        self.bouton_retour.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bouton_retour.clicked.connect(self.retour_parametres.emit)

    # --------------------------------------------------------------------------
    # Utilitaires de gare
    # --------------------------------------------------------------------------

    def _definir_feu_gare(
        self,
        etat: str,
    ) -> None:
        """Modifie le feu si la gare active en possède un."""

        if self._gare_active is None:
            return

        if hasattr(
            self._gare_active,
            "etat_feu",
        ):
            self._gare_active.etat_feu = etat

    # --------------------------------------------------------------------------
    # Réception des signaux
    # --------------------------------------------------------------------------

    def recevoir_signal(
        self,
        i: int,
        nom_pays: str,
    ) -> None:
        """
        Signale qu'une nouvelle carte vient d'être publiée.

        `i` doit être compris entre 1 et `n`.
        """

        if not 1 <= i <= self.n:
            return

        maintenant = time.monotonic()

        signal_rapide = (
            self._dernier_signal is not None
            and (maintenant - self._dernier_signal) < self.delai_arret
        )

        self._dernier_signal = maintenant

        self._file_signaux.append(
            (
                i,
                nom_pays,
                signal_rapide,
            )
        )

        # ------------------------------------------------------------------
        # Gare de départ
        # ------------------------------------------------------------------

        # Les signaux peuvent déjà arriver pendant les trois secondes de
        # départ. On les conserve simplement dans la file.
        if self._index_gare_active == 0:
            return

        # ------------------------------------------------------------------
        # Aucune gare actuellement affichée
        # ------------------------------------------------------------------

        if self._gare_active is None:

            self._demarrer_gare_suivante()

            return

        # ------------------------------------------------------------------
        # Gare intermédiaire déjà en cours
        # ------------------------------------------------------------------

        # La gare finale doit toujours provoquer un vrai arrêt.
        if self._index_gare_active == self.n:
            return

        # Un nouveau résultat existe déjà pendant que la gare précédente
        # n'est pas terminée : on cherche donc à rattraper le retard.
        if self._etat == "approche":

            self._passage_sans_arret = True

            self._definir_feu_gare("vert")

        elif self._etat == "arret":

            # On écourte immédiatement l'arrêt.
            self._passage_sans_arret = True

            self._ouverture_barriere = 1.0

            self._definir_feu_gare("vert")

            self._etat = "depart_gare"
            self._temps_etat = 0.0

            self._demarrer_transition_paysage()

    # --------------------------------------------------------------------------
    # Gestion des gares
    # --------------------------------------------------------------------------

    def _demarrer_gare_suivante(self) -> None:
        """Démarre l'animation du prochain signal reçu."""

        if not self._file_signaux:

            self._etat = "trajet"

            return

        (
            i,
            nom_pays,
            signal_rapide,
        ) = self._file_signaux.popleft()

        self._i_actuel = i
        self._nom_pays_actuel = nom_pays

        # Les indices correspondent directement :
        #
        #     gare[0] = départ
        #     gare[1] = pays 1
        #     ...
        #     gare[n] = arrivée
        #
        self._index_gare_active = i

        self._gare_active = self.gares[i]

        largeur_gare = self._largeur_gare()

        # La gare arrive de la droite.
        self._x_gare_depart = self.width() - largeur_gare * 0.10

        self._x_gare = self._x_gare_depart

        # ------------------------------------------------------------------
        # Arrêt ou passage
        # ------------------------------------------------------------------

        if i == self.n:

            # La gare d'arrivée n'est jamais traversée.
            self._passage_sans_arret = False

        else:

            self._passage_sans_arret = signal_rapide or len(self._file_signaux) > 0

        self._ouverture_barriere = 0.0

        self._temps_etat = 0.0

        self._etat = "approche"

        self._definir_feu_gare("vert" if self._passage_sans_arret else "rouge")

    def _terminer_gare(self) -> None:
        """
        Retire une gare intermédiaire et traite éventuellement la suivante.

        Cette méthode n'est jamais appelée pour la gare d'arrivée.
        """

        # Si le fondu n'est pas complètement terminé, on valide directement
        # le paysage suivant.
        if self._paysage_suivant is not None:

            self._paysage_courant = self._paysage_suivant

            self._paysage_suivant = None

            self._fondu_paysage = 0.0

        # Après la gare i, on se trouve sur le paysage i.
        if 0 <= self._i_actuel < len(self.paysages):
            self._index_paysage = self._i_actuel

        self._gare_active = None
        self._index_gare_active = None

        self._nom_pays_actuel = None

        self._ouverture_barriere = 0.0

        self._passage_sans_arret = False

        self._etat = "trajet"
        self._temps_etat = 0.0

        if self._file_signaux:

            self._demarrer_gare_suivante()

    # --------------------------------------------------------------------------
    # Paysages
    # --------------------------------------------------------------------------

    def _demarrer_transition_paysage(self) -> None:
        """
        Prépare le paysage qui suit la gare intermédiaire courante.

        La gare d'arrivée ne possède aucun paysage après elle.
        """

        # Départ et arrivée ne déclenchent pas cette transition.
        if self._i_actuel <= 0 or self._i_actuel >= self.n:
            return

        index_suivant = self._i_actuel

        if index_suivant >= len(self.paysages):
            return

        paysage_suivant = self.paysages[index_suivant]

        # Petite gare de campagne : même objet paysage.
        if paysage_suivant is self._paysage_courant:

            self._index_paysage = index_suivant

            return

        self._paysage_suivant = paysage_suivant

        self._fondu_paysage = 0.0

    def _actualiser_transition_paysage(
        self,
        dt: float,
    ) -> None:
        """Fait progresser le fondu entre deux paysages."""

        if self._paysage_suivant is None:
            return

        self._fondu_paysage += dt / self.duree_transition_paysage

        if self._fondu_paysage >= 1.0:

            self._paysage_courant = self._paysage_suivant

            self._paysage_suivant = None

            self._fondu_paysage = 0.0

            self._index_paysage = self._i_actuel

    # --------------------------------------------------------------------------
    # Contrôle de l'animation
    # --------------------------------------------------------------------------

    def demarrer(self) -> None:
        """Démarre ou reprend l'animation."""

        # Une animation terminée reste volontairement figée.
        if self._etat == "termine":
            return

        if self._timer.isActive():
            return

        self._anime = True

        self._horloge.restart()

        self._timer.start()

    def arreter(self) -> None:
        """Met l'animation en pause."""

        self._anime = False

        self._timer.stop()

    def reinitialiser(self) -> None:
        """Replace complètement l'animation dans sa gare de départ."""

        self.distance_parcourue = 0.0
        self.vitesse_courante = 0.0

        # ------------------------------------------------------------------
        # Signaux
        # ------------------------------------------------------------------

        self._file_signaux.clear()

        self._dernier_signal = None

        # ------------------------------------------------------------------
        # Gare de départ
        # ------------------------------------------------------------------

        self._gare_active = self.gares[0]

        self._index_gare_active = 0

        self._i_actuel = 0
        self._nom_pays_actuel = None

        self._x_gare = 0.0
        self._x_gare_depart = 0.0

        self._gare_depart_positionnee = False

        self._passage_sans_arret = False

        self._ouverture_barriere = 0.0

        self._etat = "depart_attente"
        self._temps_etat = 0.0

        # Tous les feux repartent au rouge.
        for gare in self.gares:

            if hasattr(
                gare,
                "etat_feu",
            ):
                gare.etat_feu = "rouge"

        self._definir_feu_gare("rouge")

        # ------------------------------------------------------------------
        # Paysage initial
        # ------------------------------------------------------------------

        self._index_paysage = 0

        self._paysage_courant = self.paysages[0]

        self._paysage_suivant = None

        self._fondu_paysage = 0.0

        # ------------------------------------------------------------------
        # Redémarrage du moteur
        # ------------------------------------------------------------------

        self._anime = True

        self._horloge.restart()

        if not self._timer.isActive():
            self._timer.start()

        self.update()

    def definir_vitesse(
        self,
        vitesse: float,
    ) -> None:
        """Modifie la vitesse de croisière."""

        self.vitesse = max(
            0.0,
            float(vitesse),
        )

    # --------------------------------------------------------------------------
    # Vitesse
    # --------------------------------------------------------------------------

    def _vitesse_cible(self) -> float:
        """Retourne la vitesse visuelle souhaitée."""

        retard = len(self._file_signaux)

        # ------------------------------------------------------------------
        # Gare de départ
        # ------------------------------------------------------------------

        if self._etat in (
            "depart_attente",
            "depart_feu_vert",
        ):
            return 0.0

        if self._etat == "depart_initial":
            return self.vitesse

        # ------------------------------------------------------------------
        # Arrivée
        # ------------------------------------------------------------------

        if self._etat in (
            "arrivee",
            "termine",
        ):
            return 0.0

        # ------------------------------------------------------------------
        # Trajet normal
        # ------------------------------------------------------------------

        if self._etat == "trajet":

            if retard == 0:
                return self.vitesse

            facteur = min(
                1.60,
                1.10 + retard * 0.15,
            )

            return self.vitesse * facteur

        # ------------------------------------------------------------------
        # Approche
        # ------------------------------------------------------------------

        if self._etat == "approche":

            if self._passage_sans_arret:

                return self.vitesse * 0.85

            return self.vitesse * 0.55

        # ------------------------------------------------------------------
        # Arrêt
        # ------------------------------------------------------------------

        if self._etat == "arret":
            return 0.0

        # ------------------------------------------------------------------
        # Passage rapide
        # ------------------------------------------------------------------

        if self._etat == "passage":

            facteur = min(
                1.80,
                1.25 + retard * 0.20,
            )

            return self.vitesse * facteur

        # ------------------------------------------------------------------
        # Départ d'une gare intermédiaire
        # ------------------------------------------------------------------

        if self._etat == "depart_gare":

            facteur = min(
                1.60,
                1.0 + retard * 0.15,
            )

            return self.vitesse * facteur

        return self.vitesse

    def _actualiser_vitesse(
        self,
        dt: float,
    ) -> None:
        """Approche progressivement la vitesse cible."""

        cible = self._vitesse_cible()

        facteur = min(
            1.0,
            dt * 4.0,
        )

        self.vitesse_courante += (cible - self.vitesse_courante) * facteur

        if abs(self.vitesse_courante - cible) < 0.05:

            self.vitesse_courante = cible

    # --------------------------------------------------------------------------
    # Géométrie des gares
    # --------------------------------------------------------------------------

    def _x_arret_gare(self) -> float:
        """
        Centre la gare autour du train lorsque celui-ci est à quai.

        Cela garantit notamment que l'arrière du train reste bien à
        l'intérieur de la gare.
        """

        rect_train = self._rect_train(self._rect_rails())

        largeur_gare = self._largeur_gare()

        return rect_train.center().x() - largeur_gare / 2

    # --------------------------------------------------------------------------
    # Animation des gares
    # --------------------------------------------------------------------------

    def _actualiser_gare(
        self,
        dt: float,
    ) -> None:
        """Met à jour la position et l'état de la gare active."""

        if self._gare_active is None:
            return

        # ------------------------------------------------------------------
        # Position initiale de la gare de départ
        # ------------------------------------------------------------------

        if self._etat == "depart_attente" and not self._gare_depart_positionnee:

            self._x_gare = self._x_arret_gare()

            self._gare_depart_positionnee = True

        self._temps_etat += dt

        largeur_gare = self._largeur_gare()

        x_arret = self._x_arret_gare()

        # Une gare est très proche de la voie et défile donc rapidement.
        facteur_gare = 2.6

        vitesse_gare = max(
            90.0,
            self.vitesse_courante * facteur_gare,
        )

        # ------------------------------------------------------------------
        # Gare de départ : feu rouge
        # ------------------------------------------------------------------

        if self._etat == "depart_attente":

            self._definir_feu_gare("rouge")

            if self._temps_etat >= self.duree_attente_depart:

                self._definir_feu_gare("vert")

                self._etat = "depart_feu_vert"

                self._temps_etat = 0.0

            return

        # ------------------------------------------------------------------
        # Gare de départ : feu vert
        # ------------------------------------------------------------------

        if self._etat == "depart_feu_vert":

            self._definir_feu_gare("vert")

            if self._temps_etat >= self.duree_feu_vert_depart:

                self._etat = "depart_initial"

                self._temps_etat = 0.0

            return

        # ------------------------------------------------------------------
        # Sortie de la gare de départ
        # ------------------------------------------------------------------

        if self._etat == "depart_initial":

            self._definir_feu_gare("vert")

            self._x_gare -= vitesse_gare * dt

            if self._x_gare + largeur_gare < -20:

                self._gare_active = None
                self._index_gare_active = None

                self._etat = "trajet"
                self._temps_etat = 0.0

                if self._file_signaux:
                    self._demarrer_gare_suivante()

            return

        # ------------------------------------------------------------------
        # Approche d'une gare
        # ------------------------------------------------------------------

        if self._etat == "approche":

            # En cas de passage sans arrêt, la barrière de la petite gare
            # commence à se lever avant même que le train n'arrive au centre.
            if self._passage_sans_arret:

                distance_totale = max(
                    1.0,
                    self._x_gare_depart - x_arret,
                )

                progression = (self._x_gare_depart - self._x_gare) / distance_totale

                self._ouverture_barriere = max(
                    0.0,
                    min(
                        1.0,
                        (progression - 0.35) / 0.50,
                    ),
                )

            self._x_gare -= vitesse_gare * dt

            if self._x_gare <= x_arret:

                self._x_gare = x_arret

                self._temps_etat = 0.0

                # ----------------------------------------------------------
                # Gare d'arrivée
                # ----------------------------------------------------------

                if self._i_actuel == self.n:

                    self._passage_sans_arret = False

                    self._definir_feu_gare("rouge")

                    self._etat = "arrivee"

                # ----------------------------------------------------------
                # Passage sans arrêt
                # ----------------------------------------------------------

                elif self._passage_sans_arret:

                    self._definir_feu_gare("vert")

                    self._etat = "passage"

                    self._demarrer_transition_paysage()

                # ----------------------------------------------------------
                # Arrêt normal
                # ----------------------------------------------------------

                else:

                    self._definir_feu_gare("rouge")

                    self._etat = "arret"

            return

        # ------------------------------------------------------------------
        # Arrêt intermédiaire
        # ------------------------------------------------------------------

        if self._etat == "arret":

            # Le compteur d'arrêt ne commence qu'une fois le train réellement
            # immobilisé.
            if self.vitesse_courante > 0.7:

                self._temps_etat = 0.0

                return

            debut_ouverture = self.duree_attente_gare

            if self._temps_etat >= debut_ouverture:

                t = (self._temps_etat - debut_ouverture) / self.duree_ouverture_barriere

                self._ouverture_barriere = max(
                    0.0,
                    min(
                        1.0,
                        t,
                    ),
                )

            duree_totale = self.duree_attente_gare + self.duree_ouverture_barriere

            if self._temps_etat >= duree_totale:

                self._ouverture_barriere = 1.0

                self._definir_feu_gare("vert")

                self._etat = "depart_gare"

                self._temps_etat = 0.0

                self._demarrer_transition_paysage()

            return

        # ------------------------------------------------------------------
        # Passage sans arrêt
        # ------------------------------------------------------------------

        if self._etat == "passage":

            self._ouverture_barriere = min(
                1.0,
                self._ouverture_barriere + dt * 3.5,
            )

            facteur_rattrapage = 1.0 + min(
                1.25,
                len(self._file_signaux) * 0.25,
            )

            self._x_gare -= vitesse_gare * facteur_rattrapage * dt

            self._actualiser_transition_paysage(dt)

            if self._x_gare + largeur_gare < -20:
                self._terminer_gare()

            return

        # ------------------------------------------------------------------
        # Départ après un arrêt intermédiaire
        # ------------------------------------------------------------------

        if self._etat == "depart_gare":

            self._ouverture_barriere = 1.0

            self._definir_feu_gare("vert")

            self._x_gare -= vitesse_gare * dt

            self._actualiser_transition_paysage(dt)

            if self._x_gare + largeur_gare < -20:
                self._terminer_gare()

            return

        # ------------------------------------------------------------------
        # Gare d'arrivée
        # ------------------------------------------------------------------

        if self._etat == "arrivee":

            # La gare reste parfaitement immobile autour du train.
            self._x_gare = x_arret

            self._definir_feu_gare("rouge")

            # La vitesse est ramenée progressivement à zéro par
            # _actualiser_vitesse().
            if self.vitesse_courante <= 0.5:

                self.vitesse_courante = 0.0
                self._etat = "termine"
                self._anime = False
                self._timer.stop()

                # Ajout du bouton de retour
                self.bouton_retour.setVisible(True)
                self._positionner_bouton_retour()

                self.update()

            return

    # --------------------------------------------------------------------------
    # Arrêt final
    # --------------------------------------------------------------------------

    def _positionner_bouton_retour(self) -> None:
        """Positionne le bouton de retour dans la scène finale."""

        largeur = min(
            300,
            int(self.width() * 0.34),
        )
        hauteur = 42

        x = (self.width() - largeur) // 2
        y = int(self.height() * 0.82)

        self.bouton_retour.setGeometry(
            x,
            y,
            largeur,
            hauteur,
        )

    # --------------------------------------------------------------------------
    # Animation générale
    # --------------------------------------------------------------------------

    def _actualiser_animation(self) -> None:
        """Met à jour l'ensemble de la scène."""

        if not self._anime:
            return

        temps_ms = self._horloge.restart()

        dt = min(
            temps_ms / 1000.0,
            0.050,
        )

        # ------------------------------------------------------------------
        # Vitesse
        # ------------------------------------------------------------------

        self._actualiser_vitesse(dt)

        # ------------------------------------------------------------------
        # Distance visuelle
        # ------------------------------------------------------------------

        self.distance_parcourue += self.vitesse_courante * dt

        if self.distance_parcourue > 1_000_000:

            self.distance_parcourue %= 10_000

        # ------------------------------------------------------------------
        # Gare
        # ------------------------------------------------------------------

        self._actualiser_gare(dt)

        self.update()

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    def _rect_scene(self) -> QRectF:
        """Zone complète de la scène."""

        return QRectF(
            0.0,
            0.0,
            self.width(),
            self.height(),
        )

    def _rect_rails(self) -> QRectF:
        """Retourne la zone réservée à la voie ferrée."""

        hauteur = max(
            58.0,
            min(
                92.0,
                self.height() * 0.32,
            ),
        )

        y = self.height() * 0.68

        return QRectF(
            0.0,
            y,
            self.width(),
            hauteur,
        )

    def _rect_train(
        self,
        rect_rails: QRectF,
    ) -> QRectF:
        """Positionne le train sur les rails."""

        largeur_ref = self.train.largeur_recommandee()

        hauteur_ref = 140.0

        largeur_max = self.width() * 0.62

        hauteur_max = self.height() * 0.62

        echelle = min(
            largeur_max / largeur_ref,
            hauteur_max / hauteur_ref,
        )

        largeur_train = largeur_ref * echelle

        hauteur_train = hauteur_ref * echelle

        y_rail = self.rails.y_roulement(rect_rails)

        bas_train = y_rail + hauteur_train * 0.03

        haut_train = bas_train - hauteur_train

        centre_x = self.width() * 0.44

        return QRectF(
            centre_x - largeur_train / 2,
            haut_train,
            largeur_train,
            hauteur_train,
        )

    def _largeur_gare(self) -> float:
        """
        Retourne la largeur de la gare active.

        On impose également une largeur minimale légèrement supérieure à
        celle du train afin que toute la rame puisse être contenue à quai.
        """

        if self._gare_active is None:
            return 0.0

        largeur_recommandee = self._gare_active.largeur_recommandee(self.height())

        rect_train = self._rect_train(self._rect_rails())

        largeur_minimale = rect_train.width() + self.width() * 0.08

        return min(
            self.width() * 0.88,
            max(
                largeur_recommandee,
                largeur_minimale,
            ),
        )

    def _rect_gare(self) -> QRectF | None:
        """Retourne le rectangle de la gare active."""

        if self._gare_active is None:
            return None

        return QRectF(
            self._x_gare,
            0.0,
            self._largeur_gare(),
            self.height(),
        )

    # --------------------------------------------------------------------------
    # Roues
    # --------------------------------------------------------------------------

    def _phase_roues(
        self,
        rect_train: QRectF,
    ) -> float:
        """
        Calcule la rotation des roues à partir de la distance parcourue.
        """

        rayon_roue = rect_train.height() * 0.11

        if rayon_roue <= 0:
            return 0.0

        circonference = 2 * math.pi * rayon_roue

        return (self.distance_parcourue / circonference) % 1.0

    # --------------------------------------------------------------------------
    # Paysages
    # --------------------------------------------------------------------------

    def _peindre_paysages(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_rail: float,
    ) -> None:
        """Dessine le paysage courant et son éventuelle transition."""

        if self._paysage_suivant is None:

            self._paysage_courant.peindre(
                painter=painter,
                rect_scene=rect_scene,
                y_rail=y_rail,
                distance=self.distance_parcourue,
            )

            return

        alpha = max(
            0.0,
            min(
                1.0,
                self._fondu_paysage,
            ),
        )

        # ------------------------------------------------------------------
        # Ancien paysage
        # ------------------------------------------------------------------

        painter.save()

        painter.setOpacity(1.0 - alpha)

        self._paysage_courant.peindre(
            painter=painter,
            rect_scene=rect_scene,
            y_rail=y_rail,
            distance=self.distance_parcourue,
        )

        painter.restore()

        # ------------------------------------------------------------------
        # Nouveau paysage
        # ------------------------------------------------------------------

        painter.save()

        painter.setOpacity(alpha)

        self._paysage_suivant.peindre(
            painter=painter,
            rect_scene=rect_scene,
            y_rail=y_rail,
            distance=self.distance_parcourue,
        )

        painter.restore()

    # --------------------------------------------------------------------------
    # Dessin
    # --------------------------------------------------------------------------

    def resizeEvent(
        self,
        event,
    ) -> None:

        super().resizeEvent(event)

        if self.bouton_retour.isVisible():
            self._positionner_bouton_retour()

    def paintEvent(
        self,
        event,
    ) -> None:

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        rect_scene = self._rect_scene()

        rect_rails = self._rect_rails()

        rect_train = self._rect_train(rect_rails)

        y_rail = self.rails.y_roulement(rect_rails)

        # ------------------------------------------------------------------
        # Paysage
        # ------------------------------------------------------------------

        self._peindre_paysages(
            painter,
            rect_scene,
            y_rail,
        )

        # ------------------------------------------------------------------
        # Gare
        # ------------------------------------------------------------------

        rect_gare = self._rect_gare()

        gare_masque_rails = self._gare_active is not None and getattr(
            self._gare_active,
            "masque_rails",
            False,
        )

        # La gare de départ n'affiche ni nom, ni 0/n.
        est_gare_depart = self._index_gare_active == 0

        if est_gare_depart:

            nom_pays_affiche = None
            i_affiche = None
            n_affiche = None

        else:

            nom_pays_affiche = self._nom_pays_actuel

            i_affiche = self._i_actuel

            n_affiche = self.n

        # ------------------------------------------------------------------
        # Fonction commune de dessin arrière
        # ------------------------------------------------------------------

        def peindre_gare_derriere():

            self._gare_active.peindre_arriere(
                painter=painter,
                rect=rect_gare,
                nom_pays=nom_pays_affiche,
                i=i_affiche,
                n=n_affiche,
                y_rail=y_rail,
            )

        # ------------------------------------------------------------------
        # Gare dont les rails restent visibles
        # ------------------------------------------------------------------

        if (
            self._gare_active is not None
            and rect_gare is not None
            and not gare_masque_rails
        ):

            peindre_gare_derriere()

        # ------------------------------------------------------------------
        # Rails
        # ------------------------------------------------------------------

        self.rails.peindre(
            painter,
            rect_rails,
            decalage=self.distance_parcourue,
        )

        # ------------------------------------------------------------------
        # Gare intérieure : elle recouvre les rails
        # ------------------------------------------------------------------

        if (
            self._gare_active is not None
            and rect_gare is not None
            and gare_masque_rails
        ):

            peindre_gare_derriere()

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
        # Premier plan de la gare
        # ------------------------------------------------------------------

        kwargs_avant = {
            "ouverture_barriere": self._ouverture_barriere,
        }

        if self._etat == "termine" and self._index_gare_active == self.n:
            kwargs_avant["message_final"] = "Toutes les cartes ont été ajoutées"

        if self._gare_active is not None and rect_gare is not None:

            self._gare_active.peindre_avant(
                painter=painter, rect=rect_gare, y_rail=y_rail, **kwargs_avant
            )

        painter.end()
