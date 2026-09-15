################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.56 – Classe de création d'une gare de départ / arrivée                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

from _4_Interface._4_3_Icones._4_3_54_gare_ancienne import (
    GareAncienne,
    _assombrir,
    _avec_alpha,
    _eclaircir,
)

# 1 -- Classe de gare terminus -------------------------------------------------


class GareDepartArrivee(GareAncienne):
    """
    Gare ancienne utilisée au début et à la fin de l'animation.

    La gare est un terminus :

        sens = 1
            Le fond monumental est à gauche et les voies sortent à droite.
            C'est la configuration naturelle pour le départ.

        sens = -1
            La composition est inversée.
            C'est la configuration naturelle pour l'arrivée.

    `nom_pays` peut être None :
        aucun panneau de gare n'est alors affiché.

    `i` et `n` peuvent être None :
        la plaque de progression n'est alors pas affichée.

    Cela permet notamment d'utiliser la gare initiale pendant la phase
    "préparation des données" sans lui attribuer artificiellement un pays
    ou une étape de progression.
    """

    masque_paysage = True
    masque_rails = True

    def __init__(
        self,
        sens: int = 1,
        couleur_mur: QColor | str = "#D7C7AE",
        couleur_mur_bas: QColor | str = "#BCA98E",
        couleur_metal: QColor | str = "#647076",
        couleur_metal_fonce: QColor | str = "#495257",
        couleur_verre: QColor | str = "#CFE0E5",
        couleur_quai: QColor | str = "#A99A88",
        couleur_bord_quai: QColor | str = "#E8DECC",
        couleur_plancher: QColor | str = "#7F6E5D",
        lampes_allumees: bool = True,
        etat_feu: str = "vert",
    ):
        super().__init__(
            couleur_mur=couleur_mur,
            couleur_mur_bas=couleur_mur_bas,
            couleur_metal=couleur_metal,
            couleur_metal_fonce=couleur_metal_fonce,
            couleur_verre=couleur_verre,
            couleur_quai=couleur_quai,
            couleur_bord_quai=couleur_bord_quai,
            couleur_plancher=couleur_plancher,
            lampes_allumees=lampes_allumees,
            etat_feu=etat_feu,
        )

        self.sens = 1 if sens >= 0 else -1

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    def largeur_recommandee(
        self,
        hauteur_scene: float,
    ) -> float:
        """
        La gare terminus est volontairement assez longue.

        Le train doit pouvoir être entièrement contenu à l'intérieur.
        """

        return hauteur_scene * 3.40

    def _x_inverse(
        self,
        rect: QRectF,
        proportion: float,
    ) -> float:
        """
        Convertit une position horizontale normalisée selon le sens.

        Une proportion de 0.20 donnera :
            - 20 % depuis la gauche si sens = 1 ;
            - 20 % depuis la droite si sens = -1.
        """

        if self.sens > 0:
            return rect.left() + rect.width() * proportion

        return rect.right() - rect.width() * proportion

    # --------------------------------------------------------------------------
    # Fond monumental
    # --------------------------------------------------------------------------

    def _dessiner_fond_terminus(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """
        Dessine le côté fermé du terminus.

        On crée une grande façade intérieure avec :
            - une arche centrale ;
            - des moulures ;
            - une grande horloge héritée de GareAncienne ;
            - une porte de service ;
            - quelques panneaux décoratifs.
        """

        h = rect.height()

        if self.sens > 0:

            rect_fond = QRectF(
                rect.left(),
                rect.top(),
                rect.width() * 0.20,
                y_quai - rect.top(),
            )

        else:

            rect_fond = QRectF(
                rect.right() - rect.width() * 0.20,
                rect.top(),
                rect.width() * 0.20,
                y_quai - rect.top(),
            )

        # ------------------------------------------------------------------
        # Mur principal
        # ------------------------------------------------------------------

        gradient = QLinearGradient(
            rect_fond.topLeft(),
            rect_fond.bottomLeft(),
        )

        gradient.setColorAt(
            0.0,
            _eclaircir(
                self.couleur_mur,
                0.13,
            ),
        )

        gradient.setColorAt(
            1.0,
            _assombrir(
                self.couleur_mur,
                0.07,
            ),
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient))

        painter.drawRect(rect_fond)

        # ------------------------------------------------------------------
        # Grande arche décorative
        # ------------------------------------------------------------------

        marge_x = rect_fond.width() * 0.18

        largeur_arche = rect_fond.width() - 2 * marge_x

        y_bas = y_quai - h * 0.035

        y_haut = rect.top() + h * 0.20

        path = QPainterPath()

        path.moveTo(
            rect_fond.left() + marge_x,
            y_bas,
        )

        path.lineTo(
            rect_fond.left() + marge_x,
            y_haut + h * 0.10,
        )

        path.quadTo(
            QPointF(
                rect_fond.center().x(),
                y_haut,
            ),
            QPointF(
                rect_fond.right() - marge_x,
                y_haut + h * 0.10,
            ),
        )

        path.lineTo(
            rect_fond.right() - marge_x,
            y_bas,
        )

        painter.setBrush(Qt.BrushStyle.NoBrush)

        pen_arche = QPen(
            _assombrir(
                self.couleur_mur_bas,
                0.20,
            )
        )

        pen_arche.setWidthF(
            max(
                2.0,
                h * 0.012,
            )
        )

        painter.setPen(pen_arche)

        painter.drawPath(path)

        # ------------------------------------------------------------------
        # Corniche
        # ------------------------------------------------------------------

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(
            _assombrir(
                self.couleur_mur,
                0.10,
            )
        )

        hauteur_corniche = h * 0.025

        painter.drawRect(
            QRectF(
                rect_fond.left(),
                rect.top() + h * 0.145,
                rect_fond.width(),
                hauteur_corniche,
            )
        )

        # ------------------------------------------------------------------
        # Soubassement
        # ------------------------------------------------------------------

        rect_soubassement = QRectF(
            rect_fond.left(),
            y_quai - h * 0.15,
            rect_fond.width(),
            h * 0.15,
        )

        grad_bas = QLinearGradient(
            rect_soubassement.topLeft(),
            rect_soubassement.bottomLeft(),
        )

        grad_bas.setColorAt(
            0.0,
            self.couleur_mur_bas,
        )

        grad_bas.setColorAt(
            1.0,
            _assombrir(
                self.couleur_mur_bas,
                0.15,
            ),
        )

        painter.setBrush(QBrush(grad_bas))

        painter.drawRect(rect_soubassement)

        # ------------------------------------------------------------------
        # Porte de service
        # ------------------------------------------------------------------

        largeur_porte = rect_fond.width() * 0.20

        hauteur_porte = h * 0.17

        rect_porte = QRectF(
            rect_fond.center().x() - largeur_porte / 2,
            y_quai - hauteur_porte,
            largeur_porte,
            hauteur_porte,
        )

        grad_porte = QLinearGradient(
            rect_porte.topLeft(),
            rect_porte.topRight(),
        )

        grad_porte.setColorAt(
            0.0,
            QColor("#695744"),
        )

        grad_porte.setColorAt(
            0.5,
            QColor("#806A50"),
        )

        grad_porte.setColorAt(
            1.0,
            QColor("#5B4A3A"),
        )

        painter.setPen(
            QPen(
                QColor("#493C30"),
                max(
                    1.0,
                    h * 0.004,
                ),
            )
        )

        painter.setBrush(QBrush(grad_porte))

        painter.drawRoundedRect(
            rect_porte,
            largeur_porte * 0.06,
            largeur_porte * 0.06,
        )

        # Poignée
        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QColor("#B99B5C"))

        painter.drawEllipse(
            QPointF(
                rect_porte.right() - largeur_porte * 0.20,
                rect_porte.center().y(),
            ),
            h * 0.006,
            h * 0.006,
        )

    # --------------------------------------------------------------------------
    # Ouverture vers les voies
    # --------------------------------------------------------------------------

    def _dessiner_sortie_terminus(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """
        Dessine l'ouverture unique du terminus.

        Elle se trouve à droite au départ et à gauche à l'arrivée.
        """

        h = rect.height()

        largeur = rect.width() * 0.18

        hauteur = h * 0.57

        if self.sens > 0:

            x_centre = rect.right() - largeur * 0.52

        else:

            x_centre = rect.left() + largeur * 0.52

        x0 = x_centre - largeur / 2

        y0 = y_quai - hauteur

        # ------------------------------------------------------------------
        # Ouverture
        # ------------------------------------------------------------------

        path = QPainterPath()

        path.moveTo(
            x0,
            y_quai,
        )

        path.lineTo(
            x0,
            y0 + hauteur * 0.28,
        )

        path.quadTo(
            QPointF(
                x_centre,
                y0 - hauteur * 0.10,
            ),
            QPointF(
                x0 + largeur,
                y0 + hauteur * 0.28,
            ),
        )

        path.lineTo(
            x0 + largeur,
            y_quai,
        )

        path.closeSubpath()

        # Vers l'extérieur : davantage de lumière
        gradient = QLinearGradient(
            QPointF(
                x0,
                y0,
            ),
            QPointF(
                x0,
                y_quai,
            ),
        )

        gradient.setColorAt(
            0.0,
            QColor("#DCE9EC"),
        )

        gradient.setColorAt(
            0.55,
            QColor("#B7CCD0"),
        )

        gradient.setColorAt(
            1.0,
            QColor("#7A8B8E"),
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient))

        painter.drawPath(path)

        # ------------------------------------------------------------------
        # Encadrement épais
        # ------------------------------------------------------------------

        pen = QPen(self.couleur_metal_fonce)

        pen.setWidthF(
            max(
                2.0,
                h * 0.012,
            )
        )

        painter.setPen(pen)

        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawPath(path)

        # Deuxième arc intérieur pour donner de la profondeur
        decalage = h * 0.018

        path_interieur = QPainterPath()

        path_interieur.moveTo(
            x0 + decalage,
            y_quai,
        )

        path_interieur.lineTo(
            x0 + decalage,
            y0 + hauteur * 0.31,
        )

        path_interieur.quadTo(
            QPointF(
                x_centre,
                y0 - hauteur * 0.03,
            ),
            QPointF(
                x0 + largeur - decalage,
                y0 + hauteur * 0.31,
            ),
        )

        path_interieur.lineTo(
            x0 + largeur - decalage,
            y_quai,
        )

        pen_interieur = QPen(
            _avec_alpha(
                self.couleur_metal_fonce,
                130,
            )
        )

        pen_interieur.setWidthF(
            max(
                1.0,
                h * 0.005,
            )
        )

        painter.setPen(pen_interieur)

        painter.drawPath(path_interieur)

    # --------------------------------------------------------------------------
    # Butoir décoratif
    # --------------------------------------------------------------------------

    def _dessiner_butoir(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """
        Dessine un petit butoir contre le fond fermé du terminus.

        Il reste en arrière-plan du train et suggère la fin des voies sans
        afficher les rails eux-mêmes.
        """

        h = rect.height()

        if self.sens > 0:

            x = rect.left() + rect.width() * 0.205

        else:

            x = rect.right() - rect.width() * 0.205

        largeur = h * 0.10

        hauteur = h * 0.085

        pen = QPen(QColor("#3F4548"))

        pen.setWidthF(
            max(
                2.0,
                h * 0.011,
            )
        )

        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(pen)

        # Montants
        painter.drawLine(
            QPointF(
                x - largeur / 2,
                y_quai,
            ),
            QPointF(
                x - largeur * 0.25,
                y_quai - hauteur,
            ),
        )

        painter.drawLine(
            QPointF(
                x + largeur / 2,
                y_quai,
            ),
            QPointF(
                x + largeur * 0.25,
                y_quai - hauteur,
            ),
        )

        # Traverse
        painter.drawLine(
            QPointF(
                x - largeur * 0.32,
                y_quai - hauteur,
            ),
            QPointF(
                x + largeur * 0.32,
                y_quai - hauteur,
            ),
        )

        # Tampons
        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QColor("#292E31"))

        rayon = h * 0.016

        for dx in (
            -largeur * 0.22,
            largeur * 0.22,
        ):

            painter.drawEllipse(
                QPointF(
                    x + dx,
                    y_quai - hauteur,
                ),
                rayon,
                rayon,
            )

    # --------------------------------------------------------------------------
    # Dessin arrière
    # --------------------------------------------------------------------------

    def peindre_arriere(
        self,
        painter: QPainter,
        rect: QRectF,
        nom_pays: str | None = None,
        i: int | None = None,
        n: int | None = None,
        y_rail: float | None = None,
        **kwargs,
    ) -> None:
        """Dessine l'intérieur de la gare derrière le train."""

        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        h = rect.height()

        y_quai = self._y_quai(
            rect,
            y_rail,
        )

        # ------------------------------------------------------------------
        # Fond général
        # ------------------------------------------------------------------

        self._dessiner_fond_mural(
            painter,
            rect,
            y_quai,
        )

        # ------------------------------------------------------------------
        # Verrière et structure
        # ------------------------------------------------------------------

        self._dessiner_verriere(
            painter,
            rect,
            y_quai,
        )

        self._dessiner_piliers(
            painter,
            rect,
            y_quai,
        )

        self._dessiner_lampes_suspendues(
            painter,
            rect,
            y_quai,
        )

        # ------------------------------------------------------------------
        # Terminus
        # ------------------------------------------------------------------

        self._dessiner_fond_terminus(
            painter,
            rect,
            y_quai,
        )

        self._dessiner_sortie_terminus(
            painter,
            rect,
            y_quai,
        )

        self._dessiner_butoir(
            painter,
            rect,
            y_quai,
        )

        # ------------------------------------------------------------------
        # Horloge
        # ------------------------------------------------------------------

        self.horloge.peindre(
            painter,
            centre=QPointF(
                self._x_inverse(
                    rect,
                    0.115,
                ),
                rect.top() + h * 0.255,
            ),
            rayon=h * 0.052,
        )

        # ------------------------------------------------------------------
        # Panneau facultatif
        # ------------------------------------------------------------------

        if nom_pays:

            if self.sens > 0:

                x_panneau = rect.left() + rect.width() * 0.37

            else:

                x_panneau = rect.right() - rect.width() * 0.37 - rect.width() * 0.21

            rect_panneau = QRectF(
                x_panneau,
                y_quai - h * 0.28,
                rect.width() * 0.21,
                h * 0.24,
            )

            self.panneau.peindre(
                painter,
                rect_panneau,
                nom_pays,
            )

            # --------------------------------------------------------------
            # Plaque i / n facultative
            # --------------------------------------------------------------

            if i is not None and n is not None:

                if self.sens > 0:

                    x_plaque = rect_panneau.right() + h * 0.020

                else:

                    x_plaque = rect_panneau.left() - h * 0.020 - h * 0.12

                rect_plaque = QRectF(
                    x_plaque,
                    y_quai - h * 0.26,
                    h * 0.12,
                    h * 0.22,
                )

                self.plaque.peindre(
                    painter,
                    rect_plaque,
                    i,
                    n,
                )

        # ------------------------------------------------------------------
        # Banc
        # ------------------------------------------------------------------

        if self.sens > 0:

            x_banc = rect.left() + rect.width() * 0.61

        else:

            x_banc = rect.right() - rect.width() * 0.61 - rect.width() * 0.11

        self._dessiner_banc(
            painter,
            QRectF(
                x_banc,
                y_quai - h * 0.105,
                rect.width() * 0.11,
                h * 0.10,
            ),
        )

        # ------------------------------------------------------------------
        # Feu près de l'ouverture
        # ------------------------------------------------------------------

        if self.sens > 0:

            x_feu = rect.right() - rect.width() * 0.15

        else:

            x_feu = rect.left() + rect.width() * 0.10

        self.feu.peindre(
            painter,
            QRectF(
                x_feu,
                y_quai - h * 0.30,
                rect.width() * 0.05,
                h * 0.28,
            ),
            etat=kwargs.get(
                "etat_feu",
                self.etat_feu,
            ),
        )

        painter.restore()

    # --------------------------------------------------------------------------
    # Bouton final
    # --------------------------------------------------------------------------

    def _dessiner_panneau_final(
        self,
        painter: QPainter,
        rect: QRectF,
        texte: str,
    ) -> None:
        """
        Dessine le grand panneau de fin de publication.

        Le panneau est placé au premier plan, suspendu dans la gare terminus.
        """

        h = rect.height()

        largeur = min(
            rect.width() * 0.52,
            h * 1.85,
        )

        hauteur = h * 0.15

        x = rect.center().x() - largeur / 2

        y = rect.top() + h * 0.11

        rect_panneau = QRectF(
            x,
            y,
            largeur,
            hauteur,
        )

        # ----------------------------------------------------------------------
        # Suspensions
        # ----------------------------------------------------------------------

        y_accroche = rect.top() + h * 0.035

        decalage_accroches = largeur * 0.34

        pen_suspension = QPen(self.couleur_metal_fonce)

        pen_suspension.setWidthF(
            max(
                1.5,
                h * 0.007,
            )
        )

        painter.setPen(pen_suspension)

        for dx in (
            -decalage_accroches,
            decalage_accroches,
        ):

            x_fil = rect.center().x() + dx

            painter.drawLine(
                QPointF(
                    x_fil,
                    y_accroche,
                ),
                QPointF(
                    x_fil,
                    rect_panneau.top(),
                ),
            )

        # ----------------------------------------------------------------------
        # Ombre
        # ----------------------------------------------------------------------

        rect_ombre = QRectF(
            rect_panneau.left() + h * 0.012,
            rect_panneau.top() + h * 0.012,
            rect_panneau.width(),
            rect_panneau.height(),
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(
            QColor(
                0,
                0,
                0,
                55,
            )
        )

        painter.drawRoundedRect(
            rect_ombre,
            h * 0.018,
            h * 0.018,
        )

        # ----------------------------------------------------------------------
        # Cadre
        # ----------------------------------------------------------------------

        painter.setBrush(self.couleur_metal_fonce)

        painter.drawRoundedRect(
            rect_panneau,
            h * 0.018,
            h * 0.018,
        )

        marge = h * 0.015

        rect_interieur = rect_panneau.adjusted(
            marge,
            marge,
            -marge,
            -marge,
        )

        # ----------------------------------------------------------------------
        # Fond ivoire
        # ----------------------------------------------------------------------

        gradient = QLinearGradient(
            rect_interieur.topLeft(),
            rect_interieur.bottomLeft(),
        )

        gradient.setColorAt(
            0.0,
            QColor("#F3EBDD"),
        )

        gradient.setColorAt(
            1.0,
            QColor("#DDD0BA"),
        )

        painter.setBrush(QBrush(gradient))

        painter.drawRoundedRect(
            rect_interieur,
            h * 0.010,
            h * 0.010,
        )

        # ----------------------------------------------------------------------
        # Texte
        # ----------------------------------------------------------------------

        font = painter.font()

        font.setBold(True)

        font.setPointSizeF(
            max(
                8.0,
                h * 0.043,
            )
        )

        painter.setFont(font)

        painter.setPen(QColor("#353B3E"))

        painter.drawText(
            rect_interieur.adjusted(
                h * 0.020,
                0,
                -h * 0.020,
                0,
            ),
            Qt.AlignmentFlag.AlignCenter,
            texte,
        )

    # --------------------------------------------------------------------------
    # Dessin avant
    # --------------------------------------------------------------------------

    def peindre_avant(
        self,
        painter: QPainter,
        rect: QRectF,
        y_rail: float | None = None,
        **kwargs,
    ) -> None:
        """
        Dessine les éléments situés devant le train.

        Peut notamment recevoir :
            message_final : str | None
                Grand panneau affiché dans la gare d'arrivée.
        """

        if rect.width() <= 0 or rect.height() <= 0 or y_rail is None:
            return

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        y_quai = self._y_quai(
            rect,
            y_rail,
        )

        # ----------------------------------------------------------------------
        # Quai au premier plan
        # ----------------------------------------------------------------------

        self._dessiner_bloc_bas_avant(
            painter,
            rect,
            y_quai,
        )

        # ----------------------------------------------------------------------
        # Panneau final facultatif
        # ----------------------------------------------------------------------

        message_final = kwargs.get("message_final")

        if message_final:

            self._dessiner_panneau_final(
                painter=painter,
                rect=rect,
                texte=message_final,
            )

        painter.restore()
