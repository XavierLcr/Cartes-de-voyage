################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_4                                #
# Onglet 4.4.5 – Classe du sol                                                 #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------

import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

# 1 -- Classe du sol -----------------------------------------------------------


class Sol:
    """
    Dessine un sol pavé en perspective dans la partie basse de la scène.
    """

    def __init__(
        self,
        proportion_hauteur: float = 0.40,
        largeur_pave: float = 95.0,
        hauteur_pave: float = 55.0,
    ):

        self.proportion_hauteur = proportion_hauteur

        # Dimensions approximatives des pavés au premier plan
        self.largeur_pave = largeur_pave
        self.hauteur_pave = hauteur_pave

    # 1 -- Géométrie -----------------------------------------------------------

    def _rect_sol(
        self,
        rect_scene: QRectF,
    ) -> QRectF:
        """Renvoie la zone occupée par le sol."""

        hauteur = rect_scene.height() * self.proportion_hauteur

        return QRectF(
            rect_scene.left(),
            rect_scene.bottom() - hauteur,
            rect_scene.width(),
            hauteur,
        )

    def _positions_lignes(
        self,
        rect: QRectF,
    ) -> list[float]:
        """
        Calcule les limites horizontales des rangées de pavés.

        Les rangées deviennent progressivement plus petites en s'approchant
        de l'horizon.
        """

        positions = [rect.bottom()]

        y = rect.bottom()
        hauteur = self.hauteur_pave

        while y > rect.top():

            # Profondeur 0 = horizon, 1 = premier plan
            profondeur = (y - rect.top()) / rect.height()

            # Les pavés sont beaucoup plus aplatis au loin
            facteur = 0.20 + 0.80 * profondeur

            hauteur_ligne = hauteur * facteur

            y = max(
                rect.top(),
                y - hauteur_ligne,
            )

            positions.append(y)

        return list(reversed(positions))

    # 2 -- Perspective ---------------------------------------------------------

    def _x_perspective(
        self,
        x_bas: float,
        y: float,
        rect: QRectF,
    ) -> float:
        """
        Ramène progressivement les coordonnées horizontales vers le centre
        du sol quand on se rapproche de l'horizon.
        """

        profondeur = (y - rect.top()) / rect.height()

        # On évite une convergence excessive.
        facteur = 0.45 + 0.55 * profondeur

        return rect.center().x() + (x_bas - rect.center().x()) * facteur

    # 3 -- Fond ----------------------------------------------------------------

    def _dessiner_fond(
        self,
        painter: QPainter,
        rect: QRectF,
        theme,
    ) -> None:
        """Dessine la couleur de fond minérale."""

        degrade = QLinearGradient(
            rect.left(),
            rect.top(),
            rect.left(),
            rect.bottom(),
        )

        degrade.setColorAt(
            0.0,
            theme.couleur("pierre_claire"),
        )

        degrade.setColorAt(
            1.0,
            theme.couleur("pierre_foncee"),
        )

        painter.fillRect(
            rect,
            degrade,
        )

    # 4 -- Pavés ---------------------------------------------------------------

    def _dessiner_paves(
        self,
        painter: QPainter,
        rect: QRectF,
        theme,
    ) -> None:
        """Dessine chaque pavé individuellement sous forme de trapèze."""

        lignes = self._positions_lignes(rect)

        couleur_base = QColor(theme.couleur("pierre_claire"))
        couleur_joint = QColor(theme.couleur("pierre_foncee"))
        couleur_joint.setAlpha(125)

        random.seed(18)

        for ligne in range(len(lignes) - 1):

            y_haut = lignes[ligne]
            y_bas = lignes[ligne + 1]

            # Profondeur de la rangée :
            # 0 = horizon, 1 = premier plan
            y_milieu = (y_haut + y_bas) / 2

            profondeur = (y_milieu - rect.top()) / rect.height()

            # Davantage de pavés lorsque la rangée est éloignée.
            # Au premier plan : facteur ≈ 1
            # À l'horizon    : facteur ≈ 2.2
            facteur_nombre = 1.0 + (1.0 - profondeur) * 1.5

            n_colonnes = max(
                1,
                math.ceil(rect.width() / self.largeur_pave * facteur_nombre),
            )

            largeur_reelle = rect.width() / n_colonnes

            # Rangées alternées façon dallage
            decalage = largeur_reelle / 2 if ligne % 2 else 0.0

            # On dépasse volontairement légèrement la scène afin que
            # les demi-pavés des bords soient correctement dessinés.
            debut = -1
            fin = n_colonnes + 1

            for colonne in range(debut, fin):

                x1_bas = rect.left() + colonne * largeur_reelle - decalage

                x2_bas = x1_bas + largeur_reelle

                # Projection des mêmes limites vers la rangée supérieure.
                x1_haut = self._x_perspective(
                    x_bas=x1_bas,
                    y=y_haut,
                    rect=rect,
                )

                x2_haut = self._x_perspective(
                    x_bas=x2_bas,
                    y=y_haut,
                    rect=rect,
                )

                x1_bas_proj = self._x_perspective(
                    x_bas=x1_bas,
                    y=y_bas,
                    rect=rect,
                )

                x2_bas_proj = self._x_perspective(
                    x_bas=x2_bas,
                    y=y_bas,
                    rect=rect,
                )

                chemin = QPainterPath()

                chemin.moveTo(QPointF(x1_haut, y_haut))

                chemin.lineTo(QPointF(x2_haut, y_haut))

                chemin.lineTo(QPointF(x2_bas_proj, y_bas))

                chemin.lineTo(QPointF(x1_bas_proj, y_bas))

                chemin.closeSubpath()

                # Légère variation minérale entre les pavés
                variation = random.randint(-10, 10)

                couleur = QColor(
                    max(0, min(255, couleur_base.red() + variation)),
                    max(0, min(255, couleur_base.green() + variation)),
                    max(0, min(255, couleur_base.blue() + variation)),
                )

                painter.setBrush(couleur)

                painter.setPen(
                    QPen(
                        couleur_joint,
                        1.15,
                    )
                )

                painter.drawPath(chemin)

    # 5 -- Ligne d'horizon -----------------------------------------------------

    def _dessiner_horizon(
        self,
        painter: QPainter,
        rect: QRectF,
        theme,
    ) -> None:
        """Dessine une séparation très discrète entre le sol et le fond."""

        couleur = QColor(theme.couleur("pierre_foncee"))

        couleur.setAlpha(75)

        painter.setPen(
            QPen(
                couleur,
                1.0,
            )
        )

        painter.drawLine(
            QPointF(rect.left(), rect.top()),
            QPointF(rect.right(), rect.top()),
        )

    # 6 -- Dessin principal ----------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        theme,
    ) -> None:
        """Dessine l'ensemble du sol pavé."""

        rect_sol = self._rect_sol(
            rect_scene=rect_scene,
        )

        painter.save()

        painter.setClipRect(rect_sol)

        self._dessiner_fond(
            painter=painter,
            rect=rect_sol,
            theme=theme,
        )

        self._dessiner_paves(
            painter=painter,
            rect=rect_sol,
            theme=theme,
        )

        self._dessiner_horizon(
            painter=painter,
            rect=rect_sol,
            theme=theme,
        )

        painter.restore()
