################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.16 – Script de création de l'icône de curseurs                           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QRadialGradient,
)

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_icone_curseurs(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône "paramètres" : trois curseurs de réglage horizontaux, à hauteurs
    et positions différentes, avec poignées rondes en dégradé (effet "glossy")
    et ombre portée douce. Design plus fin et fluide qu'un engrenage classique,
    sans angle dur, cohérent avec le style des autres icônes du projet."""

    COULEUR_RAIL = QColor("#B8BEC9")
    COULEUR_RAIL_ACTIF = QColor("#5C6472")

    # (position relative de la poignée sur le rail [0-1], couleur d'accent)
    CURSEURS = [
        (0.68, QColor("#33C7E8")),
        (0.35, QColor("#FF6F6F")),
        (0.52, QColor("#8C6FFF")),
    ]

    cx, cy = centre.x(), centre.y()

    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    largeur_rail = taille * 0.62
    x_gauche = cx - largeur_rail / 2
    x_droite = cx + largeur_rail / 2
    espace_y = taille * 0.30
    y_depart = cy - espace_y

    epaisseur_rail = taille * 0.035
    rayon_poignee = taille * 0.075
    rayon_ombre = rayon_poignee * 1.35

    for i, (position, couleur_accent) in enumerate(CURSEURS):
        y = y_depart + i * espace_y
        x_poignee = x_gauche + largeur_rail * position

        # -- Rail : portion "parcourue" plus foncée, reste plus clair --------
        pen_rail_clair = QPen(COULEUR_RAIL)
        pen_rail_clair.setWidthF(epaisseur_rail)
        pen_rail_clair.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_rail_clair)
        painter.drawLine(QPointF(x_gauche, y), QPointF(x_droite, y))

        pen_rail_actif = QPen(COULEUR_RAIL_ACTIF)
        pen_rail_actif.setWidthF(epaisseur_rail)
        pen_rail_actif.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_rail_actif)
        painter.drawLine(QPointF(x_gauche, y), QPointF(x_poignee, y))

        # -- Ombre douce sous la poignée --------------------------------------
        painter.setPen(Qt.PenStyle.NoPen)
        ombre = QRadialGradient(
            QPointF(x_poignee, y + rayon_poignee * 0.25), rayon_ombre
        )
        c_ombre_pleine = QColor(0, 0, 0, 60)
        c_ombre_transp = QColor(0, 0, 0, 0)
        ombre.setColorAt(0.0, c_ombre_pleine)
        ombre.setColorAt(1.0, c_ombre_transp)
        painter.setBrush(QBrush(ombre))
        painter.drawEllipse(
            QPointF(x_poignee, y + rayon_poignee * 0.25), rayon_ombre, rayon_ombre
        )

        # -- Poignée : dégradé radial glossy + léger contour ------------------
        degrade_poignee = QRadialGradient(
            QPointF(x_poignee - rayon_poignee * 0.3, y - rayon_poignee * 0.35),
            rayon_poignee * 1.6,
        )
        degrade_poignee.setColorAt(0.0, couleur_accent.lighter(150))
        degrade_poignee.setColorAt(0.55, couleur_accent)
        degrade_poignee.setColorAt(1.0, couleur_accent.darker(115))

        pen_contour = QPen(couleur_accent.darker(140))
        pen_contour.setWidthF(taille * 0.008)
        painter.setPen(pen_contour)
        painter.setBrush(QBrush(degrade_poignee))
        painter.drawEllipse(QPointF(x_poignee, y), rayon_poignee, rayon_poignee)

        # -- Petit reflet blanc pour l'effet "glossy" -------------------------
        painter.setPen(Qt.PenStyle.NoPen)
        reflet = QColor(255, 255, 255, 130)
        painter.setBrush(QBrush(reflet))
        painter.drawEllipse(
            QPointF(x_poignee - rayon_poignee * 0.32, y - rayon_poignee * 0.35),
            rayon_poignee * 0.32,
            rayon_poignee * 0.22,
        )
