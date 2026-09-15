################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.52 – Classe de création d'une petite gare de campagne                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations

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


# 2 -- Panneau de gare ---------------------------------------------------------


class PanneauGare:
    """Dessine un panneau de gare porté par deux petits poteaux."""

    def __init__(
        self,
        couleur_fond: QColor | str = "#F3E7CA",
        couleur_bord: QColor | str = "#4B4036",
        couleur_texte: QColor | str = "#38322E",
        couleur_poteau: QColor | str = "#5E5349",
    ):
        self.couleur_fond = _qcolor(couleur_fond)
        self.couleur_bord = _qcolor(couleur_bord)
        self.couleur_texte = _qcolor(couleur_texte)
        self.couleur_poteau = _qcolor(couleur_poteau)

    def _police_adaptee(
        self,
        texte: str,
        largeur_max: float,
        taille_max: float,
    ) -> QFont:
        """Réduit automatiquement la police pour les noms longs."""
        taille = taille_max

        while taille >= 7:
            police = QFont("Segoe UI", int(taille))
            police.setBold(True)

            largeur = QFontMetricsF(police).horizontalAdvance(texte)

            if largeur <= largeur_max:
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
        """Dessine le panneau dans `rect`."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        hauteur_panneau = rect.height() * 0.46

        panneau = QRectF(
            rect.left(),
            rect.top(),
            rect.width(),
            hauteur_panneau,
        )

        # Poteaux
        largeur_poteau = max(2.0, rect.width() * 0.025)

        x1 = panneau.left() + panneau.width() * 0.18
        x2 = panneau.right() - panneau.width() * 0.18

        pen_poteau = QPen(self.couleur_poteau)
        pen_poteau.setWidthF(largeur_poteau)

        painter.setPen(pen_poteau)

        for x in (x1, x2):
            painter.drawLine(
                QPointF(x, panneau.bottom()),
                QPointF(x, rect.bottom()),
            )

        # Ombre
        ombre = panneau.translated(
            rect.width() * 0.012,
            rect.height() * 0.025,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha("#000000", 35))
        painter.drawRoundedRect(
            ombre,
            panneau.height() * 0.15,
            panneau.height() * 0.15,
        )

        # Plaque
        gradient = QLinearGradient(
            panneau.topLeft(),
            panneau.bottomLeft(),
        )
        gradient.setColorAt(0.0, _eclaircir(self.couleur_fond, 0.15))
        gradient.setColorAt(1.0, _assombrir(self.couleur_fond, 0.05))

        pen = QPen(self.couleur_bord)
        pen.setWidthF(max(1.2, rect.height() * 0.015))

        painter.setPen(pen)
        painter.setBrush(QBrush(gradient))

        painter.drawRoundedRect(
            panneau,
            panneau.height() * 0.15,
            panneau.height() * 0.15,
        )

        # Texte
        marge = panneau.width() * 0.08

        police = self._police_adaptee(
            nom,
            panneau.width() - 2 * marge,
            panneau.height() * 0.32,
        )

        painter.setFont(police)
        painter.setPen(self.couleur_texte)

        painter.drawText(
            panneau.adjusted(marge, 0, -marge, 0),
            Qt.AlignmentFlag.AlignCenter,
            nom,
        )

        painter.restore()


# 3 -- Borne de progression ----------------------------------------------------


class BorneProgression:
    """
    Affiche la progression i / n sur une petite plaque ferroviaire.

    La plaque est montée sur une tige métallique et destinée à être
    placée immédiatement à côté du panneau de gare.
    """

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
        """Dessine la plaque et sa tige métallique."""

        painter.save()
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        # ------------------------------------------------------------------
        # Plaque
        # ------------------------------------------------------------------

        hauteur_plaque = rect.height() * 0.42

        rect_plaque = QRectF(
            rect.left(),
            rect.top(),
            rect.width(),
            hauteur_plaque,
        )

        # ------------------------------------------------------------------
        # Tige
        # ------------------------------------------------------------------

        x_tige = rect.center().x()

        largeur_tige = max(
            2.0,
            rect.width() * 0.065,
        )

        gradient_tige = QLinearGradient(
            QPointF(
                x_tige - largeur_tige,
                0,
            ),
            QPointF(
                x_tige + largeur_tige,
                0,
            ),
        )

        gradient_tige.setColorAt(
            0.0,
            _assombrir(
                self.couleur_tige,
                0.28,
            ),
        )

        gradient_tige.setColorAt(
            0.42,
            _eclaircir(
                self.couleur_tige,
                0.34,
            ),
        )

        gradient_tige.setColorAt(
            1.0,
            _assombrir(
                self.couleur_tige,
                0.20,
            ),
        )

        rect_tige = QRectF(
            x_tige - largeur_tige / 2,
            rect_plaque.bottom(),
            largeur_tige,
            rect.bottom() - rect_plaque.bottom(),
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(gradient_tige))

        painter.drawRoundedRect(
            rect_tige,
            largeur_tige / 2,
            largeur_tige / 2,
        )

        # ------------------------------------------------------------------
        # Ombre de la plaque
        # ------------------------------------------------------------------

        ombre = rect_plaque.translated(
            rect.width() * 0.025,
            rect.height() * 0.018,
        )

        painter.setBrush(
            _avec_alpha(
                "#000000",
                45,
            )
        )

        painter.drawRoundedRect(
            ombre,
            rect_plaque.height() * 0.13,
            rect_plaque.height() * 0.13,
        )

        # ------------------------------------------------------------------
        # Métal de la plaque
        # ------------------------------------------------------------------

        gradient_plaque = QLinearGradient(
            rect_plaque.topLeft(),
            rect_plaque.bottomRight(),
        )

        gradient_plaque.setColorAt(
            0.0,
            _eclaircir(
                self.couleur_plaque,
                0.27,
            ),
        )

        gradient_plaque.setColorAt(
            0.35,
            self.couleur_plaque,
        )

        gradient_plaque.setColorAt(
            1.0,
            _assombrir(
                self.couleur_plaque,
                0.23,
            ),
        )

        pen = QPen(self.couleur_bord)

        pen.setWidthF(
            max(
                1.0,
                rect.width() * 0.025,
            )
        )

        painter.setPen(pen)

        painter.setBrush(QBrush(gradient_plaque))

        painter.drawRoundedRect(
            rect_plaque,
            rect_plaque.height() * 0.13,
            rect_plaque.height() * 0.13,
        )

        # ------------------------------------------------------------------
        # Petits rivets
        # ------------------------------------------------------------------

        rayon_rivet = max(
            1.0,
            rect.width() * 0.025,
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(
            _eclaircir(
                self.couleur_plaque,
                0.45,
            )
        )

        marge = rect.width() * 0.10

        for x in (
            rect_plaque.left() + marge,
            rect_plaque.right() - marge,
        ):
            painter.drawEllipse(
                QPointF(
                    x,
                    rect_plaque.top() + marge,
                ),
                rayon_rivet,
                rayon_rivet,
            )

        # ------------------------------------------------------------------
        # Texte
        # ------------------------------------------------------------------

        police = QFont(
            "Segoe UI",
            max(
                7,
                int(rect_plaque.height() * 0.30),
            ),
        )

        police.setBold(True)

        painter.setFont(police)

        painter.setPen(self.couleur_texte)

        painter.drawText(
            rect_plaque,
            Qt.AlignmentFlag.AlignCenter,
            f"{i}/{n}",
        )

        painter.restore()


# 4 -- Petite maison de gare ---------------------------------------------------


class MaisonGare:
    """
    Dessine une petite maison de garde / bâtiment voyageurs.

    Elle reste volontairement simple afin de ne pas cacher le paysage.
    """

    def __init__(
        self,
        couleur_mur: QColor | str = "#E7D6B6",
        couleur_toit: QColor | str = "#8B4738",
        couleur_bois: QColor | str = "#6F503B",
        couleur_vitre: QColor | str = "#91B7C5",
    ):
        self.couleur_mur = _qcolor(couleur_mur)
        self.couleur_toit = _qcolor(couleur_toit)
        self.couleur_bois = _qcolor(couleur_bois)
        self.couleur_vitre = _qcolor(couleur_vitre)

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine le petit bâtiment."""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Corps
        corps = QRectF(
            rect.left() + rect.width() * 0.08,
            rect.top() + rect.height() * 0.30,
            rect.width() * 0.84,
            rect.height() * 0.70,
        )

        gradient = QLinearGradient(
            corps.topLeft(),
            corps.bottomLeft(),
        )
        gradient.setColorAt(0.0, _eclaircir(self.couleur_mur, 0.12))
        gradient.setColorAt(1.0, _assombrir(self.couleur_mur, 0.08))

        painter.setPen(
            QPen(
                _assombrir(self.couleur_mur, 0.28),
                max(1.0, rect.height() * 0.008),
            )
        )
        painter.setBrush(QBrush(gradient))
        painter.drawRect(corps)

        # Toit
        path_toit = QPainterPath()

        path_toit.moveTo(
            rect.left(),
            rect.top() + rect.height() * 0.34,
        )
        path_toit.lineTo(
            rect.center().x(),
            rect.top(),
        )
        path_toit.lineTo(
            rect.right(),
            rect.top() + rect.height() * 0.34,
        )
        path_toit.closeSubpath()

        grad_toit = QLinearGradient(
            rect.topLeft(),
            QPointF(rect.left(), rect.top() + rect.height() * 0.34),
        )
        grad_toit.setColorAt(0.0, _eclaircir(self.couleur_toit, 0.12))
        grad_toit.setColorAt(1.0, _assombrir(self.couleur_toit, 0.14))

        painter.setPen(
            QPen(
                _assombrir(self.couleur_toit, 0.28),
                max(1.0, rect.height() * 0.008),
            )
        )
        painter.setBrush(QBrush(grad_toit))
        painter.drawPath(path_toit)

        # Porte
        porte = QRectF(
            corps.center().x() - corps.width() * 0.10,
            corps.top() + corps.height() * 0.30,
            corps.width() * 0.20,
            corps.height() * 0.70,
        )

        painter.setPen(
            QPen(
                _assombrir(self.couleur_bois, 0.25),
                max(1.0, rect.height() * 0.007),
            )
        )
        painter.setBrush(self.couleur_bois)
        painter.drawRoundedRect(
            porte,
            porte.width() * 0.08,
            porte.width() * 0.08,
        )

        # Fenêtres
        largeur_fenetre = corps.width() * 0.18
        hauteur_fenetre = corps.height() * 0.25

        for x in (
            corps.left() + corps.width() * 0.16,
            corps.right() - corps.width() * 0.16 - largeur_fenetre,
        ):

            fenetre = QRectF(
                x,
                corps.top() + corps.height() * 0.27,
                largeur_fenetre,
                hauteur_fenetre,
            )

            grad_vitre = QLinearGradient(
                fenetre.topLeft(),
                fenetre.bottomLeft(),
            )
            grad_vitre.setColorAt(0.0, _eclaircir(self.couleur_vitre, 0.25))
            grad_vitre.setColorAt(1.0, _assombrir(self.couleur_vitre, 0.12))

            painter.setPen(
                QPen(
                    self.couleur_bois,
                    max(1.0, rect.height() * 0.008),
                )
            )
            painter.setBrush(QBrush(grad_vitre))

            painter.drawRect(fenetre)

            # Croisillon
            painter.drawLine(
                QPointF(fenetre.center().x(), fenetre.top()),
                QPointF(fenetre.center().x(), fenetre.bottom()),
            )
            painter.drawLine(
                QPointF(fenetre.left(), fenetre.center().y()),
                QPointF(fenetre.right(), fenetre.center().y()),
            )

        painter.restore()


# 5 -- Barrière de sortie ------------------------------------------------------


class BarriereGare:
    """
    Dessine une petite barrière de sortie de gare.

    Le pied reste toujours vertical.

    Le bras est en revanche dessiné en perspective :
        - fermeture : il descend légèrement vers les rails ;
        - ouverture : il se relève presque verticalement.

    `ouverture` :
        0.0 = fermée
        1.0 = ouverte
    """

    def __init__(
        self,
        couleur_claire: QColor | str = "#F1E8D8",
        couleur_rouge: QColor | str = "#B84A45",
        couleur_socle: QColor | str = "#4C5154",
        angle_fermee: float = -17.0,
        angle_ouverte: float = 77.0,
    ):
        self.couleur_claire = _qcolor(couleur_claire)
        self.couleur_rouge = _qcolor(couleur_rouge)
        self.couleur_socle = _qcolor(couleur_socle)

        self.angle_fermee = angle_fermee
        self.angle_ouverte = angle_ouverte

    def peindre(
        self,
        painter: QPainter,
        pivot: QPointF,
        longueur: float,
        hauteur_scene: float,
        ouverture: float = 0.0,
    ) -> None:
        """Dessine la barrière autour de son pivot."""

        ouverture = max(
            0.0,
            min(1.0, ouverture),
        )

        painter.save()
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        # ------------------------------------------------------------------
        # Pied vertical
        # ------------------------------------------------------------------

        largeur_socle = hauteur_scene * 0.035
        hauteur_socle = hauteur_scene * 0.18

        rect_socle = QRectF(
            pivot.x() - largeur_socle / 2,
            pivot.y() - hauteur_socle * 0.18,
            largeur_socle,
            hauteur_socle,
        )

        gradient_socle = QLinearGradient(
            rect_socle.topLeft(),
            rect_socle.topRight(),
        )

        gradient_socle.setColorAt(
            0.0,
            _assombrir(self.couleur_socle, 0.20),
        )
        gradient_socle.setColorAt(
            0.45,
            _eclaircir(self.couleur_socle, 0.15),
        )
        gradient_socle.setColorAt(
            1.0,
            _assombrir(self.couleur_socle, 0.25),
        )

        painter.setPen(
            QPen(
                _assombrir(self.couleur_socle, 0.30),
                max(1.0, hauteur_scene * 0.005),
            )
        )

        painter.setBrush(QBrush(gradient_socle))

        painter.drawRoundedRect(
            rect_socle,
            largeur_socle * 0.20,
            largeur_socle * 0.20,
        )

        # ------------------------------------------------------------------
        # Bras
        # ------------------------------------------------------------------

        painter.save()

        painter.translate(pivot)

        angle = self.angle_fermee + (self.angle_ouverte - self.angle_fermee) * ouverture

        painter.rotate(angle)

        epaisseur = max(
            5.0,
            hauteur_scene * 0.028,
        )

        rect_bras = QRectF(
            -longueur,
            -epaisseur / 2,
            longueur,
            epaisseur,
        )

        painter.setPen(
            QPen(
                _assombrir(self.couleur_claire, 0.28),
                max(1.0, epaisseur * 0.08),
            )
        )

        painter.setBrush(self.couleur_claire)

        painter.drawRoundedRect(
            rect_bras,
            epaisseur * 0.30,
            epaisseur * 0.30,
        )

        # Bandes rouges
        largeur_bande = longueur / 7

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(self.couleur_rouge)

        for i in (1, 3, 5):

            painter.drawRect(
                QRectF(
                    -longueur + i * largeur_bande,
                    -epaisseur / 2,
                    largeur_bande,
                    epaisseur,
                )
            )

        painter.restore()

        # ------------------------------------------------------------------
        # Axe
        # ------------------------------------------------------------------

        rayon = hauteur_scene * 0.018

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(
            _eclaircir(
                self.couleur_socle,
                0.30,
            )
        )

        painter.drawEllipse(
            pivot,
            rayon,
            rayon,
        )

        painter.restore()


# 6 -- Classe principale de gare ----------------------------------------------


class GareCampagne:
    """
    Petite gare de campagne destinée à l'animation du train.

    Contrairement aux grandes gares :
        - elle ne masque pas le paysage ;
        - elle ne provoque pas de changement de décor ;
        - elle peut comporter une petite maisonnette ;
        - elle dispose d'une barrière de sortie.

    La gare est dessinée en deux couches :
        - `peindre_arriere` avant le train ;
        - `peindre_avant` après le train.
    """

    masque_paysage = False
    masque_rails = False

    def __init__(
        self,
        avec_maison: bool = True,
        maison_a_gauche: bool = True,
        couleur_quai: QColor | str = "#BDB5A5",
        couleur_bord_quai: QColor | str = "#E3D9C8",
        couleur_sol: QColor | str = "#8C8274",
        lampadaire_allume: bool = False,
    ):
        self.avec_maison = avec_maison
        self.maison_a_gauche = maison_a_gauche
        self.lampadaire_allume = lampadaire_allume

        self.couleur_quai = _qcolor(couleur_quai)
        self.couleur_bord_quai = _qcolor(couleur_bord_quai)
        self.couleur_sol = _qcolor(couleur_sol)

        self.panneau = PanneauGare()
        self.borne = BorneProgression()
        self.maison = MaisonGare()
        self.barriere = BarriereGare()

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    def largeur_recommandee(
        self,
        hauteur_scene: float,
    ) -> float:
        """Largeur approximative idéale de la gare."""
        return hauteur_scene * 2.35

    def _y_quai(
        self,
        rect: QRectF,
        y_rail: float | None,
    ) -> float:
        """Altitude du dessus du quai."""
        if y_rail is not None:
            return y_rail - rect.height() * 0.055

        return rect.top() + rect.height() * 0.68

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
        Dessine les éléments situés derrière le train.

        `rect` peut faire toute la hauteur du widget ; la gare n'utilise
        volontairement que sa partie inférieure.
        """
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        y_quai = self._y_quai(rect, y_rail)

        # ------------------------------------------------------------------
        # Quai
        # ------------------------------------------------------------------

        hauteur_quai = h * 0.13

        rect_quai = QRectF(
            rect.left() + rect.width() * 0.025,
            y_quai,
            rect.width() * 0.95,
            hauteur_quai,
        )

        gradient = QLinearGradient(
            rect_quai.topLeft(),
            rect_quai.bottomLeft(),
        )

        gradient.setColorAt(
            0.0,
            _eclaircir(self.couleur_quai, 0.10),
        )
        gradient.setColorAt(
            1.0,
            _assombrir(self.couleur_quai, 0.15),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(rect_quai)

        # Bord clair du quai
        bord = QRectF(
            rect_quai.left(),
            rect_quai.top(),
            rect_quai.width(),
            max(3.0, h * 0.018),
        )

        painter.setBrush(self.couleur_bord_quai)
        painter.drawRect(bord)

        # ------------------------------------------------------------------
        # Maison éventuelle
        # ------------------------------------------------------------------

        if self.avec_maison:

            largeur_maison = rect.width() * 0.30
            hauteur_maison = h * 0.39

            if self.maison_a_gauche:
                x_maison = rect.left() + rect.width() * 0.07
            else:
                x_maison = rect.right() - rect.width() * 0.07 - largeur_maison

            rect_maison = QRectF(
                x_maison,
                y_quai - hauteur_maison,
                largeur_maison,
                hauteur_maison,
            )

            self.maison.peindre(
                painter,
                rect_maison,
            )

        # ------------------------------------------------------------------
        # Panneau de gare
        # ------------------------------------------------------------------

        largeur_panneau = rect.width() * 0.31
        hauteur_panneau = h * 0.26

        if self.avec_maison and not self.maison_a_gauche:
            x_panneau = rect.left() + rect.width() * 0.12
        else:
            x_panneau = rect.left() + rect.width() * 0.48

        rect_panneau = QRectF(
            x_panneau,
            y_quai - hauteur_panneau,
            largeur_panneau,
            hauteur_panneau,
        )

        self.panneau.peindre(
            painter,
            rect_panneau,
            nom_pays,
        )

        # ------------------------------------------------------------------
        # Plaque de progression
        # ------------------------------------------------------------------

        if i is not None and n is not None:

            largeur_borne = h * 0.13
            hauteur_borne = h * 0.25

            rect_borne = QRectF(
                rect_panneau.right() + h * 0.025,
                y_quai - hauteur_borne,
                largeur_borne,
                hauteur_borne,
            )

            self.borne.peindre(
                painter,
                rect_borne,
                i,
                n,
            )

        # ------------------------------------------------------------------
        # Lampadaire
        # ------------------------------------------------------------------

        x_lampe = rect.left() + rect.width() * 0.94

        y_lampe = y_quai - h * 0.235

        # Halo lumineux
        if self.lampadaire_allume:

            rayon_halo = h * 0.115

            halo = QRadialGradient(
                QPointF(
                    x_lampe,
                    y_lampe,
                ),
                rayon_halo,
            )

            halo.setColorAt(
                0.0,
                QColor(
                    255,
                    222,
                    145,
                    110,
                ),
            )

            halo.setColorAt(
                0.35,
                QColor(
                    255,
                    218,
                    135,
                    55,
                ),
            )

            halo.setColorAt(
                1.0,
                QColor(
                    255,
                    210,
                    120,
                    0,
                ),
            )

            painter.setPen(Qt.PenStyle.NoPen)

            painter.setBrush(QBrush(halo))

            painter.drawEllipse(
                QPointF(
                    x_lampe,
                    y_lampe,
                ),
                rayon_halo,
                rayon_halo,
            )

        # Mât
        pen_mat = QPen(QColor("#4C5152"))

        pen_mat.setWidthF(
            max(
                2.0,
                h * 0.012,
            )
        )

        painter.setPen(pen_mat)

        painter.drawLine(
            QPointF(
                x_lampe,
                y_quai,
            ),
            QPointF(
                x_lampe,
                y_lampe,
            ),
        )

        # Petite tête métallique
        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QColor("#454C50"))

        painter.drawEllipse(
            QPointF(
                x_lampe,
                y_lampe,
            ),
            h * 0.032,
            h * 0.032,
        )

        # Ampoule
        if self.lampadaire_allume:

            couleur_ampoule = QColor("#FFE3A0")

        else:

            couleur_ampoule = QColor("#B9B39F")

        painter.setBrush(couleur_ampoule)

        painter.drawEllipse(
            QPointF(
                x_lampe,
                y_lampe,
            ),
            h * 0.020,
            h * 0.020,
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
        """Dessine la borne et la barrière devant le train."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        h = rect.height()
        y_quai = self._y_quai(rect, y_rail)

        # ------------------------------------------------------------------
        # Barrière de sortie
        # ------------------------------------------------------------------

        pivot = QPointF(
            rect.right() - rect.width() * 0.035,
            y_quai - h * 0.015,
        )

        self.barriere.peindre(
            painter=painter,
            pivot=pivot,
            longueur=rect.width() * 0.25,
            hauteur_scene=h,
            ouverture=kwargs.get("ouverture_barriere", 0.0),
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
        """
        Dessine la gare entièrement.

        Cette méthode est pratique pour tester la gare seule. Dans la scène
        finale, préférer `peindre_arriere` puis `peindre_avant`.
        """
        self.peindre_arriere(
            painter=painter,
            rect=rect,
            nom_pays=nom_pays,
            i=i,
            n=n,
            y_rail=y_rail,
        )

        self.peindre_avant(painter=painter, rect=rect, y_rail=y_rail, **kwargs)
