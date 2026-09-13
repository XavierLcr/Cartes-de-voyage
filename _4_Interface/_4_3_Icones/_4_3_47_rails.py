################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.47 – Classe de création de rails                                         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPen,
)

# 1 -- Fonctions utilitaires ---------------------------------------------------


def _normaliser(
    x: float,
    y: float,
) -> tuple[float, float]:
    """Normalise un vecteur 2D."""

    norme = math.hypot(x, y)

    if norme <= 0:
        return 0.0, 0.0

    return x / norme, y / norme


def _normale_chemin(
    chemin: QPainterPath,
    t: float,
) -> QPointF:
    """Calcule la normale locale au chemin pour une position t comprise entre 0 et 1."""

    epsilon = 0.001

    t_avant = max(
        0.0,
        t - epsilon,
    )

    t_apres = min(
        1.0,
        t + epsilon,
    )

    p1 = chemin.pointAtPercent(t_avant)

    p2 = chemin.pointAtPercent(t_apres)

    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()

    dx, dy = _normaliser(
        dx,
        dy,
    )

    return QPointF(
        -dy,
        dx,
    )


def _creer_chemin_rail(
    depart: QPointF,
    arrivee: QPointF,
    courbure: float = 0.15,
) -> QPainterPath:
    """
    Crée le chemin central d'une voie ferrée entre deux points.

    `courbure` :
        0.0  -> voie droite
        > 0  -> courbe dans un sens
        < 0  -> courbe dans l'autre sens
    """

    dx = arrivee.x() - depart.x()
    dy = arrivee.y() - depart.y()

    distance = math.hypot(
        dx,
        dy,
    )

    if distance <= 0:
        return QPainterPath(depart)

    ux = dx / distance
    uy = dy / distance

    # Vecteur perpendiculaire
    nx = -uy
    ny = ux

    decalage = distance * courbure

    # Points de contrôle placés à 1/3 et 2/3 du trajet,
    # décalés dans la même direction pour créer une courbe douce.
    controle_1 = QPointF(
        depart.x() + dx / 3 + nx * decalage,
        depart.y() + dy / 3 + ny * decalage,
    )

    controle_2 = QPointF(
        depart.x() + 2 * dx / 3 + nx * decalage,
        depart.y() + 2 * dy / 3 + ny * decalage,
    )

    chemin = QPainterPath(depart)

    chemin.cubicTo(
        controle_1,
        controle_2,
        arrivee,
    )

    return chemin


# 2 -- Fonction de dessin d'un rail --------------------------------------------


def _dessiner_un_rail(
    painter: QPainter,
    depart: QPointF,
    arrivee: QPointF,
    courbure: float = 0.15,
    ecartement: float = 10.0,
    largeur_rail: float = 2.4,
    largeur_traverse: float = 18.0,
    epaisseur_traverse: float = 3.0,
    espacement_traverses: float = 12.0,
    couleur_rail: QColor | str = "#686868",
    couleur_reflet: QColor | str = "#C8C8C8",
    couleur_traverse: QColor | str = "#71513C",
) -> None:
    """
    Dessine une voie ferrée complète entre deux points.

    La voie comporte :
        - deux rails parallèles ;
        - un léger reflet métallique ;
        - des traverses régulièrement réparties ;
        - une courbe de Bézier contrôlée par `courbure`.
    """

    chemin_central = _creer_chemin_rail(
        depart=depart,
        arrivee=arrivee,
        courbure=courbure,
    )

    longueur = chemin_central.length()

    if longueur <= 0:
        return

    painter.save()

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing,
        True,
    )

    couleur_rail = QColor(couleur_rail)

    couleur_reflet = QColor(couleur_reflet)

    couleur_traverse = QColor(couleur_traverse)

    # -- Traverses -------------------------------------------------------------

    n_traverses = max(
        2,
        int(longueur / espacement_traverses),
    )

    pen_traverse = QPen(couleur_traverse)

    pen_traverse.setWidthF(epaisseur_traverse)

    pen_traverse.setCapStyle(Qt.PenCapStyle.RoundCap)

    painter.setPen(pen_traverse)

    for i in range(n_traverses + 1):

        distance = longueur * i / n_traverses

        t = chemin_central.percentAtLength(distance)

        centre = chemin_central.pointAtPercent(t)

        normale = _normale_chemin(
            chemin_central,
            t,
        )

        demi_largeur = largeur_traverse / 2

        p1 = QPointF(
            centre.x() - normale.x() * demi_largeur,
            centre.y() - normale.y() * demi_largeur,
        )

        p2 = QPointF(
            centre.x() + normale.x() * demi_largeur,
            centre.y() + normale.y() * demi_largeur,
        )

        painter.drawLine(
            p1,
            p2,
        )

    # -- Construction des deux rails ------------------------------------------

    chemin_gauche = QPainterPath()
    chemin_droit = QPainterPath()

    n_points = max(
        40,
        int(longueur / 4),
    )

    demi_ecartement = ecartement / 2

    for i in range(n_points + 1):

        t = i / n_points

        centre = chemin_central.pointAtPercent(t)

        normale = _normale_chemin(
            chemin_central,
            t,
        )

        gauche = QPointF(
            centre.x() - normale.x() * demi_ecartement,
            centre.y() - normale.y() * demi_ecartement,
        )

        droite = QPointF(
            centre.x() + normale.x() * demi_ecartement,
            centre.y() + normale.y() * demi_ecartement,
        )

        if i == 0:

            chemin_gauche.moveTo(gauche)

            chemin_droit.moveTo(droite)

        else:

            chemin_gauche.lineTo(gauche)

            chemin_droit.lineTo(droite)

    # -- Rails métalliques -----------------------------------------------------

    pen_rail = QPen(couleur_rail)

    pen_rail.setWidthF(largeur_rail)

    pen_rail.setCapStyle(Qt.PenCapStyle.RoundCap)

    pen_rail.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

    painter.setPen(pen_rail)

    painter.drawPath(chemin_gauche)

    painter.drawPath(chemin_droit)

    # -- Reflet métallique -----------------------------------------------------

    couleur_reflet.setAlpha(150)

    pen_reflet = QPen(couleur_reflet)

    pen_reflet.setWidthF(
        max(
            0.5,
            largeur_rail * 0.30,
        )
    )

    pen_reflet.setCapStyle(Qt.PenCapStyle.RoundCap)

    pen_reflet.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

    painter.setPen(pen_reflet)

    painter.drawPath(chemin_gauche)

    painter.drawPath(chemin_droit)

    painter.restore()


# 3 -- Classe de gestion des rails ---------------------------------------------


class Rails:
    """
    Gère plusieurs portions de voie ferrée.

    Chaque portion est définie par :
        - un point de départ ;
        - un point d'arrivée ;
        - une courbure propre éventuelle.
    """

    def __init__(
        self,
        couples_points: (
            list[tuple[QPointF, QPointF] | tuple[QPointF, QPointF, float]] | None
        ) = None,
        courbure: float = 0.15,
        ecartement: float = 10.0,
        largeur_rail: float = 2.4,
        largeur_traverse: float = 18.0,
        epaisseur_traverse: float = 3.0,
        espacement_traverses: float = 12.0,
        couleur_rail: QColor | str = "#686868",
        couleur_reflet: QColor | str = "#C8C8C8",
        couleur_traverse: QColor | str = "#71513C",
    ) -> None:

        self.couples_points = couples_points if couples_points is not None else []

        self.courbure = courbure

        self.ecartement = ecartement
        self.largeur_rail = largeur_rail

        self.largeur_traverse = largeur_traverse
        self.epaisseur_traverse = epaisseur_traverse
        self.espacement_traverses = espacement_traverses

        self.couleur_rail = QColor(couleur_rail)

        self.couleur_reflet = QColor(couleur_reflet)

        self.couleur_traverse = QColor(couleur_traverse)

    # 3.1 -- Ajout d'une portion -----------------------------------------------

    def ajouter(
        self,
        depart: QPointF,
        arrivee: QPointF,
        courbure: float | None = None,
    ) -> None:
        """Ajoute une nouvelle portion de voie."""

        if courbure is None:

            self.couples_points.append(
                (
                    depart,
                    arrivee,
                )
            )

        else:

            self.couples_points.append(
                (
                    depart,
                    arrivee,
                    courbure,
                )
            )

    # 3.2 -- Suppression --------------------------------------------------------

    def vider(self) -> None:
        """Supprime toutes les portions de voie."""

        self.couples_points.clear()

    # 3.3 -- Dessin -------------------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
    ) -> None:
        """Dessine toutes les portions de voie."""

        for portion in self.couples_points:

            if len(portion) == 3:

                depart, arrivee, courbure = portion

            else:

                depart, arrivee = portion
                courbure = self.courbure

            _dessiner_un_rail(
                painter=painter,
                depart=depart,
                arrivee=arrivee,
                courbure=courbure,
                ecartement=self.ecartement,
                largeur_rail=self.largeur_rail,
                largeur_traverse=self.largeur_traverse,
                epaisseur_traverse=self.epaisseur_traverse,
                espacement_traverses=self.espacement_traverses,
                couleur_rail=self.couleur_rail,
                couleur_reflet=self.couleur_reflet,
                couleur_traverse=self.couleur_traverse,
            )
