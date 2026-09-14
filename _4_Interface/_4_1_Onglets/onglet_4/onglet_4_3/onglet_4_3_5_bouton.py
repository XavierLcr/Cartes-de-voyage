################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_3                                #
# Onglet 4.3.5 – Bouton des recommandations                                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import (
    Qt,
    QRectF,
    QPointF,
    QVariantAnimation,
    QEasingCurve,
)

from PyQt6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
    QRadialGradient,
)

from PyQt6.QtWidgets import (
    QPushButton,
    QSizePolicy,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    _trouver_police_disponible,
)

# 1 -- Bouton de recommandation ------------------------------------------------


class BoutonRecommandation(QPushButton):
    """
    Bouton inspiré des commandes anciennes de gare :
    cadre en laiton, plaque émaillée sombre et léger relief.
    """

    def __init__(
        self,
        fonction_traduction,
        parent=None,
    ):
        super().__init__(parent)

        self.fonction_traduction = fonction_traduction

        self.setMinimumHeight(54)
        self.setMaximumHeight(64)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setFlat(True)

        # On dessine entièrement le bouton nous-mêmes
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)

        self.police = _trouver_police_disponible(
            [
                "CormorantGaramond",
                "Book Antiqua",
                "Georgia",
                "Palatino Linotype",
                "Segoe UI",
            ]
        )

        # État graphique
        self._survol = 0.0
        self._enfonce = False

        # Animation du survol
        self._animation_survol = QVariantAnimation(self)

        self._animation_survol.setDuration(180)
        self._animation_survol.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._animation_survol.valueChanged.connect(self._mettre_a_jour_survol)

    # --------------------------------------------------------------------------
    # Langue
    # --------------------------------------------------------------------------

    def set_langue(self):

        self.setText(self.fonction_traduction("bouton_recommandations"))
        self.setToolTip(self.fonction_traduction("recommandation_passeport"))

    # --------------------------------------------------------------------------
    # Animation
    # --------------------------------------------------------------------------

    def _mettre_a_jour_survol(self, valeur):
        self._survol = float(valeur)
        self.update()

    def _animer_survol(self, destination: float):

        self._animation_survol.stop()

        self._animation_survol.setStartValue(self._survol)

        self._animation_survol.setEndValue(destination)

        self._animation_survol.start()

    # --------------------------------------------------------------------------
    # Événements souris
    # --------------------------------------------------------------------------

    def enterEvent(self, event):
        self._animer_survol(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animer_survol(0.0)
        super().leaveEvent(event)

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            self._enfonce = True
            self.update()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        self._enfonce = False
        self.update()

        super().mouseReleaseEvent(event)

    # --------------------------------------------------------------------------
    # Dessin
    # --------------------------------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()

        decalage_appui = 2 if self._enfonce else 0

        rect_exterieur = QRectF(
            4,
            4 + decalage_appui,
            w - 8,
            h - 10,
        )

        # ----------------------------------------------------------------------
        # Ombre
        # ----------------------------------------------------------------------

        if not self._enfonce:

            rect_ombre = QRectF(rect_exterieur)

            rect_ombre.translate(
                0,
                4,
            )

            ombre = QColor("#000000")
            ombre.setAlpha(65)

            painter.setPen(Qt.PenStyle.NoPen)

            painter.setBrush(ombre)

            painter.drawRoundedRect(
                rect_ombre,
                8,
                8,
            )

        # ----------------------------------------------------------------------
        # Cadre en laiton
        # ----------------------------------------------------------------------

        couleur_claire = QColor(
            188 + int(25 * self._survol),
            145 + int(22 * self._survol),
            69 + int(15 * self._survol),
        )

        couleur_milieu = QColor(
            133 + int(18 * self._survol),
            94 + int(15 * self._survol),
            38,
        )

        couleur_sombre = QColor(
            75,
            49,
            19,
        )

        degrade_laiton = QLinearGradient(
            rect_exterieur.topLeft(),
            rect_exterieur.bottomLeft(),
        )

        degrade_laiton.setColorAt(
            0.00,
            couleur_claire,
        )

        degrade_laiton.setColorAt(
            0.22,
            couleur_milieu,
        )

        degrade_laiton.setColorAt(
            0.50,
            QColor("#D0A450"),
        )

        degrade_laiton.setColorAt(
            0.78,
            couleur_milieu,
        )

        degrade_laiton.setColorAt(
            1.00,
            couleur_sombre,
        )

        painter.setBrush(degrade_laiton)

        painter.setPen(
            QPen(
                QColor("#533819"),
                1.2,
            )
        )

        painter.drawRoundedRect(
            rect_exterieur,
            8,
            8,
        )

        # ----------------------------------------------------------------------
        # Plaque émaillée centrale
        # ----------------------------------------------------------------------

        rect_plaque = rect_exterieur.adjusted(
            7,
            6,
            -7,
            -6,
        )

        degrade_plaque = QLinearGradient(
            rect_plaque.topLeft(),
            rect_plaque.bottomLeft(),
        )

        if self._enfonce:

            degrade_plaque.setColorAt(
                0.0,
                QColor("#182D29"),
            )

            degrade_plaque.setColorAt(
                1.0,
                QColor("#0D1E1C"),
            )

        else:

            degrade_plaque.setColorAt(
                0.0,
                QColor("#294942"),
            )

            degrade_plaque.setColorAt(
                0.45,
                QColor("#1D3A35"),
            )

            degrade_plaque.setColorAt(
                1.0,
                QColor("#122A27"),
            )

        painter.setBrush(degrade_plaque)

        painter.setPen(
            QPen(
                QColor("#10221F"),
                1.0,
            )
        )

        painter.drawRoundedRect(
            rect_plaque,
            5,
            5,
        )

        # ----------------------------------------------------------------------
        # Reflet sur l'émail
        # ----------------------------------------------------------------------

        couleur_reflet = QColor("#FFFFFF")

        couleur_reflet.setAlpha(int(20 + 20 * self._survol))

        reflet = QLinearGradient(
            rect_plaque.topLeft(),
            rect_plaque.bottomLeft(),
        )

        transparent = QColor("#FFFFFF")
        transparent.setAlpha(0)

        reflet.setColorAt(
            0.0,
            couleur_reflet,
        )

        reflet.setColorAt(
            0.35,
            transparent,
        )

        reflet.setColorAt(
            1.0,
            transparent,
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(reflet)

        painter.drawRoundedRect(
            rect_plaque.adjusted(
                2,
                2,
                -2,
                -2,
            ),
            4,
            4,
        )

        # ----------------------------------------------------------------------
        # Rivets
        # ----------------------------------------------------------------------

        rayon_rivet = max(
            2.0,
            h * 0.045,
        )

        positions_rivets = (
            QPointF(
                rect_exterieur.left() + 11,
                rect_exterieur.center().y(),
            ),
            QPointF(
                rect_exterieur.right() - 11,
                rect_exterieur.center().y(),
            ),
        )

        for centre in positions_rivets:

            degrade_rivet = QRadialGradient(
                centre,
                rayon_rivet,
                QPointF(
                    centre.x() - rayon_rivet * 0.3,
                    centre.y() - rayon_rivet * 0.3,
                ),
            )

            degrade_rivet.setColorAt(
                0.0,
                QColor("#F0D58E"),
            )

            degrade_rivet.setColorAt(
                0.45,
                QColor("#B0863F"),
            )

            degrade_rivet.setColorAt(
                1.0,
                QColor("#624318"),
            )

            painter.setBrush(degrade_rivet)

            painter.setPen(
                QPen(
                    QColor("#4B3215"),
                    0.7,
                )
            )

            painter.drawEllipse(
                centre,
                rayon_rivet,
                rayon_rivet,
            )

            # Fente de vis
            painter.setPen(
                QPen(
                    QColor("#58411F"),
                    0.7,
                )
            )

            painter.drawLine(
                QPointF(
                    centre.x() - rayon_rivet * 0.45,
                    centre.y(),
                ),
                QPointF(
                    centre.x() + rayon_rivet * 0.45,
                    centre.y(),
                ),
            )

        # ----------------------------------------------------------------------
        # Texte
        # ----------------------------------------------------------------------

        taille_police = max(
            10,
            int(h * 0.24),
        )

        painter.setFont(
            QFont(
                self.police,
                taille_police,
                QFont.Weight.DemiBold,
            )
        )

        # Petite ombre gravée
        couleur_ombre_texte = QColor("#000000")
        couleur_ombre_texte.setAlpha(90)

        painter.setPen(couleur_ombre_texte)

        painter.drawText(
            rect_plaque.translated(
                0,
                1,
            ).adjusted(
                22,
                0,
                -22,
                0,
            ),
            Qt.AlignmentFlag.AlignCenter,
            self.text(),
        )

        # Texte crème
        couleur_texte = QColor("#EFE4C6")

        if self._enfonce:
            couleur_texte = QColor("#D7C9A7")

        painter.setPen(couleur_texte)

        painter.drawText(
            rect_plaque.adjusted(
                22,
                0,
                -22,
                0,
            ),
            Qt.AlignmentFlag.AlignCenter,
            self.text(),
        )
