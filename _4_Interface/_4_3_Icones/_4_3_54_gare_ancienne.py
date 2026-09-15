################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.54 – Classe de création d'une gare ancienne                              #
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


# 2 -- Panneau principal de gare ----------------------------------------------


class PanneauGareAncienne:
    """Panneau élégant de quai avec support métallique."""

    def __init__(
        self,
        couleur_fond: QColor | str = "#EFE4C7",
        couleur_bord: QColor | str = "#4E4338",
        couleur_texte: QColor | str = "#2E2A27",
        couleur_metal: QColor | str = "#5D666B",
    ):
        self.couleur_fond = _qcolor(couleur_fond)
        self.couleur_bord = _qcolor(couleur_bord)
        self.couleur_texte = _qcolor(couleur_texte)
        self.couleur_metal = _qcolor(couleur_metal)

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

        # Tige / support
        largeur_tige = max(2.0, rect.width() * 0.035)
        x_tige = rect.center().x()

        gradient_tige = QLinearGradient(
            QPointF(x_tige - largeur_tige, 0),
            QPointF(x_tige + largeur_tige, 0),
        )
        gradient_tige.setColorAt(0.0, _assombrir(self.couleur_metal, 0.22))
        gradient_tige.setColorAt(0.5, _eclaircir(self.couleur_metal, 0.20))
        gradient_tige.setColorAt(1.0, _assombrir(self.couleur_metal, 0.20))

        rect_tige = QRectF(
            x_tige - largeur_tige / 2,
            rect.top() + rect.height() * 0.28,
            largeur_tige,
            rect.height() * 0.72,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient_tige))
        painter.drawRoundedRect(
            rect_tige,
            largeur_tige * 0.45,
            largeur_tige * 0.45,
        )

        # Plaque
        rect_plaque = QRectF(
            rect.left(),
            rect.top(),
            rect.width(),
            rect.height() * 0.38,
        )

        ombre = rect_plaque.translated(rect.width() * 0.018, rect.height() * 0.025)
        painter.setBrush(_avec_alpha("#000000", 35))
        painter.drawRoundedRect(
            ombre,
            rect_plaque.height() * 0.16,
            rect_plaque.height() * 0.16,
        )

        gradient_plaque = QLinearGradient(
            rect_plaque.topLeft(),
            rect_plaque.bottomLeft(),
        )
        gradient_plaque.setColorAt(0.0, _eclaircir(self.couleur_fond, 0.16))
        gradient_plaque.setColorAt(1.0, _assombrir(self.couleur_fond, 0.06))

        pen = QPen(self.couleur_bord)
        pen.setWidthF(max(1.1, rect.height() * 0.018))

        painter.setPen(pen)
        painter.setBrush(QBrush(gradient_plaque))
        painter.drawRoundedRect(
            rect_plaque,
            rect_plaque.height() * 0.16,
            rect_plaque.height() * 0.16,
        )

        # Petits rivets
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_assombrir(self.couleur_fond, 0.22))

        marge = rect_plaque.width() * 0.10
        rayon = max(1.0, rect_plaque.height() * 0.06)

        for x in (
            rect_plaque.left() + marge,
            rect_plaque.right() - marge,
        ):
            for y in (
                rect_plaque.top() + marge * 0.55,
                rect_plaque.bottom() - marge * 0.55,
            ):
                painter.drawEllipse(QPointF(x, y), rayon, rayon)

        # Texte
        marge_texte = rect_plaque.width() * 0.08

        police = self._police_adaptee(
            nom,
            rect_plaque.width() - 2 * marge_texte,
            rect_plaque.height() * 0.36,
        )

        painter.setFont(police)
        painter.setPen(self.couleur_texte)
        painter.drawText(
            rect_plaque.adjusted(marge_texte, 0, -marge_texte, 0),
            Qt.AlignmentFlag.AlignCenter,
            nom,
        )

        painter.restore()


# 3 -- Plaque métallique de progression ---------------------------------------


class PlaqueProgressionAncienne:
    """Petite plaque de progression i/n à support métallique."""

    def __init__(
        self,
        couleur_plaque: QColor | str = "#566168",
        couleur_bord: QColor | str = "#30383D",
        couleur_texte: QColor | str = "#F3EEE4",
        couleur_tige: QColor | str = "#555E63",
    ):
        self.couleur_plaque = _qcolor(couleur_plaque)
        self.couleur_bord = _qcolor(couleur_bord)
        self.couleur_texte = _qcolor(couleur_texte)
        self.couleur_tige = _qcolor(couleur_tige)

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        i: int,
        n: int,
    ) -> None:
        """Dessine la plaque et sa tige."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect_plaque = QRectF(
            rect.left(),
            rect.top(),
            rect.width(),
            rect.height() * 0.42,
        )

        x_tige = rect.center().x()
        largeur_tige = max(2.0, rect.width() * 0.08)

        gradient_tige = QLinearGradient(
            QPointF(x_tige - largeur_tige, 0),
            QPointF(x_tige + largeur_tige, 0),
        )
        gradient_tige.setColorAt(0.0, _assombrir(self.couleur_tige, 0.25))
        gradient_tige.setColorAt(0.5, _eclaircir(self.couleur_tige, 0.28))
        gradient_tige.setColorAt(1.0, _assombrir(self.couleur_tige, 0.20))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient_tige))
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

        gradient = QLinearGradient(
            rect_plaque.topLeft(),
            rect_plaque.bottomRight(),
        )
        gradient.setColorAt(0.0, _eclaircir(self.couleur_plaque, 0.26))
        gradient.setColorAt(0.40, self.couleur_plaque)
        gradient.setColorAt(1.0, _assombrir(self.couleur_plaque, 0.22))

        pen = QPen(self.couleur_bord)
        pen.setWidthF(max(1.0, rect.width() * 0.030))

        painter.setPen(pen)
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(
            rect_plaque,
            rect_plaque.height() * 0.16,
            rect_plaque.height() * 0.16,
        )

        # Rivets
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_eclaircir(self.couleur_plaque, 0.40))

        r = max(1.0, rect.width() * 0.025)
        marge = rect.width() * 0.12

        for x in (
            rect_plaque.left() + marge,
            rect_plaque.right() - marge,
        ):
            painter.drawEllipse(
                QPointF(x, rect_plaque.top() + marge * 0.8),
                r,
                r,
            )

        police = QFont("Segoe UI", max(7, int(rect_plaque.height() * 0.30)))
        police.setBold(True)

        painter.setFont(police)
        painter.setPen(self.couleur_texte)
        painter.drawText(
            rect_plaque,
            Qt.AlignmentFlag.AlignCenter,
            f"{i}/{n}",
        )

        painter.restore()


# 4 -- Feu ferroviaire ---------------------------------------------------------


class FeuFerroviaire:
    """Petit feu ferroviaire ancien, centré sur un mât unique."""

    def __init__(
        self,
        couleur_metal: QColor | str = "#40464A",
        couleur_support: QColor | str = "#4F575C",
    ):
        self.couleur_metal = _qcolor(couleur_metal)
        self.couleur_support = _qcolor(couleur_support)

    def _dessiner_optique(
        self,
        painter: QPainter,
        centre: QPointF,
        rayon: float,
        couleur: QColor,
        allume: bool,
    ) -> None:
        """Dessine une optique avec bague métallique, halo et reflet."""
        painter.save()

        if allume:
            halo = QRadialGradient(centre, rayon * 3.0)
            halo.setColorAt(0.0, _avec_alpha(couleur, 115))
            halo.setColorAt(0.35, _avec_alpha(couleur, 48))
            halo.setColorAt(1.0, _avec_alpha(couleur, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(centre, rayon * 3.0, rayon * 3.0)

        # Bague / cuvelage.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_assombrir(self.couleur_metal, 0.42))
        painter.drawEllipse(centre, rayon * 1.27, rayon * 1.27)

        grad = QRadialGradient(
            QPointF(centre.x() - rayon * 0.20, centre.y() - rayon * 0.22),
            rayon * 1.15,
        )
        grad.setColorAt(0.0, _eclaircir(couleur, 0.42 if allume else 0.12))
        grad.setColorAt(0.58, couleur if allume else _assombrir(couleur, 0.44))
        grad.setColorAt(1.0, _assombrir(couleur, 0.56))

        painter.setBrush(QBrush(grad))
        painter.drawEllipse(centre, rayon, rayon)

        # Petit éclat dans le verre.
        painter.setBrush(_avec_alpha("#FFFFFF", 65 if allume else 28))
        painter.drawEllipse(
            QPointF(centre.x() - rayon * 0.24, centre.y() - rayon * 0.26),
            rayon * 0.25,
            rayon * 0.16,
        )

        painter.restore()

    def _dessiner_casquette(
        self,
        painter: QPainter,
        centre: QPointF,
        rayon: float,
    ) -> None:
        """Dessine la petite visière métallique au-dessus d'une optique."""
        path = QPainterPath()
        path.moveTo(centre.x() - rayon * 1.28, centre.y() - rayon * 0.58)
        path.quadTo(
            QPointF(centre.x(), centre.y() - rayon * 1.30),
            QPointF(centre.x() + rayon * 1.28, centre.y() - rayon * 0.58),
        )
        path.lineTo(centre.x() + rayon * 1.05, centre.y() - rayon * 0.25)
        path.quadTo(
            QPointF(centre.x(), centre.y() - rayon * 0.82),
            QPointF(centre.x() - rayon * 1.05, centre.y() - rayon * 0.25),
        )
        path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_assombrir(self.couleur_metal, 0.18))
        painter.drawPath(path)

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        etat: str = "rouge",
    ) -> None:
        """Dessine le feu complet, parfaitement centré dans ``rect``."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        etat = etat.lower().strip()
        if etat not in {"rouge", "vert", "orange"}:
            etat = "rouge"

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        cx = rect.center().x()

        # Le coffret est indépendant de la largeur du rect afin de ne pas
        # devenir trop large dans une scène panoramique.
        largeur_boite = min(rect.width() * 0.84, h * 0.34)
        hauteur_boite = h * 0.44
        y_boite = rect.top() + h * 0.015

        rect_boite = QRectF(
            cx - largeur_boite / 2,
            y_boite,
            largeur_boite,
            hauteur_boite,
        )

        # Mât, strictement centré sous le coffret.
        largeur_mat = max(2.5, h * 0.055)
        rect_mat = QRectF(
            cx - largeur_mat / 2,
            rect_boite.bottom() - h * 0.008,
            largeur_mat,
            rect.bottom() - h * 0.055 - rect_boite.bottom() + h * 0.008,
        )

        gradient_mat = QLinearGradient(
            QPointF(rect_mat.left(), 0),
            QPointF(rect_mat.right(), 0),
        )
        gradient_mat.setColorAt(0.0, _assombrir(self.couleur_support, 0.28))
        gradient_mat.setColorAt(0.48, _eclaircir(self.couleur_support, 0.18))
        gradient_mat.setColorAt(1.0, _assombrir(self.couleur_support, 0.24))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient_mat))
        painter.drawRoundedRect(
            rect_mat,
            largeur_mat * 0.42,
            largeur_mat * 0.42,
        )

        # Socle vissé au sol.
        rect_socle = QRectF(
            cx - h * 0.075,
            rect.bottom() - h * 0.060,
            h * 0.150,
            h * 0.045,
        )
        painter.setBrush(_assombrir(self.couleur_support, 0.22))
        painter.drawRoundedRect(
            rect_socle,
            rect_socle.height() * 0.22,
            rect_socle.height() * 0.22,
        )

        # Coffret.
        gradient_boite = QLinearGradient(
            rect_boite.topLeft(),
            rect_boite.bottomRight(),
        )
        gradient_boite.setColorAt(0.0, _eclaircir(self.couleur_metal, 0.15))
        gradient_boite.setColorAt(0.45, self.couleur_metal)
        gradient_boite.setColorAt(1.0, _assombrir(self.couleur_metal, 0.22))

        pen_boite = QPen(_assombrir(self.couleur_metal, 0.40))
        pen_boite.setWidthF(max(1.0, h * 0.017))
        painter.setPen(pen_boite)
        painter.setBrush(QBrush(gradient_boite))
        painter.drawRoundedRect(
            rect_boite,
            largeur_boite * 0.12,
            largeur_boite * 0.12,
        )

        # Charnières / petites attaches latérales.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_eclaircir(self.couleur_metal, 0.18))
        for y in (
            rect_boite.top() + hauteur_boite * 0.18,
            rect_boite.bottom() - hauteur_boite * 0.18,
        ):
            painter.drawRoundedRect(
                QRectF(
                    rect_boite.right() - h * 0.014,
                    y - h * 0.010,
                    h * 0.020,
                    h * 0.020,
                ),
                h * 0.004,
                h * 0.004,
            )

        rayon = min(largeur_boite * 0.19, hauteur_boite * 0.095)
        centres = [
            QPointF(cx, rect_boite.top() + hauteur_boite * 0.20),
            QPointF(cx, rect_boite.top() + hauteur_boite * 0.50),
            QPointF(cx, rect_boite.top() + hauteur_boite * 0.80),
        ]
        couleurs = (QColor("#D14B41"), QColor("#D09C35"), QColor("#4AA35B"))
        etats = ("rouge", "orange", "vert")

        for centre, couleur, nom_etat in zip(centres, couleurs, etats):
            self._dessiner_casquette(painter, centre, rayon)
            self._dessiner_optique(
                painter,
                centre,
                rayon,
                couleur,
                etat == nom_etat,
            )

        painter.restore()


# 5 -- Horloge# 5 -- Horloge ----------------------------------------------------------------


class HorlogeGare:
    """Petite horloge ancienne de quai."""

    def __init__(
        self,
        couleur_cadre: QColor | str = "#514A43",
        couleur_fond: QColor | str = "#F6F1E7",
        couleur_trait: QColor | str = "#2C2A28",
    ):
        self.couleur_cadre = _qcolor(couleur_cadre)
        self.couleur_fond = _qcolor(couleur_fond)
        self.couleur_trait = _qcolor(couleur_trait)

    def peindre(
        self,
        painter: QPainter,
        centre: QPointF,
        rayon: float,
    ) -> None:
        """Dessine une horloge simple."""
        if rayon <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha("#000000", 35))
        painter.drawEllipse(
            QPointF(centre.x() + rayon * 0.06, centre.y() + rayon * 0.09),
            rayon,
            rayon,
        )

        grad = QRadialGradient(centre, rayon)
        grad.setColorAt(0.0, _eclaircir(self.couleur_fond, 0.12))
        grad.setColorAt(1.0, self.couleur_fond)

        pen = QPen(self.couleur_cadre)
        pen.setWidthF(max(1.0, rayon * 0.12))
        painter.setPen(pen)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(centre, rayon, rayon)

        # Graduations principales
        painter.translate(centre)
        painter.setPen(QPen(self.couleur_trait, max(1.0, rayon * 0.06)))

        for i in range(12):
            painter.save()
            painter.rotate(i * 30)
            painter.drawLine(
                QPointF(0, -rayon * 0.76),
                QPointF(0, -rayon * 0.90),
            )
            painter.restore()

        # Aiguilles : 10h10, visuellement sympa
        painter.setPen(
            QPen(
                self.couleur_trait, max(1.0, rayon * 0.08), cap=Qt.PenCapStyle.RoundCap
            )
        )
        painter.save()
        painter.rotate(300)  # heure
        painter.drawLine(QPointF(0, 0), QPointF(0, -rayon * 0.40))
        painter.restore()

        painter.setPen(
            QPen(
                self.couleur_trait, max(1.0, rayon * 0.05), cap=Qt.PenCapStyle.RoundCap
            )
        )
        painter.save()
        painter.rotate(60)  # minutes
        painter.drawLine(QPointF(0, 0), QPointF(0, -rayon * 0.62))
        painter.restore()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.couleur_trait)
        painter.drawEllipse(QPointF(0, 0), rayon * 0.10, rayon * 0.10)

        painter.restore()


# 6 -- Gare ancienne -----------------------------------------------------------


class GareAncienne:
    """
    Gare intérieure ancienne pleine hauteur.

    Logique visuelle
    ----------------
    On se situe à l'intérieur d'une gare ancienne :
        - verrière / marquise haute ;
        - piliers métalliques ;
        - mur de fond et quai ;
        - entrée de gare à gauche ;
        - sortie de gare à droite ;
        - feu ferroviaire à droite.

    La gare masque le paysage : elle sert donc de transition entre deux décors.
    """

    masque_paysage = True
    masque_rails = True

    def __init__(
        self,
        couleur_mur: QColor | str = "#D7C7AE",
        couleur_mur_bas: QColor | str = "#BCA98E",
        couleur_metal: QColor | str = "#647076",
        couleur_metal_fonce: QColor | str = "#495257",
        couleur_verre: QColor | str = "#CFE0E5",
        couleur_quai: QColor | str = "#A99A88",
        couleur_bord_quai: QColor | str = "#E8DECC",
        couleur_plancher: QColor | str = "#7F6E5D",
        lampes_allumees: bool = True,
        etat_feu: str = "rouge",
    ):
        self.couleur_mur = _qcolor(couleur_mur)
        self.couleur_mur_bas = _qcolor(couleur_mur_bas)
        self.couleur_metal = _qcolor(couleur_metal)
        self.couleur_metal_fonce = _qcolor(couleur_metal_fonce)
        self.couleur_verre = _qcolor(couleur_verre)
        self.couleur_quai = _qcolor(couleur_quai)
        self.couleur_bord_quai = _qcolor(couleur_bord_quai)
        self.couleur_plancher = _qcolor(couleur_plancher)

        self.lampes_allumees = lampes_allumees
        self.etat_feu = etat_feu

        self.panneau = PanneauGareAncienne()
        self.plaque = PlaqueProgressionAncienne()
        self.feu = FeuFerroviaire()
        self.horloge = HorlogeGare()

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    def largeur_recommandee(
        self,
        hauteur_scene: float,
    ) -> float:
        """Largeur idéale approximative."""
        return hauteur_scene * 3.20

    def _y_quai(
        self,
        rect: QRectF,
        y_rail: float | None,
    ) -> float:
        """Altitude du quai."""
        if y_rail is not None:
            return y_rail - rect.height() * 0.055
        return rect.top() + rect.height() * 0.69

    # --------------------------------------------------------------------------
    # Éléments de structure
    # --------------------------------------------------------------------------

    def _dessiner_fond_mural(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """Dessine le mur de fond, son soubassement et ses moulures."""
        h = rect.height()

        rect_mur = QRectF(
            rect.left(),
            rect.top(),
            rect.width(),
            y_quai - rect.top(),
        )

        gradient_mur = QLinearGradient(
            rect_mur.topLeft(),
            rect_mur.bottomLeft(),
        )
        gradient_mur.setColorAt(0.0, _eclaircir(self.couleur_mur, 0.14))
        gradient_mur.setColorAt(0.62, self.couleur_mur)
        gradient_mur.setColorAt(1.0, _assombrir(self.couleur_mur, 0.055))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient_mur))
        painter.drawRect(rect_mur)

        # Soubassement plus robuste et légèrement plus froid.
        hauteur_bas = h * 0.18
        rect_bas = QRectF(
            rect.left(),
            y_quai - hauteur_bas,
            rect.width(),
            hauteur_bas,
        )

        grad_bas = QLinearGradient(
            rect_bas.topLeft(),
            rect_bas.bottomLeft(),
        )
        grad_bas.setColorAt(0.0, _eclaircir(self.couleur_mur_bas, 0.10))
        grad_bas.setColorAt(0.45, self.couleur_mur_bas)
        grad_bas.setColorAt(1.0, _assombrir(self.couleur_mur_bas, 0.14))

        painter.setBrush(QBrush(grad_bas))
        painter.drawRect(rect_bas)

        # Corniche séparant le soubassement du mur : elle sert de ligne de
        # référence commune à toutes les portes et fenêtres.
        y_corniche = rect_bas.top()
        epaisseur = max(2.0, h * 0.009)

        painter.setBrush(_assombrir(self.couleur_mur_bas, 0.13))
        painter.drawRect(
            QRectF(rect.left(), y_corniche - epaisseur * 0.35, rect.width(), epaisseur)
        )
        painter.setBrush(_eclaircir(self.couleur_mur_bas, 0.18))
        painter.drawRect(
            QRectF(
                rect.left(),
                y_corniche - epaisseur * 0.45,
                rect.width(),
                epaisseur * 0.28,
            )
        )

        # Joints horizontaux très discrets : moins réguliers qu'avant pour
        # éviter l'effet "papier millimétré".
        pen_joint = QPen(_avec_alpha(_assombrir(self.couleur_mur, 0.22), 58))
        pen_joint.setWidthF(max(1.0, h * 0.0028))
        painter.setPen(pen_joint)

        for proportion in (0.31, 0.47, 0.61):
            y = rect.top() + h * proportion
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))

        # Quelques joints verticaux décalés donnent une vraie texture de pierre
        # sans charger tout le fond.
        pas = h * 0.34
        x = rect.left() + pas * 0.55
        y_1 = rect.top() + h * 0.31
        y_2 = y_corniche
        while x < rect.right():
            painter.drawLine(QPointF(x, y_1), QPointF(x, y_2))
            x += pas

    def _dessiner_ouverture_laterale(
        self,
        painter: QPainter,
        rect: QRectF,
        x_centre: float,
        y_quai: float,
        largeur: float,
        hauteur: float,
        cote: str,
    ) -> None:
        """Dessine l'ouverture par laquelle la rame entre ou quitte la halle.

        L'ouverture reste tangente au bord de la scène pour que le train puisse
        réellement y disparaître, mais la maçonnerie, l'arche intérieure et la
        perspective sont décalées vers l'intérieur de la gare.
        """
        h = rect.height()
        cote = cote.lower().strip()
        sens = 1.0 if cote == "entree" else -1.0

        x0 = x_centre - largeur / 2
        x1 = x_centre + largeur / 2
        y0 = y_quai - hauteur
        y_naissance = y0 + hauteur * 0.23

        def chemin_arche(decalage_x: float = 0.0, retrait: float = 0.0) -> QPainterPath:
            gauche = x0 + retrait + decalage_x
            droite = x1 - retrait + decalage_x
            haut = y0 + retrait * 0.35
            naissance = y_naissance + retrait * 0.20

            path = QPainterPath()
            path.moveTo(gauche, y_quai)
            path.lineTo(gauche, naissance)
            path.cubicTo(
                QPointF(gauche, haut),
                QPointF(droite, haut),
                QPointF(droite, naissance),
            )
            path.lineTo(droite, y_quai)
            path.closeSubpath()
            return path

        path = chemin_arche()

        # Ombre portée du grand encadrement.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha("#000000", 42))
        painter.drawPath(chemin_arche(decalage_x=sens * h * 0.010))

        # Profondeur intérieure : même ambiance des deux côtés, seule la
        # direction de la lumière change.
        if cote == "entree":
            c_exterieur = QColor(111, 128, 138)
            c_interieur = QColor(54, 61, 66)
        else:
            c_exterieur = QColor(183, 204, 210)
            c_interieur = QColor(67, 74, 79)

        gradient = QLinearGradient(
            QPointF(x0 if sens > 0 else x1, y0),
            QPointF(x1 if sens > 0 else x0, y_quai),
        )
        gradient.setColorAt(0.0, c_exterieur)
        gradient.setColorAt(0.52, _melanger(c_exterieur, c_interieur, 0.55))
        gradient.setColorAt(1.0, c_interieur)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

        # Gros bandeau de pierre/métal autour de l'ouverture.
        pen_cadre = QPen(_assombrir(self.couleur_mur_bas, 0.30))
        pen_cadre.setWidthF(max(3.0, h * 0.020))
        pen_cadre.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen_cadre)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Filet clair côté lumière.
        pen_lumiere = QPen(_avec_alpha(_eclaircir(self.couleur_mur_bas, 0.35), 155))
        pen_lumiere.setWidthF(max(1.0, h * 0.004))
        painter.setPen(pen_lumiere)
        painter.drawPath(chemin_arche(decalage_x=-sens * h * 0.006, retrait=h * 0.008))

        # Seconde arche en retrait : elle matérialise l'épaisseur de la halle.
        profondeur = sens * h * 0.030
        retrait = h * 0.018
        path_interieur = chemin_arche(decalage_x=profondeur, retrait=retrait)

        pen_inner = QPen(_avec_alpha(self.couleur_metal_fonce, 175))
        pen_inner.setWidthF(max(1.0, h * 0.006))
        painter.setPen(pen_inner)
        painter.drawPath(path_interieur)

        # Deux montants de structure à l'intérieur de la bouche. Leur léger
        # décalage donne une perspective sans faire croire à des portes.
        y_bas = y_quai - h * 0.010
        y_haut = y_naissance + hauteur * 0.04
        for p in (0.20, 0.80):
            x_ext = x0 + largeur * p
            x_int = x_ext + profondeur * 0.72
            painter.drawLine(QPointF(x_ext, y_bas), QPointF(x_int, y_haut))

        # Traverse haute discrète.
        painter.drawLine(
            QPointF(x0 + largeur * 0.18, y_naissance + hauteur * 0.035),
            QPointF(x1 - largeur * 0.18, y_naissance + hauteur * 0.035),
        )

    def _dessiner_baie_murale(
        self,
        painter: QPainter,
        rect_baie: QRectF,
        type_baie: str = "fenetre",
    ) -> None:
        """Dessine une fenêtre ou une porte ancienne avec la même grille."""
        if rect_baie.width() <= 0 or rect_baie.height() <= 0:
            return

        type_baie = type_baie.lower().strip()
        est_porte = type_baie == "porte"
        w = rect_baie.width()
        h = rect_baie.height()

        # Ombre d'encadrement.
        ombre = rect_baie.translated(w * 0.035, h * 0.025)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha("#000000", 28))
        painter.drawRoundedRect(ombre, w * 0.06, w * 0.06)

        # Cadre extérieur.
        cadre = QPen(_assombrir(self.couleur_mur_bas, 0.24))
        cadre.setWidthF(max(1.5, w * 0.075))
        painter.setPen(cadre)
        painter.setBrush(_assombrir(self.couleur_metal_fonce, 0.10))
        painter.drawRoundedRect(rect_baie, w * 0.055, w * 0.055)

        marge = w * 0.10
        vitrage = rect_baie.adjusted(marge, marge, -marge, -marge)

        grad = QLinearGradient(vitrage.topLeft(), vitrage.bottomRight())
        grad.setColorAt(0.0, _eclaircir(self.couleur_verre, 0.22))
        grad.setColorAt(0.50, self.couleur_verre)
        grad.setColorAt(1.0, _assombrir(self.couleur_verre, 0.18))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(vitrage, w * 0.025, w * 0.025)

        pen_menuiserie = QPen(_assombrir(self.couleur_metal_fonce, 0.08))
        pen_menuiserie.setWidthF(max(1.0, w * 0.040))
        painter.setPen(pen_menuiserie)

        # Toutes les baies partagent le même axe vertical.
        painter.drawLine(
            QPointF(vitrage.center().x(), vitrage.top()),
            QPointF(vitrage.center().x(), vitrage.bottom()),
        )

        if est_porte:
            # Imposte vitrée et deux vantaux bien alignés.
            y_imposte = vitrage.top() + vitrage.height() * 0.24
            painter.drawLine(
                QPointF(vitrage.left(), y_imposte),
                QPointF(vitrage.right(), y_imposte),
            )

            # Panneaux bas plus opaques.
            y_panneau = vitrage.top() + vitrage.height() * 0.67
            painter.drawLine(
                QPointF(vitrage.left(), y_panneau),
                QPointF(vitrage.right(), y_panneau),
            )
            painter.setBrush(
                _avec_alpha(_assombrir(self.couleur_metal_fonce, 0.02), 78)
            )
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(
                QRectF(
                    vitrage.left(),
                    y_panneau,
                    vitrage.width(),
                    vitrage.bottom() - y_panneau,
                )
            )

            # Poignées symétriques.
            painter.setBrush(_eclaircir(self.couleur_metal_fonce, 0.30))
            r = max(1.1, w * 0.025)
            cy = vitrage.top() + vitrage.height() * 0.58
            painter.drawEllipse(QPointF(vitrage.center().x() - w * 0.065, cy), r, r)
            painter.drawEllipse(QPointF(vitrage.center().x() + w * 0.065, cy), r, r)
        else:
            # Deux traverses donnent six petits carreaux réguliers.
            for p in (0.34, 0.68):
                y = vitrage.top() + vitrage.height() * p
                painter.drawLine(
                    QPointF(vitrage.left(), y),
                    QPointF(vitrage.right(), y),
                )

            # Appui de fenêtre saillant.
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(_assombrir(self.couleur_mur_bas, 0.08))
            painter.drawRoundedRect(
                QRectF(
                    rect_baie.left() - w * 0.06,
                    rect_baie.bottom() - h * 0.015,
                    rect_baie.width() + w * 0.12,
                    h * 0.055,
                ),
                h * 0.012,
                h * 0.012,
            )

        # Reflet diagonal léger, identique sur toutes les vitres.
        painter.setPen(QPen(_avec_alpha("#FFFFFF", 55), max(1.0, w * 0.018)))
        painter.drawLine(
            QPointF(
                vitrage.left() + vitrage.width() * 0.15,
                vitrage.top() + vitrage.height() * 0.08,
            ),
            QPointF(
                vitrage.left() + vitrage.width() * 0.45,
                vitrage.bottom() - vitrage.height() * 0.08,
            ),
        )

    def _dessiner_piliers(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """Dessine des piliers métalliques sur une grille symétrique."""
        h = rect.height()

        positions = (
            rect.left() + rect.width() * 0.17,
            rect.left() + rect.width() * 0.39,
            rect.left() + rect.width() * 0.61,
            rect.left() + rect.width() * 0.83,
        )

        largeur = h * 0.055
        y_top = rect.top() + h * 0.105

        for x in positions:
            rect_pilier = QRectF(
                x - largeur / 2,
                y_top,
                largeur,
                y_quai - y_top,
            )

            # Ombre portée vers la droite.
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(_avec_alpha("#000000", 28))
            painter.drawRoundedRect(
                rect_pilier.translated(h * 0.007, h * 0.004),
                largeur * 0.16,
                largeur * 0.16,
            )

            grad = QLinearGradient(
                QPointF(rect_pilier.left(), 0),
                QPointF(rect_pilier.right(), 0),
            )
            grad.setColorAt(0.0, _assombrir(self.couleur_metal, 0.28))
            grad.setColorAt(0.22, self.couleur_metal)
            grad.setColorAt(0.52, _eclaircir(self.couleur_metal, 0.14))
            grad.setColorAt(1.0, _assombrir(self.couleur_metal, 0.24))

            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(
                rect_pilier,
                largeur * 0.16,
                largeur * 0.16,
            )

            # Nervure centrale.
            painter.setBrush(_avec_alpha(_eclaircir(self.couleur_metal, 0.30), 95))
            painter.drawRect(
                QRectF(
                    x - largeur * 0.055,
                    rect_pilier.top() + h * 0.040,
                    largeur * 0.11,
                    rect_pilier.height() - h * 0.075,
                )
            )

            # Chapiteau.
            rect_tete = QRectF(
                rect_pilier.left() - largeur * 0.34,
                rect_pilier.top(),
                rect_pilier.width() + largeur * 0.68,
                h * 0.038,
            )
            painter.setBrush(_assombrir(self.couleur_metal, 0.10))
            painter.drawRoundedRect(
                rect_tete,
                rect_tete.height() * 0.18,
                rect_tete.height() * 0.18,
            )

            # Pied boulonné, aligné exactement sur le quai.
            rect_pied = QRectF(
                x - largeur * 0.80,
                y_quai - h * 0.028,
                largeur * 1.60,
                h * 0.028,
            )
            painter.setBrush(_assombrir(self.couleur_metal, 0.16))
            painter.drawRoundedRect(
                rect_pied,
                rect_pied.height() * 0.20,
                rect_pied.height() * 0.20,
            )

            painter.setBrush(_eclaircir(self.couleur_metal, 0.28))
            r = max(1.0, h * 0.004)
            for dx in (-largeur * 0.46, largeur * 0.46):
                painter.drawEllipse(QPointF(x + dx, y_quai - h * 0.014), r, r)

    def _dessiner_verriere(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """Dessine une vraie verrière cintrée avec charpente et contreventements."""
        h = rect.height()

        rect_verriere = QRectF(
            rect.left() + rect.width() * 0.075,
            rect.top() + h * 0.020,
            rect.width() * 0.85,
            max(h * 0.18, y_quai - rect.top() - h * 0.45),
        )

        y_naissance = rect_verriere.top() + rect_verriere.height() * 0.24
        y_controle = rect_verriere.top() - rect_verriere.height() * 0.10

        path_verriere = QPainterPath()
        path_verriere.moveTo(rect_verriere.left(), rect_verriere.bottom())
        path_verriere.lineTo(rect_verriere.left(), y_naissance)
        path_verriere.quadTo(
            QPointF(rect_verriere.center().x(), y_controle),
            QPointF(rect_verriere.right(), y_naissance),
        )
        path_verriere.lineTo(rect_verriere.right(), rect_verriere.bottom())
        path_verriere.closeSubpath()

        grad_verre = QLinearGradient(
            rect_verriere.topLeft(),
            rect_verriere.bottomLeft(),
        )
        grad_verre.setColorAt(0.0, _eclaircir(self.couleur_verre, 0.34))
        grad_verre.setColorAt(0.55, self.couleur_verre)
        grad_verre.setColorAt(1.0, _assombrir(self.couleur_verre, 0.07))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_verre))
        painter.drawPath(path_verriere)

        # Tout ce qui suit est découpé proprement par la forme de la verrière.
        painter.save()
        painter.setClipPath(path_verriere)

        pen_fin = QPen(_avec_alpha(self.couleur_metal_fonce, 195))
        pen_fin.setWidthF(max(1.0, h * 0.0055))
        painter.setPen(pen_fin)

        n_travees = 8
        xs = []
        for i in range(n_travees + 1):
            t = i / n_travees
            x = rect_verriere.left() + rect_verriere.width() * t
            y_courbe = (
                (1 - t) ** 2 * y_naissance
                + 2 * (1 - t) * t * y_controle
                + t**2 * y_naissance
            )
            xs.append((x, y_courbe))
            painter.drawLine(QPointF(x, y_courbe), QPointF(x, rect_verriere.bottom()))

        # Traverses horizontales.
        for proportion in (0.38, 0.66, 0.86):
            y = rect_verriere.top() + rect_verriere.height() * proportion
            painter.drawLine(
                QPointF(rect_verriere.left(), y),
                QPointF(rect_verriere.right(), y),
            )

        # Contreventements en X dans une travée sur deux.
        pen_x = QPen(_avec_alpha(self.couleur_metal_fonce, 120))
        pen_x.setWidthF(max(1.0, h * 0.0035))
        painter.setPen(pen_x)
        y_x_haut = rect_verriere.top() + rect_verriere.height() * 0.43
        y_x_bas = rect_verriere.top() + rect_verriere.height() * 0.82

        for i in range(0, n_travees, 2):
            xg = xs[i][0]
            xd = xs[i + 1][0]
            painter.drawLine(QPointF(xg, y_x_haut), QPointF(xd, y_x_bas))
            painter.drawLine(QPointF(xd, y_x_haut), QPointF(xg, y_x_bas))

        # Reflets verticaux, beaucoup plus discrets que les anciens grands traits.
        painter.setPen(QPen(_avec_alpha("#FFFFFF", 42), max(1.0, h * 0.003)))
        for p in (0.15, 0.46, 0.72):
            x = rect_verriere.left() + rect_verriere.width() * p
            painter.drawLine(
                QPointF(x, rect_verriere.top() + rect_verriere.height() * 0.18),
                QPointF(x - h * 0.035, rect_verriere.bottom()),
            )

        painter.restore()

        # Grosses poutres de rive : elles donnent enfin une vraie limite au toit.
        pen_rive = QPen(_assombrir(self.couleur_metal_fonce, 0.10))
        pen_rive.setWidthF(max(2.0, h * 0.010))
        painter.setPen(pen_rive)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path_verriere)

    def _dessiner_lampes_suspendues(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """Dessine trois lampes suspendues alignées sur les travées."""
        h = rect.height()
        y_support = rect.top() + h * 0.185
        y_lampe = rect.top() + h * 0.285

        positions = (
            rect.left() + rect.width() * 0.28,
            rect.left() + rect.width() * 0.50,
            rect.left() + rect.width() * 0.72,
        )

        for x in positions:
            pen = QPen(self.couleur_metal_fonce)
            pen.setWidthF(max(1.0, h * 0.0045))
            painter.setPen(pen)
            painter.drawLine(QPointF(x, y_support), QPointF(x, y_lampe))

            # Petite rosace d'accroche.
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(_assombrir(self.couleur_metal_fonce, 0.06))
            painter.drawEllipse(QPointF(x, y_support), h * 0.010, h * 0.006)

            if self.lampes_allumees:
                halo = QRadialGradient(QPointF(x, y_lampe + h * 0.020), h * 0.095)
                halo.setColorAt(0.0, QColor(255, 229, 163, 84))
                halo.setColorAt(0.44, QColor(255, 219, 145, 26))
                halo.setColorAt(1.0, QColor(255, 214, 130, 0))
                painter.setBrush(QBrush(halo))
                painter.drawEllipse(
                    QPointF(x, y_lampe + h * 0.020),
                    h * 0.095,
                    h * 0.095,
                )

            largeur = h * 0.060
            hauteur = h * 0.034
            path = QPainterPath()
            path.moveTo(x - largeur / 2, y_lampe)
            path.lineTo(x + largeur / 2, y_lampe)
            path.lineTo(x + largeur * 0.30, y_lampe + hauteur)
            path.lineTo(x - largeur * 0.30, y_lampe + hauteur)
            path.closeSubpath()

            painter.setBrush(_assombrir(self.couleur_metal, 0.07))
            painter.drawPath(path)

            # Liseré inférieur de l'abat-jour.
            painter.setPen(
                QPen(_eclaircir(self.couleur_metal, 0.12), max(1.0, h * 0.0025))
            )
            painter.drawLine(
                QPointF(x - largeur * 0.30, y_lampe + hauteur),
                QPointF(x + largeur * 0.30, y_lampe + hauteur),
            )

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(
                QColor("#F6DDA2") if self.lampes_allumees else QColor("#B3AEA3")
            )
            painter.drawEllipse(
                QPointF(x, y_lampe + hauteur * 0.72),
                h * 0.0115,
                h * 0.0115,
            )

    def _dessiner_banc(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine un petit banc de quai."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Assise
        grad_assise = QLinearGradient(
            rect.topLeft(),
            rect.bottomLeft(),
        )
        grad_assise.setColorAt(0.0, QColor("#936C4A"))
        grad_assise.setColorAt(1.0, QColor("#6F513A"))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_assise))

        rect_assise = QRectF(
            rect.left(),
            rect.top() + rect.height() * 0.42,
            rect.width(),
            rect.height() * 0.18,
        )
        painter.drawRoundedRect(
            rect_assise,
            rect_assise.height() * 0.20,
            rect_assise.height() * 0.20,
        )

        # Dossier
        rect_dossier = QRectF(
            rect.left() + rect.width() * 0.08,
            rect.top() + rect.height() * 0.10,
            rect.width() * 0.84,
            rect.height() * 0.18,
        )
        painter.drawRoundedRect(
            rect_dossier,
            rect_dossier.height() * 0.20,
            rect_dossier.height() * 0.20,
        )

        # Pieds métalliques
        pen = QPen(QColor("#4D5357"))
        pen.setWidthF(max(1.0, rect.width() * 0.05))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        for x in (
            rect.left() + rect.width() * 0.20,
            rect.right() - rect.width() * 0.20,
        ):
            painter.drawLine(
                QPointF(x, rect_assise.bottom()),
                QPointF(x, rect.bottom()),
            )

        painter.restore()

    def _dessiner_quai(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """Dessine le quai intérieur."""
        rect_quai = QRectF(
            rect.left(),
            y_quai,
            rect.width(),
            rect.height() * 0.15,
        )

        grad_quai = QLinearGradient(
            rect_quai.topLeft(),
            rect_quai.bottomLeft(),
        )
        grad_quai.setColorAt(0.0, _eclaircir(self.couleur_quai, 0.08))
        grad_quai.setColorAt(1.0, _assombrir(self.couleur_quai, 0.14))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_quai))
        painter.drawRect(rect_quai)

        # Bande claire de bord de quai
        rect_bord = QRectF(
            rect_quai.left(),
            rect_quai.top(),
            rect_quai.width(),
            max(3.0, rect.height() * 0.018),
        )

        painter.setBrush(self.couleur_bord_quai)
        painter.drawRect(rect_bord)

        # Lignes de dalles
        pen = QPen(_avec_alpha(_assombrir(self.couleur_quai, 0.25), 90))
        pen.setWidthF(max(1.0, rect.height() * 0.0035))
        painter.setPen(pen)

        largeur_dalle = rect.width() * 0.12
        x = rect.left()
        while x < rect.right():
            painter.drawLine(
                QPointF(x, rect_quai.top()),
                QPointF(x, rect_quai.bottom()),
            )
            x += largeur_dalle

    def _dessiner_sol_avant(
        self,
        painter: QPainter,
        rect: QRectF,
        y_rail: float,
    ) -> None:
        """Dessine le sol avant du hall, sous les rails."""
        rect_sol = QRectF(
            rect.left(),
            y_rail + rect.height() * 0.09,
            rect.width(),
            rect.bottom() - (y_rail + rect.height() * 0.09),
        )

        if rect_sol.height() <= 0:
            return

        grad = QLinearGradient(
            rect_sol.topLeft(),
            rect_sol.bottomLeft(),
        )
        grad.setColorAt(0.0, _eclaircir(self.couleur_plancher, 0.08))
        grad.setColorAt(1.0, _assombrir(self.couleur_plancher, 0.14))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(rect_sol)

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
        """Dessine la gare derrière le train sur une grille architecturale commune."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        w = rect.width()
        y_quai = self._y_quai(rect, y_rail)

        # ------------------------------------------------------------------
        # Fond et grandes ouvertures latérales
        # ------------------------------------------------------------------

        self._dessiner_fond_mural(painter, rect, y_quai)

        # Les ouvertures restent tangentes aux bords pour que le train puisse
        # entrer et sortir sans traverser visuellement un mur.
        largeur_ouverture = w * 0.155
        hauteur_ouverture = h * 0.545

        self._dessiner_ouverture_laterale(
            painter=painter,
            rect=rect,
            x_centre=rect.left() + largeur_ouverture / 2,
            y_quai=y_quai,
            largeur=largeur_ouverture,
            hauteur=hauteur_ouverture,
            cote="entree",
        )

        self._dessiner_ouverture_laterale(
            painter=painter,
            rect=rect,
            x_centre=rect.right() - largeur_ouverture / 2,
            y_quai=y_quai,
            largeur=largeur_ouverture,
            hauteur=hauteur_ouverture,
            cote="sortie",
        )

        # ------------------------------------------------------------------
        # Baies du mur de fond
        # ------------------------------------------------------------------
        # Même ligne basse, mêmes proportions de menuiserie : les fenêtres et
        # la porte semblent enfin appartenir au même bâtiment.

        largeur_fenetre = h * 0.18
        hauteur_fenetre = h * 0.235
        bas_fenetre = y_quai - h * 0.195

        for proportion_x in (0.245, 0.695):
            rect_fenetre = QRectF(
                rect.left() + w * proportion_x - largeur_fenetre / 2,
                bas_fenetre - hauteur_fenetre,
                largeur_fenetre,
                hauteur_fenetre,
            )
            self._dessiner_baie_murale(
                painter,
                rect_fenetre,
                type_baie="fenetre",
            )

        largeur_porte = h * 0.19
        hauteur_porte = h * 0.315
        rect_porte = QRectF(
            rect.left() + w * 0.555 - largeur_porte / 2,
            y_quai - hauteur_porte,
            largeur_porte,
            hauteur_porte,
        )
        self._dessiner_baie_murale(
            painter,
            rect_porte,
            type_baie="porte",
        )

        # ------------------------------------------------------------------
        # Verrière, charpente et piliers
        # ------------------------------------------------------------------

        self._dessiner_verriere(painter, rect, y_quai)
        self._dessiner_piliers(painter, rect, y_quai)
        self._dessiner_lampes_suspendues(painter, rect, y_quai)

        # ------------------------------------------------------------------
        # Horloge
        # ------------------------------------------------------------------

        self.horloge.peindre(
            painter,
            centre=QPointF(rect.center().x(), rect.top() + h * 0.185),
            rayon=h * 0.058,
        )

        # ------------------------------------------------------------------
        # Panneau de gare et progression
        # ------------------------------------------------------------------

        rect_panneau = QRectF(
            rect.left() + w * 0.305,
            y_quai - h * 0.285,
            w * 0.195,
            h * 0.245,
        )
        self.panneau.peindre(painter, rect_panneau, nom_pays)

        if i is not None and n is not None:
            rect_plaque = QRectF(
                rect_panneau.right() + h * 0.018,
                y_quai - h * 0.245,
                h * 0.105,
                h * 0.205,
            )
            self.plaque.peindre(painter, rect_plaque, i, n)

        # ------------------------------------------------------------------
        # Banc
        # ------------------------------------------------------------------

        rect_banc = QRectF(
            rect.left() + w * 0.605,
            y_quai - h * 0.108,
            h * 0.34,
            h * 0.103,
        )
        self._dessiner_banc(painter, rect_banc)

        # ------------------------------------------------------------------
        # Feu de sortie
        # ------------------------------------------------------------------
        # Il est maintenant placé dans une vraie travée, entre le banc et la
        # bouche de sortie, plutôt que calculé depuis le bord droit.

        largeur_feu = h * 0.18
        hauteur_feu = h * 0.30
        x_feu = rect.left() + w * 0.770

        rect_feu = QRectF(
            x_feu - largeur_feu / 2,
            y_quai - hauteur_feu,
            largeur_feu,
            hauteur_feu,
        )
        self.feu.peindre(painter, rect_feu, etat=self.etat_feu)

        painter.restore()

    # --------------------------------------------------------------------------
    # Bloc de devant
    # --------------------------------------------------------------------------

    def _dessiner_bloc_bas_avant(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """
        Dessine toute la partie basse de la gare devant le train.

        Ce bloc masque :
            - les rails ;
            - les traverses ;
            - les roues du train.

        Le train donne ainsi l'impression d'être encaissé derrière le quai.
        """

        h = rect.height()

        # ----------------------------------------------------------------------
        # Masse principale
        # ----------------------------------------------------------------------

        rect_bas = QRectF(
            rect.left(),
            y_quai,
            rect.width(),
            rect.bottom() - y_quai,
        )

        gradient = QLinearGradient(
            rect_bas.topLeft(),
            rect_bas.bottomLeft(),
        )

        gradient.setColorAt(
            0.0,
            _eclaircir(
                self.couleur_quai,
                0.08,
            ),
        )

        gradient.setColorAt(
            0.18,
            self.couleur_quai,
        )

        gradient.setColorAt(
            1.0,
            _assombrir(
                self.couleur_plancher,
                0.15,
            ),
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient))

        painter.drawRect(rect_bas)

        # ----------------------------------------------------------------------
        # Bord clair du quai
        # ----------------------------------------------------------------------

        hauteur_bord = max(
            4.0,
            h * 0.020,
        )

        rect_bord = QRectF(
            rect.left(),
            y_quai,
            rect.width(),
            hauteur_bord,
        )

        painter.setBrush(self.couleur_bord_quai)

        painter.drawRect(rect_bord)

        # ----------------------------------------------------------------------
        # Ombre juste sous le bord du quai
        # ----------------------------------------------------------------------

        hauteur_ombre = h * 0.030

        ombre = QLinearGradient(
            QPointF(
                0,
                y_quai + hauteur_bord,
            ),
            QPointF(
                0,
                y_quai + hauteur_bord + hauteur_ombre,
            ),
        )

        ombre.setColorAt(
            0.0,
            QColor(
                0,
                0,
                0,
                65,
            ),
        )

        ombre.setColorAt(
            1.0,
            QColor(
                0,
                0,
                0,
                0,
            ),
        )

        painter.setBrush(QBrush(ombre))

        painter.drawRect(
            QRectF(
                rect.left(),
                y_quai + hauteur_bord,
                rect.width(),
                hauteur_ombre,
            )
        )

        # ----------------------------------------------------------------------
        # Dalles
        # ----------------------------------------------------------------------

        pen_dalles = QPen(
            _avec_alpha(
                _assombrir(
                    self.couleur_quai,
                    0.30,
                ),
                80,
            )
        )

        pen_dalles.setWidthF(
            max(
                1.0,
                h * 0.003,
            )
        )

        painter.setPen(pen_dalles)

        largeur_dalle = rect.width() * 0.10

        x = rect.left()

        while x <= rect.right():

            painter.drawLine(
                QPointF(
                    x,
                    y_quai,
                ),
                QPointF(
                    x,
                    rect.bottom(),
                ),
            )

            x += largeur_dalle

        # Quelques lignes horizontales discrètes
        for proportion in (
            0.34,
            0.67,
        ):

            y = y_quai + rect_bas.height() * proportion

            painter.drawLine(
                QPointF(
                    rect.left(),
                    y,
                ),
                QPointF(
                    rect.right(),
                    y,
                ),
            )

    # --------------------------------------------------------------------------
    # Dessin avant
    # --------------------------------------------------------------------------

    def peindre_avant(
        self, painter: QPainter, rect: QRectF, y_rail: float | None = None, **kwargs
    ) -> None:
        """
        Dessine les éléments situés devant le train.

        Dans une gare ancienne, toute la partie basse du quai passe devant
        la rame afin de masquer les rails et les roues.
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

        # ------------------------------------------------------------------
        # Bloc bas devant le train
        # ------------------------------------------------------------------

        self._dessiner_bloc_bas_avant(
            painter,
            rect,
            y_quai,
        )

        # ------------------------------------------------------------------
        # Piliers très proches
        # ------------------------------------------------------------------

        h = rect.height()

        largeur = rect.width() * 0.020

        for x in (
            rect.left() + rect.width() * 0.02,
            rect.right() - rect.width() * 0.02 - largeur,
        ):

            rect_pilier = QRectF(
                x,
                rect.top(),
                largeur,
                y_quai - rect.top(),
            )

            gradient = QLinearGradient(
                rect_pilier.left(),
                0,
                rect_pilier.right(),
                0,
            )

            gradient.setColorAt(
                0.0,
                _assombrir(
                    self.couleur_metal_fonce,
                    0.28,
                ),
            )

            gradient.setColorAt(
                0.45,
                _eclaircir(
                    self.couleur_metal_fonce,
                    0.06,
                ),
            )

            gradient.setColorAt(
                1.0,
                _assombrir(
                    self.couleur_metal_fonce,
                    0.20,
                ),
            )

            painter.setPen(Qt.PenStyle.NoPen)

            painter.setBrush(QBrush(gradient))

            painter.drawRect(rect_pilier)

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
        """Dessine la gare complète."""
        self.peindre_arriere(
            painter=painter,
            rect=rect,
            nom_pays=nom_pays,
            i=i,
            n=n,
            y_rail=y_rail,
        )

        self.peindre_avant(
            painter=painter,
            rect=rect,
            i=i,
            n=n,
            y_rail=y_rail,
            **kwargs,
        )
