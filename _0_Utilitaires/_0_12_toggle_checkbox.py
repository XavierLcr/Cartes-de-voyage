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
    QPointF,
)
from PyQt6.QtGui import QPainter, QColor, QFontMetrics
from PyQt6.QtWidgets import QCheckBox

from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_texte,
    generer_couleur_aleatoire_hex,
    transformer_couleur_texte,
)

# 1 -- Toggle plus joli qu'une QCheckBox ---------------------------------------


class ToggleSwitch(QCheckBox):
    """Un toggle switch animé avec support du texte et d'une icône."""

    def __init__(
        self,
        text="",
        style=1,
        parent=None,
        track_width=44,
        track_height=24,
        fonction_dessin=None,
        taille_icone=20,
    ):
        super().__init__(parent)

        self._track_width = track_width
        self._track_height = track_height

        self._knob_margin = 3
        self._knob_diameter = track_height - 2 * self._knob_margin

        self._text_spacing = 8
        self._icon_spacing = 8

        # ------------------------------------------------------------------
        # Icône dessinée directement
        # ------------------------------------------------------------------

        self._fonction_dessin = fonction_dessin
        self._taille_icone = taille_icone

        # ------------------------------------------------------------------
        # Couleurs
        # ------------------------------------------------------------------

        self._color_off = QColor("#B4B2A9")
        self._color_on = QColor("#93E5EB")
        self._color_knob = QColor("#FFFFFF")
        self._color_text = QColor("#2C2C2A")

        # ------------------------------------------------------------------
        # Position du bouton
        # ------------------------------------------------------------------

        self._knob_position = 0.0

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("QCheckBox::indicator { width: 0px; height: 0px; }")

        # ------------------------------------------------------------------
        # Animation
        # ------------------------------------------------------------------

        self._animation = QPropertyAnimation(
            self,
            b"knob_position",
            self,
        )

        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.stateChanged.connect(self._animate_to_state)

        if text:
            self.setText(text)

        self.set_style(style=style)

    # =========================================================================
    # État / animation
    # =========================================================================

    def _animate_to_state(self, state):

        self._animation.stop()

        self._animation.setStartValue(self._knob_position)

        self._animation.setEndValue(1.0 if state else 0.0)

        self._animation.start()

    def get_knob_position(self):
        return self._knob_position

    def set_knob_position(self, value):

        self._knob_position = value
        self.update()

    knob_position = pyqtProperty(
        float,
        get_knob_position,
        set_knob_position,
    )

    def setChecked(self, checked: bool):

        super().setChecked(checked)

        self._animation.stop()

        self.set_knob_position(1.0 if checked else 0.0)

    # =========================================================================
    # Texte
    # =========================================================================

    def setText(self, text):

        super().setText(text)

        self.updateGeometry()
        self.update()

    # =========================================================================
    # Icône vectorielle
    # =========================================================================

    def setFonctionDessin(
        self,
        fonction_dessin,
        taille_icone=None,
    ):
        """
        Définit une fonction de dessin vectoriel.

        Si fonction_dessin vaut None, le ToggleSwitch revient au système
        classique setIcon().
        """

        self._fonction_dessin = fonction_dessin

        if taille_icone is not None:
            self._taille_icone = taille_icone

        self.updateGeometry()
        self.update()

    # =========================================================================
    # Taille
    # =========================================================================

    def sizeHint(self):

        fm = QFontMetrics(self.font())

        text = self.text()

        text_width = fm.horizontalAdvance(text) if text else 0

        # ------------------------------------------------------------------
        # Taille de l'icône
        # ------------------------------------------------------------------

        icon_width = 0
        icon_height = 0

        # Priorité à l'icône vectorielle
        if self._fonction_dessin is not None:

            icon_width = self._taille_icone
            icon_height = self._taille_icone

        # Sinon fallback sur QIcon
        elif not self.icon().isNull():

            icon_size = self.iconSize()

            icon_width = icon_size.width()
            icon_height = icon_size.height()

        # ------------------------------------------------------------------
        # Partie située après le switch
        #
        # [switch] [icône] [texte]
        # ------------------------------------------------------------------

        contenu_width = 0

        if icon_width:
            contenu_width += icon_width

        if icon_width and text_width:
            contenu_width += self._icon_spacing

        if text_width:
            contenu_width += text_width

        if contenu_width:
            contenu_width += self._text_spacing

        width = self._track_width + contenu_width

        height = max(
            self._track_height,
            fm.height(),
            icon_height,
        )

        return QSize(
            width,
            height,
        )

    def minimumSizeHint(self):
        return self.sizeHint()

    # =========================================================================
    # Style
    # =========================================================================

    def set_style(
        self,
        style: int,
        preset={},
        teintes=None,
    ):

        if style == 0:

            couleur = generer_couleur_aleatoire_hex(
                preset=preset,
                teintes_autorisees=teintes,
            )

        elif style == 1:

            couleur = "#ADCEDB"

        else:

            couleur = "#0C808F"

        texte_temp = str(
            renvoyer_couleur_texte(
                style=style,
                couleur=couleur,
            )
        )

        poignee_temp = {
            1: "#FFFFFF",
            2: transformer_couleur_texte(bg_color="#000000"),
            0: generer_couleur_aleatoire_hex(
                preset=preset,
                teintes_autorisees=teintes,
            ),
        }.get(
            style,
            "#FFFFFF",
        )

        self._color_on = QColor(couleur)
        self._color_knob = QColor(poignee_temp)
        self._color_text = QColor(texte_temp)

        self.update()

    # =========================================================================
    # Dessin
    # =========================================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        painter.setRenderHint(
            QPainter.RenderHint.TextAntialiasing,
            True,
        )

        painter.setPen(Qt.PenStyle.NoPen)

        # ------------------------------------------------------------------
        # Désactivé
        # ------------------------------------------------------------------

        if not self.isEnabled():
            painter.setOpacity(0.4)

        # ------------------------------------------------------------------
        # Switch
        # ------------------------------------------------------------------

        track_y = (self.height() - self._track_height) / 2

        track_color = self._interpolate_color(
            self._color_off,
            self._color_on,
            self._knob_position,
        )

        painter.setBrush(track_color)

        track_rect = QRectF(
            0,
            track_y,
            self._track_width,
            self._track_height,
        )

        radius = self._track_height / 2

        painter.drawRoundedRect(
            track_rect,
            radius,
            radius,
        )

        # ------------------------------------------------------------------
        # Knob
        # ------------------------------------------------------------------

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

        # ------------------------------------------------------------------
        # Contenu : icône + texte
        # ------------------------------------------------------------------

        x = self._track_width

        has_vector_icon = self._fonction_dessin is not None

        has_qicon = not has_vector_icon and not self.icon().isNull()

        has_icon = has_vector_icon or has_qicon

        has_text = bool(self.text())

        if has_icon or has_text:
            x += self._text_spacing

        # ------------------------------------------------------------------
        # Icône vectorielle
        # ------------------------------------------------------------------

        if has_vector_icon:

            taille = self._taille_icone

            centre = QPointF(
                x + taille / 2,
                self.height() / 2,
            )

            painter.save()

            self._fonction_dessin(
                painter,
                centre,
                taille,
            )

            painter.restore()

            x += taille

            if has_text:
                x += self._icon_spacing

        # ------------------------------------------------------------------
        # Ancien système QIcon
        # ------------------------------------------------------------------

        elif has_qicon:

            icon_size = self.iconSize()

            icon_y = (self.height() - icon_size.height()) / 2

            self.icon().paint(
                painter,
                int(x),
                int(icon_y),
                icon_size.width(),
                icon_size.height(),
            )

            x += icon_size.width()

            if has_text:
                x += self._icon_spacing

        # ------------------------------------------------------------------
        # Texte
        # ------------------------------------------------------------------

        if has_text:

            painter.setPen(self._color_text)

            text_rect = QRectF(
                x,
                0,
                self.width() - x,
                self.height(),
            )

            painter.drawText(
                text_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                self.text(),
            )

    # =========================================================================
    # Utilitaires
    # =========================================================================

    @staticmethod
    def _interpolate_color(
        c1: QColor,
        c2: QColor,
        t: float,
    ) -> QColor:

        r = int(c1.red() + (c2.red() - c1.red()) * t)

        g = int(c1.green() + (c2.green() - c1.green()) * t)

        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)

        return QColor(
            r,
            g,
            b,
        )

    # =========================================================================
    # Clic
    # =========================================================================

    def hitButton(self, pos):
        return self.contentsRect().contains(pos)
