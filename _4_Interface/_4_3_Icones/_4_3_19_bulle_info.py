################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.19 – Script de création de l'icône d'une bulle d'info                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QRadialGradient,
    QLinearGradient,
    QConicalGradient,
    QPainterPath,
)

# 1 -- Fonction de création de l'icône ------------------------------------------


def _lerp_couleur(c1: QColor, c2: QColor, t: float) -> QColor:
    """Interpole linéairement entre deux couleurs (t entre 0 et 1)."""
    t = max(0.0, min(1.0, t))
    return QColor(
        round(c1.red() + (c2.red() - c1.red()) * t),
        round(c1.green() + (c2.green() - c1.green()) * t),
        round(c1.blue() + (c2.blue() - c1.blue()) * t),
    )


def _dessiner_icone_information(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône "information" : anneau épais dégradé qui se "brise" en bulles
    de tailles décroissantes, avec un "i" assorti au centre. Style inspiré
    d'une illustration vectorielle moderne, dégradé continu violet -> teal
    (mêmes couleurs que le reste de la palette d'icônes)."""

    COULEUR_A = QColor("#F704C2")
    COULEUR_B = QColor("#697CE7")

    cx, cy = centre.x(), centre.y()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    rayon_anneau = taille * 0.44
    epaisseur = taille * 0.12
    angle_depart = 25.0  # extrémité "teal" de l'anneau (juste au-dessus de 3h)
    balayage = -300.0  # parcourt l'anneau dans le sens horaire
    angle_fin = angle_depart + balayage  # extrémité "violette" (= -275 -> 85°)

    # # -- Ombre douce sous la composition -----------------------------------------
    # painter.setPen(Qt.PenStyle.NoPen)
    # ombre = QRadialGradient(QPointF(cx, cy + rayon_anneau * 0.85), taille * 0.36)
    # ombre.setColorAt(0.0, QColor(0, 0, 0, 45))
    # ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
    # painter.setBrush(QBrush(ombre))
    # painter.drawEllipse(
    #     QPointF(cx, cy + rayon_anneau * 0.82), taille * 0.30, taille * 0.07
    # )

    # -- Anneau principal : dégradé conique violet -> teal ------------------------
    # Le dégradé conique démarre à l'angle de l'extrémité "violette" (angle_fin)
    # et progresse dans le sens anti-horaire (convention Qt) jusqu'à tomber sur
    # l'extrémité "teal" (angle_depart) -- ce qui correspond exactement au
    # grand arc dessiné (sens horaire, de angle_depart à angle_fin).
    degrade_anneau = QConicalGradient(QPointF(cx, cy), angle_fin % 360)
    t_teal = (angle_depart - (angle_fin % 360)) % 360 / 360
    degrade_anneau.setColorAt(0.0, COULEUR_A)
    degrade_anneau.setColorAt(t_teal, COULEUR_B)
    degrade_anneau.setColorAt(1.0, COULEUR_B)

    rect_anneau = QRectF(
        cx - rayon_anneau, cy - rayon_anneau, rayon_anneau * 2, rayon_anneau * 2
    )
    chemin_anneau = QPainterPath()
    chemin_anneau.arcMoveTo(rect_anneau, angle_depart)
    chemin_anneau.arcTo(rect_anneau, angle_depart, balayage)

    pen_anneau = QPen(QBrush(degrade_anneau), epaisseur)
    pen_anneau.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_anneau)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(chemin_anneau)

    # -- "i" assorti au centre, dégradé vertical cohérent --------------------------
    degrade_i = QLinearGradient(
        QPointF(cx, cy - taille * 0.16), QPointF(cx, cy + taille * 0.20)
    )
    degrade_i.setColorAt(0.0, _lerp_couleur(COULEUR_A, COULEUR_B, 0.10))
    degrade_i.setColorAt(1.0, _lerp_couleur(COULEUR_A, COULEUR_B, 0.75))

    rayon_point_i = taille * 0.07
    y_point_i = cy - taille * 0.15
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(degrade_i))
    painter.drawEllipse(QPointF(cx, y_point_i), rayon_point_i, rayon_point_i)

    largeur_hampe = taille * 0.085
    y_hampe_haut = cy - taille * 0.01
    y_hampe_bas = cy + taille * 0.23
    rect_hampe = QRectF(
        cx - largeur_hampe / 2, y_hampe_haut, largeur_hampe, y_hampe_bas - y_hampe_haut
    )
    painter.setBrush(QBrush(degrade_i))
    painter.drawRoundedRect(rect_hampe, largeur_hampe / 2, largeur_hampe / 2)
