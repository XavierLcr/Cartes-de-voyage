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
)
from PyQt6.QtWidgets import QWidget, QSizePolicy, QGraphicsDropShadowEffect

from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)

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
    - Le sable est composé de centaines de grains individuels générés
      une fois (position, taille et teinte aléatoires mais stables
      d'un repaint à l'autre), pour un rendu granuleux plutôt qu'un
      simple aplat de couleur. Seuls les grains sous le niveau courant
      sont visibles (découpe via le contour du bocal), ce qui anime
      naturellement la montée du sable pendant l'animation.
    - Une poignée de grains plus clairs ("étincelles") simulent un
      reflet de lumière sur quelques grains. Surface du sable
      légèrement irrégulière plutôt qu'une ligne parfaitement plate.
    - Reflet doux façon verre sur le bocal, couvercle décoratif.
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

    NB_GRAINS = 480

    def __init__(
        self,
        fonction_traduction,
        value: int = 0,
        maximum: int = 220,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self.fonction_traduction = fonction_traduction
        self._value = (
            0.0  # valeur animée, affichée à l'écran (niveau du sable / anneau)
        )
        self.target_value = 0  # dernière valeur demandée (source de vérité)
        self.maximum = max(1, maximum)  # jamais 0, évite la division par zéro
        self.set_langue()
        self.theme = CompteurTheme(style=0)

        # --- anneau de progression (cercle de données) ---
        self._arc_width_ratio = 0.09  # épaisseur de l'arc / diamètre du cercle
        self._start_angle = 90  # l'arc démarre en haut du cercle

        # --- comportement du halo "presque plein" ---
        self._seuil_presque_plein = (
            0.92  # % du maximum à partir duquel le halo se déclenche
        )

        # --- sable ---
        self._grains = self._generer_grains(self.NB_GRAINS)
        self._phase_vagues = random.Random(7).uniform(0.0, math.tau)

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
    def set_value(
        self, value: int | None, animate: bool = True, duration: int = 900
    ) -> None:
        """Met à jour le niveau affiché (sable + anneau), avec ou sans animation."""
        if value is not None:
            value = max(0, min(value, self.maximum))
            self.target_value = value
        else:
            value = self.target_value

        self._value_anim.stop()  # évite les à-coups si on change en plein vol
        self._value_anim.setDuration(duration if animate else 0)
        self._value_anim.setStartValue(self._value)
        self._value_anim.setEndValue(float(value))
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
        aire = max(1, self.width() * self.height())
        cible = max(150, min(900, int(aire / 55)))
        if abs(cible - len(self._grains)) > max(20, int(len(self._grains) * 0.25)):
            self._grains = self._generer_grains(cible)

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
            echelle = rng.uniform(0.45, 1.35)  # hétérogénéité de taille
            teinte_t = rng.uniform(0.0, 1.0)  # hétérogénéité de teinte
            etincelle = rng.random() < 0.05  # quelques grains qui accrochent la lumière
            grains.append((nx, ny, echelle, teinte_t, etincelle))
        return grains

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
            "couvercle_h": h * 0.10,
            "rayon_coin": min(w, h) * 0.16,
        }

    def _chemin_corps(self, m: dict) -> QPainterPath:
        """Contour du bocal (col + épaules + corps), sans le couvercle —
        c'est aussi la zone utilisée pour découper le sable et le reflet."""
        x0, x1, y0, y1 = m["x0"], m["x1"], m["y0"], m["y1"]
        cx = m["cx"]
        corps_haut = m["corps_haut"]
        col_x0 = cx - m["col_largeur"] / 2
        col_x1 = cx + m["col_largeur"] / 2
        r = m["rayon_coin"]
        haut_col = y0 + m["couvercle_h"] * 0.55
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

    def _dessiner_couvercle(self, painter: QPainter, m: dict) -> None:
        """Petit couvercle décoratif au sommet du col, pour lire clairement
        la forme comme un bocal fermé plutôt qu'un vase ouvert."""
        col_x0 = m["cx"] - m["col_largeur"] / 2
        col_x1 = m["cx"] + m["col_largeur"] / 2
        debord = m["col_largeur"] * 0.14
        rect_couvercle = QRectF(
            col_x0 - debord,
            m["y0"],
            (col_x1 - col_x0) + 2 * debord,
            m["couvercle_h"],
        )
        rayon = m["couvercle_h"] * 0.4

        chemin = QPainterPath()
        chemin.addRoundedRect(rect_couvercle, rayon, rayon)

        couleur = QColor(self.theme.piste)
        couleur.setAlpha(210)
        pen = QPen(self.theme.texte)
        pen.setWidthF(max(1.0, m["rayon_coin"] * 0.06))
        painter.setPen(pen)
        painter.setBrush(QBrush(couleur))
        painter.drawPath(chemin)

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
        rayon_base = largeur * 0.028
        rayon_max = rayon_base * 1.4

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
        pen_surface.setWidthF(max(1.2, largeur * 0.012))
        pen_surface.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_surface)
        pas = max(4.0, largeur / 14)
        x = x0
        while x < x1:
            vague = math.sin(x * 0.09 + self._phase_vagues) * largeur * 0.006
            painter.drawPoint(QPointF(x, niveau_y + vague))
            x += pas

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
        marge = side_cercle * 0.07
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
            "Segoe UI", max(9, int(side_cercle * 0.15)), QFont.Weight.Bold
        )
        painter.setFont(police_valeur)
        valeur_str = f"{int(round(self._value))}"
        rect_valeur = rect_arc.adjusted(0, -side_cercle * 0.07, 0, -side_cercle * 0.07)
        painter.drawText(rect_valeur, Qt.AlignmentFlag.AlignCenter, valeur_str)

        # --- légende, élidée pour rester dans le cercle ---
        police_etiquette = QFont("Segoe UI", max(6, int(side_cercle * 0.052)))
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
            "Segoe UI", max(6, int(side_cercle * 0.045)), QFont.Weight.DemiBold
        )
        painter.setFont(police_pct)
        fm = painter.fontMetrics()
        largeur_bulle = fm.horizontalAdvance(pct_texte) + side_cercle * 0.06
        hauteur_bulle = fm.height() * 1.2
        rect_bulle = QRectF(0, 0, largeur_bulle, hauteur_bulle)
        rect_bulle.moveCenter(
            QPointF(rect_arc.center().x(), rect_arc.center().y() + side_cercle * 0.255)
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

        jar_h = content_rect.height()
        jar_w = min(jar_h * 0.62, content_rect.width() * 0.34)
        jar_rect = QRectF(
            content_rect.left(),
            content_rect.top() + (content_rect.height() - jar_h) / 2,
            jar_w,
            jar_h,
        )

        gap = content_rect.width() * 0.06
        zone_droite_w = max(0.0, content_rect.right() - (jar_rect.right() + gap))
        diam_cercle = min(content_rect.height(), zone_droite_w)
        cercle_rect = QRectF(
            jar_rect.right() + gap + (zone_droite_w - diam_cercle) / 2,
            content_rect.top() + (content_rect.height() - diam_cercle) / 2,
            diam_cercle,
            diam_cercle,
        )

        percent = self._value / self.maximum if self.maximum else 0.0
        percent = max(0.0, min(1.0, percent))

        m = self._mesures_bocal(jar_rect)

        self._dessiner_sable(painter, m, percent)

        contour = self._chemin_corps(m)
        pen_contour = QPen(self.theme.piste)
        pen_contour.setWidthF(max(1.2, side * 0.012))
        painter.setPen(pen_contour)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(contour)

        self._dessiner_reflet_verre(painter, m, contour)
        self._dessiner_couvercle(painter, m)

        if diam_cercle > 0:
            if self._glow_opacity > 0:
                self._dessiner_glow(painter, cercle_rect, diam_cercle)
            self._dessiner_cercle_donnees(painter, cercle_rect, percent)
