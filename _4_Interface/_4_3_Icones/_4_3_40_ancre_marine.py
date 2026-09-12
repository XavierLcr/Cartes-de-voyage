################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.40 – Script de création d'une ancre marine                               #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QBrush,
    QPen,
    QColor,
    QLinearGradient,
)
from PyQt6.QtCore import Qt, QPointF

# 1 -- Fonction de création de l'encre -----------------------------------------


# 1septies -- Fonction de création de l'ancre au fond de la mer ------------------


def _dessiner_ancre(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    inclinaison: float = 0.0,
    couleur: QColor = None,
    phase: float = 0.0,
    degrade: bool = True,
) -> None:
    """Dessine une ancre marine classique posée au fond, légèrement
    couchée sur le sable (via `inclinaison`, en radians). Élément de
    décor statique : ne nage pas et n'a pas de `sens`, mais `phase`
    anime un léger balancement d'algues accrochées à la tige, pour
    éviter un objet totalement figé au fond de la scène.

    `centre` est le point de contact avec le sable (la base de l'ancre,
    pas son sommet).
    """
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.translate(centre)
    painter.rotate(math.degrees(inclinaison))

    if couleur is None:
        couleur = QColor("#7A6455")  # brun rouille

    trait = QColor(couleur).darker(145)
    trait.setAlpha(220)
    pen = QPen(trait)
    pen.setWidthF(max(1.0, taille * 0.035))
    painter.setPen(pen)

    if degrade:
        metal_brush = QLinearGradient(-taille * 0.15, 0, taille * 0.15, 0)
        metal_brush.setColorAt(0.0, QColor(couleur).darker(120))
        metal_brush.setColorAt(0.5, QColor(couleur).lighter(115))
        metal_brush.setColorAt(1.0, QColor(couleur).darker(120))
        pinceau_metal = QBrush(metal_brush)
    else:
        pinceau_metal = QBrush(couleur)
    painter.setBrush(pinceau_metal)

    # repère : y négatif = vers le haut (vers la surface), base au niveau y=0
    hauteur = taille * 0.85
    largeur_pattes = taille * 0.55

    # --- tige verticale ---
    tige = QPainterPath()
    tige_l = taille * 0.06
    tige.addRoundedRect(
        -tige_l / 2, -hauteur, tige_l, hauteur * 0.82, tige_l * 0.4, tige_l * 0.4
    )
    painter.drawPath(tige)

    # --- anneau supérieur (pour la chaîne) ---
    painter.setBrush(Qt.BrushStyle.NoBrush)
    anneau = QPainterPath()
    r_anneau = taille * 0.10
    anneau.addEllipse(QPointF(0, -hauteur - r_anneau * 0.6), r_anneau, r_anneau)
    painter.drawPath(anneau)

    # --- barre transversale (le "jas", proche du haut de la tige) ---
    painter.setBrush(pinceau_metal)
    jas = QPainterPath()
    jas_l = taille * 0.32
    jas_h = taille * 0.045
    jas.addRoundedRect(
        -jas_l / 2, -hauteur * 0.72 - jas_h / 2, jas_l, jas_h, jas_h * 0.4, jas_h * 0.4
    )
    painter.drawPath(jas)

    # --- pattes courbes + pointes (des deux côtés, en forme de crochet) ---
    for cote in (-1, 1):
        patte = QPainterPath()
        patte.moveTo(0, -hauteur * 0.05)
        patte.quadTo(
            cote * largeur_pattes * 0.55,
            -hauteur * 0.10,
            cote * largeur_pattes * 0.60,
            hauteur * 0.05,
        )
        # pointe de l'ancre (triangle)
        patte.quadTo(
            cote * largeur_pattes * 0.62,
            hauteur * 0.14,
            cote * largeur_pattes * 0.42,
            hauteur * 0.12,
        )
        painter.drawPath(patte)

    # --- reflet métallique discret sur la tige ---
    painter.setPen(Qt.PenStyle.NoPen)
    reflet = QColor(255, 255, 255, 70)
    painter.setBrush(QBrush(reflet))
    reflet_path = QPainterPath()
    reflet_path.addRoundedRect(
        -tige_l * 0.15,
        -hauteur * 0.95,
        tige_l * 0.3,
        hauteur * 0.55,
        tige_l * 0.1,
        tige_l * 0.1,
    )
    painter.drawPath(reflet_path)

    # --- taches de rouille (petites ellipses irrégulières) ---
    rouille = QColor("#8A4A2E")
    rouille.setAlpha(120)
    painter.setBrush(QBrush(rouille))
    for dx, dy, r in (
        (tige_l * 0.3, -hauteur * 0.35, taille * 0.03),
        (-tige_l * 0.2, -hauteur * 0.55, taille * 0.02),
        (jas_l * 0.25, -hauteur * 0.70, taille * 0.025),
    ):
        painter.drawEllipse(QPointF(dx, dy), r, r)

    # --- petite algue accrochée à la base, qui ondule avec phase ---
    painter.setBrush(Qt.BrushStyle.NoBrush)
    algue_pen = QPen(QColor("#4C7A4A"))
    algue_pen.setWidthF(max(0.8, taille * 0.02))
    painter.setPen(algue_pen)
    ondulation_algue = math.sin(phase) * taille * 0.08
    for i, decalage_x in enumerate((-taille * 0.08, taille * 0.10)):
        algue = QPainterPath()
        base_x = decalage_x
        algue.moveTo(base_x, hauteur * 0.08)
        algue.quadTo(
            base_x + ondulation_algue * (0.6 if i == 0 else -0.6),
            hauteur * 0.08 - taille * 0.18,
            base_x + ondulation_algue * (1.0 if i == 0 else -1.0),
            hauteur * 0.08 - taille * 0.30,
        )
        painter.drawPath(algue)

    painter.restore()
