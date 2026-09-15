################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.50 – Classe de création d'un train régional                              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

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

from _4_Interface._4_3_Icones._4_3_47_fenetre import FenetreTrain

# 1 -- Fonctions utilitaires ---------------------------------------------------


def _qcolor(couleur: QColor | str) -> QColor:
    """Retourne un QColor à partir d'une chaîne hexadécimale ou d'un QColor."""
    return couleur if isinstance(couleur, QColor) else QColor(couleur)


def _avec_alpha(couleur: QColor | str, alpha: int) -> QColor:
    """Retourne la couleur avec l'alpha demandé."""
    c = _qcolor(couleur)
    c.setAlpha(max(0, min(255, alpha)))
    return c


def _melanger(
    couleur_1: QColor | str,
    couleur_2: QColor | str,
    t: float,
) -> QColor:
    """
    Mélange deux couleurs en RGB.

    `t=0` renvoie `couleur_1`, `t=1` renvoie `couleur_2`.
    """
    c1 = _qcolor(couleur_1)
    c2 = _qcolor(couleur_2)
    t = max(0.0, min(1.0, t))

    return QColor(
        round(c1.red() * (1 - t) + c2.red() * t),
        round(c1.green() * (1 - t) + c2.green() * t),
        round(c1.blue() * (1 - t) + c2.blue() * t),
        round(c1.alpha() * (1 - t) + c2.alpha() * t),
    )


def _eclaircir(couleur: QColor | str, t: float = 0.2) -> QColor:
    """Éclaircit une couleur en la rapprochant du blanc."""
    return _melanger(couleur, "#FFFFFF", t)


def _assombrir(couleur: QColor | str, t: float = 0.2) -> QColor:
    """Assombrit une couleur en la rapprochant du noir."""
    return _melanger(couleur, "#000000", t)


# 2 -- Classe de roue de train -------------------------------------------------


class RoueTrain:
    """
    Dessine une roue de train stylisée.

    Une rotation peut être fournie pour donner une impression de roulement.
    """

    def __init__(
        self,
        couleur_pneu: QColor | str = "#262A2E",
        couleur_jante: QColor | str = "#858C93",
        couleur_moyeu: QColor | str = "#C7CDD3",
    ):
        self.couleur_pneu = _qcolor(couleur_pneu)
        self.couleur_jante = _qcolor(couleur_jante)
        self.couleur_moyeu = _qcolor(couleur_moyeu)

    def peindre(
        self,
        painter: QPainter,
        centre: QPointF,
        rayon: float,
        rotation_deg: float = 0.0,
        nb_rayons: int = 6,
    ) -> None:
        """Dessine la roue centrée sur `centre`."""
        if rayon <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Pneumatique
        grad_externe = QRadialGradient(centre, rayon)
        grad_externe.setColorAt(0.0, _eclaircir(self.couleur_pneu, 0.18))
        grad_externe.setColorAt(0.75, self.couleur_pneu)
        grad_externe.setColorAt(1.0, _assombrir(self.couleur_pneu, 0.35))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_externe))
        painter.drawEllipse(centre, rayon, rayon)

        # Jante
        rayon_jante = rayon * 0.72
        grad_jante = QRadialGradient(centre, rayon_jante)
        grad_jante.setColorAt(0.0, _eclaircir(self.couleur_jante, 0.35))
        grad_jante.setColorAt(1.0, _assombrir(self.couleur_jante, 0.20))

        painter.setBrush(QBrush(grad_jante))
        painter.drawEllipse(centre, rayon_jante, rayon_jante)

        # Rayons tournants
        painter.save()
        painter.translate(centre)
        painter.rotate(rotation_deg)

        pen_rayons = QPen(_avec_alpha(_assombrir(self.couleur_jante, 0.15), 180))
        pen_rayons.setWidthF(max(1.0, rayon * 0.10))
        painter.setPen(pen_rayons)

        for i in range(nb_rayons):
            angle = 2 * math.pi * i / nb_rayons
            x = math.cos(angle) * rayon_jante * 0.82
            y = math.sin(angle) * rayon_jante * 0.82
            painter.drawLine(QPointF(0, 0), QPointF(x, y))

        painter.restore()

        # Moyeu
        rayon_moyeu = rayon * 0.25
        grad_moyeu = QRadialGradient(centre, rayon_moyeu)
        grad_moyeu.setColorAt(0.0, _eclaircir(self.couleur_moyeu, 0.35))
        grad_moyeu.setColorAt(1.0, _assombrir(self.couleur_moyeu, 0.15))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_moyeu))
        painter.drawEllipse(centre, rayon_moyeu, rayon_moyeu)

        # Reflet
        reflet = QRectF(
            centre.x() - rayon * 0.55,
            centre.y() - rayon * 0.70,
            rayon * 0.75,
            rayon * 0.35,
        )
        painter.setBrush(_avec_alpha("#FFFFFF", 45))
        painter.drawEllipse(reflet)

        painter.restore()


# 3 -- Classe de voiture régionale ---------------------------------------------


class VoitureRegionale:
    """
    Dessine une voiture régionale chic.

    Style recherché :
        - voiture compacte et lisible ;
        - bandeau supérieur crème ;
        - caisse bordeaux / vert profond / autre ton chic ;
        - filet décoratif doré discret ;
        - bande faux bois ;
        - fenêtres régulières.
    """

    def __init__(
        self,
        nb_fenetres: int = 4,
        fenetres_allumees: list[bool] | None = None,
        couleur_caisse: QColor | str = "#7A2032",
        couleur_bandeau: QColor | str = "#E6DDCF",
        couleur_toit: QColor | str = "#58636B",
        couleur_bas: QColor | str = "#2A3035",
        couleur_bois: QColor | str = "#8A6445",
        couleur_filet: QColor | str = "#C9A86A",
        couleur_portes: QColor | str | None = None,
    ):
        self.nb_fenetres = max(1, nb_fenetres)
        self.couleur_caisse = _qcolor(couleur_caisse)
        self.couleur_bandeau = _qcolor(couleur_bandeau)
        self.couleur_toit = _qcolor(couleur_toit)
        self.couleur_bas = _qcolor(couleur_bas)
        self.couleur_bois = _qcolor(couleur_bois)
        self.couleur_filet = _qcolor(couleur_filet)
        self.couleur_portes = (
            _qcolor(couleur_portes)
            if couleur_portes is not None
            else _melanger(self.couleur_caisse, self.couleur_bandeau, 0.25)
        )

        if fenetres_allumees is None:
            self.fenetres_allumees = [False] * self.nb_fenetres
        else:
            valeurs = list(fenetres_allumees[: self.nb_fenetres])
            while len(valeurs) < self.nb_fenetres:
                valeurs.append(False)
            self.fenetres_allumees = valeurs

        self.roue = RoueTrain()
        self.fenetres: list[FenetreTrain] = []
        self._reconstruire_fenetres()

    def _reconstruire_fenetres(self) -> None:
        """Reconstruit la liste des fenêtres à partir des états allumés."""
        self.fenetres = [
            FenetreTrain(
                couleur="#9EC6D9",
                double=False,
                gauche_allumee=allumee,
                couleur_cadre="#434B50",
                couleur_montant="#4B5358",
                intensite_lumiere=1.0,
                halo=True,
                reflets=True,
            )
            for allumee in self.fenetres_allumees
        ]

    def definir_fenetres_allumees(self, fenetres_allumees: list[bool]) -> None:
        """Met à jour l'état allumé / éteint des fenêtres."""
        valeurs = list(fenetres_allumees[: self.nb_fenetres])
        while len(valeurs) < self.nb_fenetres:
            valeurs.append(False)

        self.fenetres_allumees = valeurs
        self._reconstruire_fenetres()

    def largeur_recommandee(self) -> float:
        """Largeur recommandée pour conserver de bonnes proportions."""
        return 210 + self.nb_fenetres * 54

    def _dessiner_ombre(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine une ombre légère sous la voiture."""
        ombre = QRectF(
            rect.left() + rect.width() * 0.10,
            rect.bottom() - rect.height() * 0.12,
            rect.width() * 0.80,
            rect.height() * 0.12,
        )

        grad = QRadialGradient(
            ombre.center(),
            ombre.width() * 0.55,
        )
        grad.setColorAt(0.0, _avec_alpha("#000000", 55))
        grad.setColorAt(1.0, _avec_alpha("#000000", 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(ombre)

    def _dessiner_bande_bois(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine une bande faux bois discrète sur la caisse."""
        grad_bois = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad_bois.setColorAt(0.0, _eclaircir(self.couleur_bois, 0.18))
        grad_bois.setColorAt(0.5, self.couleur_bois)
        grad_bois.setColorAt(1.0, _assombrir(self.couleur_bois, 0.22))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_bois))
        painter.drawRoundedRect(rect, rect.height() * 0.20, rect.height() * 0.20)

        # Veines du bois très légères
        pen_bois = QPen(_avec_alpha(_assombrir(self.couleur_bois, 0.25), 45))
        pen_bois.setWidthF(max(1.0, rect.height() * 0.03))
        painter.setPen(pen_bois)

        y1 = rect.top() + rect.height() * 0.35
        y2 = rect.top() + rect.height() * 0.68
        painter.drawLine(
            QPointF(rect.left() + rect.width() * 0.08, y1),
            QPointF(rect.right() - rect.width() * 0.08, y1),
        )
        painter.drawLine(
            QPointF(rect.left() + rect.width() * 0.12, y2),
            QPointF(rect.right() - rect.width() * 0.12, y2),
        )

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        phase_roues: float = 0.0,
    ) -> None:
        """Dessine la voiture dans `rect`."""
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        self._dessiner_ombre(painter, rect)

        # ------------------------------------------------------------------
        # Zones principales
        # ------------------------------------------------------------------

        rect_corps = QRectF(
            rect.left() + rect.width() * 0.03,
            rect.top() + rect.height() * 0.18,
            rect.width() * 0.94,
            rect.height() * 0.50,
        )

        rect_toit = QRectF(
            rect_corps.left() + rect_corps.width() * 0.02,
            rect_corps.top() - rect.height() * 0.09,
            rect_corps.width() * 0.96,
            rect.height() * 0.14,
        )

        rect_bandeau = QRectF(
            rect_corps.left(),
            rect_corps.top(),
            rect_corps.width(),
            rect_corps.height() * 0.22,
        )

        rect_bois = QRectF(
            rect_corps.left() + rect_corps.width() * 0.03,
            rect_corps.top() + rect_corps.height() * 0.63,
            rect_corps.width() * 0.94,
            rect_corps.height() * 0.18,
        )

        rect_soubassement = QRectF(
            rect_corps.left() + rect_corps.width() * 0.02,
            rect_corps.bottom() - rect_corps.height() * 0.05,
            rect_corps.width() * 0.96,
            rect.height() * 0.12,
        )

        # ------------------------------------------------------------------
        # Toit
        # ------------------------------------------------------------------

        grad_toit = QLinearGradient(rect_toit.topLeft(), rect_toit.bottomLeft())
        grad_toit.setColorAt(0.0, _eclaircir(self.couleur_toit, 0.25))
        grad_toit.setColorAt(0.55, self.couleur_toit)
        grad_toit.setColorAt(1.0, _assombrir(self.couleur_toit, 0.28))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_toit))
        painter.drawRoundedRect(
            rect_toit, rect_toit.height() * 0.60, rect_toit.height() * 0.60
        )

        # ------------------------------------------------------------------
        # Corps principal
        # ------------------------------------------------------------------

        grad_caisse = QLinearGradient(rect_corps.topLeft(), rect_corps.bottomLeft())
        grad_caisse.setColorAt(0.0, _eclaircir(self.couleur_caisse, 0.14))
        grad_caisse.setColorAt(0.45, self.couleur_caisse)
        grad_caisse.setColorAt(1.0, _assombrir(self.couleur_caisse, 0.18))

        pen_corps = QPen(_assombrir(self.couleur_caisse, 0.35))
        pen_corps.setWidthF(max(1.2, rect.height() * 0.010))
        painter.setPen(pen_corps)
        painter.setBrush(QBrush(grad_caisse))
        painter.drawRoundedRect(
            rect_corps, rect_corps.height() * 0.12, rect_corps.height() * 0.12
        )

        # Bandeau supérieur crème
        grad_bandeau = QLinearGradient(
            rect_bandeau.topLeft(), rect_bandeau.bottomLeft()
        )
        grad_bandeau.setColorAt(0.0, _eclaircir(self.couleur_bandeau, 0.18))
        grad_bandeau.setColorAt(1.0, _assombrir(self.couleur_bandeau, 0.10))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_bandeau))
        painter.drawRoundedRect(
            rect_bandeau, rect_bandeau.height() * 0.45, rect_bandeau.height() * 0.45
        )

        # Bande faux bois
        self._dessiner_bande_bois(painter, rect_bois)

        # Filets décoratifs
        pen_filet = QPen(self.couleur_filet)
        pen_filet.setWidthF(max(1.0, rect.height() * 0.008))
        painter.setPen(pen_filet)

        y_filet_1 = rect_corps.top() + rect_corps.height() * 0.27
        y_filet_2 = rect_corps.top() + rect_corps.height() * 0.58
        painter.drawLine(
            QPointF(rect_corps.left() + rect_corps.width() * 0.03, y_filet_1),
            QPointF(rect_corps.right() - rect_corps.width() * 0.03, y_filet_1),
        )
        painter.drawLine(
            QPointF(rect_corps.left() + rect_corps.width() * 0.03, y_filet_2),
            QPointF(rect_corps.right() - rect_corps.width() * 0.03, y_filet_2),
        )

        # ------------------------------------------------------------------
        # Portes
        # ------------------------------------------------------------------

        largeur_porte = rect_corps.width() * 0.11
        marge_porte = rect_corps.width() * 0.035

        rect_porte_g = QRectF(
            rect_corps.left() + marge_porte,
            rect_corps.top() + rect_corps.height() * 0.10,
            largeur_porte,
            rect_corps.height() * 0.78,
        )
        rect_porte_d = QRectF(
            rect_corps.right() - marge_porte - largeur_porte,
            rect_corps.top() + rect_corps.height() * 0.10,
            largeur_porte,
            rect_corps.height() * 0.78,
        )

        for rect_porte in (rect_porte_g, rect_porte_d):
            grad_porte = QLinearGradient(rect_porte.topLeft(), rect_porte.bottomLeft())
            grad_porte.setColorAt(0.0, _eclaircir(self.couleur_portes, 0.15))
            grad_porte.setColorAt(1.0, _assombrir(self.couleur_portes, 0.12))

            painter.setPen(
                QPen(
                    _assombrir(self.couleur_portes, 0.32),
                    max(1, int(rect.height() * 0.01)),
                )
            )
            painter.setBrush(QBrush(grad_porte))
            painter.drawRoundedRect(
                rect_porte, rect_porte.width() * 0.12, rect_porte.width() * 0.12
            )

            # Petite vitre de porte
            vitre = QRectF(
                rect_porte.left() + rect_porte.width() * 0.23,
                rect_porte.top() + rect_porte.height() * 0.14,
                rect_porte.width() * 0.54,
                rect_porte.height() * 0.27,
            )
            painter.setPen(Qt.PenStyle.NoPen)
            grad_vitre = QLinearGradient(vitre.topLeft(), vitre.bottomLeft())
            grad_vitre.setColorAt(0.0, _eclaircir("#8FBFD5", 0.35))
            grad_vitre.setColorAt(1.0, _assombrir("#8FBFD5", 0.15))
            painter.setBrush(QBrush(grad_vitre))
            painter.drawRoundedRect(vitre, vitre.width() * 0.18, vitre.width() * 0.18)

            # Poignée
            poignee = QRectF(
                rect_porte.right() - rect_porte.width() * 0.18,
                rect_porte.center().y() - rect_porte.height() * 0.07,
                rect_porte.width() * 0.05,
                rect_porte.height() * 0.14,
            )
            painter.setBrush(self.couleur_filet)
            painter.drawRoundedRect(poignee, poignee.width(), poignee.width())

        # ------------------------------------------------------------------
        # Fenêtres
        # ------------------------------------------------------------------

        zone_fenetres = QRectF(
            rect_porte_g.right() + rect_corps.width() * 0.025,
            rect_corps.top() + rect_corps.height() * 0.16,
            rect_porte_d.left() - rect_porte_g.right() - rect_corps.width() * 0.05,
            rect_corps.height() * 0.32,
        )

        espacement = zone_fenetres.width() * 0.03
        largeur_fen = (
            zone_fenetres.width() - espacement * (self.nb_fenetres - 1)
        ) / self.nb_fenetres
        hauteur_fen = zone_fenetres.height()

        for i, fenetre in enumerate(self.fenetres):
            x = zone_fenetres.left() + i * (largeur_fen + espacement)
            rect_fen = QRectF(
                x,
                zone_fenetres.top(),
                largeur_fen,
                hauteur_fen,
            )
            fenetre.peindre(painter, rect_fen)

        # ------------------------------------------------------------------
        # Reflet général de caisse
        # ------------------------------------------------------------------

        rect_reflet = QRectF(
            rect_corps.left() + rect_corps.width() * 0.05,
            rect_corps.top() + rect_corps.height() * 0.06,
            rect_corps.width() * 0.62,
            rect_corps.height() * 0.18,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha("#FFFFFF", 34))
        painter.drawRoundedRect(
            rect_reflet,
            rect_reflet.height() * 0.50,
            rect_reflet.height() * 0.50,
        )

        # ------------------------------------------------------------------
        # Soubassement
        # ------------------------------------------------------------------

        grad_bas = QLinearGradient(
            rect_soubassement.topLeft(), rect_soubassement.bottomLeft()
        )
        grad_bas.setColorAt(0.0, _eclaircir(self.couleur_bas, 0.14))
        grad_bas.setColorAt(1.0, _assombrir(self.couleur_bas, 0.18))

        painter.setBrush(QBrush(grad_bas))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(
            rect_soubassement,
            rect_soubassement.height() * 0.25,
            rect_soubassement.height() * 0.25,
        )

        # Bogies sobres
        rect_bogie_g = QRectF(
            rect_corps.left() + rect_corps.width() * 0.15,
            rect_soubassement.bottom() - rect.height() * 0.02,
            rect_corps.width() * 0.15,
            rect.height() * 0.06,
        )
        rect_bogie_d = QRectF(
            rect_corps.right() - rect_corps.width() * 0.30,
            rect_soubassement.bottom() - rect.height() * 0.02,
            rect_corps.width() * 0.15,
            rect.height() * 0.06,
        )

        painter.setBrush(_assombrir(self.couleur_bas, 0.10))
        painter.drawRoundedRect(
            rect_bogie_g, rect_bogie_g.height() * 0.30, rect_bogie_g.height() * 0.30
        )
        painter.drawRoundedRect(
            rect_bogie_d, rect_bogie_d.height() * 0.30, rect_bogie_d.height() * 0.30
        )

        # Roues
        rayon_roue = rect.height() * 0.11
        y_roue = rect.bottom() - rayon_roue - rect.height() * 0.03
        rotation_deg = (phase_roues % 1.0) * 360.0

        x_roues = (
            rect.left() + rect.width() * 0.23,
            rect.left() + rect.width() * 0.43,
            rect.left() + rect.width() * 0.62,
            rect.left() + rect.width() * 0.82,
        )

        for x in x_roues:
            self.roue.peindre(
                painter,
                QPointF(x, y_roue),
                rayon_roue,
                rotation_deg=rotation_deg,
            )

        # Attelage
        pen_attelage = QPen(_assombrir(self.couleur_bas, 0.05))
        pen_attelage.setWidthF(max(1.5, rect.height() * 0.012))
        painter.setPen(pen_attelage)

        y_attelage = rect_corps.bottom() - rect_corps.height() * 0.08
        painter.drawLine(
            QPointF(rect.left(), y_attelage),
            QPointF(rect.left() + rect.width() * 0.04, y_attelage),
        )
        painter.drawLine(
            QPointF(rect.right() - rect.width() * 0.04, y_attelage),
            QPointF(rect.right(), y_attelage),
        )

        painter.restore()


# 4 -- Classe de motrice régionale ---------------------------------------------


class MotriceRegionale:
    """
    Dessine une petite locomotive régionale chic.

    Le but n'est pas le réalisme ferroviaire absolu, mais une lecture immédiate :
        - cabine arrière ;
        - capot avant ;
        - grosses roues motrices ;
        - bielle animable ;
        - style élégant et chaleureux.
    """

    def __init__(
        self,
        couleur_caisse: QColor | str = "#7A2032",
        couleur_bandeau: QColor | str = "#E6DDCF",
        couleur_toit: QColor | str = "#58636B",
        couleur_bas: QColor | str = "#2A3035",
        couleur_bois: QColor | str = "#8A6445",
        couleur_filet: QColor | str = "#C9A86A",
    ):
        self.couleur_caisse = _qcolor(couleur_caisse)
        self.couleur_bandeau = _qcolor(couleur_bandeau)
        self.couleur_toit = _qcolor(couleur_toit)
        self.couleur_bas = _qcolor(couleur_bas)
        self.couleur_bois = _qcolor(couleur_bois)
        self.couleur_filet = _qcolor(couleur_filet)

        self.roue = RoueTrain()

    def largeur_recommandee(self) -> float:
        """Largeur recommandée de la motrice."""
        return 275

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        sens: int = 1,
        phase_roues: float = 0.0,
    ) -> None:
        """
        Dessine la motrice.

        `sens = 1`  : avant vers la droite
        `sens = -1` : avant vers la gauche
        `phase_roues` sert à animer les roues / la bielle.
        """
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if sens < 0:
            painter.translate(rect.center().x(), 0)
            painter.scale(-1, 1)
            painter.translate(-rect.center().x(), 0)

        phase = phase_roues % 1.0
        angle_deg = phase * 360.0
        theta = phase * 2 * math.pi

        # Ombre
        ombre = QRectF(
            rect.left() + rect.width() * 0.12,
            rect.bottom() - rect.height() * 0.12,
            rect.width() * 0.76,
            rect.height() * 0.12,
        )
        grad_ombre = QRadialGradient(ombre.center(), ombre.width() * 0.55)
        grad_ombre.setColorAt(0.0, _avec_alpha("#000000", 55))
        grad_ombre.setColorAt(1.0, _avec_alpha("#000000", 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_ombre))
        painter.drawEllipse(ombre)

        # Géométrie générale
        x = rect.left()
        y = rect.top()
        w = rect.width()
        h = rect.height()

        rect_chassis = QRectF(
            x + w * 0.10,
            y + h * 0.58,
            w * 0.78,
            h * 0.22,
        )

        rect_cabine = QRectF(
            x + w * 0.14,
            y + h * 0.24,
            w * 0.23,
            h * 0.34,
        )

        rect_toit_cabine = QRectF(
            rect_cabine.left() - w * 0.01,
            rect_cabine.top() - h * 0.07,
            rect_cabine.width() + w * 0.03,
            h * 0.10,
        )

        # Capot moteur
        path_capot = QPainterPath()
        path_capot.moveTo(x + w * 0.33, y + h * 0.60)
        path_capot.lineTo(x + w * 0.33, y + h * 0.36)
        path_capot.quadTo(
            x + w * 0.44,
            y + h * 0.24,
            x + w * 0.60,
            y + h * 0.28,
        )
        path_capot.lineTo(x + w * 0.83, y + h * 0.31)
        path_capot.quadTo(
            x + w * 0.91,
            y + h * 0.42,
            x + w * 0.89,
            y + h * 0.60,
        )
        path_capot.closeSubpath()

        # Châssis
        grad_chassis = QLinearGradient(
            rect_chassis.topLeft(), rect_chassis.bottomLeft()
        )
        grad_chassis.setColorAt(0.0, _eclaircir(self.couleur_bas, 0.14))
        grad_chassis.setColorAt(1.0, _assombrir(self.couleur_bas, 0.18))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_chassis))
        painter.drawRoundedRect(
            rect_chassis,
            rect_chassis.height() * 0.30,
            rect_chassis.height() * 0.30,
        )

        # Cabine
        grad_cabine = QLinearGradient(rect_cabine.topLeft(), rect_cabine.bottomLeft())
        grad_cabine.setColorAt(0.0, _eclaircir(self.couleur_caisse, 0.14))
        grad_cabine.setColorAt(0.45, self.couleur_caisse)
        grad_cabine.setColorAt(1.0, _assombrir(self.couleur_caisse, 0.18))

        pen_cabine = QPen(_assombrir(self.couleur_caisse, 0.35))
        pen_cabine.setWidthF(max(1.2, h * 0.010))
        painter.setPen(pen_cabine)
        painter.setBrush(QBrush(grad_cabine))
        painter.drawRoundedRect(
            rect_cabine,
            rect_cabine.width() * 0.10,
            rect_cabine.width() * 0.10,
        )

        # Toit cabine
        grad_toit = QLinearGradient(
            rect_toit_cabine.topLeft(), rect_toit_cabine.bottomLeft()
        )
        grad_toit.setColorAt(0.0, _eclaircir(self.couleur_toit, 0.25))
        grad_toit.setColorAt(0.55, self.couleur_toit)
        grad_toit.setColorAt(1.0, _assombrir(self.couleur_toit, 0.28))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_toit))
        painter.drawRoundedRect(
            rect_toit_cabine,
            rect_toit_cabine.height() * 0.55,
            rect_toit_cabine.height() * 0.55,
        )

        # Capot
        grad_capot = QLinearGradient(
            QPointF(0, y + h * 0.26),
            QPointF(0, y + h * 0.60),
        )
        grad_capot.setColorAt(0.0, _eclaircir(self.couleur_caisse, 0.10))
        grad_capot.setColorAt(0.55, self.couleur_caisse)
        grad_capot.setColorAt(1.0, _assombrir(self.couleur_caisse, 0.16))

        painter.setPen(pen_cabine)
        painter.setBrush(QBrush(grad_capot))
        painter.drawPath(path_capot)

        # Bandeau crème sur capot
        rect_bandeau = QRectF(
            x + w * 0.37,
            y + h * 0.34,
            w * 0.42,
            h * 0.08,
        )
        grad_bandeau = QLinearGradient(
            rect_bandeau.topLeft(), rect_bandeau.bottomLeft()
        )
        grad_bandeau.setColorAt(0.0, _eclaircir(self.couleur_bandeau, 0.18))
        grad_bandeau.setColorAt(1.0, _assombrir(self.couleur_bandeau, 0.10))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_bandeau))
        painter.drawRoundedRect(
            rect_bandeau,
            rect_bandeau.height() * 0.45,
            rect_bandeau.height() * 0.45,
        )

        # Bande faux bois
        rect_bois = QRectF(
            x + w * 0.38,
            y + h * 0.50,
            w * 0.32,
            h * 0.09,
        )
        grad_bois = QLinearGradient(rect_bois.topLeft(), rect_bois.bottomLeft())
        grad_bois.setColorAt(0.0, _eclaircir(self.couleur_bois, 0.18))
        grad_bois.setColorAt(0.5, self.couleur_bois)
        grad_bois.setColorAt(1.0, _assombrir(self.couleur_bois, 0.22))
        painter.setBrush(QBrush(grad_bois))
        painter.drawRoundedRect(
            rect_bois,
            rect_bois.height() * 0.20,
            rect_bois.height() * 0.20,
        )

        # Filets décoratifs
        pen_filet = QPen(self.couleur_filet)
        pen_filet.setWidthF(max(1.0, h * 0.008))
        painter.setPen(pen_filet)
        painter.drawLine(
            QPointF(x + w * 0.16, y + h * 0.44),
            QPointF(x + w * 0.80, y + h * 0.44),
        )
        painter.drawLine(
            QPointF(x + w * 0.16, y + h * 0.60),
            QPointF(x + w * 0.83, y + h * 0.60),
        )

        # Fenêtres cabine
        grad_vitre = QLinearGradient(
            QPointF(0, rect_cabine.top()),
            QPointF(0, rect_cabine.bottom()),
        )
        grad_vitre.setColorAt(0.0, _eclaircir("#9BC5D7", 0.35))
        grad_vitre.setColorAt(1.0, _assombrir("#9BC5D7", 0.20))

        pen_vitre = QPen(QColor("#455158"))
        pen_vitre.setWidthF(max(1.0, h * 0.008))
        painter.setPen(pen_vitre)
        painter.setBrush(QBrush(grad_vitre))

        rect_vitre_1 = QRectF(
            rect_cabine.left() + rect_cabine.width() * 0.12,
            rect_cabine.top() + rect_cabine.height() * 0.16,
            rect_cabine.width() * 0.28,
            rect_cabine.height() * 0.28,
        )
        rect_vitre_2 = QRectF(
            rect_cabine.left() + rect_cabine.width() * 0.46,
            rect_cabine.top() + rect_cabine.height() * 0.16,
            rect_cabine.width() * 0.28,
            rect_cabine.height() * 0.28,
        )
        rect_vitre_avant = QRectF(
            x + w * 0.79,
            y + h * 0.35,
            w * 0.07,
            h * 0.12,
        )

        for rect_vitre in (rect_vitre_1, rect_vitre_2, rect_vitre_avant):
            painter.drawRoundedRect(
                rect_vitre,
                rect_vitre.width() * 0.16,
                rect_vitre.width() * 0.16,
            )

        # Reflet
        rect_reflet = QRectF(
            x + w * 0.20,
            y + h * 0.22,
            w * 0.26,
            h * 0.08,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_avec_alpha("#FFFFFF", 34))
        painter.drawRoundedRect(
            rect_reflet,
            rect_reflet.height() * 0.50,
            rect_reflet.height() * 0.50,
        )

        # Phare avant
        centre_phare = QPointF(
            x + w * 0.88,
            y + h * 0.48,
        )
        grad_phare = QRadialGradient(centre_phare, h * 0.05)
        grad_phare.setColorAt(0.0, QColor("#FFF7D1"))
        grad_phare.setColorAt(0.55, QColor("#EBCB7A"))
        grad_phare.setColorAt(1.0, QColor("#B28A3A"))
        painter.setBrush(QBrush(grad_phare))
        pen_phare = QPen(_assombrir("#B28A3A", 0.25))
        pen_phare.setWidthF(max(1.0, h * 0.007))
        painter.setPen(pen_phare)
        painter.drawEllipse(centre_phare, h * 0.030, h * 0.030)

        # Tampons avant
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_qcolor("#3B4045"))
        x_tampons = x + w * 0.885
        y_tampons = y + h * 0.64
        rayon_tampon = h * 0.018

        for dy in (-h * 0.025, h * 0.025):
            painter.drawEllipse(
                QPointF(x_tampons, y_tampons + dy),
                rayon_tampon,
                rayon_tampon,
            )

        # Roues
        rayon_grand = h * 0.125
        rayon_petit = h * 0.090
        y_roue = rect.bottom() - rayon_grand - h * 0.03

        c_arriere = QPointF(x + w * 0.24, y_roue)
        c_1 = QPointF(x + w * 0.49, y_roue)
        c_2 = QPointF(x + w * 0.69, y_roue)
        c_avant = QPointF(x + w * 0.86, rect.bottom() - rayon_petit - h * 0.04)

        self.roue.peindre(painter, c_arriere, rayon_petit, rotation_deg=angle_deg)
        self.roue.peindre(painter, c_1, rayon_grand, rotation_deg=angle_deg)
        self.roue.peindre(painter, c_2, rayon_grand, rotation_deg=angle_deg)
        self.roue.peindre(painter, c_avant, rayon_petit, rotation_deg=angle_deg)

        # Bielle motrice
        pin_r = rayon_grand * 0.55
        p1 = QPointF(
            c_1.x() + math.cos(theta) * pin_r,
            c_1.y() + math.sin(theta) * pin_r,
        )
        p2 = QPointF(
            c_2.x() + math.cos(theta) * pin_r,
            c_2.y() + math.sin(theta) * pin_r,
        )

        pen_bielle = QPen(QColor("#C9CED3"))
        pen_bielle.setWidthF(max(2.0, h * 0.015))
        pen_bielle.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bielle)
        painter.drawLine(p1, p2)

        painter.setBrush(QColor("#E2E7EB"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(p1, h * 0.018, h * 0.018)
        painter.drawEllipse(p2, h * 0.018, h * 0.018)

        # Attelage arrière vers le wagon
        pen_attelage = QPen(QColor("#42484D"))
        pen_attelage.setWidthF(max(1.8, h * 0.013))
        pen_attelage.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_attelage)
        y_attelage = y + h * 0.63
        painter.drawLine(
            QPointF(x + w * 0.04, y_attelage),
            QPointF(x + w * 0.12, y_attelage),
        )

        painter.restore()


# 5 -- Classe de train régional complet ----------------------------------------


class TrainRegional:
    """
    Assemble une motrice et une voiture régionale.

    Le train peut être utilisé :
        - avec motrice + wagon ;
        - avec wagon seul ;
        - en conservant des proportions fixes.
    """

    def __init__(
        self,
        avec_motrice: bool = True,
        nb_fenetres_wagon: int = 4,
        fenetres_wagon_allumees: list[bool] | None = None,
        nb_fenetres_motrice: int = 2,
        fenetres_motrice_allumees: list[bool] | None = None,
        couleur_caisse: QColor | str = "#7A2032",
        couleur_bandeau: QColor | str = "#E6DDCF",
        couleur_toit: QColor | str = "#58636B",
        couleur_bas: QColor | str = "#2A3035",
        couleur_bois: QColor | str = "#8A6445",
        couleur_filet: QColor | str = "#C9A86A",
    ):
        self.avec_motrice = avec_motrice

        self.wagon = VoitureRegionale(
            nb_fenetres=nb_fenetres_wagon,
            fenetres_allumees=fenetres_wagon_allumees,
            couleur_caisse=couleur_caisse,
            couleur_bandeau=couleur_bandeau,
            couleur_toit=couleur_toit,
            couleur_bas=couleur_bas,
            couleur_bois=couleur_bois,
            couleur_filet=couleur_filet,
        )

        self.motrice = MotriceRegionale(
            couleur_caisse=couleur_caisse,
            couleur_bandeau=couleur_bandeau,
            couleur_toit=couleur_toit,
            couleur_bas=couleur_bas,
            couleur_bois=couleur_bois,
            couleur_filet=couleur_filet,
        )

    def definir_fenetres_wagon(self, valeurs: list[bool]) -> None:
        """Met à jour les fenêtres du wagon."""
        self.wagon.definir_fenetres_allumees(valeurs)

    def definir_fenetres_motrice(self, valeurs: list[bool]) -> None:
        """Met à jour les fenêtres de la motrice."""
        self.motrice.definir_fenetres_allumees(valeurs)

    def largeur_recommandee(self) -> float:
        """Largeur recommandée du train complet."""
        if self.avec_motrice:
            return (
                self.wagon.largeur_recommandee()
                + self.motrice.largeur_recommandee()
                + 8
            )
        return self.wagon.largeur_recommandee()

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        sens: int = 1,
        phase_roues: float = 0.0,
    ) -> None:
        """
        Dessine le train complet.

        `sens = 1`  : le train regarde vers la droite
        `sens = -1` : symétrie horizontale complète
        `phase_roues` permet d'animer le roulement.
        """
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if sens < 0:
            painter.translate(rect.center().x(), 0)
            painter.scale(-1, 1)
            painter.translate(-rect.center().x(), 0)

        largeur_ref = self.largeur_recommandee()
        hauteur_ref = 140.0

        scale_x = rect.width() / largeur_ref
        scale_y = rect.height() / hauteur_ref
        echelle = min(scale_x, scale_y)

        largeur_utilisee = largeur_ref * echelle
        hauteur_utilisee = hauteur_ref * echelle

        x0 = rect.center().x() - largeur_utilisee / 2
        y0 = rect.center().y() - hauteur_utilisee / 2

        if self.avec_motrice:
            largeur_wagon = self.wagon.largeur_recommandee() * echelle
            largeur_motrice = self.motrice.largeur_recommandee() * echelle
            espace = 4 * echelle

            rect_wagon = QRectF(
                x0,
                y0,
                largeur_wagon,
                hauteur_utilisee,
            )

            rect_motrice = QRectF(
                rect_wagon.right() + espace - largeur_motrice * 0.075,
                y0,
                largeur_motrice,
                hauteur_utilisee,
            )

            # Wagon puis motrice : lecture visuelle bien plus claire
            self.wagon.peindre(painter, rect_wagon, phase_roues=phase_roues)
            self.motrice.peindre(
                painter,
                rect_motrice,
                sens=1,
                phase_roues=phase_roues,
            )

            # Attelage compact
            y_attelage = y0 + hauteur_utilisee * 0.63

            pen_attelage = QPen(QColor("#42484D"))
            pen_attelage.setWidthF(max(1.6, hauteur_utilisee * 0.012))
            pen_attelage.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_attelage)

            x_g = rect_wagon.right()
            x_d = rect_motrice.left()

            painter.drawLine(
                QPointF(x_g, y_attelage),
                QPointF(x_d, y_attelage),
            )

        else:
            self.wagon.peindre(
                painter,
                QRectF(x0, y0, largeur_utilisee, hauteur_utilisee),
                phase_roues=phase_roues,
            )

        painter.restore()
