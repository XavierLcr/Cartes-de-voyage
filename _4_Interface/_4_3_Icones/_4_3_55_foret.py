################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.55 – Classe de création d'un paysage forestier                           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations

import math
import random

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)

# 1 -- Fonctions utilitaires ---------------------------------------------------


def _qcolor(couleur: QColor | str) -> QColor:
    """Retourne un QColor."""
    return couleur if isinstance(couleur, QColor) else QColor(couleur)


def _avec_alpha(
    couleur: QColor | str,
    alpha: int,
) -> QColor:
    """Retourne une copie de la couleur avec l'alpha demandé."""
    couleur = QColor(_qcolor(couleur))

    couleur.setAlpha(
        max(
            0,
            min(255, alpha),
        )
    )

    return couleur


def _melanger(
    couleur_1: QColor | str,
    couleur_2: QColor | str,
    proportion: float,
) -> QColor:
    """Interpole deux couleurs en RGB."""
    c1 = _qcolor(couleur_1)
    c2 = _qcolor(couleur_2)

    p = max(
        0.0,
        min(1.0, proportion),
    )

    return QColor(
        round(c1.red() * (1 - p) + c2.red() * p),
        round(c1.green() * (1 - p) + c2.green() * p),
        round(c1.blue() * (1 - p) + c2.blue() * p),
        round(c1.alpha() * (1 - p) + c2.alpha() * p),
    )


def _eclaircir(
    couleur: QColor | str,
    proportion: float = 0.20,
) -> QColor:
    """Éclaircit une couleur."""
    return _melanger(
        couleur,
        "#FFFFFF",
        proportion,
    )


def _assombrir(
    couleur: QColor | str,
    proportion: float = 0.20,
) -> QColor:
    """Assombrit une couleur."""
    return _melanger(
        couleur,
        "#000000",
        proportion,
    )


# 2 -- Classe du paysage -------------------------------------------------------


class PaysageForet:
    """
    Dessine un paysage forestier défilant derrière le train.

    Le décor est constitué de plusieurs plans :

        - ciel ;
        - collines boisées lointaines ;
        - forêt lointaine ;
        - forêt intermédiaire ;
        - arbres proches ;
        - sous-bois au bord de la voie.

    Les différents plans défilent à des vitesses différentes afin de créer
    un effet de parallaxe.

    Paramètres particuliers disponibles dans `peindre` via **kwargs :

        densite : float
            Multiplicateur de densité des arbres. Défaut : 1.0.

        proportion_coniferes : float
            Proportion approximative de conifères. Défaut : 0.35.

        brume : float
            Intensité de la brume entre 0 et 1. Défaut : 0.15.

        oiseaux : bool
            Affiche quelques oiseaux lointains. Défaut : True.
    """

    def __init__(
        self,
        graine: int = 57,
        couleur_ciel_haut: QColor | str = "#B8D5DE",
        couleur_ciel_bas: QColor | str = "#DDE8DD",
        couleur_colline: QColor | str = "#849B7B",
        couleur_foret_loin: QColor | str = "#71876A",
        couleur_foret_moyenne: QColor | str = "#536F50",
        couleur_foret_proche: QColor | str = "#36533B",
        couleur_tronc: QColor | str = "#6D523C",
        couleur_sol: QColor | str = "#536044",
        couleur_sous_bois: QColor | str = "#354737",
    ):
        self.graine = graine

        self.couleur_ciel_haut = _qcolor(couleur_ciel_haut)
        self.couleur_ciel_bas = _qcolor(couleur_ciel_bas)

        self.couleur_colline = _qcolor(couleur_colline)

        self.couleur_foret_loin = _qcolor(couleur_foret_loin)
        self.couleur_foret_moyenne = _qcolor(couleur_foret_moyenne)
        self.couleur_foret_proche = _qcolor(couleur_foret_proche)

        self.couleur_tronc = _qcolor(couleur_tronc)

        self.couleur_sol = _qcolor(couleur_sol)
        self.couleur_sous_bois = _qcolor(couleur_sous_bois)

    # --------------------------------------------------------------------------
    # Géométrie générale
    # --------------------------------------------------------------------------

    @staticmethod
    def _y_horizon(
        rect_scene: QRectF,
        y_rail: float,
    ) -> float:
        """Altitude de l'horizon."""
        return rect_scene.top() + (y_rail - rect_scene.top()) * 0.50

    # --------------------------------------------------------------------------
    # Ciel
    # --------------------------------------------------------------------------

    def _dessiner_ciel(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
    ) -> None:
        """Dessine le ciel forestier."""

        rect_ciel = QRectF(
            rect_scene.left(),
            rect_scene.top(),
            rect_scene.width(),
            y_horizon - rect_scene.top(),
        )

        gradient = QLinearGradient(
            rect_ciel.topLeft(),
            rect_ciel.bottomLeft(),
        )

        gradient.setColorAt(
            0.0,
            self.couleur_ciel_haut,
        )

        gradient.setColorAt(
            1.0,
            self.couleur_ciel_bas,
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient))

        painter.drawRect(rect_ciel)

    # --------------------------------------------------------------------------
    # Collines boisées
    # --------------------------------------------------------------------------

    def _dessiner_collines(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
        distance: float,
    ) -> None:
        """Dessine de grandes collines très lointaines."""

        largeur_motif = 650.0

        decalage = (distance * 0.018) % largeur_motif

        y_base = y_horizon + rect_scene.height() * 0.10

        hauteur = rect_scene.height() * 0.15

        path = QPainterPath()

        x_debut = rect_scene.left() - largeur_motif - decalage

        path.moveTo(
            x_debut,
            y_base,
        )

        x = x_debut

        index = -1

        while x <= rect_scene.right() + largeur_motif:

            rng = random.Random(self.graine + 500 + index)

            largeur = largeur_motif * rng.uniform(
                0.70,
                1.15,
            )

            hauteur_locale = hauteur * rng.uniform(
                0.55,
                1.0,
            )

            x_centre = x + largeur / 2

            path.quadTo(
                QPointF(
                    x_centre,
                    y_base - hauteur_locale,
                ),
                QPointF(
                    x + largeur,
                    y_base,
                ),
            )

            x += largeur
            index += 1

        path.lineTo(
            rect_scene.right() + largeur_motif,
            y_base + rect_scene.height(),
        )

        path.lineTo(
            x_debut,
            y_base + rect_scene.height(),
        )

        path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(self.couleur_colline)

        painter.drawPath(path)

    # --------------------------------------------------------------------------
    # Arbres
    # --------------------------------------------------------------------------

    def _dessiner_conifere(
        self,
        painter: QPainter,
        x: float,
        y_sol: float,
        hauteur: float,
        couleur: QColor,
        opacite: int = 255,
    ) -> None:
        """Dessine un conifère stylisé."""

        if hauteur <= 0:
            return

        couleur = _avec_alpha(
            couleur,
            opacite,
        )

        largeur = hauteur * 0.40

        hauteur_tronc = hauteur * 0.25

        # Tronc
        rect_tronc = QRectF(
            x - hauteur * 0.035,
            y_sol - hauteur_tronc,
            hauteur * 0.07,
            hauteur_tronc,
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(
            _avec_alpha(
                self.couleur_tronc,
                opacite,
            )
        )

        painter.drawRect(rect_tronc)

        # Trois étages de feuillage
        sommets = (
            (0.00, 0.00, 0.48),
            (0.22, 0.27, 0.70),
            (0.45, 0.50, 0.92),
        )

        painter.setBrush(couleur)

        for debut, fin, facteur_largeur in sommets:

            y_haut = y_sol - hauteur + hauteur * debut

            y_bas = y_sol - hauteur + hauteur * fin

            demi_largeur = largeur * facteur_largeur

            path = QPainterPath()

            path.moveTo(
                x,
                y_haut,
            )

            path.lineTo(
                x - demi_largeur,
                y_bas,
            )

            path.quadTo(
                QPointF(
                    x,
                    y_bas - hauteur * 0.035,
                ),
                QPointF(
                    x + demi_largeur,
                    y_bas,
                ),
            )

            path.closeSubpath()

            painter.drawPath(path)

    def _dessiner_feuillu(
        self,
        painter: QPainter,
        x: float,
        y_sol: float,
        hauteur: float,
        couleur: QColor,
        opacite: int = 255,
        variante: int = 0,
    ) -> None:
        """Dessine un arbre feuillu avec plusieurs masses de feuillage."""

        if hauteur <= 0:
            return

        couleur = _avec_alpha(
            couleur,
            opacite,
        )

        hauteur_tronc = hauteur * 0.48

        largeur_tronc = hauteur * 0.075

        rect_tronc = QRectF(
            x - largeur_tronc / 2,
            y_sol - hauteur_tronc,
            largeur_tronc,
            hauteur_tronc,
        )

        gradient = QLinearGradient(
            rect_tronc.left(),
            0,
            rect_tronc.right(),
            0,
        )

        gradient.setColorAt(
            0.0,
            _avec_alpha(
                _assombrir(
                    self.couleur_tronc,
                    0.20,
                ),
                opacite,
            ),
        )

        gradient.setColorAt(
            0.5,
            _avec_alpha(
                _eclaircir(
                    self.couleur_tronc,
                    0.08,
                ),
                opacite,
            ),
        )

        gradient.setColorAt(
            1.0,
            _avec_alpha(
                _assombrir(
                    self.couleur_tronc,
                    0.18,
                ),
                opacite,
            ),
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient))

        painter.drawRoundedRect(
            rect_tronc,
            largeur_tronc * 0.30,
            largeur_tronc * 0.30,
        )

        # Branches principales
        pen_branches = QPen(
            _avec_alpha(
                self.couleur_tronc,
                opacite,
            )
        )

        pen_branches.setWidthF(
            max(
                1.0,
                largeur_tronc * 0.42,
            )
        )

        pen_branches.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(pen_branches)

        y_branches = y_sol - hauteur_tronc * 0.75

        painter.drawLine(
            QPointF(
                x,
                y_branches,
            ),
            QPointF(
                x - hauteur * 0.17,
                y_branches - hauteur * 0.18,
            ),
        )

        painter.drawLine(
            QPointF(
                x,
                y_branches,
            ),
            QPointF(
                x + hauteur * 0.19,
                y_branches - hauteur * 0.22,
            ),
        )

        # Feuillage
        rng = random.Random(self.graine + 9000 + variante)

        painter.setPen(Qt.PenStyle.NoPen)

        masses = (
            (-0.25, -0.52, 0.30),
            (0.05, -0.62, 0.34),
            (0.30, -0.48, 0.29),
            (-0.08, -0.33, 0.38),
            (0.23, -0.28, 0.32),
        )

        for i, (
            dx,
            dy,
            rayon,
        ) in enumerate(masses):

            variation = rng.uniform(
                -0.06,
                0.06,
            )

            c = _melanger(
                couleur,
                "#FFFFFF" if i % 2 == 0 else "#000000",
                abs(variation),
            )

            c.setAlpha(opacite)

            painter.setBrush(c)

            painter.drawEllipse(
                QPointF(
                    x + dx * hauteur,
                    y_sol + dy * hauteur,
                ),
                hauteur * rayon,
                hauteur * rayon * 0.72,
            )

    # --------------------------------------------------------------------------
    # Plans forestiers
    # --------------------------------------------------------------------------

    def _dessiner_rangee_arbres(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_sol: float,
        distance: float,
        facteur_defilement: float,
        couleur: QColor,
        hauteur_min: float,
        hauteur_max: float,
        espacement: float,
        graine: int,
        densite: float,
        proportion_coniferes: float,
        opacite: int = 255,
    ) -> None:
        """
        Dessine une rangée déterministe d'arbres.

        Les arbres sont générés à partir de leur indice dans le monde afin
        d'éviter qu'ils changent d'apparence pendant le défilement.
        """

        densite = max(
            0.20,
            densite,
        )

        espacement_reel = espacement / densite

        decalage_monde = distance * facteur_defilement

        premier_indice = math.floor(
            (decalage_monde - rect_scene.width()) / espacement_reel
        )

        dernier_indice = math.ceil(
            (decalage_monde + rect_scene.width() * 2) / espacement_reel
        )

        for indice in range(
            premier_indice,
            dernier_indice + 1,
        ):

            rng = random.Random(self.graine + graine + indice * 7919)

            x_monde = indice * espacement_reel + rng.uniform(
                -espacement_reel * 0.25,
                espacement_reel * 0.25,
            )

            x = rect_scene.left() + x_monde - decalage_monde

            if (
                x < rect_scene.left() - espacement_reel
                or x > rect_scene.right() + espacement_reel
            ):
                continue

            hauteur = rect_scene.height() * rng.uniform(
                hauteur_min,
                hauteur_max,
            )

            est_conifere = rng.random() < proportion_coniferes

            if est_conifere:

                self._dessiner_conifere(
                    painter=painter,
                    x=x,
                    y_sol=y_sol,
                    hauteur=hauteur,
                    couleur=couleur,
                    opacite=opacite,
                )

            else:

                self._dessiner_feuillu(
                    painter=painter,
                    x=x,
                    y_sol=y_sol,
                    hauteur=hauteur,
                    couleur=couleur,
                    opacite=opacite,
                    variante=indice,
                )

    # --------------------------------------------------------------------------
    # Sol
    # --------------------------------------------------------------------------

    def _dessiner_sol(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_rail: float,
    ) -> None:
        """Dessine le sol forestier."""

        y_debut = y_rail - rect_scene.height() * 0.17

        rect_sol = QRectF(
            rect_scene.left(),
            y_debut,
            rect_scene.width(),
            y_rail - y_debut,
        )

        gradient = QLinearGradient(
            rect_sol.topLeft(),
            rect_sol.bottomLeft(),
        )

        gradient.setColorAt(
            0.0,
            _eclaircir(
                self.couleur_sol,
                0.10,
            ),
        )

        gradient.setColorAt(
            1.0,
            _assombrir(
                self.couleur_sol,
                0.15,
            ),
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient))

        painter.drawRect(rect_sol)

    # --------------------------------------------------------------------------
    # Sous-bois proche
    # --------------------------------------------------------------------------

    def _dessiner_sous_bois(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_rail: float,
        distance: float,
    ) -> None:
        """Dessine une végétation basse très proche de la voie."""

        hauteur = rect_scene.height() * 0.060

        y_base = y_rail - rect_scene.height() * 0.018

        largeur_motif = 42.0

        decalage = (distance * 0.55) % largeur_motif

        painter.setPen(Qt.PenStyle.NoPen)

        x = rect_scene.left() - largeur_motif - decalage

        index = 0

        while x < rect_scene.right() + largeur_motif:

            rng = random.Random(self.graine + 16000 + index)

            rayon_x = largeur_motif * rng.uniform(
                0.55,
                1.10,
            )

            rayon_y = hauteur * rng.uniform(
                0.45,
                0.90,
            )

            couleur = _melanger(
                self.couleur_sous_bois,
                self.couleur_foret_proche,
                rng.uniform(
                    0.0,
                    0.25,
                ),
            )

            painter.setBrush(couleur)

            painter.drawEllipse(
                QPointF(
                    x,
                    y_base,
                ),
                rayon_x,
                rayon_y,
            )

            x += largeur_motif
            index += 1

    # --------------------------------------------------------------------------
    # Brume
    # --------------------------------------------------------------------------

    def _dessiner_brume(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
        intensite: float,
    ) -> None:
        """Ajoute une fine brume au fond de la forêt."""

        intensite = max(
            0.0,
            min(
                1.0,
                intensite,
            ),
        )

        if intensite <= 0:
            return

        hauteur = rect_scene.height() * 0.26

        gradient = QLinearGradient(
            QPointF(
                0,
                y_horizon - hauteur * 0.45,
            ),
            QPointF(
                0,
                y_horizon + hauteur,
            ),
        )

        alpha_max = int(105 * intensite)

        gradient.setColorAt(
            0.0,
            QColor(
                230,
                239,
                235,
                0,
            ),
        )

        gradient.setColorAt(
            0.45,
            QColor(
                230,
                239,
                235,
                alpha_max,
            ),
        )

        gradient.setColorAt(
            1.0,
            QColor(
                230,
                239,
                235,
                0,
            ),
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient))

        painter.drawRect(
            QRectF(
                rect_scene.left(),
                y_horizon - hauteur * 0.45,
                rect_scene.width(),
                hauteur * 1.45,
            )
        )

    # --------------------------------------------------------------------------
    # Oiseaux
    # --------------------------------------------------------------------------

    def _dessiner_oiseaux(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        distance: float,
    ) -> None:
        """Dessine quelques oiseaux très lointains."""

        decalage = distance * 0.008

        painter.setBrush(Qt.BrushStyle.NoBrush)

        pen = QPen(
            _avec_alpha(
                "#4E5D60",
                115,
            )
        )

        pen.setWidthF(
            max(
                1.0,
                rect_scene.height() * 0.0035,
            )
        )

        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(pen)

        positions = (
            (0.18, 0.20, 0.018),
            (0.22, 0.17, 0.014),
            (0.26, 0.21, 0.013),
        )

        for px, py, taille in positions:

            x = rect_scene.left() + (px * rect_scene.width() - decalage) % (
                rect_scene.width() * 1.25
            )

            y = rect_scene.top() + py * rect_scene.height()

            largeur = rect_scene.width() * taille

            hauteur = largeur * 0.32

            path = QPainterPath()

            path.moveTo(
                x - largeur,
                y,
            )

            path.quadTo(
                QPointF(
                    x - largeur * 0.45,
                    y - hauteur,
                ),
                QPointF(
                    x,
                    y,
                ),
            )

            path.quadTo(
                QPointF(
                    x + largeur * 0.45,
                    y - hauteur,
                ),
                QPointF(
                    x + largeur,
                    y,
                ),
            )

            painter.drawPath(path)

    # --------------------------------------------------------------------------
    # Dessin principal
    # --------------------------------------------------------------------------

    def peindre(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_rail: float,
        distance: float = 0.0,
        **kwargs,
    ) -> None:
        """
        Dessine le paysage forestier complet.

        Paramètres spécifiques dans `kwargs` :
            densite               : float, défaut 1.0
            proportion_coniferes  : float, défaut 0.35
            brume                 : float, défaut 0.15
            oiseaux               : bool, défaut True
        """

        if rect_scene.width() <= 0 or rect_scene.height() <= 0:
            return

        densite = max(0.20, float(kwargs.get("densite", 1.0)))

        proportion_coniferes = max(
            0.0,
            min(1.0, float(kwargs.get("proportion_coniferes", 0.35))),
        )

        brume = max(
            0.0,
            min(
                1.0,
                float(kwargs.get("brume", 0.15)),
            ),
        )

        oiseaux = bool(kwargs.get("oiseaux", True))

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        y_horizon = self._y_horizon(
            rect_scene,
            y_rail,
        )

        # ------------------------------------------------------------------
        # Ciel
        # ------------------------------------------------------------------

        self._dessiner_ciel(
            painter,
            rect_scene,
            y_horizon,
        )

        if oiseaux:
            self._dessiner_oiseaux(
                painter,
                rect_scene,
                distance,
            )

        # ------------------------------------------------------------------
        # Collines
        # ------------------------------------------------------------------

        self._dessiner_collines(
            painter,
            rect_scene,
            y_horizon,
            distance,
        )

        # ------------------------------------------------------------------
        # Forêt lointaine
        # ------------------------------------------------------------------

        self._dessiner_rangee_arbres(
            painter=painter,
            rect_scene=rect_scene,
            y_sol=y_horizon + rect_scene.height() * 0.09,
            distance=distance,
            facteur_defilement=0.045,
            couleur=self.couleur_foret_loin,
            hauteur_min=0.10,
            hauteur_max=0.17,
            espacement=48.0,
            graine=1000,
            densite=densite * 1.15,
            proportion_coniferes=proportion_coniferes + 0.10,
            opacite=190,
        )

        # Brume entre les couches
        self._dessiner_brume(
            painter,
            rect_scene,
            y_horizon,
            brume,
        )

        # ------------------------------------------------------------------
        # Sol
        # ------------------------------------------------------------------

        self._dessiner_sol(
            painter,
            rect_scene,
            y_rail,
        )

        # ------------------------------------------------------------------
        # Forêt intermédiaire
        # ------------------------------------------------------------------

        self._dessiner_rangee_arbres(
            painter=painter,
            rect_scene=rect_scene,
            y_sol=y_rail - rect_scene.height() * 0.10,
            distance=distance,
            facteur_defilement=0.13,
            couleur=self.couleur_foret_moyenne,
            hauteur_min=0.16,
            hauteur_max=0.25,
            espacement=78.0,
            graine=3000,
            densite=densite,
            proportion_coniferes=proportion_coniferes,
            opacite=235,
        )

        # ------------------------------------------------------------------
        # Arbres proches
        # ------------------------------------------------------------------

        self._dessiner_rangee_arbres(
            painter=painter,
            rect_scene=rect_scene,
            y_sol=y_rail - rect_scene.height() * 0.025,
            distance=distance,
            facteur_defilement=0.32,
            couleur=self.couleur_foret_proche,
            hauteur_min=0.20,
            hauteur_max=0.33,
            espacement=145.0,
            graine=7000,
            densite=densite * 0.85,
            proportion_coniferes=proportion_coniferes,
            opacite=255,
        )

        # ------------------------------------------------------------------
        # Sous-bois très proche
        # ------------------------------------------------------------------

        self._dessiner_sous_bois(
            painter,
            rect_scene,
            y_rail,
            distance,
        )

        painter.restore()
