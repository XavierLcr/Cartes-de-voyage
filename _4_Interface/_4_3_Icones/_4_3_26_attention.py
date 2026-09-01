################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.26 – Script de création de l'icône attention                             #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QLinearGradient,
    QPainterPath,
)

# 1 -- Fonction de création de l'icône -------------------------------------------


def _dessiner_icone_avertissement(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône "avertissement" : triangle stylisé aux coins arrondis, dégradé
    orange/jaune, avec un point d'exclamation blanc au centre."""

    COULEUR_TRIANGLE = QColor("#F5D93A")
    COULEUR_CONTOUR = QColor("#F5A623")
    COULEUR_EXCLAMATION = QColor("#414040")

    cx, cy = centre.x(), centre.y()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # -- Dimensions de base ---------------------------------------------
    taille_triangle = taille * 0.90
    arrondi = taille * 0.10

    # Sommets du triangle (haut, bas-gauche, bas-droite)
    hx, hy = cx, cy - taille_triangle * 0.52
    bgx, bgy = cx - taille_triangle * 0.52, cy + taille_triangle * 0.42
    bdx, bdy = cx + taille_triangle * 0.52, cy + taille_triangle * 0.42

    # ============================================================
    # CORPS DU TRIANGLE (coins arrondis)
    # ============================================================
    chemin_triangle = QPainterPath()

    def _point_vers(px, py, qx, qy, distance):
        """Retourne un point situé à `distance` de (px,py) en direction de (qx,qy)."""
        dx, dy = qx - px, qy - py
        longueur = (dx**2 + dy**2) ** 0.5
        return QPointF(px + dx / longueur * distance, py + dy / longueur * distance)

    p1 = _point_vers(hx, hy, bgx, bgy, arrondi)
    p2 = _point_vers(hx, hy, bdx, bdy, arrondi)
    p3 = _point_vers(bgx, bgy, hx, hy, arrondi)
    p4 = _point_vers(bgx, bgy, bdx, bdy, arrondi)
    p5 = _point_vers(bdx, bdy, bgx, bgy, arrondi)
    p6 = _point_vers(bdx, bdy, hx, hy, arrondi)

    chemin_triangle.moveTo(p1)
    chemin_triangle.quadTo(QPointF(hx, hy), p2)
    chemin_triangle.lineTo(p6)
    chemin_triangle.quadTo(QPointF(bdx, bdy), p5)
    chemin_triangle.lineTo(p4)
    chemin_triangle.quadTo(QPointF(bgx, bgy), p3)
    chemin_triangle.lineTo(p1)
    chemin_triangle.closeSubpath()

    degrade_triangle = QLinearGradient(QPointF(cx, hy), QPointF(cx, bgy))
    degrade_triangle.setColorAt(0.0, COULEUR_TRIANGLE.lighter(115))
    degrade_triangle.setColorAt(1.0, COULEUR_TRIANGLE.darker(105))

    pen_triangle = QPen(COULEUR_CONTOUR)
    pen_triangle.setWidthF(taille * 0.03)
    pen_triangle.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen_triangle)
    painter.setBrush(QBrush(degrade_triangle))
    painter.drawPath(chemin_triangle)

    # ============================================================
    # POINT D'EXCLAMATION
    # ============================================================
    largeur_barre = taille * 0.09
    haut_barre = cy - taille_triangle * 0.18
    bas_barre = cy + taille_triangle * 0.06

    pen_exclamation = QPen(COULEUR_EXCLAMATION)
    pen_exclamation.setWidthF(largeur_barre)
    pen_exclamation.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_exclamation)
    painter.drawLine(QPointF(cx, haut_barre), QPointF(cx, bas_barre))

    # -- Point du bas -----------------------------------------------------
    rayon_point = largeur_barre * 0.55
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_EXCLAMATION))
    painter.drawEllipse(
        QPointF(cx, cy + taille_triangle * 0.20), rayon_point, rayon_point
    )
