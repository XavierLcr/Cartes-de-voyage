################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.23 – Script de création de l'icône d'un balai                            #
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

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_icone_balai(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône "réinitialiser l'interface" : balai stylisé (manche + brins en
    éventail) avec de petits traits de balayage courbes pour suggérer
    l'action, plus explicite qu'un simple pictogramme d'objet. Même esprit
    visuel que les autres icônes : dégradé simple, une seule ombre portée,
    un seul reflet glossy."""

    COULEUR_MANCHE = QColor("#A9702F")  # bois/brun
    COULEUR_BRINS = QColor("#E8B04B")  # paille/jaune doré
    COULEUR_BALAYAGE = QColor(
        "#8FA3B8"
    )  # gris-bleu discret pour les traits de mouvement

    cx, cy = centre.x(), centre.y()

    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # -- Dimensions de base -------------------------------------------------
    # Le balai est incliné à ~35° : manche en haut-gauche, tête en bas-droite

    angle = math.radians(35)
    dir_x, dir_y = math.cos(angle), math.sin(angle)  # direction du manche
    perp_x, perp_y = -dir_y, dir_x  # perpendiculaire (largeur)

    longueur_manche = taille * 0.70
    largeur_manche = taille * 0.07

    x_haut_manche = cx - dir_x * longueur_manche * 0.5
    y_haut_manche = cy - dir_y * longueur_manche * 0.5
    x_bas_manche = cx + dir_x * longueur_manche * 0.32
    y_bas_manche = cy + dir_y * longueur_manche * 0.32

    # ============================================================
    # OMBRE PORTÉE UNIQUE
    # ============================================================
    painter.setPen(Qt.PenStyle.NoPen)
    ombre = QRadialGradient(
        QPointF(cx + dir_x * taille * 0.15, cy + dir_y * taille * 0.15 + taille * 0.08),
        taille * 0.6,
    )
    ombre.setColorAt(0.0, QColor(0, 0, 0, 40))
    ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.setBrush(QBrush(ombre))
    painter.drawEllipse(
        QPointF(cx + dir_x * taille * 0.15, cy + dir_y * taille * 0.15 + taille * 0.08),
        taille * 0.55,
        taille * 0.55,
    )

    # ============================================================
    # TÊTE DU BALAI (éventail de brins, dessiné avant le manche)
    # ============================================================
    largeur_tete = taille * 0.46
    hauteur_tete = taille * 0.30

    x_racine = x_bas_manche
    y_racine = y_bas_manche
    x_pointe_tete = x_racine + dir_x * hauteur_tete
    y_pointe_tete = y_racine + dir_y * hauteur_tete

    chemin_brins = QPainterPath()
    chemin_brins.moveTo(
        x_racine - perp_x * largeur_manche * 0.9,
        y_racine - perp_y * largeur_manche * 0.9,
    )
    chemin_brins.lineTo(
        x_pointe_tete - perp_x * largeur_tete / 2,
        y_pointe_tete - perp_y * largeur_tete / 2,
    )
    # petites dents en zigzag sur le bord des brins pour l'effet "paille"
    n_dents = 5
    for i in range(n_dents + 1):
        t = i / n_dents
        decalage = (largeur_tete / 2) - t * largeur_tete
        prof = hauteur_tete * 0.08 if i % 2 == 0 else 0
        chemin_brins.lineTo(
            x_pointe_tete - perp_x * decalage + dir_x * prof,
            y_pointe_tete - perp_y * decalage + dir_y * prof,
        )
    chemin_brins.lineTo(
        x_racine + perp_x * largeur_manche * 0.9,
        y_racine + perp_y * largeur_manche * 0.9,
    )
    chemin_brins.closeSubpath()

    degrade_brins = QRadialGradient(
        QPointF(x_pointe_tete, y_pointe_tete), largeur_tete * 0.9
    )
    degrade_brins.setColorAt(0.0, COULEUR_BRINS.lighter(120))
    degrade_brins.setColorAt(1.0, COULEUR_BRINS.darker(110))

    pen_contour_brins = QPen(COULEUR_BRINS.darker(140))
    pen_contour_brins.setWidthF(taille * 0.004)
    pen_contour_brins.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen_contour_brins)
    painter.setBrush(QBrush(degrade_brins))
    painter.drawPath(chemin_brins)

    # -- Ligature (bande qui attache les brins au manche) --------------------
    largeur_ligature = taille * 0.09
    chemin_ligature = QPainterPath()
    chemin_ligature.moveTo(
        x_racine - perp_x * largeur_manche * 1.1,
        y_racine - perp_y * largeur_manche * 1.1,
    )
    chemin_ligature.lineTo(
        x_racine + perp_x * largeur_manche * 1.1,
        y_racine + perp_y * largeur_manche * 1.1,
    )
    chemin_ligature.lineTo(
        x_racine + dir_x * largeur_ligature + perp_x * largeur_manche * 0.85,
        y_racine + dir_y * largeur_ligature + perp_y * largeur_manche * 0.85,
    )
    chemin_ligature.lineTo(
        x_racine + dir_x * largeur_ligature - perp_x * largeur_manche * 0.85,
        y_racine + dir_y * largeur_ligature - perp_y * largeur_manche * 0.85,
    )
    chemin_ligature.closeSubpath()

    pen_ligature = QPen(QColor("#6B4423").darker(120))
    pen_ligature.setWidthF(taille * 0.004)
    painter.setPen(pen_ligature)
    painter.setBrush(QBrush(QColor("#6B4423")))
    painter.drawPath(chemin_ligature)

    # ============================================================
    # MANCHE (rectangle arrondi incliné, dégradé simple)
    # ============================================================
    chemin_manche = QPainterPath()
    chemin_manche.moveTo(
        x_haut_manche - perp_x * largeur_manche / 2,
        y_haut_manche - perp_y * largeur_manche / 2,
    )
    chemin_manche.lineTo(
        x_bas_manche - perp_x * largeur_manche / 2,
        y_bas_manche - perp_y * largeur_manche / 2,
    )
    chemin_manche.lineTo(
        x_bas_manche + perp_x * largeur_manche / 2,
        y_bas_manche + perp_y * largeur_manche / 2,
    )
    chemin_manche.lineTo(
        x_haut_manche + perp_x * largeur_manche / 2,
        y_haut_manche + perp_y * largeur_manche / 2,
    )
    chemin_manche.closeSubpath()

    degrade_manche = QRadialGradient(
        QPointF(x_haut_manche, y_haut_manche), longueur_manche * 0.8
    )
    degrade_manche.setColorAt(0.0, COULEUR_MANCHE.lighter(125))
    degrade_manche.setColorAt(1.0, COULEUR_MANCHE.darker(110))

    pen_contour_manche = QPen(COULEUR_MANCHE.darker(130))
    pen_contour_manche.setWidthF(taille * 0.004)
    pen_contour_manche.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_contour_manche)
    painter.setBrush(QBrush(degrade_manche))
    painter.drawPath(chemin_manche)

    # -- Petit bout arrondi en haut du manche --------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_MANCHE.lighter(115)))
    painter.drawEllipse(
        QPointF(x_haut_manche, y_haut_manche), largeur_manche / 2, largeur_manche / 2
    )

    # -- Reflet glossy discret sur le manche ----------------------------------
    reflet = QColor(255, 255, 255, 80)
    painter.setBrush(QBrush(reflet))
    x_reflet = x_haut_manche + dir_x * longueur_manche * 0.2
    y_reflet = y_haut_manche + dir_y * longueur_manche * 0.2
    painter.drawEllipse(
        QPointF(
            x_reflet - perp_x * largeur_manche * 0.15,
            y_reflet - perp_y * largeur_manche * 0.15,
        ),
        largeur_manche * 0.18,
        longueur_manche * 0.12,
    )

    # ============================================================
    # TRAITS DE BALAYAGE (petites courbes suggérant le mouvement de reset)
    # ============================================================
    pen_balayage = QPen(COULEUR_BALAYAGE)
    pen_balayage.setWidthF(taille * 0.02)
    pen_balayage.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_balayage)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    for i, decalage in enumerate([-0.18, 0.0, 0.18]):
        x0 = x_pointe_tete + perp_x * largeur_tete * (0.55 + abs(decalage))
        y0 = (
            y_pointe_tete
            + perp_y * largeur_tete * (0.55 + abs(decalage))
            - taille * 0.04 * i
        )
        chemin_trait = QPainterPath()
        x_depart = x0 - dir_x * taille * 0.02
        y_depart = y0 - dir_y * taille * 0.02
        chemin_trait.moveTo(x_depart, y_depart)
        chemin_trait.quadTo(
            x_depart + dir_x * taille * 0.08 - perp_x * taille * 0.03,
            y_depart + dir_y * taille * 0.08 - perp_y * taille * 0.03,
            x_depart + dir_x * taille * 0.16,
            y_depart + dir_y * taille * 0.16,
        )
        painter.drawPath(chemin_trait)
