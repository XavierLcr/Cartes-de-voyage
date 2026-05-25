################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_param_profil/                               #
# Onglet du bouton Switch                                                      #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
    QRectF,
    QPointF,
    QSize,
    pyqtSignal,
)
import math
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient


class BoutonSwitch(QWidget):

    stateChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(100, 50))

        self._checked = True
        self._anim_pos = 1.0

        self._animation = QPropertyAnimation(self, b"animPos")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    # ========= API PUBLIQUE =========

    def set_position(self, checked: bool):
        if self._checked == checked:
            return

        self._checked = checked
        self.set_anim_pos(value=checked)

        self._animation.stop()
        self._animation.setStartValue(self._anim_pos)
        self._animation.setEndValue(1.0 if checked else 0.0)
        self._animation.start()

        self.stateChanged.emit(checked)

    def get_position(self) -> bool:
        return self._checked

    # ========= PROPRIÉTÉ ANIMÉE =========

    def get_anim_pos(self):
        return self._anim_pos

    def set_anim_pos(self, value):
        self._anim_pos = value
        self.update()

    animPos = pyqtProperty(float, fget=get_anim_pos, fset=set_anim_pos)

    # ========= EVENTS =========

    def mousePressEvent(self, event):
        self.set_position(checked=not self._checked)

    # ========= PAINT =========

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # =========================================================
        # Fond
        # =========================================================

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(
            QColor(255, 200, 0) if self._checked else QColor(120, 120, 120)
        )

        painter.drawRoundedRect(
            0,
            0,
            self.width(),
            self.height(),
            self.height() / 2,
            self.height() / 2,
        )

        # =========================================================
        # Curseur
        # =========================================================

        margin = 5

        d = self.height() - 2 * margin

        x = margin + (self.width() - d - 2 * margin) * self._anim_pos

        knob_rect = QRectF(x, margin, d, d)

        painter.setBrush(QColor(255, 255, 255) if self._checked else QColor(40, 40, 40))

        painter.drawEllipse(knob_rect)

        # =========================================================
        # Icône
        # =========================================================

        center = knob_rect.center()

        if self._checked:
            self.draw_sun(painter, center, d)
        else:
            self.draw_moon(painter, center, d)

    def draw_sun(self, painter, center, size):

        # =========================================================
        # PARAMÈTRES
        # =========================================================

        radius = size * 0.18

        ray_inner = radius + size * 0.02
        ray_outer = radius + size * 0.14

        # =========================================================
        # GLOW (halo doux)
        # =========================================================

        glow = QRadialGradient(center, size * 0.45)
        glow.setColorAt(0.0, QColor(255, 230, 80, 180))
        glow.setColorAt(0.4, QColor(255, 200, 0, 80))
        glow.setColorAt(1.0, QColor(255, 200, 0, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(center, size * 0.45, size * 0.45)

        # =========================================================
        # RAYONS (douce variation d'épaisseur)
        # =========================================================

        for i in range(12):

            angle = (2 * math.pi / 12) * i

            x1 = center.x() + math.cos(angle) * ray_inner
            y1 = center.y() + math.sin(angle) * ray_inner

            x2 = center.x() + math.cos(angle) * ray_outer
            y2 = center.y() + math.sin(angle) * ray_outer

            pen = QPen(QColor(255, 170, 0, 180), 2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # =========================================================
        # CŒUR DU SOLEIL (gradient + léger relief)
        # =========================================================

        core_gradient = QRadialGradient(center, radius * 1.2)
        core_gradient.setColorAt(0.0, QColor(255, 255, 140))
        core_gradient.setColorAt(0.6, QColor(255, 200, 0))
        core_gradient.setColorAt(1.0, QColor(255, 140, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(core_gradient)
        painter.drawEllipse(center, radius, radius)

        # =========================================================
        # BRILLANCE (petit reflet en haut à gauche)
        # =========================================================

        highlight = QPointF(center.x() - radius * 0.4, center.y() - radius * 0.4)

        painter.setBrush(QColor(255, 255, 255, 120))
        painter.drawEllipse(highlight, radius * 0.35, radius * 0.35)

    def draw_moon(self, painter, center, size):

        moon_color = QColor(230, 230, 230)
        cut_color = QColor(40, 40, 40)

        painter.setPen(Qt.PenStyle.NoPen)

        radius = size * 0.22

        # =========================================================
        # Cercle principal (lune)
        # =========================================================

        painter.setBrush(QBrush(moon_color))
        painter.drawEllipse(center, radius, radius)

        # =========================================================
        # "Découpe" pour croissant
        # =========================================================

        painter.setBrush(QBrush(cut_color))

        offset = radius * 0.45

        # deuxième cercle décalé (crée un croissant propre)
        painter.drawEllipse(
            QPointF(center.x() + offset, center.y() - offset * 0.2), radius, radius
        )
