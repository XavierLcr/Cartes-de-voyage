################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.31 – Script de création de l'icône d'un calendrier                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_icone_calendrier(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône calendrier minimaliste avec lignes représentant les jours."""

    COULEUR_CORPS = QColor("#5EC9B3")
    COULEUR_ACCENT = QColor("#F2789F")
    COULEUR_PAPIER = QColor("#FFFFFF")
    COULEUR_JOUR = QColor("#AAA59D")

    cx, cy = centre.x(), centre.y()

    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # ------------------------------------------------------------------
    # Dimensions
    # ------------------------------------------------------------------

    largeur = taille * 0.78
    hauteur = taille * 0.70

    x = cx - largeur / 2
    y = cy - hauteur / 2

    rayon = taille * 0.085

    epaisseur = max(1.0, taille * 0.035)

    # ------------------------------------------------------------------
    # Corps du calendrier
    # ------------------------------------------------------------------

    painter.setPen(
        QPen(
            COULEUR_CORPS,
            epaisseur,
        )
    )
    painter.setBrush(COULEUR_PAPIER)

    painter.drawRoundedRect(
        QRectF(
            x,
            y,
            largeur,
            hauteur,
        ),
        rayon,
        rayon,
    )

    # ------------------------------------------------------------------
    # Bandeau supérieur
    # ------------------------------------------------------------------

    hauteur_bandeau = hauteur * 0.30

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(COULEUR_CORPS)

    painter.drawRoundedRect(
        QRectF(
            x,
            y,
            largeur,
            hauteur_bandeau + rayon,
        ),
        rayon,
        rayon,
    )

    # Partie inférieure du bandeau droite
    painter.drawRect(
        QRectF(
            x,
            y + hauteur_bandeau - rayon,
            largeur,
            rayon,
        )
    )

    # ------------------------------------------------------------------
    # Attaches supérieures
    # ------------------------------------------------------------------

    largeur_attache = taille * 0.075
    hauteur_attache = taille * 0.19

    for ratio in (0.28, 0.72):

        ax = x + largeur * ratio

        # Petit cercle blanc autour de l'attache
        painter.setBrush(COULEUR_PAPIER)

        painter.drawEllipse(
            QPointF(ax, y + taille * 0.025),
            largeur_attache * 0.95,
            largeur_attache * 0.95,
        )

        # Attache rose
        painter.setBrush(COULEUR_ACCENT)

        painter.drawRoundedRect(
            QRectF(
                ax - largeur_attache / 2,
                y - taille * 0.025,
                largeur_attache,
                hauteur_attache,
            ),
            largeur_attache / 2,
            largeur_attache / 2,
        )

    # ------------------------------------------------------------------
    # Ligne de séparation
    # ------------------------------------------------------------------

    painter.setPen(
        QPen(
            COULEUR_CORPS.lighter(130),
            max(0.7, taille * 0.018),
        )
    )

    ligne_y = y + hauteur_bandeau

    painter.drawLine(
        QPointF(x + taille * 0.03, ligne_y),
        QPointF(x + largeur - taille * 0.03, ligne_y),
    )

    # ------------------------------------------------------------------
    # Lignes représentant les jours
    # ------------------------------------------------------------------

    # 4 colonnes × 3 lignes.
    # On ne remplit volontairement pas toute la grille :
    # cela donne un aspect plus léger à petite taille.

    nombre_colonnes = 4
    nombre_lignes = 3

    largeur_zone = largeur * 0.68
    hauteur_zone = hauteur * 0.40

    debut_x = cx - largeur_zone / 2
    debut_y = y + hauteur * 0.48

    espacement_x = largeur_zone / (nombre_colonnes - 1)
    espacement_y = hauteur_zone / (nombre_lignes - 1)

    longueur_trait = taille * 0.105
    epaisseur_trait = max(1.3, taille * 0.045)

    jours = {
        (0, 0),
        (1, 0),
        (2, 0),
        (3, 0),
        (0, 1),
        (1, 1),
        (2, 1),
        (3, 1),
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
    }

    # Jour sélectionné
    jour_selectionne = (2, 1)

    for colonne, ligne in jours:

        px = debut_x + colonne * espacement_x
        py = debut_y + ligne * espacement_y

        est_selectionne = (colonne, ligne) == jour_selectionne

        painter.setPen(
            QPen(
                COULEUR_ACCENT if est_selectionne else COULEUR_JOUR,
                epaisseur_trait,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )

        painter.drawLine(
            QPointF(
                px - longueur_trait / 2,
                py,
            ),
            QPointF(
                px + longueur_trait / 2,
                py,
            ),
        )

    painter.restore()
