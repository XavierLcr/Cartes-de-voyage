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
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient

from _0_Utilitaires._0_1_fonctions_utiles_gen import phase_lunaire


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
            self.draw_moon(painter, center, d, phase=phase_lunaire())

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

    def draw_moon(self, painter, center, size, phase=0.25):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        import math

        radius = size * 0.3

        # =========================================================
        # 1. Base lune (gradient doux = essentiel)
        # =========================================================
        base = QRadialGradient(
            center - QPointF(radius * 0.2, radius * 0.2), radius * 1.2
        )

        base.setColorAt(0.0, QColor(255, 255, 255))
        base.setColorAt(0.6, QColor(235, 235, 240))
        base.setColorAt(1.0, QColor(190, 190, 200))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(base)
        painter.drawEllipse(center, radius, radius)

        # =========================================================
        # 2. Ombre de phase (propre et douce)
        # =========================================================
        illum = (1 - math.cos(2 * math.pi * phase)) / 2

        # direction du croissant
        direction = 1 if phase < 0.5 else -1

        offset = radius * (1 - illum) * 1.8 * direction

        shadow = QRadialGradient(center + QPointF(offset, 0), radius * 1.2)

        shadow.setColorAt(0.0, QColor(0, 0, 0, 0))
        shadow.setColorAt(0.6, QColor(10, 10, 20, 120))
        shadow.setColorAt(1.0, QColor(0, 0, 0, 255))

        painter.setBrush(shadow)
        painter.drawEllipse(center, radius, radius)

        # =========================================================
        # 3. Cratères subtils (très léger)
        # =========================================================
        painter.setBrush(QColor(180, 180, 190, 40))

        import random

        random.seed(3)

        for _ in range(8):
            angle = random.uniform(0, 6.28)
            dist = random.uniform(0, radius * 0.7)

            x = center.x() + math.cos(angle) * dist
            y = center.y() + math.sin(angle) * dist

            r = random.uniform(radius * 0.05, radius * 0.12)

            painter.drawEllipse(QPointF(x, y), r, r)

        # =========================================================
        # 4. Glow léger (donne le côté “lune lumineuse”)
        # =========================================================
        glow = QRadialGradient(center, radius * 1.6)
        glow.setColorAt(0.7, QColor(255, 255, 255, 0))
        glow.setColorAt(1.0, QColor(200, 200, 255, 30))

        painter.setBrush(glow)
        painter.drawEllipse(center, radius * 1.05, radius * 1.05)
