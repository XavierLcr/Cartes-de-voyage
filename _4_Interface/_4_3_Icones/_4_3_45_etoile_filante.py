################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.45 – Classe de création d"une étoile filante                             #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math
import random
import time

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QBrush,
    QLinearGradient,
    QPainter,
    QPen,
    QRadialGradient,
)

# 1 -- Fonction de dessin d'une étoile filante ---------------------------------


def _dessiner_une_etoile_filante(
    painter: QPainter,
    position: QPointF,
    direction: QPointF,
    longueur: float,
    epaisseur: float,
    couleur: QColor | str = "#FFF8D6",
    opacite: float = 1.0,
) -> None:
    """
    Dessine une étoile filante et sa traînée.

    `direction` correspond au sens de déplacement de l'étoile.
    La traînée est naturellement dessinée dans le sens opposé.
    """

    if opacite <= 0.0:
        return

    couleur = QColor(couleur)

    # Normalisation de la direction
    norme = math.hypot(
        direction.x(),
        direction.y(),
    )

    if norme <= 0:
        return

    dx = direction.x() / norme
    dy = direction.y() / norme

    # Extrémité arrière de la traînée
    queue = QPointF(
        position.x() - dx * longueur,
        position.y() - dy * longueur,
    )

    painter.save()
    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing,
        True,
    )

    # -- Halo extérieur ---------------------------------------------------------

    gradient_halo = QLinearGradient(
        queue,
        position,
    )

    couleur_transparente = QColor(couleur)
    couleur_transparente.setAlpha(0)

    couleur_halo = QColor(couleur)
    couleur_halo.setAlpha(int(70 * opacite))

    gradient_halo.setColorAt(
        0.0,
        couleur_transparente,
    )

    gradient_halo.setColorAt(
        0.65,
        couleur_halo,
    )

    couleur_tete_halo = QColor(couleur)
    couleur_tete_halo.setAlpha(int(150 * opacite))

    gradient_halo.setColorAt(
        1.0,
        couleur_tete_halo,
    )

    pen_halo = QPen(
        QBrush(gradient_halo),
        epaisseur * 4.0,
    )

    pen_halo.setCapStyle(Qt.PenCapStyle.RoundCap)

    painter.setPen(pen_halo)

    painter.drawLine(
        queue,
        position,
    )

    # -- Traînée principale -----------------------------------------------------

    gradient = QLinearGradient(
        queue,
        position,
    )

    couleur_queue = QColor(couleur)
    couleur_queue.setAlpha(0)

    couleur_milieu = QColor(couleur)
    couleur_milieu.setAlpha(int(130 * opacite))

    couleur_tete = QColor(couleur)
    couleur_tete.setAlpha(int(255 * opacite))

    gradient.setColorAt(
        0.0,
        couleur_queue,
    )

    gradient.setColorAt(
        0.55,
        couleur_milieu,
    )

    gradient.setColorAt(
        1.0,
        couleur_tete,
    )

    pen = QPen(
        QBrush(gradient),
        epaisseur,
    )

    pen.setCapStyle(Qt.PenCapStyle.RoundCap)

    painter.setPen(pen)

    painter.drawLine(
        queue,
        position,
    )

    # -- Cœur lumineux ----------------------------------------------------------

    rayon_halo = epaisseur * 4.5

    halo = QRadialGradient(
        position,
        rayon_halo,
    )

    couleur_centre = QColor(couleur)
    couleur_centre.setAlpha(int(220 * opacite))

    couleur_bord = QColor(couleur)
    couleur_bord.setAlpha(0)

    halo.setColorAt(
        0.0,
        couleur_centre,
    )

    halo.setColorAt(
        1.0,
        couleur_bord,
    )

    painter.setPen(Qt.PenStyle.NoPen)

    painter.setBrush(QBrush(halo))

    painter.drawEllipse(
        position,
        rayon_halo,
        rayon_halo,
    )

    # Petit noyau blanc très lumineux
    couleur_noyau = QColor("#FFFFFF")
    couleur_noyau.setAlpha(int(255 * opacite))

    painter.setBrush(couleur_noyau)

    rayon_noyau = max(
        0.8,
        epaisseur * 0.7,
    )

    painter.drawEllipse(
        position,
        rayon_noyau,
        rayon_noyau,
    )

    painter.restore()


# 2 -- Classe de gestion de l'étoile filante -----------------------------------


class EtoileFilante:
    """
    Gère l'apparition occasionnelle d'une étoile filante pendant la nuit.

    Un seul passage est actif à la fois. Les délais, trajectoires et durées
    sont légèrement aléatoires afin d'éviter un comportement répétitif.
    """

    def __init__(
        self,
        intervalle_min: float = 7.0,
        intervalle_max: float = 20.0,
        duree_min: float = 0.7,
        duree_max: float = 1.2,
        angle_min: float = 18.0,
        angle_max: float = 32.0,
        longueur_ratio_min: float = 0.12,
        longueur_ratio_max: float = 0.22,
        epaisseur_ratio: float = 0.003,
        couleur: QColor | str = "#FFF8D6",
        graine: int | None = None,
    ) -> None:

        self.intervalle_min = intervalle_min
        self.intervalle_max = intervalle_max

        self.duree_min = duree_min
        self.duree_max = duree_max

        self.angle_min = angle_min
        self.angle_max = angle_max

        self.longueur_ratio_min = longueur_ratio_min
        self.longueur_ratio_max = longueur_ratio_max

        self.epaisseur_ratio = epaisseur_ratio

        self.couleur = QColor(couleur)

        self._rng = random.Random(graine)

        self._active = False
        self._nuit_precedente = False

        self._debut = 0.0
        self._duree = 1.0
        self._prochain_passage = 0.0

        self._x_depart = 0.0
        self._y_depart = 0.0

        self._distance = 0.0
        self._angle = 0.0
        self._sens = 1

        self._longueur_ratio = 0.15

    # 2.1 -- Gestion des passages ----------------------------------------------

    def _programmer_prochain_passage(
        self,
        maintenant: float,
    ) -> None:

        self._prochain_passage = maintenant + self._rng.uniform(
            self.intervalle_min,
            self.intervalle_max,
        )

    def _demarrer_passage(
        self,
        maintenant: float,
    ) -> None:
        """Génère une nouvelle trajectoire."""

        self._active = True
        self._debut = maintenant

        self._duree = self._rng.uniform(
            self.duree_min,
            self.duree_max,
        )

        # Départ dans la partie supérieure du ciel
        self._x_depart = self._rng.uniform(
            0.15,
            0.85,
        )

        self._y_depart = self._rng.uniform(
            0.05,
            0.25,
        )

        # Distance parcourue relativement à la largeur de la scène
        self._distance = self._rng.uniform(
            0.30,
            0.48,
        )

        # L'étoile peut partir vers la gauche ou vers la droite
        self._sens = self._rng.choice((-1, 1))

        self._angle = math.radians(
            self._rng.uniform(
                self.angle_min,
                self.angle_max,
            )
        )

        self._longueur_ratio = self._rng.uniform(
            self.longueur_ratio_min,
            self.longueur_ratio_max,
        )

    # 2.2 -- Dessin -------------------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        nuit: float,
    ) -> None:
        """
        Met à jour et dessine éventuellement l'étoile filante.

        L'animation n'est active que lorsque `nuit` vaut réellement 1.
        """

        maintenant = time.monotonic()

        nuit_complete = nuit >= 0.999

        # -- Sortie de la nuit complète -----------------------------------------

        if not nuit_complete:

            self._active = False
            self._nuit_precedente = False

            return

        # -- Entrée dans la nuit complète ---------------------------------------

        if not self._nuit_precedente:

            self._active = False

            self._programmer_prochain_passage(maintenant)

            self._nuit_precedente = True

        # -- Attente du prochain passage ----------------------------------------

        if not self._active:

            if maintenant < self._prochain_passage:
                return

            self._demarrer_passage(maintenant)

        # -- Progression ---------------------------------------------------------

        progression = (maintenant - self._debut) / self._duree

        if progression >= 1.0:

            self._active = False

            self._programmer_prochain_passage(maintenant)

            return

        progression = max(
            0.0,
            min(1.0, progression),
        )

        # -- Trajectoire ---------------------------------------------------------

        distance = rect_scene.width() * self._distance

        dx = math.cos(self._angle) * distance * self._sens

        dy = math.sin(self._angle) * distance

        depart = QPointF(
            rect_scene.left() + rect_scene.width() * self._x_depart,
            rect_scene.top() + rect_scene.height() * self._y_depart,
        )

        position = QPointF(
            depart.x() + dx * progression,
            depart.y() + dy * progression,
        )

        direction = QPointF(
            dx,
            dy,
        )

        # -- Fondu en entrée et en sortie ---------------------------------------

        fondu_entree = min(
            1.0,
            progression / 0.08,
        )

        fondu_sortie = min(
            1.0,
            (1.0 - progression) / 0.20,
        )

        opacite = min(
            fondu_entree,
            fondu_sortie,
        )

        # -- Dimensions ---------------------------------------------------------

        taille_reference = min(
            rect_scene.width(),
            rect_scene.height(),
        )

        longueur = taille_reference * self._longueur_ratio

        epaisseur = max(
            1.0,
            taille_reference * self.epaisseur_ratio,
        )

        # -- Dessin -------------------------------------------------------------

        _dessiner_une_etoile_filante(
            painter=painter,
            position=position,
            direction=direction,
            longueur=longueur,
            epaisseur=epaisseur,
            couleur=self.couleur,
            opacite=opacite,
        )
