################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.57 – Classe de création d'un paysage de montagne enneigé                 #
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
)

# 1 -- Outils ------------------------------------------------------------------


def _avec_alpha(
    couleur: QColor | str,
    alpha: int,
) -> QColor:
    """Renvoie une couleur avec transparence modifiée."""
    c = QColor(couleur)
    c.setAlpha(max(0, min(255, alpha)))
    return c


def _interpoler_couleurs(
    couleur_1: QColor | str,
    couleur_2: QColor | str,
    t: float,
) -> QColor:
    """Interpolation simple entre deux couleurs RGB."""
    t = max(0.0, min(1.0, float(t)))

    c1 = QColor(couleur_1)
    c2 = QColor(couleur_2)

    return QColor(
        int(c1.red() + (c2.red() - c1.red()) * t),
        int(c1.green() + (c2.green() - c1.green()) * t),
        int(c1.blue() + (c2.blue() - c1.blue()) * t),
        int(c1.alpha() + (c2.alpha() - c1.alpha()) * t),
    )


# 2 -- Classe de paysage -------------------------------------------------------


class PaysageMontagneEnneigee:
    """
    Paysage de montagne avec vallée et neige.

    Le décor contient :
        - un ciel froid dégradé ;
        - plusieurs couches de montagnes ;
        - des sommets enneigés ;
        - une vallée ;
        - quelques sapins ;
        - éventuellement des flocons animés.

    Le paysage est pensé pour être utilisé derrière le train dans
    l'animation de publication.
    """

    def __init__(
        self,
        graine: int = 84,
        neige_active: bool = True,
        intensite_neige: float = 1.0,
        n_couches_montagnes: int = 3,
        n_sapins: int = 18,
        avec_brume: bool = True,
    ):

        self.graine = graine
        self.neige_active = neige_active
        self.intensite_neige = max(
            0.0,
            float(intensite_neige),
        )
        self.n_couches_montagnes = max(
            2,
            int(n_couches_montagnes),
        )
        self.n_sapins = max(
            0,
            int(n_sapins),
        )
        self.avec_brume = avec_brume

        self._rng = random.Random(self.graine)

        # ------------------------------------------------------------------
        # Géométrie pré-générée
        # ------------------------------------------------------------------

        self.profils_montagnes = [
            self._generer_profil_montagne(
                index_couche=i,
            )
            for i in range(self.n_couches_montagnes)
        ]

        self.sapins = self._generer_sapins()

        self.flocons = self._generer_flocons()

    # --------------------------------------------------------------------------
    # Génération des profils
    # --------------------------------------------------------------------------

    def _generer_profil_montagne(
        self,
        index_couche: int,
    ) -> list[tuple[float, float]]:
        """
        Génère un profil montagneux en coordonnées normalisées.

        Chaque point vaut :
            (x_ratio, hauteur_ratio)
        """

        rng = random.Random(self.graine + 100 * (index_couche + 1))

        n_points = 8 + index_couche * 2

        points = []

        for i in range(n_points + 1):

            x_ratio = i / n_points

            # Les couches proches sont plus hautes et plus contrastées.
            profondeur = index_couche / max(1, self.n_couches_montagnes - 1)

            base_min = 0.18 + profondeur * 0.10
            base_max = 0.42 + profondeur * 0.20

            # On force quelques sommets plus marqués.
            oscillation = 0.08 * math.sin(
                x_ratio * math.pi * (2.3 + 0.4 * index_couche)
            )

            hauteur_ratio = (
                rng.uniform(
                    base_min,
                    base_max,
                )
                + oscillation
            )

            hauteur_ratio = max(
                0.12,
                min(0.78, hauteur_ratio),
            )

            points.append(
                (
                    x_ratio,
                    hauteur_ratio,
                )
            )

        return points

    def _generer_sapins(self) -> list[dict]:
        """Pré-génère quelques sapins pour la vallée."""

        rng = random.Random(self.graine + 3001)

        sapins = []

        for _ in range(self.n_sapins):

            sapins.append(
                {
                    "x": rng.uniform(0.02, 0.98),
                    "taille": rng.uniform(0.55, 1.15),
                    "couche": rng.choice([0, 1]),
                }
            )

        sapins.sort(
            key=lambda s: (
                s["couche"],
                s["taille"],
            )
        )

        return sapins

    def _generer_flocons(self) -> list[dict]:
        """Pré-génère les particules de neige."""

        rng = random.Random(self.graine + 7007)

        n_flocons = int(90 + 70 * self.intensite_neige)

        flocons = []

        for _ in range(n_flocons):

            flocons.append(
                {
                    "x": rng.random(),
                    "y": rng.random(),
                    "rayon": rng.uniform(0.8, 2.4),
                    "vitesse": rng.uniform(0.65, 1.40),
                    "derive": rng.uniform(0.10, 0.50),
                    "alpha": rng.randint(110, 220),
                }
            )

        return flocons

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    def _rect_ciel(
        self,
        rect_scene: QRectF,
    ) -> QRectF:
        """Zone du ciel."""
        return QRectF(
            rect_scene.left(),
            rect_scene.top(),
            rect_scene.width(),
            rect_scene.height() * 0.73,
        )

    def _rect_sol(
        self,
        rect_scene: QRectF,
        y_rail: float,
    ) -> QRectF:
        """
        Zone visible du sol devant les montagnes.

        On laisse un peu d'air entre la vallée et les rails pour que le train
        garde visuellement sa place.
        """

        y_sol = min(
            rect_scene.bottom(),
            y_rail - rect_scene.height() * 0.03,
        )

        hauteur = max(
            0.0,
            rect_scene.bottom() - y_sol,
        )

        return QRectF(
            rect_scene.left(),
            y_sol,
            rect_scene.width(),
            hauteur,
        )

    # --------------------------------------------------------------------------
    # Couleurs
    # --------------------------------------------------------------------------

    def _couleur_montagne(
        self,
        profondeur: float,
    ) -> QColor:
        """Couleur d'une couche de montagne."""
        return _interpoler_couleurs(
            "#B9C7D3",
            "#596875",
            profondeur,
        )

    def _couleur_vallee(
        self,
        profondeur: float,
    ) -> QColor:
        """Couleur des vallées / collines basses."""
        return _interpoler_couleurs(
            "#DCE3E2",
            "#97A59F",
            profondeur,
        )

    # --------------------------------------------------------------------------
    # Dessin du fond
    # --------------------------------------------------------------------------

    def _dessiner_ciel(
        self,
        painter: QPainter,
        rect_scene: QRectF,
    ) -> None:
        """Dessine le ciel dégradé."""

        rect_ciel = self._rect_ciel(rect_scene)

        gradient = QLinearGradient(
            rect_ciel.topLeft(),
            rect_ciel.bottomLeft(),
        )

        gradient.setColorAt(
            0.0,
            QColor("#C9E2F2"),
        )
        gradient.setColorAt(
            0.45,
            QColor("#EAF3FA"),
        )
        gradient.setColorAt(
            1.0,
            QColor("#F7FBFF"),
        )

        painter.fillRect(
            rect_ciel,
            QBrush(gradient),
        )

    def _dessiner_brume(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_horizon: float,
    ) -> None:
        """Ajoute une légère brume froide au pied des montagnes."""

        if not self.avec_brume:
            return

        h = rect_scene.height()

        for i in range(3):

            largeur = rect_scene.width() * (0.88 + i * 0.08)
            hauteur = h * (0.09 + i * 0.02)

            rect_brume = QRectF(
                rect_scene.center().x() - largeur / 2,
                y_horizon - hauteur * 0.35 + i * h * 0.015,
                largeur,
                hauteur,
            )

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(
                _avec_alpha(
                    "#F7FBFF",
                    70 - i * 12,
                )
            )
            painter.drawEllipse(rect_brume)

    # --------------------------------------------------------------------------
    # Dessin des montagnes
    # --------------------------------------------------------------------------

    def _chemin_montagne(
        self,
        rect_scene: QRectF,
        points_normes: list[tuple[float, float]],
        profondeur: float,
        decalage_x: float = 0.0,
        base_y: float | None = None,
    ) -> QPainterPath:
        """Construit le chemin d'une chaîne de montagnes."""

        if base_y is None:
            base_y = rect_scene.height() * (0.62 + profondeur * 0.11)

        chemin = QPainterPath()
        chemin.moveTo(
            rect_scene.left(),
            rect_scene.top() + base_y,
        )

        for x_ratio, hauteur_ratio in points_normes:

            x = rect_scene.left() + (x_ratio * rect_scene.width()) + decalage_x

            y = rect_scene.top() + base_y - hauteur_ratio * rect_scene.height() * 0.55

            chemin.lineTo(QPointF(x, y))

        chemin.lineTo(
            rect_scene.right(),
            rect_scene.top() + base_y,
        )
        chemin.lineTo(
            rect_scene.right(),
            rect_scene.bottom(),
        )
        chemin.lineTo(
            rect_scene.left(),
            rect_scene.bottom(),
        )
        chemin.closeSubpath()

        return chemin

    def _dessiner_neige_sommets(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        points_normes: list[tuple[float, float]],
        profondeur: float,
        base_y: float,
        decalage_x: float = 0.0,
    ) -> None:
        """Dessine une ligne de neige sur les plus hauts reliefs."""

        if len(points_normes) < 3:
            return

        seuil = 0.43 - profondeur * 0.08

        path_neige = QPainterPath()
        a_commence = False

        for i, (x_ratio, hauteur_ratio) in enumerate(points_normes):

            if hauteur_ratio < seuil:
                continue

            x = rect_scene.left() + (x_ratio * rect_scene.width()) + decalage_x

            y = rect_scene.top() + base_y - hauteur_ratio * rect_scene.height() * 0.55

            if not a_commence:
                path_neige.moveTo(x, y + rect_scene.height() * 0.018)
                a_commence = True

            path_neige.lineTo(x, y + rect_scene.height() * 0.012)

            # Petit retour vers le bas pour donner une plaque de neige.
            if i < len(points_normes) - 1:
                path_neige.lineTo(
                    x + rect_scene.width() * 0.01,
                    y + rect_scene.height() * 0.03,
                )

        if not a_commence:
            return

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(
            _avec_alpha(
                "#FDFEFF",
                235,
            )
        )
        painter.drawPath(path_neige)

    def _dessiner_montagnes(
        self,
        painter: QPainter,
        rect_scene: QRectF,
    ) -> None:
        """Dessine toutes les couches de montagnes."""

        for i, points_normes in enumerate(self.profils_montagnes):

            profondeur = i / max(
                1,
                self.n_couches_montagnes - 1,
            )

            base_y = rect_scene.height() * (0.60 + profondeur * 0.12)

            chemin = self._chemin_montagne(
                rect_scene=rect_scene,
                points_normes=points_normes,
                profondeur=profondeur,
                base_y=base_y,
            )

            couleur = self._couleur_montagne(profondeur)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(couleur)
            painter.drawPath(chemin)

            # Léger liseré froid.
            pen = QPen(
                _avec_alpha(
                    "#E8F1F6",
                    90,
                )
            )
            pen.setWidthF(1.2)
            painter.setPen(pen)

            for j in range(len(points_normes) - 1):

                x1r, h1 = points_normes[j]
                x2r, h2 = points_normes[j + 1]

                x1 = rect_scene.left() + x1r * rect_scene.width()
                x2 = rect_scene.left() + x2r * rect_scene.width()

                y1 = rect_scene.top() + base_y - h1 * rect_scene.height() * 0.55
                y2 = rect_scene.top() + base_y - h2 * rect_scene.height() * 0.55

                painter.drawLine(
                    QPointF(x1, y1),
                    QPointF(x2, y2),
                )

            self._dessiner_neige_sommets(
                painter=painter,
                rect_scene=rect_scene,
                points_normes=points_normes,
                profondeur=profondeur,
                base_y=base_y,
            )

        self._dessiner_brume(
            painter=painter,
            rect_scene=rect_scene,
            y_horizon=rect_scene.top() + rect_scene.height() * 0.66,
        )

    # --------------------------------------------------------------------------
    # Vallée
    # --------------------------------------------------------------------------

    def _dessiner_vallees(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        rect_sol: QRectF,
        distance: float,
    ) -> None:
        """Dessine des collines / vallons au pied des montagnes."""

        h = rect_scene.height()
        w = rect_scene.width()

        couches = [
            {
                "profondeur": 0.0,
                "amplitude": 0.030,
                "periode": 0.55,
                "vitesse": 0.10,
                "couleur": self._couleur_vallee(0.15),
                "alpha": 255,
            },
            {
                "profondeur": 1.0,
                "amplitude": 0.045,
                "periode": 0.42,
                "vitesse": 0.22,
                "couleur": self._couleur_vallee(0.85),
                "alpha": 255,
            },
        ]

        for couche in couches:

            amplitude = h * couche["amplitude"]
            periode = w * couche["periode"]
            decalage = -(distance * couche["vitesse"]) % periode

            y_base = rect_sol.top() - h * (0.015 + 0.020 * couche["profondeur"])

            path = QPainterPath()
            path.moveTo(
                rect_scene.left(),
                rect_scene.bottom(),
            )

            x = rect_scene.left() - periode + decalage

            path.lineTo(
                x,
                y_base,
            )

            while x <= rect_scene.right() + periode:

                x1 = x + periode * 0.25
                x2 = x + periode * 0.50
                x3 = x + periode * 0.75
                x4 = x + periode

                path.cubicTo(
                    QPointF(x1, y_base - amplitude),
                    QPointF(x2, y_base - amplitude),
                    QPointF(x2, y_base),
                )

                path.cubicTo(
                    QPointF(x3, y_base + amplitude * 0.08),
                    QPointF(x4, y_base + amplitude * 0.08),
                    QPointF(x4, y_base),
                )

                x += periode

            path.lineTo(
                rect_scene.right(),
                rect_scene.bottom(),
            )
            path.closeSubpath()

            couleur = QColor(couche["couleur"])
            couleur.setAlpha(couche["alpha"])

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(couleur)
            painter.drawPath(path)

    def _dessiner_sol_neige(
        self,
        painter: QPainter,
        rect_sol: QRectF,
    ) -> None:
        """Dessine le premier plan enneigé."""

        if rect_sol.height() <= 0:
            return

        gradient = QLinearGradient(
            rect_sol.topLeft(),
            rect_sol.bottomLeft(),
        )

        gradient.setColorAt(
            0.0,
            QColor("#F5F8FA"),
        )
        gradient.setColorAt(
            1.0,
            QColor("#DDE5E8"),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(rect_sol)

    # --------------------------------------------------------------------------
    # Sapins
    # --------------------------------------------------------------------------

    def _dessiner_un_sapin(
        self,
        painter: QPainter,
        centre: QPointF,
        taille: float,
        couleur_tronc: QColor | str,
        couleur_feuillage: QColor | str,
    ) -> None:
        """Dessine un petit sapin stylisé."""

        h = taille
        w = h * 0.34

        # Tronc
        rect_tronc = QRectF(
            centre.x() - w * 0.10,
            centre.y() - h * 0.12,
            w * 0.20,
            h * 0.18,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(couleur_tronc))
        painter.drawRoundedRect(
            rect_tronc,
            1.5,
            1.5,
        )

        # Étages de feuillage
        for i, facteur in enumerate([1.00, 0.78, 0.58]):

            largeur = w * facteur
            y_sommet = centre.y() - h * (0.20 + i * 0.20)
            y_base = y_sommet + h * 0.28

            path = QPainterPath()
            path.moveTo(
                centre.x(),
                y_sommet,
            )
            path.lineTo(
                centre.x() - largeur / 2,
                y_base,
            )
            path.lineTo(
                centre.x() + largeur / 2,
                y_base,
            )
            path.closeSubpath()

            painter.setBrush(QColor(couleur_feuillage))
            painter.drawPath(path)

            # petite touche de neige sur les branches
            painter.setBrush(
                _avec_alpha(
                    "#FDFEFF",
                    205,
                )
            )

            petite_neige = QPainterPath()
            petite_neige.moveTo(
                centre.x() - largeur * 0.18,
                y_sommet + h * 0.07,
            )
            petite_neige.lineTo(
                centre.x(),
                y_sommet + h * 0.03,
            )
            petite_neige.lineTo(
                centre.x() + largeur * 0.18,
                y_sommet + h * 0.07,
            )
            petite_neige.lineTo(
                centre.x() + largeur * 0.10,
                y_sommet + h * 0.10,
            )
            petite_neige.lineTo(
                centre.x() - largeur * 0.10,
                y_sommet + h * 0.10,
            )
            petite_neige.closeSubpath()

            painter.drawPath(petite_neige)

    def _dessiner_sapins(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        rect_sol: QRectF,
        distance: float,
    ) -> None:
        """Dessine les sapins de la vallée avec léger défilement."""

        if not self.sapins:
            return

        w = rect_scene.width()
        h = rect_scene.height()

        for sapin in self.sapins:

            couche = sapin["couche"]

            vitesse = 0.18 if couche == 0 else 0.36
            taille = h * (0.09 if couche == 0 else 0.13) * sapin["taille"]

            x_base = rect_scene.left() + sapin["x"] * w
            x = (
                rect_scene.left()
                + ((x_base - rect_scene.left() - distance * vitesse) % (w + 80.0))
                - 40.0
            )

            y = rect_sol.top() + h * (0.01 if couche == 0 else 0.03)

            couleur_feuillage = "#6C837B" if couche == 0 else "#48635A"

            self._dessiner_un_sapin(
                painter=painter,
                centre=QPointF(x, y),
                taille=taille,
                couleur_tronc="#66584B",
                couleur_feuillage=couleur_feuillage,
            )

    # --------------------------------------------------------------------------
    # Neige
    # --------------------------------------------------------------------------

    def _dessiner_neige(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        distance: float,
    ) -> None:
        """Dessine des flocons animés."""

        if not self.neige_active:
            return

        w = rect_scene.width()
        h = rect_scene.height()

        painter.setPen(Qt.PenStyle.NoPen)

        for flocon in self.flocons:

            # Chute verticale + légère dérive horizontale.
            y = ((flocon["y"] * h) + distance * 0.18 * flocon["vitesse"]) % (
                h + 30.0
            ) - 15.0

            x = ((flocon["x"] * w) + distance * 0.08 * flocon["derive"]) % (
                w + 40.0
            ) - 20.0

            r = flocon["rayon"]

            painter.setBrush(
                QColor(
                    255,
                    255,
                    255,
                    flocon["alpha"],
                )
            )
            painter.drawEllipse(
                QPointF(
                    rect_scene.left() + x,
                    rect_scene.top() + y,
                ),
                r,
                r,
            )

    # --------------------------------------------------------------------------
    # Dessin principal
    # --------------------------------------------------------------------------

    def peindre(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        y_rail: float,
        distance: float = 0.0,
        **kwargs,
    ) -> None:
        """
        Dessine le paysage complet.

        Paramètres
        ----------
        painter :
            QPainter déjà actif.
        rect_scene :
            Rectangle complet de la scène.
        y_rail :
            Ordonnée de roulement des rails.
        distance :
            Distance visuelle parcourue, utilisée pour l'animation.
        """

        if rect_scene.width() <= 0 or rect_scene.height() <= 0:
            return

        painter.save()

        try:

            painter.setRenderHint(
                QPainter.RenderHint.Antialiasing,
                True,
            )

            rect_sol = self._rect_sol(
                rect_scene=rect_scene,
                y_rail=y_rail,
            )

            # ------------------------------------------------------------------
            # Fond
            # ------------------------------------------------------------------

            self._dessiner_ciel(
                painter=painter,
                rect_scene=rect_scene,
            )

            # ------------------------------------------------------------------
            # Reliefs
            # ------------------------------------------------------------------

            self._dessiner_montagnes(
                painter=painter,
                rect_scene=rect_scene,
            )

            self._dessiner_vallees(
                painter=painter,
                rect_scene=rect_scene,
                rect_sol=rect_sol,
                distance=distance,
            )

            # ------------------------------------------------------------------
            # Premier plan
            # ------------------------------------------------------------------

            self._dessiner_sol_neige(
                painter=painter,
                rect_sol=rect_sol,
            )

            self._dessiner_sapins(
                painter=painter,
                rect_scene=rect_scene,
                rect_sol=rect_sol,
                distance=distance,
            )

            # ------------------------------------------------------------------
            # Neige
            # ------------------------------------------------------------------

            self._dessiner_neige(
                painter=painter,
                rect_scene=rect_scene,
                distance=distance,
            )

        finally:

            painter.restore()
