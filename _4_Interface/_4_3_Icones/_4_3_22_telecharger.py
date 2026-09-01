################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.22 – Script de création de l'icône de téléchargement                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, Qt, QRectF
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import _dessiner_badge_validation

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_icone_telechargement(
    painter: QPainter, centre: QPointF, taille: float, validee: bool
) -> None:
    """Icône "télécharger" : flèche pleine pointant vers le bas au-dessus
    d'un plateau (tiroir de réception). Dégradé linéaire simple, sans ombre
    portée ni reflet glossy."""

    COULEUR_DEBUT = QColor("#ff9d5c")
    COULEUR_FIN = QColor("#ff5c8a")

    cx, cy = centre.x(), centre.y()

    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # -- Dimensions de base -------------------------------------------------
    largeur_fleche = taille * 0.25  # largeur de la tige de la flèche
    largeur_pointe = taille * 0.5  # largeur du triangle de la pointe
    hauteur_tige = taille * 0.32  # hauteur de la tige rectangulaire
    hauteur_pointe = taille * 0.24  # hauteur du triangle

    y_haut_tige = cy - taille * 0.32
    y_bas_tige = y_haut_tige + hauteur_tige
    y_pointe = y_bas_tige + hauteur_pointe

    largeur_plateau = taille * 0.62
    y_plateau = cy + taille * 0.28
    epaisseur_plateau = taille * 0.09

    # ============================================================
    # FLÈCHE PLEINE + PLATEAU (chemin unique, dégradé linéaire)
    # ============================================================
    chemin_fleche = QPainterPath()
    chemin_fleche.moveTo(cx - largeur_fleche / 2, y_haut_tige)
    chemin_fleche.lineTo(cx + largeur_fleche / 2, y_haut_tige)
    chemin_fleche.lineTo(cx + largeur_fleche / 2, y_bas_tige)
    chemin_fleche.lineTo(cx + largeur_pointe / 2, y_bas_tige)
    chemin_fleche.lineTo(cx, y_pointe)
    chemin_fleche.lineTo(cx - largeur_pointe / 2, y_bas_tige)
    chemin_fleche.lineTo(cx - largeur_fleche / 2, y_bas_tige)
    chemin_fleche.closeSubpath()

    chemin_plateau = QPainterPath()
    chemin_plateau.addRect(
        QRectF(
            cx - largeur_plateau / 2,
            y_plateau,
            largeur_plateau,
            epaisseur_plateau,
        )
    )

    chemin_icone = chemin_fleche.united(chemin_plateau)

    degrade = QLinearGradient(QPointF(cx, y_haut_tige), QPointF(cx, y_plateau))
    degrade.setColorAt(0.0, COULEUR_DEBUT)
    degrade.setColorAt(1.0, COULEUR_FIN)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(degrade))
    painter.drawPath(chemin_icone)

    # Badge de validation (optionnel)
    if validee:
        _dessiner_badge_validation(painter=painter, centre=centre, taille=taille)
