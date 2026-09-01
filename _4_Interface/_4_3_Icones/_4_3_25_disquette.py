################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.25 – Script de création de l'icône de sauvegarde (disquette)             #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QPainterPath,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import _dessiner_badge_validation

# 1 -- Fonction de création de l'icône -------------------------------------------


def _dessiner_icone_disquette(
    painter: QPainter, centre: QPointF, taille: float, validee: bool = False
) -> None:
    """Icône "sauvegarder" : disquette minimaliste (corps + coin coupé, volet,
    étiquette), à plat, sans dégradé ni reflet. Palette alignée sur l'icône
    voyage : gris du poteau pour le corps/volet, accent cyan pour le repère
    de statut. Pas d'ombre portée. Si validee=True, ajoute un badge check
    vert en bas à droite pour signaler une sauvegarde réussie."""

    COULEUR_CORPS = QColor("#7B74E8")  # violet doux
    COULEUR_VOLET = QColor("#D9D6FF")  # lavande clair
    COULEUR_LABEL = QColor("#FFF7ED")  # blanc cassé chaud (pas gris)
    COULEUR_ACCENT = QColor("#FF7A6B")  # corail (accent de l'icône voyage)
    COULEUR_BARRES = QColor("#C7C2F7")  # lavande un peu plus soutenu pour les barres

    cx, cy = centre.x(), centre.y()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # -- Dimensions de base ---------------------------------------------
    taille_corps = taille * 0.80
    arrondi = taille * 0.11
    coin_coupe = taille * 0.18
    arrondi_coin_coupe = taille * 0.045

    x0 = cx - taille_corps / 2
    y0 = cy - taille_corps / 2
    x1 = cx + taille_corps / 2
    y1 = cy + taille_corps / 2

    # ============================================================
    # CORPS DE LA DISQUETTE (carré très arrondi, coin haut-droit
    # coupé en biseau doux plutôt qu'en angle vif)
    # ============================================================
    chemin_corps = QPainterPath()
    chemin_corps.moveTo(x0 + arrondi, y0)
    chemin_corps.lineTo(x1 - coin_coupe, y0)
    chemin_corps.quadTo(
        x1 - coin_coupe + arrondi_coin_coupe,
        y0 + arrondi_coin_coupe * 0.2,
        x1 - coin_coupe * 0.35,
        y0 + coin_coupe * 0.65,
    )
    chemin_corps.quadTo(x1, y0 + coin_coupe, x1, y0 + coin_coupe + arrondi_coin_coupe)
    chemin_corps.lineTo(x1, y1 - arrondi)
    chemin_corps.quadTo(x1, y1, x1 - arrondi, y1)
    chemin_corps.lineTo(x0 + arrondi, y1)
    chemin_corps.quadTo(x0, y1, x0, y1 - arrondi)
    chemin_corps.lineTo(x0, y0 + arrondi)
    chemin_corps.quadTo(x0, y0, x0 + arrondi, y0)
    chemin_corps.closeSubpath()

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_CORPS))
    painter.drawPath(chemin_corps)

    # ============================================================
    # VOLET (bande supérieure, à plat)
    # ============================================================
    largeur_volet = taille_corps * 0.60
    hauteur_volet = taille_corps * 0.26
    x_volet = cx - largeur_volet / 2
    y_volet = y0 + taille_corps * 0.09

    chemin_volet = QPainterPath()
    chemin_volet.addRoundedRect(
        x_volet, y_volet, largeur_volet, hauteur_volet, taille * 0.05, taille * 0.05
    )

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_VOLET))
    painter.drawPath(chemin_volet)

    # -- Petit repère de statut (touche de couleur, remplace l'encoche) -----
    rayon_repere = hauteur_volet * 0.22
    x_repere = x_volet + largeur_volet * 0.78
    y_repere = y_volet + hauteur_volet / 2

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_ACCENT))
    painter.drawEllipse(QPointF(x_repere, y_repere), rayon_repere, rayon_repere)

    # ============================================================
    # ÉTIQUETTE (rectangle clair, bas de la disquette, à plat)
    # ============================================================
    largeur_label = taille_corps * 0.70
    hauteur_label = taille_corps * 0.34
    x_label = cx - largeur_label / 2
    y_label = y_volet + hauteur_volet + taille_corps * 0.09

    chemin_label = QPainterPath()
    chemin_label.addRoundedRect(
        x_label, y_label, largeur_label, hauteur_label, taille * 0.045, taille * 0.045
    )

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_LABEL))
    painter.drawPath(chemin_label)

    # -- Deux barres simples au centre de l'étiquette (repère "texte") ------
    pen_barre = QPen(COULEUR_BARRES)
    pen_barre.setWidthF(hauteur_label * 0.16)
    pen_barre.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_barre)

    marge_barre = largeur_label * 0.16
    for frac, longueur_relative in [(0.36, 1.0), (0.68, 0.62)]:
        y_barre = y_label + hauteur_label * frac
        x_fin = (
            x_label
            + marge_barre
            + (largeur_label - 2 * marge_barre) * longueur_relative
        )
        painter.drawLine(
            QPointF(x_label + marge_barre, y_barre),
            QPointF(x_fin, y_barre),
        )

    # Badge de validation (optionnel)
    if validee:
        _dessiner_badge_validation(painter=painter, centre=centre, taille=taille)
