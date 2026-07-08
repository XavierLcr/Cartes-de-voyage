################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6                                #
# Onglet 4.6.2 – Compteur de pays visistés                                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
from typing import Optional, Tuple

from PyQt6.QtCore import (
    QEasingCurve,
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
    """Palette de couleurs du widget compteur, générée depuis le style de l'appli."""

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
        # Fond : identique au fond général de l'appli
        self.background = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#E5E7EC",
                sombre="#07215E",
            )
        )
        self.text = QColor(
            str(renvoyer_couleur_texte(style=style, couleur=self.background.name()))
            if style != 1
            else "#07215E"
        )

        # Piste : dérivée du texte, très diluée
        self.track = QColor(self.text)
        self.track.setAlpha(30 if style == "clair" else 25)

        # Dégradé de progression
        self.progress_start = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#3F51B5",
                sombre="#3F51B5",
            )
        )
        self.progress_end = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#1696A9",
                sombre="#26C6DA",
                reference=self.progress_start.name(),
                essais=limite_essais,
            )
        )

        # Sous-texte
        self.subtext = QColor(self.text)
        self.subtext.setAlpha(140)

        # Halo "objectif atteint"
        self.complete = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#26C6DA",
                sombre="#26C6DA",
            )
        )


# 2 -- Classe du compteur  -----------------------------------------------------


class CompteurCirculaireWidget(QWidget):
    """
    Compteur circulaire animé (ex. "Pays visités : 42 / 200").

    Fonctionnalités :
    - Animation fluide et interruptible (pas de glitch si on change la
      valeur pendant l'animation en cours).
    - Dégradé conique sur l'arc de progression, dont la teinte évolue avec
      le pourcentage atteint.
    - Ombre portée douce + halo pulsé lorsque l'objectif est atteint.
    - Entièrement redimensionnable (rien n'est codé en dur en pixels).
    - Thème personnalisable via CompteurTheme.
    """

    def __init__(
        self,
        fonction_traduction,
        value: int = 0,
        maximum: int = 200,
        theme: Optional[CompteurTheme] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self.fonction_traduction = fonction_traduction
        self._value = 0.0  # valeur animée, affichée à l'écran
        self.target_value = 0  # dernière valeur demandée (source de vérité)
        self.maximum = max(1, maximum)  # jamais 0, évite la division par zéro
        self.set_langue()
        self.theme = CompteurTheme(style=0)

        self._arc_width = 14
        self._start_angle = 90  # l'arc démarre en haut du cercle
        self._glow_opacity = 0.0

        self.setMinimumSize(140, 140)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(35)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

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

        side = min(self.width(), self.height())
        margin = self._arc_width / 2 + 6
        rect = QRectF(
            (self.width() - side) / 2 + margin,
            (self.height() - side) / 2 + margin,
            side - 2 * margin,
            side - 2 * margin,
        )

        percent = self._value / self.maximum if self.maximum else 0.0
        percent = max(0.0, min(1.0, percent))

        # --- disque de fond ---
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.theme.background))
        painter.drawEllipse(
            rect.adjusted(-margin * 0.4, -margin * 0.4, margin * 0.4, margin * 0.4)
        )

        # --- halo pulsé quand l'objectif est atteint ---
        if self._glow_opacity > 0:
            glow_color = QColor(self.theme.complete)
            glow_color.setAlphaF(0.35 * self._glow_opacity)
            painter.setBrush(QBrush(glow_color))
            expand = 10 * self._glow_opacity
            painter.drawEllipse(rect.adjusted(-expand, -expand, expand, expand))

        # --- piste (arc de fond, toujours complet) ---
        pen = QPen(self.theme.track)
        pen.setWidth(self._arc_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect, 0, 360 * 16)

        # --- arc de progression, dégradé conique ---
        if percent > 0:
            gradient = QConicalGradient(rect.center(), self._start_angle)
            c1, c2 = self._interpolated_colors(percent)
            gradient.setColorAt(0.0, c1)
            gradient.setColorAt(1.0, c2)

            pen = QPen(QBrush(gradient), self._arc_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            span = int(360 * percent * 16)
            painter.drawArc(rect, self._start_angle * 16, -span)

        # --- valeur centrale ---
        painter.setPen(self.theme.text)
        value_font = QFont("Segoe UI", max(10, int(side * 0.16)), QFont.Weight.Bold)
        painter.setFont(value_font)
        value_str = f"{int(round(self._value))}"
        value_rect = rect.adjusted(0, -side * 0.05, 0, -side * 0.05)
        painter.drawText(value_rect, Qt.AlignmentFlag.AlignCenter, value_str)

        # --- légende ---
        painter.setPen(self.theme.subtext)
        label_font = QFont("Segoe UI", max(7, int(side * 0.06)))
        painter.setFont(label_font)
        label_rect = rect.adjusted(0, side * 0.22, 0, side * 0.22)
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, self.label_text)

        # --- pourcentage discret ---
        painter.setPen(self.theme.subtext)
        pct_font = QFont("Segoe UI", max(6, int(side * 0.045)))
        painter.setFont(pct_font)
        pct_rect = rect.adjusted(0, side * 0.32, 0, side * 0.32)
        painter.drawText(
            pct_rect, Qt.AlignmentFlag.AlignCenter, f"{int(percent * 100)}%"
        )

    def _interpolated_colors(self, percent: float) -> Tuple[QColor, QColor]:
        """Fait évoluer la teinte du dégradé selon la progression."""
        start = self.theme.progress_start
        end = self.theme.progress_end
        mixed = QColor(
            int(start.red() + (end.red() - start.red()) * percent),
            int(start.green() + (end.green() - start.green()) * percent),
            int(start.blue() + (end.blue() - start.blue()) * percent),
        )
        return start, mixed

    def set_langue(self):
        self.label_text = self.fonction_traduction("granularite_pays_visites")
        self.update()

    def set_style(self, style, nuances, teintes):

        self.theme = CompteurTheme(
            style=style, nuances=nuances, teinte=teintes, limite_essais=20
        )
        self.update()
