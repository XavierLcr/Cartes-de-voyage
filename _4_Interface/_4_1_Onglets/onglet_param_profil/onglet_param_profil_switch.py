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
from PyQt6.QtGui import QPainter, QColor, QFont, QPen


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

            # =====================================================
            # Soleil
            # =====================================================

            painter.setPen(QPen(QColor(255, 180, 0), 2))
            painter.setBrush(QColor(255, 220, 0))

            radius = d * 0.18

            # Centre du soleil
            painter.drawEllipse(center, radius, radius)

            # Rayons
            ray_length = d * 0.12

            for angle in range(0, 360, 45):

                rad = math.radians(angle)

                x1 = center.x() + math.cos(rad) * (radius + 2)
                y1 = center.y() + math.sin(rad) * (radius + 2)

                x2 = center.x() + math.cos(rad) * (radius + ray_length)
                y2 = center.y() + math.sin(rad) * (radius + ray_length)

                painter.drawLine(
                    QPointF(x1, y1),
                    QPointF(x2, y2),
                )

        else:

            # =====================================================
            # Lune
            # =====================================================

            painter.setPen(Qt.PenStyle.NoPen)

            moon_color = QColor(230, 230, 230)

            painter.setBrush(moon_color)

            radius = d * 0.24

            # Cercle principal
            painter.drawEllipse(center, radius, radius)

            # Découpe pour former le croissant
            painter.setBrush(QColor(40, 40, 40))

            offset = radius * 0.45

            painter.drawEllipse(
                QPointF(center.x() + offset, center.y() - offset * 0.2),
                radius,
                radius,
            )
