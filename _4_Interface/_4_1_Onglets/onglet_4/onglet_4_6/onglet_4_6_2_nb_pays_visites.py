################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6                                #
# Onglet 4.6.2 – Compteur de pays visités (harmonisé avec le widget 4.6.3)     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math
from typing import Optional, Tuple

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    pyqtProperty,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QSizePolicy, QWidget

from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)

# 1 -- Classe de création des couleurs -----------------------------------------


class CompteurTheme:
    """
    Palette de couleurs du widget compteur.

    Reprend la structure de `ThemeCarte` (onglet 4.6.3) : même fond de
    carte, même convention d'ombre, mêmes appels de style — mais avec son
    propre accent turquoise (sarcelle -> cyan), pour se démarquer un peu
    de la carte voisine tout en restant cohérent dans la construction.
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

        # Piste (arc de fond) : dérivée du texte, très diluée, même alpha
        # que la barre du mini-graphique de la carte voisine.
        self.piste = QColor(self.texte)
        self.piste.setAlpha(30 if style == "clair" else 25)

        # Dégradé de progression : turquoise sarcelle -> cyan, un accent
        # propre au compteur plutôt qu'un simple recopiage du badge voisin.
        self.progression_debut = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#15DDCC",
                sombre="#14B8A6",
            )
        )
        self.progression_fin = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#22D3EE",
                sombre="#67E8F9",
                reference=self.progression_debut.name(),
                essais=limite_essais,
            )
        )

        # Sous-texte
        self.sous_texte = QColor(self.texte)
        self.sous_texte.setAlpha(140)

        # Halo "objectif atteint" : teinte reprise du dégradé plutôt qu'une
        # couleur teal indépendante.
        self.complete = QColor(self.progression_fin)

        # Ombre portée : même convention que ThemeCarte (dérivée du texte).
        self.ombre = QColor(self.texte)
        self.ombre.setAlpha(60 if style == "clair" else 120)

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


# 2 -- Classe du compteur  -----------------------------------------------------


class CompteurCirculaireWidget(QWidget):
    """
    Compteur circulaire animé (ex. "Pays visités : 42 / 200"), présenté
    dans une carte à coins arrondis identique à celle du widget "Nombre
    de voyages" (même rayon, même ombre, même typographie), pour que les
    deux widgets forment un ensemble cohérent sur le tableau de bord.

    Fonctionnalités :
    - Animation fluide et interruptible (pas de glitch si on change la
      valeur pendant l'animation en cours).
    - Dégradé conique turquoise qui s'intensifie avec le pourcentage
      (interpolation HSV), avec un petit curseur lumineux en bout d'arc.
    - Pourcentage affiché dans une bulle discrète.
    - Ombre portée + léger halo lorsque l'objectif est atteint.
    - Entièrement redimensionnable (rien n'est codé en dur en pixels).
    - Thème personnalisable via CompteurTheme.
    """

    def __init__(
        self,
        fonction_traduction,
        value: int = 0,
        maximum: int = 200,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self.fonction_traduction = fonction_traduction
        self._value = 0.0  # valeur animée, affichée à l'écran
        self.target_value = 0  # dernière valeur demandée (source de vérité)
        self.maximum = max(1, maximum)  # jamais 0, évite la division par zéro
        self.set_langue()
        self.theme = CompteurTheme(style=0)

        self._arc_width_ratio = 0.09  # épaisseur de l'arc / diamètre du cercle
        self._start_angle = 90  # l'arc démarre en haut du cercle
        self._glow_opacity = 0.0

        self.setMinimumSize(100, 100)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Ombre portée : mêmes réglages que la carte "Nombre de voyages"
        # (blur 30, décalage (0, 8), couleur dérivée du texte).
        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(30)
        self._ombre_effet.setOffset(0, 8)
        self._ombre_effet.setColor(self.theme.ombre)
        self.setGraphicsEffect(self._ombre_effet)

        self._value_anim = QPropertyAnimation(self, b"animatedValue", self)
        self._value_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._glow_anim = QPropertyAnimation(self, b"glowOpacity", self)
        self._glow_anim.setDuration(900)
        self._glow_anim.setStartValue(0.0)
        self._glow_anim.setKeyValueAt(0.5, 1.0)
        self._glow_anim.setEndValue(0.0)
        self._glow_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

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
    def set_value(self, value: int, animate: bool = True, duration: int = 1200) -> None:
        """Met à jour la valeur affichée, avec ou sans animation."""
        value = max(0, min(value, self.maximum))
        self.target_value = value

        self._value_anim.stop()  # évite les à-coups si on change en plein vol
        self._value_anim.setDuration(duration if animate else 0)
        self._value_anim.setStartValue(self._value)
        self._value_anim.setEndValue(float(value))
        self._value_anim.start()

        if value >= self.maximum:
            self._glow_anim.stop()
            self._glow_anim.start()

    def set_maximum(self, maximum: int) -> None:
        self.maximum = max(1, maximum)
        self.update()

    def sizeHint(self):
        from PyQt6.QtCore import QSize

        return QSize(200, 200)

    # ---------------------------------------------------------------
    # Rendu
    # ---------------------------------------------------------------
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()

        # --- carte à coins arrondis : même formule que la carte voisine ---
        rect_carte = QRectF(0, 0, w, h).adjusted(2, 2, -2, -2)
        rayon = min(24, min(w, h) * 0.18)
        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(rect_carte, rayon, rayon)
        painter.fillPath(chemin_carte, QBrush(self.theme.fond))
        painter.setClipPath(chemin_carte)

        # --- anneau de progression, centré dans la carte ---
        side = min(w, h)
        arc_width = max(6.0, side * self._arc_width_ratio)
        marge = side * 0.14
        rect = QRectF(
            (w - side) / 2 + marge,
            (h - side) / 2 + marge,
            side - 2 * marge,
            side - 2 * marge,
        )

        percent = self._value / self.maximum if self.maximum else 0.0
        percent = max(0.0, min(1.0, percent))

        # --- halo discret quand l'objectif est atteint ---
        if self._glow_opacity > 0:
            glow_color = QColor(self.theme.complete)
            glow_color.setAlphaF(0.22 * self._glow_opacity)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(glow_color))
            expand = side * 0.05 * self._glow_opacity
            painter.drawEllipse(rect.adjusted(-expand, -expand, expand, expand))

        # --- piste (arc de fond, toujours complet) ---
        pen = QPen(self.theme.piste)
        pen.setWidthF(arc_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect, 0, 360 * 16)

        # --- arc de progression : dégradé qui s'intensifie avec le pourcentage ---
        if percent > 0:
            gradient = QConicalGradient(rect.center(), self._start_angle)
            c_debut, c_milieu, c_fin = self._couleurs_intensifiees(percent)
            gradient.setColorAt(0.0, c_debut)
            gradient.setColorAt(0.55, c_milieu)
            gradient.setColorAt(1.0, c_fin)

            pen = QPen(QBrush(gradient), arc_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            span = int(360 * percent * 16)
            painter.drawArc(rect, self._start_angle * 16, -span)

            # --- petit curseur lumineux à l'extrémité de l'arc ---
            point_fin = self._point_sur_arc(rect, self._start_angle, percent)
            halo_curseur = QColor(c_fin)
            halo_curseur.setAlpha(85)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo_curseur))
            r_halo = arc_width * 0.58
            painter.drawEllipse(point_fin, r_halo, r_halo)
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            r_coeur = arc_width * 0.22
            painter.drawEllipse(point_fin, r_coeur, r_coeur)

        # --- valeur centrale : même famille/graisse que la carte voisine ---
        painter.setPen(self.theme.texte)
        police_valeur = QFont("Segoe UI", max(10, int(side * 0.15)), QFont.Weight.Bold)
        painter.setFont(police_valeur)
        valeur_str = f"{int(round(self._value))}"
        rect_valeur = rect.adjusted(0, -side * 0.07, 0, -side * 0.07)
        painter.drawText(rect_valeur, Qt.AlignmentFlag.AlignCenter, valeur_str)

        # --- légende ---
        painter.setPen(self.theme.sous_texte)
        police_etiquette = QFont("Segoe UI", max(7, int(side * 0.052)))
        painter.setFont(police_etiquette)
        rect_etiquette = rect.adjusted(0, side * 0.15, 0, side * 0.15)
        painter.drawText(rect_etiquette, Qt.AlignmentFlag.AlignCenter, self.label_text)

        # --- pourcentage dans une petite bulle ---
        pct_texte = f"{int(percent * 100)}%"
        police_pct = QFont("Segoe UI", max(6, int(side * 0.04)), QFont.Weight.DemiBold)
        painter.setFont(police_pct)
        fm = painter.fontMetrics()
        largeur_bulle = fm.horizontalAdvance(pct_texte) + side * 0.055
        hauteur_bulle = fm.height() * 1.2
        rect_bulle = QRectF(0, 0, largeur_bulle, hauteur_bulle)
        rect_bulle.moveCenter(
            QPointF(rect.center().x(), rect.center().y() + side * 0.255)
        )

        chemin_bulle = QPainterPath()
        chemin_bulle.addRoundedRect(rect_bulle, hauteur_bulle / 2, hauteur_bulle / 2)
        couleur_bulle = QColor(self.theme.progression_debut)
        couleur_bulle.setAlpha(28)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(couleur_bulle))
        painter.drawPath(chemin_bulle)

        painter.setPen(self.theme.sous_texte)
        painter.drawText(rect_bulle, Qt.AlignmentFlag.AlignCenter, pct_texte)

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
        Renvoie 3 arrêts de couleur pour le dégradé conique : la fin de
        l'arc devient progressivement plus saturée/vive à mesure que le
        pourcentage augmente, pour donner une sensation de progression
        "qui s'intensifie" plutôt qu'un dégradé statique.
        """
        debut = self.theme.progression_debut
        cible_fin = self.theme.progression_fin
        fin = CompteurTheme._blend_hsv(debut, cible_fin, 0.35 + 0.65 * percent)
        milieu = CompteurTheme._blend_hsv(debut, fin, 0.5)
        return debut, milieu, fin

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
