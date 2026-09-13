################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.48 – Classe de création d'un avion                                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import random

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
)

# 1 -- Fonction de dessin d'un avion -------------------------------------------


def _dessiner_un_avion(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    rotation: float = 0.0,
    couleur: QColor | str = "#E8ECEF",
    couleur_secondaire: QColor | str = "#9AA7B0",
    couleur_vitre: QColor | str = "#496778",
) -> None:
    """
    Dessine un avion stylisé vu de dessus.

    `rotation` est exprimée en degrés.
    """

    if taille <= 0:
        return

    couleur = QColor(couleur)
    couleur_secondaire = QColor(couleur_secondaire)
    couleur_vitre = QColor(couleur_vitre)

    longueur = taille
    hauteur = taille * 0.48

    rect = QRectF(
        centre.x() - longueur / 2,
        centre.y() - hauteur / 2,
        longueur,
        hauteur,
    )

    painter.save()

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing,
        True,
    )

    painter.translate(centre)
    painter.rotate(rotation)
    painter.translate(-centre)

    cx = rect.center().x()
    cy = rect.center().y()

    largeur = rect.width()
    hauteur = rect.height()

    # --------------------------------------------------------------------------
    # Ailes
    # --------------------------------------------------------------------------

    ailes = QPainterPath()

    # Aile haute
    ailes.moveTo(
        cx + largeur * 0.08,
        cy - hauteur * 0.04,
    )

    ailes.lineTo(
        cx - largeur * 0.10,
        cy - hauteur * 0.46,
    )

    ailes.lineTo(
        cx - largeur * 0.22,
        cy - hauteur * 0.45,
    )

    ailes.lineTo(
        cx - largeur * 0.09,
        cy - hauteur * 0.045,
    )

    # Aile basse
    ailes.moveTo(
        cx + largeur * 0.08,
        cy + hauteur * 0.04,
    )

    ailes.lineTo(
        cx - largeur * 0.10,
        cy + hauteur * 0.46,
    )

    ailes.lineTo(
        cx - largeur * 0.22,
        cy + hauteur * 0.45,
    )

    ailes.lineTo(
        cx - largeur * 0.09,
        cy + hauteur * 0.045,
    )

    painter.setPen(Qt.PenStyle.NoPen)

    painter.setBrush(couleur_secondaire)

    painter.drawPath(ailes)

    # --------------------------------------------------------------------------
    # Empennage
    # --------------------------------------------------------------------------

    queue = QPainterPath()

    queue.moveTo(
        cx - largeur * 0.33,
        cy - hauteur * 0.03,
    )

    queue.lineTo(
        cx - largeur * 0.45,
        cy - hauteur * 0.19,
    )

    queue.lineTo(
        cx - largeur * 0.49,
        cy - hauteur * 0.18,
    )

    queue.lineTo(
        cx - largeur * 0.41,
        cy - hauteur * 0.02,
    )

    queue.moveTo(
        cx - largeur * 0.33,
        cy + hauteur * 0.03,
    )

    queue.lineTo(
        cx - largeur * 0.45,
        cy + hauteur * 0.19,
    )

    queue.lineTo(
        cx - largeur * 0.49,
        cy + hauteur * 0.18,
    )

    queue.lineTo(
        cx - largeur * 0.41,
        cy + hauteur * 0.02,
    )

    painter.drawPath(queue)

    # --------------------------------------------------------------------------
    # Fuselage
    # --------------------------------------------------------------------------

    fuselage = QPainterPath()

    fuselage.moveTo(
        cx + largeur * 0.48,
        cy,
    )

    fuselage.cubicTo(
        cx + largeur * 0.34,
        cy - hauteur * 0.10,
        cx - largeur * 0.18,
        cy - hauteur * 0.10,
        cx - largeur * 0.40,
        cy - hauteur * 0.055,
    )

    fuselage.lineTo(
        cx - largeur * 0.47,
        cy,
    )

    fuselage.lineTo(
        cx - largeur * 0.40,
        cy + hauteur * 0.055,
    )

    fuselage.cubicTo(
        cx - largeur * 0.18,
        cy + hauteur * 0.10,
        cx + largeur * 0.34,
        cy + hauteur * 0.10,
        cx + largeur * 0.48,
        cy,
    )

    fuselage.closeSubpath()

    gradient = QLinearGradient(
        rect.left(),
        rect.top(),
        rect.right(),
        rect.bottom(),
    )

    gradient.setColorAt(
        0.0,
        couleur.lighter(120),
    )

    gradient.setColorAt(
        0.50,
        couleur,
    )

    gradient.setColorAt(
        1.0,
        couleur.darker(120),
    )

    painter.setBrush(QBrush(gradient))

    painter.drawPath(fuselage)

    # --------------------------------------------------------------------------
    # Cockpit
    # --------------------------------------------------------------------------

    cockpit = QPainterPath()

    cockpit.moveTo(
        cx + largeur * 0.31,
        cy,
    )

    cockpit.cubicTo(
        cx + largeur * 0.25,
        cy - hauteur * 0.045,
        cx + largeur * 0.17,
        cy - hauteur * 0.045,
        cx + largeur * 0.13,
        cy,
    )

    cockpit.cubicTo(
        cx + largeur * 0.17,
        cy + hauteur * 0.045,
        cx + largeur * 0.25,
        cy + hauteur * 0.045,
        cx + largeur * 0.31,
        cy,
    )

    cockpit.closeSubpath()

    painter.setBrush(couleur_vitre)

    painter.drawPath(cockpit)

    painter.restore()


# 2 -- Classe de gestion de l'avion --------------------------------------------


class Avion:
    """
    Gère un avion animé suivant un chemin passant par plusieurs points.

    Le chemin commence hors de la zone à gauche, passe par tous les points
    fournis, puis ressort hors de la zone à droite.
    """

    def __init__(
        self,
        taille: float = 42.0,
        vitesse: float = 120.0,
        tension: float = 0.80,
        marge_sortie: float = 50.0,
        couleur: QColor | str = "#E8ECEF",
        couleur_secondaire: QColor | str = "#9AA7B0",
        couleur_vitre: QColor | str = "#496778",
        graine: int | None = None,
    ) -> None:

        self.taille = taille
        self.vitesse = vitesse
        self.tension = tension
        self.marge_sortie = marge_sortie

        self.couleur = QColor(couleur)
        self.couleur_secondaire = QColor(couleur_secondaire)
        self.couleur_vitre = QColor(couleur_vitre)

        self._rng = random.Random(graine)

        self._y_entree = self._rng.uniform(
            0.15,
            0.85,
        )

        self._y_sortie = self._rng.uniform(
            0.15,
            0.85,
        )

        self._distance = 0.0
        self._longueur_chemin = 0.0

    # 2.1 -- Nouveau passage ----------------------------------------------------

    def _nouveau_passage(self) -> None:

        self._distance = 0.0

        self._y_entree = self._rng.uniform(
            0.15,
            0.85,
        )

        self._y_sortie = self._rng.uniform(
            0.15,
            0.85,
        )

    # 2.2 -- Construction du chemin --------------------------------------------

    def _creer_chemin_lisse(
        self,
        points: list[QPointF],
    ) -> QPainterPath:
        """Crée une courbe douce passant exactement par chaque point."""

        chemin = QPainterPath()

        if not points:
            return chemin

        chemin.moveTo(points[0])

        if len(points) == 1:
            return chemin

        facteur = self.tension / 6

        for i in range(len(points) - 1):

            p0 = points[i - 1] if i > 0 else points[i]

            p1 = points[i]
            p2 = points[i + 1]

            p3 = points[i + 2] if i + 2 < len(points) else p2

            controle_1 = QPointF(
                p1.x() + (p2.x() - p0.x()) * facteur,
                p1.y() + (p2.y() - p0.y()) * facteur,
            )

            controle_2 = QPointF(
                p2.x() - (p3.x() - p1.x()) * facteur,
                p2.y() - (p3.y() - p1.y()) * facteur,
            )

            chemin.cubicTo(
                controle_1,
                controle_2,
                p2,
            )

        return chemin

    def creer_chemin(
        self,
        points_passage: list[QPointF],
        rect_zone: QRectF,
    ) -> QPainterPath:
        """
        Ajoute automatiquement les points d'entrée et de sortie au chemin.
        """

        hauteur = rect_zone.height()

        entree = QPointF(
            rect_zone.left() - self.marge_sortie,
            rect_zone.top() + hauteur * self._y_entree,
        )

        sortie = QPointF(
            rect_zone.right() + self.marge_sortie,
            rect_zone.top() + hauteur * self._y_sortie,
        )

        points = [
            entree,
            *points_passage,
            sortie,
        ]

        return self._creer_chemin_lisse(points)

    # 2.3 -- Animation ----------------------------------------------------------

    def animer(
        self,
        delta_s: float,
    ) -> None:
        """Fait avancer l'avion selon sa vitesse."""

        if self._longueur_chemin <= 0:
            return

        self._distance += self.vitesse * delta_s

        if self._distance >= self._longueur_chemin:

            self._nouveau_passage()

    # 2.4 -- Dessin -------------------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        points_passage: list[QPointF],
        rect_zone: QRectF,
    ) -> None:
        """Construit le chemin courant et dessine l'avion dessus."""

        chemin = self.creer_chemin(
            points_passage=points_passage,
            rect_zone=rect_zone,
        )

        self._longueur_chemin = chemin.length()

        if self._longueur_chemin <= 0:
            return

        distance = min(
            self._distance,
            self._longueur_chemin,
        )

        progression = chemin.percentAtLength(distance)

        position = chemin.pointAtPercent(progression)

        rotation = -chemin.angleAtPercent(progression)

        _dessiner_un_avion(
            painter=painter,
            centre=position,
            taille=self.taille,
            rotation=rotation,
            couleur=self.couleur,
            couleur_secondaire=self.couleur_secondaire,
            couleur_vitre=self.couleur_vitre,
        )
