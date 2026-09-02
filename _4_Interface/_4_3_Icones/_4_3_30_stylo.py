################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.30 – Script de création de l'icône stylo plume                           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QFont,
    QPainterPath,
)

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_icone_stylo_plume(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône "stylo plume" : illustrée non pas par un objet mais par une
    calligraphie de deux lettres en police script, chacune dans une couleur
    vive différente, complétée d'un petit paraphe (trait courbe + point)
    qui rappelle le geste d'écriture. Formes simples et couleurs plates
    pour rester net même en petite taille."""

    COULEUR_LETTRE_1 = QColor("#5EC9B3")  # turquoise
    COULEUR_LETTRE_2 = QColor("#F2789F")  # rose corail
    COULEUR_PARAPHE = QColor("#F0C34E")  # or

    cx, cy = centre.x(), centre.y()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # ============================================================
    # DEUX LETTRES EN CALLIGRAPHIE (police script/italique)
    # ============================================================
    police = QFont("Brush Script MT")
    if not QFont(police).exactMatch():
        police = QFont("Segoe Script")
    if not QFont(police).exactMatch():
        police = QFont("Georgia")
        police.setItalic(True)
    police.setPixelSize(int(taille * 0.62))
    painter.setFont(police)

    decalage = taille * 0.02  # léger chevauchement, comme une vraie signature

    painter.setPen(QPen(COULEUR_LETTRE_1))
    zone_lettre_1 = QRectF(
        cx - taille * 0.48, cy - taille * 0.40, taille * 0.55, taille * 0.85
    )
    painter.drawText(zone_lettre_1, Qt.AlignmentFlag.AlignCenter, "A")

    painter.setPen(QPen(COULEUR_LETTRE_2))
    zone_lettre_2 = QRectF(
        cx - taille * 0.10 + decalage, cy - taille * 0.40, taille * 0.55, taille * 0.85
    )
    painter.drawText(zone_lettre_2, Qt.AlignmentFlag.AlignCenter, "a")

    # ============================================================
    # PETIT PARAPHE SOUS LES LETTRES (trait courbe + point)
    # ============================================================
    chemin_paraphe = QPainterPath()
    chemin_paraphe.moveTo(cx - taille * 0.32, cy + taille * 0.32)
    chemin_paraphe.quadTo(
        cx, cy + taille * 0.42, cx + taille * 0.30, cy + taille * 0.30
    )

    pen_paraphe = QPen(COULEUR_PARAPHE)
    pen_paraphe.setWidthF(taille * 0.045)
    pen_paraphe.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_paraphe)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(chemin_paraphe)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_PARAPHE))
    painter.drawEllipse(
        QPointF(cx + taille * 0.36, cy + taille * 0.27), taille * 0.035, taille * 0.035
    )
