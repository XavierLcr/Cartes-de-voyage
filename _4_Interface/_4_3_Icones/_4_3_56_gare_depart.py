################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.56 – Classe de création d'une gare de départ / arrivée                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QRadialGradient,
)

# 1 -- Fonctions utilitaires ---------------------------------------------------


def _qcolor(couleur: QColor | str) -> QColor:
    """Convertit une couleur en QColor."""
    return couleur if isinstance(couleur, QColor) else QColor(couleur)


def _melanger(
    c1: QColor | str,
    c2: QColor | str,
    t: float,
) -> QColor:
    """
    Mélange linéaire de deux couleurs.

    `t=0` => c1
    `t=1` => c2
    """

    c1 = _qcolor(c1)
    c2 = _qcolor(c2)

    t = max(0.0, min(1.0, t))

    return QColor(
        round(c1.red() * (1 - t) + c2.red() * t),
        round(c1.green() * (1 - t) + c2.green() * t),
        round(c1.blue() * (1 - t) + c2.blue() * t),
        round(c1.alpha() * (1 - t) + c2.alpha() * t),
    )


def _eclaircir(
    couleur: QColor | str,
    facteur: float = 0.15,
) -> QColor:
    """Éclaircit une couleur en la rapprochant du blanc."""
    return _melanger(couleur, "#FFFFFF", facteur)


def _assombrir(
    couleur: QColor | str,
    facteur: float = 0.15,
) -> QColor:
    """Assombrit une couleur en la rapprochant du noir."""
    return _melanger(couleur, "#000000", facteur)


def _avec_alpha(
    couleur: QColor | str,
    alpha: int,
) -> QColor:
    """Retourne la couleur avec un alpha imposé."""
    c = _qcolor(couleur)
    c.setAlpha(max(0, min(255, alpha)))
    return c


# 2 -- Classe de gare départ / arrivée -----------------------------------------


class GareDepartArrivee:
    """
    Gare de départ / arrivée totalement autonome.

    Style choisi :
        terminus ferroviaire art déco avec grande verrière et façade
        monumentale.

    Sens :
        sens = 1
            façade fermée à gauche, sortie vers la droite
        sens = -1
            façade fermée à droite, sortie vers la gauche

    Utilisation :
        - `peindre_arriere(...)` dessine ce qui est derrière le train
        - `peindre_avant(...)` dessine ce qui est devant le train
    """

    masque_paysage = True
    masque_rails = True

    def __init__(
        self,
        sens: int = 1,
        couleur_mur: QColor | str = "#D8CCB6",
        couleur_mur_fonce: QColor | str = "#B79F84",
        couleur_metal: QColor | str = "#6B767D",
        couleur_metal_fonce: QColor | str = "#465056",
        couleur_verre: QColor | str = "#C9DEE6",
        couleur_quai: QColor | str = "#A8957F",
        couleur_bord_quai: QColor | str = "#E8DECF",
        couleur_bois: QColor | str = "#6E5845",
        couleur_laiton: QColor | str = "#B79A5B",
        couleur_enseigne: QColor | str = "#23404B",
        lampes_allumees: bool = True,
        etat_feu: str = "vert",
    ):
        self.sens = 1 if sens >= 0 else -1

        self.couleur_mur = _qcolor(couleur_mur)
        self.couleur_mur_fonce = _qcolor(couleur_mur_fonce)
        self.couleur_metal = _qcolor(couleur_metal)
        self.couleur_metal_fonce = _qcolor(couleur_metal_fonce)
        self.couleur_verre = _qcolor(couleur_verre)
        self.couleur_quai = _qcolor(couleur_quai)
        self.couleur_bord_quai = _qcolor(couleur_bord_quai)
        self.couleur_bois = _qcolor(couleur_bois)
        self.couleur_laiton = _qcolor(couleur_laiton)
        self.couleur_enseigne = _qcolor(couleur_enseigne)

        self.lampes_allumees = lampes_allumees
        self.etat_feu = etat_feu

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    def largeur_recommandee(
        self,
        hauteur_scene: float,
    ) -> float:
        """
        Largeur recommandée.

        On garde une gare assez longue pour avoir :
            - un vrai fond de terminus ;
            - une sortie lisible ;
            - de la place pour le train.
        """
        return hauteur_scene * 3.55

    def _x(
        self,
        rect: QRectF,
        proportion: float,
    ) -> float:
        """
        Coordonnée x normalisée selon le sens.

        Ex. proportion=0.20 :
            - 20 % depuis la gauche si sens=1
            - 20 % depuis la droite si sens=-1
        """

        if self.sens > 0:
            return rect.left() + rect.width() * proportion

        return rect.right() - rect.width() * proportion

    def _rect_norm(
        self,
        rect: QRectF,
        x: float,
        y: float,
        w: float,
        h: float,
    ) -> QRectF:
        """
        Crée un QRectF à partir de proportions [0..1], en tenant compte du sens.

        `x` est défini dans le repère naturel du départ :
            petit x = côté façade monumentale
            grand x = côté sortie
        """

        if self.sens > 0:
            return QRectF(
                rect.left() + rect.width() * x,
                rect.top() + rect.height() * y,
                rect.width() * w,
                rect.height() * h,
            )

        return QRectF(
            rect.right() - rect.width() * (x + w),
            rect.top() + rect.height() * y,
            rect.width() * w,
            rect.height() * h,
        )

    def _y_quai(
        self,
        rect: QRectF,
        y_rail: float | None,
    ) -> float:
        """
        Détermine le niveau du quai.

        Si `y_rail` est fourni, on s'aligne proprement dessus.
        Sinon on prend une valeur cohérente par défaut.
        """

        if y_rail is None:
            return rect.bottom() - rect.height() * 0.18

        return y_rail - rect.height() * 0.035

    # --------------------------------------------------------------------------
    # Petits outils de dessin
    # --------------------------------------------------------------------------

    def _dessiner_ombre_rect(
        self,
        painter: QPainter,
        rect: QRectF,
        rayon: float,
        decalage: float,
        alpha: int = 55,
    ) -> None:
        """Dessine une ombre douce derrière un rectangle arrondi."""

        rect_ombre = QRectF(
            rect.left() + decalage,
            rect.top() + decalage,
            rect.width(),
            rect.height(),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, alpha))
        painter.drawRoundedRect(rect_ombre, rayon, rayon)

    def _dessiner_ligne_artdeco(
        self,
        painter: QPainter,
        rect: QRectF,
        n: int = 9,
    ) -> None:
        """
        Dessine une petite frise géométrique art déco.
        """

        if n <= 0 or rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha(self.couleur_laiton, 185))

        pas = rect.width() / n

        for i in range(n):
            x0 = rect.left() + i * pas
            x1 = x0 + pas / 2
            x2 = x0 + pas

            yb = rect.bottom()
            yh = rect.top()

            poly = QPolygonF(
                [
                    QPointF(x0, yb),
                    QPointF(x1, yh),
                    QPointF(x2, yb),
                    QPointF(x1, yb - rect.height() * 0.22),
                ]
            )

            painter.drawPolygon(poly)

        painter.restore()

    # --------------------------------------------------------------------------
    # Fond général
    # --------------------------------------------------------------------------

    def _dessiner_fond_general(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """
        Dessine le fond général intérieur de la gare :
            - haut plus lumineux ;
            - bas plus chaud ;
            - ambiance intérieure de hall ferroviaire.
        """

        fond = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        fond.setColorAt(0.00, _eclaircir(self.couleur_mur, 0.10))
        fond.setColorAt(0.38, self.couleur_mur)
        fond.setColorAt(1.00, _assombrir(self.couleur_mur, 0.06))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(fond))
        painter.drawRect(rect)

        # Voile léger dans la partie basse pour renforcer la profondeur
        rect_bas = QRectF(
            rect.left(),
            y_quai - rect.height() * 0.18,
            rect.width(),
            rect.height() * 0.18,
        )

        grad_bas = QLinearGradient(rect_bas.topLeft(), rect_bas.bottomLeft())
        grad_bas.setColorAt(0.0, _avec_alpha(self.couleur_mur_fonce, 40))
        grad_bas.setColorAt(1.0, _avec_alpha(self.couleur_mur_fonce, 115))

        painter.setBrush(QBrush(grad_bas))
        painter.drawRect(rect_bas)

    # --------------------------------------------------------------------------
    # Sol et quai arrière
    # --------------------------------------------------------------------------

    def _dessiner_quai_interieur(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """
        Dessine le quai visible derrière le train :
            - bande principale ;
            - bord clair ;
            - joints de dallage.
        """

        h = rect.height()

        rect_quai = QRectF(
            rect.left(),
            y_quai - h * 0.11,
            rect.width(),
            h * 0.11,
        )

        grad = QLinearGradient(rect_quai.topLeft(), rect_quai.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_quai, 0.10))
        grad.setColorAt(1.0, _assombrir(self.couleur_quai, 0.08))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(rect_quai)

        # Bande de sécurité claire
        rect_bord = QRectF(
            rect.left(),
            y_quai - h * 0.028,
            rect.width(),
            h * 0.028,
        )

        grad_bord = QLinearGradient(rect_bord.topLeft(), rect_bord.bottomLeft())
        grad_bord.setColorAt(0.0, _eclaircir(self.couleur_bord_quai, 0.10))
        grad_bord.setColorAt(1.0, _assombrir(self.couleur_bord_quai, 0.05))

        painter.setBrush(QBrush(grad_bord))
        painter.drawRect(rect_bord)

        # Joints horizontaux
        pen_joint = QPen(_avec_alpha(_assombrir(self.couleur_quai, 0.22), 105))
        pen_joint.setWidthF(max(1.0, h * 0.0026))
        painter.setPen(pen_joint)

        y1 = rect_quai.top() + rect_quai.height() * 0.38
        y2 = rect_quai.top() + rect_quai.height() * 0.68

        painter.drawLine(QPointF(rect.left(), y1), QPointF(rect.right(), y1))
        painter.drawLine(QPointF(rect.left(), y2), QPointF(rect.right(), y2))

        # Dallage vertical espacé
        for p in (0.07, 0.18, 0.31, 0.44, 0.58, 0.72, 0.84, 0.94):
            x = rect.left() + rect.width() * p
            painter.drawLine(
                QPointF(x, rect_quai.top() + rect_quai.height() * 0.30),
                QPointF(x, y_quai),
            )

    # --------------------------------------------------------------------------
    # Grande verrière
    # --------------------------------------------------------------------------

    def _dessiner_verriere(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """
        Dessine la grande verrière centrale.

        On vise un rendu plus prestigieux que la gare ancienne :
            - grande baie cintrée ;
            - montants métalliques ;
            - travées latérales ;
            - lumière diffuse.
        """

        h = rect.height()

        rect_verriere = self._rect_norm(
            rect,
            0.20,
            0.06,
            0.58,
            0.58,
        )

        rect_verriere.setBottom(y_quai - h * 0.01)

        # Fond de lumière
        fond = QLinearGradient(
            rect_verriere.topLeft(),
            rect_verriere.bottomLeft(),
        )
        fond.setColorAt(0.0, _eclaircir(self.couleur_verre, 0.34))
        fond.setColorAt(0.45, self.couleur_verre)
        fond.setColorAt(1.0, _assombrir(self.couleur_verre, 0.15))

        # Forme principale avec sommet cintré
        xg = rect_verriere.left()
        xd = rect_verriere.right()
        yh = rect_verriere.top()
        yb = rect_verriere.bottom()
        yc = yh + rect_verriere.height() * 0.22

        path = QPainterPath()
        path.moveTo(xg, yb)
        path.lineTo(xg, yc)
        path.quadTo(
            QPointF(rect_verriere.center().x(), yh - rect_verriere.height() * 0.10),
            QPointF(xd, yc),
        )
        path.lineTo(xd, yb)
        path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(fond))
        painter.drawPath(path)

        # Structure métallique extérieure
        pen_ext = QPen(self.couleur_metal_fonce)
        pen_ext.setWidthF(max(2.0, h * 0.010))
        painter.setPen(pen_ext)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Contre-cadre intérieur
        marge = h * 0.018

        path_int = QPainterPath()
        path_int.moveTo(xg + marge, yb)
        path_int.lineTo(xg + marge, yc + marge * 0.4)
        path_int.quadTo(
            QPointF(rect_verriere.center().x(), yh - rect_verriere.height() * 0.03),
            QPointF(xd - marge, yc + marge * 0.4),
        )
        path_int.lineTo(xd - marge, yb)

        pen_int = QPen(_avec_alpha(self.couleur_metal, 170))
        pen_int.setWidthF(max(1.0, h * 0.0045))
        painter.setPen(pen_int)
        painter.drawPath(path_int)

        # Montants verticaux
        pen_montants = QPen(self.couleur_metal)
        pen_montants.setWidthF(max(1.0, h * 0.0042))
        painter.setPen(pen_montants)

        proportions = [0.10, 0.22, 0.35, 0.50, 0.65, 0.78, 0.90]

        for p in proportions:
            x = rect_verriere.left() + rect_verriere.width() * p

            # hauteur approchée sous l'arc
            dx = abs(p - 0.5) / 0.5
            y_haut = yh + rect_verriere.height() * (0.18 * dx * dx + 0.02)

            painter.drawLine(
                QPointF(x, yb),
                QPointF(x, y_haut),
            )

        # Traverse horizontale principale
        y_tr = rect_verriere.top() + rect_verriere.height() * 0.43
        painter.drawLine(
            QPointF(rect_verriere.left(), y_tr),
            QPointF(rect_verriere.right(), y_tr),
        )

        # Reflets
        pen_reflet = QPen(_avec_alpha("#FFFFFF", 80))
        pen_reflet.setWidthF(max(1.0, h * 0.003))
        painter.setPen(pen_reflet)

        for p in (0.18, 0.30, 0.43):
            x = rect_verriere.left() + rect_verriere.width() * p
            painter.drawLine(
                QPointF(x, yh + rect_verriere.height() * 0.10),
                QPointF(
                    x + rect_verriere.width() * 0.06, yb - rect_verriere.height() * 0.10
                ),
            )

        # Frise basse
        rect_frise = QRectF(
            rect_verriere.left(),
            yb - h * 0.028,
            rect_verriere.width(),
            h * 0.018,
        )

        self._dessiner_ligne_artdeco(
            painter,
            rect_frise,
            n=11,
        )

    # --------------------------------------------------------------------------
    # Façade de terminus
    # --------------------------------------------------------------------------

    def _dessiner_facade_terminus(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """
        Dessine la façade fermée du terminus, plus affirmée que dans l'ancienne.

        On y met :
            - un grand panneau mural monumental ;
            - un fronton géométrique ;
            - une niche décorative ;
            - une porte de service ;
            - une horloge.
        """

        h = rect.height()

        rect_facade = self._rect_norm(
            rect,
            0.02,
            0.09,
            0.20,
            0.56,
        )
        rect_facade.setBottom(y_quai)

        # Panneau mural principal
        grad = QLinearGradient(rect_facade.topLeft(), rect_facade.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_mur, 0.08))
        grad.setColorAt(0.55, self.couleur_mur)
        grad.setColorAt(1.0, _assombrir(self.couleur_mur_fonce, 0.08))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(
            rect_facade,
            h * 0.020,
            h * 0.020,
        )

        # Encadrement
        pen_cadre = QPen(_assombrir(self.couleur_mur_fonce, 0.20))
        pen_cadre.setWidthF(max(1.0, h * 0.005))
        painter.setPen(pen_cadre)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(
            rect_facade.adjusted(h * 0.004, h * 0.004, -h * 0.004, -h * 0.004),
            h * 0.017,
            h * 0.017,
        )

        # Fronton art déco
        xg = rect_facade.left() + rect_facade.width() * 0.10
        xd = rect_facade.right() - rect_facade.width() * 0.10
        yb = rect_facade.top() + rect_facade.height() * 0.17
        ym = rect_facade.top() + rect_facade.height() * 0.04
        yc = rect_facade.center().x()

        poly_fronton = QPolygonF(
            [
                QPointF(xg, yb),
                QPointF(xg + rect_facade.width() * 0.10, yb),
                QPointF(
                    xg + rect_facade.width() * 0.10, yb - rect_facade.height() * 0.06
                ),
                QPointF(
                    yc - rect_facade.width() * 0.09, yb - rect_facade.height() * 0.06
                ),
                QPointF(yc - rect_facade.width() * 0.09, ym),
                QPointF(yc + rect_facade.width() * 0.09, ym),
                QPointF(
                    yc + rect_facade.width() * 0.09, yb - rect_facade.height() * 0.06
                ),
                QPointF(
                    xd - rect_facade.width() * 0.10, yb - rect_facade.height() * 0.06
                ),
                QPointF(xd - rect_facade.width() * 0.10, yb),
                QPointF(xd, yb),
            ]
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_assombrir(self.couleur_mur_fonce, 0.04))
        painter.drawPolygon(poly_fronton)

        # Niche décorative centrale
        rect_niche = QRectF(
            rect_facade.left() + rect_facade.width() * 0.20,
            rect_facade.top() + rect_facade.height() * 0.23,
            rect_facade.width() * 0.60,
            rect_facade.height() * 0.33,
        )

        grad_niche = QLinearGradient(rect_niche.topLeft(), rect_niche.bottomLeft())
        grad_niche.setColorAt(0.0, _assombrir(self.couleur_mur, 0.14))
        grad_niche.setColorAt(1.0, _assombrir(self.couleur_mur_fonce, 0.08))

        painter.setBrush(QBrush(grad_niche))
        painter.setPen(
            QPen(_assombrir(self.couleur_mur_fonce, 0.25), max(1.0, h * 0.004))
        )
        painter.drawRoundedRect(rect_niche, h * 0.014, h * 0.014)

        # Éventail métallique dans la niche
        centre_eventail = QPointF(
            rect_niche.center().x(),
            rect_niche.bottom() - rect_niche.height() * 0.08,
        )

        pen_eventail = QPen(_avec_alpha(self.couleur_laiton, 180))
        pen_eventail.setWidthF(max(1.0, h * 0.0032))
        painter.setPen(pen_eventail)

        for angle in range(-70, 71, 14):
            rad = math.radians(angle)
            x = centre_eventail.x() + math.cos(rad) * rect_niche.width() * 0.34
            y = centre_eventail.y() - math.sin(rad) * rect_niche.height() * 0.78
            painter.drawLine(centre_eventail, QPointF(x, y))

        # Porte de service
        rect_porte = QRectF(
            rect_facade.left() + rect_facade.width() * 0.36,
            y_quai - rect.height() * 0.17,
            rect_facade.width() * 0.28,
            rect.height() * 0.17,
        )

        grad_porte = QLinearGradient(rect_porte.topLeft(), rect_porte.topRight())
        grad_porte.setColorAt(0.0, _assombrir(self.couleur_bois, 0.08))
        grad_porte.setColorAt(0.5, self.couleur_bois)
        grad_porte.setColorAt(1.0, _assombrir(self.couleur_bois, 0.18))

        painter.setPen(QPen(_assombrir(self.couleur_bois, 0.35), max(1.0, h * 0.004)))
        painter.setBrush(QBrush(grad_porte))
        painter.drawRoundedRect(rect_porte, h * 0.009, h * 0.009)

        # Montants de porte
        pen_porte = QPen(_avec_alpha(_eclaircir(self.couleur_bois, 0.08), 130))
        pen_porte.setWidthF(max(1.0, h * 0.0025))
        painter.setPen(pen_porte)

        x1 = rect_porte.left() + rect_porte.width() * 0.33
        x2 = rect_porte.left() + rect_porte.width() * 0.66
        painter.drawLine(
            QPointF(x1, rect_porte.top()), QPointF(x1, rect_porte.bottom())
        )
        painter.drawLine(
            QPointF(x2, rect_porte.top()), QPointF(x2, rect_porte.bottom())
        )

        # Poignée
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.couleur_laiton)
        painter.drawEllipse(
            QPointF(
                rect_porte.right() - rect_porte.width() * 0.18,
                rect_porte.center().y(),
            ),
            h * 0.0055,
            h * 0.0055,
        )

        # Horloge
        self._dessiner_horloge(
            painter,
            centre=QPointF(
                rect_facade.center().x(),
                rect_facade.top() + rect_facade.height() * 0.18,
            ),
            rayon=h * 0.052,
        )

    # --------------------------------------------------------------------------
    # Horloge
    # --------------------------------------------------------------------------

    def _dessiner_horloge(
        self,
        painter: QPainter,
        centre: QPointF,
        rayon: float,
    ) -> None:
        """Dessine une horloge stylisée autonome."""

        if rayon <= 0:
            return

        painter.save()

        rect = QRectF(
            centre.x() - rayon,
            centre.y() - rayon,
            2 * rayon,
            2 * rayon,
        )

        self._dessiner_ombre_rect(
            painter,
            rect.adjusted(rayon * 0.12, rayon * 0.12, -rayon * 0.12, -rayon * 0.12),
            rayon * 0.24,
            rayon * 0.07,
            alpha=45,
        )

        # Couronne
        painter.setPen(
            QPen(_assombrir(self.couleur_metal_fonce, 0.18), max(1.0, rayon * 0.18))
        )
        painter.setBrush(_melanger(self.couleur_laiton, "#D7C39A", 0.30))
        painter.drawEllipse(rect)

        # Fond
        painter.setPen(
            QPen(_assombrir(self.couleur_metal_fonce, 0.25), max(1.0, rayon * 0.05))
        )
        painter.setBrush(QColor("#F8F4EA"))
        painter.drawEllipse(
            rect.adjusted(rayon * 0.14, rayon * 0.14, -rayon * 0.14, -rayon * 0.14)
        )

        # Index
        painter.setPen(QPen(QColor("#333333"), max(1.0, rayon * 0.05)))

        for heure in range(12):
            angle = math.radians(heure * 30 - 90)
            r1 = rayon * 0.58
            r2 = rayon * 0.76
            p1 = QPointF(
                centre.x() + math.cos(angle) * r1, centre.y() + math.sin(angle) * r1
            )
            p2 = QPointF(
                centre.x() + math.cos(angle) * r2, centre.y() + math.sin(angle) * r2
            )
            painter.drawLine(p1, p2)

        # Aiguilles fixes
        pen_aig = QPen(QColor("#2D3336"), max(1.0, rayon * 0.08))
        pen_aig.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_aig)

        # ~10h10
        angle_h = math.radians(10 * 30 + 5 - 90)
        angle_m = math.radians(10 * 6 - 90)

        painter.drawLine(
            centre,
            QPointF(
                centre.x() + math.cos(angle_h) * rayon * 0.34,
                centre.y() + math.sin(angle_h) * rayon * 0.34,
            ),
        )

        painter.drawLine(
            centre,
            QPointF(
                centre.x() + math.cos(angle_m) * rayon * 0.55,
                centre.y() + math.sin(angle_m) * rayon * 0.55,
            ),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#2D3336"))
        painter.drawEllipse(centre, rayon * 0.08, rayon * 0.08)

        painter.restore()

    # --------------------------------------------------------------------------
    # Ouverture vers les voies
    # --------------------------------------------------------------------------

    def _dessiner_sortie(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """
        Dessine l'ouverture côté départ / arrivée.

        Elle est plus haute et plus noble qu'une simple arche :
            - grand portail cintré ;
            - lumière extérieure ;
            - double encadrement métallique.
        """

        h = rect.height()

        rect_sortie = self._rect_norm(
            rect,
            0.80,
            0.14,
            0.16,
            0.49,
        )
        rect_sortie.setBottom(y_quai)

        xg = rect_sortie.left()
        xd = rect_sortie.right()
        yc = rect_sortie.center().x()
        yh = rect_sortie.top()
        yb = rect_sortie.bottom()
        y_arc = yh + rect_sortie.height() * 0.25

        path = QPainterPath()
        path.moveTo(xg, yb)
        path.lineTo(xg, y_arc)
        path.quadTo(
            QPointF(yc, yh - rect_sortie.height() * 0.10),
            QPointF(xd, y_arc),
        )
        path.lineTo(xd, yb)
        path.closeSubpath()

        grad = QLinearGradient(QPointF(xg, yh), QPointF(xg, yb))
        grad.setColorAt(0.0, QColor("#E7F0F3"))
        grad.setColorAt(0.45, QColor("#C5D8DE"))
        grad.setColorAt(1.0, QColor("#8B9EA4"))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawPath(path)

        # Halo extérieur
        rect_halo = rect_sortie.adjusted(-h * 0.020, -h * 0.020, h * 0.020, 0)
        halo = QRadialGradient(
            QPointF(
                rect_halo.center().x(), rect_halo.top() + rect_halo.height() * 0.26
            ),
            rect_halo.width() * 0.65,
        )
        halo.setColorAt(0.0, QColor(255, 255, 255, 85))
        halo.setColorAt(1.0, QColor(255, 255, 255, 0))

        painter.setBrush(QBrush(halo))
        painter.drawPath(path)

        # Encadrements
        pen_ext = QPen(self.couleur_metal_fonce)
        pen_ext.setWidthF(max(2.0, h * 0.010))
        painter.setPen(pen_ext)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        decalage = h * 0.017
        path_int = QPainterPath()
        path_int.moveTo(xg + decalage, yb)
        path_int.lineTo(xg + decalage, y_arc + decalage * 0.2)
        path_int.quadTo(
            QPointF(yc, yh - rect_sortie.height() * 0.01),
            QPointF(xd - decalage, y_arc + decalage * 0.2),
        )
        path_int.lineTo(xd - decalage, yb)

        pen_int = QPen(_avec_alpha(self.couleur_metal, 180))
        pen_int.setWidthF(max(1.0, h * 0.004))
        painter.setPen(pen_int)
        painter.drawPath(path_int)

        # Léger trait de perspective au sol
        pen_sol = QPen(_avec_alpha(QColor("#FFFFFF"), 100))
        pen_sol.setWidthF(max(1.0, h * 0.003))
        painter.setPen(pen_sol)

        for frac in (0.18, 0.36, 0.54, 0.72):
            x1 = rect_sortie.left() + rect_sortie.width() * frac
            painter.drawLine(
                QPointF(x1, yb - h * 0.005),
                QPointF(yc, yh + rect_sortie.height() * 0.16),
            )

    # --------------------------------------------------------------------------
    # Banc
    # --------------------------------------------------------------------------

    def _dessiner_banc(
        self,
        painter: QPainter,
        rect_banc: QRectF,
    ) -> None:
        """Dessine un banc discret mais détaillé."""

        h = rect_banc.height()

        painter.save()

        # Assise
        rect_assise = QRectF(
            rect_banc.left(),
            rect_banc.top() + h * 0.36,
            rect_banc.width(),
            h * 0.18,
        )

        grad_assise = QLinearGradient(rect_assise.topLeft(), rect_assise.bottomLeft())
        grad_assise.setColorAt(0.0, _eclaircir(self.couleur_bois, 0.12))
        grad_assise.setColorAt(1.0, _assombrir(self.couleur_bois, 0.15))

        painter.setPen(QPen(_assombrir(self.couleur_bois, 0.30), max(1.0, h * 0.03)))
        painter.setBrush(QBrush(grad_assise))
        painter.drawRoundedRect(rect_assise, h * 0.06, h * 0.06)

        # Dossier
        rect_dossier = QRectF(
            rect_banc.left() + rect_banc.width() * 0.08,
            rect_banc.top() + h * 0.06,
            rect_banc.width() * 0.84,
            h * 0.18,
        )

        painter.drawRoundedRect(rect_dossier, h * 0.05, h * 0.05)

        # Lattes
        pen_lattes = QPen(_avec_alpha(_eclaircir(self.couleur_bois, 0.12), 110))
        pen_lattes.setWidthF(max(1.0, h * 0.015))
        painter.setPen(pen_lattes)

        for frac in (0.24, 0.50, 0.76):
            x = rect_banc.left() + rect_banc.width() * frac
            painter.drawLine(
                QPointF(x, rect_assise.top()),
                QPointF(x, rect_assise.bottom()),
            )

        # Pieds
        pen_pieds = QPen(self.couleur_metal_fonce, max(1.0, h * 0.045))
        pen_pieds.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_pieds)

        for frac in (0.20, 0.80):
            x = rect_banc.left() + rect_banc.width() * frac
            painter.drawLine(
                QPointF(x, rect_assise.bottom()),
                QPointF(x - rect_banc.width() * 0.03, rect_banc.bottom()),
            )

        painter.restore()

    # --------------------------------------------------------------------------
    # Signal
    # --------------------------------------------------------------------------

    def _dessiner_feu(
        self,
        painter: QPainter,
        rect: QRectF,
        etat: str = "vert",
    ) -> None:
        """
        Dessine un petit signal ferroviaire stylisé.
        """

        h = rect.height()

        painter.save()

        # Mât
        pen_mat = QPen(self.couleur_metal_fonce)
        pen_mat.setWidthF(max(2.0, h * 0.045))
        pen_mat.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_mat)

        x_mat = rect.left() + rect.width() * 0.30
        painter.drawLine(
            QPointF(x_mat, rect.bottom()),
            QPointF(x_mat, rect.top() + rect.height() * 0.06),
        )

        # Tête
        rect_tete = QRectF(
            rect.left() + rect.width() * 0.40,
            rect.top() + rect.height() * 0.02,
            rect.width() * 0.44,
            rect.height() * 0.48,
        )

        grad = QLinearGradient(rect_tete.topLeft(), rect_tete.bottomLeft())
        grad.setColorAt(0.0, QColor("#51585C"))
        grad.setColorAt(1.0, QColor("#353A3D"))

        painter.setPen(QPen(QColor("#262A2D"), max(1.0, h * 0.02)))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect_tete, h * 0.05, h * 0.05)

        # Feux
        positions = {
            "rouge": rect_tete.top() + rect_tete.height() * 0.22,
            "orange": rect_tete.top() + rect_tete.height() * 0.50,
            "vert": rect_tete.top() + rect_tete.height() * 0.78,
        }

        rayon = rect_tete.width() * 0.18

        for nom, y in positions.items():
            actif = (etat or "").lower() == nom

            if nom == "rouge":
                couleur = QColor("#D64949")
            elif nom == "orange":
                couleur = QColor("#E2A23C")
            else:
                couleur = QColor("#46B766")

            painter.setPen(Qt.PenStyle.NoPen)

            if actif:
                halo = QRadialGradient(
                    QPointF(rect_tete.center().x(), y),
                    rayon * 2.2,
                )
                halo.setColorAt(0.0, _avec_alpha(couleur, 130))
                halo.setColorAt(1.0, _avec_alpha(couleur, 0))
                painter.setBrush(QBrush(halo))
                painter.drawEllipse(
                    QPointF(rect_tete.center().x(), y), rayon * 2.2, rayon * 2.2
                )
                painter.setBrush(couleur)
            else:
                painter.setBrush(_assombrir(couleur, 0.55))

            painter.drawEllipse(
                QPointF(rect_tete.center().x(), y),
                rayon,
                rayon,
            )

        painter.restore()

    # --------------------------------------------------------------------------
    # Lampes suspendues
    # --------------------------------------------------------------------------

    def _dessiner_lampes(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """
        Dessine des suspensions sous la verrière.
        """

        h = rect.height()

        y_accroche = rect.top() + h * 0.12
        y_lampe = rect.top() + h * 0.25

        pen_fil = QPen(_avec_alpha(self.couleur_metal_fonce, 180))
        pen_fil.setWidthF(max(1.0, h * 0.0026))
        painter.setPen(pen_fil)

        for p in (0.35, 0.50, 0.65):
            x = self._x(rect, p)
            painter.drawLine(
                QPointF(x, y_accroche),
                QPointF(x, y_lampe - h * 0.020),
            )

            # Chapeau
            rect_chapeau = QRectF(
                x - h * 0.018,
                y_lampe - h * 0.020,
                h * 0.036,
                h * 0.015,
            )

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self.couleur_metal)
            painter.drawRoundedRect(rect_chapeau, h * 0.005, h * 0.005)

            # Globe
            centre = QPointF(x, y_lampe + h * 0.010)
            rayon = h * 0.016

            if self.lampes_allumees:
                halo = QRadialGradient(centre, rayon * 2.8)
                halo.setColorAt(0.0, QColor(255, 235, 185, 95))
                halo.setColorAt(1.0, QColor(255, 235, 185, 0))
                painter.setBrush(QBrush(halo))
                painter.drawEllipse(centre, rayon * 2.8, rayon * 2.8)

                painter.setBrush(QColor("#F6E3B1"))
            else:
                painter.setBrush(QColor("#C7D1D6"))

            painter.drawEllipse(centre, rayon, rayon)

    # --------------------------------------------------------------------------
    # Enseigne pays
    # --------------------------------------------------------------------------

    def _dessiner_panneau_nom(
        self,
        painter: QPainter,
        rect: QRectF,
        texte: str,
    ) -> None:
        """
        Dessine un panneau principal de gare.
        """

        h = rect.height()

        self._dessiner_ombre_rect(
            painter,
            rect,
            h * 0.06,
            h * 0.02,
            alpha=45,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.couleur_enseigne)
        painter.drawRoundedRect(rect, h * 0.05, h * 0.05)

        marge = h * 0.02
        rect_interieur = rect.adjusted(marge, marge, -marge, -marge)

        painter.setPen(QPen(_eclaircir(self.couleur_laiton, 0.12), max(1.0, h * 0.01)))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect_interieur, h * 0.04, h * 0.04)

        font = QFont(painter.font())
        font.setBold(True)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, max(0.5, h * 0.010))
        font.setPointSizeF(max(8.0, h * 0.075))
        painter.setFont(font)

        painter.setPen(QColor("#F5EEE0"))
        painter.drawText(
            rect_interieur.adjusted(h * 0.03, 0, -h * 0.03, 0),
            Qt.AlignmentFlag.AlignCenter,
            texte,
        )

    # --------------------------------------------------------------------------
    # Plaque progression
    # --------------------------------------------------------------------------

    def _dessiner_plaque_progression(
        self,
        painter: QPainter,
        rect: QRectF,
        i: int,
        n: int,
    ) -> None:
        """
        Dessine une petite plaque de progression `i / n`.
        """

        h = rect.height()

        self._dessiner_ombre_rect(
            painter,
            rect,
            h * 0.06,
            h * 0.02,
            alpha=35,
        )

        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_mur, 0.22))
        grad.setColorAt(1.0, _assombrir(self.couleur_mur, 0.06))

        painter.setPen(
            QPen(_assombrir(self.couleur_metal_fonce, 0.15), max(1.0, h * 0.035))
        )
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect, h * 0.08, h * 0.08)

        font = QFont(painter.font())
        font.setBold(True)
        font.setPointSizeF(max(7.0, h * 0.22))
        painter.setFont(font)

        painter.setPen(QColor("#394145"))
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            f"{i}/{n}",
        )

    # --------------------------------------------------------------------------
    # Panneau final
    # --------------------------------------------------------------------------

    def _dessiner_panneau_final(
        self,
        painter: QPainter,
        rect: QRectF,
        texte: str,
    ) -> None:
        """
        Grand panneau suspendu pour l'écran final.
        """

        h = rect.height()

        largeur = min(rect.width() * 0.50, h * 1.95)
        hauteur = h * 0.16

        rect_panneau = QRectF(
            rect.center().x() - largeur / 2,
            rect.top() + h * 0.10,
            largeur,
            hauteur,
        )

        # Suspensions
        y_accroche = rect.top() + h * 0.035
        decalage = largeur * 0.34

        pen_fil = QPen(self.couleur_metal_fonce)
        pen_fil.setWidthF(max(1.0, h * 0.0045))
        painter.setPen(pen_fil)

        for dx in (-decalage, decalage):
            x = rect.center().x() + dx
            painter.drawLine(
                QPointF(x, y_accroche),
                QPointF(x, rect_panneau.top()),
            )

        self._dessiner_ombre_rect(
            painter,
            rect_panneau,
            h * 0.018,
            h * 0.012,
            alpha=55,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.couleur_metal_fonce)
        painter.drawRoundedRect(rect_panneau, h * 0.018, h * 0.018)

        marge = h * 0.015
        rect_interieur = rect_panneau.adjusted(marge, marge, -marge, -marge)

        grad = QLinearGradient(rect_interieur.topLeft(), rect_interieur.bottomLeft())
        grad.setColorAt(0.0, QColor("#F3EBDD"))
        grad.setColorAt(1.0, QColor("#DDD0BA"))

        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect_interieur, h * 0.010, h * 0.010)

        font = QFont(painter.font())
        font.setBold(True)
        font.setPointSizeF(max(8.0, h * 0.043))
        painter.setFont(font)

        painter.setPen(QColor("#353B3E"))
        painter.drawText(
            rect_interieur.adjusted(h * 0.020, 0, -h * 0.020, 0),
            Qt.AlignmentFlag.AlignCenter,
            texte,
        )

    # --------------------------------------------------------------------------
    # Bloc de quai au premier plan
    # --------------------------------------------------------------------------

    def _dessiner_bloc_bas_avant(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """
        Dessine le quai au premier plan, devant le train.
        """

        h = rect.height()

        rect_bloc = QRectF(
            rect.left(),
            y_quai - h * 0.025,
            rect.width(),
            rect.bottom() - (y_quai - h * 0.025),
        )

        grad = QLinearGradient(rect_bloc.topLeft(), rect_bloc.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_quai, 0.04))
        grad.setColorAt(1.0, _assombrir(self.couleur_quai, 0.16))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(rect_bloc)

        rect_bord = QRectF(
            rect.left(),
            y_quai - h * 0.025,
            rect.width(),
            h * 0.025,
        )

        grad_bord = QLinearGradient(rect_bord.topLeft(), rect_bord.bottomLeft())
        grad_bord.setColorAt(0.0, _eclaircir(self.couleur_bord_quai, 0.10))
        grad_bord.setColorAt(1.0, _assombrir(self.couleur_bord_quai, 0.03))

        painter.setBrush(QBrush(grad_bord))
        painter.drawRect(rect_bord)

        # Ombre du train / scène vers le bas
        rect_ombre = QRectF(
            rect.left(),
            rect_bloc.top(),
            rect.width(),
            h * 0.09,
        )

        ombre = QLinearGradient(rect_ombre.topLeft(), rect_ombre.bottomLeft())
        ombre.setColorAt(0.0, QColor(0, 0, 0, 40))
        ombre.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(ombre))
        painter.drawRect(rect_ombre)

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
        """
        Dessine la gare derrière le train.
        """

        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        h = rect.height()
        y_quai = self._y_quai(rect, y_rail)

        # Fond général
        self._dessiner_fond_general(painter, rect, y_quai)

        # Quai intérieur
        self._dessiner_quai_interieur(painter, rect, y_quai)

        # Grande verrière
        self._dessiner_verriere(painter, rect, y_quai)

        # Lampes
        self._dessiner_lampes(painter, rect, y_quai)

        # Façade fermée
        self._dessiner_facade_terminus(painter, rect, y_quai)

        # Sortie
        self._dessiner_sortie(painter, rect, y_quai)

        # Banc
        rect_banc = self._rect_norm(
            rect,
            0.59,
            0.0,
            0.12,
            0.10,
        )
        rect_banc.moveTop(y_quai - h * 0.102)
        rect_banc.setHeight(h * 0.10)
        self._dessiner_banc(painter, rect_banc)

        # Panneau pays
        if nom_pays:
            rect_panneau = self._rect_norm(
                rect,
                0.33,
                0.0,
                0.22,
                0.12,
            )
            rect_panneau.moveTop(y_quai - h * 0.30)
            rect_panneau.setHeight(h * 0.12)

            self._dessiner_panneau_nom(
                painter,
                rect_panneau,
                nom_pays,
            )

            # Plaque progression
            if i is not None and n is not None:
                rect_plaque = self._rect_norm(
                    rect,
                    0.57,
                    0.0,
                    0.08,
                    0.10,
                )
                rect_plaque.moveTop(y_quai - h * 0.28)
                rect_plaque.setHeight(h * 0.10)

                self._dessiner_plaque_progression(
                    painter,
                    rect_plaque,
                    i,
                    n,
                )

        # Feu
        x_feu_prop = 0.84 if self.sens > 0 else 0.08
        rect_feu = QRectF(
            self._x(rect, x_feu_prop) - rect.width() * 0.02,
            y_quai - h * 0.30,
            rect.width() * 0.05,
            h * 0.28,
        )

        self._dessiner_feu(
            painter,
            rect_feu,
            etat=kwargs.get("etat_feu", self.etat_feu),
        )

        painter.restore()

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

        Paramètre facultatif :
            message_final : str | None
        """

        if rect.width() <= 0 or rect.height() <= 0 or y_rail is None:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        y_quai = self._y_quai(rect, y_rail)

        # Quai avant
        self._dessiner_bloc_bas_avant(
            painter,
            rect,
            y_quai,
        )

        # Panneau final éventuel
        message_final = kwargs.get("message_final")
        if message_final:
            self._dessiner_panneau_final(
                painter,
                rect,
                message_final,
            )

        painter.restore()
