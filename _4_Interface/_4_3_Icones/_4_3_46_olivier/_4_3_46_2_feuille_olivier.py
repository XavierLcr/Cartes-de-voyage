################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones/_4_3_46_olivier                                     #
# 4.3.46.2 – Classe de création d"une feuille d'olivier                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QBrush,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

# 1 -- Classe FeuilleOlivier ---------------------------------------------------


class FeuilleOlivier:
    """
    Représente une feuille d'olivier stylisée.

    La feuille est fine, lancéolée et légèrement asymétrique.
    Son orientation et sa courbure peuvent varier afin de créer
    un feuillage plus naturel.
    """

    def __init__(
        self,
        couleur: QColor | str = "#74885B",
        couleur_dessous: QColor | str = "#A7AD92",
        inclinaison: float = 0.0,
        courbure: float = 0.0,
        face_dessous: bool = False,
    ) -> None:

        self.couleur = QColor(couleur)
        self.couleur_dessous = QColor(couleur_dessous)

        self.inclinaison = inclinaison
        self.courbure = max(
            -1.0,
            min(1.0, courbure),
        )

        self.face_dessous = face_dessous

    # 1.1 -- Forme -------------------------------------------------------------

    def _creer_forme(
        self,
        rect: QRectF,
    ) -> QPainterPath:
        """Crée la silhouette lancéolée de la feuille."""

        cx = rect.center().x()

        haut = rect.top()
        bas = rect.bottom()

        largeur = rect.width()
        hauteur = rect.height()

        courbure_x = largeur * 0.16 * self.courbure

        path = QPainterPath()

        # Pointe supérieure
        path.moveTo(
            QPointF(
                cx,
                haut,
            )
        )

        # Côté droit
        path.cubicTo(
            QPointF(
                cx + largeur * 0.34 + courbure_x * 0.25,
                haut + hauteur * 0.20,
            ),
            QPointF(
                cx + largeur * 0.48 + courbure_x * 0.75,
                haut + hauteur * 0.55,
            ),
            QPointF(
                cx + courbure_x,
                bas,
            ),
        )

        # Côté gauche
        path.cubicTo(
            QPointF(
                cx - largeur * 0.42 + courbure_x * 0.65,
                haut + hauteur * 0.62,
            ),
            QPointF(
                cx - largeur * 0.30 + courbure_x * 0.20,
                haut + hauteur * 0.20,
            ),
            QPointF(
                cx,
                haut,
            ),
        )

        path.closeSubpath()

        return path

    # 1.2 -- Dessin des nervures -----------------------------------------------

    def _dessiner_nervures(
        self,
        painter: QPainter,
        rect: QRectF,
        couleur: QColor,
    ) -> None:

        cx = rect.center().x()

        haut = rect.top()
        bas = rect.bottom()

        largeur = rect.width()
        hauteur = rect.height()

        courbure_x = largeur * 0.16 * self.courbure

        # -- Nervure centrale ---------------------------------------------------

        couleur_nervure = QColor(couleur)

        if self.face_dessous:
            couleur_nervure = couleur_nervure.darker(115)
        else:
            couleur_nervure = couleur_nervure.lighter(125)

        couleur_nervure.setAlpha(150)

        pen = QPen(couleur_nervure)

        pen.setWidthF(
            max(
                0.6,
                largeur * 0.035,
            )
        )

        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(pen)

        path = QPainterPath()

        path.moveTo(
            QPointF(
                cx,
                haut + hauteur * 0.06,
            )
        )

        path.quadTo(
            QPointF(
                cx + courbure_x * 0.35,
                rect.center().y(),
            ),
            QPointF(
                cx + courbure_x,
                bas - hauteur * 0.04,
            ),
        )

        painter.drawPath(path)

        # -- Nervures secondaires ----------------------------------------------

        couleur_secondaire = QColor(couleur_nervure)
        couleur_secondaire.setAlpha(75)

        pen_secondaire = QPen(couleur_secondaire)

        pen_secondaire.setWidthF(
            max(
                0.35,
                largeur * 0.015,
            )
        )

        pen_secondaire.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(pen_secondaire)

        for t in (
            0.25,
            0.38,
            0.51,
            0.64,
            0.77,
        ):

            y = haut + hauteur * t

            centre_x = cx + courbure_x * t

            largeur_locale = largeur * 0.34 * (1.0 - abs(t - 0.5) * 1.15)

            # Gauche
            painter.drawLine(
                QPointF(
                    centre_x,
                    y,
                ),
                QPointF(
                    centre_x - largeur_locale,
                    y - hauteur * 0.055,
                ),
            )

            # Droite
            painter.drawLine(
                QPointF(
                    centre_x,
                    y,
                ),
                QPointF(
                    centre_x + largeur_locale,
                    y - hauteur * 0.045,
                ),
            )

    # 1.3 -- Dessin complet ----------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine la feuille dans le rectangle fourni."""

        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        # -- Rotation -----------------------------------------------------------

        centre = rect.center()

        painter.translate(centre)
        painter.rotate(self.inclinaison)
        painter.translate(-centre)

        # -- Silhouette ---------------------------------------------------------

        forme = self._creer_forme(rect)

        couleur_base = self.couleur_dessous if self.face_dessous else self.couleur

        sombre = couleur_base.darker(125)
        clair = couleur_base.lighter(122)

        # -- Dégradé du limbe ---------------------------------------------------

        gradient = QLinearGradient(
            rect.left(),
            rect.center().y(),
            rect.right(),
            rect.center().y(),
        )

        if self.face_dessous:

            gradient.setColorAt(
                0.0,
                sombre,
            )

            gradient.setColorAt(
                0.45,
                clair,
            )

            gradient.setColorAt(
                1.0,
                couleur_base,
            )

        else:

            gradient.setColorAt(
                0.0,
                sombre,
            )

            gradient.setColorAt(
                0.35,
                couleur_base,
            )

            gradient.setColorAt(
                0.65,
                clair,
            )

            gradient.setColorAt(
                1.0,
                sombre,
            )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient))

        painter.drawPath(forme)

        # -- Léger contour ------------------------------------------------------

        contour = QColor(sombre)

        contour.setAlpha(80)

        pen_contour = QPen(contour)

        pen_contour.setWidthF(
            max(
                0.4,
                rect.width() * 0.012,
            )
        )

        painter.setPen(pen_contour)

        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawPath(forme)

        # -- Nervures -----------------------------------------------------------

        painter.save()

        painter.setClipPath(forme)

        self._dessiner_nervures(
            painter=painter,
            rect=rect,
            couleur=couleur_base,
        )

        painter.restore()

        # -- Pétiole ------------------------------------------------------------

        couleur_petiole = QColor("#5F6947")

        if self.face_dessous:
            couleur_petiole = QColor("#777C67")

        pen_petiole = QPen(couleur_petiole)

        pen_petiole.setWidthF(
            max(
                0.7,
                rect.width() * 0.04,
            )
        )

        pen_petiole.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(pen_petiole)

        painter.drawLine(
            QPointF(
                rect.center().x() + rect.width() * 0.16 * self.courbure,
                rect.bottom() - rect.height() * 0.01,
            ),
            QPointF(
                rect.center().x() + rect.width() * 0.20 * self.courbure,
                rect.bottom() + rect.height() * 0.10,
            ),
        )

        painter.restore()
