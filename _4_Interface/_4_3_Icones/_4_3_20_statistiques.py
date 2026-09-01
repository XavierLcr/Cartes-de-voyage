################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.20 – Script de création de l'icône statistiques                          #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QRadialGradient,
    QLinearGradient,
    QPainterPath,
)

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_icone_courbes(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône "statistiques" : un petit graphique à axes avec 3 courbes
    lissées de tendances différentes (hausse, baisse, plateau ondulant),
    chacune avec un point terminal glossy. Traits épaissis pour rester
    lisibles en petite taille. Même esprit que les autres icônes :
    dégradés doux, ombre portée, reflets."""

    COULEUR_AXE = QColor("#C4CAD4")
    COURBES = [
        # (couleur, [liste de points relatifs (x de 0 à 1, y de 0 à 1, 0=haut)])
        (
            QColor("#33C7E8"),
            [(0.0, 0.62), (0.28, 0.45), (0.55, 0.55), (0.78, 0.22), (1.0, 0.12)],
        ),
        (
            QColor("#8C6FFF"),
            [(0.0, 0.30), (0.26, 0.50), (0.52, 0.20), (0.76, 0.42), (1.0, 0.32)],
        ),
        (
            QColor("#FF6F6F"),
            [(0.0, 0.78), (0.30, 0.68), (0.58, 0.80), (0.80, 0.60), (1.0, 0.70)],
        ),
    ]

    cx, cy = centre.x(), centre.y()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    zone_largeur = taille * 0.95
    zone_hauteur = taille * 0.80
    zone_gauche = cx - zone_largeur / 2
    zone_haut = cy - zone_hauteur / 2 - taille * 0.02
    zone_bas = zone_haut + zone_hauteur

    # -- Ombre douce sous la composition ------------------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    ombre = QRadialGradient(QPointF(cx, zone_bas + taille * 0.08), taille * 0.4)
    ombre.setColorAt(0.0, QColor(0, 0, 0, 40))
    ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.setBrush(QBrush(ombre))
    painter.drawEllipse(
        QPointF(cx, zone_bas + taille * 0.06), taille * 0.32, taille * 0.06
    )

    # -- Axes (fines lignes en L, discrètes) --------------------------------------
    pen_axe = QPen(COULEUR_AXE)
    pen_axe.setWidthF(taille * 0.02)
    pen_axe.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_axe)
    painter.drawLine(
        QPointF(zone_gauche, zone_haut - taille * 0.03), QPointF(zone_gauche, zone_bas)
    )
    painter.drawLine(
        QPointF(zone_gauche, zone_bas),
        QPointF(zone_gauche + zone_largeur + taille * 0.03, zone_bas),
    )

    def _point_absolu(p):
        x_rel, y_rel = p
        return QPointF(
            zone_gauche + x_rel * zone_largeur, zone_haut + y_rel * zone_hauteur
        )

    # -- Courbes lissées (Catmull-Rom -> Bézier) ----------------------------------
    for couleur, points_rel in COURBES:
        pts = [_point_absolu(p) for p in points_rel]

        chemin = QPainterPath()
        chemin.moveTo(pts[0])
        for i in range(len(pts) - 1):
            p0 = pts[i - 1] if i > 0 else pts[i]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[i + 2] if i + 2 < len(pts) else pts[i + 1]
            c1 = QPointF(p1.x() + (p2.x() - p0.x()) / 6, p1.y() + (p2.y() - p0.y()) / 6)
            c2 = QPointF(p2.x() - (p3.x() - p1.x()) / 6, p2.y() - (p3.y() - p1.y()) / 6)
            chemin.cubicTo(c1, c2, p2)

        # Ombre légère de la courbe (léger décalage, pour du relief)
        couleur_ombre = couleur.darker(160)
        pen_ombre_courbe = QPen(
            QColor(couleur_ombre.red(), couleur_ombre.green(), couleur_ombre.blue(), 60)
        )
        pen_ombre_courbe.setWidthF(taille * 0.050)
        pen_ombre_courbe.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_ombre_courbe.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen_ombre_courbe)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        chemin_ombre = QPainterPath(chemin)
        chemin_ombre.translate(0, taille * 0.014)
        painter.drawPath(chemin_ombre)

        # Trait principal, dégradé le long du tracé (plus clair -> plus soutenu)
        degrade_ligne = QLinearGradient(zone_gauche, 0, zone_gauche + zone_largeur, 0)
        degrade_ligne.setColorAt(0.0, couleur.lighter(125))
        degrade_ligne.setColorAt(1.0, couleur.darker(105))
        pen_courbe = QPen(QBrush(degrade_ligne), taille * 0.046)
        pen_courbe.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_courbe.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen_courbe)
        painter.drawPath(chemin)

        # Point terminal glossy
        rayon_point = taille * 0.042
        p_fin = pts[-1]
        degrade_point = QRadialGradient(
            QPointF(p_fin.x() - rayon_point * 0.3, p_fin.y() - rayon_point * 0.35),
            rayon_point * 1.6,
        )
        degrade_point.setColorAt(0.0, couleur.lighter(150))
        degrade_point.setColorAt(1.0, couleur.darker(110))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(degrade_point))
        painter.drawEllipse(p_fin, rayon_point, rayon_point)
        painter.setBrush(QBrush(QColor(255, 255, 255, 150)))
        painter.drawEllipse(
            QPointF(p_fin.x() - rayon_point * 0.3, p_fin.y() - rayon_point * 0.35),
            rayon_point * 0.32,
            rayon_point * 0.22,
        )
