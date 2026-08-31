################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.24 – Script de création d'un icône d'éventail                            #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QRadialGradient,
    QPainterPath,
)

COULEUR_EVENTAIL = "#4FBAD8"

# 1 -- Éventail générique (fermé ou ouvert selon l'angle) ------------------------


def _dessiner_eventail(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    angle_ouverture_deg: float,
    couleur: QColor,
) -> None:
    """Dessine un éventail en papier vu de face, pivot en bas, dont
    l'angle d'ouverture détermine s'il est fermé (baguette fine) ou
    ouvert (large arc de plis). Sert de base commune aux icônes
    'déplier' et 'replier' de l'arbre."""

    cx, cy = centre.x(), centre.y()
    x_pivot = cx
    y_pivot = cy + taille * 0.36

    rayon_ext = taille * 0.56
    rayon_int = taille * 0.10
    demi_angle = angle_ouverture_deg / 2.0

    def point_arc(rayon: float, angle_deg: float) -> QPointF:
        theta = math.radians(angle_deg)
        return QPointF(
            x_pivot + rayon * math.sin(theta), y_pivot - rayon * math.cos(theta)
        )

    n_segments = 24

    # -- Ombre portée unique -------------------------------------------------
    # painter.setPen(Qt.PenStyle.NoPen)
    # ombre = QRadialGradient(QPointF(cx, cy + taille * 0.10), taille * 0.6)
    # ombre.setColorAt(0.0, QColor(0, 0, 0, 35))
    # ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
    # painter.setBrush(QBrush(ombre))
    # painter.drawEllipse(QPointF(cx, cy + taille * 0.10), taille * 0.5, taille * 0.5)

    # -- Corps de l'éventail (anneau d'arc rempli) ----------------------------
    chemin = QPainterPath()
    chemin.moveTo(point_arc(rayon_ext, -demi_angle))
    for i in range(1, n_segments + 1):
        a = -demi_angle + (angle_ouverture_deg * i / n_segments)
        chemin.lineTo(point_arc(rayon_ext, a))
    for i in range(n_segments + 1):
        a = demi_angle - (angle_ouverture_deg * i / n_segments)
        chemin.lineTo(point_arc(rayon_int, a))
    chemin.closeSubpath()

    degrade = QRadialGradient(QPointF(x_pivot, y_pivot), rayon_ext * 1.1)
    degrade.setColorAt(0.0, couleur.lighter(130))
    degrade.setColorAt(1.0, couleur.darker(108))

    pen_contour = QPen(couleur.darker(130))
    pen_contour.setWidthF(taille * 0.004)
    pen_contour.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen_contour)
    painter.setBrush(QBrush(degrade))
    painter.drawPath(chemin)

    # -- Plis (fines lignes radiales, façon baguettes d'éventail) ------------
    pen_pli = QPen(couleur.darker(145))
    pen_pli.setWidthF(taille * 0.012)
    pen_pli.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_pli)
    n_plis = 5
    for i in range(n_plis):
        a = -demi_angle + (angle_ouverture_deg * i / (n_plis - 1)) if n_plis > 1 else 0
        painter.drawLine(point_arc(rayon_int * 1.3, a), point_arc(rayon_ext * 0.96, a))

    # -- Reflet glossy discret -------------------------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    reflet = QColor(255, 255, 255, 70)
    painter.setBrush(QBrush(reflet))
    a_reflet = -demi_angle * 0.35
    p_reflet = point_arc(rayon_ext * 0.55, a_reflet)
    painter.drawEllipse(p_reflet, taille * 0.05, taille * 0.08)

    # -- Rivet (pivot) -----------------------------------------------------
    degrade_rivet = QRadialGradient(
        QPointF(x_pivot - taille * 0.01, y_pivot - taille * 0.01), taille * 0.06
    )
    degrade_rivet.setColorAt(0.0, QColor("#F2E7C9"))
    degrade_rivet.setColorAt(1.0, QColor("#C9B074"))
    pen_rivet = QPen(QColor("#8A7440"))
    pen_rivet.setWidthF(taille * 0.003)
    painter.setPen(pen_rivet)
    painter.setBrush(QBrush(degrade_rivet))
    painter.drawEllipse(QPointF(x_pivot, y_pivot), taille * 0.05, taille * 0.05)


# 2 -- Icône "déplier l'arbre" (éventail ouvert) ----------------------------------


def _dessiner_icone_arbre_deplier(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône 'déplier l'arbre' : éventail grand ouvert."""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    _dessiner_eventail(
        painter,
        centre,
        taille,
        angle_ouverture_deg=130,
        couleur=QColor(COULEUR_EVENTAIL),
    )


# 3 -- Icône "replier l'arbre" (éventail fermé) -----------------------------------


def _dessiner_icone_arbre_replier(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône 'replier l'arbre' : éventail fermé (fine baguette)."""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    _dessiner_eventail(
        painter,
        centre,
        taille,
        angle_ouverture_deg=30,
        couleur=QColor(COULEUR_EVENTAIL),
    )
