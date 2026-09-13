################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.43 – Script de création d'une mouette                                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QPointF

# 1 -- Fonctions utilitaires : géométrie sur courbe de Bézier quadratique ------


def _point_bezier_quad(p0: tuple, p1: tuple, p2: tuple, t: float) -> tuple:
    """Point sur une courbe de Bézier quadratique B(t)."""
    mt = 1.0 - t
    x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
    y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
    return (x, y)


def _tangente_bezier_quad(p0: tuple, p1: tuple, p2: tuple, t: float) -> tuple:
    """Vecteur tangent (non normalisé) B'(t)."""
    mt = 1.0 - t
    dx = 2 * mt * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
    dy = 2 * mt * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
    return (dx, dy)


def _normale_unitaire(v: tuple) -> tuple:
    """Vecteur perpendiculaire unitaire à `v` (rotation de +90°)."""
    dx, dy = v
    norme = math.hypot(dx, dy) or 1.0
    return (-dy / norme, dx / norme)


def _aile_effilee(
    tip: tuple,
    control: tuple,
    centre_aile: tuple,
    epaisseur_max: float,
    n_echantillons: int,
    inverser: bool,
) -> tuple:
    """
    Construit les bords supérieur et inférieur d'une aile effilée le long
    d'une courbe de Bézier quadratique allant de la pointe (`tip`) au
    creux central (`centre_aile`).

    L'épaisseur est nulle (ou presque) aux deux extrémités et maximale
    vers le milieu de l'aile, ce qui donne une silhouette en forme de
    plume plutôt qu'un simple trait à largeur constante.

    Retourne (bord_haut, bord_bas), deux listes de points allant de la
    pointe vers le centre.
    """
    epaisseur_min = epaisseur_max * 0.10
    bord_haut = []
    bord_bas = []

    for i in range(n_echantillons + 1):
        t = i / n_echantillons
        px, py = _point_bezier_quad(tip, control, centre_aile, t)
        tangente = _tangente_bezier_quad(tip, control, centre_aile, t)
        nx, ny = _normale_unitaire(tangente)

        # Profil d'épaisseur : fin aux extrémités, large au milieu.
        largeur = epaisseur_min + (epaisseur_max - epaisseur_min) * (
            math.sin(math.pi * t) ** 0.8
        )
        demi = largeur / 2.0

        if inverser:
            nx, ny = -nx, -ny

        bord_haut.append((px + nx * demi, py + ny * demi))
        bord_bas.append((px - nx * demi, py - ny * demi))

    return bord_haut, bord_bas


# 2 -- Fonction de création de la mouette --------------------------------------


def _dessiner_mouette(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    couleur: QColor = None,
    rotation: float = 0.0,
    phase: float = 0.0,
    epaisseur_ratio: float = 0.16,
    asymetrie: float = 0.35,
    releve_pointes: float = 0.10,
    effile: bool = True,
    corps: bool = True,
) -> None:
    """
    Dessine une mouette stylisée vue de loin, en silhouette, telle qu'on
    la croise dans les pictogrammes de ciel marin.

    Par rapport à une simple ligne en "M", cette version :
      - effile les ailes (fines aux pointes, plus larges au centre) pour
        une silhouette de type "plume" plutôt qu'un trait uniforme ;
      - relève légèrement les pointes des ailes (petit crochet), signature
        visuelle des mouettes stylisées ;
      - désynchronise légèrement le battement des deux ailes pour éviter
        un mouvement trop mécanique ;
      - ajoute, en option, un petit corps/tête pour ancrer la silhouette.

    Paramètres
    ----------
    painter :
        QPainter utilisé pour le dessin.

    centre :
        Position du centre de la mouette (creux entre les deux ailes).

    taille :
        Envergure globale de la mouette.

    couleur :
        Couleur de la silhouette.

    rotation :
        Rotation en radians (utile pour une légère inclinaison en vol).

    phase :
        Phase utilisée pour animer le battement des ailes.

    epaisseur_ratio :
        Épaisseur maximale du trait/de l'aile, relative à `taille`.

    asymetrie :
        Déphasage (en radians) entre le battement de l'aile gauche et
        celui de l'aile droite ; 0 = battement parfaitement symétrique.

    releve_pointes :
        Hauteur du léger crochet aux extrémités des ailes, relative à
        `taille`. Mettre à 0 pour des pointes plates.

    effile :
        Si True, dessine les ailes comme une forme remplie et effilée.
        Si False, revient à un simple trait d'épaisseur constante
        (rendu moins coûteux, utile pour de très petites icônes).

    corps :
        Si True, ajoute un petit corps/tête au centre de la mouette.
    """

    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    if couleur is None:
        couleur = QColor("#FFFFFF")

    painter.translate(centre)
    painter.rotate(math.degrees(rotation))

    # -- Battement (avec léger déphasage gauche/droite) --------------------
    # `battement` oscille entre 0 (ailes basses, presque à plat) et 1
    # (ailes hautes, à la verticale du corps) : c'est ce qui donne
    # l'impression de vol plutôt qu'une forme figée. Le déphasage entre
    # les deux ailes évite un battement trop symétrique et mécanique.
    battement_g = 0.5 + 0.5 * math.sin(phase)
    battement_d = 0.5 + 0.5 * math.sin(phase + asymetrie)

    envergure = taille * 0.5
    hauteur_aile_g = taille * (0.18 + 0.34 * battement_g)
    hauteur_aile_d = taille * (0.18 + 0.34 * battement_d)
    creux_centre = taille * (0.06 + 0.12 * min(battement_g, battement_d))
    hook = taille * releve_pointes

    # -- Points de contrôle des deux ailes -----------------------------------
    # Pointe légèrement relevée (hook), point de contrôle qui donne la
    # courbure de l'aile, et point central partagé (le creux).
    tip_g = (-envergure, -hook)
    ctrl_g = (-envergure * 0.45, -hauteur_aile_g)
    tip_d = (envergure, -hook)
    ctrl_d = (envergure * 0.45, -hauteur_aile_d)
    centre_aile = (0.0, -creux_centre)

    epaisseur_max = max(1.5, taille * epaisseur_ratio)

    pen = QPen(couleur)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

    if effile:
        # -- Silhouette remplie, effilée aux pointes -------------------------
        n = 20
        haut_g, bas_g = _aile_effilee(
            tip_g, ctrl_g, centre_aile, epaisseur_max, n, inverser=False
        )
        haut_d, bas_d = _aile_effilee(
            tip_d, ctrl_d, centre_aile, epaisseur_max, n, inverser=True
        )

        mouette = QPainterPath()
        mouette.moveTo(QPointF(*haut_g[0]))
        for pt in haut_g[1:]:
            mouette.lineTo(QPointF(*pt))
        for pt in reversed(haut_d):
            mouette.lineTo(QPointF(*pt))
        for pt in bas_d:
            mouette.lineTo(QPointF(*pt))
        for pt in reversed(bas_g):
            mouette.lineTo(QPointF(*pt))
        mouette.closeSubpath()

        pen.setWidthF(max(1.0, taille * 0.01))
        painter.setPen(pen)
        painter.setBrush(QBrush(couleur))
        painter.drawPath(mouette)
    else:
        # -- Repli : simple trait d'épaisseur constante ----------------------
        mouette = QPainterPath()
        mouette.moveTo(QPointF(*tip_g))
        mouette.quadTo(QPointF(*ctrl_g), QPointF(*centre_aile))
        mouette.quadTo(QPointF(*ctrl_d), QPointF(*tip_d))

        pen.setWidthF(epaisseur_max)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(mouette)

    # -- Corps / tête optionnel ----------------------------------------------
    if corps:
        rayon_corps = taille * 0.045
        centre_corps = QPointF(0, -creux_centre - rayon_corps * 0.6)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(couleur))
        painter.drawEllipse(centre_corps, rayon_corps, rayon_corps * 0.85)

    painter.restore()
