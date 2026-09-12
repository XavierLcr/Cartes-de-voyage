################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6                                #
# Onglet 4.6.1.2 – Mer animée (bulles + poissons)                              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math
import random
from typing import List

from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QPen,
    QColor,
    QRadialGradient,
    QLinearGradient,
)

from _4_Interface._4_3_Icones._4_3_34_poissons import _dessiner_poisson
from _4_Interface._4_3_Icones._4_3_35_raie import _dessiner_raie
from _4_Interface._4_3_Icones._4_3_36_tortue_de_mer import _dessiner_tortue
from _4_Interface._4_3_Icones._4_3_37_poisson_globe import _dessiner_poisson_globe
from _4_Interface._4_3_Icones._4_3_38_requin import _dessiner_requin
from _4_Interface._4_3_Icones._4_3_39_bouee import _dessiner_bouee
from _4_Interface._4_3_Icones._4_3_41_poulpe import _dessiner_poulpe

# 1 -- Fonction de dessin d'un poisson selon ses caractéristiques --------------


def _dessiner_creature(
    painter,
    centre,
    taille,
    sens,
    couleur,
    type_creature="poisson",
    phase=0.0,
    degrade=True,
):
    if type_creature == "raie":
        _dessiner_raie(painter, centre, taille, sens, couleur, phase, degrade)
    elif type_creature == "tortue":
        _dessiner_tortue(painter, centre, taille, sens, couleur, phase, degrade)
    elif type_creature == "poisson-globe":
        _dessiner_poisson_globe(painter, centre, taille, sens, couleur, phase, degrade)
    elif type_creature == "requin":
        _dessiner_requin(painter, centre, taille, sens, couleur, phase, degrade)
    elif type_creature == "poulpe":
        _dessiner_poulpe(painter, centre, taille, sens, couleur, phase, degrade)
    else:
        _dessiner_poisson(
            painter,
            centre,
            taille,
            sens,
            couleur,
            phase=phase,
            degrade=degrade,
        )


# 2 -- Création de la liste de poissons ----------------------------------------


## 2.1 -- Fonction de choix du poisson -----------------------------------------


def _tirer_type_poisson() -> str:

    REPARTITION_TYPES = [
        ("raie", 0.14),
        ("tortue", 0.14),
        ("poisson-globe", 0.10),
        ("requin", 0.12),
        ("poulpe", 0.48),
        ("poisson", 0.02),
    ]

    tirage = random.random()
    cumul = 0.0
    for type_creature, proba in REPARTITION_TYPES:
        cumul += proba
        if tirage < cumul:
            return type_creature
    return REPARTITION_TYPES[-1][0]


## 2.2 -- Fonction de génération des poissons ----------------------------------


def _generer_poissons(n: int) -> List[dict]:
    """Prégénère n poissons nageant dans la mer : trajectoire horizontale
    en va-et-vient (gauche <-> droite), à une hauteur et une vitesse qui
    varient d'un poisson à l'autre pour un banc naturel plutôt que des
    clones synchronisés."""
    rng = random.Random(2024)
    PALETTES_PAR_TYPE = {
        "poisson": ["#E8834A", "#D96C6C", "#E0B24C"],
        "requin": ["#D1D5D5", "#BAD1E6", "#CAD8E3"],
        "raie": ["#4C7FB0", "#A9C2C6", "#6C8CA0"],
        "tortue": ["#7A9E6E", "#5FA88A", "#8C9E5C"],
        "poisson-globe": ["#E8C468", "#D9B482", "#C9A876"],
        "poulpe": ["#C98F9B", "#A985B5", "#D29A78", "#7FA6B8"],
    }
    poissons = []
    for i in range(n):
        sens = 1 if rng.random() < 0.5 else -1
        type_creature_temp = _tirer_type_poisson()
        poissons.append(
            {
                "nx": rng.uniform(0.0, 1.0),  # position horizontale (0-1) dans la mer
                "ny": rng.uniform(0.1, 0.9),  # hauteur (0 = surface, 1 = fond)
                "sens": sens,  # 1 = va vers la droite, -1 = vers la gauche
                "vitesse": rng.uniform(
                    0.05, 0.11
                ),  # fraction de largeur / seconde-anim
                "echelle": rng.uniform(0.75, 1.25),
                "amplitude_verticale": rng.uniform(0.015, 0.035),
                "phase": rng.uniform(0.0, math.tau),
                "couleur": QColor(
                    random.choice(PALETTES_PAR_TYPE.get(type_creature_temp))
                ),
                "type_creature": type_creature_temp,
            }
        )
    return poissons


## 2.3 -- Fonction de génération des bouées ------------------------------------


def _generer_bouees(n: int) -> List[dict]:
    """Prégénère n bouées flottant à la surface, réparties horizontalement,
    chacune avec sa propre phase de tangage pour éviter un mouvement
    synchronisé (comme pour les poissons, on désynchronise via `phase`)."""
    rng = random.Random(7)
    return [
        {
            "nx": rng.uniform(0.4, 0.92),  # position horizontale (0-1), fixe
            "echelle": rng.uniform(0.85, 1.15),
            "phase": rng.uniform(0.0, math.tau),
        }
        for _ in range(n)
    ]


# 3 -- Classe de la mer --------------------------------------------------------


class MerAnimee:
    """
    Mer animée (dégradé d'eau, bulles montantes, poissons qui nagent),
    destinée à être dessinée en bande pleine largeur dans le bas d'une
    carte hôte (widget compteur, widget verre d'eau, ou tout autre
    widget partageant le même besoin).

    Composition plutôt qu'héritage de QWidget : la mer ne possède pas
    sa propre surface, elle est peinte directement sur le QPainter du
    widget hôte, dans son `paintEvent`, à l'endroit de l'ordre de
    dessin choisi par l'appelant (ex. avant la plage, pour que celle-ci
    recouvre naturellement le bas de la mer).

    Gère son propre timer d'animation : `demarrer()` / `arreter()`.
    """

    def __init__(
        self,
        n_bulles: int = 25,
        n_poissons: int = 6,
        n_bouees: int = 1,
        niveau_mer_ratio: float = 1 / 3,
        intervalle_ms: int = 30,
        parent=None,
    ) -> None:
        self._niveau_mer_ratio = (
            niveau_mer_ratio  # fraction basse de la carte occupée par la mer
        )
        self._phase_mer = 0.0

        self._bulles_mer = self._generer_bulles_mer(n_bulles)
        self._poissons = _generer_poissons(int(max(1, n_poissons)))
        self._bouees = _generer_bouees(int(max(0, n_bouees)))

        self._intervalle_ms = intervalle_ms
        self._timer = QTimer(parent)
        self._timer.timeout.connect(self._animer)
        self._on_tick = (
            None  # callback optionnel appelé après chaque pas (ex. self.update())
        )

    # ---------------------------------------------------------------
    # Cycle de vie du timer
    # ---------------------------------------------------------------
    def demarrer(self, on_tick=None) -> None:
        """Démarre l'animation. `on_tick`, si fourni, est appelé après
        chaque pas de simulation (typiquement `widget.update()`)."""
        if on_tick is not None:
            self._on_tick = on_tick
        if not self._timer.isActive():
            self._timer.start(self._intervalle_ms)

    def arreter(self) -> None:
        self._timer.stop()

    # ---------------------------------------------------------------
    # Génération
    # ---------------------------------------------------------------
    def _generer_bulles_mer(self, n: int) -> List[dict]:
        rng = random.Random(4)
        return [
            {
                "nx": rng.uniform(0.04, 0.96),
                "ny": rng.uniform(0.05, 0.95),
                "r_ratio": rng.uniform(0.010, 0.026),  # rayon / largeur de la mer
                "vitesse": rng.uniform(0.0012, 0.003),
                "phase": rng.uniform(0.0, math.tau),
            }
            for _ in range(n)
        ]

    # ---------------------------------------------------------------
    # Simulation
    # ---------------------------------------------------------------
    def _animer(self) -> None:
        self._phase_mer += 0.055
        for bulle in self._bulles_mer:
            bulle["ny"] -= bulle["vitesse"]
            if bulle["ny"] < 0.05:
                bulle["ny"] = 0.98
                bulle["nx"] = random.uniform(0.04, 0.96)

        for poisson in self._poissons:
            poisson["nx"] += poisson["vitesse"] * poisson["sens"] * 0.03
            if poisson["nx"] > 1.05:
                poisson["nx"] = 1.05
                poisson["sens"] = -1
            elif poisson["nx"] < -0.05:
                poisson["nx"] = -0.05
                poisson["sens"] = 1

        if self._on_tick is not None:
            self._on_tick()

    # ---------------------------------------------------------------
    # Rendu
    # ---------------------------------------------------------------
    def dessiner(self, painter: QPainter, rect_carte: QRectF) -> None:
        """Dessine la mer, ses bulles et ses poissons dans `rect_carte`
        (bande pleine largeur occupant le tiers inférieur, par défaut)."""
        gauche = rect_carte.left()
        droite = rect_carte.right()
        largeur = droite - gauche
        bas = rect_carte.bottom()
        niveau_mer = rect_carte.top() + rect_carte.height() * (
            1 - self._niveau_mer_ratio
        )

        def _y_surface_mer(t: float) -> float:
            return (
                niveau_mer
                + math.sin(t * math.tau * 2 + self._phase_mer) * largeur * 0.008
                + math.sin(t * math.tau * 5 - self._phase_mer * 0.7) * largeur * 0.004
            )

        # --- forme de la mer (surface ondulée -> fond plat) ---
        mer = QPainterPath()
        mer.moveTo(gauche, niveau_mer)
        n_pts = 60
        for i in range(n_pts + 1):
            t = i / n_pts
            x = gauche + largeur * t
            y = _y_surface_mer(t=t)
            mer.lineTo(x, y)
        mer.lineTo(droite, bas)
        mer.lineTo(gauche, bas)
        mer.closeSubpath()

        # --- dégradé de l'eau ---
        gradient = QLinearGradient(0, niveau_mer, 0, bas)
        gradient.setColorAt(0.0, QColor(120, 205, 225, 130))
        gradient.setColorAt(0.25, QColor(90, 185, 215, 150))
        gradient.setColorAt(0.70, QColor(55, 145, 190, 175))
        gradient.setColorAt(1.0, QColor(30, 105, 155, 200))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawPath(mer)

        # --- lumière sous la surface ---
        painter.save()
        painter.setClipPath(mer)
        lumiere = QRadialGradient(
            QPointF(gauche + largeur * 0.32, niveau_mer + largeur * 0.10),
            largeur * 0.7,
        )
        lumiere.setColorAt(0, QColor(220, 250, 255, 90))
        lumiere.setColorAt(1, QColor(220, 250, 255, 0))
        painter.setBrush(lumiere)
        painter.drawEllipse(
            QRectF(gauche - largeur * 0.3, niveau_mer, largeur * 1.6, largeur * 0.9)
        )
        painter.restore()

        # --- bulles ---
        painter.save()
        painter.setClipPath(mer)
        hauteur_mer = bas - niveau_mer
        for bulle in self._bulles_mer:
            x = gauche + bulle["nx"] * largeur
            x += math.sin(self._phase_mer * 1.5 + bulle["phase"]) * largeur * 0.01
            y = niveau_mer + bulle["ny"] * hauteur_mer
            r = bulle["r_ratio"] * largeur

            gradient_bulle = QRadialGradient(QPointF(x - r * 0.3, y - r * 0.3), r)
            gradient_bulle.setColorAt(0, QColor(255, 255, 255, 150))
            gradient_bulle.setColorAt(1, QColor(210, 245, 255, 25))
            painter.setBrush(gradient_bulle)
            painter.setPen(QPen(QColor(255, 255, 255, 90), 0.7))
            painter.drawEllipse(QRectF(x - r, y - r, 2 * r, 2 * r))

        painter.restore()

        # --- poissons qui nagent ---
        painter.save()
        painter.setClipPath(mer)
        hauteur_mer = bas - niveau_mer
        for poisson in self._poissons:
            x = gauche + poisson["nx"] * largeur
            y = (
                niveau_mer
                + poisson["ny"] * hauteur_mer
                + math.sin(self._phase_mer * 2.0 + poisson["phase"])
                * hauteur_mer
                * poisson["amplitude_verticale"]
            )
            taille = (
                largeur
                * 0.10
                * poisson["echelle"]
                * (1.3 if poisson["type_creature"] == "requin" else 1.0)
            )
            _dessiner_creature(
                painter,
                QPointF(x, y),
                taille,
                poisson["sens"],
                poisson["couleur"],
                type_creature=poisson["type_creature"],
                phase=self._phase_mer * poisson.get("vitesse_nage", 3.0)
                + poisson["phase"],
            )
        painter.restore()

        # --- bouées flottantes (hors clip : le dôme dépasse au-dessus de l'eau) ---
        hauteur_mer = bas - niveau_mer
        for bouee in self._bouees:
            x = gauche + bouee["nx"] * largeur
            t = bouee["nx"]
            y_surface = _y_surface_mer(t=t)
            profondeur_corde = bas
            taille = largeur * 0.11 * bouee["echelle"]
            _dessiner_bouee(
                painter,
                QPointF(x, y_surface),
                taille,
                profondeur_corde,
                phase=self._phase_mer * 0.4 + bouee["phase"],
                degrade=True,
            )

        # --- ligne de surface ---
        surface = QPainterPath()
        for i in range(n_pts + 1):
            t = i / n_pts
            x = gauche + largeur * t
            y = _y_surface_mer(t=t)
            if i == 0:
                surface.moveTo(x, y)
            else:
                surface.lineTo(x, y)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(225, 250, 255, 185), 1.4))
        painter.drawPath(surface)
