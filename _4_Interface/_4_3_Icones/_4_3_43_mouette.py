################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.43 – Script de création d'une mouette                                    #
################################################################################
#
# Mouette vue de profil, plus réaliste mais toujours stylisée :
# - corps plus fuselé ;
# - aile principale mieux dessinée ;
# - aile arrière discrète pour donner du volume ;
# - bec coloré ;
# - extrémités des ailes plus sombres ;
# - paramètre `inverse` pour la retourner horizontalement proprement.
#

# 0 -- Initialisation ----------------------------------------------------------

import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

# 1 -- Fonctions utilitaires ---------------------------------------------------


def _qcolor(couleur: QColor | str | None, defaut: str = "#F3F2ED") -> QColor:
    """Convertit en QColor."""
    if couleur is None:
        return QColor(defaut)
    if isinstance(couleur, QColor):
        return QColor(couleur)
    return QColor(couleur)


def _melanger(
    couleur_1: QColor | str,
    couleur_2: QColor | str,
    t: float,
) -> QColor:
    """
    Mélange linéaire entre deux couleurs.
    t = 0   -> couleur_1
    t = 1   -> couleur_2
    """
    c1 = _qcolor(couleur_1)
    c2 = _qcolor(couleur_2)
    t = max(0.0, min(1.0, t))

    r = round(c1.red() * (1.0 - t) + c2.red() * t)
    g = round(c1.green() * (1.0 - t) + c2.green() * t)
    b = round(c1.blue() * (1.0 - t) + c2.blue() * t)
    a = round(c1.alpha() * (1.0 - t) + c2.alpha() * t)

    return QColor(r, g, b, a)


def _chemin_lisse(
    points: list[tuple[float, float]], fermer: bool = True
) -> QPainterPath:
    """
    Construit un contour lissé passant par une suite de points via une
    conversion Catmull-Rom -> Bézier cubique.
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

        c1 = (
            p1[0] + (p2[0] - p0[0]) / 6.0,
            p1[1] + (p2[1] - p0[1]) / 6.0,
        )
        c2 = (
            p2[0] - (p3[0] - p1[0]) / 6.0,
            p2[1] - (p3[1] - p1[1]) / 6.0,
        )

        chemin.cubicTo(QPointF(*c1), QPointF(*c2), QPointF(*p2))

    if fermer:
        chemin.closeSubpath()

    return chemin


def _plume(
    base: tuple[float, float],
    pointe: tuple[float, float],
    largeur_base: float,
) -> QPainterPath:
    """
    Petit triangle fin et pointu, utile pour des plumes de queue ou
    de bouts d'ailes.
    """
    dx = pointe[0] - base[0]
    dy = pointe[1] - base[1]
    norme = math.hypot(dx, dy) or 1.0

    nx = -dy / norme
    ny = dx / norme
    demi = largeur_base / 2.0

    chemin = QPainterPath()
    chemin.moveTo(QPointF(base[0] + nx * demi, base[1] + ny * demi))
    chemin.lineTo(QPointF(*pointe))
    chemin.lineTo(QPointF(base[0] - nx * demi, base[1] - ny * demi))
    chemin.closeSubpath()

    return chemin


# 2 -- Formes principales ------------------------------------------------------


def _path_corps(t: float) -> QPainterPath:
    """
    Corps fuselé, incluant la tête et la base du bec.
    L'origine locale correspond approximativement à l'épaule / dos.
    """
    pts = [
        (-0.47 * t, -0.035 * t),  # queue haut
        (-0.31 * t, -0.060 * t),
        (-0.10 * t, -0.075 * t),  # dos
        (0.10 * t, -0.095 * t),
        (0.21 * t, -0.108 * t),  # sommet de tête
        (0.30 * t, -0.090 * t),
        (0.37 * t, -0.060 * t),
        (0.40 * t, -0.035 * t),  # base bec haut
        (0.34 * t, -0.020 * t),
        (0.28 * t, 0.005 * t),  # joue
        (0.23 * t, 0.028 * t),
        (0.16 * t, 0.055 * t),  # gorge
        (0.08 * t, 0.085 * t),
        (-0.03 * t, 0.125 * t),  # ventre
        (-0.18 * t, 0.117 * t),
        (-0.31 * t, 0.080 * t),
        (-0.43 * t, 0.030 * t),  # queue bas
    ]
    return _chemin_lisse(pts, fermer=True)


def _path_calotte(t: float) -> QPainterPath:
    """
    Légère zone plus grise sur le dessus du corps / tête.
    """
    pts = [
        (-0.18 * t, -0.040 * t),
        (-0.06 * t, -0.070 * t),
        (0.06 * t, -0.085 * t),
        (0.18 * t, -0.100 * t),
        (0.28 * t, -0.084 * t),
        (0.33 * t, -0.056 * t),
        (0.28 * t, -0.038 * t),
        (0.16 * t, -0.040 * t),
        (0.04 * t, -0.032 * t),
        (-0.10 * t, -0.025 * t),
    ]
    return _chemin_lisse(pts, fermer=True)


def _path_aile_principale(t: float) -> QPainterPath:
    """
    Aile principale, repliée au niveau du poignet, en vol plané.
    """
    pts = [
        (0.00 * t, -0.045 * t),  # racine avant
        (0.07 * t, -0.145 * t),
        (0.14 * t, -0.300 * t),
        (0.16 * t, -0.500 * t),  # poignet
        (0.11 * t, -0.680 * t),
        (0.01 * t, -0.840 * t),
        (-0.14 * t, -0.950 * t),
        (-0.29 * t, -0.985 * t),
        (-0.43 * t, -0.890 * t),  # bout externe
        (-0.36 * t, -0.800 * t),
        (-0.28 * t, -0.760 * t),
        (-0.21 * t, -0.695 * t),
        (-0.15 * t, -0.585 * t),
        (-0.09 * t, -0.445 * t),
        (-0.05 * t, -0.295 * t),
        (-0.035 * t, -0.170 * t),
        (-0.055 * t, -0.075 * t),  # racine arrière
    ]
    return _chemin_lisse(pts, fermer=True)


def _path_aile_arriere(t: float) -> QPainterPath:
    """
    Aile arrière discrète, plus petite, pour éviter un rendu trop plat.
    """
    pts = [
        (-0.03 * t, -0.040 * t),
        (0.03 * t, -0.140 * t),
        (0.08 * t, -0.320 * t),
        (0.09 * t, -0.520 * t),
        (0.04 * t, -0.680 * t),
        (-0.05 * t, -0.790 * t),
        (-0.18 * t, -0.825 * t),
        (-0.29 * t, -0.735 * t),
        (-0.22 * t, -0.645 * t),
        (-0.14 * t, -0.535 * t),
        (-0.08 * t, -0.390 * t),
        (-0.045 * t, -0.220 * t),
        (-0.060 * t, -0.090 * t),
    ]
    return _chemin_lisse(pts, fermer=True)


def _path_patch_aile(t: float) -> QPainterPath:
    """
    Petite zone plus claire au centre de l'aile, pour casser l'à-plat.
    """
    pts = [
        (-0.03 * t, -0.150 * t),
        (0.03 * t, -0.280 * t),
        (0.02 * t, -0.430 * t),
        (-0.08 * t, -0.530 * t),
        (-0.11 * t, -0.365 * t),
        (-0.08 * t, -0.210 * t),
    ]
    return _chemin_lisse(pts, fermer=True)


def _path_bout_aile(t: float) -> QPainterPath:
    """
    Zone sombre du bout d'aile.
    """
    pts = [
        (-0.14 * t, -0.760 * t),
        (-0.26 * t, -0.920 * t),
        (-0.41 * t, -0.905 * t),
        (-0.34 * t, -0.800 * t),
        (-0.22 * t, -0.725 * t),
    ]
    return _chemin_lisse(pts, fermer=True)


def _path_bec(t: float) -> QPainterPath:
    """
    Bec légèrement allongé.
    """
    chemin = QPainterPath()
    chemin.moveTo(QPointF(0.33 * t, -0.020 * t))
    chemin.lineTo(QPointF(0.53 * t, -0.002 * t))
    chemin.lineTo(QPointF(0.40 * t, 0.016 * t))
    chemin.lineTo(QPointF(0.30 * t, 0.004 * t))
    chemin.closeSubpath()
    return chemin


# 3 -- Fonction principale -----------------------------------------------------


def _dessiner_mouette(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    couleur: QColor | str | None = None,
    rotation: float = 0.0,
    phase: float = 0.0,
    amplitude_battement: float = 0.26,
    inverse: bool = False,
    couleur_bec: QColor | str | None = None,
    couleur_bout_aile: QColor | str | None = None,
    couleur_oeil: QColor | str = "#1E2329",
) -> None:
    """
    Dessine une mouette stylisée plus réaliste, vue de profil.

    Paramètres
    ----------
    painter :
        QPainter utilisé pour le dessin.

    centre :
        Point d'ancrage principal (épaule / dos).

    taille :
        Taille générale de la mouette.

    couleur :
        Couleur principale du plumage. Si None, une teinte blanc-gris
        naturelle est utilisée.

    rotation :
        Rotation globale en radians.

    phase :
        Phase du battement d'aile.

    amplitude_battement :
        Amplitude du battement d'aile (en radians).

    inverse :
        Si True, applique une symétrie horizontale : la mouette regarde
        vers la gauche sans être renversée verticalement.

    couleur_bec :
        Couleur du bec. Si None, une teinte ocre / jaune est utilisée.

    couleur_bout_aile :
        Couleur sombre du bout d'aile. Si None, gris anthracite.

    couleur_oeil :
        Couleur de l'œil.
    """

    if taille <= 0:
        return

    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # -------------------------------------------------------------------------
    # Palette
    # -------------------------------------------------------------------------

    base = _qcolor(couleur, "#F3F2ED")
    ventre = _melanger(base, "#FFFFFF", 0.55)
    dos = _melanger(base, "#B7BCC3", 0.55)
    aile = _melanger(base, "#D2D6DB", 0.35)
    aile_ombre = _melanger(aile, "#AEB4BB", 0.35)

    bec = _qcolor(couleur_bec, "#DCAA49")
    pattes = _melanger(bec, "#A4672A", 0.35)
    bout_aile = _qcolor(couleur_bout_aile, "#2F343C")
    oeil = _qcolor(couleur_oeil)

    contour = _melanger(base, "#5E6670", 0.55)
    contour_doux = _melanger(contour, "#FFFFFF", 0.20)

    # -------------------------------------------------------------------------
    # Transformations globales
    # -------------------------------------------------------------------------

    painter.translate(centre)
    painter.rotate(math.degrees(rotation))

    if inverse:
        painter.scale(-1.0, 1.0)

    t = taille

    pen_contour = QPen(contour)
    pen_contour.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen_contour.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen_contour.setWidthF(max(1.0, t * 0.0075))

    pen_fin = QPen(contour_doux)
    pen_fin.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen_fin.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen_fin.setWidthF(max(0.8, t * 0.0045))

    # -------------------------------------------------------------------------
    # Aile arrière (discrète, semi-transparente)
    # -------------------------------------------------------------------------

    painter.save()
    painter.translate(-0.02 * t, -0.01 * t)
    painter.rotate(math.degrees(amplitude_battement * 0.55 * math.sin(phase + 0.35)))
    painter.setOpacity(0.26)

    grad_aile_ar = QLinearGradient(QPointF(0, -1.0 * t), QPointF(0, -0.02 * t))
    grad_aile_ar.setColorAt(0.0, _melanger(aile_ombre, bout_aile, 0.08))
    grad_aile_ar.setColorAt(1.0, _melanger(aile_ombre, base, 0.20))

    painter.setPen(pen_fin)
    painter.setBrush(QBrush(grad_aile_ar))
    painter.drawPath(_path_aile_arriere(t))
    painter.restore()

    # -------------------------------------------------------------------------
    # Queue en éventail
    # -------------------------------------------------------------------------

    pivot_queue = (-0.29 * t, 0.000 * t)
    plumes_queue = [
        ((-0.58 * t, -0.090 * t), 0.040 * t),
        ((-0.65 * t, -0.020 * t), 0.048 * t),
        ((-0.66 * t, 0.050 * t), 0.048 * t),
        ((-0.60 * t, 0.115 * t), 0.040 * t),
    ]

    painter.setPen(pen_fin)
    for i, (pointe, largeur) in enumerate(plumes_queue):
        if i in (1, 2):
            couleur_plume = _melanger(base, dos, 0.18)
        else:
            couleur_plume = _melanger(base, dos, 0.28)

        painter.setBrush(QBrush(couleur_plume))
        painter.drawPath(_plume(pivot_queue, pointe, largeur))

    # -------------------------------------------------------------------------
    # Corps
    # -------------------------------------------------------------------------

    grad_corps = QLinearGradient(QPointF(0, -0.12 * t), QPointF(0, 0.14 * t))
    grad_corps.setColorAt(0.00, dos)
    grad_corps.setColorAt(0.48, base)
    grad_corps.setColorAt(1.00, ventre)

    painter.setPen(pen_contour)
    painter.setBrush(QBrush(grad_corps))
    painter.drawPath(_path_corps(t))

    # Dessus du corps / tête un peu plus gris
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(_melanger(dos, aile, 0.15)))
    painter.drawPath(_path_calotte(t))

    # -------------------------------------------------------------------------
    # Pattes repliées
    # -------------------------------------------------------------------------

    painter.setPen(pen_fin)
    painter.setBrush(QBrush(pattes))
    for pointe, largeur in (
        ((-0.14 * t, 0.165 * t), 0.018 * t),
        ((-0.08 * t, 0.170 * t), 0.018 * t),
    ):
        painter.drawPath(_plume((-0.11 * t, 0.105 * t), pointe, largeur))

    # -------------------------------------------------------------------------
    # Aile principale
    # -------------------------------------------------------------------------

    painter.save()
    painter.rotate(math.degrees(amplitude_battement * math.sin(phase)))

    grad_aile = QLinearGradient(QPointF(0, -1.0 * t), QPointF(0, 0.0))
    grad_aile.setColorAt(0.00, _melanger(aile, dos, 0.20))
    grad_aile.setColorAt(0.70, aile)
    grad_aile.setColorAt(1.00, _melanger(aile, base, 0.25))

    painter.setPen(pen_contour)
    painter.setBrush(QBrush(grad_aile))
    painter.drawPath(_path_aile_principale(t))

    # Zone plus claire au centre de l'aile
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(_melanger(aile, "#FFFFFF", 0.28)))
    painter.drawPath(_path_patch_aile(t))

    # Bout d'aile sombre
    painter.setBrush(QBrush(bout_aile))
    painter.drawPath(_path_bout_aile(t))

    # Primaires sombres bien visibles
    painter.setBrush(QBrush(_melanger(bout_aile, "#1D2127", 0.15)))
    primaires = [
        ((-0.19 * t, -0.760 * t), (-0.29 * t, -0.915 * t), 0.034 * t),
        ((-0.25 * t, -0.785 * t), (-0.39 * t, -0.945 * t), 0.036 * t),
        ((-0.31 * t, -0.790 * t), (-0.47 * t, -0.885 * t), 0.034 * t),
    ]
    for base_plume, pointe_plume, largeur in primaires:
        painter.drawPath(_plume(base_plume, pointe_plume, largeur))

    painter.restore()

    # -------------------------------------------------------------------------
    # Bec
    # -------------------------------------------------------------------------

    grad_bec = QLinearGradient(
        QPointF(0.29 * t, -0.02 * t), QPointF(0.53 * t, 0.02 * t)
    )
    grad_bec.setColorAt(0.00, _melanger(bec, "#FFF3BF", 0.12))
    grad_bec.setColorAt(1.00, _melanger(bec, "#9D6427", 0.22))

    bec_pen = QPen(_melanger(bec, "#7C4D1F", 0.35))
    bec_pen.setWidthF(max(0.8, t * 0.0040))
    bec_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

    painter.setPen(bec_pen)
    painter.setBrush(QBrush(grad_bec))
    painter.drawPath(_path_bec(t))

    # Séparation mandibule
    mandibule_pen = QPen(_melanger(bec, "#7C4D1F", 0.50))
    mandibule_pen.setWidthF(max(0.7, t * 0.0028))
    painter.setPen(mandibule_pen)
    painter.drawLine(
        QPointF(0.34 * t, 0.000 * t),
        QPointF(0.49 * t, 0.005 * t),
    )

    # -------------------------------------------------------------------------
    # Oeil
    # -------------------------------------------------------------------------

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(oeil))
    painter.drawEllipse(QPointF(0.23 * t, -0.045 * t), 0.010 * t, 0.010 * t)

    # Petit reflet dans l'œil
    painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
    painter.drawEllipse(QPointF(0.227 * t, -0.048 * t), 0.0035 * t, 0.0035 * t)

    painter.restore()
