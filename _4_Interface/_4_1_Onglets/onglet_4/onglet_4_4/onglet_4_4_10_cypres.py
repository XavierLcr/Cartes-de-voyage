################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_4                                #
# Onglet 4.4.10 – Classe de création d'un cyprès                               #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math
import random

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)

# 1 -- Classe de création d'un cyprès ------------------------------------------


class Cypres:
    """
    Représente un cyprès méditerranéen stylisé.

    Le cyprès est un objet graphique simple : il n'est pas un QWidget
    et se dessine directement dans un QPainter.
    """

    def __init__(
        self,
        couleur_feuillage: str = "#315A3A",
        couleur_tronc: str = "#6B5140",
        graine: int = 0,
    ):

        self.couleur_feuillage = QColor(couleur_feuillage)
        self.couleur_tronc = QColor(couleur_tronc)

        self.graine = graine

    # 1.1 -- Utilitaires -------------------------------------------------------

    @staticmethod
    def _melanger(
        couleur_1: QColor,
        couleur_2: QColor,
        poids: float,
    ) -> QColor:

        poids = max(0.0, min(1.0, poids))

        return QColor(
            round(couleur_1.red() * (1 - poids) + couleur_2.red() * poids),
            round(couleur_1.green() * (1 - poids) + couleur_2.green() * poids),
            round(couleur_1.blue() * (1 - poids) + couleur_2.blue() * poids),
            round(couleur_1.alpha() * (1 - poids) + couleur_2.alpha() * poids),
        )

    # 1.2 -- Dessin du tronc ---------------------------------------------------

    def _dessiner_tronc(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """
        Dessine un tronc fin et légèrement irrégulier.

        Le pied est très légèrement évasé et le haut du tronc
        disparaît progressivement dans le feuillage.
        """

        centre_x = rect.center().x()

        largeur_base = rect.width() * 0.085
        largeur_haut = rect.width() * 0.040

        hauteur = rect.height() * 0.32

        y_bas = rect.bottom() - rect.height() * 0.015
        y_haut = y_bas - hauteur

        # ------------------------------------------------------------------
        # Forme générale du tronc
        # ------------------------------------------------------------------

        path = QPainterPath()

        path.moveTo(
            centre_x - largeur_base * 0.65,
            y_bas,
        )

        # Côté gauche : pied légèrement évasé puis resserrement
        path.cubicTo(
            centre_x - largeur_base * 0.60,
            y_bas - hauteur * 0.08,
            centre_x - largeur_haut * 0.60,
            y_haut + hauteur * 0.28,
            centre_x - largeur_haut / 2,
            y_haut,
        )

        # Haut du tronc
        path.lineTo(
            centre_x + largeur_haut / 2,
            y_haut,
        )

        # Côté droit
        path.cubicTo(
            centre_x + largeur_haut * 0.55,
            y_haut + hauteur * 0.28,
            centre_x + largeur_base * 0.55,
            y_bas - hauteur * 0.08,
            centre_x + largeur_base * 0.65,
            y_bas,
        )

        # Petite irrégularité du pied
        path.quadTo(
            centre_x,
            y_bas + rect.height() * 0.008,
            centre_x - largeur_base * 0.65,
            y_bas,
        )

        path.closeSubpath()

        # ------------------------------------------------------------------
        # Dégradé du bois
        # ------------------------------------------------------------------

        sombre = self._melanger(
            self.couleur_tronc,
            QColor("#2C211A"),
            0.38,
        )

        clair = self._melanger(
            self.couleur_tronc,
            QColor("#D1A875"),
            0.18,
        )

        gradient = QLinearGradient(
            centre_x - largeur_base,
            0,
            centre_x + largeur_base,
            0,
        )

        gradient.setColorAt(0.0, sombre)
        gradient.setColorAt(0.30, self.couleur_tronc)
        gradient.setColorAt(0.58, clair)
        gradient.setColorAt(1.0, sombre)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))

        painter.drawPath(path)

        # ------------------------------------------------------------------
        # Quelques lignes d'écorce très discrètes
        # ------------------------------------------------------------------

        couleur_ecorce = QColor(sombre)
        couleur_ecorce.setAlpha(65)

        pen = QPen(couleur_ecorce)
        pen.setWidthF(max(0.5, rect.width() * 0.006))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(pen)

        painter.drawLine(
            QPointF(
                centre_x - largeur_base * 0.18,
                y_bas - hauteur * 0.05,
            ),
            QPointF(
                centre_x - largeur_haut * 0.10,
                y_haut + hauteur * 0.38,
            ),
        )

        painter.drawLine(
            QPointF(
                centre_x + largeur_base * 0.22,
                y_bas - hauteur * 0.14,
            ),
            QPointF(
                centre_x + largeur_haut * 0.12,
                y_haut + hauteur * 0.50,
            ),
        )

    # 1.3 -- Silhouette générale ----------------------------------------------

    def _creer_silhouette(
        self,
        rect: QRectF,
    ) -> QPainterPath:

        random.seed(self.graine)

        centre_x = rect.center().x()

        haut = rect.top() + rect.height() * 0.025
        bas = rect.bottom() - rect.height() * 0.10

        hauteur = bas - haut

        largeur_max = rect.width() * 0.72

        n_points = 15

        gauche = []
        droite = []

        for i in range(n_points + 1):

            t = i / n_points

            y = haut + hauteur * t

            # Profil général :
            # très fin au sommet, s'élargit progressivement puis
            # se resserre très légèrement vers la base.
            profil = math.sin(t * math.pi * 0.72)

            profil *= 0.72 + 0.28 * t

            largeur = largeur_max * profil / 2

            # Petites irrégularités naturelles
            irregularite = random.uniform(-0.08, 0.08)

            largeur *= 1 + irregularite

            # Le sommet doit rester très fin
            largeur += rect.width() * 0.018 * t

            gauche.append(
                QPointF(
                    centre_x - largeur,
                    y,
                )
            )

            droite.append(
                QPointF(
                    centre_x + largeur,
                    y,
                )
            )

        path = QPainterPath()

        path.moveTo(
            QPointF(
                centre_x,
                haut,
            )
        )

        for point in droite[1:]:
            path.lineTo(point)

        for point in reversed(gauche):
            path.lineTo(point)

        path.closeSubpath()

        return path

    # 1.4 -- Feuillage ---------------------------------------------------------

    def _dessiner_feuillage(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:

        random.seed(self.graine)

        silhouette = self._creer_silhouette(rect)

        sombre = self._melanger(
            self.couleur_feuillage,
            QColor("#07170D"),
            0.42,
        )

        clair = self._melanger(
            self.couleur_feuillage,
            QColor("#A8C487"),
            0.20,
        )

        # Dégradé principal du feuillage
        gradient = QLinearGradient(
            rect.left(),
            rect.center().y(),
            rect.right(),
            rect.center().y(),
        )

        gradient.setColorAt(0.0, sombre)
        gradient.setColorAt(0.28, self.couleur_feuillage)
        gradient.setColorAt(0.58, clair)
        gradient.setColorAt(0.82, self.couleur_feuillage)
        gradient.setColorAt(1.0, sombre)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawPath(silhouette)

        # Ombre centrale
        ombre = QRadialGradient(
            QPointF(
                rect.center().x() - rect.width() * 0.10,
                rect.center().y(),
            ),
            rect.width() * 0.50,
        )

        ombre.setColorAt(
            0.0,
            QColor(
                sombre.red(),
                sombre.green(),
                sombre.blue(),
                0,
            ),
        )

        ombre.setColorAt(
            1.0,
            QColor(
                sombre.red(),
                sombre.green(),
                sombre.blue(),
                100,
            ),
        )

        painter.save()
        painter.setClipPath(silhouette)
        painter.setBrush(QBrush(ombre))
        painter.drawRect(rect)
        painter.restore()

        # Petites masses de feuillage
        self._dessiner_masses_feuillage(
            painter=painter,
            rect=rect,
            silhouette=silhouette,
            sombre=sombre,
            clair=clair,
        )

    # 1.5 -- Détails du feuillage ---------------------------------------------

    def _dessiner_masses_feuillage(
        self,
        painter: QPainter,
        rect: QRectF,
        silhouette: QPainterPath,
        sombre: QColor,
        clair: QColor,
    ) -> None:

        random.seed(self.graine + 17)

        painter.save()
        painter.setClipPath(silhouette)
        painter.setPen(Qt.PenStyle.NoPen)

        n_masses = 45

        for _ in range(n_masses):

            t = random.uniform(0.10, 0.96)

            y = rect.top() + rect.height() * t

            # Largeur disponible approximative selon la hauteur
            profil = math.sin(t * math.pi * 0.72)
            profil *= 0.72 + 0.28 * t

            demi_largeur = rect.width() * 0.34 * profil

            x = rect.center().x() + random.uniform(
                -demi_largeur,
                demi_largeur,
            )

            largeur = rect.width() * random.uniform(
                0.08,
                0.20,
            )

            hauteur = rect.height() * random.uniform(
                0.025,
                0.065,
            )

            # La partie gauche reçoit davantage d'ombre,
            # la partie droite davantage de lumière.
            position_x = (x - rect.center().x()) / max(1, rect.width() / 2)

            if position_x < -0.15:

                couleur = sombre

            elif position_x > 0.15:

                couleur = clair

            else:

                couleur = self.couleur_feuillage

            couleur = QColor(couleur)
            couleur.setAlpha(random.randint(35, 90))

            painter.setBrush(couleur)

            painter.drawEllipse(
                QRectF(
                    x - largeur / 2,
                    y - hauteur / 2,
                    largeur,
                    hauteur,
                )
            )

        painter.restore()

    # 1.6 -- Pointe ------------------------------------------------------------

    def _dessiner_pointe(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """
        Ajoute quelques petites branches à la pointe pour éviter
        une terminaison trop géométrique.
        """

        sommet = QPointF(
            rect.center().x(),
            rect.top() + rect.height() * 0.025,
        )

        couleur = self._melanger(
            self.couleur_feuillage,
            QColor("#101C12"),
            0.25,
        )

        pen = QPen(couleur)
        pen.setWidthF(max(1.0, rect.width() * 0.018))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(pen)

        painter.drawLine(
            sommet,
            QPointF(
                sommet.x() - rect.width() * 0.025,
                sommet.y() + rect.height() * 0.075,
            ),
        )

        painter.drawLine(
            sommet,
            QPointF(
                sommet.x() + rect.width() * 0.020,
                sommet.y() + rect.height() * 0.065,
            ),
        )

    # 1.7 -- Dessin complet ----------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """
        Dessine le cyprès dans le rectangle fourni.

        Le bas du rectangle correspond au niveau du sol.
        """

        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._dessiner_tronc(
            painter=painter,
            rect=rect,
        )

        self._dessiner_feuillage(
            painter=painter,
            rect=rect,
        )

        self._dessiner_pointe(
            painter=painter,
            rect=rect,
        )

        painter.restore()
