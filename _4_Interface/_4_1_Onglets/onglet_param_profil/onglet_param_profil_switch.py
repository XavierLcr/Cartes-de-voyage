from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
    QRect,
    QSize,
    pyqtSignal,
)
from PyQt6.QtGui import QPainter, QColor, QFont


class BoutonSwitch(QWidget):

    stateChanged = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(120, 60))

        self._checked = True  # ✅ état logique UNIQUE
        self._anim_pos = 1.0  # détail graphique interne

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

        # Fond
        painter.setBrush(
            QColor(255, 200, 0) if self._checked else QColor(200, 200, 200)
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(
            0, 0, self.width(), self.height(), self.height() // 2, self.height() // 2
        )

        # Curseur
        d = self.height() - 10
        x = 5 + (self.width() - d - 10) * self._anim_pos

        painter.setBrush(QColor(255, 255, 255) if self._checked else QColor(50, 50, 50))
        painter.drawEllipse(int(x), 5, d, d)

        # Emoji
        painter.setFont(QFont("Arial", 20))
        painter.setPen(Qt.GlobalColor.black if self._checked else Qt.GlobalColor.white)
        painter.drawText(
            QRect(int(x), 5, d, d),
            Qt.AlignmentFlag.AlignCenter,
            "☀️" if self._checked else "🌙",
        )
