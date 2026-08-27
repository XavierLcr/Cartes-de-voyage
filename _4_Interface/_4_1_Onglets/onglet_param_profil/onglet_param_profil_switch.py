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
    QSize,
    pyqtSignal,
)
from PyQt6.QtGui import QPainter, QColor
from _4_Interface._4_3_Icones._4_3_7_soleil_brillant import _dessiner_soleil
from _4_Interface._4_3_Icones._4_3_8_lune_avec_phase import _dessiner_lune

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
            _dessiner_soleil(painter=painter, centre=center, taille=d)
        else:
            _dessiner_lune(
                painter=painter, centre=center, taille=d, phase=phase_lunaire()
            )

    def resizeEvent(self, event):
        # La hauteur idéale d'un switch = moitié de la largeur (forme "pilule")
        hauteur_max = int(max(30, self.width() / 1.1))

        if self.height() > hauteur_max:
            self.setMaximumHeight(hauteur_max)
        else:
            self.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX, on retire la contrainte

        super().resizeEvent(event)
