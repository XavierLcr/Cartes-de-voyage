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
    """
    Petit feu ferroviaire ancien.

    `etat` peut valoir :
        - "rouge"
        - "vert"
        - "orange"
    """

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
        """Dessine un feu simple."""
        painter.save()

        if allume:
            halo = QRadialGradient(centre, rayon * 2.8)
            halo.setColorAt(0.0, _avec_alpha(couleur, 110))
            halo.setColorAt(0.35, _avec_alpha(couleur, 50))
            halo.setColorAt(1.0, _avec_alpha(couleur, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(centre, rayon * 2.8, rayon * 2.8)

        grad = QRadialGradient(centre, rayon)
        grad.setColorAt(0.0, _eclaircir(couleur, 0.30 if allume else 0.10))
        grad.setColorAt(0.65, couleur if allume else _assombrir(couleur, 0.40))
        grad.setColorAt(1.0, _assombrir(couleur, 0.45))

        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centre, rayon, rayon)

        # Reflet
        painter.setBrush(_avec_alpha("#FFFFFF", 45 if allume else 25))
        painter.drawEllipse(
            QPointF(
                centre.x() - rayon * 0.22,
                centre.y() - rayon * 0.26,
            ),
            rayon * 0.28,
            rayon * 0.18,
        )

        painter.restore()

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        etat: str = "rouge",
    ) -> None:
        """Dessine le feu complet."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        etat = etat.lower().strip()
        if etat not in {"rouge", "vert", "orange"}:
            etat = "rouge"

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Mât
        largeur_mat = max(2.5, rect.width() * 0.07)
        gradient_mat = QLinearGradient(
            rect.left(),
            0,
            rect.left() + largeur_mat,
            0,
        )
        gradient_mat.setColorAt(0.0, _assombrir(self.couleur_support, 0.25))
        gradient_mat.setColorAt(0.45, _eclaircir(self.couleur_support, 0.15))
        gradient_mat.setColorAt(1.0, _assombrir(self.couleur_support, 0.20))

        rect_mat = QRectF(
            rect.center().x() - largeur_mat / 2,
            rect.top() + rect.height() * 0.18,
            largeur_mat,
            rect.height() * 0.82,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient_mat))
        painter.drawRoundedRect(
            rect_mat,
            largeur_mat * 0.45,
            largeur_mat * 0.45,
        )

        # Coffret
        rect_boite = QRectF(
            rect.left() + rect.width() * 0.18,
            rect.top(),
            rect.width() * 0.64,
            rect.height() * 0.32,
        )

        gradient_boite = QLinearGradient(
            rect_boite.topLeft(),
            rect_boite.bottomLeft(),
        )
        gradient_boite.setColorAt(0.0, _eclaircir(self.couleur_metal, 0.10))
        gradient_boite.setColorAt(1.0, _assombrir(self.couleur_metal, 0.12))

        painter.setPen(
            QPen(_assombrir(self.couleur_metal, 0.35), max(1.0, rect.width() * 0.03))
        )
        painter.setBrush(QBrush(gradient_boite))
        painter.drawRoundedRect(
            rect_boite,
            rect_boite.width() * 0.16,
            rect_boite.width() * 0.16,
        )

        # Trois optiques
        cx = rect_boite.center().x()
        r = rect_boite.height() * 0.12

        centres = [
            QPointF(cx, rect_boite.top() + rect_boite.height() * 0.22),
            QPointF(cx, rect_boite.top() + rect_boite.height() * 0.50),
            QPointF(cx, rect_boite.top() + rect_boite.height() * 0.78),
        ]

        self._dessiner_optique(
            painter,
            centres[0],
            r,
            QColor("#D14B41"),
            etat == "rouge",
        )
        self._dessiner_optique(
            painter,
            centres[1],
            r,
            QColor("#D09C35"),
            etat == "orange",
        )
        self._dessiner_optique(
            painter,
            centres[2],
            r,
            QColor("#4AA35B"),
            etat == "vert",
        )

        painter.restore()


# 5 -- Horloge ----------------------------------------------------------------


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
        """Mur de fond et soubassement."""
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
        gradient_mur.setColorAt(0.0, _eclaircir(self.couleur_mur, 0.12))
        gradient_mur.setColorAt(0.65, self.couleur_mur)
        gradient_mur.setColorAt(1.0, _assombrir(self.couleur_mur, 0.05))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient_mur))
        painter.drawRect(rect_mur)

        # Soubassement
        rect_bas = QRectF(
            rect.left(),
            y_quai - rect.height() * 0.18,
            rect.width(),
            rect.height() * 0.18,
        )

        grad_bas = QLinearGradient(
            rect_bas.topLeft(),
            rect_bas.bottomLeft(),
        )
        grad_bas.setColorAt(0.0, _eclaircir(self.couleur_mur_bas, 0.08))
        grad_bas.setColorAt(1.0, _assombrir(self.couleur_mur_bas, 0.12))

        painter.setBrush(QBrush(grad_bas))
        painter.drawRect(rect_bas)

        # Quelques joints / lignes décoratives
        pen = QPen(_avec_alpha(_assombrir(self.couleur_mur, 0.22), 85))
        pen.setWidthF(max(1.0, rect.height() * 0.004))
        painter.setPen(pen)

        for k in (0.18, 0.33, 0.48):
            y = rect.top() + rect.height() * k
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))

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
        """Dessine une grande ouverture en arche."""
        x0 = x_centre - largeur / 2
        y0 = y_quai - hauteur

        path = QPainterPath()
        path.moveTo(x0, y_quai)
        path.lineTo(x0, y0 + hauteur * 0.28)
        path.quadTo(
            QPointF(x0 + largeur / 2, y0 - hauteur * 0.12),
            QPointF(x0 + largeur, y0 + hauteur * 0.28),
        )
        path.lineTo(x0 + largeur, y_quai)
        path.closeSubpath()

        # Intérieur sombre / lumineux
        if cote == "entree":
            c1 = QColor(58, 64, 71)
            c2 = QColor(105, 114, 122)
        else:
            c1 = QColor(223, 233, 235)
            c2 = QColor(176, 196, 201)

        gradient = QLinearGradient(
            QPointF(x0, y0),
            QPointF(x0 + largeur, y_quai),
        )
        gradient.setColorAt(0.0, c2)
        gradient.setColorAt(1.0, c1)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

        # Cadre d'arche
        pen = QPen(self.couleur_metal_fonce)
        pen.setWidthF(max(2.0, rect.height() * 0.009))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Petite perspective / profondeur
        decalage = rect.width() * 0.018 if cote == "entree" else -rect.width() * 0.018

        path_interieur = QPainterPath()
        path_interieur.moveTo(x0 + decalage, y_quai)
        path_interieur.lineTo(x0 + decalage, y0 + hauteur * 0.32)
        path_interieur.quadTo(
            QPointF(x0 + largeur / 2 + decalage, y0 - hauteur * 0.03),
            QPointF(x0 + largeur + decalage, y0 + hauteur * 0.32),
        )
        path_interieur.lineTo(x0 + largeur + decalage, y_quai)

        pen_inner = QPen(_avec_alpha(self.couleur_metal_fonce, 120))
        pen_inner.setWidthF(max(1.0, rect.height() * 0.004))
        painter.setPen(pen_inner)
        painter.drawPath(path_interieur)

    def _dessiner_piliers(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """Dessine les montants principaux de la gare."""
        h = rect.height()

        positions = (
            rect.left() + rect.width() * 0.18,
            rect.left() + rect.width() * 0.38,
            rect.left() + rect.width() * 0.60,
            rect.left() + rect.width() * 0.80,
        )

        for x in positions:
            largeur = rect.width() * 0.028

            rect_pilier = QRectF(
                x - largeur / 2,
                rect.top() + h * 0.10,
                largeur,
                y_quai - rect.top() - h * 0.10,
            )

            grad = QLinearGradient(
                rect_pilier.left(),
                0,
                rect_pilier.right(),
                0,
            )
            grad.setColorAt(0.0, _assombrir(self.couleur_metal, 0.24))
            grad.setColorAt(0.50, _eclaircir(self.couleur_metal, 0.10))
            grad.setColorAt(1.0, _assombrir(self.couleur_metal, 0.22))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(
                rect_pilier,
                largeur * 0.20,
                largeur * 0.20,
            )

            # Chapiteau / renfort supérieur
            rect_tete = QRectF(
                rect_pilier.left() - largeur * 0.28,
                rect_pilier.top(),
                rect_pilier.width() + largeur * 0.56,
                h * 0.040,
            )

            painter.setBrush(_assombrir(self.couleur_metal, 0.08))
            painter.drawRoundedRect(
                rect_tete,
                rect_tete.height() * 0.22,
                rect_tete.height() * 0.22,
            )

    def _dessiner_verriere(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """Dessine la marquise / verrière intérieure."""
        h = rect.height()

        rect_verriere = QRectF(
            rect.left() + rect.width() * 0.08,
            rect.top() + h * 0.02,
            rect.width() * 0.84,
            y_quai - rect.top() - h * 0.46,
        )

        # Fond vitré
        grad_verre = QLinearGradient(
            rect_verriere.topLeft(),
            rect_verriere.bottomLeft(),
        )
        grad_verre.setColorAt(0.0, _eclaircir(self.couleur_verre, 0.28))
        grad_verre.setColorAt(1.0, _assombrir(self.couleur_verre, 0.04))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_verre))
        painter.drawRoundedRect(
            rect_verriere,
            rect_verriere.height() * 0.10,
            rect_verriere.height() * 0.10,
        )

        # Charpente
        pen = QPen(_avec_alpha(self.couleur_metal_fonce, 190))
        pen.setWidthF(max(1.0, rect.height() * 0.006))
        painter.setPen(pen)

        # Arcs principaux
        n_arcs = 5
        for i in range(n_arcs):
            x = rect_verriere.left() + rect_verriere.width() * i / (n_arcs - 1)

            path = QPainterPath()
            path.moveTo(x, rect_verriere.bottom())
            path.quadTo(
                QPointF(x, rect_verriere.top() + rect_verriere.height() * 0.15),
                QPointF(x, rect_verriere.top()),
            )
            painter.drawPath(path)

        # Traverses horizontales
        for p in (0.18, 0.42, 0.66, 0.86):
            y = rect_verriere.top() + rect_verriere.height() * p
            painter.drawLine(
                QPointF(rect_verriere.left(), y),
                QPointF(rect_verriere.right(), y),
            )

        # Reflets
        painter.setPen(
            QPen(_avec_alpha("#FFFFFF", 45), max(1.0, rect.height() * 0.004))
        )
        for p in (0.20, 0.48):
            painter.drawLine(
                QPointF(
                    rect_verriere.left() + rect_verriere.width() * p,
                    rect_verriere.top(),
                ),
                QPointF(
                    rect_verriere.left() + rect_verriere.width() * (p - 0.12),
                    rect_verriere.bottom(),
                ),
            )

    def _dessiner_lampes_suspendues(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """Dessine quelques lampes suspendues sous la verrière."""
        h = rect.height()

        y_support = rect.top() + h * 0.19

        positions = (
            rect.left() + rect.width() * 0.26,
            rect.left() + rect.width() * 0.50,
            rect.left() + rect.width() * 0.74,
        )

        for x in positions:
            # Tige
            pen = QPen(self.couleur_metal_fonce)
            pen.setWidthF(max(1.0, h * 0.005))
            painter.setPen(pen)

            y_lampe = y_support + h * 0.10
            painter.drawLine(
                QPointF(x, y_support),
                QPointF(x, y_lampe),
            )

            # Halo
            if self.lampes_allumees:
                halo = QRadialGradient(
                    QPointF(x, y_lampe + h * 0.010),
                    h * 0.10,
                )
                halo.setColorAt(0.0, QColor(255, 229, 163, 80))
                halo.setColorAt(0.45, QColor(255, 219, 145, 28))
                halo.setColorAt(1.0, QColor(255, 214, 130, 0))

                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(halo))
                painter.drawEllipse(
                    QPointF(x, y_lampe + h * 0.010),
                    h * 0.10,
                    h * 0.10,
                )

            # Abat-jour
            path = QPainterPath()
            largeur = h * 0.060
            hauteur = h * 0.032

            path.moveTo(x - largeur / 2, y_lampe)
            path.lineTo(x + largeur / 2, y_lampe)
            path.lineTo(x + largeur * 0.28, y_lampe + hauteur)
            path.lineTo(x - largeur * 0.28, y_lampe + hauteur)
            path.closeSubpath()

            painter.setBrush(_assombrir(self.couleur_metal, 0.05))
            painter.drawPath(path)

            # Ampoule
            painter.setBrush(
                QColor("#F6DDA2") if self.lampes_allumees else QColor("#B3AEA3")
            )
            painter.drawEllipse(
                QPointF(x, y_lampe + hauteur * 0.65),
                h * 0.012,
                h * 0.012,
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
        """
        Dessine la gare derrière le train.
        """
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        y_quai = self._y_quai(rect, y_rail)

        # ------------------------------------------------------------------
        # Fond
        # ------------------------------------------------------------------

        self._dessiner_fond_mural(
            painter,
            rect,
            y_quai,
        )

        # ------------------------------------------------------------------
        # Entrée et sortie
        # ------------------------------------------------------------------

        largeur_ouverture = rect.width() * 0.16
        hauteur_ouverture = h * 0.54

        self._dessiner_ouverture_laterale(
            painter=painter,
            rect=rect,
            x_centre=rect.left() + rect.width() * 0.08,
            y_quai=y_quai,
            largeur=largeur_ouverture,
            hauteur=hauteur_ouverture,
            cote="entree",
        )

        self._dessiner_ouverture_laterale(
            painter=painter,
            rect=rect,
            x_centre=rect.right() - rect.width() * 0.08,
            y_quai=y_quai,
            largeur=largeur_ouverture,
            hauteur=hauteur_ouverture,
            cote="sortie",
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
        # Horloge
        # ------------------------------------------------------------------

        self.horloge.peindre(
            painter,
            centre=QPointF(
                rect.center().x(),
                rect.top() + h * 0.19,
            ),
            rayon=h * 0.060,
        )

        # ------------------------------------------------------------------
        # Panneau + plaque progression
        # ------------------------------------------------------------------

        rect_panneau = QRectF(
            rect.left() + rect.width() * 0.30,
            y_quai - h * 0.28,
            rect.width() * 0.20,
            h * 0.24,
        )

        self.panneau.peindre(
            painter,
            rect_panneau,
            nom_pays,
        )

        if i is not None and n is not None:

            rect_plaque = QRectF(
                rect_panneau.right() + h * 0.020,
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

        rect_banc = QRectF(
            rect.left() + rect.width() * 0.57,
            y_quai - h * 0.105,
            rect.width() * 0.11,
            h * 0.10,
        )

        self._dessiner_banc(
            painter,
            rect_banc,
        )

        # ------------------------------------------------------------------
        # Feu de sortie
        # ------------------------------------------------------------------

        rect_feu = QRectF(
            rect.right() - rect.width() * 0.13,
            y_quai - h * 0.30,
            rect.width() * 0.05,
            h * 0.28,
        )

        self.feu.peindre(
            painter,
            rect_feu,
            etat=self.etat_feu,
        )

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
