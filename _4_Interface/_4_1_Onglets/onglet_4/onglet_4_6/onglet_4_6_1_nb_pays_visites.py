################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6                                #
# Onglet 4.6.1 – Compteur de pays visités (harmonisé avec le widget 4.6.3)     #
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


import math
from typing import Optional, Tuple

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
    QPolygonF,
    QBrush,
    QPen,
    QColor,
    QFont,
    QRadialGradient,
)
from PyQt6.QtWidgets import QWidget, QSizePolicy, QGraphicsDropShadowEffect

# Ces trois fonctions sont déjà définies dans ton module de thèmes
# (utilisées par ThemeCarte) : à importer depuis leur emplacement réel.
# from .theme_carte import renvoyer_couleur_widget, renvoyer_couleur_texte, renvoyer_couleur_widget_differente


class CompteurTheme:
    """
    Palette de couleurs du widget compteur.

    Reprend la structure de `ThemeCarte` (onglet 4.6.3) : même fond de
    carte, même convention d'ombre, mêmes appels de style — mais avec son
    propre accent turquoise (sarcelle -> cyan), pour se démarquer un peu
    de la carte voisine tout en restant cohérent dans la construction.

    Sur le cadran de vitesse, la zone rouge / le halo de surrégime ne
    doivent PAS suivre la rotation de teinte (`teinte`) réservée à
    l'accent turquoise : un signal de danger doit rester reconnaissable
    comme "rouge" quelle que soit l'instance du widget. `alerte` est donc
    une couleur fixe (deux nuances clair/sombre), indépendante de
    `renvoyer_couleur_widget`.
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
        self.piste.setAlpha(30 if style == 1 else 25)

        # Dégradé de progression / aiguille : turquoise sarcelle -> cyan,
        # un accent propre au compteur plutôt qu'un simple recopiage du
        # badge voisin.
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

        # Halo générique "objectif atteint" (gardé pour compatibilité avec
        # d'éventuels autres usages de CompteurTheme) : reprend le dégradé.
        self.complete = QColor(self.progression_fin)

        # Alerte / zone rouge : couleur fixe, volontairement indépendante
        # de `teinte`. Un rouge un peu plus vif sur fond clair (besoin de
        # contraste sur du blanc), un rouge légèrement éclairci sur fond
        # sombre (besoin de contraste sur le fond quasi noir).
        self.alerte = QColor("#E11D2E" if style != 1 else "#FF6B6B")

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


class CompteurCirculaireWidget(QWidget):
    """
    Compteur de vitesse minimaliste avec aiguille (ex. "128 km/h"),
    présenté dans une carte à coins arrondis identique à celle du widget
    "Nombre de voyages" (même rayon, même ombre, même typographie), pour
    que les deux widgets forment un ensemble cohérent sur le tableau de
    bord.

    Fonctionnalités :
    - Animation fluide et interruptible de l'aiguille (pas de glitch si
      on change la valeur pendant l'animation en cours).
    - Cadran épuré occupant tout l'espace disponible : graduations
      majeures/mineures, zone "zone rouge" (redline) en fin de course.
    - Aiguille fine en forme de losange + moyeu central.
    - Quelques touches décoratives discrètes (reflet, liseré du cadran,
      petits "rivets" aux coins) pour un rendu tableau de bord.
    - Lecture digitale de la valeur dans une bulle discrète (ex. "128
      km/h"), avec le pourcentage affiché juste en dessous.
    - Léger flash lumineux (couleur d'alerte fixe) lorsque la zone rouge
      est atteinte.
    - Entièrement redimensionnable (rien n'est codé en dur en pixels).
    - Thème personnalisable via CompteurTheme.
    """

    def __init__(
        self,
        fonction_traduction,
        value: int = 0,
        maximum: int = 220,
        unite: str = "km/h",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self.fonction_traduction = fonction_traduction
        self._value = 0.0  # valeur animée, affichée à l'écran (position de l'aiguille)
        self.target_value = 0  # dernière valeur demandée (source de vérité)
        self.maximum = max(1, maximum)  # jamais 0, évite la division par zéro
        self.unite = unite
        self.set_langue()
        self.theme = CompteurTheme(style=0)

        # --- géométrie du cadran ---
        self._start_angle = 225.0  # position de l'aiguille à 0 (bas-gauche)
        self._sweep_angle = 270.0  # balayage total jusqu'à la valeur max (sens horaire)
        self._redline_ratio = 0.82  # début de la zone rouge (% de la valeur max)
        self._nb_majeures = self._nb_divisions_lisibles(self.maximum)

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
        self._glow_anim.setDuration(700)
        self._glow_anim.setStartValue(0.0)
        self._glow_anim.setKeyValueAt(0.5, 1.0)
        self._glow_anim.setEndValue(0.0)
        self._glow_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._etait_en_zone_rouge = False

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
        """Met à jour la vitesse affichée (position de l'aiguille), avec ou sans animation."""
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

        entre_en_zone_rouge = (value / self.maximum) >= self._redline_ratio
        if entre_en_zone_rouge and not self._etait_en_zone_rouge:
            self._glow_anim.stop()
            self._glow_anim.start()
        self._etait_en_zone_rouge = entre_en_zone_rouge

    def set_maximum(self, maximum: int) -> None:
        self.maximum = max(1, maximum)
        self._nb_majeures = self._nb_divisions_lisibles(self.maximum)
        self.update()

    def set_unite(self, unite: str) -> None:
        self.unite = unite
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
        rayon_carte = min(24, min(w, h) * 0.18)
        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(rect_carte, rayon_carte, rayon_carte)
        painter.fillPath(chemin_carte, QBrush(self.theme.fond))
        painter.setClipPath(chemin_carte)

        # --- cadran : on utilise (presque) tout l'espace de la carte ---
        side = min(w, h)
        marge = side * 0.10
        rect = QRectF(
            (w - side) / 2 + marge,
            (h - side) / 2 + marge,
            side - 2 * marge,
            side - 2 * marge,
        )
        centre = rect.center()
        rayon_cadran = rect.width() / 2

        # --- touche déco n°1 : petits "rivets" discrets aux coins de la carte ---
        self._dessiner_rivets(painter, rect_carte, side)

        # --- touche déco n°2 : reflet doux façon verre, en haut à gauche du cadran ---
        self._dessiner_reflet(painter, centre, rayon_cadran)

        percent = self._value / self.maximum if self.maximum else 0.0
        percent = max(0.0, min(1.0, percent))

        # --- halo discret quand la zone rouge est atteinte (couleur d'alerte fixe) ---
        if self._glow_opacity > 0:
            glow_color = QColor(self.theme.alerte)
            glow_color.setAlphaF(0.20 * self._glow_opacity)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(glow_color))
            expand = side * 0.05 * self._glow_opacity
            painter.drawEllipse(rect.adjusted(-expand, -expand, expand, expand))

        # --- touche déco n°3 : fin liseré (bezel) juste à l'extérieur du cadran ---
        pen_bezel = QPen(self.theme.piste)
        pen_bezel.setWidthF(max(1.0, side * 0.006))
        couleur_bezel = QColor(self.theme.piste)
        couleur_bezel.setAlpha(140)
        pen_bezel.setColor(couleur_bezel)
        painter.setPen(pen_bezel)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        expand_bezel = side * 0.025
        painter.drawEllipse(
            rect.adjusted(-expand_bezel, -expand_bezel, expand_bezel, expand_bezel)
        )

        # --- arc de piste (neutre) sur tout le balayage ---
        arc_width = max(3.0, side * 0.02)
        pen = QPen(self.theme.piste)
        pen.setWidthF(arc_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect, int(self._start_angle * 16), int(-self._sweep_angle * 16))

        # --- zone rouge en fin de course (couleur d'alerte fixe) ---
        debut_zone_rouge_pct = self._redline_ratio
        angle_debut_zone = self._start_angle - debut_zone_rouge_pct * self._sweep_angle
        angle_span_zone = (1.0 - debut_zone_rouge_pct) * self._sweep_angle
        pen_zone = QPen(QColor(self.theme.alerte))
        pen_zone.setWidthF(arc_width)
        pen_zone.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_zone)
        painter.drawArc(rect, int(angle_debut_zone * 16), int(-angle_span_zone * 16))

        # --- graduations majeures + mineures ---
        self._dessiner_graduations(painter, rect, centre, rayon_cadran, side)

        # --- aiguille ---
        angle_aiguille = self._start_angle - percent * self._sweep_angle
        self._dessiner_aiguille(painter, centre, rayon_cadran, angle_aiguille, side)

        # --- moyeu central ---
        r_moyeu = side * 0.045
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.theme.sous_texte))
        painter.drawEllipse(centre, r_moyeu, r_moyeu)
        painter.setBrush(QBrush(self.theme.fond))
        painter.drawEllipse(centre, r_moyeu * 0.45, r_moyeu * 0.45)

        # --- lecture digitale dans une bulle discrète ---
        valeur_str = f"{int(round(self._value))} {self.unite}"
        police_valeur = QFont(
            "Segoe UI", max(8, int(side * 0.062)), QFont.Weight.DemiBold
        )
        painter.setFont(police_valeur)
        fm = painter.fontMetrics()
        largeur_bulle = fm.horizontalAdvance(valeur_str) + side * 0.07
        hauteur_bulle = fm.height() * 1.25
        rect_bulle = QRectF(0, 0, largeur_bulle, hauteur_bulle)
        rect_bulle.moveCenter(QPointF(centre.x(), centre.y() + rayon_cadran * 0.50))

        chemin_bulle = QPainterPath()
        chemin_bulle.addRoundedRect(rect_bulle, hauteur_bulle / 2, hauteur_bulle / 2)
        couleur_bulle = QColor(self.theme.progression_debut)
        couleur_bulle.setAlpha(28)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(couleur_bulle))
        painter.drawPath(chemin_bulle)

        painter.setPen(self.theme.texte)
        painter.drawText(rect_bulle, Qt.AlignmentFlag.AlignCenter, valeur_str)

        # --- légende + pourcentage, juste sous la bulle ---
        painter.setPen(self.theme.sous_texte)
        police_etiquette = QFont("Segoe UI", max(7, int(side * 0.042)))
        painter.setFont(police_etiquette)
        texte_legende = f"{self.label_text} · {int(round(percent * 100))} %"
        rect_etiquette = QRectF(rect_bulle)
        rect_etiquette.moveCenter(
            QPointF(centre.x(), rect_bulle.center().y() + hauteur_bulle * 1.05)
        )
        painter.drawText(rect_etiquette, Qt.AlignmentFlag.AlignCenter, texte_legende)

    def _dessiner_rivets(
        self, painter: QPainter, rect_carte: QRectF, side: float
    ) -> None:
        """Quatre petits repères discrets aux coins de la carte, pour une touche 'panneau'."""
        r_rivet = max(1.2, side * 0.010)
        pad = side * 0.075
        couleur = QColor(self.theme.piste)
        couleur.setAlpha(110)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(couleur))
        for pos in (
            QPointF(rect_carte.left() + pad, rect_carte.top() + pad),
            QPointF(rect_carte.right() - pad, rect_carte.top() + pad),
            QPointF(rect_carte.left() + pad, rect_carte.bottom() - pad),
            QPointF(rect_carte.right() - pad, rect_carte.bottom() - pad),
        ):
            painter.drawEllipse(pos, r_rivet, r_rivet)

    def _dessiner_reflet(
        self, painter: QPainter, centre: QPointF, rayon_cadran: float
    ) -> None:
        """Reflet doux façon verre bombé, très subtil, en haut à gauche du cadran."""
        foyer = QPointF(
            centre.x() - rayon_cadran * 0.35, centre.y() - rayon_cadran * 0.45
        )
        gradient = QRadialGradient(foyer, rayon_cadran * 1.15)
        couleur_centre = QColor("#FFFFFF")
        couleur_centre.setAlphaF(0.06)
        couleur_bord = QColor("#FFFFFF")
        couleur_bord.setAlphaF(0.0)
        gradient.setColorAt(0.0, couleur_centre)
        gradient.setColorAt(1.0, couleur_bord)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        rect_reflet = QRectF(
            centre.x() - rayon_cadran,
            centre.y() - rayon_cadran,
            rayon_cadran * 2,
            rayon_cadran * 2,
        )
        painter.drawEllipse(rect_reflet)

    def _dessiner_graduations(
        self,
        painter: QPainter,
        rect: QRectF,
        centre: QPointF,
        rayon_cadran: float,
        side: float,
    ) -> None:
        """Dessine les graduations majeures (avec chiffres) et mineures du cadran."""
        nb_majeures = self._nb_majeures
        nb_mineures_par_intervalle = 4

        police_chiffres = QFont("Segoe UI", max(6, int(side * 0.040)))
        painter.setFont(police_chiffres)
        fm = painter.fontMetrics()

        for i in range(nb_majeures + 1):
            pct = i / nb_majeures
            angle = self._start_angle - pct * self._sweep_angle
            en_zone_rouge = pct >= self._redline_ratio

            couleur = (
                QColor(self.theme.alerte) if en_zone_rouge else QColor(self.theme.texte)
            )
            pen = QPen(couleur)
            pen.setWidthF(max(1.5, side * 0.012))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            p_ext = self._point_polaire(centre, angle, rayon_cadran)
            p_int = self._point_polaire(centre, angle, rayon_cadran * 0.87)
            painter.drawLine(p_int, p_ext)

            # chiffre correspondant à la graduation
            valeur_grad = int(round(pct * self.maximum))
            p_texte = self._point_polaire(centre, angle, rayon_cadran * 0.72)
            painter.setPen(couleur)
            texte_rect = QRectF(
                0, 0, fm.horizontalAdvance(str(valeur_grad)) + 6, fm.height()
            )
            texte_rect.moveCenter(p_texte)
            painter.drawText(texte_rect, Qt.AlignmentFlag.AlignCenter, str(valeur_grad))

            # graduations mineures entre deux majeures
            if i < nb_majeures:
                pen_mineure = QPen(self.theme.piste)
                pen_mineure.setWidthF(max(1.0, side * 0.006))
                pen_mineure.setCapStyle(Qt.PenCapStyle.RoundCap)
                for j in range(1, nb_mineures_par_intervalle):
                    pct_m = pct + (j / nb_mineures_par_intervalle) * (1 / nb_majeures)
                    angle_m = self._start_angle - pct_m * self._sweep_angle
                    couleur_m = (
                        QColor(self.theme.alerte)
                        if pct_m >= self._redline_ratio
                        else self.theme.piste
                    )
                    pen_mineure.setColor(couleur_m)
                    painter.setPen(pen_mineure)
                    p_ext_m = self._point_polaire(centre, angle_m, rayon_cadran)
                    p_int_m = self._point_polaire(centre, angle_m, rayon_cadran * 0.93)
                    painter.drawLine(p_int_m, p_ext_m)

    def _dessiner_aiguille(
        self,
        painter: QPainter,
        centre: QPointF,
        rayon_cadran: float,
        angle_deg: float,
        side: float,
    ) -> None:
        """Dessine une aiguille fine en forme de losange, avec une courte contre-pointe."""
        longueur = rayon_cadran * 0.80
        largeur = side * 0.018
        longueur_queue = rayon_cadran * 0.14

        pointe = self._point_polaire(centre, angle_deg, longueur)
        queue = self._point_polaire(centre, angle_deg + 180, longueur_queue)
        gauche = self._point_polaire(centre, angle_deg + 90, largeur)
        droite = self._point_polaire(centre, angle_deg - 90, largeur)

        aiguille = QPolygonF([pointe, gauche, queue, droite])

        couleur_aiguille = (
            QColor(self.theme.alerte)
            if (self._value / self.maximum if self.maximum else 0)
            >= self._redline_ratio
            else QColor(self.theme.progression_fin)
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(couleur_aiguille))
        painter.drawPolygon(aiguille)

    @staticmethod
    def _point_polaire(centre: QPointF, angle_deg: float, rayon: float) -> QPointF:
        """Point sur un cercle de rayon `rayon` autour de `centre`, à l'angle `angle_deg`
        (convention mathématique standard : 0° = droite, 90° = haut, sens antihoraire).
        """
        angle_rad = math.radians(angle_deg)
        return QPointF(
            centre.x() + rayon * math.cos(angle_rad),
            centre.y() - rayon * math.sin(angle_rad),
        )

    @staticmethod
    def _nb_divisions_lisibles(maximum: int) -> int:
        """Choisit un nombre de graduations majeures qui donne des paliers ronds
        (ex. par 10, 20, 25, 50...) plutôt qu'une division arbitraire du maximum."""
        for candidat in (10, 20, 25, 50, 100, 200, 250, 500):
            if maximum % candidat == 0 and 6 <= maximum // candidat <= 12:
                return maximum // candidat
        # repli : entre 6 et 12 divisions, la plus proche de 10
        for n in (10, 8, 12, 6, 11, 9, 7):
            if maximum % n == 0:
                return n
        return 10

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
