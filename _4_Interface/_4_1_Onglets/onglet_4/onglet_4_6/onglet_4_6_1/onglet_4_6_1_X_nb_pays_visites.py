################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6/onglet_4_6_1                   #
# Onglet 4.6.1.X – Compteur de pays visités                                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
from typing import Optional

from PyQt6.QtCore import (
    Qt,
    QRectF,
    QPointF,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
)
from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QBrush,
    QPen,
    QColor,
    QRadialGradient,
    QLinearGradient,
)
from PyQt6.QtWidgets import QWidget, QSizePolicy

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import ombre_onglet_4_6
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
    - Le bocal est légèrement penché, comme planté de travers dans le
      sable plutôt que posé bien droit ; un léger bourrelet à l'ouverture
      du col vient en plus suggérer l'épaisseur du verre.
    - Une plage de sable, quelques coquillages et une étoile de mer
      stylisés occupent le bas-gauche de la carte (délégués eux aussi à
      `SableEtDecorMarin`).
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

        # --- posture du bocal ---
        # Légère inclinaison, comme un bocal planté un peu de travers dans
        # le sable plutôt que posé bien droit — l'angle est positif car
        # `QPainter.rotate` tourne dans le sens horaire : le col penche
        # donc vers la droite, dans le sens où la plage s'enfonce.
        self._echelle_bocal = 0.6
        self._angle_inclinaison_bocal = 10.0  # degrés

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
        x0, x1, y0, y1 = m["x0"], m["x1"], m["y0"], m["y1"]
        cx = m["cx"]
        corps_haut = m["corps_haut"]
        col_largeur = m["col_largeur"]
        r = m["rayon_coin"]
        haut_col = y0
        marge_epaule = (y1 - corps_haut) * 0.16

        # Léger évasement du bord du col (bourrelet), plutôt que des parois
        # parfaitement parallèles jusqu'en haut.
        evasement = col_largeur * 0.08
        col_x0_haut = cx - col_largeur / 2 - evasement
        col_x1_haut = cx + col_largeur / 2 + evasement
        col_x0_bas = cx - col_largeur / 2
        col_x1_bas = cx + col_largeur / 2

        # Renflement du corps : les parois bombent légèrement vers
        # l'extérieur au lieu d'être des lignes droites, comme un bocal
        # soufflé plutôt qu'un cylindre.
        bulge = (x1 - x0) * 0.045
        corps_milieu_y = corps_haut + (y1 - (corps_haut + marge_epaule)) * 0.55

        chemin = QPainterPath()
        chemin.moveTo(col_x0_haut, haut_col)
        chemin.lineTo(col_x0_bas, corps_haut)
        chemin.quadTo(x0 - bulge * 0.2, corps_haut, x0, corps_haut + marge_epaule)
        chemin.quadTo(x0 - bulge, corps_milieu_y, x0, y1 - r)
        chemin.quadTo(x0, y1, x0 + r, y1)
        chemin.lineTo(x1 - r, y1)
        chemin.quadTo(x1, y1, x1, y1 - r)
        chemin.quadTo(x1 + bulge, corps_milieu_y, x1, corps_haut + marge_epaule)
        chemin.quadTo(x1 + bulge * 0.2, corps_haut, col_x1_bas, corps_haut)
        chemin.lineTo(col_x1_haut, haut_col)
        chemin.closeSubpath()
        return chemin

    # ---------------------------------------------------------------
    # Rendu du verre (bocal)
    # ---------------------------------------------------------------

    def _dessiner_verre_corps(self, painter: QPainter, contour: QPainterPath) -> None:
        """Légère teinte bleu-vert translucide sur tout le corps, pour que les
        parois se lisent comme du verre même là où il n'y a pas encore de
        sable — plutôt qu'un bocal invisible tant qu'il n'est pas assez
        rempli."""
        painter.save()
        painter.setClipPath(contour)
        bbox = contour.boundingRect()
        gradient = QLinearGradient(bbox.left(), 0, bbox.right(), 0)
        c_bord = QColor("#BFD9E0")
        c_bord.setAlphaF(0.24)
        c_centre = QColor("#EAF5F7")
        c_centre.setAlphaF(0.09)
        gradient.setColorAt(0.0, c_bord)
        gradient.setColorAt(0.5, c_centre)
        gradient.setColorAt(1.0, c_bord)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(bbox)
        painter.restore()

    def _dessiner_reflet_verre(self, painter, m, contour):
        painter.save()
        painter.setClipPath(contour)

        # --- halo diffus existant ---
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

        # --- reflet linéaire (bande verticale), typique du verre courbe ---
        largeur = m["x1"] - m["x0"]
        streak_x = m["x0"] + largeur * 0.24
        streak_w = largeur * 0.09
        streak_rect = QRectF(
            streak_x - streak_w / 2,
            m["corps_haut"],
            streak_w,
            (m["y1"] - m["corps_haut"]) * 0.82,
        )
        grad_streak = QLinearGradient(streak_rect.left(), 0, streak_rect.right(), 0)
        c_out = QColor("#FFFFFF")
        c_out.setAlphaF(0.0)
        c_in = QColor("#FFFFFF")
        c_in.setAlphaF(0.22)
        grad_streak.setColorAt(0.0, c_out)
        grad_streak.setColorAt(0.5, c_in)
        grad_streak.setColorAt(1.0, c_out)
        chemin_streak = QPainterPath()
        chemin_streak.addRoundedRect(streak_rect, streak_w / 2, streak_w / 2)
        painter.setBrush(QBrush(grad_streak))
        painter.drawPath(chemin_streak)

        painter.restore()

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
        pen = QPen(self._PALETTE["piste"])
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

        # --- zone de contenu : bocal à gauche, cercle de données à droite
        # (widget plus large que haut, donc pas d'empilement vertical) ---
        marge_h = side * 0.2
        marge_v = side * 0.1
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

        # Zone d'enfoncement du bocal courant : la plage ne pourra pas
        # recouvrir plus que `enfoncement_bocal_ratio` de sa hauteur.
        self._sable.calculer_zone_bocal(jar_rect)

        # --- bocal, légèrement penché : tout le rendu du bocal (sable,
        # pluie, contour, reflet) tourne autour du pied du bocal, comme
        # s'il avait été planté de travers plutôt que posé bien droit. ---
        painter.save()
        pivot = QPointF(jar_rect.center().x(), jar_rect.bottom())
        painter.translate(pivot)
        painter.rotate(self._angle_inclinaison_bocal)
        painter.translate(-pivot)

        contour = self._chemin_corps(m)
        m["chemin_corps"] = (
            contour  # évite de recalculer la géométrie du bocal côté sable
        )

        # Teinte de verre sur tout le corps, pour que les parois se lisent
        # même là où le sable n'a pas encore atteint — sinon le bocal reste
        # quasi invisible tant qu'il n'est pas assez rempli.
        self._dessiner_verre_corps(painter, contour)

        self._sable.dessiner_sable_bocal(painter, m, percent, self._PALETTE)

        # Contour en dégradé horizontal (bords plus sombres, centre plus
        # clair) pour suggérer la courbure/épaisseur du verre plutôt
        # qu'un simple trait uni.
        grad_contour = QLinearGradient(m["x0"], 0, m["x1"], 0)
        c_bord_sombre = QColor(self._PALETTE["piste"]).darker(130)
        c_bord_sombre.setAlpha(self._PALETTE["piste"].alpha())
        c_milieu = QColor(self._PALETTE["piste"])
        c_milieu.setAlpha(int(self._PALETTE["piste"].alpha() * 0.5))
        grad_contour.setColorAt(0.0, c_bord_sombre)
        grad_contour.setColorAt(0.5, c_milieu)
        grad_contour.setColorAt(1.0, c_bord_sombre)
        pen_contour = QPen(QBrush(grad_contour), max(1.2, side * 0.012))
        painter.setPen(pen_contour)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(contour)

        self._dessiner_col_bouteille(painter, m)
        self._dessiner_reflet_verre(painter, m, contour)

        painter.restore()

        # Pluie de sable dessinée hors rotation, pour une chute verticale
        # indépendante de l'inclinaison du bocal.
        self._sable.dessiner_pluie(
            painter, m, pivot, self._angle_inclinaison_bocal, self._PALETTE
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
