################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6/onglet_4_6_1                   #
# Onglet 4.6.1.X – Compteur de pays visités                                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import random, time, math
from typing import Optional

from PyQt6.QtCore import (
    Qt,
    QRectF,
    QPointF,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
)
from PyQt6.QtGui import QPainter, QPainterPath, QBrush
from PyQt6.QtWidgets import QWidget, QSizePolicy

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import ombre_onglet_4_6
from _4_Interface._4_3_Icones._4_3_42_etoile import Etoiles
from _4_Interface._4_3_Icones._4_3_43_mouette import _dessiner_mouette
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_1.onglet_4_6_1_1_theme import (
    CompteurTheme,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_1.onglet_4_6_1_2_mer import (
    MerAnimee,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_1.onglet_4_6_1_3_infographie import (
    CercleDonnees,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_1.onglet_4_6_1_4_sable import (
    SableEtDecorMarin,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_6.onglet_4_6_1.onglet_4_6_1_5_bouteille import (
    BocalVerre,
)

# 1 -- Classe du compteur ------------------------------------------------------


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
      le haut du widget à chaque augmentation de la valeur (voir
      `SableEtDecorMarin`, qui porte toute la logique du sable, de la
      plage et du décor marin).
    - Le bocal (géométrie et rendu "verre" : corps renflé, col évasé,
      teinte translucide, contour en dégradé, reflets) est délégué à
      `BocalVerre` ; il est légèrement penché, comme planté de travers
      dans le sable plutôt que posé bien droit.
    - Une plage de sable, quelques coquillages et une étoile de mer
      stylisés occupent le bas-gauche de la carte (délégués eux aussi à
      `SableEtDecorMarin`).
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

    def __init__(
        self,
        fonction_traduction,
        plage_hauteur_debut_ratio: float = 0.6,
        value: int = 0,
        maximum: int = 220,
        parent: Optional[QWidget] = None,
        duree_animation: int = 1000,
        n_poissons: int = 6,
        n_bouees: int = 2,
    ) -> None:
        super().__init__(parent)

        self.fonction_traduction = fonction_traduction
        self._value = (
            0.0  # valeur animée, affichée à l'écran (niveau du sable / anneau)
        )
        self.target_value = 0  # dernière valeur demandée (source de vérité)
        self.maximum = max(1, maximum)  # jamais 0, évite la division par zéro
        self.duree_animation = duree_animation
        self.set_langue()

        # Mise à jour du style
        self.set_style()

        # --- Anneau de progression (cercle de données) ---
        self._cercle = CercleDonnees(start_angle=90, arc_width_ratio=0.10)
        self._echelle_cercle = 0.7

        # --- comportement du halo "presque plein" ---
        self._seuil_presque_plein = (
            0.92  # % du maximum à partir duquel le halo se déclenche
        )

        # --- bocal (géométrie + rendu "verre"), voir onglet_4_6_1_5_bocal.py ---
        self._bocal = BocalVerre(angle_inclinaison=10.0, echelle=0.6)

        # --- sable (bocal + plage), pluie et décor marin ---
        # Toute cette logique est déléguée : voir `onglet_4_6_1_4_sable.py`.
        self._sable = SableEtDecorMarin(
            plage_hauteur_debut_ratio=plage_hauteur_debut_ratio,
        )

        # --- mer (bas du widget, sous/au-delà de la plage) ---
        self._mer = MerAnimee(
            n_bulles=25, n_poissons=n_poissons, n_bouees=n_bouees, parent=self
        )
        self._mer.demarrer(on_tick=self.update)

        self._glow_opacity = 0.0

        self.setMinimumSize(140, 90)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

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

        self._etoiles = Etoiles(n=20)
        self._rng_mouette = random.Random()  # non seedé : vol réellement aléatoire
        self._mouette = {
            "active": False,
            "debut": 0.0,
            "duree": 0.0,
            "y_ratio": 0.0,
            "sens": 1,
            "prochain_vol": time.monotonic() + self._rng_mouette.uniform(4.0, 12.0),
        }

        self.set_value(value, animate=True)

    # ---------------------------------------------------------------
    # Compat : la plage s'ajuste désormais dans SableEtDecorMarin, mais on
    # garde cet attribut lisible depuis l'extérieur au cas où du code
    # appelant s'y référait déjà.
    # ---------------------------------------------------------------
    @property
    def plage_hauteur_debut_ratio(self) -> float:
        return self._sable.plage_hauteur_debut_ratio

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
            self._sable.pluie_progress = self._value_anim.currentTime() / duree
        else:
            self._sable.pluie_progress = 1.0
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
            self._sable.generer_pluie(delta, value, self.maximum)
        else:
            self._sable.vider_pluie()

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

    def set_style(self, style: int | None = None):
        self._PALETTE = CompteurTheme()._PALETTE
        if style is not None:
            self.setGraphicsEffect(ombre_onglet_4_6(style=style, parent=self))
        self.update()

    def sizeHint(self):
        from PyQt6.QtCore import QSize

        return QSize(240, 150)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # La densité de grains (bocal + plage) suit (grossièrement) l'aire
        # du widget ; voir `SableEtDecorMarin.ajuster_densite` pour la
        # règle exacte (on ne régénère que sur un écart notable).
        aire = max(1, self.width() * self.height())
        self._sable.ajuster_densite(aire)

    def _on_anim_terminee(self) -> None:
        """Nettoyage une fois l'animation de niveau terminée : la pluie de
        sable encore affichée (s'il en reste) est retirée — le sable
        statique a de toute façon atteint le niveau final au même
        moment, donc rien ne "disparaît" visuellement."""
        self._sable.vider_pluie()
        self.update()

    def _dessiner_mouette_animee(
        self, painter: QPainter, rect_carte: QRectF, side: float
    ) -> None:

        jour = 1.0 - self._PALETTE.get("nuit", 0.0)
        if jour <= 0.0:
            return  # pleine nuit : pas de mouette

        now = time.monotonic()
        m = self._mouette

        # -- Déclenchement d'un nouveau vol ------------------------------------
        if not m["active"] and now >= m["prochain_vol"]:
            m["active"] = True
            m["debut"] = now
            m["duree"] = self._rng_mouette.uniform(4.0, 7.0)
            m["y_ratio"] = self._rng_mouette.uniform(0.05, 0.28)  # tiers supérieur
            m["sens"] = self._rng_mouette.choice([-1, 1])

        if not m["active"]:
            return

        # -- Progression du vol -------------------------------------------------
        progress = (now - m["debut"]) / m["duree"]
        if progress >= 1.0:
            m["active"] = False
            m["prochain_vol"] = now + self._rng_mouette.uniform(8.0, 20.0)
            return

        # Traverse un peu au-delà des bords, pour une entrée/sortie naturelle
        marge = rect_carte.width() * 0.12
        if m["sens"] == 1:
            x = rect_carte.left() - marge + progress * (rect_carte.width() + 2 * marge)
        else:
            x = rect_carte.right() + marge - progress * (rect_carte.width() + 2 * marge)

        # Léger bobbing vertical, pour une trajectoire moins rectiligne
        y = (
            rect_carte.top()
            + m["y_ratio"] * rect_carte.height()
            + math.sin(progress * math.pi * 3) * side * 0.02
        )

        # Fondu en entrée/sortie de vol
        fondu = min(1.0, progress / 0.1, (1.0 - progress) / 0.1)

        taille = side * 0.09

        phase_battement = progress * m["duree"] * 9.0  # fréquence du battement d'ailes

        painter.save()
        painter.setOpacity(jour * fondu)
        _dessiner_mouette(
            painter,
            centre=QPointF(x, y),
            taille=taille,
            rotation=0.0,
            phase=phase_battement,
            inverse=m["sens"] != 1,
        )
        painter.restore()

    # ---------------------------------------------------------------
    # Rendu global
    # ---------------------------------------------------------------
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
        painter.fillPath(chemin_carte, QBrush(self._PALETTE["fond"]))
        painter.setClipPath(chemin_carte)

        self._etoiles.dessiner_etoiles(
            painter=painter,
            rect=rect_carte,
            side=side,
            opacite=self._PALETTE.get("nuit", 0.0),
        )
        self._dessiner_mouette_animee(painter, rect_carte, side)

        # --- zone de contenu : bocal à gauche, cercle de données à droite
        # (widget plus large que haut, donc pas d'empilement vertical) ---
        marge_h = side * 0.2
        marge_v = side * 0.1
        content_rect = rect_carte.adjusted(marge_h, marge_v, -marge_h, -marge_v)

        jar_h_max = content_rect.height()
        jar_w_max = min(jar_h_max * 0.62, content_rect.width() * 0.34)

        jar_h = jar_h_max * self._bocal.echelle
        jar_w = jar_w_max * self._bocal.echelle
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

        m = self._bocal.mesures(jar_rect)

        # Zone d'enfoncement du bocal courant : la plage ne pourra pas
        # recouvrir plus que `enfoncement_bocal_ratio` de sa hauteur.
        self._sable.calculer_zone_bocal(jar_rect)

        # --- bocal, légèrement penché : tout le rendu du bocal (sable,
        # pluie, contour, reflet) tourne autour du pied du bocal, comme
        # s'il avait été planté de travers plutôt que posé bien droit. ---
        painter.save()
        pivot = QPointF(jar_rect.center().x(), jar_rect.bottom())
        painter.translate(pivot)
        painter.rotate(self._bocal.angle_inclinaison)
        painter.translate(-pivot)

        contour = self._bocal.chemin_corps(m)
        m["chemin_corps"] = (
            contour  # évite de recalculer la géométrie du bocal côté sable
        )

        # Teinte de verre sur tout le corps, pour que les parois se lisent
        # même là où le sable n'a pas encore atteint — sinon le bocal reste
        # quasi invisible tant qu'il n'est pas assez rempli.
        self._bocal.dessiner_verre_corps(painter, contour)

        self._sable.dessiner_sable_bocal(painter, m, percent, self._PALETTE)

        self._bocal.dessiner_contour(painter, m, contour, self._PALETTE, side)
        self._bocal.dessiner_col(painter, m, self._PALETTE)
        self._bocal.dessiner_reflet(painter, m, contour)

        painter.restore()

        # Pluie de sable dessinée hors rotation, pour une chute verticale
        # indépendante de l'inclinaison du bocal.
        self._sable.dessiner_pluie(
            painter, m, pivot, self._bocal.angle_inclinaison, self._PALETTE
        )

        self._mer.dessiner(painter, rect_carte)

        # --- plage de sable : dessinée après le bocal, pour que sa base
        # se retrouve naturellement enfouie dans le sable ---
        self._sable.dessiner_plage(painter, rect_carte, self._PALETTE)
        self._sable.dessiner_decor_marin(
            painter, rect_carte, self._PALETTE, zone="plage"
        )

        if diam_cercle > 0:
            self._cercle.dessiner_glow(
                painter, cercle_rect, diam_cercle, self._PALETTE, self._glow_opacity
            )
            self._cercle.dessiner(
                painter=painter,
                cercle_rect=cercle_rect,
                percent=percent,
                valeur=self._value,
                label_text=self.label_text,
                palette=self._PALETTE,
            )

    def relancer_animation(self) -> None:
        """Relance l'animation du compteur sans modifier les données."""

        # --- Animation du niveau de sable / anneau, avec une pluie complète ---
        self._value_anim.stop()
        self._value_anim.setDuration(self.duree_animation)
        self._value_anim.setStartValue(0.0)
        self._value_anim.setEndValue(float(self.target_value))

        if self.target_value > 0:
            self._sable.generer_pluie(
                self.target_value, self.target_value, self.maximum
            )
        else:
            self._sable.vider_pluie()

        self._value_anim.start()

        # --- Rejoue le halo si la valeur cible est presque pleine ---
        presque_plein = (self.target_value / self.maximum) >= self._seuil_presque_plein

        if presque_plein:
            self._glow_anim.stop()
            self._glow_anim.start()
