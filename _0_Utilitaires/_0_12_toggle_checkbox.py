################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# 0.12 – Jolie version d'une QCheckBox                                         #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
    QRectF,
    QSize,
)
from PyQt6.QtGui import QPainter, QColor, QFontMetrics
from PyQt6.QtWidgets import QCheckBox

from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_texte,
    generer_couleur_aleatoire_hex,
)

# 1 -- Toggle plus joli qu'une QCheckBox ---------------------------------------


class ToggleSwitch(QCheckBox):
    """Un toggle switch animé, avec support de setText() comme une QCheckBox normale."""

    def __init__(self, text="", style=1, parent=None, track_width=44, track_height=24):
        super().__init__(parent)
        self._track_width = track_width
        self._track_height = track_height
        self._knob_margin = 3
        self._knob_diameter = track_height - 2 * self._knob_margin
        self._text_spacing = 8  # espace entre le switch et le texte

        # Couleurs (inspirées de la palette de la maquette)
        self._color_off = QColor("#B4B2A9")  # gris neutre
        self._color_on = QColor("#93E5EB")  # bleu accent
        self._color_knob = QColor("#FFFFFF")
        self._color_text = QColor("#2C2C2A")

        # Position du knob, animée entre 0.0 (off) et 1.0 (on)
        self._knob_position = 0.0

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # On neutralise l'indicateur natif (sinon il se superpose à notre
        # piste dessinée à la main) mais on garde le texte natif désactivé
        # nous-mêmes : c'est nous qui le dessinons dans paintEvent.
        self.setStyleSheet("QCheckBox::indicator { width: 0px; height: 0px; }")

        self._animation = QPropertyAnimation(self, b"knob_position", self)
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.stateChanged.connect(self._animate_to_state)

        if text:
            self.setText(text)

        self.set_style(style=style)

    def _animate_to_state(self, state):
        self._animation.stop()
        self._animation.setStartValue(self._knob_position)
        self._animation.setEndValue(1.0 if state else 0.0)
        self._animation.start()

    # --- on intercepte setText pour recalculer la taille du widget ---
    def setText(self, text):
        super().setText(text)
        self.updateGeometry()  # informe le layout que sizeHint() a changé
        self.update()

    # --- propriété animable par QPropertyAnimation ---
    def get_knob_position(self):
        return self._knob_position

    def set_knob_position(self, value):
        self._knob_position = value
        self.update()

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self._animation.stop()
        self.set_knob_position(1.0 if checked else 0.0)

    knob_position = pyqtProperty(float, get_knob_position, set_knob_position)

    # --- taille recommandée : switch + espace + texte, calculé dynamiquement ---
    def sizeHint(self):
        fm = QFontMetrics(self.font())
        text = self.text()
        text_width = fm.horizontalAdvance(text) if text else 0
        extra = self._text_spacing + text_width if text else 0
        width = self._track_width + extra
        height = max(self._track_height, fm.height())
        return QSize(width, height)

    def minimumSizeHint(self):
        return self.sizeHint()

    def set_style(self, style: int, preset={}, teintes=None):

        if style == 0:
            couleur = generer_couleur_aleatoire_hex(
                preset=preset, teintes_autorisees=teintes
            )
        elif style == 1:
            couleur = "#ADCEDB"
        else:
            couleur = "#0C808F"

        texte_temp = str(renvoyer_couleur_texte(style=style, couleur=couleur))
        poignet_temp = str(
            renvoyer_couleur_texte({1: 2, 2: 1}.get(style, 0), couleur=texte_temp)
        )
        self._color_on = QColor(couleur)
        self._color_knob = QColor(poignet_temp)
        self._color_text = QColor(texte_temp)

    # --- rendu personnalisé : piste + knob + texte ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        if not self.isEnabled():
            painter.setOpacity(0.4)

        # La piste est verticalement centrée dans le widget (utile si le
        # texte est plus haut que la piste)
        track_y = (self.height() - self._track_height) / 2

        track_color = self._interpolate_color(
            self._color_off, self._color_on, self._knob_position
        )
        painter.setBrush(track_color)
        track_rect = QRectF(0, track_y, self._track_width, self._track_height)
        radius = self._track_height / 2
        painter.drawRoundedRect(track_rect, radius, radius)

        min_x = self._knob_margin
        max_x = self._track_width - self._knob_diameter - self._knob_margin
        knob_x = min_x + (max_x - min_x) * self._knob_position

        painter.setBrush(self._color_knob)
        painter.drawEllipse(
            QRectF(
                knob_x,
                track_y + self._knob_margin,
                self._knob_diameter,
                self._knob_diameter,
            )
        )

        # Texte dessiné à droite du switch, centré verticalement
        text = self.text()
        if text:
            painter.setPen(self._color_text)
            text_rect = QRectF(
                self._track_width + self._text_spacing,
                0,
                self.width() - self._track_width - self._text_spacing,
                self.height(),
            )
            painter.drawText(
                text_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                text,
            )

    @staticmethod
    def _interpolate_color(c1: QColor, c2: QColor, t: float) -> QColor:
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        return QColor(r, g, b)

    # Le clic doit basculer l'état sur toute la largeur du widget
    # (switch + texte), pas seulement sur la piste
    def hitButton(self, pos):
        return self.contentsRect().contains(pos)
