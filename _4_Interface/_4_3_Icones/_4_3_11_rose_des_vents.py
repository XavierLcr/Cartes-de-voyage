################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.11 – Script de création d'une rose des vents (version améliorée)         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import QPointF, Qt, QRectF
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QPolygonF,
    QRadialGradient,
    QFont,
)

# 1 -- Fonction de création de la rose des vents -------------------------------


def _dessiner_icone_rose_vents(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    rotation_deg: float = 0.0,
    afficher_lettre_nord: bool = True,
) -> None:
    """Icône boussole (rose des vents) :
    - étoile principale à 4 branches (N/E/S/O) en effet pinwheel
      (triangle clair + triangle sombre, dégradé radial pour le relief)
    - étoile secondaire à 4 branches intercardinales (NE/SE/SO/NO), plus
      courte et plus fine, placée en dessous, pour un rendu plus réaliste
    - double cercle de contour
    - graduations fines tous les 45°
    - repère coloré + lettre "N" marquant le nord
    - `rotation_deg` permet d'orienter la rose (utile si la carte n'est
      pas orientée plein nord vers le haut)
    """

    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    COULEUR_TEINTE_CLAIRE = QColor("#98C1D9")
    COULEUR_TEINTE_SOMBRE = QColor("#3D5A80")
    COULEUR_TEINTE_CLAIRE_SEC = QColor("#C4DDE9")
    COULEUR_TEINTE_SOMBRE_SEC = QColor("#5C7DA3")
    COULEUR_CERCLE = QColor("#3D5A80")
    COULEUR_NORD = QColor("#EE6C4D")
    COULEUR_CENTRE = QColor("#293241")
    COULEUR_TEXTE = QColor("#293241")

    cx, cy = centre.x(), centre.y()
    rayon_cercle_ext = taille * 0.46
    rayon_cercle_int = taille * 0.42
    rayon_long = taille * 0.40  # pointe des branches cardinales
    rayon_court = taille * 0.15  # base des branches cardinales
    rayon_long_sec = taille * 0.24  # pointe des branches intercardinales
    rayon_court_sec = taille * 0.08  # base des branches intercardinales
    rayon_centre = taille * 0.035
    rayon_pointe_nord = taille * 0.03
    rayon_graduation = taille * 0.44

    def point_angle(angle_deg: float, rayon: float) -> QPointF:
        # 0° = nord (en haut), sens horaire, + rotation globale
        angle_rad = math.radians(angle_deg - 90 + rotation_deg)
        return QPointF(
            cx + math.cos(angle_rad) * rayon, cy + math.sin(angle_rad) * rayon
        )

    # -- Cercles de contour (double liseré pour plus de relief) --------------
    pen_cercle = QPen(COULEUR_CERCLE)
    pen_cercle.setWidthF(taille * 0.012)
    pen_cercle.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_cercle)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setOpacity(0.55)
    painter.drawEllipse(centre, rayon_cercle_ext, rayon_cercle_ext)
    painter.setOpacity(0.3)
    painter.drawEllipse(centre, rayon_cercle_int, rayon_cercle_int)
    painter.setOpacity(1.0)

    # -- Graduations tous les 45° ---------------------------------------------
    pen_grad = QPen(COULEUR_CERCLE)
    pen_grad.setWidthF(taille * 0.01)
    pen_grad.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_grad)
    painter.setOpacity(0.35)
    for angle in range(0, 360, 45):
        p1 = point_angle(angle, rayon_graduation)
        p2 = point_angle(angle, rayon_graduation - taille * 0.025)
        painter.drawLine(p1, p2)
    painter.setOpacity(1.0)

    def dessiner_etoile(angles, rayon_pointe, rayon_base, clair, sombre):
        painter.setPen(Qt.PenStyle.NoPen)
        for angle_pointe in angles:
            pointe = point_angle(angle_pointe, rayon_pointe)
            cote_gauche = point_angle(angle_pointe - 45, rayon_base)
            cote_droit = point_angle(angle_pointe + 45, rayon_base)

            degrade_clair = QRadialGradient(centre, rayon_pointe)
            degrade_clair.setColorAt(0.0, clair.lighter(115))
            degrade_clair.setColorAt(1.0, clair)
            painter.setBrush(QBrush(degrade_clair))
            painter.drawPolygon(QPolygonF([centre, cote_gauche, pointe]))

            degrade_sombre = QRadialGradient(centre, rayon_pointe)
            degrade_sombre.setColorAt(0.0, sombre.lighter(110))
            degrade_sombre.setColorAt(1.0, sombre)
            painter.setBrush(QBrush(degrade_sombre))
            painter.drawPolygon(QPolygonF([centre, pointe, cote_droit]))

    # -- Étoile secondaire (intercardinale : NE, SE, SO, NO) — en dessous -----
    dessiner_etoile(
        (45, 135, 225, 315),
        rayon_long_sec,
        rayon_court_sec,
        COULEUR_TEINTE_CLAIRE_SEC,
        COULEUR_TEINTE_SOMBRE_SEC,
    )

    # -- Étoile principale (cardinale : N, E, S, O) — par-dessus --------------
    dessiner_etoile(
        (0, 90, 180, 270),
        rayon_long,
        rayon_court,
        COULEUR_TEINTE_CLAIRE,
        COULEUR_TEINTE_SOMBRE,
    )

    # -- Repère nord -------------------------------------------------------------
    pointe_nord = point_angle(0, rayon_long)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_NORD))
    painter.drawEllipse(pointe_nord, rayon_pointe_nord, rayon_pointe_nord)

    # -- Lettre "N" au-dessus du repère nord --------------------------------------
    if afficher_lettre_nord:
        police = QFont("Arial", max(1, int(taille * 0.11)))
        police.setBold(True)
        painter.setFont(police)
        painter.setPen(QPen(COULEUR_TEXTE))
        point_lettre = point_angle(0, rayon_cercle_ext + taille * 0.10)
        rect_lettre = QRectF(
            point_lettre.x() - taille * 0.12,
            point_lettre.y() - taille * 0.12,
            taille * 0.24,
            taille * 0.24,
        )
        painter.drawText(rect_lettre, Qt.AlignmentFlag.AlignCenter, "N")

    # -- Point central -------------------------------------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_CENTRE))
    painter.drawEllipse(centre, rayon_centre, rayon_centre)
