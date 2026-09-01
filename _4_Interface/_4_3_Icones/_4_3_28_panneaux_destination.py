################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.28 – Script de création de l'icône de voyage                             #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QLinearGradient,
    QRadialGradient,
    QPolygonF,
)

# 1 -- Pictogrammes internes aux panneaux --------------------------------------


### Avion ----------------------------------------------------------------------


def _dessiner_glyphe_avion(painter: QPainter, centre: QPointF, echelle: float) -> None:
    """Petit avion stylisé (vue de dessus), en aplat blanc."""
    cx, cy = centre.x(), centre.y()
    forme = QPolygonF(
        [
            QPointF(cx + echelle * 0.85, cy),
            QPointF(cx - echelle * 0.30, cy - echelle * 0.42),
            QPointF(cx - echelle * 0.05, cy),
            QPointF(cx - echelle * 0.30, cy + echelle * 0.42),
        ]
    )
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
    painter.drawPolygon(forme)


### Train ----------------------------------------------------------------------


def _dessiner_glyphe_train(painter: QPainter, centre: QPointF, echelle: float) -> None:
    """Petit train stylisé (vue de côté), en aplat blanc avec fenêtre et roues."""
    cx, cy = centre.x(), centre.y()
    largeur = echelle * 1.5
    hauteur = echelle * 0.85

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
    painter.drawRoundedRect(
        int(cx - largeur / 2),
        int(cy - hauteur / 2),
        int(largeur),
        int(hauteur * 0.85),
        int(hauteur * 0.25),
        int(hauteur * 0.25),
    )

    # Fenêtre (découpe par contraste, couleur du panneau redessinée par-dessus)
    painter.setBrush(QBrush(QColor(255, 255, 255, 60)))
    painter.drawRoundedRect(
        int(cx - largeur * 0.28),
        int(cy - hauteur * 0.32),
        int(largeur * 0.4),
        int(hauteur * 0.35),
        int(hauteur * 0.08),
        int(hauteur * 0.08),
    )

    # Roues
    painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
    rayon_roue = hauteur * 0.20
    y_roue = cy + hauteur * 0.30
    painter.drawEllipse(QPointF(cx - largeur * 0.22, y_roue), rayon_roue, rayon_roue)
    painter.drawEllipse(QPointF(cx + largeur * 0.22, y_roue), rayon_roue, rayon_roue)


### Bateau ---------------------------------------------------------------------


def _dessiner_glyphe_bateau(painter: QPainter, centre: QPointF, echelle: float) -> None:
    """Petit voilier stylisé (vue de côté), coque + mât + voile."""
    cx, cy = centre.x(), centre.y()

    # Coque (trapèze pointu vers le bas)
    coque = QPolygonF(
        [
            QPointF(cx - echelle * 0.75, cy + echelle * 0.05),
            QPointF(cx + echelle * 0.75, cy + echelle * 0.05),
            QPointF(cx + echelle * 0.35, cy + echelle * 0.48),
            QPointF(cx - echelle * 0.35, cy + echelle * 0.48),
        ]
    )
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
    painter.drawPolygon(coque)

    # Mât
    pen_mat = QPen(QColor(255, 255, 255, 235))
    pen_mat.setWidthF(echelle * 0.08)
    pen_mat.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_mat)
    painter.drawLine(
        QPointF(cx, cy + echelle * 0.05),
        QPointF(cx, cy - echelle * 0.65),
    )

    # Voile
    voile = QPolygonF(
        [
            QPointF(cx, cy - echelle * 0.60),
            QPointF(cx, cy - echelle * 0.02),
            QPointF(cx + echelle * 0.55, cy - echelle * 0.02),
        ]
    )
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPolygon(voile)


### Dictionnaire des panneaux --------------------------------------------------


GLYPHES = {
    "avion": _dessiner_glyphe_avion,
    "train": _dessiner_glyphe_train,
    "bateau": _dessiner_glyphe_bateau,
}


# 2 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_icone_voyage(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône "voyager" : un panneau directionnel (poteau + 3 flèches), chaque
    flèche pointant une direction différente et portant un petit pictogramme
    (avion / train / bateau). Style cohérent avec le reste du projet : dégradés
    doux, ombres portées légères, coins arrondis."""

    COULEUR_POTEAU_CLAIR = QColor("#C7CCD6")
    COULEUR_POTEAU_FONCE = QColor("#8B93A1")

    PANNEAUX = [
        (-0.30, 1, QColor("#33C7E8"), "avion"),
        (-0.02, -1, QColor("#FF6F6F"), "train"),
        (0.26, 1, QColor("#8C6FFF"), "bateau"),
    ]

    cx, cy = centre.x(), centre.y()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # -- 2.1 Ombre au sol -----------------------------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    ombre_sol = QRadialGradient(QPointF(cx, cy + taille * 0.48), taille * 0.22)
    ombre_sol.setColorAt(0.0, QColor(0, 0, 0, 55))
    ombre_sol.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.setBrush(QBrush(ombre_sol))
    painter.drawEllipse(QPointF(cx, cy + taille * 0.48), taille * 0.20, taille * 0.06)

    # -- 2.2 Poteau -------------------------------------------------------------
    epaisseur_poteau = taille * 0.045
    y_haut_poteau = cy - taille * 0.46
    y_bas_poteau = cy + taille * 0.46

    degrade_poteau = QLinearGradient(cx - epaisseur_poteau, 0, cx + epaisseur_poteau, 0)
    degrade_poteau.setColorAt(0.0, COULEUR_POTEAU_CLAIR)
    degrade_poteau.setColorAt(1.0, COULEUR_POTEAU_FONCE)

    pen_poteau = QPen(QBrush(degrade_poteau), epaisseur_poteau)
    pen_poteau.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_poteau)
    painter.drawLine(QPointF(cx, y_haut_poteau), QPointF(cx, y_bas_poteau))

    # -- 2.3 Panneaux directionnels ---------------------------------------------
    longueur_panneau = taille * 0.44
    hauteur_panneau = taille * 0.16
    longueur_pointe = taille * 0.10

    for y_relatif, direction, couleur, nom_glyphe in PANNEAUX:
        y = cy + taille * y_relatif
        x_debut = cx - direction * taille * 0.01
        x_fin_rect = x_debut + direction * (longueur_panneau - longueur_pointe)
        x_pointe = x_debut + direction * longueur_panneau

        panneau = QPolygonF(
            [
                QPointF(x_debut, y - hauteur_panneau / 2),
                QPointF(x_fin_rect, y - hauteur_panneau / 2),
                QPointF(x_pointe, y),
                QPointF(x_fin_rect, y + hauteur_panneau / 2),
                QPointF(x_debut, y + hauteur_panneau / 2),
            ]
        )

        # Ombre du panneau
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 35)))
        painter.drawPolygon(panneau.translated(0, taille * 0.02))

        # Remplissage dégradé
        degrade_panneau = QLinearGradient(
            QPointF(x_debut, y - hauteur_panneau / 2),
            QPointF(x_pointe, y + hauteur_panneau / 2),
        )
        degrade_panneau.setColorAt(0.0, couleur.lighter(130))
        degrade_panneau.setColorAt(1.0, couleur.darker(110))

        pen_contour = QPen(couleur.darker(150))
        pen_contour.setWidthF(taille * 0.008)
        pen_contour.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen_contour)
        painter.setBrush(QBrush(degrade_panneau))
        painter.drawPolygon(panneau)

        # Pictogramme centré dans la partie rectangulaire du panneau
        x_centre_glyphe = (x_debut + x_fin_rect) / 2
        centre_glyphe = QPointF(x_centre_glyphe, y)
        GLYPHES[nom_glyphe](painter, centre_glyphe, hauteur_panneau * 0.5)

    # -- 2.4 Capuchon arrondi en haut du poteau ----------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_POTEAU_CLAIR))
    painter.drawEllipse(
        QPointF(cx, y_haut_poteau), epaisseur_poteau * 0.9, epaisseur_poteau * 0.9
    )
