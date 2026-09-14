################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones/_4_3_48_avion                                       #
# 4.3.48.2 – Fonction de dessin d'un avion de ligne                            #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
)

from _4_Interface._4_3_Icones._4_3_48_avion._4_3_48_1_lumieres import (
    dessiner_lumiere_avion,
)

# 1 -- Fonctions de dessin d'un avion ------------------------------------------


## 1.1 -- Avion de ligne -------------------------------------------------------


def _dessiner_avion_ligne(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    rotation: float = 0.0,
    **kwargs,
) -> None:
    """
    Dessine un gros avion de ligne stylisé vu de dessus,
    inspiré des proportions d'un Airbus A380.

    `rotation` est exprimée en degrés.
    """

    if taille <= 0:
        return

    couleur = QColor(kwargs.get("couleur", "#E8ECEF"))
    couleur_secondaire = QColor(kwargs.get("couleur_secondaire", "#AAB4BC"))
    couleur_vitre = QColor(kwargs.get("couleur_vitre", "#496778"))
    couleur_moteur = QColor(kwargs.get("couleur_moteur", "#D7DDE1"))
    couleur_entree_moteur = QColor(kwargs.get("couleur_entree_moteur", "#4D5961"))
    lumieres = kwargs.get("lumieres", False)
    lumieres_droite = kwargs.get("lumieres_droite", "#35FF70")
    lumieres_gauche = kwargs.get("lumieres_gauche", "#FF3030")
    lumieres_centre = kwargs.get("lumieres_centre", "#FFFFFF")

    # L'A380 possède une très grande envergure.
    longueur = taille
    envergure = taille * 0.90

    rect = QRectF(
        centre.x() - longueur / 2,
        centre.y() - envergure / 2,
        longueur,
        envergure,
    )

    painter.save()

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing,
        True,
    )

    painter.translate(centre)
    painter.rotate(rotation)
    painter.translate(-centre)

    cx = centre.x()
    cy = centre.y()

    l = longueur
    h = envergure

    painter.setPen(Qt.PenStyle.NoPen)

    # --------------------------------------------------------------------------
    # Réacteurs
    # --------------------------------------------------------------------------

    def dessiner_moteur(
        x: float,
        y: float,
        echelle: float = 1.0,
    ) -> None:

        longueur_moteur = l * 0.105 * echelle
        largeur_moteur = h * 0.055 * echelle

        # Petit pylône reliant le moteur à l'aile
        pylone = QPainterPath()

        pylone.moveTo(
            x - longueur_moteur * 0.15,
            y,
        )

        pylone.lineTo(
            x - longueur_moteur * 0.35,
            y - largeur_moteur * 0.90,
        )

        pylone.lineTo(
            x + longueur_moteur * 0.18,
            y - largeur_moteur * 0.45,
        )

        pylone.closeSubpath()

        painter.setBrush(couleur_secondaire.darker(105))

        painter.drawPath(pylone)

        # Nacelle
        moteur = QPainterPath()

        moteur.moveTo(
            x + longueur_moteur / 2,
            y,
        )

        moteur.cubicTo(
            x + longueur_moteur * 0.38,
            y - largeur_moteur / 2,
            x - longueur_moteur * 0.32,
            y - largeur_moteur / 2,
            x - longueur_moteur / 2,
            y,
        )

        moteur.cubicTo(
            x - longueur_moteur * 0.32,
            y + largeur_moteur / 2,
            x + longueur_moteur * 0.38,
            y + largeur_moteur / 2,
            x + longueur_moteur / 2,
            y,
        )

        moteur.closeSubpath()

        gradient_moteur = QLinearGradient(
            x,
            y - largeur_moteur / 2,
            x,
            y + largeur_moteur / 2,
        )

        gradient_moteur.setColorAt(
            0.0,
            couleur_moteur.lighter(125),
        )

        gradient_moteur.setColorAt(
            0.5,
            couleur_moteur,
        )

        gradient_moteur.setColorAt(
            1.0,
            couleur_moteur.darker(115),
        )

        painter.setBrush(QBrush(gradient_moteur))
        painter.drawPath(moteur)

        # Entrée sombre du réacteur
        rayon = largeur_moteur * 0.31

        painter.setBrush(couleur_entree_moteur)

        painter.drawEllipse(
            QPointF(
                x + longueur_moteur * 0.39,
                y,
            ),
            rayon,
            rayon,
        )

        # Centre de la turbine
        painter.setBrush(couleur_entree_moteur.lighter(150))

        painter.drawEllipse(
            QPointF(
                x + longueur_moteur * 0.40,
                y,
            ),
            rayon * 0.30,
            rayon * 0.30,
        )

    # Deux réacteurs par aile
    positions_moteurs = (
        (cx + l * 0.045, cy - h * 0.155),
        (cx - l * 0.025, cy - h * 0.305),
        (cx + l * 0.045, cy + h * 0.155),
        (cx - l * 0.025, cy + h * 0.305),
    )

    for x, y in positions_moteurs:
        dessiner_moteur(
            x,
            y,
        )

    # --------------------------------------------------------------------------
    # Ailes
    # --------------------------------------------------------------------------

    ailes = QPainterPath()

    # Aile supérieure
    ailes.moveTo(
        cx + l * 0.13,
        cy - h * 0.040,
    )

    # Bord d'attaque : très balayé vers l'arrière
    ailes.lineTo(
        cx - l * 0.12,
        cy - h * 0.46,
    )

    # Saumon d'aile
    ailes.cubicTo(
        cx - l * 0.15,
        cy - h * 0.485,
        cx - l * 0.19,
        cy - h * 0.48,
        cx - l * 0.20,
        cy - h * 0.455,
    )

    # Bord de fuite
    ailes.lineTo(
        cx - l * 0.12,
        cy - h * 0.20,
    )

    ailes.lineTo(
        cx - l * 0.20,
        cy - h * 0.055,
    )

    ailes.lineTo(
        cx + l * 0.13,
        cy - h * 0.040,
    )

    ailes.closeSubpath()

    # Aile inférieure
    ailes.moveTo(
        cx + l * 0.13,
        cy + h * 0.040,
    )

    ailes.lineTo(
        cx - l * 0.12,
        cy + h * 0.46,
    )

    ailes.cubicTo(
        cx - l * 0.15,
        cy + h * 0.485,
        cx - l * 0.19,
        cy + h * 0.48,
        cx - l * 0.20,
        cy + h * 0.455,
    )

    ailes.lineTo(
        cx - l * 0.12,
        cy + h * 0.20,
    )

    ailes.lineTo(
        cx - l * 0.20,
        cy + h * 0.055,
    )

    ailes.lineTo(
        cx + l * 0.13,
        cy + h * 0.040,
    )

    ailes.closeSubpath()

    gradient_ailes = QLinearGradient(
        cx,
        cy - h / 2,
        cx,
        cy + h / 2,
    )

    gradient_ailes.setColorAt(
        0.0,
        couleur_secondaire.lighter(118),
    )

    gradient_ailes.setColorAt(
        0.5,
        couleur_secondaire,
    )

    gradient_ailes.setColorAt(
        1.0,
        couleur_secondaire.darker(108),
    )

    painter.setBrush(QBrush(gradient_ailes))
    painter.drawPath(ailes)

    # --------------------------------------------------------------------------
    # Empennage horizontal
    # --------------------------------------------------------------------------

    empennage = QPainterPath()

    # Partie supérieure
    empennage.moveTo(
        cx - l * 0.34,
        cy - h * 0.028,
    )

    empennage.lineTo(
        cx - l * 0.45,
        cy - h * 0.20,
    )

    empennage.cubicTo(
        cx - l * 0.47,
        cy - h * 0.22,
        cx - l * 0.49,
        cy - h * 0.21,
        cx - l * 0.48,
        cy - h * 0.18,
    )

    empennage.lineTo(
        cx - l * 0.415,
        cy - h * 0.025,
    )

    empennage.closeSubpath()

    # Partie inférieure
    empennage.moveTo(
        cx - l * 0.34,
        cy + h * 0.028,
    )

    empennage.lineTo(
        cx - l * 0.45,
        cy + h * 0.20,
    )

    empennage.cubicTo(
        cx - l * 0.47,
        cy + h * 0.22,
        cx - l * 0.49,
        cy + h * 0.21,
        cx - l * 0.48,
        cy + h * 0.18,
    )

    empennage.lineTo(
        cx - l * 0.415,
        cy + h * 0.025,
    )

    empennage.closeSubpath()

    painter.setBrush(couleur_secondaire)
    painter.drawPath(empennage)

    # --------------------------------------------------------------------------
    # Fuselage
    # --------------------------------------------------------------------------

    fuselage = QPainterPath()

    # Pointe avant arrondie
    fuselage.moveTo(
        cx + l * 0.50,
        cy,
    )

    # Flanc supérieur
    fuselage.cubicTo(
        cx + l * 0.485,
        cy - h * 0.025,
        cx + l * 0.44,
        cy - h * 0.043,
        cx + l * 0.36,
        cy - h * 0.050,
    )

    fuselage.cubicTo(
        cx + l * 0.15,
        cy - h * 0.060,
        cx - l * 0.15,
        cy - h * 0.060,
        cx - l * 0.34,
        cy - h * 0.045,
    )

    # Rétrécissement vers la queue
    fuselage.cubicTo(
        cx - l * 0.41,
        cy - h * 0.038,
        cx - l * 0.46,
        cy - h * 0.020,
        cx - l * 0.49,
        cy,
    )

    fuselage.cubicTo(
        cx - l * 0.46,
        cy + h * 0.020,
        cx - l * 0.41,
        cy + h * 0.038,
        cx - l * 0.34,
        cy + h * 0.045,
    )

    fuselage.cubicTo(
        cx - l * 0.15,
        cy + h * 0.060,
        cx + l * 0.15,
        cy + h * 0.060,
        cx + l * 0.36,
        cy + h * 0.050,
    )

    fuselage.cubicTo(
        cx + l * 0.44,
        cy + h * 0.043,
        cx + l * 0.485,
        cy + h * 0.025,
        cx + l * 0.50,
        cy,
    )

    fuselage.closeSubpath()

    gradient_fuselage = QLinearGradient(
        cx,
        cy - h * 0.07,
        cx,
        cy + h * 0.07,
    )

    gradient_fuselage.setColorAt(
        0.0,
        couleur.lighter(125),
    )

    gradient_fuselage.setColorAt(
        0.48,
        couleur,
    )

    gradient_fuselage.setColorAt(
        1.0,
        couleur.darker(115),
    )

    painter.setBrush(QBrush(gradient_fuselage))
    painter.drawPath(fuselage)

    # --------------------------------------------------------------------------
    # Cockpit
    # --------------------------------------------------------------------------

    cockpit = QPainterPath()

    cockpit.moveTo(
        cx + l * 0.455,
        cy,
    )

    cockpit.cubicTo(
        cx + l * 0.440,
        cy - h * 0.018,
        cx + l * 0.410,
        cy - h * 0.025,
        cx + l * 0.390,
        cy - h * 0.019,
    )

    cockpit.lineTo(
        cx + l * 0.405,
        cy,
    )

    cockpit.lineTo(
        cx + l * 0.390,
        cy + h * 0.019,
    )

    cockpit.cubicTo(
        cx + l * 0.410,
        cy + h * 0.025,
        cx + l * 0.440,
        cy + h * 0.018,
        cx + l * 0.455,
        cy,
    )

    cockpit.closeSubpath()

    painter.setBrush(couleur_vitre)
    painter.drawPath(cockpit)

    # --------------------------------------------------------------------------
    # Double rangée de hublots
    # --------------------------------------------------------------------------

    if taille >= 70:

        couleur_hublots = couleur_vitre.darker(115)

        painter.setBrush(couleur_hublots)

        rayon_hublot = max(
            0.7,
            l * 0.0040,
        )

        n_hublots = 18

        x_debut = cx - l * 0.27
        x_fin = cx + l * 0.32

        for i in range(n_hublots):

            t = i / (n_hublots - 1)

            x = x_debut + (x_fin - x_debut) * t

            # Deux ponts de l'A380 suggérés par
            # deux lignes de petits hublots.
            for y in (
                cy - h * 0.020,
                cy + h * 0.020,
            ):

                painter.drawEllipse(
                    QPointF(x, y),
                    rayon_hublot,
                    rayon_hublot * 0.65,
                )

    # --------------------------------------------------------------------------
    # Lumières
    # --------------------------------------------------------------------------

    if lumieres == True:

        rayon_lumiere = l * 0.05

        # Gauche
        dessiner_lumiere_avion(
            painter,
            QPointF(
                cx - l * 0.15,
                cy - h * 0.465,
            ),
            lumieres_gauche,
            rayon_lumiere,
        )

        # Droite
        dessiner_lumiere_avion(
            painter,
            QPointF(
                cx - l * 0.15,
                cy + h * 0.465,
            ),
            lumieres_droite,
            rayon_lumiere,
        )

        # Centre
        dessiner_lumiere_avion(
            painter,
            QPointF(
                cx - l * 0.485,
                cy,
            ),
            lumieres_centre,
            rayon_lumiere * 0.8,
        )

    painter.restore()
