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
        self._position = 1  # 0 = gauche (nuit), 1 = droite (jour)
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.setDuration(300)  # Durée de l'animation en ms
        self.clicked = True

    def get_position(self):
        return self._position

    def set_position(self, pos):
        self._position = pos
        self.update()  # Redessine le widget

    position = pyqtProperty(float, fget=get_position, fset=set_position)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dessine le fond du switch (sans bordure visible)
        painter.setBrush(
            QColor(200, 200, 200) if not self.clicked else QColor(255, 200, 0)
        )
        painter.setPen(Qt.PenStyle.NoPen)  # Désactive le contour
        painter.drawRoundedRect(
            0, 0, self.width(), self.height(), self.height() // 2, self.height() // 2
        )

        # Dessine le cercle mobile
        circle_diameter = self.height() - 10
        x = 5 + (self.width() - circle_diameter - 10) * self._position
        painter.setBrush(
            QColor(50, 50, 50) if not self.clicked else QColor(255, 255, 255)
        )
        painter.setPen(Qt.PenStyle.NoPen)  # Désactive le contour du cercle
        painter.drawEllipse(int(x), 5, circle_diameter, circle_diameter)

        # Dessine l'emoji
        painter.setFont(QFont("Arial", 20))
        painter.setPen(Qt.GlobalColor.black if self.clicked else Qt.GlobalColor.white)
        painter.drawText(
            QRect(int(x), 5, circle_diameter, circle_diameter),
            Qt.AlignmentFlag.AlignCenter,
            "☀️" if self.clicked else "🌙",
        )

    def mousePressEvent(self, event):
        self.clicked = not self.clicked
        self.animation.setStartValue(0 if self.clicked else 1)
        self.animation.setEndValue(1 if self.clicked else 0)
        self.animation.start()
        self.stateChanged.emit(self.clicked)
