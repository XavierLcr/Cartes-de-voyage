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
    # Géométrie commune aux arbres
    # --------------------------------------------------------------------------

    @staticmethod
    def _point_axe_arbre(
        x_sol: float,
        y_sol: float,
        hauteur: float,
        ratio: float,
        inclinaison: float,
    ) -> QPointF:
        """
        Retourne un point situé sur l'axe central de l'arbre.

        ratio = 0.0 :
            pied de l'arbre.

        ratio = 1.0 :
            sommet théorique de l'arbre.

        `inclinaison` correspond au décalage horizontal total du sommet,
        exprimé relativement à la hauteur de l'arbre.
        """

        return QPointF(
            x_sol + hauteur * inclinaison * ratio,
            y_sol - hauteur * ratio,
        )

    @staticmethod
    def _creer_masse_feuillage(
        centre: QPointF,
        rayon_x: float,
        rayon_y: float,
        rng: random.Random,
        irregularite: float = 0.14,
        n_points: int = 12,
    ) -> QPainterPath:
        """
        Crée une masse végétale organique.

        Contrairement à une ellipse, le contour présente de petites
        irrégularités tout en restant doux grâce aux courbes quadratiques.
        """

        points = []

        for i in range(n_points):

            angle = 2.0 * math.pi * i / n_points

            facteur = rng.uniform(
                1.0 - irregularite,
                1.0 + irregularite,
            )

            points.append(
                QPointF(
                    centre.x() + math.cos(angle) * rayon_x * facteur,
                    centre.y() + math.sin(angle) * rayon_y * facteur,
                )
            )

        path = QPainterPath()

        dernier = points[-1]
        premier = points[0]

        milieu = QPointF(
            (dernier.x() + premier.x()) / 2,
            (dernier.y() + premier.y()) / 2,
        )

        path.moveTo(milieu)

        for i, point in enumerate(points):

            suivant = points[(i + 1) % len(points)]

            milieu_suivant = QPointF(
                (point.x() + suivant.x()) / 2,
                (point.y() + suivant.y()) / 2,
            )

            path.quadTo(
                point,
                milieu_suivant,
            )

        path.closeSubpath()

        return path

    # --------------------------------------------------------------------------
    # Tronc
    # --------------------------------------------------------------------------

    def _dessiner_tronc_arbre(
        self,
        painter: QPainter,
        x: float,
        y_sol: float,
        hauteur: float,
        ratio_haut: float,
        largeur_base: float,
        inclinaison: float,
        opacite: int,
        graine: int,
        niveau_details: float = 1.0,
    ) -> None:
        """
        Dessine un tronc légèrement fuselé et incliné.

        La géométrie du tronc suit exactement le même axe que le reste
        de l'arbre.
        """

        rng = random.Random(graine)

        p_haut = self._point_axe_arbre(
            x,
            y_sol,
            hauteur,
            ratio_haut,
            inclinaison,
        )

        p_25 = self._point_axe_arbre(
            x,
            y_sol,
            hauteur,
            ratio_haut * 0.25,
            inclinaison,
        )

        p_70 = self._point_axe_arbre(
            x,
            y_sol,
            hauteur,
            ratio_haut * 0.70,
            inclinaison,
        )

        largeur_haut = largeur_base * 0.43

        # ------------------------------------------------------------------
        # Racines
        # ------------------------------------------------------------------

        if niveau_details >= 0.45:

            pen_racines = QPen(
                _avec_alpha(
                    _assombrir(
                        self.couleur_tronc,
                        0.14,
                    ),
                    int(opacite * 0.84),
                )
            )

            pen_racines.setWidthF(
                max(
                    0.8,
                    largeur_base * 0.18,
                )
            )

            pen_racines.setCapStyle(Qt.PenCapStyle.RoundCap)

            painter.setPen(pen_racines)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            for sens in (-1, 1):

                longueur = largeur_base * rng.uniform(
                    0.75,
                    1.25,
                )

                painter.drawLine(
                    QPointF(
                        x + sens * largeur_base * 0.18,
                        y_sol - largeur_base * 0.04,
                    ),
                    QPointF(
                        x + sens * longueur,
                        y_sol + largeur_base * 0.07,
                    ),
                )

        # ------------------------------------------------------------------
        # Silhouette principale
        # ------------------------------------------------------------------

        path = QPainterPath()

        path.moveTo(
            x - largeur_base / 2,
            y_sol,
        )

        path.cubicTo(
            QPointF(
                p_25.x() - largeur_base * 0.45,
                p_25.y(),
            ),
            QPointF(
                p_70.x() - largeur_base * 0.29,
                p_70.y(),
            ),
            QPointF(
                p_haut.x() - largeur_haut / 2,
                p_haut.y(),
            ),
        )

        path.lineTo(
            p_haut.x() + largeur_haut / 2,
            p_haut.y(),
        )

        path.cubicTo(
            QPointF(
                p_70.x() + largeur_base * 0.29,
                p_70.y(),
            ),
            QPointF(
                p_25.x() + largeur_base * 0.45,
                p_25.y(),
            ),
            QPointF(
                x + largeur_base / 2,
                y_sol,
            ),
        )

        path.closeSubpath()

        # ------------------------------------------------------------------
        # Volume du bois
        # ------------------------------------------------------------------

        gradient = QLinearGradient(
            x - largeur_base / 2,
            0,
            x + largeur_base / 2,
            0,
        )

        gradient.setColorAt(
            0.0,
            _avec_alpha(
                _assombrir(
                    self.couleur_tronc,
                    0.29,
                ),
                opacite,
            ),
        )

        gradient.setColorAt(
            0.34,
            _avec_alpha(
                _eclaircir(
                    self.couleur_tronc,
                    0.10,
                ),
                opacite,
            ),
        )

        gradient.setColorAt(
            0.68,
            _avec_alpha(
                self.couleur_tronc,
                opacite,
            ),
        )

        gradient.setColorAt(
            1.0,
            _avec_alpha(
                _assombrir(
                    self.couleur_tronc,
                    0.24,
                ),
                opacite,
            ),
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient))

        painter.drawPath(path)

        # ------------------------------------------------------------------
        # Écorce
        # ------------------------------------------------------------------

        if niveau_details >= 0.65 and hauteur >= 80:

            pen_ecorce = QPen(
                _avec_alpha(
                    _assombrir(
                        self.couleur_tronc,
                        0.34,
                    ),
                    int(opacite * 0.33),
                )
            )

            pen_ecorce.setWidthF(
                max(
                    0.65,
                    largeur_base * 0.065,
                )
            )

            pen_ecorce.setCapStyle(Qt.PenCapStyle.RoundCap)

            painter.setPen(pen_ecorce)

            for _ in range(3):

                ratio_1 = rng.uniform(
                    0.08,
                    ratio_haut * 0.67,
                )

                ratio_2 = min(
                    ratio_haut * 0.88,
                    ratio_1
                    + rng.uniform(
                        0.07,
                        0.15,
                    ),
                )

                p1 = self._point_axe_arbre(
                    x,
                    y_sol,
                    hauteur,
                    ratio_1,
                    inclinaison,
                )

                p2 = self._point_axe_arbre(
                    x,
                    y_sol,
                    hauteur,
                    ratio_2,
                    inclinaison,
                )

                decalage = largeur_base * rng.uniform(
                    -0.18,
                    0.18,
                )

                painter.drawLine(
                    QPointF(
                        p1.x() + decalage,
                        p1.y(),
                    ),
                    QPointF(
                        p2.x() + decalage * 0.55,
                        p2.y(),
                    ),
                )

    # --------------------------------------------------------------------------
    # Branches des feuillus
    # --------------------------------------------------------------------------

    def _dessiner_branches_feuillu(
        self,
        painter: QPainter,
        x: float,
        y_sol: float,
        hauteur: float,
        inclinaison: float,
        opacite: int,
        graine: int,
        niveau_details: float,
    ) -> None:

        if niveau_details <= 0.20:
            return

        rng = random.Random(graine + 113)

        branches = (
            (
                0.42,
                -1,
                0.19,
                0.16,
            ),
            (
                0.48,
                +1,
                0.22,
                0.20,
            ),
            (
                0.55,
                -1,
                0.15,
                0.15,
            ),
            (
                0.60,
                +1,
                0.14,
                0.14,
            ),
        )

        pen = QPen(
            _avec_alpha(
                _assombrir(
                    self.couleur_tronc,
                    0.10,
                ),
                int(opacite * 0.91),
            )
        )

        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setBrush(Qt.BrushStyle.NoBrush)

        for i, (
            ratio,
            sens,
            dx,
            dy,
        ) in enumerate(branches):

            if i >= 2 and niveau_details < 0.60:
                break

            origine = self._point_axe_arbre(
                x,
                y_sol,
                hauteur,
                ratio,
                inclinaison,
            )

            largeur = hauteur * (0.016 if i < 2 else 0.010)

            pen.setWidthF(
                max(
                    0.8,
                    largeur,
                )
            )

            painter.setPen(pen)

            longueur_x = (
                hauteur
                * dx
                * rng.uniform(
                    0.88,
                    1.10,
                )
            )

            montee = (
                hauteur
                * dy
                * rng.uniform(
                    0.90,
                    1.10,
                )
            )

            destination = QPointF(
                origine.x() + sens * longueur_x,
                origine.y() - montee,
            )

            controle = QPointF(
                origine.x() + sens * longueur_x * 0.46,
                origine.y() - montee * 0.23,
            )

            path = QPainterPath()

            path.moveTo(origine)

            path.quadTo(
                controle,
                destination,
            )

            painter.drawPath(path)

    # --------------------------------------------------------------------------
    # Feuillus
    # --------------------------------------------------------------------------

    def _dessiner_feuillu(
        self,
        painter: QPainter,
        x: float,
        y_sol: float,
        hauteur: float,
        couleur: QColor,
        opacite: int = 255,
        variante: int = 0,
        inclinaison: float = 0.0,
        niveau_details: float = 1.0,
    ) -> None:
        """
        Dessine un arbre feuillu structuré autour d'un même axe.

        Le tronc et les branches sont peints en premier, puis le houppier
        vient les recouvrir partiellement.
        """

        if hauteur <= 0:
            return

        rng = random.Random(self.graine + 9000 + variante)

        couleur = _avec_alpha(
            couleur,
            opacite,
        )

        largeur_tronc = hauteur * rng.uniform(
            0.060,
            0.078,
        )

        # ------------------------------------------------------------------
        # Bois
        # ------------------------------------------------------------------

        self._dessiner_tronc_arbre(
            painter=painter,
            x=x,
            y_sol=y_sol,
            hauteur=hauteur,
            ratio_haut=0.66,
            largeur_base=largeur_tronc,
            inclinaison=inclinaison,
            opacite=opacite,
            graine=(self.graine + variante * 17),
            niveau_details=niveau_details,
        )

        self._dessiner_branches_feuillu(
            painter=painter,
            x=x,
            y_sol=y_sol,
            hauteur=hauteur,
            inclinaison=inclinaison,
            opacite=opacite,
            graine=(self.graine + variante * 31),
            niveau_details=niveau_details,
        )

        # ------------------------------------------------------------------
        # Axe du houppier
        # ------------------------------------------------------------------

        centre_axe = self._point_axe_arbre(
            x,
            y_sol,
            hauteur,
            0.68,
            inclinaison,
        )

        # Toutes les masses sont calculées autour de ce point :
        # le feuillage suit donc naturellement l'inclinaison du tronc.

        masses = (
            # dx     dy     rx     ry
            (-0.18, 0.00, 0.20, 0.17),
            (0.00, -0.11, 0.25, 0.21),
            (0.19, -0.01, 0.20, 0.17),
            (-0.07, 0.12, 0.25, 0.18),
            (0.13, 0.11, 0.23, 0.17),
        )

        painter.setPen(Qt.PenStyle.NoPen)

        # ------------------------------------------------------------------
        # Masses principales
        # ------------------------------------------------------------------

        for i, (
            dx,
            dy,
            rayon_x,
            rayon_y,
        ) in enumerate(masses):

            centre = QPointF(
                centre_axe.x() + dx * hauteur,
                centre_axe.y() + dy * hauteur,
            )

            if i in (0, 2):

                couleur_locale = _assombrir(
                    couleur,
                    0.085,
                )

            elif i == 1:

                couleur_locale = _eclaircir(
                    couleur,
                    0.035,
                )

            else:

                couleur_locale = couleur

            couleur_locale = _avec_alpha(
                couleur_locale,
                opacite,
            )

            painter.setBrush(couleur_locale)

            path = self._creer_masse_feuillage(
                centre=centre,
                rayon_x=(hauteur * rayon_x),
                rayon_y=(hauteur * rayon_y),
                rng=rng,
                irregularite=(0.11 if niveau_details < 0.5 else 0.15),
                n_points=(10 if niveau_details < 0.5 else 12),
            )

            painter.drawPath(path)

        # ------------------------------------------------------------------
        # Petites touches lumineuses
        # ------------------------------------------------------------------

        if niveau_details >= 0.55 and hauteur >= 75:

            couleur_lumiere = _avec_alpha(
                _eclaircir(
                    couleur,
                    0.13,
                ),
                int(opacite * 0.72),
            )

            painter.setBrush(couleur_lumiere)

            reflets = (
                (
                    -0.11,
                    -0.13,
                    0.10,
                    0.065,
                ),
                (
                    0.07,
                    -0.18,
                    0.11,
                    0.070,
                ),
                (
                    0.17,
                    -0.06,
                    0.075,
                    0.050,
                ),
            )

            for (
                dx,
                dy,
                rayon_x,
                rayon_y,
            ) in reflets:

                centre = QPointF(
                    centre_axe.x() + dx * hauteur,
                    centre_axe.y() + dy * hauteur,
                )

                path = self._creer_masse_feuillage(
                    centre=centre,
                    rayon_x=(hauteur * rayon_x),
                    rayon_y=(hauteur * rayon_y),
                    rng=rng,
                    irregularite=0.18,
                    n_points=9,
                )

                painter.drawPath(path)

    # --------------------------------------------------------------------------
    # Conifères
    # --------------------------------------------------------------------------

    def _dessiner_conifere(
        self,
        painter: QPainter,
        x: float,
        y_sol: float,
        hauteur: float,
        couleur: QColor,
        opacite: int = 255,
        variante: int = 0,
        inclinaison: float = 0.0,
        niveau_details: float = 1.0,
    ) -> None:
        """
        Dessine un conifère plus naturel.

        Le tronc monte profondément sous le feuillage et tous les étages
        sont centrés sur le même axe incliné.
        """

        if hauteur <= 0:
            return

        rng = random.Random(self.graine + 12000 + variante)

        couleur = _avec_alpha(
            couleur,
            opacite,
        )

        largeur_tronc = hauteur * rng.uniform(
            0.045,
            0.060,
        )

        # ------------------------------------------------------------------
        # Tronc
        # ------------------------------------------------------------------

        self._dessiner_tronc_arbre(
            painter=painter,
            x=x,
            y_sol=y_sol,
            hauteur=hauteur,
            ratio_haut=0.78,
            largeur_base=largeur_tronc,
            inclinaison=inclinaison,
            opacite=opacite,
            graine=(self.graine + variante * 23),
            niveau_details=(niveau_details * 0.72),
        )

        # ------------------------------------------------------------------
        # Étages du feuillage
        #
        # Les ratios sont mesurés depuis le sommet.
        # Le dernier étage descend presque jusqu'au sol.
        # ------------------------------------------------------------------

        etages = (
            # haut  bas   demi-largeur
            (0.01, 0.30, 0.095),
            (0.15, 0.48, 0.145),
            (0.31, 0.64, 0.195),
            (0.46, 0.79, 0.245),
            (0.60, 0.91, 0.285),
        )

        painter.setPen(Qt.PenStyle.NoPen)

        for i, (
            ratio_haut,
            ratio_bas,
            demi_largeur,
        ) in enumerate(etages):

            sommet = self._point_axe_arbre(
                x,
                y_sol,
                hauteur,
                1.0 - ratio_haut,
                inclinaison,
            )

            base = self._point_axe_arbre(
                x,
                y_sol,
                hauteur,
                1.0 - ratio_bas,
                inclinaison,
            )

            largeur = (
                hauteur
                * demi_largeur
                * rng.uniform(
                    0.94,
                    1.06,
                )
            )

            gauche = QPointF(
                base.x() - largeur,
                base.y()
                + hauteur
                * rng.uniform(
                    -0.008,
                    0.008,
                ),
            )

            droite = QPointF(
                base.x() + largeur,
                base.y()
                + hauteur
                * rng.uniform(
                    -0.008,
                    0.008,
                ),
            )

            path = QPainterPath()

            path.moveTo(sommet)

            # Côté gauche : légèrement bombé.

            path.cubicTo(
                QPointF(
                    sommet.x() - largeur * 0.20,
                    sommet.y() + (base.y() - sommet.y()) * 0.42,
                ),
                QPointF(
                    gauche.x() + largeur * 0.12,
                    gauche.y() - hauteur * 0.025,
                ),
                gauche,
            )

            # Bas de la branche : légèrement retombant.

            path.quadTo(
                QPointF(
                    base.x(),
                    base.y() + hauteur * 0.030,
                ),
                droite,
            )

            # Côté droit.

            path.cubicTo(
                QPointF(
                    droite.x() - largeur * 0.12,
                    droite.y() - hauteur * 0.025,
                ),
                QPointF(
                    sommet.x() + largeur * 0.20,
                    sommet.y() + (base.y() - sommet.y()) * 0.42,
                ),
                sommet,
            )

            path.closeSubpath()

            # Une très légère variation de teinte entre étages
            # évite l'effet d'un seul bloc plat.

            if i <= 1:

                couleur_locale = _eclaircir(
                    couleur,
                    0.025,
                )

            elif i >= 4:

                couleur_locale = _assombrir(
                    couleur,
                    0.05,
                )

            else:

                couleur_locale = couleur

            painter.setBrush(
                _avec_alpha(
                    couleur_locale,
                    opacite,
                )
            )

            painter.drawPath(path)

        # ------------------------------------------------------------------
        # Petite accroche lumineuse
        # ------------------------------------------------------------------

        if niveau_details >= 0.60 and hauteur >= 80:

            pen = QPen(
                _avec_alpha(
                    _eclaircir(
                        couleur,
                        0.18,
                    ),
                    int(opacite * 0.32),
                )
            )

            pen.setWidthF(
                max(
                    0.7,
                    hauteur * 0.006,
                )
            )

            pen.setCapStyle(Qt.PenCapStyle.RoundCap)

            painter.setPen(pen)

            p1 = self._point_axe_arbre(
                x,
                y_sol,
                hauteur,
                0.86,
                inclinaison,
            )

            p2 = QPointF(
                p1.x() - hauteur * 0.075,
                p1.y() + hauteur * 0.075,
            )

            painter.drawLine(
                p1,
                p2,
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

        Chaque arbre possède un indice dans le monde. Cet indice détermine :

            - sa position ;
            - sa hauteur ;
            - son espèce ;
            - son inclinaison ;
            - la forme de son feuillage ;
            - ses branches ;
            - son écorce.

        Un arbre garde donc exactement la même apparence pendant tout le
        défilement.
        """

        densite = max(
            0.20,
            densite,
        )

        proportion_coniferes = max(
            0.0,
            min(
                1.0,
                proportion_coniferes,
            ),
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

            seed = self.graine + graine + indice * 7919

            rng = random.Random(seed)

            # --------------------------------------------------------------
            # Position dans le monde
            # --------------------------------------------------------------

            x_monde = indice * espacement_reel + rng.uniform(
                -espacement_reel * 0.27,
                espacement_reel * 0.27,
            )

            x = rect_scene.left() + x_monde - decalage_monde

            if (
                x < rect_scene.left() - espacement_reel
                or x > rect_scene.right() + espacement_reel
            ):
                continue

            # --------------------------------------------------------------
            # Caractéristiques de l'arbre
            # --------------------------------------------------------------

            hauteur = rect_scene.height() * rng.uniform(
                hauteur_min,
                hauteur_max,
            )

            est_conifere = rng.random() < proportion_coniferes

            # Très légère courbure naturelle.
            #
            # ±0.035 signifie que le sommet ne se décale jamais de plus
            # d'environ 3.5 % de la hauteur totale.

            inclinaison = rng.uniform(
                -0.035,
                0.035,
            )

            # Les petits arbres ont volontairement moins de détails.

            if hauteur < 65:

                niveau_details = 0.20

            elif hauteur < 95:

                niveau_details = 0.55

            else:

                niveau_details = 1.0

            # --------------------------------------------------------------
            # Dessin
            # --------------------------------------------------------------

            if est_conifere:

                self._dessiner_conifere(
                    painter=painter,
                    x=x,
                    y_sol=y_sol,
                    hauteur=hauteur,
                    couleur=couleur,
                    opacite=opacite,
                    variante=seed,
                    inclinaison=(inclinaison * 0.65),
                    niveau_details=niveau_details,
                )

            else:

                self._dessiner_feuillu(
                    painter=painter,
                    x=x,
                    y_sol=y_sol,
                    hauteur=hauteur,
                    couleur=couleur,
                    opacite=opacite,
                    variante=seed,
                    inclinaison=inclinaison,
                    niveau_details=niveau_details,
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
