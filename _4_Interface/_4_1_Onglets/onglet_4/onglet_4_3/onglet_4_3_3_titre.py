################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_3                                #
# Onglet 4.3.3 – Suggestions de nouvelles destinations – Titre                 #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QFont,
    QLinearGradient,
    QRadialGradient,
    QPen,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    _trouver_police_disponible,
)

# 1 -- Classe de titre des recommandations -------------------------------------


class TitreRecommandations(QWidget):
    """
    Panneau de gare ancien composé d'un cadre en bois et d'une plaque
    métallique émaillée.
    """

    def __init__(
        self,
        texte: str,
        parent=None,
    ):
        super().__init__(parent)

        self.texte = texte

        self.setMinimumHeight(86)
        self.setMaximumHeight(96)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.police = _trouver_police_disponible(
            [
                "CormorantGaramond",
                "Book Antiqua",
                "Georgia",
                "Palatino Linotype",
                "Times New Roman",
            ]
        )

    # --------------------------------------------------------------------------
    # Dessin
    # --------------------------------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()

        # Dimensions générales
        rect_ombre = QRectF(
            10,
            12,
            w - 20,
            h - 20,
        )

        rect_cadre = QRectF(
            10,
            8,
            w - 20,
            h - 20,
        )

        epaisseur_cadre = 9

        rect_plaque = rect_cadre.adjusted(
            epaisseur_cadre,
            epaisseur_cadre,
            -epaisseur_cadre,
            -epaisseur_cadre,
        )

        # ----------------------------------------------------------------------
        # Ombre sous le panneau
        # ----------------------------------------------------------------------

        couleur_ombre = QColor("#000000")
        couleur_ombre.setAlpha(55)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(couleur_ombre)

        painter.drawRoundedRect(
            rect_ombre,
            5,
            5,
        )

        # ----------------------------------------------------------------------
        # Cadre en bois
        # ----------------------------------------------------------------------

        degrade_bois = QLinearGradient(
            rect_cadre.topLeft(),
            rect_cadre.bottomLeft(),
        )

        degrade_bois.setColorAt(0.00, QColor("#8B633F"))
        degrade_bois.setColorAt(0.20, QColor("#6F482A"))
        degrade_bois.setColorAt(0.55, QColor("#805738"))
        degrade_bois.setColorAt(0.82, QColor("#59381F"))
        degrade_bois.setColorAt(1.00, QColor("#755033"))

        painter.setBrush(degrade_bois)

        painter.setPen(
            QPen(
                QColor("#3D2819"),
                1.4,
            )
        )

        painter.drawRoundedRect(
            rect_cadre,
            5,
            5,
        )

        # ----------------------------------------------------------------------
        # Veines du bois
        # ----------------------------------------------------------------------

        couleur_veine = QColor("#2F1D12")
        couleur_veine.setAlpha(55)

        painter.setPen(
            QPen(
                couleur_veine,
                0.8,
            )
        )

        for i in range(7):

            y = rect_cadre.top() + 6 + i * rect_cadre.height() / 7

            decalage = (i % 3 - 1) * 3

            painter.drawLine(
                QPointF(
                    rect_cadre.left() + 8,
                    y,
                ),
                QPointF(
                    rect_cadre.right() - 8,
                    y + decalage,
                ),
            )

        # Quelques petites fibres verticales
        for i in range(6):

            x = rect_cadre.left() + 18 + i * (rect_cadre.width() - 36) / 5

            painter.drawLine(
                QPointF(
                    x,
                    rect_cadre.top() + 3,
                ),
                QPointF(
                    x + (i % 2) * 2,
                    rect_cadre.top() + epaisseur_cadre - 2,
                ),
            )

            painter.drawLine(
                QPointF(
                    x,
                    rect_cadre.bottom() - epaisseur_cadre + 2,
                ),
                QPointF(
                    x - (i % 2) * 2,
                    rect_cadre.bottom() - 3,
                ),
            )

        # ----------------------------------------------------------------------
        # Plaque métallique émaillée
        # ----------------------------------------------------------------------

        degrade_plaque = QLinearGradient(
            rect_plaque.topLeft(),
            rect_plaque.bottomLeft(),
        )

        degrade_plaque.setColorAt(
            0.00,
            QColor("#435D6D"),
        )
        degrade_plaque.setColorAt(
            0.15,
            QColor("#344E5E"),
        )
        degrade_plaque.setColorAt(
            0.55,
            QColor("#294352"),
        )
        degrade_plaque.setColorAt(
            0.88,
            QColor("#203946"),
        )
        degrade_plaque.setColorAt(
            1.00,
            QColor("#182E39"),
        )

        painter.setBrush(degrade_plaque)

        painter.setPen(
            QPen(
                QColor("#15252D"),
                1.3,
            )
        )

        painter.drawRoundedRect(
            rect_plaque,
            2.5,
            2.5,
        )

        # ----------------------------------------------------------------------
        # Léger reflet de l'émail
        # ----------------------------------------------------------------------

        reflet = QLinearGradient(
            rect_plaque.topLeft(),
            rect_plaque.bottomLeft(),
        )

        transparent = QColor("#FFFFFF")
        transparent.setAlpha(0)

        clair = QColor("#FFFFFF")
        clair.setAlpha(30)

        reflet.setColorAt(0.0, clair)
        reflet.setColorAt(0.28, transparent)
        reflet.setColorAt(1.0, transparent)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(reflet)

        painter.drawRoundedRect(
            rect_plaque.adjusted(
                2,
                2,
                -2,
                -2,
            ),
            2,
            2,
        )

        # ----------------------------------------------------------------------
        # Rivets métalliques
        # ----------------------------------------------------------------------

        positions_rivets = [
            QPointF(
                rect_plaque.left() + 9,
                rect_plaque.top() + 9,
            ),
            QPointF(
                rect_plaque.right() - 9,
                rect_plaque.top() + 9,
            ),
            QPointF(
                rect_plaque.left() + 9,
                rect_plaque.bottom() - 9,
            ),
            QPointF(
                rect_plaque.right() - 9,
                rect_plaque.bottom() - 9,
            ),
        ]

        for centre in positions_rivets:

            degrade_rivet = QRadialGradient(
                centre,
                3.2,
                QPointF(
                    centre.x() - 1,
                    centre.y() - 1,
                ),
            )

            degrade_rivet.setColorAt(
                0.0,
                QColor("#E0E0D8"),
            )
            degrade_rivet.setColorAt(
                0.45,
                QColor("#9A9D98"),
            )
            degrade_rivet.setColorAt(
                1.0,
                QColor("#4C5050"),
            )

            painter.setPen(
                QPen(
                    QColor("#303334"),
                    0.6,
                )
            )

            painter.setBrush(degrade_rivet)

            painter.drawEllipse(
                centre,
                3.0,
                3.0,
            )

        # ----------------------------------------------------------------------
        # Double filet autour du texte
        # ----------------------------------------------------------------------

        rect_filet = rect_plaque.adjusted(
            17,
            8,
            -17,
            -8,
        )

        couleur_filet = QColor("#E6E0CA")
        couleur_filet.setAlpha(170)

        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.setPen(
            QPen(
                couleur_filet,
                0.8,
            )
        )

        painter.drawRect(rect_filet)

        # ----------------------------------------------------------------------
        # Texte du panneau
        # ----------------------------------------------------------------------

        painter.setFont(
            QFont(
                self.police,
                max(
                    11,
                    int(h * 0.21),
                ),
                QFont.Weight.DemiBold,
            )
        )

        couleur_texte = QColor("#F2ECD7")

        painter.setPen(couleur_texte)

        painter.drawText(
            rect_plaque.adjusted(
                32,
                0,
                -32,
                0,
            ),
            Qt.AlignmentFlag.AlignCenter,
            self.texte,
        )
