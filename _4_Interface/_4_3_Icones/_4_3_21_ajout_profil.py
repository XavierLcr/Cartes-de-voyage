################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.21 – Script de création de l'icône d'ajout d'un individu                 #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QRadialGradient,
    QPainterPath,
)

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_icone_ajout_profil(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône "ajouter un profil utilisateur" : silhouette simple en dégradé
    léger, une seule ombre portée, badge "+" agrandi en accent coloré."""

    COULEUR_SILHOUETTE = QColor("#5C6472")
    COULEUR_ACCENT = QColor("#3DDC84")  # vert "ajout" ; changer si besoin

    cx, cy = centre.x(), centre.y()

    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # -- Dimensions de base -------------------------------------------------
    rayon_tete = taille * 0.19
    y_tete = cy - taille * 0.22

    largeur_buste = taille * 0.62
    hauteur_buste = taille * 0.34
    y_buste = cy + taille * 0.10

    # ============================================================
    # OMBRE PORTÉE UNIQUE (englobe toute la silhouette + badge)
    # ============================================================
    painter.setPen(Qt.PenStyle.NoPen)
    ombre = QRadialGradient(QPointF(cx, cy + taille * 0.10), taille * 0.62)
    ombre.setColorAt(0.0, QColor(0, 0, 0, 40))
    ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.setBrush(QBrush(ombre))
    painter.drawEllipse(QPointF(cx, cy + taille * 0.10), taille * 0.55, taille * 0.55)

    # ============================================================
    # BUSTE (dégradé simple, 2 stops)
    # ============================================================
    chemin_buste = QPainterPath()
    chemin_buste.moveTo(cx - largeur_buste / 2, y_buste + hauteur_buste)
    chemin_buste.lineTo(cx - largeur_buste / 2, y_buste + hauteur_buste * 0.35)
    chemin_buste.cubicTo(
        cx - largeur_buste / 2,
        y_buste - hauteur_buste * 0.35,
        cx + largeur_buste / 2,
        y_buste - hauteur_buste * 0.35,
        cx + largeur_buste / 2,
        y_buste + hauteur_buste * 0.35,
    )
    chemin_buste.lineTo(cx + largeur_buste / 2, y_buste + hauteur_buste)
    chemin_buste.closeSubpath()

    degrade_buste = QRadialGradient(
        QPointF(cx, y_buste - hauteur_buste * 0.1), largeur_buste * 0.9
    )
    degrade_buste.setColorAt(0.0, COULEUR_SILHOUETTE.lighter(120))
    degrade_buste.setColorAt(1.0, COULEUR_SILHOUETTE.darker(105))

    pen_contour = QPen(COULEUR_SILHOUETTE.darker(125))
    pen_contour.setWidthF(taille * 0.004)
    painter.setPen(pen_contour)
    painter.setBrush(QBrush(degrade_buste))
    painter.drawPath(chemin_buste)

    # ============================================================
    # TÊTE (même logique de dégradé simple)
    # ============================================================
    degrade_tete = QRadialGradient(
        QPointF(cx, y_tete - rayon_tete * 0.15), rayon_tete * 1.6
    )
    degrade_tete.setColorAt(0.0, COULEUR_SILHOUETTE.lighter(120))
    degrade_tete.setColorAt(1.0, COULEUR_SILHOUETTE.darker(105))

    painter.setPen(pen_contour)
    painter.setBrush(QBrush(degrade_tete))
    painter.drawEllipse(QPointF(cx, y_tete), rayon_tete, rayon_tete)

    # -- Reflet glossy unique, discret, sur la tête --------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    reflet = QColor(255, 255, 255, 90)
    painter.setBrush(QBrush(reflet))
    painter.drawEllipse(
        QPointF(cx - rayon_tete * 0.3, y_tete - rayon_tete * 0.35),
        rayon_tete * 0.28,
        rayon_tete * 0.18,
    )

    # ============================================================
    # BADGE "+" — agrandi, plus lisible
    # ============================================================
    rayon_badge = taille * 0.27  # avant : 0.20
    x_badge = cx + taille * 0.30
    y_badge = cy + taille * 0.30

    degrade_badge = QRadialGradient(
        QPointF(x_badge, y_badge - rayon_badge * 0.2), rayon_badge * 1.5
    )
    degrade_badge.setColorAt(0.0, COULEUR_ACCENT.lighter(125))
    degrade_badge.setColorAt(1.0, COULEUR_ACCENT.darker(105))

    pen_badge = QPen(COULEUR_ACCENT.darker(130))
    pen_badge.setWidthF(taille * 0.005)
    painter.setPen(pen_badge)
    painter.setBrush(QBrush(degrade_badge))
    painter.drawEllipse(QPointF(x_badge, y_badge), rayon_badge, rayon_badge)

    # -- Croix "+" blanche, plus grosse et plus longue -----------------------
    epaisseur_croix = rayon_badge * 0.34  # avant : 0.32
    longueur_croix = (
        rayon_badge * 1.35
    )  # avant : 1.1 (relatif à un badge plus grand → "+" nettement plus visible)

    pen_croix = QPen(QColor("#FFFFFF"))
    pen_croix.setWidthF(epaisseur_croix)
    pen_croix.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_croix)
    painter.drawLine(
        QPointF(x_badge - longueur_croix / 2, y_badge),
        QPointF(x_badge + longueur_croix / 2, y_badge),
    )
    painter.drawLine(
        QPointF(x_badge, y_badge - longueur_croix / 2),
        QPointF(x_badge, y_badge + longueur_croix / 2),
    )
