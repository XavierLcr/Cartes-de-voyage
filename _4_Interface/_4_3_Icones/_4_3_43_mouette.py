################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.43 – Script de création d'une mouette                                    #
################################################################################
#
# Silhouette de profil : vol plané, une aile repliée au niveau du "poignet"
# et balayée vers l'arrière, tête et bec tendus vers l'avant, queue étalée
# en éventail. Pose inspirée d'une photo de mouette en vol de profil.
#

# 0 -- Initialisation ----------------------------------------------------------

import math

from PyQt6.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QPointF

# 1 -- Fonctions utilitaires ----------------------------------------------------


def _chemin_lisse(points: list, fermer: bool = True) -> QPainterPath:
    """
    Construit un contour lissé passant par une suite de points, via une
    conversion Catmull-Rom -> Bézier cubique. Beaucoup plus simple à régler
    qu'une suite manuelle de `cubicTo` : il suffit de déplacer les points
    pour changer la silhouette, la courbe reste toujours lisse et continue.

    Si `fermer` vaut True, la courbe boucle sur elle-même (silhouette
    fermée, remplissable). Sinon, elle s'arrête au dernier point.
    """
    n = len(points)
    chemin = QPainterPath()
    chemin.moveTo(QPointF(*points[0]))

    n_segments = n if fermer else n - 1
    for i in range(n_segments):
        p0 = points[(i - 1) % n]
        p1 = points[i % n]
        p2 = points[(i + 1) % n]
        p3 = points[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        chemin.cubicTo(QPointF(*c1), QPointF(*c2), QPointF(*p2))

    if fermer:
        chemin.closeSubpath()
    return chemin


def _plume(base: tuple, pointe: tuple, largeur_base: float) -> QPainterPath:
    """Triangle fin et pointu allant de `base` à `pointe` (une plume)."""
    dx, dy = pointe[0] - base[0], pointe[1] - base[1]
    norme = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / norme, dx / norme  # normale unitaire
    demi = largeur_base / 2.0

    chemin = QPainterPath()
    chemin.moveTo(QPointF(base[0] + nx * demi, base[1] + ny * demi))
    chemin.lineTo(QPointF(*pointe))
    chemin.lineTo(QPointF(base[0] - nx * demi, base[1] - ny * demi))
    chemin.closeSubpath()
    return chemin


def _chemin_aile(pts: list) -> QPainterPath:
    """
    Construit le contour d'une aile repliée à partir de 11 points :
    racine (bord d'attaque) -> poignet -> deux pointes de rémiges primaires
    séparées par une encoche -> poignet (bord de fuite) -> racine (bord de
    fuite). Le bord d'attaque et les bords entre le poignet et les pointes
    sont lissés (quadTo) ; les deux pointes de rémiges restent nettes
    (lineTo), pour un aspect "plume" reconnaissable.
    """
    (
        racine_av,
        ctrl_a,
        poignet_av,
        ctrl_b,
        pointe_1,
        encoche,
        pointe_2,
        ctrl_c,
        poignet_ar,
        ctrl_d,
        racine_ar,
    ) = pts

    chemin = QPainterPath()
    chemin.moveTo(QPointF(*racine_av))
    chemin.quadTo(QPointF(*ctrl_a), QPointF(*poignet_av))
    chemin.quadTo(QPointF(*ctrl_b), QPointF(*pointe_1))
    chemin.lineTo(QPointF(*encoche))
    chemin.lineTo(QPointF(*pointe_2))
    chemin.quadTo(QPointF(*ctrl_c), QPointF(*poignet_ar))
    chemin.quadTo(QPointF(*ctrl_d), QPointF(*racine_ar))
    chemin.closeSubpath()
    return chemin


# 2 -- Fonction de création de la mouette --------------------------------------


def _dessiner_mouette(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    couleur: QColor = None,
    rotation: float = 0.0,
    phase: float = 0.0,
    amplitude_battement: float = 0.9,
) -> None:
    """
    Dessine une mouette stylisée vue de profil, en plein vol plané : une
    aile repliée au niveau du "poignet" et balayée vers l'arrière, avec
    deux pointes de rémiges bien marquées ; un corps fuselé se terminant
    par une tête et un bec tendus vers l'avant ; une queue étalée en
    éventail à l'arrière.

    Paramètres
    ----------
    painter :
        QPainter utilisé pour le dessin.

    centre :
        Point d'ancrage de l'aile sur le dos (épaule), autour duquel tout
        le reste (corps, tête, queue) est positionné.

    taille :
        Longueur totale de la mouette, du bout du bec au bout de la queue.

    couleur :
        Couleur de la silhouette.

    rotation :
        Rotation en radians (utile pour incliner la mouette en vol, par
        exemple lors d'un virage).

    phase :
        Phase utilisée pour animer un léger battement de l'aile. Fait
        pivoter l'aile entière autour de l'épaule, sans en déformer le
        contour (le "poignet" reste plié de la même façon, comme un vrai
        battement où seule l'épaule bouge beaucoup).

    amplitude_battement :
        Amplitude du battement en radians. Mettre à 0 pour une aile figée
        dans sa pose de vol plané.
    """

    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    if couleur is None:
        couleur = QColor("#CBCBCB")

    painter.translate(centre)
    painter.rotate(math.degrees(rotation))

    pen = QPen(couleur)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen.setWidthF(max(1.0, taille * 0.008))
    painter.setPen(pen)
    painter.setBrush(QBrush(couleur))

    t = taille  # raccourci

    # -- Queue : quelques rémiges en éventail, dessinées avant le corps -----
    # Elles dépassent légèrement du corps pour donner un bord d'éventail
    # discrètement dentelé, plus vivant qu'une simple pointe unique.
    pivot_queue = (-0.28 * t, 0.005 * t)
    plumes_queue = [
        ((-0.60 * t, -0.11 * t), 0.05 * t),
        ((-0.66 * t, -0.03 * t), 0.055 * t),
        ((-0.68 * t, 0.05 * t), 0.055 * t),
        ((-0.62 * t, 0.11 * t), 0.05 * t),
    ]
    for pointe, largeur in plumes_queue:
        painter.drawPath(_plume(pivot_queue, pointe, largeur))

    # -- Corps : queue -> dos -> tête -> bec -> gorge -> poitrine -> ventre --
    corps_pts = [
        (-0.50 * t, -0.05 * t),  # 0  pointe de queue (haut)
        (-0.28 * t, -0.06 * t),  # 1  base de la queue (haut)
        (-0.04 * t, -0.085 * t),  # 2  dos / épaule (proche de `centre`)
        (0.14 * t, -0.09 * t),  # 3  nuque
        (0.26 * t, -0.115 * t),  # 4  sommet du crâne
        (0.34 * t, -0.085 * t),  # 5  front
        (0.44 * t, -0.045 * t),  # 6  base du bec (dessus)
        (0.50 * t, -0.010 * t),  # 7  pointe du bec
        (0.42 * t, 0.020 * t),  # 8  base du bec (dessous)
        (0.31 * t, 0.045 * t),  # 9  gorge
        (0.16 * t, 0.090 * t),  # 10 poitrine
        (-0.02 * t, 0.130 * t),  # 11 ventre (point le plus bas)
        (-0.20 * t, 0.115 * t),  # 12 bas-ventre
        (-0.30 * t, 0.075 * t),  # 13 base de la queue (bas)
        (-0.50 * t, 0.020 * t),  # 14 pointe de queue (bas)
    ]
    painter.drawPath(_chemin_lisse(corps_pts, fermer=True))

    # -- Pattes repliées, juste visibles sous le bas-ventre ------------------
    base_pattes = (-0.135 * t, 0.10 * t)
    for pointe, largeur in (
        ((-0.16 * t, 0.165 * t), 0.02 * t),
        ((-0.09 * t, 0.17 * t), 0.02 * t),
    ):
        painter.drawPath(_plume(base_pattes, pointe, largeur))

    # -- Aile : repliée au "poignet", deux pointes de rémiges à l'extrémité --
    # Tous les points sont définis par rapport à l'épaule (origine locale),
    # dans la pose de vol plané. Le battement fait pivoter cette forme figée
    # autour de l'épaule, ce qui suffit à donner un mouvement crédible sans
    # avoir à redéformer le contour à chaque image.
    aile_pts = [
        (0.06 * t, -0.10 * t),  # 0  racine, bord d'attaque
        (0.16 * t, -0.36 * t),  # 1  contrôle : bombé du bord d'attaque
        (0.10 * t, -0.60 * t),  # 2  poignet (bord d'attaque)
        (-0.06 * t, -0.78 * t),  # 3  contrôle : vers la 1re rémige
        (-0.22 * t, -0.90 * t),  # 4  rémige primaire externe (pointe longue)
        (-0.30 * t, -0.83 * t),  # 5  encoche entre les deux pointes
        (-0.36 * t, -0.87 * t),  # 6  rémige primaire suivante (pointe courte)
        (-0.24 * t, -0.66 * t),  # 7  contrôle : bord de fuite, avant-bras
        (-0.10 * t, -0.48 * t),  # 8  poignet (bord de fuite)
        (-0.08 * t, -0.26 * t),  # 9  contrôle : avant l'épaule
        (-0.10 * t, -0.09 * t),  # 10 racine, bord de fuite (aisselle)
    ]

    painter.save()
    battement = amplitude_battement * math.sin(phase)
    painter.rotate(math.degrees(battement))
    painter.drawPath(_chemin_aile(aile_pts))
    painter.restore()

    painter.restore()
