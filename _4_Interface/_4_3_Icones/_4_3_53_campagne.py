################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.53 – Classe de création d'un paysage de campagne                         #
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


# 2 -- Classe de paysage -------------------------------------------------------


class PaysageCampagne:
    """
    Dessine un paysage de campagne destiné à défiler derrière le train.

    Le décor est composé de plusieurs profondeurs :

        - ciel ;
        - petites collines lointaines ;
        - champs ;
        - haies et arbres proches ;
        - poteaux télégraphiques optionnels.

    Chaque plan se déplace à une vitesse différente afin de créer un
    effet de parallaxe.

    `distance` correspond à la distance visuelle parcourue par le train.
    """

    def __init__(
        self,
        graine: int = 24,
        couleur_ciel_haut: QColor | str = "#BFDDEB",
        couleur_ciel_bas: QColor | str = "#EAF2E7",
        couleur_colline_loin: QColor | str = "#A7BE92",
        couleur_colline_proche: QColor | str = "#789567",
        couleur_champ_1: QColor | str = "#C9B86D",
        couleur_champ_2: QColor | str = "#94A969",
        couleur_haie: QColor | str = "#526F4C",
        couleur_tronc: QColor | str = "#76563D",
        couleur_feuillage: QColor | str = "#537B50",
        couleur_poteau: QColor | str = "#5C5144",
        poteaux: bool = True,
    ):
        self.graine = graine

        self.couleur_ciel_haut = _qcolor(couleur_ciel_haut)
        self.couleur_ciel_bas = _qcolor(couleur_ciel_bas)

        self.couleur_colline_loin = _qcolor(couleur_colline_loin)
        self.couleur_colline_proche = _qcolor(couleur_colline_proche)

        self.couleur_champ_1 = _qcolor(couleur_champ_1)
        self.couleur_champ_2 = _qcolor(couleur_champ_2)

        self.couleur_haie = _qcolor(couleur_haie)
        self.couleur_tronc = _qcolor(couleur_tronc)
        self.couleur_feuillage = _qcolor(couleur_feuillage)

        self.couleur_poteau = _qcolor(couleur_poteau)

        self.poteaux = poteaux

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    @staticmethod
    def _y_horizon(
        rect_scene: QRectF,
        y_rail: float,
    ) -> float:
        """Position approximative de l'horizon."""
        return rect_scene.top() + (y_rail - rect_scene.top()) * 0.58

    # --------------------------------------------------------------------------
    # Ciel
    # --------------------------------------------------------------------------

    def _dessiner_ciel(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
    ) -> None:
        """Dessine le ciel."""
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
    # Collines
    # --------------------------------------------------------------------------

    def _profil_collines(
        self,
        rect_scene: QRectF,
        y_base: float,
        hauteur: float,
        largeur_bloc: float,
        decalage: float,
        graine: int,
    ) -> QPainterPath:
        """Crée un profil continu de petites collines."""
        rng = random.Random(graine)

        # On génère suffisamment de points pour couvrir largement l'écran.
        n_points = max(
            8,
            int(rect_scene.width() / largeur_bloc) + 5,
        )

        valeurs = [
            rng.uniform(
                0.35,
                1.0,
            )
            for _ in range(n_points)
        ]

        # La première et la dernière valeur sont identiques pour rendre
        # le motif plus facile à répéter.
        if len(valeurs) >= 2:
            valeurs[-1] = valeurs[0]

        chemin = QPainterPath()

        chemin.moveTo(
            rect_scene.left(),
            y_base,
        )

        premier = True

        for i in range(n_points):

            x = rect_scene.left() + i * largeur_bloc - decalage

            y = y_base - hauteur * valeurs[i]

            if premier:
                chemin.lineTo(
                    x,
                    y,
                )
                premier = False

            else:
                # Courbe légère plutôt qu'une suite de segments anguleux.
                precedent_x = rect_scene.left() + (i - 1) * largeur_bloc - decalage

                x_milieu = (precedent_x + x) / 2

                chemin.quadTo(
                    QPointF(
                        x_milieu,
                        y,
                    ),
                    QPointF(
                        x,
                        y,
                    ),
                )

        chemin.lineTo(
            rect_scene.right(),
            y_base,
        )

        chemin.closeSubpath()

        return chemin

    def _dessiner_collines(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
        distance: float,
    ) -> None:
        """Dessine deux niveaux de collines."""

        # Collines très lointaines
        decalage_loin = (distance * 0.035) % 180

        chemin_loin = self._profil_collines(
            rect_scene=rect_scene,
            y_base=y_horizon + rect_scene.height() * 0.045,
            hauteur=rect_scene.height() * 0.12,
            largeur_bloc=180,
            decalage=decalage_loin,
            graine=self.graine,
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(self.couleur_colline_loin)

        painter.drawPath(chemin_loin)

        # Collines plus proches
        decalage_proche = (distance * 0.070) % 135

        chemin_proche = self._profil_collines(
            rect_scene=rect_scene,
            y_base=y_horizon + rect_scene.height() * 0.11,
            hauteur=rect_scene.height() * 0.15,
            largeur_bloc=135,
            decalage=decalage_proche,
            graine=self.graine + 17,
        )

        painter.setBrush(self.couleur_colline_proche)

        painter.drawPath(chemin_proche)

    # --------------------------------------------------------------------------
    # Champs
    # --------------------------------------------------------------------------

    def _dessiner_champs(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
        y_rail: float,
        distance: float,
    ) -> None:
        """Dessine quelques bandes de champs."""

        hauteur_zone = y_rail - y_horizon

        if hauteur_zone <= 0:
            return

        # Fond principal
        rect_champ = QRectF(
            rect_scene.left(),
            y_horizon,
            rect_scene.width(),
            y_rail - y_horizon,
        )

        gradient = QLinearGradient(
            rect_champ.topLeft(),
            rect_champ.bottomLeft(),
        )

        gradient.setColorAt(
            0.0,
            _eclaircir(
                self.couleur_champ_1,
                0.12,
            ),
        )

        gradient.setColorAt(
            1.0,
            self.couleur_champ_2,
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient))

        painter.drawRect(rect_champ)

        # Quelques longues bandes donnent l'impression de parcelles.
        decalage = (distance * 0.12) % 260

        largeur_parcelle = 260.0

        x = rect_scene.left() - largeur_parcelle - decalage

        index = 0

        while x < rect_scene.right() + largeur_parcelle:

            couleur = self.couleur_champ_1 if index % 2 == 0 else self.couleur_champ_2

            path = QPainterPath()

            path.moveTo(
                x,
                y_horizon + hauteur_zone * 0.50,
            )

            path.lineTo(
                x + largeur_parcelle * 0.65,
                y_horizon + hauteur_zone * 0.46,
            )

            path.lineTo(
                x + largeur_parcelle,
                y_rail,
            )

            path.lineTo(
                x - largeur_parcelle * 0.15,
                y_rail,
            )

            path.closeSubpath()

            painter.setBrush(
                _avec_alpha(
                    couleur,
                    120,
                )
            )

            painter.drawPath(path)

            x += largeur_parcelle
            index += 1

    # --------------------------------------------------------------------------
    # Arbres
    # --------------------------------------------------------------------------

    def _dessiner_arbre(
        self,
        painter: QPainter,
        centre_x: float,
        y_sol: float,
        taille: float,
    ) -> None:
        """Dessine un petit arbre stylisé."""

        hauteur_tronc = taille * 0.55
        largeur_tronc = taille * 0.12

        rect_tronc = QRectF(
            centre_x - largeur_tronc / 2,
            y_sol - hauteur_tronc,
            largeur_tronc,
            hauteur_tronc,
        )

        gradient_tronc = QLinearGradient(
            rect_tronc.topLeft(),
            rect_tronc.topRight(),
        )

        gradient_tronc.setColorAt(
            0.0,
            _assombrir(
                self.couleur_tronc,
                0.18,
            ),
        )

        gradient_tronc.setColorAt(
            0.5,
            _eclaircir(
                self.couleur_tronc,
                0.10,
            ),
        )

        gradient_tronc.setColorAt(
            1.0,
            _assombrir(
                self.couleur_tronc,
                0.20,
            ),
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient_tronc))

        painter.drawRoundedRect(
            rect_tronc,
            largeur_tronc * 0.30,
            largeur_tronc * 0.30,
        )

        # Feuillage composé de plusieurs masses rondes.
        centres = (
            (-0.22, -0.28, 0.40),
            (0.20, -0.30, 0.38),
            (0.00, -0.53, 0.45),
            (-0.05, -0.10, 0.48),
        )

        for dx, dy, proportion in centres:

            rayon = taille * proportion

            couleur = _melanger(
                self.couleur_feuillage,
                "#FFFFFF",
                0.05 + max(0.0, -dy) * 0.10,
            )

            painter.setBrush(couleur)

            painter.drawEllipse(
                QPointF(
                    centre_x + dx * taille,
                    y_sol - hauteur_tronc + dy * taille,
                ),
                rayon,
                rayon * 0.80,
            )

    def _dessiner_premier_plan(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_rail: float,
        distance: float,
    ) -> None:
        """Dessine les haies, arbres et poteaux proches."""

        # ------------------------------------------------------------------
        # Haie
        # ------------------------------------------------------------------

        y_haie = y_rail - rect_scene.height() * 0.055

        hauteur_haie = rect_scene.height() * 0.035

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(self.couleur_haie)

        painter.drawRect(
            QRectF(
                rect_scene.left(),
                y_haie,
                rect_scene.width(),
                hauteur_haie,
            )
        )

        # ------------------------------------------------------------------
        # Arbres
        # ------------------------------------------------------------------

        espacement = max(
            210.0,
            rect_scene.width() * 0.20,
        )

        decalage = (distance * 0.25) % espacement

        x = rect_scene.left() - espacement - decalage

        index = 0

        while x < rect_scene.right() + espacement:

            rng = random.Random(self.graine + 100 + index)

            taille = rect_scene.height() * rng.uniform(
                0.075,
                0.12,
            )

            self._dessiner_arbre(
                painter=painter,
                centre_x=x,
                y_sol=y_haie + hauteur_haie,
                taille=taille,
            )

            x += espacement
            index += 1

        # ------------------------------------------------------------------
        # Poteaux télégraphiques
        # ------------------------------------------------------------------

        if not self.poteaux:
            return

        espacement_poteaux = 320.0

        decalage_poteaux = (distance * 0.38) % espacement_poteaux

        x = rect_scene.left() - espacement_poteaux - decalage_poteaux

        y_sol = y_rail - rect_scene.height() * 0.012

        hauteur = rect_scene.height() * 0.16

        pen = QPen(self.couleur_poteau)

        pen.setWidthF(
            max(
                1.5,
                rect_scene.height() * 0.008,
            )
        )

        painter.setPen(pen)

        while x < rect_scene.right() + espacement_poteaux:

            y_haut = y_sol - hauteur

            # Mât
            painter.drawLine(
                QPointF(
                    x,
                    y_sol,
                ),
                QPointF(
                    x,
                    y_haut,
                ),
            )

            # Traverse
            largeur = rect_scene.height() * 0.065

            painter.drawLine(
                QPointF(
                    x - largeur / 2,
                    y_haut + hauteur * 0.12,
                ),
                QPointF(
                    x + largeur / 2,
                    y_haut + hauteur * 0.12,
                ),
            )

            x += espacement_poteaux

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
        Dessine le paysage complet.

        Le paysage doit être peint avant :
            - la gare ;
            - les rails ;
            - le train.

        `distance` doit idéalement être la même distance globale que celle
        utilisée pour le défilement des rails.
        """
        if rect_scene.width() <= 0 or rect_scene.height() <= 0:
            return

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        y_horizon = self._y_horizon(
            rect_scene,
            y_rail,
        )

        self._dessiner_ciel(
            painter,
            rect_scene,
            y_horizon,
        )

        self._dessiner_collines(
            painter,
            rect_scene,
            y_horizon,
            distance,
        )

        self._dessiner_champs(
            painter,
            rect_scene,
            y_horizon,
            y_rail,
            distance,
        )

        self._dessiner_premier_plan(
            painter,
            rect_scene,
            y_rail,
            distance,
        )

        painter.restore()
