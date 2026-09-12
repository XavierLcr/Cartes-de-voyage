################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.41 – Script de création d'un poulpe                                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QBrush,
    QPen,
    QColor,
    QRadialGradient,
)

# 1 -- Fonction de création du poulpe ------------------------------------------


def _dessiner_poulpe(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    sens: float,
    couleur: QColor,
    phase: float = 0.0,
    degrade: bool = True,
) -> None:
    """Dessine un petit poulpe stylisé nageant horizontalement.

    Le manteau se gonfle et se contracte doucement au rythme de `phase`.
    Les huit bras sont longs, souples et ondulent indépendamment.

    Orienté vers la droite si `sens > 0`.
    """

    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    painter.translate(centre)

    if sens < 0:
        painter.scale(-1, 1)

    # --- Animation générale ---------------------------------------------------

    # Respiration / gonflement du manteau.
    respiration = math.sin(phase * 0.75)

    # Mouvement vertical très léger du poulpe.
    flottement = math.sin(phase * 0.75 + 0.8) * taille * 0.025
    painter.translate(0, flottement)

    # Le corps gonfle davantage en hauteur qu'en largeur.
    facteur_x = 1.0 + respiration * 0.045
    facteur_y = 1.0 + respiration * 0.095

    # --- Dimensions ------------------------------------------------------------

    # Corps volontairement plus petit que dans la première version.
    rx = taille * 0.22 * facteur_x
    ry = taille * 0.30 * facteur_y

    # Le centre du manteau est légèrement décalé vers l'avant.
    corps_x = taille * 0.10

    # --- Couleurs --------------------------------------------------------------

    trait = QColor(couleur).darker(145)
    trait.setAlpha(210)

    pen = QPen(trait)
    pen.setWidthF(max(0.8, taille * 0.025))

    couleur_bras = QColor(couleur).darker(108)
    couleur_bras.setAlpha(245)

    # ==========================================================================
    # 2 -- Tentacules
    # ==========================================================================

    # On dessine les tentacules avant le manteau pour que leur naissance
    # soit naturellement masquée par le corps.

    painter.setPen(pen)

    # Positions de départ autour de la partie basse du manteau.
    #
    # Les quatre premiers forment la partie inférieure visible.
    # Les quatre autres donnent de la profondeur sur les côtés.

    positions_bras = [
        # x, y, longueur, amplitude, phase supplémentaire
        (-0.72, 0.38, 0.34, 0.070, 0.0),
        (-0.48, 0.55, 0.42, 0.085, 0.8),
        (-0.20, 0.65, 0.47, 0.075, 1.6),
        (0.08, 0.64, 0.43, 0.090, 2.3),
        (0.34, 0.55, 0.40, 0.070, 3.0),
        (0.58, 0.43, 0.34, 0.085, 3.7),
        (-0.58, 0.68, 0.38, 0.060, 4.4),
        (0.30, 0.70, 0.40, 0.065, 5.0),
    ]

    for i, (px, py, longueur, amplitude, phase_offset) in enumerate(positions_bras):

        # Les bras suivent légèrement la respiration du corps.
        ouverture = 1.0 + respiration * 0.035

        x0 = corps_x + px * rx
        y0 = py * ry

        longueur_reelle = taille * longueur * ouverture
        amplitude_reelle = taille * amplitude

        phase_bras = phase * 1.05 + phase_offset

        # Chaque bras possède sa propre ondulation.
        ondulation_1 = math.sin(phase_bras)
        ondulation_2 = math.sin(phase_bras + 1.2)

        # Les tentacules partent vers l'arrière (gauche).
        x1 = x0 - longueur_reelle

        # Point de contrôle principal.
        xm = x0 - longueur_reelle * 0.48
        ym = y0 + ondulation_1 * amplitude_reelle

        # Extrémité.
        y1 = y0 + ondulation_2 * amplitude_reelle * 0.72

        # ----------------------------------------------------------------------
        # Silhouette du tentacule
        # ----------------------------------------------------------------------

        # Épaisseur plus importante à la base et fine à l'extrémité.
        e_base = taille * 0.042
        e_milieu = taille * 0.027
        e_pointe = taille * 0.008

        # Première moitié du ruban.
        bras = QPainterPath()

        bras.moveTo(QPointF(x0, y0 - e_base))

        bras.quadTo(
            QPointF(
                xm,
                ym - e_milieu,
            ),
            QPointF(
                x1,
                y1 - e_pointe,
            ),
        )

        # Pointe.
        bras.lineTo(
            QPointF(
                x1 - taille * 0.015,
                y1,
            )
        )

        # Retour par le dessous.
        bras.quadTo(
            QPointF(
                xm,
                ym + e_milieu,
            ),
            QPointF(
                x0,
                y0 + e_base,
            ),
        )

        bras.closeSubpath()

        painter.setPen(pen)
        painter.setBrush(QBrush(couleur_bras))
        painter.drawPath(bras)

        # ----------------------------------------------------------------------
        # Ventouses
        # ----------------------------------------------------------------------

        # Très petites et peu nombreuses pour rester lisibles.
        painter.setPen(Qt.PenStyle.NoPen)

        ventouse = QColor(couleur).lighter(155)
        ventouse.setAlpha(120)
        painter.setBrush(QBrush(ventouse))

        for j in range(3):

            t = 0.25 + j * 0.22

            x = x0 + (x1 - x0) * t

            y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * ym + t**2 * y1

            # Les ventouses sont légèrement décalées vers le dessous.
            y += taille * 0.018

            r = taille * 0.010

            painter.drawEllipse(
                QPointF(x, y),
                r,
                r,
            )

    # ==========================================================================
    # 3 -- Manteau gonflable
    # ==========================================================================

    if degrade:

        gradient = QRadialGradient(
            QPointF(
                corps_x - rx * 0.25,
                -ry * 0.35,
            ),
            max(rx, ry) * 1.25,
        )

        gradient.setColorAt(
            0.0,
            QColor(couleur).lighter(145),
        )

        gradient.setColorAt(
            0.58,
            QColor(couleur),
        )

        gradient.setColorAt(
            1.0,
            QColor(couleur).darker(122),
        )

        pinceau_corps = QBrush(gradient)

    else:
        pinceau_corps = QBrush(couleur)

    painter.setPen(pen)
    painter.setBrush(pinceau_corps)

    # Le manteau n'est volontairement PAS une ellipse parfaite.
    # Son sommet est bombé et sa partie basse se resserre.

    corps = QPainterPath()

    # Départ bas-gauche.
    corps.moveTo(
        QPointF(
            corps_x - rx * 0.75,
            ry * 0.48,
        )
    )

    # Flanc gauche.
    corps.cubicTo(
        QPointF(
            corps_x - rx * 1.05,
            ry * 0.05,
        ),
        QPointF(
            corps_x - rx * 0.95,
            -ry * 0.72,
        ),
        QPointF(
            corps_x - rx * 0.25,
            -ry * 0.96,
        ),
    )

    # Sommet.
    corps.cubicTo(
        QPointF(
            corps_x + rx * 0.25,
            -ry * 1.10,
        ),
        QPointF(
            corps_x + rx * 0.90,
            -ry * 0.72,
        ),
        QPointF(
            corps_x + rx * 0.98,
            -ry * 0.05,
        ),
    )

    # Avant du manteau.
    corps.cubicTo(
        QPointF(
            corps_x + rx * 1.05,
            ry * 0.40,
        ),
        QPointF(
            corps_x + rx * 0.68,
            ry * 0.68,
        ),
        QPointF(
            corps_x + rx * 0.25,
            ry * 0.72,
        ),
    )

    # Partie basse resserrée.
    corps.cubicTo(
        QPointF(
            corps_x - rx * 0.05,
            ry * 0.77,
        ),
        QPointF(
            corps_x - rx * 0.48,
            ry * 0.67,
        ),
        QPointF(
            corps_x - rx * 0.75,
            ry * 0.48,
        ),
    )

    corps.closeSubpath()

    painter.drawPath(corps)

    # ==========================================================================
    # 4 -- Petit reflet sur le manteau
    # ==========================================================================

    painter.setPen(Qt.PenStyle.NoPen)

    reflet = QColor(couleur).lighter(170)
    reflet.setAlpha(55)
    painter.setBrush(QBrush(reflet))

    painter.drawEllipse(
        QPointF(
            corps_x - rx * 0.25,
            -ry * 0.42,
        ),
        rx * 0.25,
        ry * 0.16,
    )

    # ==========================================================================
    # 5 -- Yeux
    # ==========================================================================

    oeil_r = taille * 0.060

    # Deux yeux placés vers l'avant du manteau.
    yeux = (
        QPointF(
            corps_x + rx * 0.54,
            -ry * 0.34,
        ),
        QPointF(
            corps_x + rx * 0.62,
            -ry * 0.05,
        ),
    )

    for oeil_centre in yeux:

        # Blanc.
        painter.setBrush(QBrush(QColor("#FFFFFF")))

        painter.drawEllipse(
            oeil_centre,
            oeil_r,
            oeil_r,
        )

        # Pupille légèrement orientée vers l'avant.
        painter.setBrush(QBrush(QColor("#1C1F2B")))

        painter.drawEllipse(
            QPointF(
                oeil_centre.x() + oeil_r * 0.18,
                oeil_centre.y(),
            ),
            oeil_r * 0.48,
            oeil_r * 0.48,
        )

        # Reflet.
        painter.setBrush(QBrush(QColor(255, 255, 255, 220)))

        painter.drawEllipse(
            QPointF(
                oeil_centre.x() + oeil_r * 0.28,
                oeil_centre.y() - oeil_r * 0.22,
            ),
            oeil_r * 0.16,
            oeil_r * 0.16,
        )

    # ==========================================================================
    # 6 -- Petite bouche
    # ==========================================================================

    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    bouche = QPainterPath()

    bouche.moveTo(
        QPointF(
            corps_x + rx * 0.70,
            ry * 0.20,
        )
    )

    bouche.quadTo(
        QPointF(
            corps_x + rx * 0.80,
            ry * 0.27,
        ),
        QPointF(
            corps_x + rx * 0.88,
            ry * 0.18,
        ),
    )

    painter.drawPath(bouche)

    painter.restore()
