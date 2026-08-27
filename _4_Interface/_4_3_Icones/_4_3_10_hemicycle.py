################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.10 – Script de création d'un hémicycle miniature    '                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math, random

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QBrush

# 1 -- Génération des points ---------------------------------------------------


def _generer_points_hemicycle(
    nb_points: int = 25,
    nb_continents: int = 6,
    taux_visite: float = 0.55,
    graine: int = 42,
) -> list[tuple[int, bool]]:
    """Génère une répartition équilibrée des points sur les continents
    (chaque continent reçoit le même nombre de points, à 1 près),
    avec un ratio visité/non-visité cohérent, puis mélange l'ordre
    de façon déterministe (graine fixe) pour un rendu reproductible."""
    base, reste = divmod(nb_points, nb_continents)
    repartition = [base + (1 if i < reste else 0) for i in range(nb_continents)]

    points = []
    for continent, effectif in enumerate(repartition):
        nb_visites = round(effectif * taux_visite)
        points += [(continent, True)] * nb_visites
        points += [(continent, False)] * (effectif - nb_visites)

    rng = random.Random(graine)
    rng.shuffle(points)
    return points


# 2 -- Classe de l'hémicycle miniature -----------------------------------------


def _dessiner_icone_hemicycle(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Icône hémicycle : points disposés en arc (façon hémicycle parlementaire),
    un point = un pays, coloré par continent, plus foncé/opaque si visité."""

    # Couleurs de base par continent (teinte moyenne, avant assombrissement/éclaircissement)
    COULEURS_CONTINENTS = [
        QColor("#9A0EE6"),  # Europe
        QColor("#968914"),  # Afrique
        QColor("#BD1F1C"),  # Asie
        QColor("#1310CE"),  # Amérique du Nord
        QColor("#1FB847"),  # Amérique du Sud
        QColor("#17959E"),  # Océanie
    ]

    # Séquence des points de l'hémicycle : (continent, visité)
    # Un mélange volontairement varié pour donner un effet "peuplé"
    POINTS = _generer_points_hemicycle(
        nb_points=24, nb_continents=len(COULEURS_CONTINENTS)
    )

    rayon_arc = taille * 0.40
    rayon_point = taille * 0.045

    # Répartition sur un demi-cercle (de 180° à 0°, donc arc supérieur)
    # sur 2 rangées pour un effet "hémicycle" plus dense
    rangees = [
        (rayon_arc, 10),  # rangée extérieure
        (rayon_arc * 0.62, 8),  # rangée du milieu
        (rayon_arc * 0.3, 6),  # rangée intérieure
    ]

    index_point = 0
    y_base = centre.y() + taille * 0.12  # ligne de base légèrement sous le centre

    for rayon, nb_points in rangees:
        for i in range(nb_points):
            if index_point >= len(POINTS):
                break

            continent, visite = POINTS[index_point]
            index_point += 1

            # Angle de 180° (gauche) à 0° (droite), réparti uniformément
            angle = math.pi - (i / (nb_points - 1)) * math.pi

            x = centre.x() + math.cos(angle) * rayon
            y = y_base - math.sin(angle) * rayon

            couleur_base = COULEURS_CONTINENTS[continent]

            if visite:
                # Pays visité : couleur pleine et bien saturée
                couleur = QColor(couleur_base)
                couleur.setAlpha(235)
            else:
                # Pays non visité : même teinte mais très éclaircie/transparente
                couleur = QColor(couleur_base)
                couleur.setAlpha(70)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(couleur))
            painter.drawEllipse(QPointF(x, y), rayon_point, rayon_point)
