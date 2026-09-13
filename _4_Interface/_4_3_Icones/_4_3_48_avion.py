################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.48 – Classe de création d'un avion                                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import random
import math

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
        anticipation_rotation: float = 60.0,
        couleur: QColor | str = "#E8ECEF",
        couleur_secondaire: QColor | str = "#9AA7B0",
        couleur_vitre: QColor | str = "#496778",
        graine: int | None = None,
    ) -> None:

        self.taille = taille
        self.vitesse = vitesse
        self.tension = tension
        self.marge_sortie = marge_sortie
        self.anticipation_rotation = anticipation_rotation
        self.repeter_en_boucle = False

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
        """
        Crée un chemin passant par tous les points avec des virages arrondis,
        sans créer les boucles que peut produire une spline Catmull-Rom.
        """

        chemin = QPainterPath()

        if not points:
            return chemin

        if len(points) == 1:
            chemin.moveTo(points[0])
            return chemin

        chemin.moveTo(points[0])

        # Plus cette valeur est grande, plus les virages sont arrondis.
        # On reste volontairement sous 0.5 pour éviter les boucles.
        arrondi = max(
            0.0,
            min(0.45, self.tension * 0.45),
        )

        for i in range(1, len(points) - 1):

            precedent = points[i - 1]
            courant = points[i]
            suivant = points[i + 1]

            # Distances avec les points voisins
            distance_avant = math.hypot(
                courant.x() - precedent.x(),
                courant.y() - precedent.y(),
            )

            distance_apres = math.hypot(
                suivant.x() - courant.x(),
                suivant.y() - courant.y(),
            )

            if distance_avant <= 0 or distance_apres <= 0:
                chemin.lineTo(courant)
                continue

            # Point où commence l'arrondi avant le point courant
            entree = QPointF(
                courant.x() - (courant.x() - precedent.x()) * arrondi,
                courant.y() - (courant.y() - precedent.y()) * arrondi,
            )

            # Point où se termine l'arrondi après le point courant
            sortie = QPointF(
                courant.x() + (suivant.x() - courant.x()) * arrondi,
                courant.y() + (suivant.y() - courant.y()) * arrondi,
            )

            chemin.lineTo(entree)

            # Courbe quadratique autour du point réellement visité
            chemin.quadTo(
                courant,
                sortie,
            )

        chemin.lineTo(points[-1])

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

            if self.repeter_en_boucle == True:
                self._nouveau_passage()
            else:
                self._distance = self._longueur_chemin

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

        distance_avant = max(
            0.0,
            distance - self.anticipation_rotation,
        )
        distance_apres = min(
            self._longueur_chemin,
            distance + self.anticipation_rotation,
        )

        t_avant = chemin.percentAtLength(distance_avant)
        t_apres = chemin.percentAtLength(distance_apres)

        point_avant = chemin.pointAtPercent(t_avant)
        point_apres = chemin.pointAtPercent(t_apres)

        dx = point_apres.x() - point_avant.x()
        dy = point_apres.y() - point_avant.y()

        rotation = math.degrees(
            math.atan2(
                dy,
                dx,
            )
        )

        _dessiner_un_avion(
            painter=painter,
            centre=position,
            taille=self.taille,
            rotation=rotation,
            couleur=self.couleur,
            couleur_secondaire=self.couleur_secondaire,
            couleur_vitre=self.couleur_vitre,
        )
