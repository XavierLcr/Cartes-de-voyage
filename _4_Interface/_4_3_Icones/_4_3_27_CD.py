################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.27 – Script de création de l'icône de sauvegarde (CD)                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QRadialGradient,
    QConicalGradient,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import _dessiner_badge_validation

# 1 -- Fonction de création de l'icône -------------------------------------------


def _dessiner_icone_cd(
    painter: QPainter, centre: QPointF, taille: float, validee: bool = False
) -> None:
    """Icône "sauvegarder" : CD stylisé (disque métallique + trou central +
    léger reflet + fine irisation). Volontairement minimaliste : peu de
    détails pour rester lisible en petite taille. Pas d'ombre portée. Si
    validee=True, ajoute un badge check vert en bas à droite pour signaler
    une sauvegarde réussie."""

    COULEUR_DISQUE_CLAIR = QColor("#E8ECF1")
    COULEUR_DISQUE_SOMBRE = QColor("#9AA5B1")
    COULEUR_CONTOUR = QColor("#6B7480")
    COULEUR_BAGUE = QColor("#5A6472")

    cx, cy = centre.x(), centre.y()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    rayon_disque = taille * 0.46
    rayon_trou = taille * 0.09
    rayon_bague = taille * 0.14

    # ============================================================
    # DISQUE (dégradé radial métallique)
    # ============================================================
    degrade_disque = QRadialGradient(QPointF(cx, cy), rayon_disque)
    degrade_disque.setColorAt(0.0, COULEUR_DISQUE_CLAIR)
    degrade_disque.setColorAt(0.55, COULEUR_DISQUE_CLAIR)
    degrade_disque.setColorAt(0.75, COULEUR_DISQUE_SOMBRE)
    degrade_disque.setColorAt(1.0, COULEUR_DISQUE_CLAIR.lighter(105))

    pen_disque = QPen(COULEUR_CONTOUR)
    pen_disque.setWidthF(taille * 0.012)
    painter.setPen(pen_disque)
    painter.setBrush(QBrush(degrade_disque))
    painter.drawEllipse(QPointF(cx, cy), rayon_disque, rayon_disque)

    # ============================================================
    # IRISATION (fin arc coloré, façon reflet arc-en-ciel de la piste)
    # ============================================================
    degrade_iris = QConicalGradient(QPointF(cx, cy), 200)
    degrade_iris.setColorAt(0.00, QColor(255, 255, 255, 0))
    degrade_iris.setColorAt(0.08, QColor(180, 140, 255, 110))
    degrade_iris.setColorAt(0.16, QColor(120, 200, 255, 110))
    degrade_iris.setColorAt(0.24, QColor(150, 255, 190, 90))
    degrade_iris.setColorAt(0.32, QColor(255, 255, 255, 0))
    degrade_iris.setColorAt(1.00, QColor(255, 255, 255, 0))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(degrade_iris))
    painter.drawEllipse(
        QRectF(
            cx - rayon_disque * 0.92,
            cy - rayon_disque * 0.92,
            rayon_disque * 1.84,
            rayon_disque * 1.84,
        )
    )

    # -- Le centre est redessiné par-dessus pour ne garder l'irisation qu'en périphérie --
    degrade_disque_centre = QRadialGradient(QPointF(cx, cy), rayon_disque * 0.72)
    degrade_disque_centre.setColorAt(0.0, COULEUR_DISQUE_CLAIR)
    degrade_disque_centre.setColorAt(1.0, COULEUR_DISQUE_CLAIR)
    painter.setBrush(QBrush(degrade_disque_centre))
    painter.drawEllipse(QPointF(cx, cy), rayon_disque * 0.72, rayon_disque * 0.72)

    # ============================================================
    # BAGUE ET TROU CENTRAL
    # ============================================================
    pen_bague = QPen(COULEUR_BAGUE)
    pen_bague.setWidthF(taille * 0.01)
    painter.setPen(pen_bague)
    painter.setBrush(QBrush(COULEUR_DISQUE_CLAIR.darker(108)))
    painter.drawEllipse(QPointF(cx, cy), rayon_bague, rayon_bague)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_CONTOUR.darker(160)))
    painter.drawEllipse(QPointF(cx, cy), rayon_trou, rayon_trou)

    # -- Reflet glossy discret ------------------------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    reflet = QColor(255, 255, 255, 90)
    painter.setBrush(QBrush(reflet))
    painter.drawEllipse(
        QPointF(cx - rayon_disque * 0.35, cy - rayon_disque * 0.40),
        rayon_disque * 0.22,
        rayon_disque * 0.12,
    )

    # Badge de validation (optionnel)
    if validee:
        _dessiner_badge_validation(painter=painter, centre=centre, taille=taille)
