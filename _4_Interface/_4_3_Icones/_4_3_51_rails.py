################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.51 – Classe de création de rails                                         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

# 1 -- Fonctions utilitaires ---------------------------------------------------


def _qcolor(couleur: QColor | str) -> QColor:
    """Retourne une couleur sous forme de QColor."""
    return couleur if isinstance(couleur, QColor) else QColor(couleur)


def _avec_alpha(
    couleur: QColor | str,
    alpha: int,
) -> QColor:
    """Retourne une copie de la couleur avec l'alpha demandé."""
    couleur = _qcolor(couleur)
    couleur.setAlpha(max(0, min(255, alpha)))
    return couleur


def _melanger(
    couleur_1: QColor | str,
    couleur_2: QColor | str,
    proportion: float,
) -> QColor:
    """Mélange deux couleurs en RGB."""
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


# 2 -- Classe de création des rails -------------------------------------------


class Rails:
    """
    Dessine une voie ferrée vue légèrement de côté.

    La voie comprend :
        - un lit de ballast optionnel ;
        - des traverses en bois ;
        - un rail arrière légèrement atténué ;
        - un rail avant plus marqué ;
        - de petits boulons optionnels.

    Le paramètre `decalage` permet de faire défiler les traverses sous un
    train immobile afin de donner une impression de mouvement.

    Un decalage croissant fait défiler la voie vers la gauche, ce qui
    correspond à un train avançant vers la droite.
    """

    def __init__(
        self,
        couleur_rail: QColor | str = "#515A60",
        couleur_traverse: QColor | str = "#70513A",
        couleur_ballast: QColor | str = "#A6A7A3",
        couleur_boulon: QColor | str = "#30363A",
        espacement_traverses: float = 46.0,
        ballast: bool = True,
        boulons: bool = True,
        texture_bois: bool = True,
    ):
        self.couleur_rail = _qcolor(couleur_rail)
        self.couleur_traverse = _qcolor(couleur_traverse)
        self.couleur_ballast = _qcolor(couleur_ballast)
        self.couleur_boulon = _qcolor(couleur_boulon)

        self.espacement_traverses = max(10.0, espacement_traverses)

        self.ballast = ballast
        self.boulons = boulons
        self.texture_bois = texture_bois

        # Décalage utilisé lors de l'animation.
        self.decalage = 0.0

    # --------------------------------------------------------------------------
    # Animation
    # --------------------------------------------------------------------------

    def avancer(
        self,
        distance: float,
    ) -> None:
        """
        Fait avancer visuellement la voie.

        Une distance positive fait défiler les traverses vers la gauche.
        """
        self.decalage = (self.decalage + distance) % self.espacement_traverses

    def reinitialiser(self) -> None:
        """Replace les traverses à leur position initiale."""
        self.decalage = 0.0

    # --------------------------------------------------------------------------
    # Géométrie
    # --------------------------------------------------------------------------

    @staticmethod
    def y_roulement(
        rect: QRectF,
    ) -> float:
        """
        Retourne l'altitude à laquelle doit toucher le bas des roues.

        Cette valeur est utile pour positionner précisément le train.
        """
        return rect.top() + rect.height() * 0.18

    # --------------------------------------------------------------------------
    # Ballast
    # --------------------------------------------------------------------------

    def _dessiner_ballast(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine un lit de ballast sous la voie."""
        if not self.ballast:
            return

        y_haut = rect.top() + rect.height() * 0.31
        y_bas = rect.bottom()

        path = QPainterPath()
        path.moveTo(rect.left(), y_haut)
        path.lineTo(rect.right(), y_haut)
        path.lineTo(rect.right(), y_bas)
        path.lineTo(rect.left(), y_bas)
        path.closeSubpath()

        gradient = QLinearGradient(
            QPointF(0, y_haut),
            QPointF(0, y_bas),
        )

        gradient.setColorAt(
            0.0,
            _eclaircir(self.couleur_ballast, 0.10),
        )
        gradient.setColorAt(
            0.50,
            self.couleur_ballast,
        )
        gradient.setColorAt(
            1.0,
            _assombrir(self.couleur_ballast, 0.14),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

        # Une petite ombre sous la voie donne davantage de profondeur.
        ombre = QRectF(
            rect.left(),
            y_haut,
            rect.width(),
            rect.height() * 0.12,
        )

        gradient_ombre = QLinearGradient(
            ombre.topLeft(),
            ombre.bottomLeft(),
        )

        gradient_ombre.setColorAt(
            0.0,
            _avec_alpha("#000000", 40),
        )
        gradient_ombre.setColorAt(
            1.0,
            _avec_alpha("#000000", 0),
        )

        painter.setBrush(QBrush(gradient_ombre))
        painter.drawRect(ombre)

    # --------------------------------------------------------------------------
    # Traverses
    # --------------------------------------------------------------------------

    def _dessiner_traverse(
        self,
        painter: QPainter,
        rect: QRectF,
        x: float,
    ) -> None:
        """Dessine une traverse légèrement en perspective."""
        h = rect.height()

        y_haut = rect.top() + h * 0.23
        y_bas = rect.top() + h * 0.78

        largeur_haut = h * 0.16
        largeur_bas = h * 0.24

        # Très légère inclinaison vers la droite.
        decalage_perspective = h * 0.04

        path = QPainterPath()

        path.moveTo(
            x - largeur_haut / 2,
            y_haut,
        )
        path.lineTo(
            x + largeur_haut / 2,
            y_haut,
        )
        path.lineTo(
            x + largeur_bas / 2 + decalage_perspective,
            y_bas,
        )
        path.lineTo(
            x - largeur_bas / 2 + decalage_perspective,
            y_bas,
        )
        path.closeSubpath()

        gradient = QLinearGradient(
            QPointF(x, y_haut),
            QPointF(x, y_bas),
        )

        gradient.setColorAt(
            0.0,
            _eclaircir(self.couleur_traverse, 0.13),
        )
        gradient.setColorAt(
            0.55,
            self.couleur_traverse,
        )
        gradient.setColorAt(
            1.0,
            _assombrir(self.couleur_traverse, 0.22),
        )

        pen = QPen(
            _assombrir(self.couleur_traverse, 0.28),
        )
        pen.setWidthF(max(0.8, h * 0.012))

        painter.setPen(pen)
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

        # Quelques veines très discrètes donnent l'impression de bois.
        if self.texture_bois:

            pen_bois = QPen(
                _avec_alpha(
                    _assombrir(self.couleur_traverse, 0.35),
                    70,
                )
            )
            pen_bois.setWidthF(max(0.6, h * 0.007))

            painter.setPen(pen_bois)

            for proportion in (0.38, 0.63):

                yy = y_haut + (y_bas - y_haut) * proportion

                largeur = largeur_haut + (largeur_bas - largeur_haut) * proportion

                painter.drawLine(
                    QPointF(
                        x - largeur * 0.34,
                        yy,
                    ),
                    QPointF(
                        x + largeur * 0.34,
                        yy,
                    ),
                )

    # --------------------------------------------------------------------------
    # Rails métalliques
    # --------------------------------------------------------------------------

    def _dessiner_rail(
        self,
        painter: QPainter,
        rect: QRectF,
        y: float,
        epaisseur: float,
        opacite: int = 255,
    ) -> None:
        """Dessine un rail horizontal avec une petite surface brillante."""
        couleur = QColor(self.couleur_rail)
        couleur.setAlpha(opacite)

        rect_rail = QRectF(
            rect.left(),
            y,
            rect.width(),
            epaisseur,
        )

        gradient = QLinearGradient(
            rect_rail.topLeft(),
            rect_rail.bottomLeft(),
        )

        gradient.setColorAt(
            0.0,
            _avec_alpha(
                _eclaircir(couleur, 0.32),
                opacite,
            ),
        )
        gradient.setColorAt(
            0.30,
            couleur,
        )
        gradient.setColorAt(
            1.0,
            _avec_alpha(
                _assombrir(couleur, 0.35),
                opacite,
            ),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))

        painter.drawRoundedRect(
            rect_rail,
            epaisseur * 0.18,
            epaisseur * 0.18,
        )

        # Bord supérieur poli.
        pen_reflet = QPen(_avec_alpha("#FFFFFF", int(opacite * 0.30)))
        pen_reflet.setWidthF(max(0.7, epaisseur * 0.10))

        painter.setPen(pen_reflet)

        painter.drawLine(
            QPointF(
                rect.left(),
                y + epaisseur * 0.12,
            ),
            QPointF(
                rect.right(),
                y + epaisseur * 0.12,
            ),
        )

    # --------------------------------------------------------------------------
    # Boulons
    # --------------------------------------------------------------------------

    def _dessiner_boulons(
        self,
        painter: QPainter,
        rect: QRectF,
        positions_x: list[float],
        y: float,
    ) -> None:
        """Dessine de petits boulons à la jonction rail / traverses."""
        if not self.boulons:
            return

        rayon = max(1.0, rect.height() * 0.018)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.couleur_boulon)

        for x in positions_x:

            painter.drawEllipse(
                QPointF(x, y),
                rayon,
                rayon,
            )

    # --------------------------------------------------------------------------
    # Dessin principal
    # --------------------------------------------------------------------------

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        decalage: float | None = None,
    ) -> None:
        """
        Dessine la voie ferrée dans `rect`.

        `decalage` :
            - None : utilise `self.decalage` ;
            - valeur positive : décale les traverses vers la gauche.

        Les rails métalliques restent immobiles ; ce sont les traverses
        et le ballast qui donnent la sensation de mouvement.
        """
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        if decalage is None:
            decalage = self.decalage

        h = rect.height()

        # ------------------------------------------------------------------
        # Ballast
        # ------------------------------------------------------------------

        self._dessiner_ballast(
            painter,
            rect,
        )

        # ------------------------------------------------------------------
        # Positions principales
        # ------------------------------------------------------------------

        y_rail_avant = self.y_roulement(rect)

        y_rail_arriere = rect.top() + h * 0.36

        epaisseur_avant = max(
            3.0,
            h * 0.095,
        )

        epaisseur_arriere = max(
            2.0,
            h * 0.065,
        )

        # ------------------------------------------------------------------
        # Rail arrière
        # ------------------------------------------------------------------

        self._dessiner_rail(
            painter,
            rect,
            y_rail_arriere,
            epaisseur_arriere,
            opacite=150,
        )

        # ------------------------------------------------------------------
        # Traverses
        # ------------------------------------------------------------------

        espacement = self.espacement_traverses

        decalage = decalage % espacement

        x_depart = rect.left() - espacement - decalage

        positions_x = []

        x = x_depart

        while x <= rect.right() + espacement:

            self._dessiner_traverse(
                painter,
                rect,
                x,
            )

            positions_x.append(x)

            x += espacement

        # ------------------------------------------------------------------
        # Rail avant
        # ------------------------------------------------------------------

        self._dessiner_rail(
            painter,
            rect,
            y_rail_avant,
            epaisseur_avant,
            opacite=255,
        )

        # ------------------------------------------------------------------
        # Boulons
        # ------------------------------------------------------------------

        self._dessiner_boulons(
            painter,
            rect,
            positions_x,
            y_rail_avant + epaisseur_avant * 0.64,
        )

        painter.restore()
