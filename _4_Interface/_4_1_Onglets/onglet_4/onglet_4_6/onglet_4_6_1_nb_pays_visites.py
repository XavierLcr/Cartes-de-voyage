################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6                                #
# Onglet 4.6.1 – Compteur de pays visités (bocal de sable, harmonisé avec le   #
# widget 4.6.3)                                                                #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math
import random
from typing import List, Optional, Tuple

from PyQt6.QtCore import (
    Qt,
    QRectF,
    QPointF,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
    QTimer,
)
from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QBrush,
    QPen,
    QColor,
    QFont,
    QFontMetrics,
    QRadialGradient,
    QConicalGradient,
    QLinearGradient,
)
from PyQt6.QtWidgets import QWidget, QSizePolicy, QGraphicsDropShadowEffect

from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)
from _4_Interface._4_3_Icones._4_3_32_etoile_de_mer import _dessiner_etoile_mer
from _4_Interface._4_3_Icones._4_3_33_coquillage import _dessiner_coquillage

# 0 -- Thème du widget ---------------------------------------------------------


class CompteurTheme:
    """
    Palette de couleurs du widget compteur.

    Reprend la structure de `ThemeCarte` (onglet 4.6.3) : même fond de
    carte, même convention d'ombre, mêmes appels de style — mais avec son
    propre accent, pour se démarquer un peu de la carte voisine tout en
    restant cohérent dans la construction.

    `progression_debut` / `progression_fin` forment le dégradé sable
    (grain plus foncé -> grain plus clair). Ce même dégradé sert
    maintenant à deux endroits : les grains du bocal, et l'anneau de
    progression du cercle de données, pour que les deux moitiés du
    widget restent visuellement de la même famille. Il suit toujours la
    rotation de teinte de `renvoyer_couleur_widget`, comme les autres
    widgets de la grille.

    `alerte` ne signale plus un danger : c'est maintenant la couleur du
    léger halo doré qui entoure le cercle de données quand le bocal est
    presque plein — un clin d'œil poétique plutôt qu'une alarme. Elle
    reste une couleur fixe (deux nuances clair/sombre), indépendante de
    `renvoyer_couleur_widget`, pour rester reconnaissable quelle que
    soit l'instance du widget.
    """

    def __init__(
        self,
        style,
        teinte=[i / 360 for i in range(0, 360, 45)],
        nuances={
            "min_luminosite": 0.8,
            "max_luminosite": 0.95,
            "min_saturation": 0.2,
            "max_saturation": 0.4,
        },
        limite_essais=20,
    ):
        # Fond de carte : identiques aux valeurs utilisées par ThemeCarte,
        # pour que les deux widgets soient posés sur le même "papier".
        self.fond = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#ffffff",
                sombre="#12141c",
            )
        )
        self.texte = QColor(
            str(renvoyer_couleur_texte(style=style, couleur=self.fond.name()))
            if style != 1
            else "#1c1f2b"
        )

        # Piste / contour : dérivé du texte, très dilué, même logique que
        # l'arc de fond du widget voisin.
        self.piste = QColor(self.texte)
        self.piste.setAlpha(30 if style == 1 else 25)

        # Dégradé sable : grain foncé (debut) -> grain clair (fin).
        # Tons chauds, sable/miel, choisis pour rester lisibles aussi bien
        # sur fond clair que sur fond sombre.
        self.progression_debut = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#C9902F",
                sombre="#B87A22",
            )
        )
        self.progression_fin = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#F3D48C",
                sombre="#FFDE9E",
                reference=self.progression_debut.name(),
                essais=limite_essais,
            )
        )

        # Sous-texte
        self.sous_texte = QColor(self.texte)
        self.sous_texte.setAlpha(140)

        # Halo générique "objectif atteint" (gardé pour compatibilité avec
        # d'éventuels autres usages de CompteurTheme) : reprend le dégradé.
        self.complete = QColor(self.progression_fin)

        # Halo "bocal presque plein" : doré et chaud, plus une alarme rouge.
        self.alerte = QColor("#FFCB61" if style != 1 else "#FFDD94")

        # Ombre portée : même convention que ThemeCarte (dérivée du texte).
        self.ombre = QColor(self.texte)
        self.ombre.setAlpha(60 if style == 1 else 120)

    @staticmethod
    def _blend_hsv(c1: QColor, c2: QColor, t: float) -> QColor:
        """Interpole deux couleurs en espace HSV (transition plus vivante qu'en RGB)."""
        h1, s1, v1, _ = c1.getHsvF()
        h2, s2, v2, _ = c2.getHsvF()
        if h1 < 0:
            h1 = h2
        if h2 < 0:
            h2 = h1
        if abs(h2 - h1) > 0.5:
            if h1 < h2:
                h1 += 1.0
            else:
                h2 += 1.0
        h = (h1 + (h2 - h1) * t) % 1.0
        s = s1 + (s2 - s1) * t
        v = v1 + (v2 - v1) * t
        blended = QColor()
        blended.setHsvF(h, min(1.0, s), min(1.0, v))
        return blended


# 2 -- Classe du compteur ------------------------------------------------------


class CompteurCirculaireWidget(QWidget):
    """
    Bocal de sable qui se remplit, associé à un cercle de progression qui
    reprend les données (valeur, libellé, pourcentage) — pour visualiser
    une progression (ex. "12 / 20 pays visités") dans une carte à coins
    arrondis identique à celle du widget voisin, pour que les deux
    widgets forment un ensemble cohérent sur le tableau de bord.

    Fonctionnalités :
    - Animation fluide et interruptible du niveau de sable (pas de
      glitch si on change la valeur pendant l'animation en cours).
    - En plus de la montée du niveau, une pluie de grains tombe depuis
      le haut du widget à chaque augmentation de la valeur : les grains
      apparaissent au-dessus du bocal, entrent par le col (désormais
      ouvert, sans couvercle) et tombent vers la surface du sable en
      formation, avec des délais et des vitesses de chute légèrement
      différents d'un grain à l'autre pour un ruissellement naturel
      plutôt qu'une arrivée groupée. Cette pluie se greffe sur
      l'animation de niveau déjà en place (aucun timer supplémentaire).
    - Le sable est composé de centaines de grains individuels fins,
      générés une fois (position, taille et teinte aléatoires mais
      stables d'un repaint à l'autre), pour un rendu granuleux plutôt
      qu'un simple aplat de couleur. Seuls les grains sous le niveau
      courant sont visibles (découpe via le contour du bocal).
    - Une poignée de grains plus clairs ("étincelles") simulent un
      reflet de lumière sur quelques grains. Surface du sable
      légèrement irrégulière plutôt qu'une ligne parfaitement plate.
    - Le bocal est légèrement penché, comme planté de travers dans le
      sable plutôt que posé bien droit ; un léger bourrelet à l'ouverture
      du col vient en plus suggérer l'épaisseur du verre.
    - Une plage de sable (plus claire que celui du bocal, texture
      granuleuse, ligne de surface irrégulière) occupe le bas-gauche de
      la carte : elle démarre à `plage_hauteur_debut_ratio` de la
      hauteur tout à gauche, et s'enfonce progressivement (de plus en
      plus bas) jusqu'aux deux tiers de la largeur, pour mimer une plage
      qui rejoint la mer (ajoutée séparément). Le bocal, posé dessus, s'y
      retrouve donc partiellement enfoui. Quelques coquillages et une
      étoile de mer stylisés reposent sur cette plage, du côté où le
      sable s'enfonce — comme déjà au fond de l'eau ; et un discret
      filigrane marin est aussi imprimé sur la carte elle-même.
    - Reflet doux façon verre sur le bocal.
    - À droite du bocal, un cercle reprend les données : anneau à
      dégradé conique qui s'intensifie avec le pourcentage (même
      famille de couleurs que le sable), petit curseur lumineux en
      bout d'arc, valeur centrale, libellé et pourcentage dans une
      bulle, le tout contenu dans le cercle.
    - Léger halo doré autour du cercle de données quand le bocal est
      presque plein.
    - Entièrement redimensionnable (rien n'est codé en dur en pixels) ;
      la densité de grains se réajuste sur un redimensionnement notable.
    - Thème personnalisable via CompteurTheme.
    """

    NB_GRAINS = 620

    def __init__(
        self,
        fonction_traduction,
        plage_hauteur_debut_ratio: float = 0.6,
        value: int = 0,
        maximum: int = 220,
        parent: Optional[QWidget] = None,
        duree_animation: int = 1000,
    ) -> None:
        super().__init__(parent)

        # --- plage de sable (fond, façon plage qui s'enfonce dans la mer) ---
        # `plage_hauteur_debut_ratio` : à quelle hauteur (0 = haut de la
        # carte, 1 = bas) le sable démarre tout à gauche de la carte.
        # Exposé en paramètre pour pouvoir ajuster facilement l'équilibre
        # visuel sable / bocal / cercle sans toucher au code.
        self.plage_hauteur_debut_ratio = max(0.05, min(0.95, plage_hauteur_debut_ratio))
        # Le sable s'arrête (déjà "sous l'eau") à cette fraction de la
        # largeur de la carte : au-delà, plus de sable visible — c'est là
        # que la mer (ajoutée séparément) prendra le relais.
        self._plage_x_fin_ratio = 0.7

        self.fonction_traduction = fonction_traduction
        self._value = (
            0.0  # valeur animée, affichée à l'écran (niveau du sable / anneau)
        )
        self.target_value = 0  # dernière valeur demandée (source de vérité)
        self.maximum = max(1, maximum)  # jamais 0, évite la division par zéro
        self.duree_animation = duree_animation
        self.set_langue()
        self.theme = CompteurTheme(style=0)

        # --- anneau de progression (cercle de données) ---
        self._arc_width_ratio = 0.09  # épaisseur de l'arc / diamètre du cercle
        self._start_angle = 90  # l'arc démarre en haut du cercle
        self._echelle_cercle = 0.7

        # --- comportement du halo "presque plein" ---
        self._seuil_presque_plein = (
            0.92  # % du maximum à partir duquel le halo se déclenche
        )

        # --- posture du bocal ---
        # Légère inclinaison, comme un bocal planté un peu de travers dans
        # le sable plutôt que posé bien droit — l'angle est positif car
        # `QPainter.rotate` tourne dans le sens horaire : le col penche
        # donc vers la droite, dans le sens où la plage s'enfonce.
        self._echelle_bocal = 0.85
        self._angle_inclinaison_bocal = 10.0  # degrés

        # --- sable (bocal) ---
        self._grains = self._generer_grains(self.NB_GRAINS)
        self._phase_vagues = random.Random(7).uniform(0.0, math.tau)

        # --- sable (plage, au pied du bocal) ---
        self._grains_plage = self._generer_grains(480)
        self._profil_plage = self._generer_profil_plage()

        # --- pluie de sable (chute depuis le haut du widget) ---
        self._pluie: List[dict] = []
        self._pluie_progress: float = 0.0
        self._easing_chute = QEasingCurve(QEasingCurve.Type.InQuad)

        # --- décors marins ---
        self._decor_plage = self._generer_decor_plage()

        # --- mer (bas du widget, sous/au-delà de la plage) ---
        self._niveau_mer_ratio = 1 / 3  # occupe le tiers inférieur de la carte
        self._phase_mer = 0.0
        self._bulles_mer = self._generer_bulles_mer(22)

        self._timer_mer = QTimer(self)
        self._timer_mer.timeout.connect(self._animer_mer)
        self._timer_mer.start(30)

        self._glow_opacity = 0.0

        self.setMinimumSize(140, 90)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Ombre portée : mêmes réglages que la carte voisine (blur 30,
        # décalage (0, 8), couleur dérivée du texte).
        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(30)
        self._ombre_effet.setOffset(0, 8)
        self._ombre_effet.setColor(self.theme.ombre)
        self.setGraphicsEffect(self._ombre_effet)

        self._value_anim = QPropertyAnimation(self, b"animatedValue", self)
        self._value_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._value_anim.finished.connect(self._on_anim_terminee)

        self._glow_anim = QPropertyAnimation(self, b"glowOpacity", self)
        self._glow_anim.setDuration(700)
        self._glow_anim.setStartValue(0.0)
        self._glow_anim.setKeyValueAt(0.5, 1.0)
        self._glow_anim.setEndValue(0.0)
        self._glow_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._etait_presque_plein = False

        self.set_value(value, animate=True)

    # ---------------------------------------------------------------
    # Propriétés animables Qt (indispensable pour QPropertyAnimation)
    # ---------------------------------------------------------------
    def _get_animated_value(self) -> float:
        return self._value

    def _set_animated_value(self, v: float) -> None:
        self._value = v
        # La pluie de sable suit la même horloge que l'animation de
        # niveau : on dérive sa progression globale (0-1) du temps
        # courant de l'animation, sans timer dédié.
        duree = self._value_anim.duration()
        if duree > 0:
            self._pluie_progress = max(
                0.0, min(1.0, self._value_anim.currentTime() / duree)
            )
        else:
            self._pluie_progress = 1.0
        self.update()

    animatedValue = pyqtProperty(float, _get_animated_value, _set_animated_value)

    def _get_glow_opacity(self) -> float:
        return self._glow_opacity

    def _set_glow_opacity(self, v: float) -> None:
        self._glow_opacity = v
        self.update()

    glowOpacity = pyqtProperty(float, _get_glow_opacity, _set_glow_opacity)

    # ---------------------------------------------------------------
    # API publique
    # ---------------------------------------------------------------
    def set_value(self, value: int | None, animate: bool = True) -> None:
        """Met à jour le niveau affiché (sable + anneau), avec ou sans animation."""
        ancienne_cible = self.target_value
        if value is not None:
            value = max(0, min(value, self.maximum))
            self.target_value = value
        else:
            value = self.target_value

        self._value_anim.stop()  # évite les à-coups si on change en plein vol
        self._value_anim.setDuration(self.duree_animation if animate else 0)
        self._value_anim.setStartValue(self._value)
        self._value_anim.setEndValue(float(value))

        # Une pluie de sable n'a de sens que si le niveau augmente : on
        # ne fait pas "remonter" des grains si la valeur diminue.
        delta = value - ancienne_cible
        if animate and delta > 0:
            self._generer_pluie(delta, value)
        else:
            self._pluie = []

        self._value_anim.start()

        presque_plein = (value / self.maximum) >= self._seuil_presque_plein
        if presque_plein and not self._etait_presque_plein:
            self._glow_anim.stop()
            self._glow_anim.start()
        self._etait_presque_plein = presque_plein

    def set_maximum(self, maximum: int) -> None:
        self.maximum = max(1, maximum)
        self.update()

    def set_langue(self):
        self.label_text = self.fonction_traduction("granularite_pays_visites")
        self.update()

    def set_style(self, style, nuances, teintes):
        self.theme = CompteurTheme(
            style=style, nuances=nuances, teinte=teintes, limite_essais=20
        )
        # L'ombre portée dépend du thème (couleur dérivée du texte) : on la
        # remet à jour pour rester cohérent avec la carte voisine si le
        # style change (mode clair / sombre).
        self._ombre_effet.setColor(self.theme.ombre)
        self.update()

    def sizeHint(self):
        from PyQt6.QtCore import QSize

        return QSize(240, 150)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # La densité de grains suit (grossièrement) l'aire du widget, pour
        # rester ni trop clairsemée sur un grand bocal, ni trop chargée
        # sur un petit. On ne régénère que sur un écart notable, pour
        # éviter de reculer le motif à chaque pixel de redimensionnement.
        # Les grains étant plus fins qu'avant, on vise une densité plus
        # élevée pour ne pas paraître clairsemé.
        aire = max(1, self.width() * self.height())
        cible = max(220, min(1200, int(aire / 40)))
        if abs(cible - len(self._grains)) > max(20, int(len(self._grains) * 0.25)):
            self._grains = self._generer_grains(cible)

        cible_plage = max(200, min(1400, int(aire / 55)))
        if abs(cible_plage - len(self._grains_plage)) > max(
            20, int(len(self._grains_plage) * 0.25)
        ):
            self._grains_plage = self._generer_grains(cible_plage)

    # ---------------------------------------------------------------
    # Génération du sable
    # ---------------------------------------------------------------
    def _generer_grains(self, n: int) -> List[Tuple[float, float, float, float, bool]]:
        """
        Prégénère n grains de sable en coordonnées normalisées (0-1) sur
        toute la zone du corps du bocal, une fois pour toutes, pour un
        rendu stable d'un repaint à l'autre. Chaque grain porte :
        (nx, ny, echelle_rayon, teinte_t, etincelle). `ny=0` correspond
        au haut du corps (sous les épaules), `ny=1` au fond du bocal.
        """
        rng = random.Random(20240614)
        grains = []
        for _ in range(n):
            nx = rng.random()
            ny = rng.random()
            echelle = rng.uniform(0.40, 1.15)  # hétérogénéité de taille (grains fins)
            teinte_t = rng.uniform(0.0, 1.0)  # hétérogénéité de teinte
            etincelle = rng.random() < 0.05  # quelques grains qui accrochent la lumière
            grains.append((nx, ny, echelle, teinte_t, etincelle))
        return grains

    def _generer_pluie(self, delta: float, value_finale: float) -> None:
        """
        Prépare une pluie de grains qui tombent du haut du widget vers la
        surface du sable en formation, pour accompagner la montée du
        niveau d'un effet de versement plutôt que d'un remplissage
        instantané. Chaque grain a son propre délai de départ et sa
        propre durée de chute (fractions du temps total de l'animation),
        pour un ruissellement étalé plutôt qu'une arrivée groupée.
        """
        rng = random.Random()  # volontairement non stable : on veut de la variété
        proportion = max(0.0, min(1.0, delta / self.maximum))
        n = int(max(6, min(150, 10 + proportion * 260)))

        percent_final = max(0.0, min(1.0, value_finale / self.maximum))
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
                }
            )
        self._pluie = grains

    def _on_anim_terminee(self) -> None:
        """Nettoyage une fois l'animation de niveau terminée : la pluie de
        sable encore affichée (s'il en reste) est retirée — le sable
        statique a de toute façon atteint le niveau final au même
        moment, donc rien ne "disparaît" visuellement."""
        self._pluie = []
        self.update()

    # ---------------------------------------------------------------
    # Génération des décors marins
    # ---------------------------------------------------------------
    def _generer_decor_plage(self) -> List[dict]:
        """Prégénère les coquillages/étoile de mer posés sur la plage — ils
        ne sont plus nichés dans le sable du bocal, mais du côté où la
        plage s'enfonce vers la mer, comme s'ils reposaient déjà au fond
        de l'eau. Positions stables (même logique que les grains) pour ne
        pas bouger d'un repaint à l'autre. `t` repère l'abscisse le long
        de la plage (0 = tout à gauche, 1 = à la limite où le sable
        disparaît sous l'eau) ; `profondeur` repère l'enfoncement sous la
        ligne de surface du sable (0 = juste sous la surface, 1 = tout en
        bas de la carte)."""
        rng = random.Random(31415)
        types = ["coquillage", "etoile", "coquillage"]
        ts = [0.30, 0.52, 0.70]
        items = []
        for i, t_base in enumerate(ts):
            items.append(
                {
                    "t": max(0.04, min(0.96, t_base + rng.uniform(-0.04, 0.04))),
                    "profondeur": rng.uniform(0.14, 0.32),
                    "type": types[i % len(types)],
                    "echelle": rng.uniform(0.85, 1.15),
                    "angle": rng.uniform(-25.0, 25.0),
                }
            )
        return items

    def _generer_profil_plage(self, n: int = 16) -> List[float]:
        """Prégénère un léger bruit vertical (mais stable), réparti le long
        de la plage, pour que la ligne de sable ne soit pas une pente
        parfaitement droite/lisse mais garde un aspect naturel."""
        rng = random.Random(90210)
        return [rng.uniform(-1.0, 1.0) for _ in range(n)]

    # ---------------------------------------------------------------
    # Géométrie du bocal
    # ---------------------------------------------------------------
    def _mesures_bocal(self, rect: QRectF) -> dict:
        """Calcule les dimensions clés du bocal à partir de son rectangle englobant."""
        w, h = rect.width(), rect.height()
        return {
            "x0": rect.left(),
            "x1": rect.right(),
            "y0": rect.top(),
            "y1": rect.bottom(),
            "cx": rect.center().x(),
            "corps_haut": rect.top() + h * 0.30,
            "col_largeur": w * 0.40,
            "rayon_coin": min(w, h) * 0.16,
        }

    def _chemin_corps(self, m: dict) -> QPainterPath:
        """Contour du bocal (col ouvert + épaules + corps) — c'est aussi la
        zone utilisée pour découper le sable et le reflet. Le col n'est
        plus fermé par un couvercle : son ouverture, tout en haut, sert
        maintenant de point d'entrée visuel à la pluie de sable qui
        tombe depuis le haut du widget."""
        x0, x1, y0, y1 = m["x0"], m["x1"], m["y0"], m["y1"]
        cx = m["cx"]
        corps_haut = m["corps_haut"]
        col_x0 = cx - m["col_largeur"] / 2
        col_x1 = cx + m["col_largeur"] / 2
        r = m["rayon_coin"]
        haut_col = y0
        marge_epaule = (y1 - corps_haut) * 0.16

        chemin = QPainterPath()
        chemin.moveTo(col_x0, haut_col)
        chemin.lineTo(col_x0, corps_haut)
        chemin.quadTo(x0, corps_haut, x0, corps_haut + marge_epaule)
        chemin.lineTo(x0, y1 - r)
        chemin.quadTo(x0, y1, x0 + r, y1)
        chemin.lineTo(x1 - r, y1)
        chemin.quadTo(x1, y1, x1, y1 - r)
        chemin.lineTo(x1, corps_haut + marge_epaule)
        chemin.quadTo(x1, corps_haut, col_x1, corps_haut)
        chemin.lineTo(col_x1, haut_col)
        chemin.closeSubpath()
        return chemin

    # ---------------------------------------------------------------
    # Géométrie de la plage
    # ---------------------------------------------------------------
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

    def _plage_y_surface(self, rect_carte: QRectF, x: float) -> float:
        """Hauteur (y) de la ligne de sable de la plage à l'abscisse `x`
        (repère widget) : une pente descendante de `plage_hauteur_debut_ratio`
        (tout à gauche de la carte) jusqu'au bas de la carte à
        `_plage_x_fin_ratio` de la largeur, pour mimer une plage qui
        s'enfonce progressivement dans la mer — plus un léger bruit pour
        rester naturelle plutôt que parfaitement lisse."""
        x0 = rect_carte.left()
        x_fin = rect_carte.left() + rect_carte.width() * self._plage_x_fin_ratio
        y0 = rect_carte.top() + rect_carte.height() * self.plage_hauteur_debut_ratio
        y_fin = rect_carte.bottom()

        t = 0.0 if x_fin <= x0 else max(0.0, min(1.0, (x - x0) / (x_fin - x0)))
        y_base = y0 + (y_fin - y0) * t
        amplitude = rect_carte.height() * 0.018
        return y_base + self._jitter_plage(t, amplitude)

    def _chemin_plage(self, rect_carte: QRectF) -> QPainterPath:
        """Construit le contour de la plage : de la gauche de la carte
        jusqu'à `_plage_x_fin_ratio` de sa largeur, avec une ligne de
        surface légèrement irrégulière plutôt qu'une pente toute droite."""
        x0 = rect_carte.left()
        x_fin = rect_carte.left() + rect_carte.width() * self._plage_x_fin_ratio
        if x_fin <= x0:
            return QPainterPath()

        chemin = QPainterPath()
        n_points = 40
        for i in range(n_points + 1):
            x = x0 + (x_fin - x0) * (i / n_points)
            y = self._plage_y_surface(rect_carte, x)
            if i == 0:
                chemin.moveTo(x, y)
            else:
                chemin.lineTo(x, y)
        chemin.lineTo(x_fin, rect_carte.bottom())
        chemin.lineTo(x0, rect_carte.bottom())
        chemin.closeSubpath()
        return chemin

    def _point_sur_plage(
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
        y_surface = self._plage_y_surface(rect_carte, x)
        y_fond = rect_carte.bottom()
        y = y_surface + (y_fond - y_surface) * max(0.0, min(1.0, profondeur))
        return QPointF(x, y)

    # ---------------------------------------------------------------
    # Rendu
    # ---------------------------------------------------------------

    def _dessiner_glow(
        self, painter: QPainter, cercle_rect: QRectF, side_cercle: float
    ) -> None:
        """Halo doré, discret, autour du cercle de données, quand le bocal
        approche du niveau maximal."""
        glow_color = QColor(self.theme.alerte)
        glow_color.setAlphaF(0.25 * self._glow_opacity)
        expand = side_cercle * 0.06 * self._glow_opacity
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow_color))
        painter.drawEllipse(cercle_rect.adjusted(-expand, -expand, expand, expand))

    def _dessiner_sable(self, painter: QPainter, m: dict, percent: float) -> None:
        """Remplit le bocal de grains individuels jusqu'au niveau courant."""
        x0, x1, y1 = m["x0"], m["x1"], m["y1"]
        corps_haut = m["corps_haut"]
        hauteur_dispo = y1 - corps_haut
        if hauteur_dispo <= 0 or percent <= 0:
            return

        niveau_y = y1 - percent * hauteur_dispo

        corps = self._chemin_corps(m)
        rect_sable = QPainterPath()
        rect_sable.addRect(QRectF(x0 - 2, niveau_y, (x1 - x0) + 4, (y1 - niveau_y) + 2))
        zone_sable = corps.intersected(rect_sable)

        painter.save()
        painter.setClipPath(zone_sable)

        # légère teinte de fond, pour que les interstices entre grains ne
        # laissent pas voir le fond de carte
        fond_sable = QColor(self.theme.progression_debut)
        fond_sable.setAlpha(45)
        painter.fillPath(zone_sable, QBrush(fond_sable))

        largeur = x1 - x0
        rayon_base = largeur * 0.020  # grains plus fins qu'auparavant
        rayon_max = rayon_base * 1.35

        painter.setPen(Qt.PenStyle.NoPen)
        for nx, ny, echelle, teinte_t, etincelle in self._grains:
            y_reel = corps_haut + ny * hauteur_dispo
            if y_reel < niveau_y - rayon_max:
                continue  # grain encore au-dessus du sable : pas la peine de le dessiner
            x_reel = x0 + nx * largeur
            rayon = rayon_base * echelle
            if etincelle:
                couleur = QColor("#FFF4DA")
                couleur.setAlpha(190)
            else:
                couleur = self.theme._blend_hsv(
                    self.theme.progression_debut, self.theme.progression_fin, teinte_t
                )
                couleur.setAlpha(min(255, int(150 + 90 * (1 - ny))))
            painter.setBrush(QBrush(couleur))
            painter.drawEllipse(QPointF(x_reel, y_reel), rayon, rayon)

        # quelques touches sur la ligne de surface, pour un niveau
        # légèrement irrégulier plutôt qu'une ligne parfaitement plate
        pen_surface = QPen(self.theme.progression_fin)
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

    def _dessiner_pluie(self, painter: QPainter, m: dict) -> None:
        """Dessine les grains actuellement 'en vol', tombant du haut du
        widget, à travers le col désormais ouvert du bocal, vers la
        surface du sable en formation. Pas de clip supplémentaire ici :
        on hérite du clip ambiant (la carte arrondie) posé dans
        `paintEvent`, pour que la chute reste visible au-dessus du
        bocal, pas seulement une fois entrée dedans."""
        if not self._pluie:
            return

        x0, x1, y1 = m["x0"], m["x1"], m["y1"]
        corps_haut = m["corps_haut"]
        hauteur_dispo = y1 - corps_haut
        if hauteur_dispo <= 0:
            return

        col_x0 = m["cx"] - m["col_largeur"] / 2
        col_x1 = m["cx"] + m["col_largeur"] / 2
        y_depart = m["y0"] - (y1 - m["y0"]) * 0.4  # départ au-dessus du bocal

        largeur = x1 - x0
        rayon_base = largeur * 0.020
        global_t = self._pluie_progress

        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        for grain in self._pluie:
            delai = grain["delay"]
            fin = min(1.0, delai + grain["duree"])
            if global_t <= delai or global_t >= fin:
                continue  # pas encore parti, ou déjà posé
            local_t = (global_t - delai) / max(1e-6, fin - delai)
            eased = self._easing_chute.valueForProgress(max(0.0, min(1.0, local_t)))

            x_reel = col_x0 + grain["nx_neck"] * (col_x1 - col_x0)
            y_cible = corps_haut + grain["ny_cible"] * hauteur_dispo
            y_reel = y_depart + (y_cible - y_depart) * eased

            rayon = rayon_base * grain["echelle"]
            if grain["etincelle"]:
                couleur = QColor("#FFF4DA")
                couleur.setAlpha(200)
            else:
                couleur = self.theme._blend_hsv(
                    self.theme.progression_debut,
                    self.theme.progression_fin,
                    grain["teinte_t"],
                )
                couleur.setAlpha(215)
            painter.setBrush(QBrush(couleur))
            painter.drawEllipse(QPointF(x_reel, y_reel), rayon, rayon)
        painter.restore()

    def _dessiner_reflet_verre(
        self, painter: QPainter, m: dict, contour: QPainterPath
    ) -> None:
        """Reflet doux façon verre bombé, très subtil, en haut à gauche du bocal."""
        painter.save()
        painter.setClipPath(contour)
        foyer = QPointF(
            m["x0"] + (m["x1"] - m["x0"]) * 0.28,
            m["corps_haut"] + (m["y1"] - m["corps_haut"]) * 0.18,
        )
        rayon = (m["x1"] - m["x0"]) * 1.1
        gradient = QRadialGradient(foyer, rayon)
        couleur_centre = QColor("#FFFFFF")
        couleur_centre.setAlphaF(0.10)
        couleur_bord = QColor("#FFFFFF")
        couleur_bord.setAlphaF(0.0)
        gradient.setColorAt(0.0, couleur_centre)
        gradient.setColorAt(1.0, couleur_bord)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(QRectF(m["x0"], m["y0"], m["x1"] - m["x0"], m["y1"] - m["y0"]))
        painter.restore()

    @staticmethod
    def _eclaircir(couleur: QColor, quantite: float) -> QColor:
        """Renvoie une version plus claire de `couleur`, mélangée avec du
        blanc à hauteur de `quantite` (0 = inchangée, 1 = blanc pur)."""
        blanc = QColor("#FFFFFF")
        r = couleur.red() + (blanc.red() - couleur.red()) * quantite
        g = couleur.green() + (blanc.green() - couleur.green()) * quantite
        b = couleur.blue() + (blanc.blue() - couleur.blue()) * quantite
        return QColor(int(r), int(g), int(b))

    def _dessiner_col_bouteille(self, painter: QPainter, m: dict) -> None:
        """Petit raffinement du bocal : un léger bourrelet à l'ouverture du
        col, pour suggérer l'épaisseur du verre plutôt qu'une simple
        tranche plate, avec un discret reflet dessus comme sur le reste
        du bocal."""
        col_x0 = m["cx"] - m["col_largeur"] / 2
        col_x1 = m["cx"] + m["col_largeur"] / 2
        haut_col = m["y0"]
        rim_h = max(2.0, (col_x1 - col_x0) * 0.16)
        rect_rim = QRectF(col_x0, haut_col - rim_h * 0.5, col_x1 - col_x0, rim_h)

        painter.save()
        pen = QPen(self.theme.piste)
        pen.setWidthF(max(1.0, rim_h * 0.35))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect_rim, 0, 180 * 16)

        reflet = QColor("#FFFFFF")
        reflet.setAlphaF(0.35)
        pen_reflet = QPen(reflet)
        pen_reflet.setWidthF(max(0.8, rim_h * 0.22))
        pen_reflet.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_reflet)
        rect_reflet = rect_rim.adjusted(rim_h * 0.3, rim_h * 0.15, -rim_h * 0.3, 0)
        painter.drawArc(rect_reflet, 20 * 16, 140 * 16)
        painter.restore()

    def _dessiner_plage(self, painter: QPainter, rect_carte: QRectF) -> None:
        """Dessine la plage de sable en bas à gauche de la carte, qui
        s'enfonce progressivement vers la mer (ajoutée séparément par
        ailleurs). Appelée après le bocal : la partie basse du bocal se
        retrouve ainsi naturellement recouverte, pour un bocal qui semble
        planté dans le sable plutôt que simplement posé devant."""
        chemin = self._chemin_plage(rect_carte)
        if chemin.isEmpty():
            return

        # Sable légèrement plus clair que celui qui tombe dans le bocal,
        # pour distinguer les deux tout en restant dans la même famille.
        couleur_debut = self._eclaircir(self.theme.progression_debut, 0.22)
        couleur_fin = self._eclaircir(self.theme.progression_fin, 0.16)

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
                couleur = self.theme._blend_hsv(couleur_debut, couleur_fin, teinte_t)
                couleur.setAlpha(min(255, int(150 + 90 * ny)))
            painter.setBrush(QBrush(couleur))
            painter.drawEllipse(QPointF(x_reel, y_reel), rayon, rayon)

        painter.restore()

    def _dessiner_decor_plage(self, painter: QPainter, rect_carte: QRectF) -> None:
        """Place les coquillages/étoile de mer sur la plage, du côté où le
        sable s'enfonce vers la mer, comme s'ils reposaient déjà au fond
        de l'eau."""
        side = min(rect_carte.width(), rect_carte.height())
        taille_base = side * 0.10

        fond = QColor("#FFF7EA")
        fond.setAlpha(220)
        trait = QColor(self.theme.texte)
        trait.setAlpha(110)

        for item in self._decor_plage:
            centre = self._point_sur_plage(rect_carte, item["t"], item["profondeur"])
            taille = taille_base * item["echelle"]
            if item["type"] == "etoile":
                _dessiner_etoile_mer(
                    painter, centre, taille * 0.8, fond, trait, item["angle"]
                )
            else:
                _dessiner_coquillage(
                    painter, centre, taille, fond, trait, item["angle"]
                )

    def _dessiner_decor_carte(
        self, painter: QPainter, rect_carte: QRectF, side: float
    ) -> None:
        """Filigrane marin discret sur le fond de la carte, en dehors du
        bocal — un petit clin d'œil décoratif au thème voyage/plage."""
        taille = side * 0.11
        marge = side * 0.11
        fond = QColor("#e07a3f")
        fond.setAlpha(85)
        trait = QColor("#8a3d18")
        trait.setAlpha(130)

        positions = {
            "haut_gauche": QPointF(
                rect_carte.left() + marge, rect_carte.top() + marge * 1.3
            ),
            "bas_droit": QPointF(
                rect_carte.right() - marge, rect_carte.bottom() - marge * 1.1
            ),
        }
        for item in self._decor_carte:
            centre = positions.get(item["coin"])
            if centre is None:
                continue
            t = taille * item["echelle"]
            if item["type"] == "etoile":
                _dessiner_etoile_mer(
                    painter, centre, t * 0.8, fond, trait, item["angle"]
                )
            else:
                _dessiner_coquillage(painter, centre, t, fond, trait, item["angle"])

    # ---------------------------------------------------------------
    # Cercle de données (anneau + valeur + libellé + pourcentage)
    # ---------------------------------------------------------------
    @staticmethod
    def _point_sur_arc(
        rect: QRectF, angle_depart_deg: float, percent: float
    ) -> QPointF:
        """Calcule le point sur le cercle correspondant à l'extrémité de l'arc."""
        angle_deg = angle_depart_deg - percent * 360.0
        angle_rad = math.radians(angle_deg)
        cx, cy = rect.center().x(), rect.center().y()
        rx, ry = rect.width() / 2, rect.height() / 2
        return QPointF(cx + rx * math.cos(angle_rad), cy - ry * math.sin(angle_rad))

    def _couleurs_intensifiees(self, percent: float) -> Tuple[QColor, QColor, QColor]:
        """
        Renvoie 3 arrêts de couleur pour le dégradé conique de l'anneau :
        la fin de l'arc devient progressivement plus saturée/vive à mesure
        que le pourcentage augmente, pour donner une sensation de
        progression "qui s'intensifie" plutôt qu'un dégradé statique.
        Reprend le même dégradé sable que les grains du bocal.
        """
        debut = self.theme.progression_debut
        cible_fin = self.theme.progression_fin
        fin = CompteurTheme._blend_hsv(debut, cible_fin, 0.35 + 0.65 * percent)
        milieu = CompteurTheme._blend_hsv(debut, fin, 0.5)
        return debut, milieu, fin

    def _dessiner_cercle_donnees(
        self, painter: QPainter, cercle_rect: QRectF, percent: float
    ) -> None:
        """
        Anneau de progression contenant les données (valeur, libellé,
        pourcentage), à droite du bocal — même esprit que l'ancienne
        version du widget, recoloré dans la même famille sable que le
        bocal qui se remplit à côté.
        """
        side_cercle = cercle_rect.width()
        arc_width = max(4.0, side_cercle * self._arc_width_ratio)
        marge = side_cercle * 0.05
        rect_arc = QRectF(
            cercle_rect.left() + marge,
            cercle_rect.top() + marge,
            cercle_rect.width() - 2 * marge,
            cercle_rect.height() - 2 * marge,
        )

        # --- piste (arc de fond, toujours complet) ---
        pen = QPen(self.theme.piste)
        pen.setWidthF(arc_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect_arc, 0, 360 * 16)

        # --- arc de progression : dégradé sable qui s'intensifie ---
        if percent > 0:
            gradient = QConicalGradient(rect_arc.center(), self._start_angle)
            c_debut, c_milieu, c_fin = self._couleurs_intensifiees(percent)
            gradient.setColorAt(0.0, c_debut)
            gradient.setColorAt(0.55, c_milieu)
            gradient.setColorAt(1.0, c_fin)

            pen = QPen(QBrush(gradient), arc_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            span = int(360 * percent * 16)
            painter.drawArc(rect_arc, self._start_angle * 16, -span)

            # --- petit curseur lumineux à l'extrémité de l'arc ---
            point_fin = self._point_sur_arc(rect_arc, self._start_angle, percent)
            halo_curseur = QColor(c_fin)
            halo_curseur.setAlpha(85)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo_curseur))
            r_halo = arc_width * 0.58
            painter.drawEllipse(point_fin, r_halo, r_halo)
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            r_coeur = arc_width * 0.22
            painter.drawEllipse(point_fin, r_coeur, r_coeur)

        # --- valeur centrale ---
        painter.setPen(self.theme.texte)
        police_valeur = QFont(
            "Segoe UI", max(9, int(side_cercle * 0.19)), QFont.Weight.Bold
        )
        painter.setFont(police_valeur)
        valeur_str = f"{int(round(self._value))}"
        rect_valeur = rect_arc.adjusted(0, -side_cercle * 0.07, 0, -side_cercle * 0.07)
        painter.drawText(rect_valeur, Qt.AlignmentFlag.AlignCenter, valeur_str)

        # --- légende, élidée pour rester dans le cercle ---
        police_etiquette = QFont("Segoe UI", max(6, int(side_cercle * 0.065)))
        fm_etiquette = QFontMetrics(police_etiquette)
        largeur_dispo = rect_arc.width() * 0.86
        texte_etiquette = fm_etiquette.elidedText(
            self.label_text, Qt.TextElideMode.ElideRight, int(largeur_dispo)
        )
        painter.setPen(self.theme.sous_texte)
        painter.setFont(police_etiquette)
        rect_etiquette = rect_arc.adjusted(0, side_cercle * 0.15, 0, side_cercle * 0.15)
        painter.drawText(rect_etiquette, Qt.AlignmentFlag.AlignCenter, texte_etiquette)

        # --- pourcentage dans une petite bulle ---
        pct_texte = f"{int(round(percent * 100))} %"
        police_pct = QFont(
            "Segoe UI", max(6, int(side_cercle * 0.055)), QFont.Weight.DemiBold
        )
        painter.setFont(police_pct)
        fm = painter.fontMetrics()
        largeur_bulle = fm.horizontalAdvance(pct_texte) + side_cercle * 0.06
        hauteur_bulle = fm.height() * 1.2
        rect_bulle = QRectF(0, 0, largeur_bulle, hauteur_bulle)
        rect_bulle.moveCenter(
            QPointF(rect_arc.center().x(), rect_arc.center().y() + side_cercle * 0.28)
        )

        chemin_bulle = QPainterPath()
        chemin_bulle.addRoundedRect(rect_bulle, hauteur_bulle / 2, hauteur_bulle / 2)
        couleur_bulle = QColor(self.theme.progression_debut)
        couleur_bulle.setAlpha(30)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(couleur_bulle))
        painter.drawPath(chemin_bulle)

        painter.setPen(self.theme.progression_debut)
        painter.drawText(rect_bulle, Qt.AlignmentFlag.AlignCenter, pct_texte)

    # -- Mer

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

    def _animer_mer(self) -> None:
        self._phase_mer += 0.055
        for bulle in self._bulles_mer:
            bulle["ny"] -= bulle["vitesse"]
            if bulle["ny"] < 0.05:
                bulle["ny"] = 0.98
                bulle["nx"] = random.uniform(0.04, 0.96)
        self.update()

    def _dessiner_mer(self, painter: QPainter, rect_carte: QRectF) -> None:
        """Mer animée occupant le tiers inférieur de la carte — même logique
        d'eau/bulles/ondulation que le widget verre d'eau, mais en bande
        pleine largeur plutôt qu'en forme de verre."""
        gauche = rect_carte.left()
        droite = rect_carte.right()
        largeur = droite - gauche
        bas = rect_carte.bottom()
        niveau_mer = rect_carte.top() + rect_carte.height() * (
            1 - self._niveau_mer_ratio
        )

        # --- forme de la mer (surface ondulée -> fond plat) ---
        mer = QPainterPath()
        mer.moveTo(gauche, niveau_mer)
        n_pts = 60
        for i in range(n_pts + 1):
            t = i / n_pts
            x = gauche + largeur * t
            y = (
                niveau_mer
                + math.sin(t * math.tau * 2.2 + self._phase_mer) * largeur * 0.006
                + math.sin(t * math.tau * 4.7 - self._phase_mer * 0.7) * largeur * 0.003
            )
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

        # --- ligne de surface ---
        surface = QPainterPath()
        for i in range(n_pts + 1):
            t = i / n_pts
            x = gauche + largeur * t
            y = (
                niveau_mer
                + math.sin(t * math.tau * 2.2 + self._phase_mer) * largeur * 0.006
                + math.sin(t * math.tau * 4.7 - self._phase_mer * 0.7) * largeur * 0.003
            )
            if i == 0:
                surface.moveTo(x, y)
            else:
                surface.lineTo(x, y)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(225, 250, 255, 185), 1.4))
        painter.drawPath(surface)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()
        side = min(w, h)

        # --- carte à coins arrondis : même formule que la carte voisine ---
        rect_carte = QRectF(0, 0, w, h).adjusted(2, 2, -2, -2)
        rayon_carte = min(24, side * 0.18)
        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(rect_carte, rayon_carte, rayon_carte)
        painter.fillPath(chemin_carte, QBrush(self.theme.fond))
        painter.setClipPath(chemin_carte)

        # --- zone de contenu : bocal à gauche, cercle de données à droite
        # (widget plus large que haut, donc pas d'empilement vertical) ---
        marge_h = side * 0.16
        marge_v = side * 0.10
        content_rect = rect_carte.adjusted(marge_h, marge_v, -marge_h, -marge_v)

        jar_h_max = content_rect.height()
        jar_w_max = min(jar_h_max * 0.62, content_rect.width() * 0.34)

        jar_h = jar_h_max * self._echelle_bocal
        jar_w = jar_w_max * self._echelle_bocal
        jar_rect = QRectF(
            content_rect.left(),
            content_rect.top() + (content_rect.height() - jar_h) / 2,
            jar_w,
            jar_h,
        )

        gap = content_rect.width() * 0.06
        zone_droite_w = max(0.0, content_rect.right() - (jar_rect.right() + gap))
        diam_cercle_max = min(content_rect.height(), zone_droite_w)
        diam_cercle = diam_cercle_max * self._echelle_cercle

        marge_cercle = (
            side * 0.05
        )  # marge propre au cercle, ajuste à ton goût (0 = collé au bord)
        cercle_rect = QRectF(
            rect_carte.right() - diam_cercle - marge_cercle,
            rect_carte.top() + marge_cercle,
            diam_cercle,
            diam_cercle,
        )

        percent = self._value / self.maximum if self.maximum else 0.0
        percent = max(0.0, min(1.0, percent))

        m = self._mesures_bocal(jar_rect)

        # --- bocal, légèrement penché : tout le rendu du bocal (sable,
        # pluie, contour, reflet) tourne autour du pied du bocal, comme
        # s'il avait été planté de travers plutôt que posé bien droit. ---
        painter.save()
        pivot = QPointF(jar_rect.center().x(), jar_rect.bottom())
        painter.translate(pivot)
        painter.rotate(self._angle_inclinaison_bocal)
        painter.translate(-pivot)

        self._dessiner_sable(painter, m, percent)
        self._dessiner_pluie(painter, m)

        contour = self._chemin_corps(m)
        pen_contour = QPen(self.theme.piste)
        pen_contour.setWidthF(max(1.2, side * 0.012))
        painter.setPen(pen_contour)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(contour)

        self._dessiner_mer(painter, rect_carte)
        self._dessiner_col_bouteille(painter, m)
        self._dessiner_reflet_verre(painter, m, contour)

        painter.restore()

        # --- plage de sable : dessinée après le bocal, pour que sa base
        # se retrouve naturellement enfouie dans le sable ---
        self._dessiner_plage(painter, rect_carte)
        self._dessiner_decor_plage(painter, rect_carte)

        if diam_cercle > 0:
            if self._glow_opacity > 0:
                self._dessiner_glow(painter, cercle_rect, diam_cercle)
            self._dessiner_cercle_donnees(painter, cercle_rect, percent)

    def relancer_animation(self) -> None:
        """Relance l'animation du compteur sans modifier les données."""

        # --- Animation du niveau de sable / anneau, avec une pluie complète ---
        self._value_anim.stop()
        self._value_anim.setDuration(self.duree_animation)
        self._value_anim.setStartValue(0.0)
        self._value_anim.setEndValue(float(self.target_value))

        if self.target_value > 0:
            self._generer_pluie(self.target_value, self.target_value)
        else:
            self._pluie = []

        self._value_anim.start()

        # --- Rejoue le halo si la valeur cible est presque pleine ---
        presque_plein = (self.target_value / self.maximum) >= self._seuil_presque_plein

        if presque_plein:
            self._glow_anim.stop()
            self._glow_anim.start()
