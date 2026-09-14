################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_3                                #
# Onglet 4.3.2 – Suggestions de nouvelles destinations  –  Reco par pays       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtWidgets import (
    QWidget,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)

from PyQt6.QtCore import Qt, QRectF, QPointF

from PyQt6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QFont,
    QLinearGradient,
    QRadialGradient,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    _trouver_police_disponible,
)

# 1 -- Classes associées au classement par pays --------------------------------


class CarteRecommandationPays(QWidget):
    """
    Tableau mécanique de gare regroupant les recommandations d'un pays.

    Le pays apparaît sur la plaque supérieure et chaque région est affichée
    sur une ligne inspirée des anciens tableaux de départ à volets mécaniques.
    """

    def __init__(
        self,
        pays_nom: str,
        emoji: str,
        regions: list[str],
        parent=None,
    ):
        super().__init__(parent)

        self.pays_nom = pays_nom
        self.emoji = emoji
        self.regions = regions

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.police_principale = _trouver_police_disponible(
            [
                "Century Gothic",
                "Segoe UI",
                "Arial",
                "Quicksand",
            ]
        )

        self.police_pays = _trouver_police_disponible(
            [
                "CormorantGaramond",
                "Book Antiqua",
                "Georgia",
                "Palatino Linotype",
            ]
        )

        # Hauteur adaptée au nombre de destinations
        hauteur = 72 + max(1, len(self.regions)) * 46 + 18

        self.setMinimumHeight(hauteur)
        self.setMaximumHeight(hauteur)

        # Ombre générale
        self._ombre_effet = QGraphicsDropShadowEffect(self)

        self._ombre_effet.setBlurRadius(22)
        self._ombre_effet.setOffset(0, 5)

        couleur_ombre = QColor("#000000")
        couleur_ombre.setAlpha(90)

        self._ombre_effet.setColor(couleur_ombre)

        self.setGraphicsEffect(self._ombre_effet)

    # --------------------------------------------------------------------------
    # Dessin principal
    # --------------------------------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        rect = QRectF(
            5,
            5,
            self.width() - 10,
            self.height() - 12,
        )

        # ----------------------------------------------------------------------
        # Cadre extérieur métallique
        # ----------------------------------------------------------------------

        degrade_cadre = QLinearGradient(
            rect.topLeft(),
            rect.bottomLeft(),
        )

        degrade_cadre.setColorAt(
            0.00,
            QColor("#74777A"),
        )
        degrade_cadre.setColorAt(
            0.10,
            QColor("#46494B"),
        )
        degrade_cadre.setColorAt(
            0.50,
            QColor("#2B2D2E"),
        )
        degrade_cadre.setColorAt(
            0.90,
            QColor("#444647"),
        )
        degrade_cadre.setColorAt(
            1.00,
            QColor("#1F2021"),
        )

        painter.setPen(
            QPen(
                QColor("#171819"),
                1.3,
            )
        )

        painter.setBrush(degrade_cadre)

        painter.drawRoundedRect(
            rect,
            7,
            7,
        )

        # ----------------------------------------------------------------------
        # Partie noire du tableau
        # ----------------------------------------------------------------------

        rect_tableau = rect.adjusted(
            8,
            8,
            -8,
            -8,
        )

        degrade_tableau = QLinearGradient(
            rect_tableau.topLeft(),
            rect_tableau.bottomLeft(),
        )

        degrade_tableau.setColorAt(
            0.0,
            QColor("#242627"),
        )

        degrade_tableau.setColorAt(
            0.35,
            QColor("#17191A"),
        )

        degrade_tableau.setColorAt(
            1.0,
            QColor("#0C0D0E"),
        )

        painter.setBrush(degrade_tableau)

        painter.setPen(
            QPen(
                QColor("#080909"),
                1,
            )
        )

        painter.drawRoundedRect(
            rect_tableau,
            4,
            4,
        )

        # ----------------------------------------------------------------------
        # Plaque du pays
        # ----------------------------------------------------------------------

        rect_pays = QRectF(
            rect_tableau.left() + 8,
            rect_tableau.top() + 7,
            rect_tableau.width() - 16,
            46,
        )

        self._dessiner_plaque_pays(
            painter,
            rect_pays,
        )

        # ----------------------------------------------------------------------
        # Lignes de destinations
        # ----------------------------------------------------------------------

        y = rect_pays.bottom() + 7

        hauteur_ligne = 40

        for numero, region in enumerate(
            self.regions,
            start=1,
        ):

            rect_ligne = QRectF(
                rect_tableau.left() + 9,
                y,
                rect_tableau.width() - 18,
                hauteur_ligne,
            )

            self._dessiner_destination(
                painter=painter,
                rect=rect_ligne,
                numero=numero,
                region=region,
            )

            y += hauteur_ligne + 6

        # ----------------------------------------------------------------------
        # Vis du cadre
        # ----------------------------------------------------------------------

        self._dessiner_vis(
            painter,
            rect,
        )

    # --------------------------------------------------------------------------
    # Plaque supérieure
    # --------------------------------------------------------------------------

    def _dessiner_plaque_pays(
        self,
        painter: QPainter,
        rect: QRectF,
    ):

        degrade = QLinearGradient(
            rect.topLeft(),
            rect.bottomLeft(),
        )

        degrade.setColorAt(
            0.0,
            QColor("#384247"),
        )

        degrade.setColorAt(
            0.48,
            QColor("#273136"),
        )

        degrade.setColorAt(
            1.0,
            QColor("#182126"),
        )

        painter.setBrush(degrade)

        painter.setPen(
            QPen(
                QColor("#5C6568"),
                0.8,
            )
        )

        painter.drawRoundedRect(
            rect,
            3,
            3,
        )

        # Fine ligne métallique inférieure
        painter.setPen(
            QPen(
                QColor("#777D7F"),
                0.7,
            )
        )

        painter.drawLine(
            QPointF(
                rect.left() + 6,
                rect.bottom() - 2,
            ),
            QPointF(
                rect.right() - 6,
                rect.bottom() - 2,
            ),
        )

        # Pays
        painter.setFont(
            QFont(
                self.police_pays,
                max(
                    11,
                    int(rect.height() * 0.40),
                ),
                QFont.Weight.DemiBold,
            )
        )

        painter.setPen(QColor("#EEE5CB"))

        texte = f"{self.emoji}  {self.pays_nom}" if self.emoji else self.pays_nom

        painter.drawText(
            rect.adjusted(
                15,
                0,
                -15,
                0,
            ),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            texte,
        )

    # --------------------------------------------------------------------------
    # Destination
    # --------------------------------------------------------------------------

    def _dessiner_destination(
        self,
        painter: QPainter,
        rect: QRectF,
        numero: int,
        region: str,
    ):

        # ----------------------------------------------------------------------
        # Fond du volet
        # ----------------------------------------------------------------------

        degrade = QLinearGradient(
            rect.topLeft(),
            rect.bottomLeft(),
        )

        degrade.setColorAt(
            0.00,
            QColor("#1C1D1D"),
        )

        degrade.setColorAt(
            0.46,
            QColor("#111212"),
        )

        degrade.setColorAt(
            0.50,
            QColor("#070808"),
        )

        degrade.setColorAt(
            0.54,
            QColor("#111212"),
        )

        degrade.setColorAt(
            1.00,
            QColor("#181919"),
        )

        painter.setBrush(degrade)

        painter.setPen(
            QPen(
                QColor("#343636"),
                0.8,
            )
        )

        painter.drawRoundedRect(
            rect,
            2.5,
            2.5,
        )

        # ----------------------------------------------------------------------
        # Séparation centrale du volet mécanique
        # ----------------------------------------------------------------------

        y_centre = rect.center().y()

        painter.setPen(
            QPen(
                QColor("#050505"),
                1.2,
            )
        )

        painter.drawLine(
            QPointF(
                rect.left() + 2,
                y_centre,
            ),
            QPointF(
                rect.right() - 2,
                y_centre,
            ),
        )

        # Petit reflet au-dessus de la coupure
        couleur_reflet = QColor("#FFFFFF")
        couleur_reflet.setAlpha(12)

        painter.setPen(
            QPen(
                couleur_reflet,
                0.7,
            )
        )

        painter.drawLine(
            QPointF(
                rect.left() + 3,
                y_centre - 1,
            ),
            QPointF(
                rect.right() - 3,
                y_centre - 1,
            ),
        )

        # ----------------------------------------------------------------------
        # Numéro
        # ----------------------------------------------------------------------

        largeur_numero = min(
            46,
            rect.width() * 0.13,
        )

        rect_numero = QRectF(
            rect.left(),
            rect.top(),
            largeur_numero,
            rect.height(),
        )

        painter.setFont(
            QFont(
                self.police_principale,
                max(
                    8,
                    int(rect.height() * 0.28),
                ),
                QFont.Weight.DemiBold,
            )
        )

        couleur_numero = QColor("#A7A18F")

        painter.setPen(couleur_numero)

        painter.drawText(
            rect_numero,
            Qt.AlignmentFlag.AlignCenter,
            str(numero).zfill(2),
        )

        # Petite séparation verticale
        painter.setPen(
            QPen(
                QColor("#3A3B3A"),
                0.8,
            )
        )

        painter.drawLine(
            QPointF(
                rect_numero.right(),
                rect.top() + 5,
            ),
            QPointF(
                rect_numero.right(),
                rect.bottom() - 5,
            ),
        )

        # ----------------------------------------------------------------------
        # Nom de la région
        # ----------------------------------------------------------------------

        rect_region = QRectF(
            rect_numero.right() + 12,
            rect.top() + 2,
            rect.right() - rect_numero.right() - 22,
            rect.height() - 4,
        )

        self._dessiner_texte_adaptatif(
            painter=painter,
            rect=rect_region,
            texte=region.upper(),
            taille_max=max(
                9,
                int(rect.height() * 0.34),
            ),
            taille_min=max(
                7,
                int(rect.height() * 0.22),
            ),
        )

        # ----------------------------------------------------------------------
        # Axes mécaniques aux extrémités
        # ----------------------------------------------------------------------

        couleur_axe = QColor("#606362")
        couleur_axe.setAlpha(150)

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(couleur_axe)

        rayon = 1.7

        for x in (
            rect.left() + 5,
            rect.right() - 5,
        ):

            painter.drawEllipse(
                QPointF(
                    x,
                    y_centre,
                ),
                rayon,
                rayon,
            )

    # --------------------------------------------------------------------------
    # Texte adaptatif
    # --------------------------------------------------------------------------

    def _dessiner_texte_adaptatif(
        self,
        painter: QPainter,
        rect: QRectF,
        texte: str,
        taille_max: int,
        taille_min: int,
    ):

        for taille in range(
            taille_max,
            taille_min - 1,
            -1,
        ):

            police = QFont(
                self.police_principale,
                taille,
                QFont.Weight.DemiBold,
            )

            police.setLetterSpacing(
                QFont.SpacingType.AbsoluteSpacing,
                max(
                    0.4,
                    taille * 0.055,
                ),
            )

            painter.setFont(police)

            metrics = painter.fontMetrics()

            if metrics.horizontalAdvance(texte) <= rect.width():

                painter.setPen(QColor("#E8E3D2"))

                painter.drawText(
                    rect,
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                    texte,
                )

                return

        # Dernier recours : élision
        police = QFont(
            self.police_principale,
            taille_min,
            QFont.Weight.DemiBold,
        )

        painter.setFont(police)

        metrics = painter.fontMetrics()

        texte = metrics.elidedText(
            texte,
            Qt.TextElideMode.ElideRight,
            int(rect.width()),
        )

        painter.setPen(QColor("#E8E3D2"))

        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            texte,
        )

    # --------------------------------------------------------------------------
    # Vis du cadre
    # --------------------------------------------------------------------------

    def _dessiner_vis(
        self,
        painter: QPainter,
        rect: QRectF,
    ):

        positions = (
            QPointF(
                rect.left() + 11,
                rect.top() + 11,
            ),
            QPointF(
                rect.right() - 11,
                rect.top() + 11,
            ),
            QPointF(
                rect.left() + 11,
                rect.bottom() - 11,
            ),
            QPointF(
                rect.right() - 11,
                rect.bottom() - 11,
            ),
        )

        for centre in positions:

            rayon = 3.0

            degrade = QRadialGradient(
                centre,
                rayon,
                QPointF(
                    centre.x() - 1,
                    centre.y() - 1,
                ),
            )

            degrade.setColorAt(
                0.0,
                QColor("#C1C3C1"),
            )

            degrade.setColorAt(
                0.45,
                QColor("#777A79"),
            )

            degrade.setColorAt(
                1.0,
                QColor("#303231"),
            )

            painter.setPen(
                QPen(
                    QColor("#252626"),
                    0.6,
                )
            )

            painter.setBrush(degrade)

            painter.drawEllipse(
                centre,
                rayon,
                rayon,
            )

            painter.setPen(
                QPen(
                    QColor("#3A3B3A"),
                    0.7,
                )
            )

            painter.drawLine(
                QPointF(
                    centre.x() - 1.5,
                    centre.y(),
                ),
                QPointF(
                    centre.x() + 1.5,
                    centre.y(),
                ),
            )
