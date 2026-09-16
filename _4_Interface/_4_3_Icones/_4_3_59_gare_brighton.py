################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.59 – Classe de création d'une gare balnéaire britannique                 #
################################################################################

from __future__ import annotations

import math
from datetime import datetime

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetricsF,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)

# 0 -- Utilitaires -------------------------------------------------------------


def _qcolor(couleur: QColor | str) -> QColor:
    return couleur if isinstance(couleur, QColor) else QColor(couleur)


def _avec_alpha(couleur: QColor | str, alpha: int) -> QColor:
    c = QColor(_qcolor(couleur))
    c.setAlpha(max(0, min(255, alpha)))
    return c


def _melanger(c1: QColor | str, c2: QColor | str, p: float) -> QColor:
    a = _qcolor(c1)
    b = _qcolor(c2)
    p = max(0.0, min(1.0, p))
    return QColor(
        round(a.red() * (1 - p) + b.red() * p),
        round(a.green() * (1 - p) + b.green() * p),
        round(a.blue() * (1 - p) + b.blue() * p),
        round(a.alpha() * (1 - p) + b.alpha() * p),
    )


def _eclaircir(couleur: QColor | str, p: float = 0.20) -> QColor:
    return _melanger(couleur, "#FFFFFF", p)


def _assombrir(couleur: QColor | str, p: float = 0.20) -> QColor:
    return _melanger(couleur, "#000000", p)


# 1 -- Signalétique ------------------------------------------------------------


class PanneauBritannique:
    """Panneau bleu marine typique d'une grande gare britannique."""

    def __init__(
        self,
        couleur_fond: QColor | str = "#17375E",
        couleur_texte: QColor | str = "#F7F3E8",
        couleur_bord: QColor | str = "#E8DCC4",
        couleur_support: QColor | str = "#304655",
    ):
        self.couleur_fond = _qcolor(couleur_fond)
        self.couleur_texte = _qcolor(couleur_texte)
        self.couleur_bord = _qcolor(couleur_bord)
        self.couleur_support = _qcolor(couleur_support)

    def _police(self, texte: str, largeur: float, taille_max: float) -> QFont:
        taille = max(7, int(taille_max))
        while taille >= 7:
            police = QFont("Segoe UI", taille)
            police.setBold(True)
            if QFontMetricsF(police).horizontalAdvance(texte) <= largeur:
                return police
            taille -= 1
        police = QFont("Segoe UI", 7)
        police.setBold(True)
        return police

    def peindre(self, painter: QPainter, rect: QRectF, nom: str) -> None:
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        rect_plaque = QRectF(rect.left(), rect.top(), rect.width(), h * 0.40)

        ombre = rect_plaque.translated(h * 0.018, h * 0.025)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha("#000000", 38))
        painter.drawRoundedRect(ombre, h * 0.035, h * 0.035)

        grad = QLinearGradient(rect_plaque.topLeft(), rect_plaque.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_fond, 0.06))
        grad.setColorAt(1.0, _assombrir(self.couleur_fond, 0.08))

        pen = QPen(self.couleur_bord)
        pen.setWidthF(max(1.0, h * 0.020))
        painter.setPen(pen)
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect_plaque, h * 0.035, h * 0.035)

        # Ligne crème décorative.
        painter.setPen(QPen(_avec_alpha(self.couleur_bord, 185), max(1.0, h * 0.008)))
        painter.drawLine(
            QPointF(
                rect_plaque.left() + rect_plaque.width() * 0.07,
                rect_plaque.top() + h * 0.085,
            ),
            QPointF(
                rect_plaque.right() - rect_plaque.width() * 0.07,
                rect_plaque.top() + h * 0.085,
            ),
        )

        police = self._police(
            nom.upper(), rect_plaque.width() * 0.82, rect_plaque.height() * 0.34
        )
        painter.setFont(police)
        painter.setPen(self.couleur_texte)
        painter.drawText(rect_plaque, Qt.AlignmentFlag.AlignCenter, nom.upper())

        # Deux supports fins parfaitement centrés.
        largeur_support = max(2.0, h * 0.035)
        for x in (
            rect_plaque.left() + rect_plaque.width() * 0.23,
            rect_plaque.right() - rect_plaque.width() * 0.23,
        ):
            rect_tige = QRectF(
                x - largeur_support / 2,
                rect_plaque.bottom(),
                largeur_support,
                rect.bottom() - rect_plaque.bottom(),
            )
            grad_tige = QLinearGradient(
                QPointF(rect_tige.left(), 0), QPointF(rect_tige.right(), 0)
            )
            grad_tige.setColorAt(0.0, _assombrir(self.couleur_support, 0.22))
            grad_tige.setColorAt(0.5, _eclaircir(self.couleur_support, 0.15))
            grad_tige.setColorAt(1.0, _assombrir(self.couleur_support, 0.20))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad_tige))
            painter.drawRoundedRect(
                rect_tige, largeur_support * 0.45, largeur_support * 0.45
            )

        painter.restore()


class PlaqueProgressionBritannique:
    """Petit cartouche de progression assorti au panneau principal."""

    def __init__(
        self,
        couleur_fond: QColor | str = "#17375E",
        couleur_texte: QColor | str = "#F7F3E8",
        couleur_bord: QColor | str = "#E8DCC4",
        couleur_support: QColor | str = "#304655",
    ):
        self.couleur_fond = _qcolor(couleur_fond)
        self.couleur_texte = _qcolor(couleur_texte)
        self.couleur_bord = _qcolor(couleur_bord)
        self.couleur_support = _qcolor(couleur_support)

    def peindre(self, painter: QPainter, rect: QRectF, i: int, n: int) -> None:
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        h = rect.height()

        rect_plaque = QRectF(rect.left(), rect.top(), rect.width(), h * 0.42)
        x_tige = rect.center().x()
        largeur_tige = max(2.0, h * 0.075)

        painter.setPen(Qt.PenStyle.NoPen)
        grad_tige = QLinearGradient(
            QPointF(x_tige - largeur_tige, 0), QPointF(x_tige + largeur_tige, 0)
        )
        grad_tige.setColorAt(0.0, _assombrir(self.couleur_support, 0.22))
        grad_tige.setColorAt(0.5, _eclaircir(self.couleur_support, 0.14))
        grad_tige.setColorAt(1.0, _assombrir(self.couleur_support, 0.20))
        painter.setBrush(QBrush(grad_tige))
        painter.drawRoundedRect(
            QRectF(
                x_tige - largeur_tige / 2,
                rect_plaque.bottom(),
                largeur_tige,
                rect.bottom() - rect_plaque.bottom(),
            ),
            largeur_tige * 0.45,
            largeur_tige * 0.45,
        )

        grad = QLinearGradient(rect_plaque.topLeft(), rect_plaque.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_fond, 0.05))
        grad.setColorAt(1.0, _assombrir(self.couleur_fond, 0.08))

        pen = QPen(self.couleur_bord)
        pen.setWidthF(max(1.0, h * 0.022))
        painter.setPen(pen)
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect_plaque, h * 0.035, h * 0.035)

        police = QFont("Segoe UI", max(7, int(rect_plaque.height() * 0.30)))
        police.setBold(True)
        painter.setFont(police)
        painter.setPen(self.couleur_texte)
        painter.drawText(rect_plaque, Qt.AlignmentFlag.AlignCenter, f"{i}/{n}")

        painter.restore()


class HorlogeSuspendueBritannique:
    """Horloge double face suspendue à la structure."""

    def __init__(
        self,
        couleur_cadre: QColor | str = "#22313B",
        couleur_fond: QColor | str = "#FAF7EF",
        couleur_trait: QColor | str = "#1D2327",
    ):
        self.couleur_cadre = _qcolor(couleur_cadre)
        self.couleur_fond = _qcolor(couleur_fond)
        self.couleur_trait = _qcolor(couleur_trait)

    def peindre(self, painter: QPainter, centre: QPointF, rayon: float) -> None:
        if rayon <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Tige de suspension.
        painter.setPen(QPen(self.couleur_cadre, max(1.0, rayon * 0.10)))
        painter.drawLine(
            QPointF(centre.x(), centre.y() - rayon * 2.4),
            QPointF(centre.x(), centre.y() - rayon),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha("#000000", 35))
        painter.drawEllipse(
            QPointF(centre.x() + rayon * 0.08, centre.y() + rayon * 0.10), rayon, rayon
        )

        grad = QRadialGradient(centre, rayon)
        grad.setColorAt(0.0, _eclaircir(self.couleur_fond, 0.05))
        grad.setColorAt(1.0, self.couleur_fond)

        pen = QPen(self.couleur_cadre)
        pen.setWidthF(max(1.0, rayon * 0.11))
        painter.setPen(pen)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(centre, rayon, rayon)

        painter.translate(centre)
        painter.setPen(QPen(self.couleur_trait, max(1.0, rayon * 0.055)))
        for k in range(12):
            painter.save()
            painter.rotate(k * 30)
            longueur = 0.16 if k % 3 == 0 else 0.10
            painter.drawLine(
                QPointF(0, -rayon * (0.88 - longueur)), QPointF(0, -rayon * 0.88)
            )
            painter.restore()

        maintenant = datetime.now()
        minute = maintenant.minute
        heure = maintenant.hour % 12 + minute / 60

        painter.setPen(
            QPen(
                self.couleur_trait, max(1.0, rayon * 0.075), cap=Qt.PenCapStyle.RoundCap
            )
        )
        painter.save()
        painter.rotate(heure * 30)
        painter.drawLine(QPointF(0, 0), QPointF(0, -rayon * 0.46))
        painter.restore()

        painter.setPen(
            QPen(
                self.couleur_trait, max(1.0, rayon * 0.045), cap=Qt.PenCapStyle.RoundCap
            )
        )
        painter.save()
        painter.rotate(minute * 6)
        painter.drawLine(QPointF(0, 0), QPointF(0, -rayon * 0.66))
        painter.restore()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.couleur_trait)
        painter.drawEllipse(QPointF(0, 0), rayon * 0.09, rayon * 0.09)
        painter.restore()


# 2 -- Feu ferroviaire ---------------------------------------------------------


class FeuBritannique:
    """Signal fin de quai, adapté à la silhouette très verticale de la gare."""

    def __init__(
        self,
        couleur_metal: QColor | str = "#2F3B43",
        couleur_support: QColor | str = "#4B5B65",
    ):
        self.couleur_metal = _qcolor(couleur_metal)
        self.couleur_support = _qcolor(couleur_support)

    def _optique(
        self,
        painter: QPainter,
        centre: QPointF,
        rayon: float,
        couleur: QColor,
        allume: bool,
    ) -> None:
        if allume:
            halo = QRadialGradient(centre, rayon * 3.0)
            halo.setColorAt(0.0, _avec_alpha(couleur, 120))
            halo.setColorAt(0.40, _avec_alpha(couleur, 42))
            halo.setColorAt(1.0, _avec_alpha(couleur, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(centre, rayon * 3.0, rayon * 3.0)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_assombrir(self.couleur_metal, 0.36))
        painter.drawEllipse(centre, rayon * 1.25, rayon * 1.25)

        grad = QRadialGradient(
            QPointF(centre.x() - rayon * 0.18, centre.y() - rayon * 0.20), rayon
        )
        grad.setColorAt(0.0, _eclaircir(couleur, 0.42 if allume else 0.10))
        grad.setColorAt(0.65, couleur if allume else _assombrir(couleur, 0.45))
        grad.setColorAt(1.0, _assombrir(couleur, 0.58))
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(centre, rayon, rayon)

    def peindre(self, painter: QPainter, rect: QRectF, etat: str = "rouge") -> None:
        if rect.width() <= 0 or rect.height() <= 0:
            return

        etat = etat.lower().strip()
        if etat not in {"rouge", "orange", "vert"}:
            etat = "rouge"

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        cx = rect.center().x()
        largeur_boite = min(rect.width() * 0.80, h * 0.28)
        hauteur_boite = h * 0.45
        rect_boite = QRectF(
            cx - largeur_boite / 2, rect.top() + h * 0.02, largeur_boite, hauteur_boite
        )

        largeur_mat = max(2.0, h * 0.048)
        rect_mat = QRectF(
            cx - largeur_mat / 2,
            rect_boite.bottom(),
            largeur_mat,
            rect.bottom() - rect_boite.bottom() - h * 0.055,
        )

        grad_mat = QLinearGradient(
            QPointF(rect_mat.left(), 0), QPointF(rect_mat.right(), 0)
        )
        grad_mat.setColorAt(0.0, _assombrir(self.couleur_support, 0.25))
        grad_mat.setColorAt(0.5, _eclaircir(self.couleur_support, 0.15))
        grad_mat.setColorAt(1.0, _assombrir(self.couleur_support, 0.20))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_mat))
        painter.drawRoundedRect(rect_mat, largeur_mat * 0.42, largeur_mat * 0.42)

        grad_boite = QLinearGradient(rect_boite.topLeft(), rect_boite.bottomRight())
        grad_boite.setColorAt(0.0, _eclaircir(self.couleur_metal, 0.12))
        grad_boite.setColorAt(1.0, _assombrir(self.couleur_metal, 0.18))
        pen = QPen(_assombrir(self.couleur_metal, 0.42))
        pen.setWidthF(max(1.0, h * 0.014))
        painter.setPen(pen)
        painter.setBrush(QBrush(grad_boite))
        painter.drawRoundedRect(rect_boite, largeur_boite * 0.11, largeur_boite * 0.11)

        rayon = min(largeur_boite * 0.18, hauteur_boite * 0.095)
        centres = [
            QPointF(cx, rect_boite.top() + hauteur_boite * 0.20),
            QPointF(cx, rect_boite.top() + hauteur_boite * 0.50),
            QPointF(cx, rect_boite.top() + hauteur_boite * 0.80),
        ]
        couleurs = (QColor("#D74F4F"), QColor("#D6A245"), QColor("#4FB868"))
        noms = ("rouge", "orange", "vert")
        for centre, couleur, nom in zip(centres, couleurs, noms):
            self._optique(painter, centre, rayon, couleur, etat == nom)

        # Socle.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_assombrir(self.couleur_support, 0.22))
        painter.drawRoundedRect(
            QRectF(cx - h * 0.068, rect.bottom() - h * 0.055, h * 0.136, h * 0.040),
            h * 0.010,
            h * 0.010,
        )

        painter.restore()


# 3 -- Gare balnéaire britannique ---------------------------------------------


class GareBalneaireBritannique:
    """
    Grande gare de terminus britannique inspirée de l'imaginaire de Brighton.

    Cette gare est volontairement très différente des gares ancienne et moderne :
        - immense nef ferroviaire plutôt qu'un simple mur de fond ;
        - répétition de piliers fins en fonte ;
        - toiture cintrée très présente ;
        - signalétique de quais britannique ;
        - passerelle / portique transversal ;
        - briques rouges et pierre crème ;
        - grande luminosité venant de la verrière et du fond.

    L'API reste identique aux autres gares du projet.
    """

    masque_paysage = True
    masque_rails = True

    def __init__(
        self,
        couleur_brique: QColor | str = "#A8654D",
        couleur_brique_foncee: QColor | str = "#7F4C3B",
        couleur_pierre: QColor | str = "#E9DFC8",
        couleur_metal: QColor | str = "#405967",
        couleur_metal_fonce: QColor | str = "#283D48",
        couleur_verre: QColor | str = "#DCEEF3",
        couleur_quai: QColor | str = "#9B9690",
        couleur_bord_quai: QColor | str = "#EFE6CE",
        couleur_plancher: QColor | str = "#746B64",
        lampes_allumees: bool = True,
        etat_feu: str = "rouge",
    ):
        self.couleur_brique = _qcolor(couleur_brique)
        self.couleur_brique_foncee = _qcolor(couleur_brique_foncee)
        self.couleur_pierre = _qcolor(couleur_pierre)
        self.couleur_metal = _qcolor(couleur_metal)
        self.couleur_metal_fonce = _qcolor(couleur_metal_fonce)
        self.couleur_verre = _qcolor(couleur_verre)
        self.couleur_quai = _qcolor(couleur_quai)
        self.couleur_bord_quai = _qcolor(couleur_bord_quai)
        self.couleur_plancher = _qcolor(couleur_plancher)

        self.lampes_allumees = lampes_allumees
        self.etat_feu = etat_feu

        self.panneau = PanneauBritannique(couleur_support=self.couleur_metal)
        self.plaque = PlaqueProgressionBritannique(couleur_support=self.couleur_metal)
        self.horloge = HorlogeSuspendueBritannique()
        self.feu = FeuBritannique(
            couleur_metal=self.couleur_metal_fonce, couleur_support=self.couleur_metal
        )

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    def largeur_recommandee(self, hauteur_scene: float) -> float:
        return hauteur_scene * 3.35

    def _y_quai(self, rect: QRectF, y_rail: float | None) -> float:
        if y_rail is not None:
            return y_rail - rect.height() * 0.055
        return rect.top() + rect.height() * 0.70

    def _axes_piliers(self, rect: QRectF) -> list[float]:
        """Axes fixes des piliers fins de la grande nef."""
        n = 11
        gauche = rect.left() + rect.width() * 0.10
        droite = rect.right() - rect.width() * 0.10
        return [gauche + (droite - gauche) * i / (n - 1) for i in range(n)]

    # --------------------------------------------------------------------------
    # Architecture générale
    # --------------------------------------------------------------------------

    def _dessiner_fond_lumineux(
        self, painter: QPainter, rect: QRectF, y_quai: float
    ) -> None:
        """Fond clair de terminus, avec façade en briques et ouverture lumineuse."""
        h = rect.height()
        w = rect.width()

        rect_fond = QRectF(rect.left(), rect.top(), w, y_quai - rect.top())
        grad = QLinearGradient(rect_fond.topLeft(), rect_fond.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_pierre, 0.14))
        grad.setColorAt(0.58, self.couleur_pierre)
        grad.setColorAt(1.0, _assombrir(self.couleur_pierre, 0.06))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(rect_fond)

        # Grandes masses latérales en briques, centre plus lumineux.
        largeur_aile = w * 0.20
        for x0 in (rect.left(), rect.right() - largeur_aile):
            rect_aile = QRectF(
                x0, rect.top() + h * 0.15, largeur_aile, y_quai - rect.top() - h * 0.15
            )
            grad_brique = QLinearGradient(rect_aile.topLeft(), rect_aile.bottomLeft())
            grad_brique.setColorAt(0.0, _eclaircir(self.couleur_brique, 0.06))
            grad_brique.setColorAt(1.0, _assombrir(self.couleur_brique, 0.09))
            painter.setBrush(QBrush(grad_brique))
            painter.drawRect(rect_aile)

            # Lignes de briques simples mais nombreuses.
            pen_joint = QPen(
                _avec_alpha(_assombrir(self.couleur_brique_foncee, 0.05), 85)
            )
            pen_joint.setWidthF(max(1.0, h * 0.0025))
            painter.setPen(pen_joint)
            pas_y = h * 0.032
            y = rect_aile.top() + pas_y
            rang = 0
            while y < rect_aile.bottom():
                painter.drawLine(
                    QPointF(rect_aile.left(), y), QPointF(rect_aile.right(), y)
                )
                decal = 0 if rang % 2 == 0 else w * 0.012
                x = rect_aile.left() + decal
                while x < rect_aile.right():
                    painter.drawLine(QPointF(x, y - pas_y), QPointF(x, y))
                    x += w * 0.024
                y += pas_y
                rang += 1

        # Grande baie terminale au centre.
        rect_baie = QRectF(
            rect.left() + w * 0.31,
            rect.top() + h * 0.18,
            w * 0.38,
            h * 0.34,
        )
        grad_baie = QLinearGradient(rect_baie.topLeft(), rect_baie.bottomLeft())
        grad_baie.setColorAt(0.0, _eclaircir(self.couleur_verre, 0.25))
        grad_baie.setColorAt(1.0, _assombrir(self.couleur_verre, 0.03))
        painter.setBrush(QBrush(grad_baie))
        painter.setPen(QPen(self.couleur_metal_fonce, max(1.0, h * 0.005)))
        painter.drawRoundedRect(rect_baie, h * 0.014, h * 0.014)

        # Trame de la grande baie.
        painter.setPen(
            QPen(_avec_alpha(self.couleur_metal_fonce, 150), max(1.0, h * 0.0035))
        )
        for i in range(1, 6):
            x = rect_baie.left() + rect_baie.width() * i / 6
            painter.drawLine(
                QPointF(x, rect_baie.top()), QPointF(x, rect_baie.bottom())
            )
        for p in (0.30, 0.60):
            y = rect_baie.top() + rect_baie.height() * p
            painter.drawLine(
                QPointF(rect_baie.left(), y), QPointF(rect_baie.right(), y)
            )

        # Reflets.
        painter.setPen(QPen(_avec_alpha("#FFFFFF", 70), max(1.0, h * 0.003)))
        for p in (0.25, 0.48, 0.72):
            x = rect_baie.left() + rect_baie.width() * p
            painter.drawLine(
                QPointF(x, rect_baie.top()),
                QPointF(x - rect_baie.width() * 0.10, rect_baie.bottom()),
            )

    def _dessiner_grande_nef(
        self, painter: QPainter, rect: QRectF, y_quai: float
    ) -> None:
        """Dessine la toiture cintrée principale, élément signature de la gare."""
        h = rect.height()
        w = rect.width()

        gauche = rect.left() + w * 0.07
        droite = rect.right() - w * 0.07
        y_base = y_quai - h * 0.03
        y_sommet = rect.top() + h * 0.025
        demi_largeur = (droite - gauche) / 2
        cx = rect.center().x()

        # Fond vitré de la nef : grande forme cintrée unique.
        path = QPainterPath()
        path.moveTo(gauche, y_base)
        path.cubicTo(
            QPointF(gauche + demi_largeur * 0.15, y_sommet + h * 0.04),
            QPointF(cx - demi_largeur * 0.22, y_sommet),
            QPointF(cx, y_sommet),
        )
        path.cubicTo(
            QPointF(cx + demi_largeur * 0.22, y_sommet),
            QPointF(droite - demi_largeur * 0.15, y_sommet + h * 0.04),
            QPointF(droite, y_base),
        )
        path.lineTo(gauche, y_base)
        path.closeSubpath()

        grad_verre = QLinearGradient(QPointF(cx, y_sommet), QPointF(cx, y_base))
        grad_verre.setColorAt(0.0, _eclaircir(self.couleur_verre, 0.22))
        grad_verre.setColorAt(0.55, self.couleur_verre)
        grad_verre.setColorAt(1.0, _assombrir(self.couleur_verre, 0.10))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_verre))
        painter.drawPath(path)

        # Arc périphérique lourd.
        pen_arc = QPen(self.couleur_metal_fonce)
        pen_arc.setWidthF(max(1.5, h * 0.010))
        painter.setPen(pen_arc)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Arceaux verticaux : nombreux et fins.
        axes = self._axes_piliers(rect)
        pen_structure = QPen(_avec_alpha(self.couleur_metal_fonce, 190))
        pen_structure.setWidthF(max(1.0, h * 0.005))
        painter.setPen(pen_structure)

        for x in axes:
            # hauteur de l'arc suivant une ellipse simplifiée.
            t = (x - cx) / (demi_largeur if demi_largeur else 1)
            t = max(-1.0, min(1.0, t))
            y_toit = y_sommet + (y_base - y_sommet) * (
                1 - math.sqrt(max(0.0, 1 - t * t))
            )
            painter.drawLine(QPointF(x, y_toit), QPointF(x, y_base))

        # Traverses suivant des bandes horizontales.
        for p in (0.28, 0.50, 0.70, 0.86):
            y = y_sommet + (y_base - y_sommet) * p
            span = demi_largeur * math.sqrt(
                max(0.0, 1 - ((y - y_sommet) / max(1.0, y_base - y_sommet) - 1) ** 2)
            )
            span = max(demi_largeur * 0.35, min(demi_largeur, span))
            painter.drawLine(QPointF(cx - span, y), QPointF(cx + span, y))

        # Contreventements croisés sur quelques travées.
        pen_x = QPen(_avec_alpha(self.couleur_metal_fonce, 105))
        pen_x.setWidthF(max(1.0, h * 0.003))
        painter.setPen(pen_x)
        for a, b in zip(axes[:-1], axes[1:]):
            if int((a - axes[0]) / max(1.0, axes[1] - axes[0])) % 2 == 0:
                y_haut = rect.top() + h * 0.16
                y_bas = y_base - h * 0.02
                painter.drawLine(QPointF(a, y_bas), QPointF(b, y_haut))
                painter.drawLine(QPointF(b, y_bas), QPointF(a, y_haut))

        # Reflets lumineux longs.
        painter.setPen(QPen(_avec_alpha("#FFFFFF", 55), max(1.0, h * 0.0035)))
        for p in (0.24, 0.50, 0.76):
            x = gauche + (droite - gauche) * p
            painter.drawLine(
                QPointF(x, y_sommet + h * 0.025),
                QPointF(x - w * 0.05, y_base - h * 0.02),
            )

    def _dessiner_piliers_fonte(
        self, painter: QPainter, rect: QRectF, y_quai: float
    ) -> None:
        """Dessine une répétition de piliers fins en fonte."""
        h = rect.height()
        largeur = h * 0.026

        for x in self._axes_piliers(rect):
            y_top = rect.top() + h * 0.15
            rect_pilier = QRectF(x - largeur / 2, y_top, largeur, y_quai - y_top)

            grad = QLinearGradient(
                QPointF(rect_pilier.left(), 0), QPointF(rect_pilier.right(), 0)
            )
            grad.setColorAt(0.0, _assombrir(self.couleur_metal, 0.24))
            grad.setColorAt(0.48, _eclaircir(self.couleur_metal, 0.12))
            grad.setColorAt(1.0, _assombrir(self.couleur_metal, 0.18))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(rect_pilier, largeur * 0.32, largeur * 0.32)

            # Chapiteau et socle.
            for y0, hh, facteur in (
                (rect_pilier.top(), h * 0.025, 1.8),
                (rect_pilier.bottom() - h * 0.035, h * 0.035, 1.9),
            ):
                painter.setBrush(_assombrir(self.couleur_metal, 0.06))
                painter.drawRoundedRect(
                    QRectF(x - largeur * facteur / 2, y0, largeur * facteur, hh),
                    hh * 0.18,
                    hh * 0.18,
                )

            # Petite console décorative en Y.
            painter.setPen(
                QPen(_avec_alpha(self.couleur_metal_fonce, 180), max(1.0, h * 0.0035))
            )
            y_console = rect_pilier.top() + h * 0.055
            painter.drawLine(
                QPointF(x, y_console), QPointF(x - h * 0.030, y_console - h * 0.035)
            )
            painter.drawLine(
                QPointF(x, y_console), QPointF(x + h * 0.030, y_console - h * 0.035)
            )

    def _dessiner_portique_transversal(
        self, painter: QPainter, rect: QRectF, y_quai: float
    ) -> None:
        """Grand portique/passerelle transversal, très différent des autres gares."""
        h = rect.height()
        w = rect.width()
        y = rect.top() + h * 0.34
        gauche = rect.left() + w * 0.13
        droite = rect.right() - w * 0.13
        hauteur = h * 0.075

        # Passerelle.
        rect_pass = QRectF(gauche, y, droite - gauche, hauteur)
        grad = QLinearGradient(rect_pass.topLeft(), rect_pass.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_metal, 0.08))
        grad.setColorAt(1.0, _assombrir(self.couleur_metal, 0.12))
        painter.setPen(QPen(self.couleur_metal_fonce, max(1.0, h * 0.004)))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect_pass, h * 0.010, h * 0.010)

        # Treillis triangulé.
        painter.setPen(
            QPen(_avec_alpha(self.couleur_metal_fonce, 170), max(1.0, h * 0.003))
        )
        n = 14
        pas = rect_pass.width() / n
        for i in range(n):
            x1 = rect_pass.left() + pas * i
            x2 = x1 + pas
            if i % 2 == 0:
                painter.drawLine(
                    QPointF(x1, rect_pass.bottom()), QPointF(x2, rect_pass.top())
                )
            else:
                painter.drawLine(
                    QPointF(x1, rect_pass.top()), QPointF(x2, rect_pass.bottom())
                )

        # Garde-corps.
        y_garde = rect_pass.top() - h * 0.026
        painter.setPen(QPen(self.couleur_metal_fonce, max(1.0, h * 0.003)))
        painter.drawLine(
            QPointF(rect_pass.left(), y_garde), QPointF(rect_pass.right(), y_garde)
        )
        for i in range(15):
            x = rect_pass.left() + rect_pass.width() * i / 14
            painter.drawLine(QPointF(x, y_garde), QPointF(x, rect_pass.top()))

        # Escaliers stylisés aux deux extrémités.
        for sens, x0 in ((1, rect_pass.left()), (-1, rect_pass.right())):
            painter.setPen(
                QPen(_avec_alpha(self.couleur_metal_fonce, 165), max(1.0, h * 0.004))
            )
            x1 = x0 + sens * w * 0.055
            painter.drawLine(QPointF(x0, rect_pass.bottom()), QPointF(x1, y_quai))
            nb = 6
            for k in range(1, nb):
                t = k / nb
                x = x0 + sens * w * 0.055 * t
                yy = rect_pass.bottom() + (y_quai - rect_pass.bottom()) * t
                painter.drawLine(
                    QPointF(x - sens * h * 0.010, yy), QPointF(x + sens * h * 0.010, yy)
                )

    def _dessiner_signalisation_quais(
        self, painter: QPainter, rect: QRectF, y_quai: float
    ) -> None:
        """Panneaux PLATFORM 1 / PLATFORM 2 suspendus au portique."""
        h = rect.height()
        w = rect.width()
        y = rect.top() + h * 0.43

        for texte, x_centre in (
            ("PLATFORM 1", rect.left() + w * 0.34),
            ("PLATFORM 2", rect.left() + w * 0.66),
        ):
            rect_p = QRectF(x_centre - w * 0.075, y, w * 0.15, h * 0.052)

            # Suspensions.
            painter.setPen(QPen(self.couleur_metal_fonce, max(1.0, h * 0.003)))
            for x in (
                rect_p.left() + rect_p.width() * 0.25,
                rect_p.right() - rect_p.width() * 0.25,
            ):
                painter.drawLine(QPointF(x, y - h * 0.040), QPointF(x, y))

            painter.setPen(QPen(QColor("#E8DCC4"), max(1.0, h * 0.003)))
            painter.setBrush(QColor("#17375E"))
            painter.drawRoundedRect(rect_p, h * 0.006, h * 0.006)

            police = QFont("Segoe UI", max(7, int(h * 0.026)))
            police.setBold(True)
            painter.setFont(police)
            painter.setPen(QColor("#F7F3E8"))
            painter.drawText(rect_p, Qt.AlignmentFlag.AlignCenter, texte)

    def _dessiner_lampes(self, painter: QPainter, rect: QRectF) -> None:
        """Lampes globe répétées entre les travées."""
        h = rect.height()
        axes = self._axes_piliers(rect)
        y_support = rect.top() + h * 0.23
        y_lampe = rect.top() + h * 0.31

        for x in axes[1:-1:2]:
            painter.setPen(QPen(self.couleur_metal_fonce, max(1.0, h * 0.003)))
            painter.drawLine(QPointF(x, y_support), QPointF(x, y_lampe - h * 0.018))

            if self.lampes_allumees:
                halo = QRadialGradient(QPointF(x, y_lampe), h * 0.070)
                halo.setColorAt(0.0, QColor(255, 235, 176, 70))
                halo.setColorAt(0.55, QColor(255, 230, 165, 18))
                halo.setColorAt(1.0, QColor(255, 230, 165, 0))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(halo))
                painter.drawEllipse(QPointF(x, y_lampe), h * 0.070, h * 0.070)

            painter.setPen(QPen(self.couleur_metal_fonce, max(1.0, h * 0.0025)))
            painter.setBrush(
                QColor("#F6E7B2") if self.lampes_allumees else QColor("#C8C0AF")
            )
            painter.drawEllipse(QPointF(x, y_lampe), h * 0.018, h * 0.018)

    def _dessiner_publicite_retro(
        self, painter: QPainter, rect: QRectF, texte: str
    ) -> None:
        """Petite affiche touristique rétro, discrète mais caractéristique."""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0.0, QColor("#F5E8C9"))
        grad.setColorAt(1.0, QColor("#D8C58E"))
        painter.setPen(QPen(QColor("#6D5648"), max(1.0, rect.height() * 0.025)))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect, rect.height() * 0.04, rect.height() * 0.04)

        # Soleil stylisé.
        centre = QPointF(
            rect.left() + rect.width() * 0.22, rect.top() + rect.height() * 0.28
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#D89A46"))
        painter.drawEllipse(centre, rect.height() * 0.10, rect.height() * 0.10)

        # Mer en bandes.
        for k, c in enumerate(
            (QColor("#5E91A7"), QColor("#7BA9B9"), QColor("#95BEC8"))
        ):
            painter.setBrush(c)
            painter.drawRect(
                QRectF(
                    rect.left(),
                    rect.top() + rect.height() * (0.58 + 0.09 * k),
                    rect.width(),
                    rect.height() * 0.09,
                )
            )

        police = QFont("Georgia", max(6, int(rect.height() * 0.12)))
        police.setBold(True)
        painter.setFont(police)
        painter.setPen(QColor("#4E3C34"))
        painter.drawText(
            QRectF(
                rect.left() + rect.width() * 0.38,
                rect.top() + rect.height() * 0.08,
                rect.width() * 0.56,
                rect.height() * 0.44,
            ),
            Qt.AlignmentFlag.AlignCenter,
            texte,
        )
        painter.restore()

    def _dessiner_bancs(self, painter: QPainter, rect: QRectF, y_quai: float) -> None:
        """Deux bancs bois/fonte répartis symétriquement."""
        h = rect.height()
        w = rect.width()

        for x0 in (rect.left() + w * 0.22, rect.left() + w * 0.69):
            rect_banc = QRectF(x0, y_quai - h * 0.095, w * 0.09, h * 0.085)
            rect_assise = QRectF(
                rect_banc.left(),
                rect_banc.top() + rect_banc.height() * 0.48,
                rect_banc.width(),
                rect_banc.height() * 0.16,
            )
            rect_dossier = QRectF(
                rect_banc.left() + rect_banc.width() * 0.05,
                rect_banc.top() + rect_banc.height() * 0.15,
                rect_banc.width() * 0.90,
                rect_banc.height() * 0.15,
            )

            grad_bois = QLinearGradient(rect_assise.topLeft(), rect_assise.bottomLeft())
            grad_bois.setColorAt(0.0, QColor("#9A704C"))
            grad_bois.setColorAt(1.0, QColor("#6B4C36"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad_bois))
            painter.drawRoundedRect(
                rect_assise, rect_assise.height() * 0.2, rect_assise.height() * 0.2
            )
            painter.drawRoundedRect(
                rect_dossier, rect_dossier.height() * 0.2, rect_dossier.height() * 0.2
            )

            pen = QPen(self.couleur_metal_fonce)
            pen.setWidthF(max(1.0, rect_banc.width() * 0.04))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            for x in (
                rect_banc.left() + rect_banc.width() * 0.20,
                rect_banc.right() - rect_banc.width() * 0.20,
            ):
                painter.drawLine(
                    QPointF(x, rect_assise.bottom()), QPointF(x, rect_banc.bottom())
                )

    def _dessiner_quai_arriere(
        self, painter: QPainter, rect: QRectF, y_quai: float
    ) -> None:
        h = rect.height()
        rect_quai = QRectF(rect.left(), y_quai, rect.width(), h * 0.14)
        grad = QLinearGradient(rect_quai.topLeft(), rect_quai.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_quai, 0.06))
        grad.setColorAt(1.0, _assombrir(self.couleur_quai, 0.12))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(rect_quai)

        painter.setBrush(self.couleur_bord_quai)
        painter.drawRect(QRectF(rect.left(), y_quai, rect.width(), max(4.0, h * 0.017)))

        pen = QPen(_avec_alpha(_assombrir(self.couleur_quai, 0.28), 75))
        pen.setWidthF(max(1.0, h * 0.003))
        painter.setPen(pen)
        pas = rect.width() * 0.075
        x = rect.left()
        while x < rect.right():
            painter.drawLine(QPointF(x, y_quai), QPointF(x, rect_quai.bottom()))
            x += pas

    # --------------------------------------------------------------------------
    # Dessin arrière
    # --------------------------------------------------------------------------

    def peindre_arriere(
        self,
        painter: QPainter,
        rect: QRectF,
        nom_pays: str,
        i: int | None = None,
        n: int | None = None,
        y_rail: float | None = None,
        **kwargs,
    ) -> None:
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        w = rect.width()
        y_quai = self._y_quai(rect, y_rail)

        # 1. Architecture de fond.
        self._dessiner_fond_lumineux(painter, rect, y_quai)
        self._dessiner_grande_nef(painter, rect, y_quai)

        # 2. Rythme vertical et transversal.
        self._dessiner_piliers_fonte(painter, rect, y_quai)
        self._dessiner_portique_transversal(painter, rect, y_quai)
        self._dessiner_signalisation_quais(painter, rect, y_quai)
        self._dessiner_lampes(painter, rect)

        # 3. Horloge suspendue au centre de la nef.
        self.horloge.peindre(
            painter,
            QPointF(rect.center().x(), rect.top() + h * 0.23),
            h * 0.046,
        )

        # 4. Signalétique principale.
        rect_panneau = QRectF(
            rect.left() + w * 0.38,
            y_quai - h * 0.24,
            w * 0.24,
            h * 0.19,
        )
        self.panneau.peindre(painter, rect_panneau, nom_pays)

        if i is not None and n is not None:
            self.plaque.peindre(
                painter,
                QRectF(
                    rect_panneau.right() + h * 0.018,
                    y_quai - h * 0.225,
                    h * 0.11,
                    h * 0.19,
                ),
                i,
                n,
            )

        # 5. Affiches rétro et bancs.
        self._dessiner_publicite_retro(
            painter,
            QRectF(rect.left() + w * 0.145, y_quai - h * 0.22, w * 0.095, h * 0.14),
            "SEA\nAIR",
        )
        self._dessiner_publicite_retro(
            painter,
            QRectF(rect.left() + w * 0.76, y_quai - h * 0.22, w * 0.095, h * 0.14),
            "COAST\nLINE",
        )
        self._dessiner_bancs(painter, rect, y_quai)

        # 6. Quai arrière et signal.
        self._dessiner_quai_arriere(painter, rect, y_quai)
        self.feu.peindre(
            painter,
            QRectF(
                rect.left() + w * 0.825,
                y_quai - h * 0.29,
                w * 0.050,
                h * 0.27,
            ),
            self.etat_feu,
        )

        painter.restore()

    # --------------------------------------------------------------------------
    # Dessin avant
    # --------------------------------------------------------------------------

    def _dessiner_bloc_bas_avant(
        self, painter: QPainter, rect: QRectF, y_quai: float
    ) -> None:
        h = rect.height()
        rect_bas = QRectF(rect.left(), y_quai, rect.width(), rect.bottom() - y_quai)

        grad = QLinearGradient(rect_bas.topLeft(), rect_bas.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_quai, 0.06))
        grad.setColorAt(0.18, self.couleur_quai)
        grad.setColorAt(1.0, _assombrir(self.couleur_plancher, 0.15))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(rect_bas)

        hauteur_bord = max(4.0, h * 0.019)
        painter.setBrush(self.couleur_bord_quai)
        painter.drawRect(QRectF(rect.left(), y_quai, rect.width(), hauteur_bord))

        # Ombre sous la rive.
        ombre = QLinearGradient(
            QPointF(0, y_quai + hauteur_bord),
            QPointF(0, y_quai + hauteur_bord + h * 0.030),
        )
        ombre.setColorAt(0.0, QColor(0, 0, 0, 60))
        ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(ombre))
        painter.drawRect(
            QRectF(rect.left(), y_quai + hauteur_bord, rect.width(), h * 0.030)
        )

        # Dalles plus étroites et nombreuses qu'ailleurs.
        pen = QPen(_avec_alpha(_assombrir(self.couleur_quai, 0.30), 80))
        pen.setWidthF(max(1.0, h * 0.003))
        painter.setPen(pen)
        pas = rect.width() * 0.070
        x = rect.left()
        while x <= rect.right():
            painter.drawLine(QPointF(x, y_quai), QPointF(x, rect.bottom()))
            x += pas
        for p in (0.34, 0.68):
            y = y_quai + rect_bas.height() * p
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))

    def peindre_avant(
        self,
        painter: QPainter,
        rect: QRectF,
        y_rail: float | None = None,
        **kwargs,
    ) -> None:
        if rect.width() <= 0 or rect.height() <= 0 or y_rail is None:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        h = rect.height()
        y_quai = self._y_quai(rect, y_rail)

        self._dessiner_bloc_bas_avant(painter, rect, y_quai)

        # Deux poteaux très proches en premier plan, très fins pour ne pas écraser la scène.
        largeur = h * 0.030
        for x in (rect.left() + h * 0.030, rect.right() - h * 0.030 - largeur):
            rect_pilier = QRectF(x, rect.top(), largeur, y_quai - rect.top())
            grad = QLinearGradient(
                QPointF(rect_pilier.left(), 0), QPointF(rect_pilier.right(), 0)
            )
            grad.setColorAt(0.0, _assombrir(self.couleur_metal_fonce, 0.26))
            grad.setColorAt(0.50, _eclaircir(self.couleur_metal_fonce, 0.06))
            grad.setColorAt(1.0, _assombrir(self.couleur_metal_fonce, 0.20))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(rect_pilier, largeur * 0.28, largeur * 0.28)

        painter.restore()

    # --------------------------------------------------------------------------
    # Dessin complet
    # --------------------------------------------------------------------------

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        nom_pays: str,
        i: int,
        n: int,
        y_rail: float | None = None,
        **kwargs,
    ) -> None:
        self.peindre_arriere(
            painter=painter,
            rect=rect,
            nom_pays=nom_pays,
            i=i,
            n=n,
            y_rail=y_rail,
            **kwargs,
        )
        self.peindre_avant(
            painter=painter,
            rect=rect,
            y_rail=y_rail,
            **kwargs,
        )
