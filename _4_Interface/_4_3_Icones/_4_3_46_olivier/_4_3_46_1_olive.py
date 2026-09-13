################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones/_4_3_46_olivier                                     #
# 4.3.46.1 – Classe de création d'une olive                                    #
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
    QRadialGradient,
)

from _0_Utilitaires._0_2_fonctions_graphiques import interpoler_couleurs

# 1 -- Classe Olive ------------------------------------------------------------


class Olive:
    """
    Représente une olive dont l'apparence dépend de son niveau de maturité.

    maturite :
        0.0 -> olive verte
        0.5 -> olive en cours de maturation
        1.0 -> olive violet-noir très mûre
    """

    def __init__(
        self,
        maturite: float = 0.0,
        inclinaison: float = 0.0,
    ) -> None:

        self.maturite = max(0.0, min(1.0, maturite))
        self.inclinaison = inclinaison

    # 1.1 -- Paramètres ---------------------------------------------------------

    def set_maturite(
        self,
        maturite: float,
    ) -> None:

        self.maturite = max(
            0.0,
            min(1.0, maturite),
        )

    # 1.2 -- Couleur ------------------------------------------------------------

    def _couleur_olive(self) -> QColor:
        """
        Calcule la couleur principale de l'olive selon sa maturité.

        La transition passe progressivement :
            vert -> vert brun -> violet -> violet presque noir.
        """

        vert = QColor("#708A35")
        vert_mur = QColor("#66732F")
        violet = QColor("#514137")
        noir_violet = QColor("#262026")

        m = self.maturite

        if m < 0.35:
            couleurs = [vert, vert_mur]
            poids = m / 0.35

        elif m < 0.70:
            couleurs = [vert_mur, violet]
            poids = (m - 0.35) / 0.35

        else:
            couleurs = [violet, noir_violet]
            poids = (m - 0.70) / 0.30

        # Renvoi de la couleur interpôlé
        return interpoler_couleurs(
            couleurs=couleurs,
            poids=[1 - poids, poids],
            retour="qcolor",
        )

    # 1.3 -- Forme --------------------------------------------------------------

    @staticmethod
    def _creer_forme(
        rect: QRectF,
    ) -> QPainterPath:
        """Crée une forme d'olive légèrement asymétrique."""

        cx = rect.center().x()

        haut = rect.top()
        bas = rect.bottom()

        largeur = rect.width()
        hauteur = rect.height()

        path = QPainterPath()

        path.moveTo(
            QPointF(
                cx - largeur * 0.04,
                haut,
            )
        )

        # Côté droit
        path.cubicTo(
            QPointF(
                cx + largeur * 0.42,
                haut + hauteur * 0.10,
            ),
            QPointF(
                cx + largeur * 0.52,
                haut + hauteur * 0.58,
            ),
            QPointF(
                cx + largeur * 0.15,
                bas,
            ),
        )

        # Bas légèrement pointu
        path.quadTo(
            QPointF(
                cx,
                bas + hauteur * 0.02,
            ),
            QPointF(
                cx - largeur * 0.14,
                bas,
            ),
        )

        # Côté gauche
        path.cubicTo(
            QPointF(
                cx - largeur * 0.48,
                haut + hauteur * 0.65,
            ),
            QPointF(
                cx - largeur * 0.42,
                haut + hauteur * 0.15,
            ),
            QPointF(
                cx - largeur * 0.04,
                haut,
            ),
        )

        path.closeSubpath()

        return path

    # 1.4 -- Dessin -------------------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine l'olive dans le rectangle fourni."""

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

        # -- Forme --------------------------------------------------------------

        forme = self._creer_forme(rect)

        couleur = self._couleur_olive()

        sombre = couleur.darker(155)
        clair = couleur.lighter(135)

        # -- Dégradé principal --------------------------------------------------

        gradient = QLinearGradient(
            rect.left(),
            rect.top(),
            rect.right(),
            rect.bottom(),
        )

        gradient.setColorAt(
            0.0,
            clair,
        )

        gradient.setColorAt(
            0.32,
            couleur,
        )

        gradient.setColorAt(
            0.72,
            couleur.darker(112),
        )

        gradient.setColorAt(
            1.0,
            sombre,
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient))

        painter.drawPath(forme)

        # -- Ombre latérale -----------------------------------------------------

        ombre = QRadialGradient(
            QPointF(
                rect.center().x() + rect.width() * 0.15,
                rect.center().y() + rect.height() * 0.08,
            ),
            rect.width() * 0.7,
        )

        couleur_ombre_centre = QColor(sombre)
        couleur_ombre_centre.setAlpha(0)

        couleur_ombre_bord = QColor(sombre)
        couleur_ombre_bord.setAlpha(110)

        ombre.setColorAt(
            0.0,
            couleur_ombre_centre,
        )

        ombre.setColorAt(
            1.0,
            couleur_ombre_bord,
        )

        painter.save()

        painter.setClipPath(forme)
        painter.setBrush(QBrush(ombre))
        painter.drawRect(rect)

        painter.restore()

        # -- Reflet -------------------------------------------------------------

        reflet = QColor("#FFFFFF")
        reflet.setAlpha(int(55 - self.maturite * 15))

        painter.setBrush(reflet)

        painter.drawEllipse(
            QRectF(
                rect.left() + rect.width() * 0.20,
                rect.top() + rect.height() * 0.17,
                rect.width() * 0.18,
                rect.height() * 0.26,
            )
        )

        # -- Attache supérieure -------------------------------------------------

        couleur_attache = QColor("#42472A")

        pen = QPen(couleur_attache)

        pen.setWidthF(
            max(
                0.7,
                rect.width() * 0.055,
            )
        )

        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(pen)

        painter.drawLine(
            QPointF(
                rect.center().x(),
                rect.top() + rect.height() * 0.03,
            ),
            QPointF(
                rect.center().x() + rect.width() * 0.05,
                rect.top() - rect.height() * 0.09,
            ),
        )

        painter.restore()
