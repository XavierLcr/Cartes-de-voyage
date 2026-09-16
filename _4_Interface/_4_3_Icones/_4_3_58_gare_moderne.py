################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.58 – Classe de création d'une gare moderne                               #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from datetime import datetime

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetricsF,
    QLinearGradient,
    QPainter,
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


# 2 -- Panneau principal moderne ----------------------------------------------


class PanneauGareModerne:
    """Panneau numérique de quai, sobre et contemporain."""

    def __init__(
        self,
        couleur_fond: QColor | str = "#1D2B36",
        couleur_bord: QColor | str = "#5E7688",
        couleur_texte: QColor | str = "#F4FBFF",
        couleur_accent: QColor | str = "#27B0E6",
        couleur_support: QColor | str = "#7A8892",
    ):
        self.couleur_fond = _qcolor(couleur_fond)
        self.couleur_bord = _qcolor(couleur_bord)
        self.couleur_texte = _qcolor(couleur_texte)
        self.couleur_accent = _qcolor(couleur_accent)
        self.couleur_support = _qcolor(couleur_support)

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
        """Dessine le panneau numérique."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        x_tige = rect.center().x()
        largeur_tige = max(2.0, h * 0.065)

        gradient_tige = QLinearGradient(
            QPointF(x_tige - largeur_tige, 0),
            QPointF(x_tige + largeur_tige, 0),
        )
        gradient_tige.setColorAt(0.0, _assombrir(self.couleur_support, 0.22))
        gradient_tige.setColorAt(0.5, _eclaircir(self.couleur_support, 0.18))
        gradient_tige.setColorAt(1.0, _assombrir(self.couleur_support, 0.18))

        rect_tige = QRectF(
            x_tige - largeur_tige / 2,
            rect.top() + h * 0.30,
            largeur_tige,
            h * 0.70,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient_tige))
        painter.drawRoundedRect(rect_tige, largeur_tige * 0.45, largeur_tige * 0.45)

        rect_panneau = QRectF(
            rect.left(),
            rect.top(),
            rect.width(),
            h * 0.39,
        )

        ombre = rect_panneau.translated(h * 0.025, h * 0.028)
        painter.setBrush(_avec_alpha("#000000", 40))
        painter.drawRoundedRect(
            ombre,
            rect_panneau.height() * 0.18,
            rect_panneau.height() * 0.18,
        )

        gradient_fond = QLinearGradient(
            rect_panneau.topLeft(),
            rect_panneau.bottomLeft(),
        )
        gradient_fond.setColorAt(0.0, _eclaircir(self.couleur_fond, 0.08))
        gradient_fond.setColorAt(1.0, _assombrir(self.couleur_fond, 0.08))

        pen = QPen(self.couleur_bord)
        pen.setWidthF(max(1.0, h * 0.020))
        painter.setPen(pen)
        painter.setBrush(QBrush(gradient_fond))
        painter.drawRoundedRect(
            rect_panneau,
            rect_panneau.height() * 0.18,
            rect_panneau.height() * 0.18,
        )

        # Liseré lumineux supérieur.
        rect_lisere = QRectF(
            rect_panneau.left() + rect_panneau.height() * 0.08,
            rect_panneau.top() + rect_panneau.height() * 0.08,
            rect_panneau.width() - rect_panneau.height() * 0.16,
            rect_panneau.height() * 0.08,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha(self.couleur_accent, 150))
        painter.drawRoundedRect(
            rect_lisere,
            rect_lisere.height() * 0.5,
            rect_lisere.height() * 0.5,
        )

        marge_texte = rect_panneau.width() * 0.08
        police = self._police_adaptee(
            nom,
            rect_panneau.width() - 2 * marge_texte,
            rect_panneau.height() * 0.34,
        )
        painter.setFont(police)
        painter.setPen(self.couleur_texte)
        painter.drawText(
            rect_panneau.adjusted(marge_texte, 0, -marge_texte, 0),
            Qt.AlignmentFlag.AlignCenter,
            nom,
        )

        painter.restore()


# 3 -- Plaque de progression moderne ------------------------------------------


class PlaqueProgressionModerne:
    """Petit badge numérique de progression i/n."""

    def __init__(
        self,
        couleur_fond: QColor | str = "#18222B",
        couleur_bord: QColor | str = "#627685",
        couleur_texte: QColor | str = "#EAF7FF",
        couleur_support: QColor | str = "#78868F",
        couleur_accent: QColor | str = "#6ED3FF",
    ):
        self.couleur_fond = _qcolor(couleur_fond)
        self.couleur_bord = _qcolor(couleur_bord)
        self.couleur_texte = _qcolor(couleur_texte)
        self.couleur_support = _qcolor(couleur_support)
        self.couleur_accent = _qcolor(couleur_accent)

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        i: int,
        n: int,
    ) -> None:
        """Dessine la plaque et son support."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        rect_boite = QRectF(
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
        grad_tige.setColorAt(0.0, _assombrir(self.couleur_support, 0.20))
        grad_tige.setColorAt(0.45, _eclaircir(self.couleur_support, 0.15))
        grad_tige.setColorAt(1.0, _assombrir(self.couleur_support, 0.18))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_tige))
        painter.drawRoundedRect(
            QRectF(
                x_tige - largeur_tige / 2,
                rect_boite.bottom(),
                largeur_tige,
                rect.bottom() - rect_boite.bottom(),
            ),
            largeur_tige * 0.45,
            largeur_tige * 0.45,
        )

        grad_boite = QLinearGradient(
            rect_boite.topLeft(),
            rect_boite.bottomLeft(),
        )
        grad_boite.setColorAt(0.0, _eclaircir(self.couleur_fond, 0.08))
        grad_boite.setColorAt(1.0, _assombrir(self.couleur_fond, 0.05))

        pen = QPen(self.couleur_bord)
        pen.setWidthF(max(1.0, h * 0.020))
        painter.setPen(pen)
        painter.setBrush(QBrush(grad_boite))
        painter.drawRoundedRect(
            rect_boite,
            rect_boite.height() * 0.20,
            rect_boite.height() * 0.20,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha(self.couleur_accent, 120))
        painter.drawRoundedRect(
            QRectF(
                rect_boite.left() + rect_boite.width() * 0.12,
                rect_boite.top() + rect_boite.height() * 0.10,
                rect_boite.width() * 0.76,
                rect_boite.height() * 0.08,
            ),
            rect_boite.height() * 0.04,
            rect_boite.height() * 0.04,
        )

        police = QFont("Segoe UI", max(7, int(rect_boite.height() * 0.31)))
        police.setBold(True)
        painter.setFont(police)
        painter.setPen(self.couleur_texte)
        painter.drawText(rect_boite, Qt.AlignmentFlag.AlignCenter, f"{i}/{n}")

        painter.restore()


# 4 -- Afficheur horaire moderne ----------------------------------------------


class HorlogeModerne:
    """Afficheur horaire numérique type quai moderne."""

    def __init__(
        self,
        couleur_fond: QColor | str = "#152028",
        couleur_bord: QColor | str = "#627685",
        couleur_texte: QColor | str = "#F4FBFF",
        couleur_accent: QColor | str = "#2CC2F0",
    ):
        self.couleur_fond = _qcolor(couleur_fond)
        self.couleur_bord = _qcolor(couleur_bord)
        self.couleur_texte = _qcolor(couleur_texte)
        self.couleur_accent = _qcolor(couleur_accent)

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        texte: str = "10:10",
    ) -> None:
        """Dessine un petit afficheur digital."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        ombre = rect.translated(rect.height() * 0.04, rect.height() * 0.05)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha("#000000", 38))
        painter.drawRoundedRect(ombre, rect.height() * 0.18, rect.height() * 0.18)

        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_fond, 0.05))
        grad.setColorAt(1.0, _assombrir(self.couleur_fond, 0.04))

        pen = QPen(self.couleur_bord)
        pen.setWidthF(max(1.0, rect.height() * 0.10))
        painter.setPen(pen)
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect, rect.height() * 0.18, rect.height() * 0.18)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha(self.couleur_accent, 145))
        painter.drawRoundedRect(
            QRectF(
                rect.left() + rect.width() * 0.06,
                rect.top() + rect.height() * 0.08,
                rect.width() * 0.88,
                rect.height() * 0.10,
            ),
            rect.height() * 0.05,
            rect.height() * 0.05,
        )

        police = QFont("Consolas", max(7, int(rect.height() * 0.40)))
        police.setBold(True)
        painter.setFont(police)
        painter.setPen(self.couleur_texte)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, texte)

        painter.restore()


# 5 -- Feu ferroviaire moderne -------------------------------------------------


class FeuFerroviaireModerne:
    """Feu ferroviaire moderne, plus fin et plus géométrique."""

    def __init__(
        self,
        couleur_metal: QColor | str = "#353D43",
        couleur_support: QColor | str = "#606D75",
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
        """Dessine une optique LED contemporaine."""
        painter.save()

        if allume:
            halo = QRadialGradient(centre, rayon * 3.2)
            halo.setColorAt(0.0, _avec_alpha(couleur, 120))
            halo.setColorAt(0.38, _avec_alpha(couleur, 52))
            halo.setColorAt(1.0, _avec_alpha(couleur, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo))
            painter.drawEllipse(centre, rayon * 3.2, rayon * 3.2)

        # Bague carrée adoucie.
        rect_bague = QRectF(
            centre.x() - rayon * 1.30,
            centre.y() - rayon * 1.30,
            rayon * 2.60,
            rayon * 2.60,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_assombrir(self.couleur_metal, 0.35))
        painter.drawRoundedRect(rect_bague, rayon * 0.42, rayon * 0.42)

        grad = QRadialGradient(
            QPointF(centre.x() - rayon * 0.18, centre.y() - rayon * 0.20),
            rayon * 1.08,
        )
        grad.setColorAt(0.0, _eclaircir(couleur, 0.42 if allume else 0.10))
        grad.setColorAt(0.62, couleur if allume else _assombrir(couleur, 0.45))
        grad.setColorAt(1.0, _assombrir(couleur, 0.58))

        painter.setBrush(QBrush(grad))
        painter.drawEllipse(centre, rayon, rayon)

        painter.setBrush(_avec_alpha("#FFFFFF", 60 if allume else 25))
        painter.drawEllipse(
            QPointF(centre.x() - rayon * 0.22, centre.y() - rayon * 0.25),
            rayon * 0.26,
            rayon * 0.17,
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

        h = rect.height()
        cx = rect.center().x()

        largeur_boite = min(rect.width() * 0.86, h * 0.30)
        hauteur_boite = h * 0.47

        rect_boite = QRectF(
            cx - largeur_boite / 2,
            rect.top() + h * 0.02,
            largeur_boite,
            hauteur_boite,
        )

        largeur_mat = max(2.5, h * 0.050)
        rect_mat = QRectF(
            cx - largeur_mat / 2,
            rect_boite.bottom() - h * 0.006,
            largeur_mat,
            rect.bottom() - rect_boite.bottom() - h * 0.055,
        )

        grad_mat = QLinearGradient(
            QPointF(rect_mat.left(), 0),
            QPointF(rect_mat.right(), 0),
        )
        grad_mat.setColorAt(0.0, _assombrir(self.couleur_support, 0.24))
        grad_mat.setColorAt(0.48, _eclaircir(self.couleur_support, 0.16))
        grad_mat.setColorAt(1.0, _assombrir(self.couleur_support, 0.20))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_mat))
        painter.drawRoundedRect(rect_mat, largeur_mat * 0.42, largeur_mat * 0.42)

        rect_socle = QRectF(
            cx - h * 0.070,
            rect.bottom() - h * 0.055,
            h * 0.140,
            h * 0.040,
        )
        painter.setBrush(_assombrir(self.couleur_support, 0.24))
        painter.drawRoundedRect(
            rect_socle,
            rect_socle.height() * 0.24,
            rect_socle.height() * 0.24,
        )

        grad_boite = QLinearGradient(rect_boite.topLeft(), rect_boite.bottomRight())
        grad_boite.setColorAt(0.0, _eclaircir(self.couleur_metal, 0.12))
        grad_boite.setColorAt(0.55, self.couleur_metal)
        grad_boite.setColorAt(1.0, _assombrir(self.couleur_metal, 0.22))

        pen = QPen(_assombrir(self.couleur_metal, 0.40))
        pen.setWidthF(max(1.0, h * 0.014))
        painter.setPen(pen)
        painter.setBrush(QBrush(grad_boite))
        painter.drawRoundedRect(
            rect_boite,
            largeur_boite * 0.12,
            largeur_boite * 0.12,
        )

        # Petite casquette supérieure moderne.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_assombrir(self.couleur_metal, 0.18))
        painter.drawRoundedRect(
            QRectF(
                rect_boite.left() + largeur_boite * 0.08,
                rect_boite.top() - h * 0.012,
                largeur_boite * 0.84,
                h * 0.022,
            ),
            h * 0.006,
            h * 0.006,
        )

        rayon = min(largeur_boite * 0.19, hauteur_boite * 0.10)
        centres = [
            QPointF(cx, rect_boite.top() + hauteur_boite * 0.21),
            QPointF(cx, rect_boite.top() + hauteur_boite * 0.50),
            QPointF(cx, rect_boite.top() + hauteur_boite * 0.79),
        ]
        couleurs = (QColor("#D24F4F"), QColor("#D29D39"), QColor("#4AB867"))
        etats = ("rouge", "orange", "vert")

        for centre, couleur, nom_etat in zip(centres, couleurs, etats):
            self._dessiner_optique(painter, centre, rayon, couleur, etat == nom_etat)

        painter.restore()


# 6 -- Gare moderne ------------------------------------------------------------


class GareModerne:
    """
    Gare intérieure moderne pleine hauteur.

    Logique visuelle
    ----------------
    On se situe dans une gare contemporaine :
        - grande façade vitrée / toiture légère ;
        - structure métallique alignée ;
        - quais sobres ;
        - portail d'entrée à gauche ;
        - portail de sortie à droite ;
        - feu ferroviaire moderne.

    L'ensemble reste compatible avec le modèle de la gare ancienne :
        - même logique de masque ;
        - même API publique ;
        - même découpage peindre_arriere / peindre_avant.
    """

    masque_paysage = True
    masque_rails = True

    def __init__(
        self,
        couleur_beton: QColor | str = "#D8E0E5",
        couleur_beton_fonce: QColor | str = "#B3C0C8",
        couleur_metal: QColor | str = "#76858F",
        couleur_metal_fonce: QColor | str = "#55636C",
        couleur_verre: QColor | str = "#DDF2FB",
        couleur_verre_fonce: QColor | str = "#B7D5E4",
        couleur_quai: QColor | str = "#9AA7AE",
        couleur_bord_quai: QColor | str = "#F0E35F",
        couleur_plancher: QColor | str = "#6E787E",
        couleur_accent: QColor | str = "#27B0E6",
        lampes_allumees: bool = True,
        etat_feu: str = "rouge",
    ):
        self.couleur_beton = _qcolor(couleur_beton)
        self.couleur_beton_fonce = _qcolor(couleur_beton_fonce)
        self.couleur_metal = _qcolor(couleur_metal)
        self.couleur_metal_fonce = _qcolor(couleur_metal_fonce)
        self.couleur_verre = _qcolor(couleur_verre)
        self.couleur_verre_fonce = _qcolor(couleur_verre_fonce)
        self.couleur_quai = _qcolor(couleur_quai)
        self.couleur_bord_quai = _qcolor(couleur_bord_quai)
        self.couleur_plancher = _qcolor(couleur_plancher)
        self.couleur_accent = _qcolor(couleur_accent)

        self.lampes_allumees = lampes_allumees
        self.etat_feu = etat_feu

        self.panneau = PanneauGareModerne(
            couleur_accent=self.couleur_accent,
            couleur_support=self.couleur_metal,
        )
        self.plaque = PlaqueProgressionModerne(
            couleur_support=self.couleur_metal,
            couleur_accent=_eclaircir(self.couleur_accent, 0.18),
        )
        self.horloge = HorlogeModerne(couleur_accent=self.couleur_accent)
        self.feu = FeuFerroviaireModerne(
            couleur_metal=self.couleur_metal_fonce,
            couleur_support=self.couleur_metal,
        )

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    def largeur_recommandee(
        self,
        hauteur_scene: float,
    ) -> float:
        """Largeur idéale approximative."""
        return hauteur_scene * 3.25

    def _y_quai(
        self,
        rect: QRectF,
        y_rail: float | None,
    ) -> float:
        """Altitude du quai."""
        if y_rail is not None:
            return y_rail - rect.height() * 0.055
        return rect.top() + rect.height() * 0.70

    def _positions_piliers(
        self,
        rect: QRectF,
    ) -> tuple[float, ...]:
        """Retourne les axes des principaux poteaux."""
        return (
            rect.left() + rect.width() * 0.17,
            rect.left() + rect.width() * 0.33,
            rect.left() + rect.width() * 0.50,
            rect.left() + rect.width() * 0.67,
            rect.left() + rect.width() * 0.83,
        )

    # --------------------------------------------------------------------------
    # Éléments de structure
    # --------------------------------------------------------------------------

    def _dessiner_fond(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """Dessine le mur, la façade et la partie basse."""
        h = rect.height()

        rect_mur = QRectF(
            rect.left(),
            rect.top(),
            rect.width(),
            y_quai - rect.top(),
        )

        grad_mur = QLinearGradient(rect_mur.topLeft(), rect_mur.bottomLeft())
        grad_mur.setColorAt(0.0, _eclaircir(self.couleur_beton, 0.08))
        grad_mur.setColorAt(0.55, self.couleur_beton)
        grad_mur.setColorAt(1.0, _assombrir(self.couleur_beton, 0.05))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_mur))
        painter.drawRect(rect_mur)

        # Partie basse plus dense.
        rect_bas = QRectF(
            rect.left(),
            y_quai - h * 0.17,
            rect.width(),
            h * 0.17,
        )
        grad_bas = QLinearGradient(rect_bas.topLeft(), rect_bas.bottomLeft())
        grad_bas.setColorAt(0.0, _eclaircir(self.couleur_beton_fonce, 0.05))
        grad_bas.setColorAt(1.0, _assombrir(self.couleur_beton_fonce, 0.12))
        painter.setBrush(QBrush(grad_bas))
        painter.drawRect(rect_bas)

        # Bande horizontale architecturale.
        painter.setBrush(_avec_alpha(_eclaircir(self.couleur_beton, 0.16), 190))
        painter.drawRect(
            QRectF(
                rect.left(),
                rect.top() + h * 0.26,
                rect.width(),
                h * 0.020,
            )
        )

        # Joints subtils.
        pen = QPen(_avec_alpha(_assombrir(self.couleur_beton, 0.22), 70))
        pen.setWidthF(max(1.0, h * 0.003))
        painter.setPen(pen)

        for y in (
            rect.top() + h * 0.17,
            rect.top() + h * 0.43,
            y_quai - h * 0.17,
        ):
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))

        for x in (0.24, 0.50, 0.76):
            x_ligne = rect.left() + rect.width() * x
            painter.drawLine(
                QPointF(x_ligne, rect.top() + h * 0.28),
                QPointF(x_ligne, y_quai),
            )

    def _dessiner_portail_lateral(
        self,
        painter: QPainter,
        rect: QRectF,
        x_centre: float,
        y_quai: float,
        largeur: float,
        hauteur: float,
        cote: str,
    ) -> None:
        """Dessine un grand portail vitré latéral avec profondeur."""
        h = rect.height()
        x0 = x_centre - largeur / 2
        y0 = y_quai - hauteur

        rect_exterieur = QRectF(x0, y0, largeur, hauteur)
        epaisseur = min(largeur, hauteur) * 0.10
        decalage = rect.width() * 0.018 if cote == "entree" else -rect.width() * 0.018

        # Cadre principal.
        grad_cadre = QLinearGradient(
            rect_exterieur.topLeft(), rect_exterieur.bottomLeft()
        )
        grad_cadre.setColorAt(0.0, _eclaircir(self.couleur_metal, 0.15))
        grad_cadre.setColorAt(1.0, _assombrir(self.couleur_metal, 0.10))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_cadre))
        painter.drawRoundedRect(
            rect_exterieur,
            h * 0.010,
            h * 0.010,
        )

        # Intérieur / profondeur.
        rect_interieur = rect_exterieur.adjusted(
            epaisseur, epaisseur, -epaisseur, -epaisseur
        )
        grad_interieur = QLinearGradient(
            rect_interieur.topLeft(), rect_interieur.bottomLeft()
        )
        if cote == "entree":
            grad_interieur.setColorAt(0.0, QColor("#84939B"))
            grad_interieur.setColorAt(1.0, QColor("#465159"))
        else:
            grad_interieur.setColorAt(0.0, QColor("#E8F5FB"))
            grad_interieur.setColorAt(1.0, QColor("#BAD7E5"))
        painter.setBrush(QBrush(grad_interieur))
        painter.drawRoundedRect(
            rect_interieur,
            h * 0.008,
            h * 0.008,
        )

        # Deuxième cadre en retrait pour la profondeur.
        rect_retrait = rect_interieur.adjusted(
            decalage, epaisseur * 0.30, decalage, -epaisseur * 0.35
        )
        pen = QPen(_avec_alpha(self.couleur_metal_fonce, 140))
        pen.setWidthF(max(1.0, h * 0.004))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(
            rect_retrait,
            h * 0.006,
            h * 0.006,
        )

        # Traverse haute et montant central vitré.
        painter.setPen(
            QPen(_avec_alpha(self.couleur_metal_fonce, 165), max(1.0, h * 0.005))
        )
        y_traverse = rect_interieur.top() + rect_interieur.height() * 0.22
        painter.drawLine(
            QPointF(rect_interieur.left(), y_traverse),
            QPointF(rect_interieur.right(), y_traverse),
        )
        painter.drawLine(
            QPointF(rect_interieur.center().x(), rect_interieur.top()),
            QPointF(rect_interieur.center().x(), rect_interieur.bottom()),
        )

        # Reflets diagonaux.
        painter.setPen(QPen(_avec_alpha("#FFFFFF", 65), max(1.0, h * 0.003)))
        for proportion in (0.24, 0.58):
            x_reflet = rect_interieur.left() + rect_interieur.width() * proportion
            painter.drawLine(
                QPointF(
                    x_reflet, rect_interieur.top() + rect_interieur.height() * 0.05
                ),
                QPointF(
                    x_reflet - rect_interieur.width() * 0.12,
                    rect_interieur.bottom() - rect_interieur.height() * 0.05,
                ),
            )

    def _dessiner_verriere(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """Dessine la grande toiture légère et ses vitrages."""
        h = rect.height()
        w = rect.width()

        rect_verriere = QRectF(
            rect.left() + w * 0.08,
            rect.top() + h * 0.03,
            w * 0.84,
            y_quai - rect.top() - h * 0.50,
        )

        grad_verre = QLinearGradient(
            rect_verriere.topLeft(), rect_verriere.bottomLeft()
        )
        grad_verre.setColorAt(0.0, _eclaircir(self.couleur_verre, 0.28))
        grad_verre.setColorAt(0.55, self.couleur_verre)
        grad_verre.setColorAt(1.0, _assombrir(self.couleur_verre_fonce, 0.05))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_verre))
        painter.drawRoundedRect(
            rect_verriere,
            rect_verriere.height() * 0.08,
            rect_verriere.height() * 0.08,
        )

        # Ossature périphérique.
        pen = QPen(_avec_alpha(self.couleur_metal_fonce, 195))
        pen.setWidthF(max(1.0, h * 0.006))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(
            rect_verriere,
            rect_verriere.height() * 0.08,
            rect_verriere.height() * 0.08,
        )

        # Montants verticaux réguliers.
        n_travees = 8
        for i in range(1, n_travees):
            x = rect_verriere.left() + rect_verriere.width() * i / n_travees
            painter.drawLine(
                QPointF(x, rect_verriere.top()),
                QPointF(x, rect_verriere.bottom()),
            )

        # Traverses.
        for p in (0.22, 0.45, 0.68, 0.87):
            y = rect_verriere.top() + rect_verriere.height() * p
            painter.drawLine(
                QPointF(rect_verriere.left(), y),
                QPointF(rect_verriere.right(), y),
            )

        # Contreventements légers.
        pen_diag = QPen(_avec_alpha(self.couleur_metal_fonce, 110))
        pen_diag.setWidthF(max(1.0, h * 0.0035))
        painter.setPen(pen_diag)
        for i in range(0, n_travees, 2):
            x1 = rect_verriere.left() + rect_verriere.width() * i / n_travees
            x2 = rect_verriere.left() + rect_verriere.width() * (i + 1) / n_travees
            painter.drawLine(
                QPointF(x1, rect_verriere.bottom()),
                QPointF(x2, rect_verriere.top() + rect_verriere.height() * 0.18),
            )

        # Reflets.
        painter.setPen(QPen(_avec_alpha("#FFFFFF", 52), max(1.0, h * 0.004)))
        for p in (0.18, 0.46, 0.73):
            painter.drawLine(
                QPointF(
                    rect_verriere.left() + rect_verriere.width() * p,
                    rect_verriere.top(),
                ),
                QPointF(
                    rect_verriere.left() + rect_verriere.width() * (p - 0.08),
                    rect_verriere.bottom(),
                ),
            )

        # Sous-face du débord de toiture.
        rect_sous_face = QRectF(
            rect.left() + w * 0.10,
            rect_verriere.bottom() - h * 0.01,
            w * 0.80,
            h * 0.040,
        )
        grad_sous_face = QLinearGradient(
            rect_sous_face.topLeft(), rect_sous_face.bottomLeft()
        )
        grad_sous_face.setColorAt(0.0, _eclaircir(self.couleur_metal, 0.05))
        grad_sous_face.setColorAt(1.0, _assombrir(self.couleur_metal, 0.10))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_sous_face))
        painter.drawRoundedRect(
            rect_sous_face,
            rect_sous_face.height() * 0.18,
            rect_sous_face.height() * 0.18,
        )

    def _dessiner_piliers(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """Dessine les poteaux principaux de la gare."""
        h = rect.height()
        largeur = h * 0.055

        for x in self._positions_piliers(rect):
            rect_pilier = QRectF(
                x - largeur / 2,
                rect.top() + h * 0.08,
                largeur,
                y_quai - rect.top() - h * 0.08,
            )

            ombre = rect_pilier.translated(h * 0.012, 0)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(_avec_alpha("#000000", 28))
            painter.drawRoundedRect(
                ombre,
                largeur * 0.18,
                largeur * 0.18,
            )

            grad = QLinearGradient(
                QPointF(rect_pilier.left(), 0),
                QPointF(rect_pilier.right(), 0),
            )
            grad.setColorAt(0.0, _assombrir(self.couleur_metal, 0.22))
            grad.setColorAt(0.45, _eclaircir(self.couleur_metal, 0.12))
            grad.setColorAt(1.0, _assombrir(self.couleur_metal, 0.18))

            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(
                rect_pilier,
                largeur * 0.18,
                largeur * 0.18,
            )

            # Nervure centrale.
            painter.setBrush(_avec_alpha(_eclaircir(self.couleur_metal, 0.18), 185))
            painter.drawRoundedRect(
                QRectF(
                    rect_pilier.center().x() - largeur * 0.08,
                    rect_pilier.top(),
                    largeur * 0.16,
                    rect_pilier.height(),
                ),
                largeur * 0.06,
                largeur * 0.06,
            )

            # Tête et pied du pilier.
            for y0, hh in (
                (rect_pilier.top(), h * 0.035),
                (rect_pilier.bottom() - h * 0.045, h * 0.045),
            ):
                painter.setBrush(_assombrir(self.couleur_metal, 0.06))
                painter.drawRoundedRect(
                    QRectF(
                        rect_pilier.left() - largeur * 0.18,
                        y0,
                        rect_pilier.width() + largeur * 0.36,
                        hh,
                    ),
                    hh * 0.18,
                    hh * 0.18,
                )

    def _dessiner_baie_vitree(
        self,
        painter: QPainter,
        rect_baie: QRectF,
        type_baie: str = "fenetre",
    ) -> None:
        """Dessine une baie vitrée ou une porte coulissante."""
        if rect_baie.width() <= 0 or rect_baie.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h_baie = rect_baie.height()
        ep = h_baie * 0.065

        grad_cadre = QLinearGradient(rect_baie.topLeft(), rect_baie.bottomLeft())
        grad_cadre.setColorAt(0.0, _eclaircir(self.couleur_metal, 0.12))
        grad_cadre.setColorAt(1.0, _assombrir(self.couleur_metal, 0.10))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_cadre))
        painter.drawRoundedRect(rect_baie, h_baie * 0.06, h_baie * 0.06)

        rect_vitre = rect_baie.adjusted(ep, ep, -ep, -ep)
        grad_vitre = QLinearGradient(rect_vitre.topLeft(), rect_vitre.bottomLeft())
        grad_vitre.setColorAt(0.0, _eclaircir(self.couleur_verre, 0.20))
        grad_vitre.setColorAt(1.0, _assombrir(self.couleur_verre_fonce, 0.04))
        painter.setBrush(QBrush(grad_vitre))
        painter.drawRoundedRect(rect_vitre, h_baie * 0.04, h_baie * 0.04)

        # Montants.
        painter.setPen(
            QPen(_avec_alpha(self.couleur_metal_fonce, 170), max(1.0, h_baie * 0.026))
        )
        if type_baie == "porte":
            x_milieu = rect_vitre.center().x()
            painter.drawLine(
                QPointF(x_milieu, rect_vitre.top()),
                QPointF(x_milieu, rect_vitre.bottom()),
            )
            y_poignee = rect_vitre.top() + rect_vitre.height() * 0.58
            for signe in (-1, 1):
                x_p = x_milieu + signe * rect_vitre.width() * 0.13
                painter.drawLine(
                    QPointF(x_p, y_poignee - rect_vitre.height() * 0.08),
                    QPointF(x_p, y_poignee + rect_vitre.height() * 0.08),
                )
            # Bandeau coulissant.
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(_avec_alpha(self.couleur_accent, 120))
            painter.drawRoundedRect(
                QRectF(
                    rect_vitre.left() + rect_vitre.width() * 0.08,
                    rect_vitre.top() + rect_vitre.height() * 0.08,
                    rect_vitre.width() * 0.84,
                    rect_vitre.height() * 0.08,
                ),
                rect_vitre.height() * 0.04,
                rect_vitre.height() * 0.04,
            )
        else:
            for p in (0.33, 0.66):
                x = rect_vitre.left() + rect_vitre.width() * p
                painter.drawLine(
                    QPointF(x, rect_vitre.top()), QPointF(x, rect_vitre.bottom())
                )
            y_traverse = rect_vitre.top() + rect_vitre.height() * 0.44
            painter.drawLine(
                QPointF(rect_vitre.left(), y_traverse),
                QPointF(rect_vitre.right(), y_traverse),
            )

        # Reflets.
        painter.setPen(QPen(_avec_alpha("#FFFFFF", 70), max(1.0, h_baie * 0.018)))
        for p in (0.28, 0.66):
            x = rect_vitre.left() + rect_vitre.width() * p
            painter.drawLine(
                QPointF(x, rect_vitre.top() + rect_vitre.height() * 0.04),
                QPointF(
                    x - rect_vitre.width() * 0.10,
                    rect_vitre.bottom() - rect_vitre.height() * 0.04,
                ),
            )

        # Allège / appui.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_assombrir(self.couleur_beton_fonce, 0.06))
        painter.drawRoundedRect(
            QRectF(
                rect_baie.left() - h_baie * 0.01,
                rect_baie.bottom(),
                rect_baie.width() + h_baie * 0.02,
                h_baie * 0.06,
            ),
            h_baie * 0.02,
            h_baie * 0.02,
        )

        painter.restore()

    def _dessiner_lampes_lineaires(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine des rampes lumineuses linéaires sous la toiture."""
        h = rect.height()
        positions = (0.24, 0.50, 0.76)
        y = rect.top() + h * 0.26

        for p in positions:
            x = rect.left() + rect.width() * p
            rect_lampe = QRectF(
                x - rect.width() * 0.08,
                y,
                rect.width() * 0.16,
                h * 0.016,
            )

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(_assombrir(self.couleur_metal, 0.10))
            painter.drawRoundedRect(
                rect_lampe,
                rect_lampe.height() * 0.5,
                rect_lampe.height() * 0.5,
            )

            if self.lampes_allumees:
                halo = QRadialGradient(
                    rect_lampe.center(),
                    rect_lampe.width() * 0.62,
                )
                halo.setColorAt(0.0, QColor(255, 252, 225, 70))
                halo.setColorAt(0.55, QColor(255, 247, 210, 18))
                halo.setColorAt(1.0, QColor(255, 247, 210, 0))
                painter.setBrush(QBrush(halo))
                painter.drawEllipse(
                    rect_lampe.center(),
                    rect_lampe.width() * 0.62,
                    h * 0.10,
                )

                painter.setBrush(QColor("#FFF4C7"))
            else:
                painter.setBrush(QColor("#C8CDD1"))

            painter.drawRoundedRect(
                rect_lampe.adjusted(
                    rect_lampe.width() * 0.08,
                    rect_lampe.height() * 0.18,
                    -rect_lampe.width() * 0.08,
                    -rect_lampe.height() * 0.18,
                ),
                rect_lampe.height() * 0.35,
                rect_lampe.height() * 0.35,
            )

    def _dessiner_tableau_depart(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine un petit tableau d'affichage des départs."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0.0, QColor("#18232B"))
        grad.setColorAt(1.0, QColor("#11181E"))

        pen = QPen(QColor("#536774"))
        pen.setWidthF(max(1.0, rect.height() * 0.04))
        painter.setPen(pen)
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect, rect.height() * 0.08, rect.height() * 0.08)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha(self.couleur_accent, 120))
        painter.drawRoundedRect(
            QRectF(
                rect.left() + rect.width() * 0.05,
                rect.top() + rect.height() * 0.07,
                rect.width() * 0.90,
                rect.height() * 0.08,
            ),
            rect.height() * 0.03,
            rect.height() * 0.03,
        )

        lignes = (
            ("TER", "10:14", "Voie 2"),
            ("IC", "10:27", "Voie 4"),
            ("RER", "10:39", "Voie 1"),
        )

        police = QFont("Segoe UI", max(6, int(rect.height() * 0.11)))
        police.setBold(True)
        painter.setFont(police)
        painter.setPen(QColor("#EAF7FF"))

        y = rect.top() + rect.height() * 0.28
        pas = rect.height() * 0.22

        for type_train, heure, voie in lignes:
            painter.drawText(
                QRectF(rect.left() + rect.width() * 0.08, y, rect.width() * 0.20, pas),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                type_train,
            )
            painter.drawText(
                QRectF(rect.left() + rect.width() * 0.34, y, rect.width() * 0.25, pas),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                heure,
            )
            painter.drawText(
                QRectF(rect.left() + rect.width() * 0.62, y, rect.width() * 0.28, pas),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                voie,
            )
            y += pas

        painter.restore()

    def _dessiner_banc(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine un banc moderne de quai."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Assise.
        grad_assise = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad_assise.setColorAt(0.0, QColor("#C4CCD1"))
        grad_assise.setColorAt(1.0, QColor("#98A5AE"))

        rect_assise = QRectF(
            rect.left(),
            rect.top() + rect.height() * 0.44,
            rect.width(),
            rect.height() * 0.16,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_assise))
        painter.drawRoundedRect(
            rect_assise,
            rect_assise.height() * 0.22,
            rect_assise.height() * 0.22,
        )

        # Dossier.
        rect_dossier = QRectF(
            rect.left() + rect.width() * 0.08,
            rect.top() + rect.height() * 0.12,
            rect.width() * 0.84,
            rect.height() * 0.16,
        )
        painter.drawRoundedRect(
            rect_dossier,
            rect_dossier.height() * 0.22,
            rect_dossier.height() * 0.22,
        )

        # Pieds fins.
        pen = QPen(_assombrir(self.couleur_metal_fonce, 0.10))
        pen.setWidthF(max(1.0, rect.width() * 0.045))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        for x in (
            rect.left() + rect.width() * 0.22,
            rect.center().x(),
            rect.right() - rect.width() * 0.22,
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
        """Dessine le quai arrière de la station moderne."""
        h = rect.height()

        rect_quai = QRectF(
            rect.left(),
            y_quai,
            rect.width(),
            h * 0.15,
        )

        grad = QLinearGradient(rect_quai.topLeft(), rect_quai.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_quai, 0.06))
        grad.setColorAt(1.0, _assombrir(self.couleur_quai, 0.10))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(rect_quai)

        # Bande de sécurité jaune.
        rect_bord = QRectF(
            rect_quai.left(),
            rect_quai.top(),
            rect_quai.width(),
            max(4.0, h * 0.018),
        )
        painter.setBrush(self.couleur_bord_quai)
        painter.drawRect(rect_bord)

        # Trame et pointillés de sécurité.
        pen_dalles = QPen(_avec_alpha(_assombrir(self.couleur_quai, 0.28), 85))
        pen_dalles.setWidthF(max(1.0, h * 0.0032))
        painter.setPen(pen_dalles)

        largeur_dalle = rect.width() * 0.10
        x = rect.left()
        while x < rect.right():
            painter.drawLine(
                QPointF(x, rect_quai.top()),
                QPointF(x, rect_quai.bottom()),
            )
            x += largeur_dalle

        pen_pointilles = QPen(_avec_alpha("#FFFFFF", 150))
        pen_pointilles.setStyle(Qt.PenStyle.DashLine)
        pen_pointilles.setDashPattern([3, 3])
        pen_pointilles.setWidthF(max(1.0, h * 0.0028))
        painter.setPen(pen_pointilles)
        painter.drawLine(
            QPointF(rect.left(), y_quai + h * 0.030),
            QPointF(rect.right(), y_quai + h * 0.030),
        )

    def _dessiner_bloc_bas_avant(
        self,
        painter: QPainter,
        rect: QRectF,
        y_quai: float,
    ) -> None:
        """Dessine le grand bloc avant qui masque le bas du train."""
        h = rect.height()

        rect_bas = QRectF(
            rect.left(),
            y_quai,
            rect.width(),
            rect.bottom() - y_quai,
        )

        grad = QLinearGradient(rect_bas.topLeft(), rect_bas.bottomLeft())
        grad.setColorAt(0.0, _eclaircir(self.couleur_quai, 0.08))
        grad.setColorAt(0.18, self.couleur_quai)
        grad.setColorAt(1.0, _assombrir(self.couleur_plancher, 0.16))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(rect_bas)

        # Bord de quai.
        hauteur_bord = max(4.0, h * 0.020)
        rect_bord = QRectF(rect.left(), y_quai, rect.width(), hauteur_bord)
        painter.setBrush(self.couleur_bord_quai)
        painter.drawRect(rect_bord)

        # Ombre sous la rive.
        hauteur_ombre = h * 0.030
        ombre = QLinearGradient(
            QPointF(0, y_quai + hauteur_bord),
            QPointF(0, y_quai + hauteur_bord + hauteur_ombre),
        )
        ombre.setColorAt(0.0, QColor(0, 0, 0, 62))
        ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(ombre))
        painter.drawRect(
            QRectF(
                rect.left(),
                y_quai + hauteur_bord,
                rect.width(),
                hauteur_ombre,
            )
        )

        # Dalles.
        pen_dalles = QPen(_avec_alpha(_assombrir(self.couleur_quai, 0.30), 78))
        pen_dalles.setWidthF(max(1.0, h * 0.003))
        painter.setPen(pen_dalles)

        largeur_dalle = rect.width() * 0.095
        x = rect.left()
        while x <= rect.right():
            painter.drawLine(QPointF(x, y_quai), QPointF(x, rect.bottom()))
            x += largeur_dalle

        for proportion in (0.32, 0.66):
            y = y_quai + rect_bas.height() * proportion
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))

        # Petits plots techniques modernes.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha(_assombrir(self.couleur_plancher, 0.14), 185))
        for p in (0.21, 0.50, 0.79):
            painter.drawRoundedRect(
                QRectF(
                    rect.left() + rect.width() * p - h * 0.012,
                    y_quai + hauteur_bord + h * 0.014,
                    h * 0.024,
                    h * 0.010,
                ),
                h * 0.003,
                h * 0.003,
            )

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
        """Dessine la gare derrière le train."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        w = rect.width()
        y_quai = self._y_quai(rect, y_rail)

        # ------------------------------------------------------------------
        # Fond général
        # ------------------------------------------------------------------

        self._dessiner_fond(painter, rect, y_quai)

        # ------------------------------------------------------------------
        # Portails latéraux
        # ------------------------------------------------------------------

        largeur_portail = w * 0.135
        hauteur_portail = h * 0.56

        self._dessiner_portail_lateral(
            painter=painter,
            rect=rect,
            x_centre=rect.left() + largeur_portail / 2,
            y_quai=y_quai,
            largeur=largeur_portail,
            hauteur=hauteur_portail,
            cote="entree",
        )
        self._dessiner_portail_lateral(
            painter=painter,
            rect=rect,
            x_centre=rect.right() - largeur_portail / 2,
            y_quai=y_quai,
            largeur=largeur_portail,
            hauteur=hauteur_portail,
            cote="sortie",
        )

        # ------------------------------------------------------------------
        # Verrière, structure et éclairage
        # ------------------------------------------------------------------

        self._dessiner_verriere(painter, rect, y_quai)
        self._dessiner_piliers(painter, rect, y_quai)
        self._dessiner_lampes_lineaires(painter, rect)

        # ------------------------------------------------------------------
        # Baies basses alignées
        # ------------------------------------------------------------------

        hauteur_baie = h * 0.22
        y_baie = y_quai - hauteur_baie

        self._dessiner_baie_vitree(
            painter,
            QRectF(rect.left() + w * 0.23, y_baie, w * 0.11, hauteur_baie),
            type_baie="fenetre",
        )
        self._dessiner_baie_vitree(
            painter,
            QRectF(rect.left() + w * 0.43, y_baie, w * 0.14, hauteur_baie),
            type_baie="porte",
        )
        self._dessiner_baie_vitree(
            painter,
            QRectF(rect.left() + w * 0.66, y_baie, w * 0.11, hauteur_baie),
            type_baie="fenetre",
        )

        # ------------------------------------------------------------------
        # Afficheur horaire central
        # ------------------------------------------------------------------

        self.horloge.peindre(
            painter,
            QRectF(
                rect.center().x() - w * 0.055,
                rect.top() + h * 0.15,
                w * 0.11,
                h * 0.072,
            ),
            texte=datetime.now().strftime("%H:%M"),
        )

        # ------------------------------------------------------------------
        # Panneau pays + progression
        # ------------------------------------------------------------------

        rect_panneau = QRectF(
            rect.left() + w * 0.29,
            y_quai - h * 0.29,
            w * 0.21,
            h * 0.24,
        )
        self.panneau.peindre(painter, rect_panneau, nom_pays)

        if i is not None and n is not None:
            rect_plaque = QRectF(
                rect_panneau.right() + h * 0.020,
                y_quai - h * 0.27,
                h * 0.12,
                h * 0.22,
            )
            self.plaque.peindre(painter, rect_plaque, i, n)

        # ------------------------------------------------------------------
        # Tableau des départs + banc
        # ------------------------------------------------------------------

        self._dessiner_tableau_depart(
            painter,
            QRectF(
                rect.left() + w * 0.58,
                rect.top() + h * 0.24,
                w * 0.17,
                h * 0.18,
            ),
        )

        self._dessiner_banc(
            painter,
            QRectF(
                rect.left() + w * 0.59,
                y_quai - h * 0.105,
                w * 0.12,
                h * 0.10,
            ),
        )

        # ------------------------------------------------------------------
        # Quai et feu
        # ------------------------------------------------------------------

        self._dessiner_quai(painter, rect, y_quai)

        rect_feu = QRectF(
            rect.left() + w * 0.765,
            y_quai - h * 0.31,
            w * 0.055,
            h * 0.29,
        )
        self.feu.peindre(painter, rect_feu, etat=self.etat_feu)

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
        """Dessine les éléments devant le train."""
        if rect.width() <= 0 or rect.height() <= 0 or y_rail is None:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        y_quai = self._y_quai(rect, y_rail)
        h = rect.height()

        # ------------------------------------------------------------------
        # Bloc bas devant la rame
        # ------------------------------------------------------------------

        self._dessiner_bloc_bas_avant(painter, rect, y_quai)

        # ------------------------------------------------------------------
        # Poteaux proches en avant-plan
        # ------------------------------------------------------------------

        largeur = h * 0.040
        for x in (
            rect.left() + h * 0.030,
            rect.right() - h * 0.030 - largeur,
        ):
            rect_pilier = QRectF(x, rect.top(), largeur, y_quai - rect.top())

            grad = QLinearGradient(
                QPointF(rect_pilier.left(), 0),
                QPointF(rect_pilier.right(), 0),
            )
            grad.setColorAt(0.0, _assombrir(self.couleur_metal_fonce, 0.26))
            grad.setColorAt(0.45, _eclaircir(self.couleur_metal_fonce, 0.05))
            grad.setColorAt(1.0, _assombrir(self.couleur_metal_fonce, 0.18))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(
                rect_pilier,
                largeur * 0.18,
                largeur * 0.18,
            )

            painter.setBrush(
                _avec_alpha(_eclaircir(self.couleur_metal_fonce, 0.15), 170)
            )
            painter.drawRoundedRect(
                QRectF(
                    rect_pilier.center().x() - largeur * 0.07,
                    rect_pilier.top(),
                    largeur * 0.14,
                    rect_pilier.height(),
                ),
                largeur * 0.05,
                largeur * 0.05,
            )

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
            **kwargs,
        )
        self.peindre_avant(
            painter=painter,
            rect=rect,
            y_rail=y_rail,
            **kwargs,
        )
