################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_3                                #
# Onglet 4.3.2 – Suggestions de nouvelles destinations – Reco par pays         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import random

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

# 1 -- Classe de recommandations par pays --------------------------------------


class CarteRecommandationPays(QWidget):
    """
    Petit tableau mécanique de gare regroupant les recommandations d'un pays.

    Le pays est affiché dans un bandeau supérieur discret et chaque région
    apparaît sur un volet mécanique compact avec un numéro de voie et un statut.
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
        self.graine = random.random()

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

        # Dimensions compactes
        self.hauteur_entete = 34
        self.hauteur_ligne = 30
        self.espacement_ligne = 3

        hauteur = (
            16
            + self.hauteur_entete
            + max(1, len(self.regions)) * (self.hauteur_ligne + self.espacement_ligne)
            + 8
        )

        self.setMinimumHeight(hauteur)
        self.setMaximumHeight(hauteur)

        # Ombre discrète
        self._ombre_effet = QGraphicsDropShadowEffect(self)

        self._ombre_effet.setBlurRadius(14)
        self._ombre_effet.setOffset(0, 3)

        couleur_ombre = QColor("#000000")
        couleur_ombre.setAlpha(70)

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
            4,
            self.width() - 10,
            self.height() - 8,
        )

        # ----------------------------------------------------------------------
        # Fin cadre métallique
        # ----------------------------------------------------------------------

        degrade_cadre = QLinearGradient(
            rect.topLeft(),
            rect.bottomLeft(),
        )

        degrade_cadre.setColorAt(
            0.0,
            QColor("#616466"),
        )
        degrade_cadre.setColorAt(
            0.35,
            QColor("#393C3D"),
        )
        degrade_cadre.setColorAt(
            1.0,
            QColor("#252728"),
        )

        painter.setPen(
            QPen(
                QColor("#1D1E1F"),
                0.9,
            )
        )

        painter.setBrush(degrade_cadre)

        painter.drawRoundedRect(
            rect,
            5,
            5,
        )

        # ----------------------------------------------------------------------
        # Surface intérieure
        # ----------------------------------------------------------------------

        rect_tableau = rect.adjusted(
            4,
            4,
            -4,
            -4,
        )

        painter.setPen(
            QPen(
                QColor("#0C0D0D"),
                0.8,
            )
        )

        painter.setBrush(QColor("#121414"))

        painter.drawRoundedRect(
            rect_tableau,
            3,
            3,
        )

        # ----------------------------------------------------------------------
        # En-tête
        # ----------------------------------------------------------------------

        rect_pays = QRectF(
            rect_tableau.left() + 4,
            rect_tableau.top() + 3,
            rect_tableau.width() - 8,
            self.hauteur_entete,
        )

        self._dessiner_entete(
            painter,
            rect_pays,
        )

        # ----------------------------------------------------------------------
        # Destinations
        # ----------------------------------------------------------------------

        y = rect_pays.bottom() + 3

        for numero, region in enumerate(
            self.regions,
            start=1,
        ):

            rect_ligne = QRectF(
                rect_tableau.left() + 5,
                y,
                rect_tableau.width() - 10,
                self.hauteur_ligne,
            )

            self._dessiner_destination(
                painter=painter,
                rect=rect_ligne,
                numero=numero,
                region=region,
            )

            y += self.hauteur_ligne + self.espacement_ligne

        # ----------------------------------------------------------------------
        # Rivets
        # ----------------------------------------------------------------------

        self._dessiner_rivets(
            painter,
            rect,
        )

    # --------------------------------------------------------------------------
    # En-tête
    # --------------------------------------------------------------------------

    def _dessiner_entete(
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
            QColor("#30383B"),
        )
        degrade.setColorAt(
            1.0,
            QColor("#202729"),
        )

        painter.setBrush(degrade)

        painter.setPen(
            QPen(
                QColor("#4C5558"),
                0.7,
            )
        )

        painter.drawRoundedRect(
            rect,
            2,
            2,
        )

        # ----------------------------------------------------------------------
        # Reflet supérieur
        # ----------------------------------------------------------------------

        reflet = QColor("#FFFFFF")
        reflet.setAlpha(18)

        painter.setPen(
            QPen(
                reflet,
                0.7,
            )
        )

        painter.drawLine(
            QPointF(
                rect.left() + 4,
                rect.top() + 1,
            ),
            QPointF(
                rect.right() - 4,
                rect.top() + 1,
            ),
        )

        # ----------------------------------------------------------------------
        # Géométrie des colonnes
        # ----------------------------------------------------------------------

        largeur_statut = min(
            105,
            rect.width() * 0.23,
        )

        largeur_voie = min(
            48,
            rect.width() * 0.10,
        )

        rect_statut = QRectF(
            rect.right() - largeur_statut - 5,
            rect.top(),
            largeur_statut,
            rect.height(),
        )

        rect_voie = QRectF(
            rect_statut.left() - largeur_voie,
            rect.top(),
            largeur_voie,
            rect.height(),
        )

        # ----------------------------------------------------------------------
        # Pays
        # ----------------------------------------------------------------------

        painter.setFont(
            QFont(
                self.police_pays,
                max(
                    10,
                    int(rect.height() * 0.42),
                ),
                QFont.Weight.DemiBold,
            )
        )

        painter.setPen(QColor("#E9E2CF"))

        texte = f"{self.emoji}  {self.pays_nom}" if self.emoji else self.pays_nom

        painter.drawText(
            QRectF(
                rect.left() + 10,
                rect.top(),
                rect_voie.left() - rect.left() - 18,
                rect.height(),
            ),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            texte,
        )

        # ----------------------------------------------------------------------
        # Titres de colonnes
        # ----------------------------------------------------------------------

        painter.setFont(
            QFont(
                self.police_principale,
                max(
                    6,
                    int(rect.height() * 0.20),
                ),
                QFont.Weight.DemiBold,
            )
        )

        couleur_entete = QColor("#AAA99F")

        painter.setPen(couleur_entete)

        painter.drawText(
            rect_voie,
            Qt.AlignmentFlag.AlignCenter,
            "VOIE",
        )

        painter.drawText(
            rect_statut,
            Qt.AlignmentFlag.AlignCenter,
            "STATUT",
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
        # Fond mécanique
        # ----------------------------------------------------------------------

        degrade = QLinearGradient(
            rect.topLeft(),
            rect.bottomLeft(),
        )

        degrade.setColorAt(
            0.00,
            QColor("#202121"),
        )
        degrade.setColorAt(
            0.45,
            QColor("#151616"),
        )
        degrade.setColorAt(
            0.49,
            QColor("#101111"),
        )
        degrade.setColorAt(
            0.51,
            QColor("#080909"),
        )
        degrade.setColorAt(
            0.55,
            QColor("#131414"),
        )
        degrade.setColorAt(
            1.00,
            QColor("#1B1C1C"),
        )

        painter.setBrush(degrade)

        painter.setPen(
            QPen(
                QColor("#313333"),
                0.6,
            )
        )

        painter.drawRoundedRect(
            rect,
            1.5,
            1.5,
        )

        # ----------------------------------------------------------------------
        # Fente centrale
        # ----------------------------------------------------------------------

        y_centre = rect.center().y()

        painter.setPen(
            QPen(
                QColor("#050505"),
                0.9,
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

        couleur_reflet = QColor("#FFFFFF")
        couleur_reflet.setAlpha(10)

        painter.setPen(
            QPen(
                couleur_reflet,
                0.6,
            )
        )

        painter.drawLine(
            QPointF(
                rect.left() + 2,
                y_centre - 1,
            ),
            QPointF(
                rect.right() - 2,
                y_centre - 1,
            ),
        )

        # ----------------------------------------------------------------------
        # Dimensions des colonnes
        # ----------------------------------------------------------------------

        largeur_numero = min(
            38,
            rect.width() * 0.08,
        )

        largeur_statut = min(
            105,
            rect.width() * 0.23,
        )

        largeur_voie = min(
            48,
            rect.width() * 0.10,
        )

        rect_numero = QRectF(
            rect.left(),
            rect.top(),
            largeur_numero,
            rect.height(),
        )

        rect_statut = QRectF(
            rect.right() - largeur_statut,
            rect.top(),
            largeur_statut,
            rect.height(),
        )

        rect_voie = QRectF(
            rect_statut.left() - largeur_voie,
            rect.top(),
            largeur_voie,
            rect.height(),
        )

        rect_region = QRectF(
            rect_numero.right() + 10,
            rect.top() + 1,
            rect_voie.left() - rect_numero.right() - 18,
            rect.height() - 2,
        )

        # ----------------------------------------------------------------------
        # Séparations verticales
        # ----------------------------------------------------------------------

        couleur_separation = QColor("#555655")
        couleur_separation.setAlpha(100)

        painter.setPen(
            QPen(
                couleur_separation,
                0.6,
            )
        )

        for x in (
            rect_numero.right(),
            rect_voie.left(),
            rect_statut.left(),
        ):

            painter.drawLine(
                QPointF(
                    x,
                    rect.top() + 4,
                ),
                QPointF(
                    x,
                    rect.bottom() - 4,
                ),
            )

        # ----------------------------------------------------------------------
        # Numéro de recommandation
        # ----------------------------------------------------------------------

        painter.setFont(
            QFont(
                self.police_principale,
                max(
                    7,
                    int(rect.height() * 0.27),
                ),
                QFont.Weight.DemiBold,
            )
        )

        painter.setPen(QColor("#888679"))

        painter.drawText(
            rect_numero,
            Qt.AlignmentFlag.AlignCenter,
            str(numero).zfill(2),
        )

        # ----------------------------------------------------------------------
        # Région
        # ----------------------------------------------------------------------

        self._dessiner_texte_adaptatif(
            painter=painter,
            rect=rect_region,
            texte=region.upper(),
            taille_max=max(
                8,
                int(rect.height() * 0.34),
            ),
            taille_min=max(
                6,
                int(rect.height() * 0.22),
            ),
        )

        # ----------------------------------------------------------------------
        # Voie
        # ----------------------------------------------------------------------

        painter.setFont(
            QFont(
                self.police_principale,
                max(
                    8,
                    int(rect.height() * 0.30),
                ),
                QFont.Weight.Bold,
            )
        )

        painter.setPen(QColor("#E3E0D4"))

        painter.drawText(
            rect_voie,
            Qt.AlignmentFlag.AlignCenter,
            str(random.Random(self.graine * numero).randint(1, 12)),
        )

        # ----------------------------------------------------------------------
        # Statut
        # ----------------------------------------------------------------------

        painter.setFont(
            QFont(
                self.police_principale,
                max(
                    6,
                    int(rect.height() * 0.21),
                ),
                QFont.Weight.DemiBold,
            )
        )

        painter.setPen(QColor("#D5A843"))

        painter.drawText(
            rect_statut.adjusted(
                4,
                0,
                -4,
                0,
            ),
            Qt.AlignmentFlag.AlignCenter,
            "À DÉCOUVRIR",
        )

        # ----------------------------------------------------------------------
        # Petits axes mécaniques
        # ----------------------------------------------------------------------

        couleur_axe = QColor("#747675")
        couleur_axe.setAlpha(110)

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(couleur_axe)

        rayon = 1.2

        for x in (
            rect.left() + 4,
            rect.right() - 4,
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
                    0.25,
                    taille * 0.035,
                ),
            )

            painter.setFont(police)

            metrics = painter.fontMetrics()

            if metrics.horizontalAdvance(texte) <= rect.width():

                painter.setPen(QColor("#E3E0D4"))

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

        painter.setPen(QColor("#E3E0D4"))

        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            texte,
        )

    # --------------------------------------------------------------------------
    # Rivets
    # --------------------------------------------------------------------------

    def _dessiner_rivets(
        self,
        painter: QPainter,
        rect: QRectF,
    ):

        positions = (
            QPointF(
                rect.left() + 8,
                rect.top() + 8,
            ),
            QPointF(
                rect.right() - 8,
                rect.top() + 8,
            ),
        )

        for centre in positions:

            rayon = 2.0

            degrade = QRadialGradient(
                centre,
                rayon,
                QPointF(
                    centre.x() - 0.6,
                    centre.y() - 0.6,
                ),
            )

            degrade.setColorAt(
                0.0,
                QColor("#B8BAB8"),
            )
            degrade.setColorAt(
                0.5,
                QColor("#727574"),
            )
            degrade.setColorAt(
                1.0,
                QColor("#353737"),
            )

            painter.setPen(
                QPen(
                    QColor("#252626"),
                    0.4,
                )
            )

            painter.setBrush(degrade)

            painter.drawEllipse(
                centre,
                rayon,
                rayon,
            )
