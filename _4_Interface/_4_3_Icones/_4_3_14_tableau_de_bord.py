################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.14 – Script de création d'un icône de tableau de bord                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, Qt, QRectF
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QPolygonF

# 1 -- Classe de création de l'icône -------------------------------------------


def _dessiner_icone_tableau_de_bord(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône tableau de bord : grille 2x2 de mini-cartes, chacune avec un
    glyphe évoquant son type de widget (repère, courbe, barres, anneau)."""

    COULEUR_COMPTEUR = QColor("#5B8DEF")  # nb pays visités
    COULEUR_COURBE = QColor("#4FBDBA")  # évolution nb voyages
    COULEUR_BARRES = QColor("#F2A65A")  # évolution nb jours voyagés
    COULEUR_DONUT = QColor("#E9647B")  # continent favori

    cx, cy = centre.x(), centre.y()
    cote_carte = taille * 0.36
    espace = taille * 0.07
    rx_carte = cote_carte * 0.16

    x_gauche = cx - cote_carte - espace / 2
    x_droite = cx + espace / 2
    y_haut = cy - cote_carte - espace / 2
    y_bas = cy + espace / 2

    def fond_carte(x: float, y: float, couleur: QColor) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setOpacity(0.16)
        painter.setBrush(QBrush(couleur))
        painter.drawRoundedRect(
            QRectF(x, y, cote_carte, cote_carte), rx_carte, rx_carte
        )
        painter.setOpacity(1.0)

    # -- 1. Compteur : repère de type "pin" (nb pays visités) --------------
    x, y = x_gauche, y_haut
    fond_carte(x, y, COULEUR_COMPTEUR)
    ccx, ccy = x + cote_carte * 0.5, y + cote_carte * 0.42
    r_pin = cote_carte * 0.20
    tip_y = y + cote_carte * 0.80

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_COMPTEUR))
    painter.drawEllipse(QPointF(ccx, ccy), r_pin, r_pin)
    painter.drawPolygon(
        QPolygonF(
            [
                QPointF(ccx - r_pin * 0.85, ccy + r_pin * 0.45),
                QPointF(ccx + r_pin * 0.85, ccy + r_pin * 0.45),
                QPointF(ccx, tip_y),
            ]
        )
    )
    painter.setOpacity(0.16)
    painter.drawEllipse(QPointF(ccx, ccy), r_pin * 0.42, r_pin * 0.42)
    painter.setOpacity(1.0)

    # -- 2. Sparkline ascendante (évolution nb voyages) ---------------------
    x, y = x_droite, y_haut
    fond_carte(x, y, COULEUR_COURBE)
    pad = cote_carte * 0.22
    points = [
        QPointF(x + pad, y + cote_carte - pad * 0.7),
        QPointF(x + cote_carte * 0.42, y + cote_carte * 0.62),
        QPointF(x + cote_carte * 0.68, y + cote_carte * 0.68),
        QPointF(x + cote_carte - pad * 0.7, y + pad),
    ]
    pen_courbe = QPen(COULEUR_COURBE)
    pen_courbe.setWidthF(cote_carte * 0.06)
    pen_courbe.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen_courbe.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen_courbe)
    painter.drawPolyline(QPolygonF(points))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_COURBE))
    painter.drawEllipse(points[-1], cote_carte * 0.05, cote_carte * 0.05)

    # -- 3. Mini barres ascendantes (évolution nb jours voyagés) -----------
    x, y = x_gauche, y_bas
    fond_carte(x, y, COULEUR_BARRES)
    hauteurs = [0.34, 0.58, 0.82]
    larg_barre = cote_carte * 0.16
    espace_barre = cote_carte * 0.10
    total_largeur = len(hauteurs) * larg_barre + (len(hauteurs) - 1) * espace_barre
    bx = x + (cote_carte - total_largeur) / 2
    base_y = y + cote_carte * 0.80

    painter.setBrush(QBrush(COULEUR_BARRES))
    for h in hauteurs:
        hauteur_barre = cote_carte * 0.62 * h
        painter.drawRoundedRect(
            QRectF(bx, base_y - hauteur_barre, larg_barre, hauteur_barre),
            larg_barre * 0.3,
            larg_barre * 0.3,
        )
        bx += larg_barre + espace_barre

    # -- 4. Anneau de proportion (continent favori) --------------------------
    x, y = x_droite, y_bas
    fond_carte(x, y, COULEUR_DONUT)
    dcx, dcy = x + cote_carte * 0.5, y + cote_carte * 0.5
    r_donut = cote_carte * 0.30
    epaisseur = cote_carte * 0.13

    pen_fond_anneau = QPen(COULEUR_DONUT)
    pen_fond_anneau.setWidthF(epaisseur)
    painter.setOpacity(0.20)
    painter.setPen(pen_fond_anneau)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(QPointF(dcx, dcy), r_donut, r_donut)
    painter.setOpacity(1.0)

    pen_segment = QPen(COULEUR_DONUT)
    pen_segment.setWidthF(epaisseur)
    pen_segment.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_segment)
    rect_arc = QRectF(dcx - r_donut, dcy - r_donut, r_donut * 2, r_donut * 2)
    # Qt : angles en 1/16e de degré, sens antihoraire depuis 3h ; on démarre en haut (90°)
    painter.drawArc(rect_arc, 90 * 16, -110 * 16)
