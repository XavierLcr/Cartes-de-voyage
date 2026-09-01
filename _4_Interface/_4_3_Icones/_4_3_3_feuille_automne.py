################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.3 – Script de création de l'icône d'une feuille à l'automne              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen

# 1 -- Fonction de dessin d'une feuille isolée ---------------------------------


def _dessiner_forme_feuille(
    painter: QPainter,
    taille: float,
    echelle: float = 1.2,
    opacite: float = 1.0,
) -> None:
    """Dessine une feuille (forme + tige + nervures "creusées") centrée sur
    l'origine (0, 0) du repère courant du painter. L'appelant est
    responsable de la transformation (translate/rotate) avant l'appel, via
    painter.save() / painter.translate() / painter.rotate() / painter.restore().

    `echelle` contrôle la taille de cette feuille par rapport à `taille`.
    `opacite` (0.0 à 1.0) permet d'atténuer les feuilles à l'arrière-plan,
    pour donner une impression de profondeur / d'éloignement.
    """

    def alpha(base: int) -> int:
        return max(0, min(255, round(base * opacite)))

    haut = QPointF(0, -taille * 0.34 * echelle)
    bas = QPointF(0, taille * 0.30 * echelle)

    feuille = QPainterPath()
    feuille.moveTo(bas)
    feuille.cubicTo(
        QPointF(-taille * 0.32 * echelle, taille * 0.12 * echelle),
        QPointF(-taille * 0.28 * echelle, -taille * 0.26 * echelle),
        haut,
    )
    feuille.cubicTo(
        QPointF(taille * 0.28 * echelle, -taille * 0.26 * echelle),
        QPointF(taille * 0.32 * echelle, taille * 0.12 * echelle),
        bas,
    )
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(255, 255, 255, alpha(225))))
    painter.drawPath(feuille)

    # petite tige, en dur (pas "creusée", pour rester bien visible)
    painter.setPen(QPen(QColor(255, 255, 255, alpha(150)), max(1.0, taille * 0.035)))
    painter.drawLine(
        bas,
        QPointF(bas.x() + taille * 0.07 * echelle, bas.y() + taille * 0.1 * echelle),
    )

    # --- nervures "creusées" dans la feuille (transparence) ---
    haut_nervure = QPointF(0, -taille * 0.28 * echelle)
    bas_nervure = QPointF(0, taille * 0.24 * echelle)

    painter.save()
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOut)

    # nervure centrale
    painter.setPen(
        QPen(
            QColor(255, 255, 255, alpha(130)),
            max(0.9, taille * 0.028),
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
        )
    )
    painter.drawLine(haut_nervure, bas_nervure)

    # nervures secondaires, en épi le long de la nervure centrale
    n_paires = 3
    for i in range(1, n_paires + 1):
        t = i / (n_paires + 1)
        point_depart = QPointF(
            haut_nervure.x(),
            haut_nervure.y() + (bas_nervure.y() - haut_nervure.y()) * t,
        )
        longueur = taille * 0.16 * echelle * (1.0 - t * 0.35)
        for signe in (-1, 1):
            point_arrivee = QPointF(
                point_depart.x() + signe * longueur,
                point_depart.y() + longueur * 0.55,
            )
            painter.setPen(
                QPen(
                    QColor(255, 255, 255, alpha(100)),
                    max(0.7, taille * 0.02),
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                )
            )
            painter.drawLine(point_depart, point_arrivee)

    painter.restore()


# 2 -- Fonction principale : scène de feuilles en train de tomber -------------


def _dessiner_icone_feuille(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône automne : une feuille principale au premier plan, accompagnée de
    deux plus petites, décalées et plus transparentes, comme suspendues en
    plein tournoiement dans leur chute. L'image reste fixe, mais les
    différences de taille, d'inclinaison et de position évoquent le
    mouvement."""

    # -- Feuille n°1
    painter.save()
    painter.translate(centre.x() + taille * 0.02, centre.y() + taille * 0.05)
    painter.rotate(-14)
    _dessiner_forme_feuille(painter, taille, echelle=1.1, opacite=1.0)
    painter.restore()

    # -- Feuille n°2
    painter.save()
    painter.translate(centre.x() - taille * 0.3, centre.y() - taille * 0.4)
    painter.rotate(43)
    _dessiner_forme_feuille(painter, taille, echelle=0.8, opacite=0.9)
    painter.restore()

    # -- Feuille n°3
    painter.save()
    painter.translate(centre.x() + taille * 0.43, centre.y() - taille * 0.4)
    painter.rotate(78)
    _dessiner_forme_feuille(painter, taille, echelle=0.55, opacite=0.75)
    painter.restore()

    # -- Feuille n°4
    painter.save()
    painter.translate(centre.x() - taille * 0.48, centre.y() - taille * 0.10)
    painter.rotate(-70)
    _dessiner_forme_feuille(painter, taille, echelle=0.4, opacite=0.55)
    painter.restore()

    # -- Feuille n°5
    painter.save()
    painter.translate(centre.x() - taille * 0.35, centre.y() + taille * 0.4)
    painter.rotate(209)
    _dessiner_forme_feuille(painter, taille, echelle=0.7, opacite=0.85)
    painter.restore()

    # -- Feuille n°6
    painter.save()
    painter.translate(centre.x() + taille * 0.45, centre.y() + taille * 0.35)
    painter.rotate(-120)
    _dessiner_forme_feuille(painter, taille, echelle=0.5, opacite=0.7)
    painter.restore()

    # -- Feuille n°7
    painter.save()
    painter.translate(centre.x() + taille * 0.1, centre.y() + taille * 0.67)
    painter.rotate(28)
    _dessiner_forme_feuille(painter, taille, echelle=0.45, opacite=0.6)
    painter.restore()
