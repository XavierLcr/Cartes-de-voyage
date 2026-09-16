################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.60 – Classe de création d'une petite gare de montagne                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations

import math

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

# 1 -- Fonctions utilitaires ---------------------------------------------------


def _qcolor(couleur: QColor | str) -> QColor:
    """Retourne un QColor."""
    return couleur if isinstance(couleur, QColor) else QColor(couleur)


def _avec_alpha(
    couleur: QColor | str,
    alpha: int,
) -> QColor:
    """Retourne une copie de la couleur avec l'alpha demandé."""
    c = QColor(_qcolor(couleur))
    c.setAlpha(max(0, min(255, alpha)))
    return c


def _melanger(
    couleur_1: QColor | str,
    couleur_2: QColor | str,
    proportion: float,
) -> QColor:
    """Interpole deux couleurs en RGB."""
    c1 = _qcolor(couleur_1)
    c2 = _qcolor(couleur_2)
    p = max(0.0, min(1.0, proportion))

    return QColor(
        round(c1.red() * (1 - p) + c2.red() * p),
        round(c1.green() * (1 - p) + c2.green() * p),
        round(c1.blue() * (1 - p) + c2.blue() * p),
        round(c1.alpha() * (1 - p) + c2.alpha() * p),
    )


def _eclaircir(
    couleur: QColor | str,
    proportion: float = 0.20,
) -> QColor:
    """Éclaircit une couleur."""
    return _melanger(couleur, "#FFFFFF", proportion)


def _assombrir(
    couleur: QColor | str,
    proportion: float = 0.20,
) -> QColor:
    """Assombrit une couleur."""
    return _melanger(couleur, "#000000", proportion)


# 2 -- Panneau montagne --------------------------------------------------------


class PanneauGareMontagne:
    """Petit panneau de gare en bois suspendu sur potence."""

    def __init__(
        self,
        couleur_bois: QColor | str = "#8B6444",
        couleur_bord: QColor | str = "#5A3F2A",
        couleur_texte: QColor | str = "#FFF8EE",
        couleur_potence: QColor | str = "#6A4B34",
    ):
        self.couleur_bois = _qcolor(couleur_bois)
        self.couleur_bord = _qcolor(couleur_bord)
        self.couleur_texte = _qcolor(couleur_texte)
        self.couleur_potence = _qcolor(couleur_potence)

    def _police_adaptee(
        self,
        texte: str,
        largeur_max: float,
        taille_max: float,
    ) -> QFont:
        """Réduit automatiquement la police si nécessaire."""
        taille = max(7, int(taille_max))

        while taille >= 7:
            police = QFont("Segoe UI", taille)
            police.setBold(True)
            if QFontMetricsF(police).horizontalAdvance(texte) <= largeur_max:
                return police
            taille -= 1

        police = QFont("Segoe UI", 7)
        police.setBold(True)
        return police

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        nom: str,
    ) -> None:
        """Dessine le panneau."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        largeur_potence = max(2.0, h * 0.060)
        x_potence = rect.left() + h * 0.18

        # Montant vertical.
        grad_potence = QLinearGradient(
            QPointF(x_potence - largeur_potence, 0),
            QPointF(x_potence + largeur_potence, 0),
        )
        grad_potence.setColorAt(0.0, _assombrir(self.couleur_potence, 0.22))
        grad_potence.setColorAt(0.50, _eclaircir(self.couleur_potence, 0.08))
        grad_potence.setColorAt(1.0, _assombrir(self.couleur_potence, 0.18))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_potence))
        painter.drawRoundedRect(
            QRectF(
                x_potence - largeur_potence / 2,
                rect.top() + h * 0.08,
                largeur_potence,
                h * 0.92,
            ),
            largeur_potence * 0.40,
            largeur_potence * 0.40,
        )

        # Potence horizontale.
        rect_traverse = QRectF(
            x_potence,
            rect.top() + h * 0.16,
            rect.width() * 0.30,
            max(2.0, h * 0.055),
        )
        painter.drawRoundedRect(
            rect_traverse,
            rect_traverse.height() * 0.30,
            rect_traverse.height() * 0.30,
        )

        # Suspentes.
        pen = QPen(_assombrir(self.couleur_potence, 0.12))
        pen.setWidthF(max(1.0, h * 0.018))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rect_panneau = QRectF(
            rect.left() + rect.width() * 0.28,
            rect.top() + h * 0.23,
            rect.width() * 0.72,
            h * 0.26,
        )

        for x in (
            rect_panneau.left() + rect_panneau.width() * 0.20,
            rect_panneau.right() - rect_panneau.width() * 0.20,
        ):
            painter.drawLine(
                QPointF(x, rect_traverse.bottom()),
                QPointF(x, rect_panneau.top()),
            )

        # Ombre.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha("#000000", 32))
        painter.drawRoundedRect(
            rect_panneau.translated(h * 0.020, h * 0.020),
            rect_panneau.height() * 0.16,
            rect_panneau.height() * 0.16,
        )

        grad_bois = QLinearGradient(rect_panneau.topLeft(), rect_panneau.bottomLeft())
        grad_bois.setColorAt(0.0, _eclaircir(self.couleur_bois, 0.12))
        grad_bois.setColorAt(0.55, self.couleur_bois)
        grad_bois.setColorAt(1.0, _assombrir(self.couleur_bois, 0.10))

        pen_bois = QPen(self.couleur_bord)
        pen_bois.setWidthF(max(1.0, h * 0.020))
        painter.setPen(pen_bois)
        painter.setBrush(QBrush(grad_bois))
        painter.drawRoundedRect(
            rect_panneau,
            rect_panneau.height() * 0.16,
            rect_panneau.height() * 0.16,
        )

        # Deux petites lattes décoratives.
        painter.setPen(
            QPen(
                _avec_alpha(_eclaircir(self.couleur_bois, 0.20), 120),
                max(1.0, h * 0.006),
            )
        )
        for p in (0.33, 0.66):
            y = rect_panneau.top() + rect_panneau.height() * p
            painter.drawLine(
                QPointF(rect_panneau.left() + rect_panneau.width() * 0.05, y),
                QPointF(rect_panneau.right() - rect_panneau.width() * 0.05, y),
            )

        police = self._police_adaptee(
            nom,
            rect_panneau.width() * 0.82,
            rect_panneau.height() * 0.42,
        )
        painter.setFont(police)
        painter.setPen(self.couleur_texte)
        painter.drawText(rect_panneau, Qt.AlignmentFlag.AlignCenter, nom)

        painter.restore()


# 3 -- Plaque de progression montagne -----------------------------------------


class PlaqueProgressionMontagne:
    """Petite plaque de progression en bois."""

    def __init__(
        self,
        couleur_bois: QColor | str = "#7F5D40",
        couleur_bord: QColor | str = "#523927",
        couleur_texte: QColor | str = "#FFF6E8",
        couleur_support: QColor | str = "#6A4B34",
    ):
        self.couleur_bois = _qcolor(couleur_bois)
        self.couleur_bord = _qcolor(couleur_bord)
        self.couleur_texte = _qcolor(couleur_texte)
        self.couleur_support = _qcolor(couleur_support)

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        i: int,
        n: int,
    ) -> None:
        """Dessine la petite plaque de progression."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        rect_plaque = QRectF(
            rect.left(),
            rect.top(),
            rect.width(),
            h * 0.44,
        )

        largeur_tige = max(2.0, h * 0.10)
        x_tige = rect.center().x()

        grad_tige = QLinearGradient(
            QPointF(x_tige - largeur_tige, 0),
            QPointF(x_tige + largeur_tige, 0),
        )
        grad_tige.setColorAt(0.0, _assombrir(self.couleur_support, 0.22))
        grad_tige.setColorAt(0.50, _eclaircir(self.couleur_support, 0.06))
        grad_tige.setColorAt(1.0, _assombrir(self.couleur_support, 0.18))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_tige))
        painter.drawRoundedRect(
            QRectF(
                x_tige - largeur_tige / 2,
                rect_plaque.bottom(),
                largeur_tige,
                rect.bottom() - rect_plaque.bottom(),
            ),
            largeur_tige * 0.38,
            largeur_tige * 0.38,
        )

        grad_bois = QLinearGradient(rect_plaque.topLeft(), rect_plaque.bottomLeft())
        grad_bois.setColorAt(0.0, _eclaircir(self.couleur_bois, 0.12))
        grad_bois.setColorAt(1.0, _assombrir(self.couleur_bois, 0.10))

        pen = QPen(self.couleur_bord)
        pen.setWidthF(max(1.0, h * 0.018))
        painter.setPen(pen)
        painter.setBrush(QBrush(grad_bois))
        painter.drawRoundedRect(
            rect_plaque,
            rect_plaque.height() * 0.18,
            rect_plaque.height() * 0.18,
        )

        police = QFont("Segoe UI", max(7, int(rect_plaque.height() * 0.30)))
        police.setBold(True)
        painter.setFont(police)
        painter.setPen(self.couleur_texte)
        painter.drawText(rect_plaque, Qt.AlignmentFlag.AlignCenter, f"{i}/{n}")

        painter.restore()


# 4 -- Petite gare de montagne -------------------------------------------------


class GareMontagne:
    """
    Petite gare de montagne en bois, mignonne et discrète.

    Logique visuelle
    ----------------
    Il s'agit d'une petite halte de montagne / petit chalet ferroviaire :
        - bâtiment bas en bois ;
        - toiture débordante ;
        - petit quai ;
        - panneau suspendu ;
        - lampe chaude ;
        - détails alpins discrets.

    Contrairement aux grandes gares, elle ne doit ni masquer le paysage,
    ni recouvrir les rails : elle se place comme un petit décor d'étape.
    """

    masque_paysage = False
    masque_rails = False

    def __init__(
        self,
        couleur_bois: QColor | str = "#9B6D47",
        couleur_bois_fonce: QColor | str = "#6B4A32",
        couleur_pierre: QColor | str = "#A59A90",
        couleur_toit: QColor | str = "#5B4E46",
        couleur_neige: QColor | str = "#F8FBFF",
        couleur_vitre: QColor | str = "#B8D6E2",
        couleur_quai: QColor | str = "#B2A89B",
        couleur_bord_quai: QColor | str = "#E7E0D5",
        couleur_accent: QColor | str = "#C64536",
        lampes_allumees: bool = True,
        etat_feu: str = "rouge",
        avec_neige: bool = False,
    ):
        self.couleur_bois = _qcolor(couleur_bois)
        self.couleur_bois_fonce = _qcolor(couleur_bois_fonce)
        self.couleur_pierre = _qcolor(couleur_pierre)
        self.couleur_toit = _qcolor(couleur_toit)
        self.couleur_neige = _qcolor(couleur_neige)
        self.couleur_vitre = _qcolor(couleur_vitre)
        self.couleur_quai = _qcolor(couleur_quai)
        self.couleur_bord_quai = _qcolor(couleur_bord_quai)
        self.couleur_accent = _qcolor(couleur_accent)

        self.lampes_allumees = lampes_allumees
        self.etat_feu = etat_feu.lower().strip()
        self.avec_neige = avec_neige

        self.panneau = PanneauGareMontagne(
            couleur_bois=self.couleur_bois_fonce,
            couleur_bord=_assombrir(self.couleur_bois_fonce, 0.16),
        )
        self.plaque = PlaqueProgressionMontagne(
            couleur_bois=_assombrir(self.couleur_bois, 0.10),
            couleur_support=self.couleur_bois_fonce,
        )

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    def largeur_recommandee(
        self,
        hauteur_scene: float,
    ) -> float:
        """Largeur idéale approximative."""
        return hauteur_scene * 2.55

    def _y_sol(
        self,
        rect: QRectF,
        y_rail: float | None,
    ) -> float:
        """Altitude de la petite plate-forme de gare."""
        if y_rail is not None:
            return y_rail - rect.height() * 0.050
        return rect.top() + rect.height() * 0.74

    # --------------------------------------------------------------------------
    # Éléments graphiques
    # --------------------------------------------------------------------------

    def _dessiner_quai(
        self,
        painter: QPainter,
        rect: QRectF,
        y_sol: float,
    ) -> None:
        """Dessine un petit quai discret derrière les rails."""
        h = rect.height()
        rect_quai = QRectF(
            rect.left() + rect.width() * 0.06,
            y_sol,
            rect.width() * 0.88,
            h * 0.060,
        )

        grad = QLinearGradient(rect_quai.topLeft(), rect_quai.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_quai, 0.08))
        grad.setColorAt(1.0, _assombrir(self.couleur_quai, 0.10))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(
            rect_quai,
            rect_quai.height() * 0.22,
            rect_quai.height() * 0.22,
        )

        rect_bord = QRectF(
            rect_quai.left(),
            rect_quai.top(),
            rect_quai.width(),
            max(2.0, h * 0.010),
        )
        painter.setBrush(self.couleur_bord_quai)
        painter.drawRect(rect_bord)

        pen = QPen(_avec_alpha(_assombrir(self.couleur_quai, 0.22), 90))
        pen.setWidthF(max(1.0, h * 0.0026))
        painter.setPen(pen)

        largeur_dalle = rect_quai.width() / 7
        x = rect_quai.left() + largeur_dalle
        while x < rect_quai.right():
            painter.drawLine(
                QPointF(x, rect_quai.top()),
                QPointF(x, rect_quai.bottom()),
            )
            x += largeur_dalle

    def _dessiner_fenetre(
        self,
        painter: QPainter,
        rect_fenetre: QRectF,
    ) -> None:
        """Dessine une fenêtre de chalet."""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect_fenetre.height()
        ep = h * 0.10

        grad_cadre = QLinearGradient(rect_fenetre.topLeft(), rect_fenetre.bottomLeft())
        grad_cadre.setColorAt(0.0, _eclaircir(self.couleur_bois_fonce, 0.10))
        grad_cadre.setColorAt(1.0, _assombrir(self.couleur_bois_fonce, 0.10))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_cadre))
        painter.drawRoundedRect(
            rect_fenetre,
            h * 0.08,
            h * 0.08,
        )

        rect_vitre = rect_fenetre.adjusted(ep, ep, -ep, -ep)

        grad_vitre = QLinearGradient(rect_vitre.topLeft(), rect_vitre.bottomLeft())
        if self.lampes_allumees:
            grad_vitre.setColorAt(0.0, QColor("#FFE7A8"))
            grad_vitre.setColorAt(1.0, QColor("#E8C97A"))
        else:
            grad_vitre.setColorAt(0.0, _eclaircir(self.couleur_vitre, 0.15))
            grad_vitre.setColorAt(1.0, _assombrir(self.couleur_vitre, 0.05))

        painter.setBrush(QBrush(grad_vitre))
        painter.drawRoundedRect(
            rect_vitre,
            h * 0.05,
            h * 0.05,
        )

        pen = QPen(_avec_alpha(_assombrir(self.couleur_bois_fonce, 0.12), 175))
        pen.setWidthF(max(1.0, h * 0.040))
        painter.setPen(pen)
        painter.drawLine(
            QPointF(rect_vitre.center().x(), rect_vitre.top()),
            QPointF(rect_vitre.center().x(), rect_vitre.bottom()),
        )
        painter.drawLine(
            QPointF(rect_vitre.left(), rect_vitre.center().y()),
            QPointF(rect_vitre.right(), rect_vitre.center().y()),
        )

        painter.setPen(QPen(_avec_alpha("#FFFFFF", 55), max(1.0, h * 0.018)))
        painter.drawLine(
            QPointF(
                rect_vitre.left() + rect_vitre.width() * 0.70,
                rect_vitre.top() + rect_vitre.height() * 0.10,
            ),
            QPointF(
                rect_vitre.left() + rect_vitre.width() * 0.52,
                rect_vitre.bottom() - rect_vitre.height() * 0.10,
            ),
        )

        # Petit bac à fleurs.
        rect_bac = QRectF(
            rect_fenetre.left() + rect_fenetre.width() * 0.10,
            rect_fenetre.bottom() + h * 0.05,
            rect_fenetre.width() * 0.80,
            h * 0.14,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_assombrir(self.couleur_bois_fonce, 0.08))
        painter.drawRoundedRect(rect_bac, h * 0.03, h * 0.03)

        for p, couleur in (
            (0.18, "#D64B58"),
            (0.38, "#F0C84F"),
            (0.58, "#D64B58"),
            (0.78, "#F0C84F"),
        ):
            x = rect_bac.left() + rect_bac.width() * p
            painter.setBrush(QColor(couleur))
            painter.drawEllipse(
                QPointF(x, rect_bac.top() + rect_bac.height() * 0.35),
                h * 0.035,
                h * 0.035,
            )
            painter.setBrush(QColor("#5E8D4E"))
            painter.drawEllipse(
                QPointF(x, rect_bac.top() + rect_bac.height() * 0.68),
                h * 0.020,
                h * 0.020,
            )

        painter.restore()

    def _dessiner_porte(
        self,
        painter: QPainter,
        rect_porte: QRectF,
    ) -> None:
        """Dessine une petite porte en bois."""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect_porte.height()
        grad = QLinearGradient(rect_porte.topLeft(), rect_porte.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_bois_fonce, 0.12))
        grad.setColorAt(1.0, _assombrir(self.couleur_bois_fonce, 0.08))

        painter.setPen(
            QPen(_assombrir(self.couleur_bois_fonce, 0.25), max(1.0, h * 0.028))
        )
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(
            rect_porte,
            h * 0.07,
            h * 0.07,
        )

        painter.setPen(
            QPen(
                _avec_alpha(_eclaircir(self.couleur_bois_fonce, 0.12), 120),
                max(1.0, h * 0.014),
            )
        )
        for p in (0.28, 0.50, 0.72):
            x = rect_porte.left() + rect_porte.width() * p
            painter.drawLine(
                QPointF(x, rect_porte.top() + h * 0.12),
                QPointF(x, rect_porte.bottom() - h * 0.12),
            )

        # Petite vitre de porte.
        rect_vitre = QRectF(
            rect_porte.left() + rect_porte.width() * 0.25,
            rect_porte.top() + rect_porte.height() * 0.18,
            rect_porte.width() * 0.50,
            rect_porte.height() * 0.24,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(
            QColor("#F2D48D") if self.lampes_allumees else self.couleur_vitre
        )
        painter.drawRoundedRect(rect_vitre, h * 0.04, h * 0.04)

        # Poignée.
        painter.setBrush(QColor("#CBAA67"))
        painter.drawEllipse(
            QPointF(
                rect_porte.right() - rect_porte.width() * 0.18,
                rect_porte.top() + rect_porte.height() * 0.56,
            ),
            h * 0.030,
            h * 0.030,
        )

        painter.restore()

    def _dessiner_chalet(
        self,
        painter: QPainter,
        rect_batiment: QRectF,
    ) -> None:
        """Dessine le petit bâtiment principal."""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect_batiment.height()

        # Ombre portée légère.
        ombre = rect_batiment.translated(h * 0.035, h * 0.028)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha("#000000", 28))
        painter.drawRoundedRect(
            ombre,
            h * 0.05,
            h * 0.05,
        )

        # Socle en pierre.
        hauteur_socle = rect_batiment.height() * 0.16
        rect_socle = QRectF(
            rect_batiment.left(),
            rect_batiment.bottom() - hauteur_socle,
            rect_batiment.width(),
            hauteur_socle,
        )
        grad_socle = QLinearGradient(rect_socle.topLeft(), rect_socle.bottomLeft())
        grad_socle.setColorAt(0.0, _eclaircir(self.couleur_pierre, 0.08))
        grad_socle.setColorAt(1.0, _assombrir(self.couleur_pierre, 0.12))
        painter.setBrush(QBrush(grad_socle))
        painter.drawRoundedRect(
            rect_socle,
            h * 0.03,
            h * 0.03,
        )

        # Corps principal en bois.
        rect_corps = QRectF(
            rect_batiment.left(),
            rect_batiment.top() + h * 0.12,
            rect_batiment.width(),
            rect_batiment.height() * 0.72,
        )
        grad_bois = QLinearGradient(rect_corps.topLeft(), rect_corps.bottomLeft())
        grad_bois.setColorAt(0.0, _eclaircir(self.couleur_bois, 0.08))
        grad_bois.setColorAt(0.60, self.couleur_bois)
        grad_bois.setColorAt(1.0, _assombrir(self.couleur_bois, 0.08))

        painter.setBrush(QBrush(grad_bois))
        painter.setPen(
            QPen(_assombrir(self.couleur_bois_fonce, 0.18), max(1.0, h * 0.018))
        )
        painter.drawRoundedRect(
            rect_corps,
            h * 0.05,
            h * 0.05,
        )

        # Lattes horizontales.
        painter.setPen(
            QPen(
                _avec_alpha(_assombrir(self.couleur_bois_fonce, 0.05), 120),
                max(1.0, h * 0.010),
            )
        )
        for p in (0.14, 0.28, 0.42, 0.56, 0.70, 0.84):
            y = rect_corps.top() + rect_corps.height() * p
            painter.drawLine(
                QPointF(rect_corps.left() + rect_corps.width() * 0.03, y),
                QPointF(rect_corps.right() - rect_corps.width() * 0.03, y),
            )

        # Toiture.
        debord = rect_batiment.width() * 0.08
        y_faitage = rect_batiment.top() - h * 0.02
        path_toit = QPainterPath()
        path_toit.moveTo(rect_batiment.left() - debord, rect_corps.top() + h * 0.08)
        path_toit.lineTo(rect_batiment.center().x(), y_faitage)
        path_toit.lineTo(rect_batiment.right() + debord, rect_corps.top() + h * 0.08)
        path_toit.lineTo(
            rect_batiment.right() + debord * 0.90, rect_corps.top() + h * 0.16
        )
        path_toit.lineTo(
            rect_batiment.left() - debord * 0.90, rect_corps.top() + h * 0.16
        )
        path_toit.closeSubpath()

        grad_toit = QLinearGradient(
            QPointF(rect_batiment.left(), y_faitage),
            QPointF(rect_batiment.left(), rect_corps.top() + h * 0.16),
        )
        grad_toit.setColorAt(0.0, _eclaircir(self.couleur_toit, 0.10))
        grad_toit.setColorAt(1.0, _assombrir(self.couleur_toit, 0.08))
        painter.setPen(QPen(_assombrir(self.couleur_toit, 0.18), max(1.0, h * 0.018)))
        painter.setBrush(QBrush(grad_toit))
        painter.drawPath(path_toit)

        # Panne de rive inférieure.
        painter.setBrush(_assombrir(self.couleur_bois_fonce, 0.06))
        painter.drawRoundedRect(
            QRectF(
                rect_batiment.left() - debord * 0.80,
                rect_corps.top() + h * 0.14,
                rect_batiment.width() + debord * 1.60,
                h * 0.028,
            ),
            h * 0.01,
            h * 0.01,
        )

        # Neige sur le toit si demandé.
        if self.avec_neige:
            path_neige = QPainterPath()
            path_neige.moveTo(
                rect_batiment.left() - debord * 0.72, rect_corps.top() + h * 0.09
            )
            path_neige.quadTo(
                QPointF(rect_batiment.center().x(), y_faitage + h * 0.04),
                QPointF(
                    rect_batiment.right() + debord * 0.72, rect_corps.top() + h * 0.09
                ),
            )
            path_neige.lineTo(
                rect_batiment.right() + debord * 0.50, rect_corps.top() + h * 0.13
            )
            path_neige.quadTo(
                QPointF(rect_batiment.center().x(), y_faitage + h * 0.07),
                QPointF(
                    rect_batiment.left() - debord * 0.50, rect_corps.top() + h * 0.13
                ),
            )
            path_neige.closeSubpath()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self.couleur_neige)
            painter.drawPath(path_neige)

        # Petite cheminée.
        rect_cheminee = QRectF(
            rect_batiment.left() + rect_batiment.width() * 0.68,
            rect_batiment.top() + h * 0.02,
            rect_batiment.width() * 0.08,
            h * 0.18,
        )
        painter.setBrush(_assombrir(self.couleur_pierre, 0.08))
        painter.setPen(QPen(_assombrir(self.couleur_pierre, 0.18), max(1.0, h * 0.010)))
        painter.drawRoundedRect(rect_cheminee, h * 0.02, h * 0.02)

        # Horloge ronde sous le pignon.
        centre_horloge = QPointF(
            rect_batiment.center().x(),
            rect_corps.top() + rect_corps.height() * 0.18,
        )
        rayon_horloge = h * 0.055
        painter.setPen(
            QPen(_assombrir(self.couleur_bois_fonce, 0.14), max(1.0, h * 0.014))
        )
        painter.setBrush(QColor("#F7F3EA"))
        painter.drawEllipse(centre_horloge, rayon_horloge, rayon_horloge)

        painter.setPen(
            QPen(QColor("#3F3730"), max(1.0, h * 0.010), cap=Qt.PenCapStyle.RoundCap)
        )
        painter.drawLine(
            centre_horloge,
            QPointF(centre_horloge.x(), centre_horloge.y() - rayon_horloge * 0.45),
        )
        painter.drawLine(
            centre_horloge,
            QPointF(centre_horloge.x() + rayon_horloge * 0.30, centre_horloge.y()),
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#3F3730"))
        painter.drawEllipse(centre_horloge, rayon_horloge * 0.08, rayon_horloge * 0.08)

        # Baies alignées.
        largeur_fen = rect_corps.width() * 0.18
        hauteur_fen = rect_corps.height() * 0.36
        y_fen = rect_corps.top() + rect_corps.height() * 0.40

        self._dessiner_fenetre(
            painter,
            QRectF(
                rect_corps.left() + rect_corps.width() * 0.10,
                y_fen,
                largeur_fen,
                hauteur_fen,
            ),
        )
        self._dessiner_porte(
            painter,
            QRectF(
                rect_corps.left() + rect_corps.width() * 0.40,
                rect_corps.top() + rect_corps.height() * 0.38,
                rect_corps.width() * 0.18,
                rect_corps.height() * 0.44,
            ),
        )
        self._dessiner_fenetre(
            painter,
            QRectF(
                rect_corps.left() + rect_corps.width() * 0.72,
                y_fen,
                largeur_fen,
                hauteur_fen,
            ),
        )

        painter.restore()

    def _dessiner_banc(
        self,
        painter: QPainter,
        rect_banc: QRectF,
    ) -> None:
        """Dessine un petit banc de quai."""
        if rect_banc.width() <= 0 or rect_banc.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        grad = QLinearGradient(rect_banc.topLeft(), rect_banc.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_bois, 0.10))
        grad.setColorAt(1.0, _assombrir(self.couleur_bois, 0.12))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))

        rect_dossier = QRectF(
            rect_banc.left() + rect_banc.width() * 0.08,
            rect_banc.top() + rect_banc.height() * 0.12,
            rect_banc.width() * 0.84,
            rect_banc.height() * 0.18,
        )
        rect_assise = QRectF(
            rect_banc.left(),
            rect_banc.top() + rect_banc.height() * 0.44,
            rect_banc.width(),
            rect_banc.height() * 0.16,
        )

        painter.drawRoundedRect(
            rect_dossier, rect_dossier.height() * 0.22, rect_dossier.height() * 0.22
        )
        painter.drawRoundedRect(
            rect_assise, rect_assise.height() * 0.22, rect_assise.height() * 0.22
        )

        pen = QPen(_assombrir(self.couleur_bois_fonce, 0.12))
        pen.setWidthF(max(1.0, rect_banc.width() * 0.055))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        for x in (
            rect_banc.left() + rect_banc.width() * 0.22,
            rect_banc.right() - rect_banc.width() * 0.22,
        ):
            painter.drawLine(
                QPointF(x, rect_assise.bottom()), QPointF(x, rect_banc.bottom())
            )

        painter.restore()

    def _dessiner_lampe(
        self,
        painter: QPainter,
        rect_lampe: QRectF,
    ) -> None:
        """Dessine une petite lanterne de quai."""
        if rect_lampe.width() <= 0 or rect_lampe.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect_lampe.height()
        x_centre = rect_lampe.center().x()
        largeur_mat = max(2.0, h * 0.055)

        grad_mat = QLinearGradient(
            QPointF(x_centre - largeur_mat, 0),
            QPointF(x_centre + largeur_mat, 0),
        )
        grad_mat.setColorAt(0.0, _assombrir(self.couleur_bois_fonce, 0.20))
        grad_mat.setColorAt(0.50, _eclaircir(self.couleur_bois_fonce, 0.08))
        grad_mat.setColorAt(1.0, _assombrir(self.couleur_bois_fonce, 0.16))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_mat))
        painter.drawRoundedRect(
            QRectF(
                x_centre - largeur_mat / 2,
                rect_lampe.top() + h * 0.18,
                largeur_mat,
                h * 0.82,
            ),
            largeur_mat * 0.35,
            largeur_mat * 0.35,
        )

        # Potence.
        pen = QPen(_assombrir(self.couleur_bois_fonce, 0.08))
        pen.setWidthF(max(1.0, h * 0.025))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(
            QPointF(x_centre, rect_lampe.top() + h * 0.26),
            QPointF(x_centre + rect_lampe.width() * 0.20, rect_lampe.top() + h * 0.26),
        )
        painter.drawLine(
            QPointF(x_centre + rect_lampe.width() * 0.18, rect_lampe.top() + h * 0.26),
            QPointF(x_centre + rect_lampe.width() * 0.10, rect_lampe.top() + h * 0.34),
        )

        centre = QPointF(
            x_centre + rect_lampe.width() * 0.20,
            rect_lampe.top() + h * 0.36,
        )
        rayon = h * 0.08

        if self.lampes_allumees:
            halo = QRadialGradient(centre, rayon * 3.0)
            halo.setColorAt(0.0, QColor(255, 236, 170, 95))
            halo.setColorAt(0.45, QColor(255, 222, 145, 30))
            halo.setColorAt(1.0, QColor(255, 222, 145, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(centre, rayon * 3.0, rayon * 3.0)

        painter.setBrush(_assombrir(self.couleur_bois_fonce, 0.06))
        painter.drawEllipse(centre, rayon * 1.05, rayon * 1.05)
        painter.setBrush(
            QColor("#FFE4A0") if self.lampes_allumees else QColor("#B7C2C7")
        )
        painter.drawEllipse(centre, rayon * 0.72, rayon * 0.72)

        painter.restore()

    def _dessiner_sapin(
        self,
        painter: QPainter,
        centre: QPointF,
        taille: float,
    ) -> None:
        """Dessine un petit sapin décoratif."""
        if taille <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Tronc.
        rect_tronc = QRectF(
            centre.x() - taille * 0.08,
            centre.y() - taille * 0.14,
            taille * 0.16,
            taille * 0.20,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#6E4A32"))
        painter.drawRoundedRect(rect_tronc, taille * 0.02, taille * 0.02)

        # Trois étages de feuillage.
        painter.setBrush(QColor("#4F7E55"))
        for decalage_y, largeur in (
            (-0.52, 0.80),
            (-0.34, 1.00),
            (-0.14, 1.18),
        ):
            path = QPainterPath()
            y_sommet = centre.y() + taille * decalage_y
            demi_l = taille * largeur * 0.26
            y_base = y_sommet + taille * 0.26
            path.moveTo(centre.x(), y_sommet)
            path.lineTo(centre.x() + demi_l, y_base)
            path.lineTo(centre.x() - demi_l, y_base)
            path.closeSubpath()
            painter.drawPath(path)

        if self.avec_neige:
            painter.setBrush(self.couleur_neige)
            for decalage_y, largeur in (
                (-0.45, 0.60),
                (-0.27, 0.78),
                (-0.07, 0.88),
            ):
                path = QPainterPath()
                y_sommet = centre.y() + taille * decalage_y
                demi_l = taille * largeur * 0.16
                y_base = y_sommet + taille * 0.07
                path.moveTo(centre.x(), y_sommet)
                path.lineTo(centre.x() + demi_l, y_base)
                path.lineTo(centre.x() - demi_l, y_base)
                path.closeSubpath()
                painter.drawPath(path)

        painter.restore()

    def _dessiner_petit_feu(
        self,
        painter: QPainter,
        rect_feu: QRectF,
    ) -> None:
        """Dessine un tout petit feu de manœuvre / signal discret."""
        if rect_feu.width() <= 0 or rect_feu.height() <= 0:
            return

        etat = (
            self.etat_feu if self.etat_feu in {"rouge", "vert", "orange"} else "rouge"
        )

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect_feu.height()
        cx = rect_feu.center().x()

        # Mât.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_assombrir(self.couleur_bois_fonce, 0.06))
        painter.drawRoundedRect(
            QRectF(
                cx - h * 0.035,
                rect_feu.top() + h * 0.28,
                h * 0.07,
                h * 0.72,
            ),
            h * 0.02,
            h * 0.02,
        )

        # Boîtier.
        rect_boite = QRectF(
            cx - h * 0.10,
            rect_feu.top(),
            h * 0.20,
            h * 0.34,
        )
        painter.setBrush(QColor("#43484C"))
        painter.drawRoundedRect(rect_boite, h * 0.03, h * 0.03)

        def dessiner_optique(y_centre: float, couleur: str, allume: bool) -> None:
            centre = QPointF(cx, y_centre)
            rayon = h * 0.042
            if allume:
                halo = QRadialGradient(centre, rayon * 2.5)
                halo.setColorAt(0.0, _avec_alpha(couleur, 100))
                halo.setColorAt(0.40, _avec_alpha(couleur, 32))
                halo.setColorAt(1.0, _avec_alpha(couleur, 0))
                painter.setBrush(QBrush(halo))
                painter.drawEllipse(centre, rayon * 2.5, rayon * 2.5)
            painter.setBrush(_assombrir("#43484C", 0.10))
            painter.drawEllipse(centre, rayon * 1.18, rayon * 1.18)
            grad = QRadialGradient(centre, rayon)
            grad.setColorAt(0.0, _eclaircir(couleur, 0.34 if allume else 0.10))
            grad.setColorAt(1.0, _assombrir(couleur, 0.45 if allume else 0.60))
            painter.setBrush(QBrush(grad))
            painter.drawEllipse(centre, rayon, rayon)

        dessiner_optique(
            rect_boite.top() + rect_boite.height() * 0.33,
            "#D14B41",
            etat == "rouge",
        )
        dessiner_optique(
            rect_boite.top() + rect_boite.height() * 0.72,
            "#4AA35B",
            etat == "vert",
        )
        if etat == "orange":
            dessiner_optique(
                rect_boite.top() + rect_boite.height() * 0.52,
                "#D09C35",
                True,
            )

        painter.restore()

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
        """Dessine la petite gare derrière le train."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        w = rect.width()
        y_sol = self._y_sol(rect, y_rail)

        # ------------------------------------------------------------------
        # Petit quai discret
        # ------------------------------------------------------------------

        self._dessiner_quai(painter, rect, y_sol)

        # ------------------------------------------------------------------
        # Petit bâtiment principal
        # ------------------------------------------------------------------

        rect_chalet = QRectF(
            rect.left() + w * 0.12,
            y_sol - h * 0.315,
            w * 0.28,
            h * 0.315,
        )
        self._dessiner_chalet(painter, rect_chalet)

        # ------------------------------------------------------------------
        # Panneau + progression
        # ------------------------------------------------------------------

        rect_panneau = QRectF(
            rect.left() + w * 0.48,
            y_sol - h * 0.24,
            w * 0.20,
            h * 0.23,
        )
        self.panneau.peindre(painter, rect_panneau, nom_pays)

        if i is not None and n is not None:
            rect_plaque = QRectF(
                rect_panneau.right() + h * 0.02,
                y_sol - h * 0.21,
                h * 0.11,
                h * 0.19,
            )
            self.plaque.peindre(painter, rect_plaque, i, n)

        # ------------------------------------------------------------------
        # Banc, lanterne et petit feu
        # ------------------------------------------------------------------

        self._dessiner_banc(
            painter,
            QRectF(
                rect.left() + w * 0.70,
                y_sol - h * 0.085,
                w * 0.08,
                h * 0.08,
            ),
        )

        self._dessiner_lampe(
            painter,
            QRectF(
                rect.left() + w * 0.80,
                y_sol - h * 0.20,
                w * 0.05,
                h * 0.20,
            ),
        )

        self._dessiner_petit_feu(
            painter,
            QRectF(
                rect.left() + w * 0.89,
                y_sol - h * 0.18,
                w * 0.035,
                h * 0.18,
            ),
        )

        # ------------------------------------------------------------------
        # Deux petits sapins décoratifs
        # ------------------------------------------------------------------

        self._dessiner_sapin(
            painter,
            QPointF(rect.left() + w * 0.08, y_sol),
            h * 0.18,
        )
        self._dessiner_sapin(
            painter,
            QPointF(rect.left() + w * 0.45, y_sol + h * 0.01),
            h * 0.15,
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
        """Ne dessine rien devant le train afin de ne rien masquer."""
        return

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
        """Dessine la gare complète."""
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
