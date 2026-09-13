################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.44 – Classe de création des cyprès                                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math
import random

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)

# 1 -- Fonctions de dessin d'un cyprès -----------------------------------------


def _melanger(
    couleur_1: QColor,
    couleur_2: QColor,
    poids: float,
) -> QColor:

    poids = max(0.0, min(1.0, poids))

    return QColor(
        round(couleur_1.red() * (1 - poids) + couleur_2.red() * poids),
        round(couleur_1.green() * (1 - poids) + couleur_2.green() * poids),
        round(couleur_1.blue() * (1 - poids) + couleur_2.blue() * poids),
        round(couleur_1.alpha() * (1 - poids) + couleur_2.alpha() * poids),
    )


def _dessiner_tronc(
    painter: QPainter,
    rect: QRectF,
    couleur_tronc: QColor,
) -> None:
    """
    Dessine un tronc fin et légèrement irrégulier.

    Le pied est très légèrement évasé et le haut du tronc
    disparaît progressivement dans le feuillage.
    """

    centre_x = rect.center().x()

    largeur_base = rect.width() * 0.085
    largeur_haut = rect.width() * 0.040

    hauteur = rect.height() * 0.32

    y_bas = rect.bottom() - rect.height() * 0.015
    y_haut = y_bas - hauteur

    # -- Forme générale du tronc ------------------------------------------------

    path = QPainterPath()

    path.moveTo(
        centre_x - largeur_base * 0.65,
        y_bas,
    )

    path.cubicTo(
        centre_x - largeur_base * 0.60,
        y_bas - hauteur * 0.08,
        centre_x - largeur_haut * 0.60,
        y_haut + hauteur * 0.28,
        centre_x - largeur_haut / 2,
        y_haut,
    )

    path.lineTo(
        centre_x + largeur_haut / 2,
        y_haut,
    )

    path.cubicTo(
        centre_x + largeur_haut * 0.55,
        y_haut + hauteur * 0.28,
        centre_x + largeur_base * 0.55,
        y_bas - hauteur * 0.08,
        centre_x + largeur_base * 0.65,
        y_bas,
    )

    path.quadTo(
        centre_x,
        y_bas + rect.height() * 0.008,
        centre_x - largeur_base * 0.65,
        y_bas,
    )

    path.closeSubpath()

    # -- Dégradé du bois --------------------------------------------------------

    sombre = _melanger(
        couleur_tronc,
        QColor("#2C211A"),
        0.38,
    )

    clair = _melanger(
        couleur_tronc,
        QColor("#D1A875"),
        0.18,
    )

    gradient = QLinearGradient(
        centre_x - largeur_base,
        0,
        centre_x + largeur_base,
        0,
    )

    gradient.setColorAt(0.0, sombre)
    gradient.setColorAt(0.30, couleur_tronc)
    gradient.setColorAt(0.58, clair)
    gradient.setColorAt(1.0, sombre)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))

    painter.drawPath(path)

    # -- Lignes d'écorce --------------------------------------------------------

    couleur_ecorce = QColor(sombre)
    couleur_ecorce.setAlpha(65)

    pen = QPen(couleur_ecorce)
    pen.setWidthF(max(0.5, rect.width() * 0.006))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)

    painter.setPen(pen)

    painter.drawLine(
        QPointF(
            centre_x - largeur_base * 0.18,
            y_bas - hauteur * 0.05,
        ),
        QPointF(
            centre_x - largeur_haut * 0.10,
            y_haut + hauteur * 0.38,
        ),
    )

    painter.drawLine(
        QPointF(
            centre_x + largeur_base * 0.22,
            y_bas - hauteur * 0.14,
        ),
        QPointF(
            centre_x + largeur_haut * 0.12,
            y_haut + hauteur * 0.50,
        ),
    )


def _creer_silhouette(
    rect: QRectF,
    rng: random.Random,
) -> QPainterPath:

    centre_x = rect.center().x()

    haut = rect.top() + rect.height() * 0.025
    bas = rect.bottom() - rect.height() * 0.10

    hauteur = bas - haut
    largeur_max = rect.width() * 0.72

    n_points = 15

    gauche = []
    droite = []

    for i in range(n_points + 1):

        t = i / n_points
        y = haut + hauteur * t

        # Profil général :
        # très fin au sommet, s'élargit progressivement puis
        # se resserre très légèrement vers la base.
        profil = math.sin(t * math.pi * 0.72)
        profil *= 0.72 + 0.28 * t

        largeur = largeur_max * profil / 2

        # Petites irrégularités naturelles
        irregularite = rng.uniform(-0.08, 0.08)
        largeur *= 1 + irregularite

        # Le sommet doit rester très fin
        largeur += rect.width() * 0.018 * t

        gauche.append(
            QPointF(
                centre_x - largeur,
                y,
            )
        )

        droite.append(
            QPointF(
                centre_x + largeur,
                y,
            )
        )

    path = QPainterPath()

    path.moveTo(
        QPointF(
            centre_x,
            haut,
        )
    )

    for point in droite[1:]:
        path.lineTo(point)

    for point in reversed(gauche):
        path.lineTo(point)

    path.closeSubpath()

    return path


def _dessiner_masses_feuillage(
    painter: QPainter,
    rect: QRectF,
    silhouette: QPainterPath,
    couleur_feuillage: QColor,
    sombre: QColor,
    clair: QColor,
    rng: random.Random,
) -> None:

    painter.save()

    painter.setClipPath(silhouette)
    painter.setPen(Qt.PenStyle.NoPen)

    n_masses = 45

    for _ in range(n_masses):

        t = rng.uniform(0.10, 0.96)

        y = rect.top() + rect.height() * t

        profil = math.sin(t * math.pi * 0.72)
        profil *= 0.72 + 0.28 * t

        demi_largeur = rect.width() * 0.34 * profil

        x = rect.center().x() + rng.uniform(
            -demi_largeur,
            demi_largeur,
        )

        largeur = rect.width() * rng.uniform(
            0.08,
            0.20,
        )

        hauteur = rect.height() * rng.uniform(
            0.025,
            0.065,
        )

        # La partie gauche reçoit davantage d'ombre,
        # la partie droite davantage de lumière.
        position_x = (x - rect.center().x()) / max(1, rect.width() / 2)

        if position_x < -0.15:
            couleur = sombre

        elif position_x > 0.15:
            couleur = clair

        else:
            couleur = couleur_feuillage

        couleur = QColor(couleur)
        couleur.setAlpha(rng.randint(35, 90))

        painter.setBrush(couleur)

        painter.drawEllipse(
            QRectF(
                x - largeur / 2,
                y - hauteur / 2,
                largeur,
                hauteur,
            )
        )

    painter.restore()


def _dessiner_feuillage(
    painter: QPainter,
    rect: QRectF,
    couleur_feuillage: QColor,
    graine: int,
) -> None:

    # Deux générateurs indépendants permettent de conserver une apparence
    # stable pour la silhouette et les détails du feuillage.
    rng_silhouette = random.Random(graine)
    rng_masses = random.Random(graine + 17)

    silhouette = _creer_silhouette(
        rect=rect,
        rng=rng_silhouette,
    )

    sombre = _melanger(
        couleur_feuillage,
        QColor("#07170D"),
        0.42,
    )

    clair = _melanger(
        couleur_feuillage,
        QColor("#A8C487"),
        0.20,
    )

    # -- Dégradé principal ------------------------------------------------------

    gradient = QLinearGradient(
        rect.left(),
        rect.center().y(),
        rect.right(),
        rect.center().y(),
    )

    gradient.setColorAt(0.0, sombre)
    gradient.setColorAt(0.28, couleur_feuillage)
    gradient.setColorAt(0.58, clair)
    gradient.setColorAt(0.82, couleur_feuillage)
    gradient.setColorAt(1.0, sombre)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))

    painter.drawPath(silhouette)

    # -- Ombre centrale ---------------------------------------------------------

    ombre = QRadialGradient(
        QPointF(
            rect.center().x() - rect.width() * 0.10,
            rect.center().y(),
        ),
        rect.width() * 0.50,
    )

    ombre.setColorAt(
        0.0,
        QColor(
            sombre.red(),
            sombre.green(),
            sombre.blue(),
            0,
        ),
    )

    ombre.setColorAt(
        1.0,
        QColor(
            sombre.red(),
            sombre.green(),
            sombre.blue(),
            100,
        ),
    )

    painter.save()

    painter.setClipPath(silhouette)
    painter.setBrush(QBrush(ombre))
    painter.drawRect(rect)

    painter.restore()

    # -- Petites masses de feuillage -------------------------------------------

    _dessiner_masses_feuillage(
        painter=painter,
        rect=rect,
        silhouette=silhouette,
        couleur_feuillage=couleur_feuillage,
        sombre=sombre,
        clair=clair,
        rng=rng_masses,
    )


def _dessiner_pointe(
    painter: QPainter,
    rect: QRectF,
    couleur_feuillage: QColor,
) -> None:
    """
    Ajoute quelques petites branches à la pointe pour éviter
    une terminaison trop géométrique.
    """

    sommet = QPointF(
        rect.center().x(),
        rect.top() + rect.height() * 0.025,
    )

    couleur = _melanger(
        couleur_feuillage,
        QColor("#101C12"),
        0.25,
    )

    pen = QPen(couleur)
    pen.setWidthF(max(1.0, rect.width() * 0.018))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)

    painter.setPen(pen)

    painter.drawLine(
        sommet,
        QPointF(
            sommet.x() - rect.width() * 0.025,
            sommet.y() + rect.height() * 0.075,
        ),
    )

    painter.drawLine(
        sommet,
        QPointF(
            sommet.x() + rect.width() * 0.020,
            sommet.y() + rect.height() * 0.065,
        ),
    )


def _dessiner_un_cypres(
    painter: QPainter,
    rect: QRectF,
    couleur_feuillage: QColor | str = "#315A3A",
    couleur_tronc: QColor | str = "#6B5140",
    graine: int = 0,
) -> None:
    """Dessine un cyprès complet dans le rectangle fourni."""

    if rect.width() <= 0 or rect.height() <= 0:
        return

    couleur_feuillage = QColor(couleur_feuillage)
    couleur_tronc = QColor(couleur_tronc)

    painter.save()

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing,
    )

    _dessiner_tronc(
        painter=painter,
        rect=rect,
        couleur_tronc=couleur_tronc,
    )

    _dessiner_feuillage(
        painter=painter,
        rect=rect,
        couleur_feuillage=couleur_feuillage,
        graine=graine,
    )

    _dessiner_pointe(
        painter=painter,
        rect=rect,
        couleur_feuillage=couleur_feuillage,
    )

    painter.restore()


# 2 -- Classe de gestion des cyprès --------------------------------------------


class Cypres:
    """
    Gère la génération et le dessin d'un ensemble de cyprès.

    Les positions et dimensions sont exprimées relativement à la scène
    afin de conserver le même décor lors d'un redimensionnement.
    """

    def __init__(
        self,
        n: int = 7,
        proportion_centrale_interdite: float = 1 / 3,
        proportion_sol: float = 0.40,
        hauteur_min: float = 0.25,
        hauteur_max: float = 0.42,
        largeur_min: float = 0.05,
        largeur_max: float = 0.075,
        decalage_sol_min: float = -0.01,
        decalage_sol_max: float = 0.015,
        couleurs_feuillage: list[str] | None = None,
        couleur_tronc: str = "#6B5140",
        graine: int | None = None,
    ) -> None:

        self.n = n

        self.proportion_centrale_interdite = proportion_centrale_interdite
        self.proportion_sol = proportion_sol

        self.hauteur_min = hauteur_min
        self.hauteur_max = hauteur_max

        self.largeur_min = largeur_min
        self.largeur_max = largeur_max

        self.decalage_sol_min = decalage_sol_min
        self.decalage_sol_max = decalage_sol_max

        self.couleurs_feuillage = couleurs_feuillage or [
            "#315A3A",
            "#397245",
            "#39553F",
        ]

        self.couleur_tronc = QColor(couleur_tronc)

        self.graine = graine

        self.arbres = []

        self.generer()

    # 2.1 -- Génération ---------------------------------------------------------

    def generer(self) -> None:
        """Génère la position et les caractéristiques des cyprès."""

        rng = random.Random(self.graine)

        limite_gauche = 0.5 - self.proportion_centrale_interdite / 2

        limite_droite = 0.5 + self.proportion_centrale_interdite / 2

        self.arbres = []

        for _ in range(self.n):

            cote = rng.choice(("gauche", "droite"))

            # Position davantage attirée vers les bords extérieurs
            t = rng.random() ** 1.5

            if cote == "gauche":

                x = t * limite_gauche

            else:

                x = 1.0 - t * (1.0 - limite_droite)

            self.arbres.append(
                {
                    "x": x,
                    "hauteur": rng.uniform(
                        self.hauteur_min,
                        self.hauteur_max,
                    ),
                    "largeur": rng.uniform(
                        self.largeur_min,
                        self.largeur_max,
                    ),
                    "decalage_sol": rng.uniform(
                        self.decalage_sol_min,
                        self.decalage_sol_max,
                    ),
                    "couleur_feuillage": rng.choice(self.couleurs_feuillage),
                    "graine": rng.randint(
                        0,
                        1_000_000,
                    ),
                }
            )

    # 2.2 -- Dessin -------------------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        rect_scene: QRectF,
    ) -> None:
        """Dessine l'ensemble des cyprès dans la scène."""

        y_sol = rect_scene.bottom() - rect_scene.height() * self.proportion_sol

        for arbre in self.arbres:

            largeur = rect_scene.width() * arbre["largeur"]

            hauteur = rect_scene.height() * arbre["hauteur"]

            x_centre = rect_scene.left() + rect_scene.width() * arbre["x"]

            decalage_sol = rect_scene.height() * arbre["decalage_sol"]

            rect_cypres = QRectF(
                x_centre - largeur / 2,
                y_sol - hauteur + decalage_sol,
                largeur,
                hauteur,
            )

            _dessiner_un_cypres(
                painter=painter,
                rect=rect_cypres,
                couleur_feuillage=arbre["couleur_feuillage"],
                couleur_tronc=self.couleur_tronc,
                graine=arbre["graine"],
            )
