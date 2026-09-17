################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.58 – Classe de création d'un paysage maritime animé                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations

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

# 1 -- Fonctions utilitaires ---------------------------------------------------


def _qcolor(couleur: QColor | str) -> QColor:
    """Retourne un QColor."""
    return couleur if isinstance(couleur, QColor) else QColor(couleur)


def _avec_alpha(
    couleur: QColor | str,
    alpha: int,
) -> QColor:
    """Retourne une copie de la couleur avec l'alpha demandé."""
    c = QColor(_qcolor(couleur))
    c.setAlpha(max(0, min(255, alpha)))
    return c


def _melanger(
    couleur_1: QColor | str,
    couleur_2: QColor | str,
    proportion: float,
) -> QColor:
    """Interpole deux couleurs en RGB."""
    c1 = _qcolor(couleur_1)
    c2 = _qcolor(couleur_2)
    p = max(0.0, min(1.0, proportion))

    return QColor(
        round(c1.red() * (1 - p) + c2.red() * p),
        round(c1.green() * (1 - p) + c2.green() * p),
        round(c1.blue() * (1 - p) + c2.blue() * p),
        round(c1.alpha() * (1 - p) + c2.alpha() * p),
    )


def _eclaircir(
    couleur: QColor | str,
    proportion: float = 0.20,
) -> QColor:
    """Éclaircit une couleur."""
    return _melanger(couleur, "#FFFFFF", proportion)


def _assombrir(
    couleur: QColor | str,
    proportion: float = 0.20,
) -> QColor:
    """Assombrit une couleur."""
    return _melanger(couleur, "#000000", proportion)


# 2 -- Paysage maritime --------------------------------------------------------


class PaysageMaritime:
    """
    Paysage maritime lumineux avec défilement lent en parallaxe.

    Le décor contient :
        - un ciel lumineux ;
        - des nuages qui dérivent très lentement ;
        - une mer animée par plusieurs nappes d'ondes ;
        - des caps / îlots lointains ;
        - une plage avec écume mobile ;
        - éventuellement un ponton et un phare ;
        - quelques mouettes ;
        - des oyats au premier plan.

    Le paramètre ``distance`` est volontairement utilisé avec des vitesses
    faibles : le paysage évolue doucement derrière le train, comme les autres
    décors de l'application, sans donner l'impression que la mer elle-même
    file à grande vitesse.
    """

    masque_paysage = False
    masque_rails = False

    def __init__(
        self,
        graine: int = 58,
        couleur_ciel_haut: QColor | str = "#8FC6F2",
        couleur_ciel_bas: QColor | str = "#EAF7FF",
        couleur_mer_haut: QColor | str = "#5EAFD0",
        couleur_mer_bas: QColor | str = "#2F7699",
        couleur_plage: QColor | str = "#E9D4A8",
        couleur_ecume: QColor | str = "#F8FCFF",
        couleur_falaise: QColor | str = "#B89E7C",
        couleur_promenade: QColor | str = "#9B8C7E",
        couleur_bois_ponton: QColor | str = "#7B5E49",
        couleur_phare: QColor | str = "#F7F1E7",
        couleur_toit_phare: QColor | str = "#C94E43",
        couleur_vegetation: QColor | str = "#80995C",
        coucher_soleil: bool = False,
        avec_ponton: bool = True,
        avec_phare: bool = True,
        avec_mouettes: bool = True,
        n_nuages: int = 5,
        n_mouettes: int = 6,
        n_oyats: int = 14,
    ):
        self.graine = int(graine)

        self.couleur_ciel_haut = _qcolor(couleur_ciel_haut)
        self.couleur_ciel_bas = _qcolor(couleur_ciel_bas)
        self.couleur_mer_haut = _qcolor(couleur_mer_haut)
        self.couleur_mer_bas = _qcolor(couleur_mer_bas)
        self.couleur_plage = _qcolor(couleur_plage)
        self.couleur_ecume = _qcolor(couleur_ecume)
        self.couleur_falaise = _qcolor(couleur_falaise)
        self.couleur_promenade = _qcolor(couleur_promenade)
        self.couleur_bois_ponton = _qcolor(couleur_bois_ponton)
        self.couleur_phare = _qcolor(couleur_phare)
        self.couleur_toit_phare = _qcolor(couleur_toit_phare)
        self.couleur_vegetation = _qcolor(couleur_vegetation)

        self.coucher_soleil = coucher_soleil
        self.avec_ponton = avec_ponton
        self.avec_phare = avec_phare
        self.avec_mouettes = avec_mouettes

        self.n_nuages = max(0, int(n_nuages))
        self.n_mouettes = max(0, int(n_mouettes))
        self.n_oyats = max(0, int(n_oyats))

        # ------------------------------------------------------------------
        # Géométrie pré-générée
        # ------------------------------------------------------------------

        self.nuages = self._generer_nuages()
        self.mouettes = self._generer_mouettes()
        self.oyats = self._generer_oyats()
        self.vagues = self._generer_vagues()
        self.caps = self._generer_caps()

        # Position normalisée des éléments singuliers. Ils défilent très
        # lentement avec la côte mais restent déterministes avec la graine.
        rng = random.Random(self.graine + 9201)
        self.x_phare = rng.uniform(0.10, 0.22)
        self.x_ponton = rng.uniform(0.56, 0.72)

    # --------------------------------------------------------------------------
    # Génération déterministe
    # --------------------------------------------------------------------------

    def _generer_nuages(self) -> list[dict]:
        """Pré-génère des nuages avec plusieurs vitesses de dérive."""
        rng = random.Random(self.graine + 1001)
        nuages = []

        for _ in range(self.n_nuages):
            nuages.append(
                {
                    "x": rng.random(),
                    "y": rng.uniform(0.08, 0.28),
                    "taille": rng.uniform(0.55, 1.20),
                    "vitesse": rng.uniform(0.012, 0.032),
                    "alpha": rng.randint(150, 215),
                }
            )

        nuages.sort(key=lambda n: n["taille"])
        return nuages

    def _generer_mouettes(self) -> list[dict]:
        """Pré-génère les mouettes du ciel."""
        rng = random.Random(self.graine + 2203)
        mouettes = []

        for _ in range(self.n_mouettes):
            mouettes.append(
                {
                    "x": rng.random(),
                    "y": rng.uniform(0.13, 0.34),
                    "taille": rng.uniform(0.65, 1.15),
                    "vitesse": rng.uniform(0.045, 0.095),
                    "phase": rng.uniform(0.0, math.tau),
                    "alpha": rng.randint(130, 205),
                }
            )

        return mouettes

    def _generer_oyats(self) -> list[dict]:
        """Pré-génère les touffes d'oyats du premier plan."""
        rng = random.Random(self.graine + 3407)
        oyats = []

        for _ in range(self.n_oyats):
            oyats.append(
                {
                    "x": rng.random(),
                    "taille": rng.uniform(0.65, 1.20),
                    "vitesse": rng.uniform(0.26, 0.38),
                    "inclinaison": rng.uniform(-0.10, 0.10),
                }
            )

        return oyats

    def _generer_vagues(self) -> list[dict]:
        """Pré-génère les différentes nappes d'ondes."""
        rng = random.Random(self.graine + 4811)
        vagues = []

        for i, p in enumerate((0.08, 0.20, 0.34, 0.50, 0.67, 0.84)):
            vagues.append(
                {
                    "p": p + rng.uniform(-0.018, 0.018),
                    "amplitude": rng.uniform(0.0045, 0.0115),
                    "periode": rng.uniform(0.10, 0.20),
                    "vitesse": 0.035 + i * 0.010 + rng.uniform(-0.005, 0.005),
                    "alpha": rng.randint(58, 105),
                    "phase": rng.uniform(0.0, 1.0),
                }
            )

        return vagues

    def _generer_caps(self) -> list[dict]:
        """Pré-génère quelques reliefs côtiers lointains."""
        rng = random.Random(self.graine + 6007)
        caps = []

        for couche in range(2):
            for _ in range(3):
                caps.append(
                    {
                        "x": rng.random(),
                        "largeur": rng.uniform(0.18, 0.34),
                        "hauteur": rng.uniform(0.035, 0.090),
                        "couche": couche,
                        "vitesse": 0.018 if couche == 0 else 0.034,
                    }
                )

        return caps

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    def largeur_recommandee(
        self,
        hauteur_scene: float,
    ) -> float:
        """Largeur idéale approximative."""
        return hauteur_scene * 3.20

    def _y_horizon(
        self,
        rect_scene: QRectF,
    ) -> float:
        """Niveau de l'horizon marin."""
        proportion = 0.47 if self.coucher_soleil else 0.43
        return rect_scene.top() + rect_scene.height() * proportion

    def _y_plage(
        self,
        rect_scene: QRectF,
        y_rail: float,
    ) -> float:
        """Altitude moyenne du premier plan sableux."""
        return min(
            rect_scene.bottom(),
            y_rail - rect_scene.height() * 0.025,
        )

    @staticmethod
    def _x_boucle(
        rect_scene: QRectF,
        x_ratio: float,
        distance: float,
        vitesse: float,
        marge: float,
    ) -> float:
        """Position horizontale avec répétition continue hors écran."""
        largeur = rect_scene.width()
        periode = largeur + 2 * marge
        x_base = rect_scene.left() + x_ratio * largeur

        return (
            rect_scene.left()
            + ((x_base - rect_scene.left() - distance * vitesse + marge) % periode)
            - marge
        )

    # --------------------------------------------------------------------------
    # Ciel
    # --------------------------------------------------------------------------

    def _dessiner_ciel(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
    ) -> None:
        """Dessine le ciel principal."""
        rect_ciel = QRectF(
            rect_scene.left(),
            rect_scene.top(),
            rect_scene.width(),
            y_horizon - rect_scene.top(),
        )

        if self.coucher_soleil:
            couleurs = (
                QColor("#EEA56F"),
                QColor("#F6CEA2"),
                QColor("#FFF2D8"),
            )
        else:
            couleurs = (
                self.couleur_ciel_haut,
                _melanger(self.couleur_ciel_haut, self.couleur_ciel_bas, 0.45),
                self.couleur_ciel_bas,
            )

        gradient = QLinearGradient(rect_ciel.topLeft(), rect_ciel.bottomLeft())
        gradient.setColorAt(0.0, couleurs[0])
        gradient.setColorAt(0.55, couleurs[1])
        gradient.setColorAt(1.0, couleurs[2])

        painter.fillRect(rect_ciel, QBrush(gradient))

    def _dessiner_soleil(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
    ) -> None:
        """Dessine un soleil presque fixe et son reflet."""
        h = rect_scene.height()

        centre = QPointF(
            rect_scene.left()
            + rect_scene.width() * (0.74 if self.coucher_soleil else 0.72),
            rect_scene.top() + h * (0.20 if self.coucher_soleil else 0.18),
        )
        rayon = h * (0.085 if self.coucher_soleil else 0.070)

        halo = QRadialGradient(centre, rayon * 2.8)
        halo.setColorAt(0.0, QColor(255, 245, 198, 135))
        halo.setColorAt(0.45, QColor(255, 235, 180, 48))
        halo.setColorAt(1.0, QColor(255, 235, 180, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(halo))
        painter.drawEllipse(centre, rayon * 2.8, rayon * 2.8)

        grad = QRadialGradient(
            QPointF(centre.x() - rayon * 0.15, centre.y() - rayon * 0.18),
            rayon,
        )
        grad.setColorAt(0.0, QColor("#FFFBEA"))
        grad.setColorAt(0.65, QColor("#FFE8A0"))
        grad.setColorAt(1.0, QColor("#F7CF77"))

        painter.setBrush(QBrush(grad))
        painter.drawEllipse(centre, rayon, rayon)

        # Reflet volontairement très doux : c'est la surface de l'eau qui
        # l'anime ensuite, pas le soleil lui-même.
        rect_reflet = QRectF(
            centre.x() - rayon * 0.35,
            y_horizon,
            rayon * 0.70,
            rect_scene.bottom() - y_horizon,
        )
        grad_reflet = QLinearGradient(rect_reflet.topLeft(), rect_reflet.bottomLeft())
        grad_reflet.setColorAt(0.0, QColor(255, 243, 205, 68))
        grad_reflet.setColorAt(1.0, QColor(255, 243, 205, 0))
        painter.setBrush(QBrush(grad_reflet))
        painter.drawRoundedRect(rect_reflet, rayon * 0.30, rayon * 0.30)

    def _dessiner_un_nuage(
        self,
        painter: QPainter,
        centre: QPointF,
        rayon: float,
        alpha: int,
    ) -> None:
        """Dessine un nuage doux à partir d'un centre."""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha("#FFFFFF", max(20, alpha // 4)))
        painter.drawEllipse(
            QPointF(centre.x() + rayon * 0.10, centre.y() + rayon * 0.12),
            rayon * 1.18,
            rayon * 0.62,
        )

        grad = QRadialGradient(
            QPointF(centre.x() - rayon * 0.08, centre.y() - rayon * 0.12),
            rayon * 1.10,
        )
        grad.setColorAt(0.0, _avec_alpha("#FFFFFF", alpha))
        grad.setColorAt(1.0, _avec_alpha("#FFFFFF", 0))
        painter.setBrush(QBrush(grad))

        for dx, dy, facteur in (
            (-0.62, 0.10, 0.52),
            (-0.18, -0.10, 0.65),
            (0.32, -0.02, 0.60),
            (0.66, 0.12, 0.48),
        ):
            painter.drawEllipse(
                QPointF(centre.x() + dx * rayon, centre.y() + dy * rayon),
                rayon * facteur,
                rayon * facteur * 0.72,
            )

    def _dessiner_nuages(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        distance: float,
    ) -> None:
        """Dessine les nuages avec une dérive très lente."""
        h = rect_scene.height()
        marge = h * 0.35

        for nuage in self.nuages:
            x = self._x_boucle(
                rect_scene,
                nuage["x"],
                distance,
                nuage["vitesse"],
                marge,
            )
            y = rect_scene.top() + rect_scene.height() * nuage["y"]
            rayon = h * 0.115 * nuage["taille"]

            self._dessiner_un_nuage(
                painter,
                QPointF(x, y),
                rayon,
                nuage["alpha"],
            )

    # --------------------------------------------------------------------------
    # Relief côtier lointain
    # --------------------------------------------------------------------------

    def _dessiner_un_cap(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
        cap: dict,
        distance: float,
    ) -> None:
        """Dessine un cap lointain avec parallaxe très faible."""
        w = rect_scene.width()
        h = rect_scene.height()
        marge = w * 0.20

        x_centre = self._x_boucle(
            rect_scene,
            cap["x"],
            distance,
            cap["vitesse"],
            marge,
        )
        largeur = w * cap["largeur"]
        hauteur = h * cap["hauteur"]

        path = QPainterPath()
        path.moveTo(x_centre - largeur / 2, y_horizon + h * 0.085)
        path.cubicTo(
            QPointF(x_centre - largeur * 0.30, y_horizon + hauteur * 0.15),
            QPointF(x_centre - largeur * 0.12, y_horizon - hauteur),
            QPointF(x_centre + largeur * 0.02, y_horizon - hauteur * 0.70),
        )
        path.cubicTo(
            QPointF(x_centre + largeur * 0.18, y_horizon - hauteur * 0.55),
            QPointF(x_centre + largeur * 0.34, y_horizon + hauteur * 0.35),
            QPointF(x_centre + largeur / 2, y_horizon + h * 0.085),
        )
        path.closeSubpath()

        profondeur = cap["couche"]
        couleur = _melanger(
            _eclaircir(self.couleur_falaise, 0.15),
            _assombrir(self.couleur_falaise, 0.10),
            0.65 * profondeur,
        )
        couleur.setAlpha(210 if profondeur == 0 else 245)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(couleur)
        painter.drawPath(path)

        # Ligne végétale irrégulière.
        painter.setBrush(_avec_alpha(_assombrir(self.couleur_vegetation, 0.08), 170))
        painter.drawRoundedRect(
            QRectF(
                x_centre - largeur * 0.16,
                y_horizon - hauteur * 0.72,
                largeur * 0.30,
                max(1.5, h * 0.010),
            ),
            h * 0.003,
            h * 0.003,
        )

    def _dessiner_caps(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
        distance: float,
    ) -> None:
        """Dessine les reliefs côtiers lointains."""
        for cap in sorted(self.caps, key=lambda c: c["couche"]):
            self._dessiner_un_cap(
                painter,
                rect_scene,
                y_horizon,
                cap,
                distance,
            )

    # --------------------------------------------------------------------------
    # Mer
    # --------------------------------------------------------------------------

    def _dessiner_mer(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
        y_plage: float,
        distance: float,
    ) -> None:
        """Dessine la mer et ses rides en déplacement lent."""
        rect_mer = QRectF(
            rect_scene.left(),
            y_horizon,
            rect_scene.width(),
            max(0.0, y_plage - y_horizon + rect_scene.height() * 0.04),
        )

        grad = QLinearGradient(rect_mer.topLeft(), rect_mer.bottomLeft())

        if self.coucher_soleil:
            grad.setColorAt(0.0, QColor("#76B9CB"))
            grad.setColorAt(0.45, QColor("#4E94B0"))
            grad.setColorAt(1.0, QColor("#2E6786"))
        else:
            grad.setColorAt(0.0, self.couleur_mer_haut)
            grad.setColorAt(
                0.45, _melanger(self.couleur_mer_haut, self.couleur_mer_bas, 0.38)
            )
            grad.setColorAt(1.0, self.couleur_mer_bas)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(rect_mer)

        # Chaque nappe possède sa propre période et vitesse. Les vagues sont
        # répétées hors écran afin que le mouvement reste parfaitement continu.
        for vague in self.vagues:
            y_base = rect_mer.top() + rect_mer.height() * vague["p"]
            periode = max(20.0, rect_scene.width() * vague["periode"])
            amplitude = rect_scene.height() * vague["amplitude"]
            decalage = (
                -(distance * vague["vitesse"] + vague["phase"] * periode) % periode
            )

            # Très légère respiration verticale de la surface.
            y = (
                y_base
                + math.sin(distance * 0.012 + vague["phase"] * math.tau)
                * amplitude
                * 0.22
            )

            pen = QPen(_avec_alpha(self.couleur_ecume, vague["alpha"]))
            pen.setWidthF(max(1.0, rect_scene.height() * 0.0032))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            x = rect_scene.left() - periode + decalage
            while x <= rect_scene.right() + periode:
                path = QPainterPath()
                path.moveTo(x, y)
                path.cubicTo(
                    QPointF(x + periode * 0.24, y - amplitude),
                    QPointF(x + periode * 0.66, y + amplitude * 0.80),
                    QPointF(x + periode, y),
                )
                painter.drawPath(path)
                x += periode

    # --------------------------------------------------------------------------
    # Littoral et premier plan
    # --------------------------------------------------------------------------

    def _chemin_littoral(
        self,
        rect_scene: QRectF,
        y_plage: float,
        distance: float,
    ) -> QPainterPath:
        """Construit une ligne de côte ondulée évoluant lentement."""
        w = rect_scene.width()
        h = rect_scene.height()
        amplitude = h * 0.028
        periode = w * 0.34
        decalage = -(distance * 0.085) % periode

        path = QPainterPath()
        path.moveTo(rect_scene.left(), rect_scene.bottom())

        x = rect_scene.left() - periode + decalage
        y_base = y_plage - h * 0.055
        path.lineTo(x, y_base)

        while x <= rect_scene.right() + periode:
            path.cubicTo(
                QPointF(x + periode * 0.25, y_base - amplitude),
                QPointF(x + periode * 0.45, y_base + amplitude * 0.35),
                QPointF(x + periode * 0.50, y_base),
            )
            path.cubicTo(
                QPointF(x + periode * 0.72, y_base + amplitude * 0.25),
                QPointF(x + periode * 0.90, y_base - amplitude * 0.55),
                QPointF(x + periode, y_base),
            )
            x += periode

        path.lineTo(rect_scene.right(), rect_scene.bottom())
        path.closeSubpath()
        return path

    def _dessiner_plage(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_plage: float,
        distance: float,
    ) -> None:
        """Dessine la plage et la frange d'écume mobile."""
        h = rect_scene.height()
        chemin = self._chemin_littoral(rect_scene, y_plage, distance)

        grad = QLinearGradient(
            QPointF(rect_scene.left(), y_plage - h * 0.09),
            QPointF(rect_scene.left(), rect_scene.bottom()),
        )
        grad.setColorAt(0.0, _eclaircir(self.couleur_plage, 0.08))
        grad.setColorAt(1.0, _assombrir(self.couleur_plage, 0.08))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawPath(chemin)

        # Ligne d'écume : même géométrie que le rivage, mais simplement tracée.
        w = rect_scene.width()
        amplitude = h * 0.028
        periode = w * 0.34
        decalage = -(distance * 0.085) % periode
        y_base = y_plage - h * 0.055

        pen = QPen(_avec_alpha(self.couleur_ecume, 165))
        pen.setWidthF(max(1.0, h * 0.0048))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        path = QPainterPath()
        x = rect_scene.left() - periode + decalage
        path.moveTo(x, y_base)

        while x <= rect_scene.right() + periode:
            path.cubicTo(
                QPointF(x + periode * 0.25, y_base - amplitude),
                QPointF(x + periode * 0.45, y_base + amplitude * 0.35),
                QPointF(x + periode * 0.50, y_base),
            )
            path.cubicTo(
                QPointF(x + periode * 0.72, y_base + amplitude * 0.25),
                QPointF(x + periode * 0.90, y_base - amplitude * 0.55),
                QPointF(x + periode, y_base),
            )
            x += periode

        painter.drawPath(path)

    def _dessiner_promenade(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_plage: float,
        distance: float,
    ) -> None:
        """Dessine une promenade dont les potelets défilent doucement."""
        h = rect_scene.height()
        w = rect_scene.width()

        y = y_plage - h * 0.012
        rect_prom = QRectF(
            rect_scene.left(),
            y,
            rect_scene.width(),
            h * 0.018,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha(self.couleur_promenade, 185))
        painter.drawRect(rect_prom)

        # Rambarde : la lisse reste stable, les montants créent le mouvement.
        y_lisse = y - h * 0.022
        pen = QPen(_avec_alpha(_assombrir(self.couleur_promenade, 0.18), 175))
        pen.setWidthF(max(1.0, h * 0.0030))
        painter.setPen(pen)
        painter.drawLine(
            QPointF(rect_scene.left(), y_lisse),
            QPointF(rect_scene.right(), y_lisse),
        )

        pas = max(20.0, w * 0.055)
        decalage = -(distance * 0.18) % pas
        x = rect_scene.left() - pas + decalage

        while x <= rect_scene.right() + pas:
            painter.drawLine(QPointF(x, y), QPointF(x, y_lisse))
            x += pas

    def _dessiner_ponton(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
        distance: float,
    ) -> None:
        """Dessine un petit ponton avançant lentement avec le littoral."""
        if not self.avec_ponton:
            return

        h = rect_scene.height()
        w = rect_scene.width()
        marge = w * 0.22

        x_debut = self._x_boucle(
            rect_scene,
            self.x_ponton,
            distance,
            0.12,
            marge,
        )
        y_ponton = y_horizon + h * 0.16
        longueur = w * 0.19
        epaisseur = h * 0.015

        rect_ponton = QRectF(x_debut, y_ponton, longueur, epaisseur)

        grad = QLinearGradient(rect_ponton.topLeft(), rect_ponton.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_bois_ponton, 0.08))
        grad.setColorAt(1.0, _assombrir(self.couleur_bois_ponton, 0.12))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(
            rect_ponton,
            epaisseur * 0.25,
            epaisseur * 0.25,
        )

        painter.setBrush(_assombrir(self.couleur_bois_ponton, 0.16))
        for p in (0.08, 0.32, 0.56, 0.80, 0.96):
            x = x_debut + longueur * p
            painter.drawRoundedRect(
                QRectF(
                    x - h * 0.005,
                    y_ponton + epaisseur * 0.20,
                    h * 0.010,
                    h * 0.070,
                ),
                h * 0.003,
                h * 0.003,
            )

        # Petit kiosque terminal.
        rect_abri = QRectF(
            x_debut + longueur * 0.82,
            y_ponton - h * 0.042,
            w * 0.044,
            h * 0.042,
        )
        painter.setBrush(_assombrir(self.couleur_bois_ponton, 0.02))
        painter.drawRoundedRect(rect_abri, h * 0.006, h * 0.006)

        path_toit = QPainterPath()
        path_toit.moveTo(rect_abri.left() - w * 0.004, rect_abri.top() + h * 0.010)
        path_toit.lineTo(rect_abri.center().x(), rect_abri.top() - h * 0.010)
        path_toit.lineTo(rect_abri.right() + w * 0.004, rect_abri.top() + h * 0.010)
        path_toit.lineTo(rect_abri.right(), rect_abri.top() + h * 0.020)
        path_toit.lineTo(rect_abri.left(), rect_abri.top() + h * 0.020)
        path_toit.closeSubpath()
        painter.setBrush(_assombrir(self.couleur_bois_ponton, 0.20))
        painter.drawPath(path_toit)

    def _dessiner_phare(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
        distance: float,
    ) -> None:
        """Dessine un phare lointain se déplaçant à peine."""
        if not self.avec_phare:
            return

        h = rect_scene.height()
        w = rect_scene.width()
        marge = w * 0.18

        x = self._x_boucle(
            rect_scene,
            self.x_phare,
            distance,
            0.028,
            marge,
        )
        y_base = y_horizon - h * 0.005
        hauteur = h * 0.11
        largeur = h * 0.040

        path = QPainterPath()
        path.moveTo(x - largeur * 0.55, y_base)
        path.lineTo(x - largeur * 0.36, y_base - hauteur)
        path.lineTo(x + largeur * 0.36, y_base - hauteur)
        path.lineTo(x + largeur * 0.55, y_base)
        path.closeSubpath()

        grad = QLinearGradient(QPointF(x, y_base - hauteur), QPointF(x, y_base))
        grad.setColorAt(0.0, _eclaircir(self.couleur_phare, 0.06))
        grad.setColorAt(1.0, _assombrir(self.couleur_phare, 0.05))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawPath(path)

        painter.setBrush(self.couleur_toit_phare)
        painter.drawRect(
            QRectF(
                x - largeur * 0.38,
                y_base - hauteur * 0.52,
                largeur * 0.76,
                hauteur * 0.16,
            )
        )

        rect_lanterne = QRectF(
            x - largeur * 0.30,
            y_base - hauteur - h * 0.018,
            largeur * 0.60,
            h * 0.024,
        )
        painter.setBrush(_assombrir(self.couleur_toit_phare, 0.10))
        painter.drawRoundedRect(rect_lanterne, h * 0.004, h * 0.004)

        painter.setBrush(QColor("#FFF3B9"))
        painter.drawRoundedRect(
            rect_lanterne.adjusted(
                largeur * 0.08,
                h * 0.003,
                -largeur * 0.08,
                -h * 0.003,
            ),
            h * 0.003,
            h * 0.003,
        )

    def _dessiner_oyats(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_plage: float,
        distance: float,
    ) -> None:
        """Dessine les oyats avec un parallaxe de premier plan."""
        h = rect_scene.height()
        marge = h * 0.16

        pen = QPen(_assombrir(self.couleur_vegetation, 0.10))
        pen.setWidthF(max(1.0, h * 0.003))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        for touffe in self.oyats:
            x0 = self._x_boucle(
                rect_scene,
                touffe["x"],
                distance,
                touffe["vitesse"],
                marge,
            )
            y0 = y_plage + h * 0.03
            longueur = h * 0.105 * touffe["taille"]
            inclinaison = touffe["inclinaison"]

            for angle_deg in (-35, -20, -8, 10, 24, 36):
                angle = math.radians(angle_deg) + inclinaison
                x1 = x0 + math.sin(angle) * longueur * 0.42
                y1 = y0 - math.cos(angle) * longueur
                painter.drawLine(QPointF(x0, y0), QPointF(x1, y1))

    # --------------------------------------------------------------------------
    # Mouettes
    # --------------------------------------------------------------------------

    def _dessiner_mouettes(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        distance: float,
    ) -> None:
        """Dessine les mouettes avec translation et battement très léger."""
        if not self.avec_mouettes:
            return

        h = rect_scene.height()
        marge = h * 0.12

        for mouette in self.mouettes:
            x = self._x_boucle(
                rect_scene,
                mouette["x"],
                distance,
                mouette["vitesse"],
                marge,
            )
            y = (
                rect_scene.top()
                + rect_scene.height() * mouette["y"]
                + math.sin(distance * 0.020 + mouette["phase"]) * h * 0.004
            )
            l = h * 0.030 * mouette["taille"]

            battement = 0.48 + 0.18 * math.sin(distance * 0.035 + mouette["phase"])

            pen = QPen(_avec_alpha("#FFFFFF", mouette["alpha"]))
            pen.setWidthF(max(1.0, h * 0.0048))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            path = QPainterPath()
            path.moveTo(x - l, y)
            path.quadTo(
                QPointF(x - l * 0.44, y - l * battement),
                QPointF(x, y),
            )
            path.quadTo(
                QPointF(x + l * 0.44, y - l * battement),
                QPointF(x + l, y),
            )
            painter.drawPath(path)

    # --------------------------------------------------------------------------
    # Dessin principal
    # --------------------------------------------------------------------------

    def peindre_arriere(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_rail: float,
        distance: float = 0.0,
        **kwargs,
    ) -> None:
        """Dessine tout le paysage derrière le train."""
        if rect_scene.width() <= 0 or rect_scene.height() <= 0:
            return

        painter.save()

        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            y_horizon = self._y_horizon(rect_scene)
            y_plage = self._y_plage(rect_scene, y_rail)

            # --------------------------------------------------------------
            # Fond très lent / quasi fixe
            # --------------------------------------------------------------

            self._dessiner_ciel(
                painter=painter,
                rect_scene=rect_scene,
                y_horizon=y_horizon,
            )
            self._dessiner_soleil(
                painter=painter,
                rect_scene=rect_scene,
                y_horizon=y_horizon,
            )
            self._dessiner_nuages(
                painter=painter,
                rect_scene=rect_scene,
                distance=distance,
            )
            self._dessiner_mouettes(
                painter=painter,
                rect_scene=rect_scene,
                distance=distance,
            )

            # --------------------------------------------------------------
            # Arrière-plan côtier
            # --------------------------------------------------------------

            self._dessiner_caps(
                painter=painter,
                rect_scene=rect_scene,
                y_horizon=y_horizon,
                distance=distance,
            )
            self._dessiner_phare(
                painter=painter,
                rect_scene=rect_scene,
                y_horizon=y_horizon,
                distance=distance,
            )

            # --------------------------------------------------------------
            # Mer
            # --------------------------------------------------------------

            self._dessiner_mer(
                painter=painter,
                rect_scene=rect_scene,
                y_horizon=y_horizon,
                y_plage=y_plage,
                distance=distance,
            )
            self._dessiner_ponton(
                painter=painter,
                rect_scene=rect_scene,
                y_horizon=y_horizon,
                distance=distance,
            )

            # --------------------------------------------------------------
            # Littoral / premier plan
            # --------------------------------------------------------------

            self._dessiner_plage(
                painter=painter,
                rect_scene=rect_scene,
                y_plage=y_plage,
                distance=distance,
            )
            self._dessiner_promenade(
                painter=painter,
                rect_scene=rect_scene,
                y_plage=y_plage,
                distance=distance,
            )
            self._dessiner_oyats(
                painter=painter,
                rect_scene=rect_scene,
                y_plage=y_plage,
                distance=distance,
            )

        finally:
            painter.restore()

    def peindre_avant(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_rail: float,
        distance: float = 0.0,
        **kwargs,
    ) -> None:
        """Ne dessine rien devant le train."""
        return

    def peindre(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_rail: float,
        distance: float = 0.0,
        **kwargs,
    ) -> None:
        """
        Dessine le paysage maritime complet.

        Paramètres
        ----------
        painter :
            QPainter déjà actif.
        rect_scene :
            Rectangle complet de la scène.
        y_rail :
            Ordonnée de roulement des rails.
        distance :
            Distance visuelle parcourue, utilisée pour le défilement lent.
        """
        self.peindre_arriere(
            painter=painter,
            rect_scene=rect_scene,
            y_rail=y_rail,
            distance=distance,
            **kwargs,
        )
        self.peindre_avant(
            painter=painter,
            rect_scene=rect_scene,
            y_rail=y_rail,
            distance=distance,
            **kwargs,
        )
