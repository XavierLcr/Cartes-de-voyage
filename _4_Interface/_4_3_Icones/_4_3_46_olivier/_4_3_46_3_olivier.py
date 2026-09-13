################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones/_4_3_46_olivier                                     #
# 4.3.46.3 – Classe de création d'un olivier                                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


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

# À adapter selon l'emplacement de tes scripts
from _4_Interface._4_3_Icones._4_3_46_olivier._4_3_46_1_olive import Olive
from _4_Interface._4_3_Icones._4_3_46_olivier._4_3_46_2_feuille_olivier import (
    FeuilleOlivier,
)

# 1 -- Classe Olivier ----------------------------------------------------------


class Olivier:
    """
    Représente un olivier méditerranéen stylisé.

    L'arbre possède :
        - un tronc épais, noueux et torsadé ;
        - plusieurs grosses branches irrégulières ;
        - une écorce gris-beige striée et creusée ;
        - un feuillage composé de FeuilleOlivier ;
        - des olives dont la quantité et la maturité varient avec la saison.

    Le décor est généré une seule fois à partir d'une graine, de sorte que
    l'arbre conserve exactement la même forme lors des redimensionnements.
    """

    def __init__(
        self,
        n_feuilles: int = 220,
        n_olives: int = 38,
        couleur_bois: QColor | str = "#817763",
        couleur_bois_clair: QColor | str = "#AAA18A",
        couleur_bois_sombre: QColor | str = "#4F493D",
        couleur_feuille: QColor | str = "#71805D",
        couleur_feuille_dessous: QColor | str = "#ADB29A",
        mois: int = 8,
        graine: int | None = 42,
    ) -> None:

        self.n_feuilles = n_feuilles
        self.n_olives = n_olives

        self.couleur_bois = QColor(couleur_bois)
        self.couleur_bois_clair = QColor(couleur_bois_clair)
        self.couleur_bois_sombre = QColor(couleur_bois_sombre)

        self.couleur_feuille = QColor(couleur_feuille)
        self.couleur_feuille_dessous = QColor(couleur_feuille_dessous)

        self.graine = graine

        # État saisonnier
        self.mois = 8
        self.densite_feuillage = 1.0
        self.densite_olives = 1.0
        self.maturite_olives = 0.35

        # Éléments générés
        self.branches = []
        self.feuilles = []
        self.olives = []

        self._generer()
        self.set_mois(mois)

    # 1.1 -- Saison ------------------------------------------------------------

    def set_mois(
        self,
        mois: int,
    ) -> None:
        """
        Modifie l'état saisonnier de l'olivier.

        La densité du feuillage, la présence des fruits et leur maturité
        évoluent automatiquement selon le mois.
        """

        self.mois = max(
            1,
            min(12, int(mois)),
        )

        # Hiver
        if self.mois in (1, 2):

            self.densite_feuillage = 0.82
            self.densite_olives = 0.05
            self.maturite_olives = 1.0

        # Début du printemps
        elif self.mois in (3, 4):

            self.densite_feuillage = 0.90
            self.densite_olives = 0.0
            self.maturite_olives = 0.0

        # Floraison / nouaison
        elif self.mois == 5:

            self.densite_feuillage = 1.0
            self.densite_olives = 0.05
            self.maturite_olives = 0.0

        # Jeunes olives
        elif self.mois == 6:

            self.densite_feuillage = 1.0
            self.densite_olives = 0.45
            self.maturite_olives = 0.05

        elif self.mois == 7:

            self.densite_feuillage = 1.0
            self.densite_olives = 0.75
            self.maturite_olives = 0.15

        # Été
        elif self.mois == 8:

            self.densite_feuillage = 1.0
            self.densite_olives = 1.0
            self.maturite_olives = 0.30

        elif self.mois == 9:

            self.densite_feuillage = 0.98
            self.densite_olives = 1.0
            self.maturite_olives = 0.50

        # Automne : maturation
        elif self.mois == 10:

            self.densite_feuillage = 0.95
            self.densite_olives = 1.0
            self.maturite_olives = 0.70

        elif self.mois == 11:

            self.densite_feuillage = 0.90
            self.densite_olives = 0.85
            self.maturite_olives = 0.90

        # Fin de récolte
        else:

            self.densite_feuillage = 0.85
            self.densite_olives = 0.35
            self.maturite_olives = 1.0

        # Mise à jour de la maturité de chaque fruit
        for olive in self.olives:

            maturite = self.maturite_olives + olive["decalage_maturite"]

            olive["objet"].maturite = max(
                0.0,
                min(1.0, maturite),
            )

    # 1.2 -- Génération --------------------------------------------------------

    def _generer(self) -> None:
        """Génère la structure fixe de l'arbre."""

        rng = random.Random(self.graine)

        self._generer_branches(rng)
        self._generer_feuilles(rng)
        self._generer_olives(rng)

    def _generer_branches(
        self,
        rng: random.Random,
    ) -> None:
        """Génère les principales branches de l'olivier."""

        self.branches = []

        # Grandes branches structurantes
        destinations = [
            (-0.34, 0.29),
            (-0.23, 0.18),
            (-0.10, 0.12),
            (0.08, 0.10),
            (0.22, 0.18),
            (0.36, 0.30),
            (-0.30, 0.43),
            (0.30, 0.43),
        ]

        for i, (x_fin, y_fin) in enumerate(destinations):

            x_depart = rng.uniform(
                -0.055,
                0.055,
            )

            y_depart = rng.uniform(
                0.54,
                0.68,
            )

            self.branches.append(
                {
                    "x_depart": x_depart,
                    "y_depart": y_depart,
                    "x_fin": x_fin,
                    "y_fin": y_fin,
                    "courbure": rng.uniform(-0.08, 0.08),
                    "epaisseur": rng.uniform(0.018, 0.030),
                    "graine": rng.randint(0, 1_000_000),
                }
            )

    def _generer_feuilles(
        self,
        rng: random.Random,
    ) -> None:
        """Génère la position et l'apparence des feuilles."""

        self.feuilles = []

        # Plusieurs masses forment une couronne irrégulière
        masses = [
            (-0.26, 0.30, 0.18, 0.15),
            (-0.10, 0.21, 0.19, 0.15),
            (0.10, 0.20, 0.20, 0.15),
            (0.27, 0.31, 0.18, 0.15),
            (-0.20, 0.43, 0.20, 0.15),
            (0.02, 0.38, 0.24, 0.18),
            (0.23, 0.44, 0.19, 0.15),
        ]

        for _ in range(self.n_feuilles):

            cx, cy, rx, ry = rng.choice(masses)

            # Répartition approximativement elliptique
            angle = rng.uniform(
                0,
                2 * math.pi,
            )

            rayon = math.sqrt(rng.random())

            x = cx + math.cos(angle) * rx * rayon

            y = cy + math.sin(angle) * ry * rayon

            inclinaison = rng.uniform(
                -85,
                85,
            )

            courbure = rng.uniform(
                -0.55,
                0.55,
            )

            face_dessous = rng.random() < 0.34

            echelle = rng.uniform(
                0.75,
                1.25,
            )

            feuille = FeuilleOlivier(
                couleur=self.couleur_feuille,
                couleur_dessous=self.couleur_feuille_dessous,
                inclinaison=inclinaison,
                courbure=courbure,
                face_dessous=face_dessous,
            )

            self.feuilles.append(
                {
                    "objet": feuille,
                    "x": x,
                    "y": y,
                    "echelle": echelle,
                    "visible": rng.random(),
                }
            )

    def _generer_olives(
        self,
        rng: random.Random,
    ) -> None:
        """Génère les fruits dans la couronne."""

        self.olives = []

        if not self.feuilles:
            return

        for _ in range(self.n_olives):

            feuille_ref = rng.choice(self.feuilles)

            x = feuille_ref["x"] + rng.uniform(-0.018, 0.018)

            y = feuille_ref["y"] + rng.uniform(0.015, 0.045)

            olive = Olive(
                maturite=0.0,
                inclinaison=rng.uniform(
                    -20,
                    20,
                ),
            )

            self.olives.append(
                {
                    "objet": olive,
                    "x": x,
                    "y": y,
                    "echelle": rng.uniform(
                        0.75,
                        1.15,
                    ),
                    "visible": rng.random(),
                    "decalage_maturite": rng.uniform(
                        -0.14,
                        0.14,
                    ),
                }
            )

    # 1.3 -- Tronc -------------------------------------------------------------

    def _creer_tronc(
        self,
        rect: QRectF,
    ) -> QPainterPath:
        """
        Crée le tronc massif et torsadé caractéristique de l'olivier.

        La base est large et irrégulière, puis le tronc se sépare légèrement
        en remontant, ce qui évite l'aspect de cylindre uniforme.
        """

        cx = rect.center().x()

        largeur = rect.width()
        hauteur = rect.height()

        y_bas = rect.bottom()
        y_haut = rect.top() + hauteur * 0.42

        path = QPainterPath()

        # Racine gauche
        path.moveTo(
            cx - largeur * 0.18,
            y_bas,
        )

        # Côté gauche
        path.cubicTo(
            cx - largeur * 0.15,
            y_bas - hauteur * 0.08,
            cx - largeur * 0.11,
            y_bas - hauteur * 0.23,
            cx - largeur * 0.095,
            y_bas - hauteur * 0.34,
        )

        path.cubicTo(
            cx - largeur * 0.10,
            y_bas - hauteur * 0.44,
            cx - largeur * 0.045,
            y_haut + hauteur * 0.035,
            cx - largeur * 0.025,
            y_haut,
        )

        # Partie supérieure
        path.lineTo(
            cx + largeur * 0.045,
            y_haut + hauteur * 0.005,
        )

        # Côté droit tortueux
        path.cubicTo(
            cx + largeur * 0.095,
            y_haut + hauteur * 0.09,
            cx + largeur * 0.070,
            y_bas - hauteur * 0.34,
            cx + largeur * 0.125,
            y_bas - hauteur * 0.20,
        )

        path.cubicTo(
            cx + largeur * 0.15,
            y_bas - hauteur * 0.11,
            cx + largeur * 0.21,
            y_bas - hauteur * 0.045,
            cx + largeur * 0.22,
            y_bas,
        )

        # Racines irrégulières
        path.lineTo(
            cx + largeur * 0.08,
            y_bas - hauteur * 0.010,
        )

        path.quadTo(
            cx,
            y_bas + hauteur * 0.008,
            cx - largeur * 0.18,
            y_bas,
        )

        path.closeSubpath()

        return path

    def _dessiner_tronc(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine le vieux bois torsadé de l'olivier."""

        forme = self._creer_tronc(rect)

        cx = rect.center().x()

        # -- Dégradé principal -------------------------------------------------

        gradient = QLinearGradient(
            rect.left(),
            0,
            rect.right(),
            0,
        )

        gradient.setColorAt(
            0.0,
            self.couleur_bois_sombre,
        )

        gradient.setColorAt(
            0.22,
            self.couleur_bois,
        )

        gradient.setColorAt(
            0.43,
            self.couleur_bois_clair,
        )

        gradient.setColorAt(
            0.62,
            self.couleur_bois,
        )

        gradient.setColorAt(
            0.82,
            self.couleur_bois_clair.darker(112),
        )

        gradient.setColorAt(
            1.0,
            self.couleur_bois_sombre,
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient))

        painter.drawPath(forme)

        # -- Creux sombre du vieux bois ---------------------------------------

        creux = QPainterPath()

        creux.moveTo(
            cx - rect.width() * 0.015,
            rect.bottom() - rect.height() * 0.08,
        )

        creux.cubicTo(
            cx - rect.width() * 0.045,
            rect.bottom() - rect.height() * 0.20,
            cx + rect.width() * 0.025,
            rect.bottom() - rect.height() * 0.31,
            cx + rect.width() * 0.005,
            rect.bottom() - rect.height() * 0.43,
        )

        creux.cubicTo(
            cx + rect.width() * 0.060,
            rect.bottom() - rect.height() * 0.30,
            cx + rect.width() * 0.030,
            rect.bottom() - rect.height() * 0.16,
            cx + rect.width() * 0.035,
            rect.bottom() - rect.height() * 0.08,
        )

        creux.closeSubpath()

        couleur_creux = QColor("#343129")

        painter.setBrush(couleur_creux)

        painter.drawPath(creux)

        # Petit reflet interne
        contour_creux = QPen(QColor(185, 175, 150, 70))

        contour_creux.setWidthF(
            max(
                0.7,
                rect.width() * 0.004,
            )
        )

        painter.setPen(contour_creux)

        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawPath(creux)

        # -- Stries de l'écorce ------------------------------------------------

        rng = random.Random(None if self.graine is None else self.graine + 452)

        painter.save()
        painter.setClipPath(forme)

        for _ in range(22):

            x = (
                cx
                + rng.uniform(
                    -0.11,
                    0.11,
                )
                * rect.width()
            )

            y1 = (
                rect.bottom()
                - rng.uniform(
                    0.05,
                    0.43,
                )
                * rect.height()
            )

            longueur = rect.height() * rng.uniform(
                0.06,
                0.18,
            )

            deviation = rect.width() * rng.uniform(
                -0.018,
                0.018,
            )

            couleur = QColor(self.couleur_bois_sombre)

            couleur.setAlpha(
                rng.randint(
                    45,
                    95,
                )
            )

            pen = QPen(couleur)

            pen.setWidthF(
                max(
                    0.45,
                    rect.width()
                    * rng.uniform(
                        0.002,
                        0.006,
                    ),
                )
            )

            pen.setCapStyle(Qt.PenCapStyle.RoundCap)

            painter.setPen(pen)

            path = QPainterPath()

            path.moveTo(
                x,
                y1,
            )

            path.cubicTo(
                x + deviation,
                y1 - longueur * 0.35,
                x - deviation,
                y1 - longueur * 0.70,
                x + deviation * 0.5,
                y1 - longueur,
            )

            painter.drawPath(path)

        painter.restore()

    # 1.4 -- Branches ----------------------------------------------------------

    def _dessiner_branches(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine les grosses branches sous le feuillage."""

        cx = rect.center().x()

        for branche in self.branches:

            depart = QPointF(
                cx + rect.width() * branche["x_depart"],
                rect.top() + rect.height() * branche["y_depart"],
            )

            fin = QPointF(
                cx + rect.width() * branche["x_fin"],
                rect.top() + rect.height() * branche["y_fin"],
            )

            dx = fin.x() - depart.x()

            dy = fin.y() - depart.y()

            courbure = rect.width() * branche["courbure"]

            path = QPainterPath()

            path.moveTo(depart)

            path.cubicTo(
                QPointF(
                    depart.x() + dx * 0.30 + courbure,
                    depart.y() + dy * 0.25,
                ),
                QPointF(
                    depart.x() + dx * 0.72 - courbure * 0.4,
                    depart.y() + dy * 0.70,
                ),
                fin,
            )

            largeur = rect.width() * branche["epaisseur"]

            # Contour sombre
            pen = QPen(self.couleur_bois_sombre)

            pen.setWidthF(largeur * 1.25)

            pen.setCapStyle(Qt.PenCapStyle.RoundCap)

            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

            painter.setPen(pen)

            painter.drawPath(path)

            # Bois principal
            pen = QPen(self.couleur_bois)

            pen.setWidthF(largeur)

            pen.setCapStyle(Qt.PenCapStyle.RoundCap)

            painter.setPen(pen)

            painter.drawPath(path)

            # Ligne claire irrégulière
            couleur_reflet = QColor(self.couleur_bois_clair)

            couleur_reflet.setAlpha(100)

            pen = QPen(couleur_reflet)

            pen.setWidthF(
                max(
                    0.6,
                    largeur * 0.18,
                )
            )

            painter.setPen(pen)

            painter.drawPath(path)

    # 1.5 -- Feuillage ---------------------------------------------------------

    def _dessiner_feuilles(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:

        largeur_base = rect.width() * 0.025

        hauteur_base = rect.height() * 0.070

        for infos in self.feuilles:

            if infos["visible"] > self.densite_feuillage:
                continue

            largeur = largeur_base * infos["echelle"]

            hauteur = hauteur_base * infos["echelle"]

            x = rect.center().x() + rect.width() * infos["x"]

            y = rect.top() + rect.height() * infos["y"]

            rect_feuille = QRectF(
                x - largeur / 2,
                y - hauteur / 2,
                largeur,
                hauteur,
            )

            infos["objet"].dessiner(
                painter=painter,
                rect=rect_feuille,
            )

    # 1.6 -- Olives ------------------------------------------------------------

    def _dessiner_olives(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:

        largeur_base = rect.width() * 0.020

        hauteur_base = rect.height() * 0.038

        for infos in self.olives:

            if infos["visible"] > self.densite_olives:
                continue

            largeur = largeur_base * infos["echelle"]

            hauteur = hauteur_base * infos["echelle"]

            x = rect.center().x() + rect.width() * infos["x"]

            y = rect.top() + rect.height() * infos["y"]

            rect_olive = QRectF(
                x - largeur / 2,
                y - hauteur / 2,
                largeur,
                hauteur,
            )

            infos["objet"].dessiner(
                painter=painter,
                rect=rect_olive,
            )

    # 1.7 -- Dessin complet ----------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine l'olivier complet."""

        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        # Branches arrière
        self._dessiner_branches(
            painter=painter,
            rect=rect,
        )

        # Tronc
        self._dessiner_tronc(
            painter=painter,
            rect=rect,
        )

        # Feuillage
        self._dessiner_feuilles(
            painter=painter,
            rect=rect,
        )

        # Fruits au premier plan
        self._dessiner_olives(
            painter=painter,
            rect=rect,
        )

        painter.restore()
