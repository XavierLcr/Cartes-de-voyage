################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6/onglet_4_6_1                   #
# Onglet 4.6.1.4 – Sable (bocal + plage + pluie) et décor marin                #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math
import random
from typing import List, Optional, Tuple

from PyQt6.QtCore import Qt, QRectF, QPointF, QEasingCurve
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor

from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_1.onglet_4_6_1_1_theme import (
    interpoler_couleurs,
)
from _4_Interface._4_3_Icones._4_3_32_etoile_de_mer import _dessiner_etoile_mer
from _4_Interface._4_3_Icones._4_3_33_coquillage import _dessiner_coquillage

# Type d'un grain : (nx, ny, echelle_rayon, teinte_t, etincelle)
Grain = Tuple[float, float, float, float, bool]

NB_GRAINS_BOCAL_DEFAUT = 1000
NB_GRAINS_PLAGE_DEFAUT = 480


# 1 -- Fonctions libres ---------------------------------------------------------


## 1.1 -- Fonction de génération des grains de sable ----------------------------


def generer_grains(n: int) -> List[Grain]:
    """
    Prégénère n grains de sable en coordonnées normalisées (0-1) sur une
    zone rectangulaire quelconque (le bocal ou la plage, selon l'appelant),
    une fois pour toutes, pour un rendu stable d'un repaint à l'autre.
    Chaque grain porte (nx, ny, echelle_rayon, teinte_t, etincelle).
    """
    rng = random.Random()
    grains: List[Grain] = []
    for _ in range(n):
        nx = rng.random()
        ny = rng.random()
        echelle = rng.uniform(0.40, 1.15)  # hétérogénéité de taille (grains fins)
        teinte_t = rng.uniform(0.0, 1.0)  # hétérogénéité de teinte
        etincelle = rng.random() < 0.05  # quelques grains qui accrochent la lumière
        grains.append((nx, ny, echelle, teinte_t, etincelle))
    return grains


## 1.2 -- Fonction d'ajustement du nombre de grains ----------------------------


def ajuster_densite_grains(
    grains: List[Grain], aire: float, diviseur: float, minimum: int, maximum: int
) -> List[Grain]:
    """
    Renvoie une nouvelle liste de grains si la densité cible (dérivée de
    `aire`) s'écarte notablement de la densité actuelle, sinon renvoie
    `grains` inchangé. Centralise la règle "on ne régénère que sur un
    écart notable", commune au bocal et à la plage, pour éviter de la
    dupliquer à chaque appelant.
    """
    cible = max(minimum, min(maximum, int(aire / diviseur)))
    if abs(cible - len(grains)) > max(20, int(len(grains) * 0.25)):
        return generer_grains(cible)
    return grains


## 1.3 -- Fonction de pivot d'objets -------------------------------------------


def rotor_point(point: QPointF, pivot: QPointF, angle_deg: float) -> QPointF:
    """
    Applique une rotation d'angle `angle_deg` autour de `pivot` à `point`.
    Utilisé pour convertir un point calculé dans le repère local (non
    incliné) du bocal vers ses coordonnées réelles à l'écran, une fois le
    bocal incliné — notamment pour faire tomber la pluie de sable au bon
    endroit malgré l'inclinaison.
    """
    angle = math.radians(angle_deg)
    dx = point.x() - pivot.x()
    dy = point.y() - pivot.y()
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    x = dx * cos_a - dy * sin_a
    y = dx * sin_a + dy * cos_a
    return QPointF(pivot.x() + x, pivot.y() + y)


## 1.4 -- Fonction d'éclairsissement d'une QColor ------------------------------


def eclaircir(couleur: QColor, quantite: float) -> QColor:
    """Renvoie une version plus claire de `couleur`, mélangée avec du blanc
    à hauteur de `quantite` (0 = inchangée, 1 = blanc pur)."""
    blanc = QColor("#FFFFFF")
    r = couleur.red() + (blanc.red() - couleur.red()) * quantite
    g = couleur.green() + (blanc.green() - couleur.green()) * quantite
    b = couleur.blue() + (blanc.blue() - couleur.blue()) * quantite
    return QColor(int(r), int(g), int(b))


# 2 -- Classe sable + décor marin -------------------------------------------


class SableEtDecorMarin:
    """
    Regroupe tout ce qui concerne le sable (bocal, pluie de grains, plage)
    et le décor marin (étoiles de mer / coquillages) semé sur la plage.

    Ne dépend d'aucun widget Qt : les méthodes de dessin reçoivent le
    QPainter, les rectangles et la palette en paramètres — c'est le widget
    hôte (le compteur circulaire) qui pilote quand peindre quoi.

    Cycle de vie attendu côté widget hôte :
    - à la construction : instancier une fois.
    - `resizeEvent` : appeler `ajuster_densite(aire)`.
    - `set_value` (si la valeur augmente) : appeler `generer_pluie(...)`.
    - animation de niveau : refléter la progression via `pluie_progress`.
    - fin d'animation : appeler `vider_pluie()`.
    - `paintEvent` : appeler `calculer_zone_bocal(jar_rect)` puis les
      méthodes `dessiner_*` dans l'ordre bocal -> pluie -> plage -> décor.
    """

    def __init__(
        self,
        plage_hauteur_debut_ratio: float = 0.4,
        plage_x_fin_ratio: float = 0.7,
        enfoncement_bocal_ratio: float = 0.14,
        nb_grains_bocal: int = NB_GRAINS_BOCAL_DEFAUT,
        nb_grains_plage: int = NB_GRAINS_PLAGE_DEFAUT,
        nb_decor_plage: Optional[int] = None,
    ) -> None:
        # --- plage de sable (façon plage qui s'enfonce dans la mer) ---
        # `plage_hauteur_debut_ratio` : à quelle hauteur (0 = haut de la
        # carte, 1 = bas) le sable démarre tout à gauche de la carte.
        self.plage_hauteur_debut_ratio = max(0.05, min(0.95, plage_hauteur_debut_ratio))
        # Le sable s'arrête (déjà "sous l'eau") à cette fraction de la
        # largeur de la carte : au-delà, plus de sable visible — c'est là
        # que la mer prend le relais.
        self._plage_x_fin_ratio = plage_x_fin_ratio

        # Enfoncement du bocal dans le sable : fraction (0-1) de sa hauteur
        # que la plage a le droit de recouvrir.
        self._enfoncement_bocal_ratio = enfoncement_bocal_ratio
        # Rempli par `calculer_zone_bocal` avec (x_gauche, x_droite,
        # y_limite, marge) du bocal courant, pour que `plage_y_surface`
        # aplanisse localement.
        self._jar_zone: Optional[Tuple[float, float, float, float]] = None

        # --- sable (bocal) ---
        self._grains_bocal = generer_grains(nb_grains_bocal)
        self._phase_vagues = random.Random(7).uniform(0.0, math.tau)

        # --- sable (plage, au pied du bocal) ---
        self._grains_plage = generer_grains(nb_grains_plage)
        self._profil_plage = self._generer_profil_plage()

        # --- pluie de sable (chute depuis le haut du widget) ---
        self._pluie: List[dict] = []
        self._pluie_progress: float = 0.0
        self._easing_chute = QEasingCurve(QEasingCurve.Type.InQuad)

        # --- décor marin (sur la plage) ---
        n = nb_decor_plage if nb_decor_plage is not None else random.randint(8, 12)
        self._decor_plage = self._generer_decor_marin(
            n, zone="plage", graine=random.randint(0, 10**5)
        )

    # ---------------------------------------------------------------
    # Densité / resize
    # ---------------------------------------------------------------
    def ajuster_densite(self, aire: float) -> None:
        """
        À appeler depuis `resizeEvent` du widget hôte. La densité de
        grains suit (grossièrement) l'aire disponible, pour rester ni
        trop clairsemée sur un grand bocal, ni trop chargée sur un petit.
        Bocal et plage sont recalculés indépendamment : ce ne sont pas
        les mêmes grains, ni la même surface.
        """
        self._grains_bocal = ajuster_densite_grains(
            self._grains_bocal, aire, diviseur=40, minimum=220, maximum=1200
        )
        self._grains_plage = ajuster_densite_grains(
            self._grains_plage, aire, diviseur=55, minimum=200, maximum=1400
        )

    # ---------------------------------------------------------------
    # Pluie de sable
    # ---------------------------------------------------------------
    @property
    def pluie_progress(self) -> float:
        return self._pluie_progress

    @pluie_progress.setter
    def pluie_progress(self, valeur: float) -> None:
        self._pluie_progress = max(0.0, min(1.0, valeur))

    def vider_pluie(self) -> None:
        """À appeler une fois l'animation de niveau terminée : le sable
        statique a de toute façon atteint le niveau final au même moment,
        donc rien ne "disparaît" visuellement en retirant la pluie."""
        self._pluie = []

    def generer_pluie(self, delta: float, value_finale: float, maximum: int) -> None:
        """
        Prépare une pluie de grains qui tombent du haut du widget vers la
        surface du sable en formation, pour accompagner la montée du
        niveau d'un effet de versement plutôt que d'un remplissage
        instantané. N'a de sens que si le niveau augmente (delta > 0) :
        c'est à l'appelant de ne pas invoquer cette méthode sinon.
        """
        rng = random.Random()  # volontairement non stable : on veut de la variété
        proportion = max(0.0, min(1.0, delta / maximum))
        n = int(max(6, min(150, 10 + proportion * 260)))

        percent_final = max(0.0, min(1.0, value_finale / maximum))
        ny_surface = 1.0 - percent_final

        grains = []
        for _ in range(n):
            grains.append(
                {
                    "nx_neck": rng.uniform(0.14, 0.86),
                    "ny_cible": max(
                        0.0, min(1.0, ny_surface + rng.uniform(-0.03, 0.07))
                    ),
                    "delay": rng.uniform(0.0, 0.5),
                    "duree": rng.uniform(0.25, 0.55),
                    "echelle": rng.uniform(0.5, 1.2),
                    "teinte_t": rng.uniform(0.0, 1.0),
                    "etincelle": rng.random() < 0.05,
                    "freq_jitter": rng.uniform(1.5, 3.2),
                    "phase_jitter": rng.uniform(0.0, math.tau),
                    "amplitude_jitter": rng.uniform(0.4, 1.1),
                }
            )
        self._pluie = grains

    # ---------------------------------------------------------------
    # Géométrie de la plage
    # ---------------------------------------------------------------
    def _generer_profil_plage(self, n: int = 16) -> List[float]:
        """Prégénère un léger bruit vertical (mais stable), réparti le long
        de la plage, pour que la ligne de sable ne soit pas une pente
        parfaitement droite/lisse mais garde un aspect naturel."""
        rng = random.Random()
        return [rng.uniform(-1.0, 1.0) for _ in range(n)]

    def _jitter_plage(self, t: float, amplitude: float) -> float:
        """Décalage vertical (autour de 0) à l'abscisse relative `t`
        (0-1) le long de la plage, combinant le bruit prégénéré et une
        légère ondulation, pour une ligne de sable pas parfaitement
        lisse."""
        pts = self._profil_plage
        n = len(pts)
        pos = max(0.0, min(0.999999, t)) * (n - 1)
        i = int(pos)
        frac = pos - i
        bruit = pts[i] + (pts[min(i + 1, n - 1)] - pts[i]) * frac
        vague = math.sin(t * math.tau * 2.3 + self._phase_vagues) * 0.4
        return (bruit + vague) * amplitude

    def calculer_zone_bocal(self, jar_rect: QRectF, marge_ratio: float = 0.9) -> None:
        """
        À appeler à chaque `paintEvent`, avec le rectangle courant du
        bocal : mémorise la zone (x_gauche, x_droite, y_limite, marge)
        dans laquelle `plage_y_surface` doit aplanir localement la pente
        de la plage, pour que le bocal ne s'y enterre pas au-delà de
        `enfoncement_bocal_ratio` de sa hauteur.
        """
        marge_transition = jar_rect.width() * marge_ratio
        self._jar_zone = (
            jar_rect.left(),
            jar_rect.right(),
            jar_rect.bottom() - jar_rect.height() * self._enfoncement_bocal_ratio,
            marge_transition,
        )

    def plage_y_surface(self, rect_carte: QRectF, x: float) -> float:
        x0 = rect_carte.left()
        x_fin = rect_carte.left() + rect_carte.width() * self._plage_x_fin_ratio
        y0 = rect_carte.top() + rect_carte.height() * self.plage_hauteur_debut_ratio
        y_fin = rect_carte.bottom()

        t = 0.0 if x_fin <= x0 else max(0.0, min(1.0, (x - x0) / (x_fin - x0)))
        y_base = y0 + (y_fin - y0) * t
        amplitude = rect_carte.height() * 0.018
        y = y_base + self._jitter_plage(t, amplitude)

        # Aplanit localement la pente au droit du bocal.
        if self._jar_zone is not None:
            xg, xd, y_limite, marge = self._jar_zone
            if marge > 0 and xg - marge <= x <= xd + marge:
                if x < xg:
                    poids = (x - (xg - marge)) / marge
                elif x > xd:
                    poids = ((xd + marge) - x) / marge
                else:
                    poids = 1.0
                poids = max(0.0, min(1.0, poids))
                y_plafonne = max(y, y_limite)
                y = y + (y_plafonne - y) * poids

        return y

    def chemin_plage(self, rect_carte: QRectF) -> QPainterPath:
        """Construit le contour de la plage : de la gauche de la carte
        jusqu'à `_plage_x_fin_ratio` de sa largeur, avec une ligne de
        surface légèrement irrégulière et des coins inférieurs arrondis.
        """
        x0 = rect_carte.left()
        x_fin = rect_carte.left() + rect_carte.width() * self._plage_x_fin_ratio
        y_bas = rect_carte.bottom()

        if x_fin <= x0:
            return QPainterPath()

        rayon = min(24.0, rect_carte.width() * 0.05, rect_carte.height() * 0.18)

        chemin = QPainterPath()

        # --- Bord supérieur de la plage ---
        n_points = 40
        for i in range(n_points + 1):
            x = x0 + (x_fin - x0) * (i / n_points)
            y = self.plage_y_surface(rect_carte, x)

            if i == 0:
                chemin.moveTo(x, y)
            else:
                chemin.lineTo(x, y)

        # --- Coin inférieur droit ---
        chemin.lineTo(x_fin, y_bas - rayon)
        chemin.quadTo(x_fin, y_bas, x_fin - rayon, y_bas)

        # --- Bord inférieur ---
        chemin.lineTo(x0 + rayon, y_bas)

        # --- Coin inférieur gauche ---
        chemin.quadTo(x0, y_bas, x0, y_bas - rayon)

        chemin.closeSubpath()

        return chemin

    def point_sur_plage(
        self, rect_carte: QRectF, t: float, profondeur: float
    ) -> QPointF:
        """Point posé sur la plage à l'abscisse relative `t` (0-1, sur
        `_plage_x_fin_ratio` de la largeur de la carte), enfoncé de
        `profondeur` (0-1) entre la ligne de surface et le bas de la
        carte — utilisé pour ancrer les coquillages/étoile dans le sable
        plutôt que de les faire flotter au-dessus."""
        x0 = rect_carte.left()
        x_fin = rect_carte.left() + rect_carte.width() * self._plage_x_fin_ratio
        x = x0 + (x_fin - x0) * max(0.0, min(1.0, t))
        y_surface = self.plage_y_surface(rect_carte, x)
        y_fond = rect_carte.bottom()
        y = y_surface + (y_fond - y_surface) * max(0.0, min(1.0, profondeur))
        return QPointF(x, y)

    # ---------------------------------------------------------------
    # Rendu du sable
    # ---------------------------------------------------------------
    def dessiner_sable_bocal(
        self, painter: QPainter, m: dict, percent: float, palette: dict
    ) -> None:
        """Remplit le bocal de grains individuels jusqu'au niveau courant.
        `m` est le dict de mesures du bocal produit par
        `CompteurCirculaireWidget._mesures_bocal`, et `_chemin_corps` doit
        être fourni via `chemin_corps` (voir plus bas) — pour éviter de
        dupliquer la géométrie du bocal ici, cette méthode reçoit le
        contour déjà découpé sous forme de rectangle de remplissage."""
        x0, x1, y1 = m["x0"], m["x1"], m["y1"]
        corps_haut = m["corps_haut"]
        hauteur_dispo = y1 - corps_haut
        if hauteur_dispo <= 0 or percent <= 0:
            return

        niveau_y = y1 - percent * hauteur_dispo

        corps = m["chemin_corps"]
        rect_sable = QPainterPath()
        rect_sable.addRect(QRectF(x0 - 2, niveau_y, (x1 - x0) + 4, (y1 - niveau_y) + 2))
        zone_sable = corps.intersected(rect_sable)

        painter.save()
        painter.setClipPath(zone_sable)

        # légère teinte de fond, pour que les interstices entre grains ne
        # laissent pas voir le fond de carte
        fond_sable = QColor(palette["sable_debut"])
        fond_sable.setAlpha(45)
        painter.fillPath(zone_sable, QBrush(fond_sable))

        largeur = x1 - x0
        rayon_base = largeur * 0.020  # grains plus fins qu'auparavant
        rayon_max = rayon_base * 1.35

        painter.setPen(Qt.PenStyle.NoPen)
        for nx, ny, echelle, teinte_t, etincelle in self._grains_bocal:
            y_reel = corps_haut + ny * hauteur_dispo
            if y_reel < niveau_y - rayon_max:
                continue  # grain encore au-dessus du sable : pas la peine de le dessiner
            x_reel = x0 + nx * largeur
            rayon = rayon_base * echelle
            if etincelle:
                couleur = QColor("#FFF4DA")
                couleur.setAlpha(190)
            else:
                couleur = interpoler_couleurs(
                    couleurs=[palette["sable_debut"], palette["sable_fin"]],
                    poids=[1 - teinte_t, teinte_t],
                    retour="qcolor",
                )
                couleur.setAlpha(min(255, int(150 + 90 * (1 - ny))))
            painter.setBrush(QBrush(couleur))
            painter.drawEllipse(QPointF(x_reel, y_reel), rayon, rayon)

        # quelques touches sur la ligne de surface, pour un niveau
        # légèrement irrégulier plutôt qu'une ligne parfaitement plate
        pen_surface = QPen(palette["sable_debut"])
        pen_surface.setWidthF(max(1.0, largeur * 0.009))
        pen_surface.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_surface)
        pas = max(4.0, largeur / 14)
        x = x0
        while x < x1:
            vague = math.sin(x * 0.09 + self._phase_vagues) * largeur * 0.006
            painter.drawPoint(QPointF(x, niveau_y + vague))
            x += pas

        painter.restore()

    def dessiner_pluie(
        self,
        painter: QPainter,
        m: dict,
        pivot: QPointF,
        angle_deg: float,
        palette: dict,
    ) -> None:
        """Dessine les grains actuellement 'en vol'. Le point d'ENTRÉE (haut
        du col) est calculé dans le repère local du bocal puis tourné comme
        le bocal -- il doit rester aligné avec le col tel qu'il apparaît,
        incliné, à l'écran, sinon le sable semble tomber à côté de
        l'ouverture. Le point d'ARRIVÉE (sur le tas de sable) est lui aussi
        tourné, pour tomber au bon endroit sur le tas. Entre les deux, la
        chute reste presque verticale (x quasi constant, ancré au col) et
        ne dérive vers la position d'arrivée qu'en toute fin de course,
        comme un grain qui se tasse en se posant plutôt qu'une ligne
        diagonale rigide."""
        if not self._pluie:
            return

        x0, x1, y1 = m["x0"], m["x1"], m["y1"]
        corps_haut = m["corps_haut"]
        hauteur_dispo = y1 - corps_haut
        if hauteur_dispo <= 0:
            return

        col_x0 = m["cx"] - m["col_largeur"] / 2
        col_x1 = m["cx"] + m["col_largeur"] / 2
        largeur = x1 - x0
        rayon_base = largeur * 0.020
        global_t = self._pluie_progress

        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        for grain in self._pluie:
            delai = grain["delay"]
            fin = min(1.0, delai + grain["duree"])
            if global_t <= delai or global_t >= fin:
                continue
            local_t = (global_t - delai) / max(1e-6, fin - delai)
            eased = self._easing_chute.valueForProgress(max(0.0, min(1.0, local_t)))

            # -- Point d'entrée : haut du col, en repère local, tourné
            # comme le bocal -- c'est LA référence visuelle pour l'ouverture.
            x_local_entree = col_x0 + grain["nx_neck"] * (col_x1 - col_x0)
            point_entree = rotor_point(
                QPointF(x_local_entree, m["y0"]), pivot, angle_deg
            )

            # -- Point d'arrivée : sur le tas de sable, en repère local,
            # tourné pareillement, pour se poser au bon endroit du tas.
            y_cible_local = corps_haut + grain["ny_cible"] * hauteur_dispo
            point_arrivee = rotor_point(
                QPointF(x_local_entree, y_cible_local), pivot, angle_deg
            )

            # Départ, au-dessus du bocal, aligné en x avec le point d'entrée
            # pour que le grain vienne bien d'au-dessus de l'ouverture telle
            # qu'elle apparaît à l'écran.
            y_depart = point_entree.y() - (y1 - m["y0"]) * 0.4

            # X : quasi figé sur le point d'entrée pendant la majorité de la
            # chute (verticale), et ne dérive vers le point d'arrivée que
            # sur la fin (tassement), via un blend non-linéaire.
            blend_x = eased**2.4
            x_reel = point_entree.x() + (point_arrivee.x() - point_entree.x()) * blend_x

            # Y : interpolation classique entre départ et arrivée.
            y_reel = y_depart + (point_arrivee.y() - y_depart) * eased

            # Léger tremblement horizontal, nul au départ et à l'arrivée.
            jitter = (
                math.sin(
                    local_t * grain["freq_jitter"] * math.tau + grain["phase_jitter"]
                )
                * grain["amplitude_jitter"]
                * rayon_base
                * 2.5
                * math.sin(local_t * math.pi)
            )
            x_reel += jitter

            rayon = rayon_base * grain["echelle"]
            if grain["etincelle"]:
                couleur = QColor("#FFF4DA")
                couleur.setAlpha(200)
            else:
                couleur = interpoler_couleurs(
                    couleurs=[palette["sable_debut"], palette["sable_fin"]],
                    poids=[1 - grain["teinte_t"], grain["teinte_t"]],
                    retour="qcolor",
                )
                couleur.setAlpha(215)
            painter.setBrush(QBrush(couleur))
            painter.drawEllipse(QPointF(x_reel, y_reel), rayon, rayon)
        painter.restore()

    def dessiner_plage(
        self, painter: QPainter, rect_carte: QRectF, palette: dict
    ) -> None:
        """Dessine la plage de sable en bas à gauche de la carte, qui
        s'enfonce progressivement vers la mer (ajoutée séparément par
        ailleurs). À appeler après le bocal : la partie basse du bocal se
        retrouve ainsi naturellement recouverte, pour un bocal qui semble
        planté dans le sable plutôt que simplement posé devant."""
        chemin = self.chemin_plage(rect_carte)
        if chemin.isEmpty():
            return

        # Sable légèrement plus clair que celui qui tombe dans le bocal,
        # pour distinguer les deux tout en restant dans la même famille.
        couleur_debut = eclaircir(palette["sable_debut"], 0.22)
        couleur_fin = eclaircir(palette["sable_fin"], 0.16)

        painter.save()
        painter.setClipPath(chemin)

        fond_sable = QColor(couleur_debut)
        fond_sable.setAlpha(235)
        painter.fillPath(chemin, QBrush(fond_sable))

        bbox = chemin.boundingRect()
        largeur = max(1.0, bbox.width())
        rayon_base = largeur * 0.020

        painter.setPen(Qt.PenStyle.NoPen)
        for nx, ny, echelle, teinte_t, etincelle in self._grains_plage:
            x_reel = bbox.left() + nx * bbox.width()
            y_reel = bbox.top() + ny * bbox.height()
            rayon = rayon_base * echelle
            if etincelle:
                couleur = QColor("#FFFBF0")
                couleur.setAlpha(185)
            else:
                couleur = interpoler_couleurs(
                    couleurs=[couleur_debut, couleur_fin],
                    poids=[1 - teinte_t, teinte_t],
                    retour="qcolor",
                )
                couleur.setAlpha(min(255, int(150 + 90 * ny)))
            painter.setBrush(QBrush(couleur))
            painter.drawEllipse(QPointF(x_reel, y_reel), rayon, rayon)

        painter.restore()

    # ---------------------------------------------------------------
    # Décor marin (étoiles de mer / coquillages)
    # ---------------------------------------------------------------
    def _generer_decor_marin(
        self,
        n: int,
        zone: str = "plage",  # "plage" ou "mer"
        graine: int = 31415,
    ) -> List[dict]:
        """
        Prégénère n éléments de décor marin (étoiles de mer / coquillages),
        destinés soit à la plage (zone="plage", ancrés via
        `point_sur_plage`), soit au fond de la mer (zone="mer", en
        coordonnées normalisées dans son rectangle). Type, couleur, taille
        et angle varient d'un exemplaire à l'autre pour éviter l'effet de
        clones.
        """
        rng = random.Random(graine)
        palette_fond = ["#FFF7EA", "#FDEBD3", "#F7DCC6", "#FFE9D6", "#F3E1EE"]
        items = []
        for _ in range(n):
            item = {
                "type": rng.choice(["etoile", "coquillage"]),
                "echelle": rng.uniform(0.45, 1),
                "angle": rng.uniform(-40.0, 40.0),
                "fond": QColor(rng.choice(palette_fond)),
                "graine_forme": rng.randint(0, 99999),
            }
            if zone == "plage":
                item["t"] = rng.uniform(0.04, 0.96)
                item["profondeur"] = rng.uniform(0.05, 0.95)
            else:  # "mer" : positions normalisées, on évite le tiers proche
                # de la surface pour rester crédible "posé au fond"
                item["nx"] = rng.uniform(0.06, 0.94)
                item["ny"] = rng.uniform(0.55, 0.92)
            items.append(item)
        return items

    def dessiner_decor_marin(
        self,
        painter: QPainter,
        rect_zone: QRectF,
        palette: dict,
        zone: str = "plage",
    ) -> None:
        """Place les éléments prégénérés — sur la plage (ancrés dans le
        sable via `point_sur_plage`) ou au fond de la mer (positions
        normalisées dans `rect_zone`)."""
        items = self._decor_plage  # seule la zone "plage" est stockée en instance

        side = min(rect_zone.width(), rect_zone.height())
        taille_base = side * 0.07  # discret par rapport au décor de la mer

        trait = QColor(palette.get("texte"))
        trait.setAlpha(110)

        for item in items:
            if zone == "plage":
                centre = self.point_sur_plage(rect_zone, item["t"], item["profondeur"])
            else:
                centre = QPointF(
                    rect_zone.left() + item["nx"] * rect_zone.width(),
                    rect_zone.top() + item["ny"] * rect_zone.height(),
                )
            taille = taille_base * item["echelle"]
            fond = QColor(item["fond"])
            fond.setAlpha(210 if zone == "plage" else 175)  # estompé sous l'eau

            if item["type"] == "etoile":
                _dessiner_etoile_mer(
                    painter,
                    centre,
                    taille * 0.8,
                    fond,
                    trait,
                    item["angle"],
                    graine=item["graine_forme"],
                )
            else:
                _dessiner_coquillage(
                    painter, centre, taille, fond, trait, item["angle"]
                )
