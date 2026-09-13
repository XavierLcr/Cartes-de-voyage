################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_4                                #
# Onglet 4.4.6 – Classe des montagnes de fond                                  #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------

import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
)

# 1 -- Classe de montagnes -----------------------------------------------------


class Montagnes:
    """
    Dessine plusieurs chaînes de montagnes en arrière-plan.

    Les montagnes les plus éloignées sont plus claires et plus basses,
    tandis que les montagnes proches sont plus foncées et plus marquées.
    """

    def __init__(
        self,
        proportion_hauteur: float = 0.32,
        n_couches: int = 3,
        graine: int = 24,
    ):

        self.proportion_hauteur = proportion_hauteur
        self.n_couches = n_couches
        self.graine = graine

    # 1 -- Géométrie -----------------------------------------------------------

    def _rect_montagnes(
        self,
        rect_scene: QRectF,
        proportion_sol: float = 0.40,
    ) -> QRectF:
        """
        Renvoie la zone dans laquelle les montagnes sont dessinées.

        La base des montagnes correspond au début du sol.
        """

        y_sol = rect_scene.bottom() - rect_scene.height() * proportion_sol

        hauteur = rect_scene.height() * self.proportion_hauteur

        return QRectF(
            rect_scene.left(),
            y_sol - hauteur,
            rect_scene.width(),
            hauteur,
        )

    # 2 -- Profil d'une chaîne -------------------------------------------------

    def _creer_profil(
        self,
        rect: QRectF,
        profondeur: float,
        graine: int,
    ) -> list[QPointF]:
        """
        Génère une succession de sommets irréguliers.

        profondeur :
            0 = chaîne éloignée
            1 = chaîne proche
        """

        random.seed(graine)

        largeur_segment = 75 - profondeur * 25

        n_points = max(
            6,
            int(rect.width() / largeur_segment),
        )

        points = []

        for i in range(n_points + 1):

            x = rect.left() + rect.width() * i / n_points

            # Les chaînes proches sont plus hautes.
            hauteur_min = rect.height() * (0.15 + profondeur * 0.12)

            hauteur_max = rect.height() * (0.45 + profondeur * 0.35)

            hauteur = random.uniform(
                hauteur_min,
                hauteur_max,
            )

            y = rect.bottom() - hauteur

            points.append(QPointF(x, y))

        return points

    # 3 -- Couleur -------------------------------------------------------------

    def _couleur_couche(
        self,
        theme,
        profondeur: float,
    ) -> QColor:
        """
        Interpole simplement entre la couleur des montagnes lointaines
        et celle des montagnes proches.
        """

        loin = QColor(theme.couleur("montagne_loin"))

        proche = QColor(theme.couleur("montagne_proche"))

        r = int(loin.red() + (proche.red() - loin.red()) * profondeur)

        g = int(loin.green() + (proche.green() - loin.green()) * profondeur)

        b = int(loin.blue() + (proche.blue() - loin.blue()) * profondeur)

        return QColor(r, g, b)

    # 4 -- Dessin d'une chaîne -------------------------------------------------

    def _dessiner_couche(
        self,
        painter: QPainter,
        rect: QRectF,
        theme,
        profondeur: float,
        graine: int,
    ) -> None:
        """Dessine une chaîne complète de montagnes."""

        points = self._creer_profil(
            rect=rect,
            profondeur=profondeur,
            graine=graine,
        )

        if not points:
            return

        chemin = QPainterPath()

        chemin.moveTo(
            QPointF(
                rect.left(),
                rect.bottom(),
            )
        )

        chemin.lineTo(points[0])

        for point in points[1:]:
            chemin.lineTo(point)

        chemin.lineTo(
            QPointF(
                rect.right(),
                rect.bottom(),
            )
        )

        chemin.closeSubpath()

        painter.setPen(
            QColor(
                0,
                0,
                0,
                0,
            )
        )

        painter.setBrush(
            self._couleur_couche(
                theme=theme,
                profondeur=profondeur,
            )
        )

        painter.drawPath(chemin)

    # 5 -- Dessin principal ----------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        theme,
        proportion_sol: float = 0.40,
    ) -> None:
        """Dessine toutes les couches de montagnes."""

        rect = self._rect_montagnes(
            rect_scene=rect_scene,
            proportion_sol=proportion_sol,
        )

        painter.save()

        for i in range(self.n_couches):

            profondeur = i / max(1, self.n_couches - 1)

            # Les couches proches sont légèrement descendues.
            decalage_vertical = profondeur * rect.height() * 0.12

            rect_couche = QRectF(
                rect.left(),
                rect.top() + decalage_vertical,
                rect.width(),
                rect.height(),
            )

            self._dessiner_couche(
                painter=painter,
                rect=rect_couche,
                theme=theme,
                profondeur=profondeur,
                graine=self.graine + i * 17,
            )

        painter.restore()
