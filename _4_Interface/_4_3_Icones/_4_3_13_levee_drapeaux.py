################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.13 – Script de création de petits drapeaux                               #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QPolygonF,
    QLinearGradient,
    QRadialGradient,
)

# 1 -- Classe de création de l'icône -------------------------------------------


def _dessiner_icone_drapeaux(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône "pays les plus visités" : mâts de hauteurs variables
    (proportionnelles au nombre de visites) surmontés de fanions colorés,
    façon petit classement en barres, posés sur une ligne de sol.

    Version "design" : ombres douces, dégradés sur les fanions, mâts avec
    reflet et pommeau, ligne de sol en dégradé, anticrénelage.
    """

    COULEURS_DRAPEAUX = [
        QColor("#FF4B4B"),
        QColor("#33D6E8"),
        QColor("#FF5FD8"),
        QColor("#7CFF5C"),
    ]
    COULEUR_MAT = QColor("#6B6B6B")
    COULEUR_MAT_CLAIR = QColor("#9A9A9A")
    COULEUR_SOL = QColor("#8A94A6")
    COULEUR_OMBRE = QColor("#000000")

    # Hauteurs relatives des mâts (1.0 = pays le plus visité)
    # → à remplacer dynamiquement par les données réelles de visites
    HAUTEURS_RELATIVES = [1.0, 0.78, 0.58, 0.40]

    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    cx, cy = centre.x(), centre.y()
    nb_mats = len(HAUTEURS_RELATIVES)
    zone_largeur = taille * 0.72
    x_gauche = cx - zone_largeur / 2
    espace_x = zone_largeur / (nb_mats - 1) if nb_mats > 1 else 0

    y_base = cy + taille * 0.28
    hauteur_max_mat = taille * 0.56
    epaisseur_mat = taille * 0.03
    largeur_drapeau = taille * 0.16
    hauteur_drapeau = taille * 0.12
    rayon_pommeau = taille * 0.022

    # -- Ombre portée douce au sol -------------------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    for i, ratio in enumerate(HAUTEURS_RELATIVES):
        x = x_gauche + i * espace_x
        ombre = QRadialGradient(QPointF(x, y_base + taille * 0.01), taille * 0.05)
        c1 = QColor(COULEUR_OMBRE)
        c1.setAlphaF(0.18)
        c2 = QColor(COULEUR_OMBRE)
        c2.setAlphaF(0.0)
        ombre.setColorAt(0.0, c1)
        ombre.setColorAt(1.0, c2)
        painter.setBrush(QBrush(ombre))
        painter.drawEllipse(
            QPointF(x, y_base + taille * 0.01), taille * 0.05, taille * 0.02
        )

    # -- Ligne de sol en dégradé ----------------------------------------------
    sol_degrade = QLinearGradient(
        QPointF(x_gauche - taille * 0.06, y_base),
        QPointF(x_gauche + zone_largeur + taille * 0.06, y_base),
    )
    c_sol_transp = QColor(COULEUR_SOL)
    c_sol_transp.setAlphaF(0.0)
    c_sol_pleine = QColor(COULEUR_SOL)
    c_sol_pleine.setAlphaF(0.5)
    sol_degrade.setColorAt(0.0, c_sol_transp)
    sol_degrade.setColorAt(0.15, c_sol_pleine)
    sol_degrade.setColorAt(0.85, c_sol_pleine)
    sol_degrade.setColorAt(1.0, c_sol_transp)

    pen_sol = QPen(QBrush(sol_degrade), taille * 0.016)
    pen_sol.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_sol)
    painter.drawLine(
        QPointF(x_gauche - taille * 0.06, y_base),
        QPointF(x_gauche + zone_largeur + taille * 0.06, y_base),
    )

    for i, ratio in enumerate(HAUTEURS_RELATIVES):
        x = x_gauche + i * espace_x
        hauteur_mat = hauteur_max_mat * ratio
        y_sommet = y_base - hauteur_mat

        # -- Mât avec léger dégradé (effet de volume) ------------------------
        mat_degrade = QLinearGradient(
            QPointF(x - epaisseur_mat, 0), QPointF(x + epaisseur_mat, 0)
        )
        mat_degrade.setColorAt(0.0, COULEUR_MAT_CLAIR)
        mat_degrade.setColorAt(0.5, COULEUR_MAT)
        mat_degrade.setColorAt(1.0, COULEUR_MAT)

        pen_mat = QPen(QBrush(mat_degrade), epaisseur_mat)
        pen_mat.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_mat)
        painter.drawLine(QPointF(x, y_base), QPointF(x, y_sommet))

        # -- Pommeau au sommet du mât -----------------------------------------
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(COULEUR_MAT_CLAIR))
        painter.drawEllipse(QPointF(x, y_sommet), rayon_pommeau, rayon_pommeau)

        # -- Fanion triangulaire en dégradé, flottant vers la droite ----------
        couleur_base = COULEURS_DRAPEAUX[i % len(COULEURS_DRAPEAUX)]
        couleur_claire = couleur_base.lighter(130)

        drapeau_degrade = QLinearGradient(
            QPointF(x, y_sommet),
            QPointF(x + largeur_drapeau, y_sommet + hauteur_drapeau * 0.5),
        )
        drapeau_degrade.setColorAt(0.0, couleur_claire)
        drapeau_degrade.setColorAt(1.0, couleur_base)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(drapeau_degrade))
        drapeau = QPolygonF(
            [
                QPointF(x, y_sommet - hauteur_drapeau * 0.05),
                QPointF(x + largeur_drapeau, y_sommet + hauteur_drapeau * 0.5),
                QPointF(x, y_sommet + hauteur_drapeau * 0.95),
            ]
        )
        painter.drawPolygon(drapeau)

        # -- Fin liseré sombre pour détacher le fanion du fond ----------------
        pen_contour = QPen(couleur_base.darker(140))
        pen_contour.setWidthF(taille * 0.006)
        pen_contour.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen_contour)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(drapeau)
