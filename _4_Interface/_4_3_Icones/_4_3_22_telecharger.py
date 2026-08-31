################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.22 – Script de création de l'icône de téléchargement                     #
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


def _dessiner_icone_telechargement(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône "télécharger" : flèche pleine pointant vers le bas au-dessus
    d'un plateau (tiroir de réception). Dégradé simple, une seule ombre
    portée, un seul reflet glossy. Même esprit visuel que les autres icônes
    (pas d'angle dur superflu, cohérence avec le style "ajout profil")."""

    COULEUR_PRINCIPALE = QColor("#4A90D9")  # bleu "téléchargement" ; changer si besoin

    cx, cy = centre.x(), centre.y()

    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # -- Dimensions de base -------------------------------------------------
    largeur_fleche = taille * 0.20  # largeur de la tige de la flèche
    largeur_pointe = taille * 0.42  # largeur du triangle de la pointe
    hauteur_tige = taille * 0.30  # hauteur de la tige rectangulaire
    hauteur_pointe = taille * 0.24  # hauteur du triangle

    y_haut_tige = cy - taille * 0.32
    y_bas_tige = y_haut_tige + hauteur_tige
    y_pointe = y_bas_tige + hauteur_pointe

    largeur_plateau = taille * 0.62
    y_plateau = cy + taille * 0.28
    epaisseur_plateau = taille * 0.09
    hauteur_rebord = taille * 0.10

    # ============================================================
    # OMBRE PORTÉE UNIQUE
    # ============================================================
    painter.setPen(Qt.PenStyle.NoPen)
    ombre = QRadialGradient(QPointF(cx, cy + taille * 0.12), taille * 0.62)
    ombre.setColorAt(0.0, QColor(0, 0, 0, 40))
    ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.setBrush(QBrush(ombre))
    painter.drawEllipse(QPointF(cx, cy + taille * 0.12), taille * 0.55, taille * 0.55)

    # ============================================================
    # FLÈCHE PLEINE (tige + pointe en un seul chemin)
    # ============================================================
    chemin_fleche = QPainterPath()
    # Coin haut-gauche de la tige
    chemin_fleche.moveTo(cx - largeur_fleche / 2, y_haut_tige)
    chemin_fleche.lineTo(cx + largeur_fleche / 2, y_haut_tige)
    chemin_fleche.lineTo(cx + largeur_fleche / 2, y_bas_tige)
    chemin_fleche.lineTo(cx + largeur_pointe / 2, y_bas_tige)
    chemin_fleche.lineTo(cx, y_pointe)
    chemin_fleche.lineTo(cx - largeur_pointe / 2, y_bas_tige)
    chemin_fleche.lineTo(cx - largeur_fleche / 2, y_bas_tige)
    chemin_fleche.closeSubpath()

    degrade_fleche = QRadialGradient(
        QPointF(cx, y_haut_tige + (y_pointe - y_haut_tige) * 0.3),
        taille * 0.5,
    )
    degrade_fleche.setColorAt(0.0, COULEUR_PRINCIPALE.lighter(120))
    degrade_fleche.setColorAt(1.0, COULEUR_PRINCIPALE.darker(105))

    pen_contour = QPen(COULEUR_PRINCIPALE.darker(125))
    pen_contour.setWidthF(taille * 0.004)
    pen_contour.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen_contour)
    painter.setBrush(QBrush(degrade_fleche))
    painter.drawPath(chemin_fleche)

    # -- Reflet glossy discret sur le haut de la tige ------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    reflet = QColor(255, 255, 255, 90)
    painter.setBrush(QBrush(reflet))
    painter.drawEllipse(
        QPointF(cx - largeur_fleche * 0.15, y_haut_tige + hauteur_tige * 0.2),
        largeur_fleche * 0.22,
        hauteur_tige * 0.18,
    )

    # ============================================================
    # PLATEAU DE RÉCEPTION (forme en U, dégradé simple)
    # ============================================================
    chemin_plateau = QPainterPath()
    chemin_plateau.moveTo(cx - largeur_plateau / 2, y_plateau)
    chemin_plateau.lineTo(cx - largeur_plateau / 2, y_plateau + hauteur_rebord)
    chemin_plateau.lineTo(
        cx - largeur_plateau / 2 + epaisseur_plateau,
        y_plateau + hauteur_rebord,
    )
    chemin_plateau.lineTo(
        cx - largeur_plateau / 2 + epaisseur_plateau,
        y_plateau + epaisseur_plateau * 0.4,
    )
    chemin_plateau.lineTo(
        cx + largeur_plateau / 2 - epaisseur_plateau,
        y_plateau + epaisseur_plateau * 0.4,
    )
    chemin_plateau.lineTo(
        cx + largeur_plateau / 2 - epaisseur_plateau,
        y_plateau + hauteur_rebord,
    )
    chemin_plateau.lineTo(cx + largeur_plateau / 2, y_plateau + hauteur_rebord)
    chemin_plateau.lineTo(cx + largeur_plateau / 2, y_plateau)
    chemin_plateau.closeSubpath()

    degrade_plateau = QRadialGradient(
        QPointF(cx, y_plateau + hauteur_rebord * 0.5), largeur_plateau * 0.9
    )
    degrade_plateau.setColorAt(0.0, COULEUR_PRINCIPALE.lighter(115))
    degrade_plateau.setColorAt(1.0, COULEUR_PRINCIPALE.darker(110))

    painter.setPen(pen_contour)
    painter.setBrush(QBrush(degrade_plateau))
    painter.drawPath(chemin_plateau)
