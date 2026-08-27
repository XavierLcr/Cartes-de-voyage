################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.5 – Script de création du globe terrestre                                #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QRadialGradient, QPainterPath, QPen

# 1 -- Fonction de création du globe terrestre ---------------------------------


def _dessiner_badge_globe(
    painter: QPainter, rect: QRectF, badge_debut, badge_fin
) -> None:
    """
    Badge circulaire en forme de globe, avec un rendu plus réaliste :
    dégradé sphérique (lumière décentrée) émeraude -> bleu océan,
    continents suggérés, grille de méridiens/parallèles et reflet
    spéculaire. L'état du QPainter est entièrement restauré à la fin
    (save/restore), donc le reste du rendu du widget n'est pas affecté.
    """
    painter.save()

    centre = rect.center()
    s = rect.width()
    rayon = s / 2

    bleu_ocean = QColor("#38BDF8")

    # --- sphère : dégradé radial décentré (lumière en haut à gauche) ---
    foyer = QPointF(centre.x() - rayon * 0.35, centre.y() - rayon * 0.4)
    degrade = QRadialGradient(centre, rayon * 1.05, foyer)
    degrade.setColorAt(0.0, badge_debut.lighter(122))
    degrade.setColorAt(0.42, badge_debut)
    degrade.setColorAt(0.75, bleu_ocean)
    degrade.setColorAt(1.0, badge_fin.darker(118))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(degrade))
    painter.drawEllipse(rect)

    # --- on limite le reste du dessin (continents, grille) au disque ---
    chemin_sphere = QPainterPath()
    chemin_sphere.addEllipse(rect)
    painter.setClipPath(chemin_sphere)

    # --- continents suggérés : taches vert soutenu, formes arrondies ---
    couleur_terre = badge_fin.darker(135)
    couleur_terre.setAlpha(150)
    painter.setBrush(QBrush(couleur_terre))
    painter.setPen(Qt.PenStyle.NoPen)

    terre_1 = QPainterPath()
    terre_1.addRoundedRect(
        QRectF(
            centre.x() - rayon * 0.78,
            centre.y() - rayon * 0.12,
            rayon * 0.68,
            rayon * 0.55,
        ),
        rayon * 0.22,
        rayon * 0.22,
    )
    painter.drawPath(terre_1)

    terre_2 = QPainterPath()
    terre_2.addRoundedRect(
        QRectF(
            centre.x() + rayon * 0.05,
            centre.y() - rayon * 0.68,
            rayon * 0.55,
            rayon * 0.42,
        ),
        rayon * 0.18,
        rayon * 0.18,
    )
    painter.drawPath(terre_2)

    terre_3 = QPainterPath()
    terre_3.addRoundedRect(
        QRectF(
            centre.x() + rayon * 0.12,
            centre.y() + rayon * 0.22,
            rayon * 0.42,
            rayon * 0.38,
        ),
        rayon * 0.16,
        rayon * 0.16,
    )
    painter.drawPath(terre_3)

    # --- contour de la sphère ---
    contour = QPen(QColor(255, 255, 255, 200))
    contour.setWidthF(s * 0.026)
    painter.setPen(contour)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(rect)

    # --- grille : méridiens + parallèles, en bleu clair (plus réaliste) ---
    grille = QPen(bleu_ocean.lighter(110))
    grille.setWidthF(s * 0.020)
    painter.setPen(grille)

    rayon_globe = rayon * 0.98
    for facteur in (0.85, 0.42):
        rect_meridien = QRectF(
            centre.x() - rayon_globe * facteur,
            centre.y() - rayon_globe,
            rayon_globe * facteur * 2,
            rayon_globe * 2,
        )
        painter.drawEllipse(rect_meridien)

    for decalage in (-0.35, 0.0, 0.4):
        painter.drawLine(
            QPointF(centre.x() - rayon_globe, centre.y() + rayon_globe * decalage),
            QPointF(centre.x() + rayon_globe, centre.y() + rayon_globe * decalage),
        )

    # --- reflet spéculaire (brillance en haut à gauche, effet "sphère") ---
    reflet = QRadialGradient(
        QPointF(centre.x() - rayon * 0.4, centre.y() - rayon * 0.45),
        rayon * 0.55,
    )
    reflet.setColorAt(0.0, QColor(255, 255, 255, 130))
    reflet.setColorAt(1.0, QColor(255, 255, 255, 0))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(reflet))
    painter.drawEllipse(
        QRectF(
            centre.x() - rayon * 0.75,
            centre.y() - rayon * 0.8,
            rayon * 1.0,
            rayon * 0.85,
        )
    )

    painter.setClipping(False)

    # --- repère "continent favori" : petit point blanc en haut à droite du globe ---
    rayon_repere = s * 0.10
    point_repere = QPointF(centre.x() + rayon * 0.6, centre.y() - rayon * 0.62)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
    painter.drawEllipse(point_repere, rayon_repere, rayon_repere)
    painter.setBrush(QBrush(badge_debut))
    painter.drawEllipse(point_repere, rayon_repere * 0.45, rayon_repere * 0.45)

    painter.restore()
