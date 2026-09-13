################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_4                                #
# Onglet 4.4.X – Brasero sur bloc de marbre                                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math
import random

from PyQt6.QtCore import (
    QObject,
    QPointF,
    QRectF,
    Qt,
    QTimer,
)

from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)

# 1 -- Classe du brasero -------------------------------------------------------


class BraseroMarbre(QObject):
    """
    Dessine un bloc de marbre surmonté d'une coupelle métallique.

    Une flamme animée peut être affichée dans la coupelle. L'objet n'est pas
    un QWidget : il se dessine directement dans le QPainter du widget parent.
    """

    INTERVALLE_ANIMATION_MS = 30

    def __init__(
        self,
        flamme: bool = True,
        couleur_marbre: str | QColor = "#D8D3C8",
        couleur_metal: str | QColor = "#3F3933",
        couleur_bronze: str | QColor = "#80684C",
        proportion_bloc_largeur: float = 0.72,
        proportion_bloc_hauteur: float = 0.40,
        graine: int = 42,
        parent=None,
    ):

        super().__init__(parent)

        self.flamme = flamme

        self.couleur_marbre = QColor(couleur_marbre)
        self.couleur_metal = QColor(couleur_metal)
        self.couleur_bronze = QColor(couleur_bronze)

        self.proportion_bloc_largeur = proportion_bloc_largeur
        self.proportion_bloc_hauteur = proportion_bloc_hauteur

        self.graine = graine

        # Animation
        self._phase = 0.0

        self._timer = QTimer(self)
        self._timer.setInterval(self.INTERVALLE_ANIMATION_MS)
        self._timer.timeout.connect(self._animer)

        # Étincelles : paramètres fixes pour éviter qu'elles changent
        # aléatoirement à chaque paintEvent.
        rng = random.Random(graine + 1000)

        self._etincelles = [
            {
                "x": rng.uniform(-0.42, 0.42),
                "phase": rng.random(),
                "vitesse": rng.uniform(0.50, 1.10),
                "taille": rng.uniform(0.55, 1.25),
                "oscillation": rng.uniform(0.7, 1.5),
            }
            for _ in range(11)
        ]

        if self.flamme:
            self._timer.start()

    # 2 -- Paramètres ----------------------------------------------------------

    def set_flamme(
        self,
        active: bool,
    ) -> None:
        """Active ou désactive la flamme."""

        self.flamme = active

        if active:
            if not self._timer.isActive():
                self._timer.start()
        else:
            self._timer.stop()

        self._demander_repaint()

    def set_couleur_marbre(
        self,
        couleur: str | QColor,
    ) -> None:

        self.couleur_marbre = QColor(couleur)
        self._demander_repaint()

    def set_couleur_metal(
        self,
        couleur: str | QColor,
    ) -> None:

        self.couleur_metal = QColor(couleur)
        self._demander_repaint()

    # 3 -- Animation -----------------------------------------------------------

    def _animer(self) -> None:
        """Fait évoluer la flamme et demande le repaint du widget parent."""

        self._phase = (self._phase + self.INTERVALLE_ANIMATION_MS / 1000) % 1000.0

        self._demander_repaint()

    def _demander_repaint(self) -> None:
        """Redessine le widget parent lorsqu'il possède une méthode update."""

        parent = self.parent()

        if parent is not None and hasattr(parent, "update"):
            parent.update()

    # 4 -- Utilitaires couleurs ------------------------------------------------

    @staticmethod
    def _melanger(
        couleur_1: QColor,
        couleur_2: QColor,
        poids: float,
    ) -> QColor:
        """Interpole deux couleurs."""

        poids = max(0.0, min(1.0, poids))

        return QColor(
            int(couleur_1.red() * (1 - poids) + couleur_2.red() * poids),
            int(couleur_1.green() * (1 - poids) + couleur_2.green() * poids),
            int(couleur_1.blue() * (1 - poids) + couleur_2.blue() * poids),
            int(couleur_1.alpha() * (1 - poids) + couleur_2.alpha() * poids),
        )

    @staticmethod
    def _avec_alpha(
        couleur: QColor,
        alpha: int,
    ) -> QColor:

        resultat = QColor(couleur)
        resultat.setAlpha(max(0, min(255, alpha)))

        return resultat

    # 5 -- Géométrie générale --------------------------------------------------

    def _geometrie(
        self,
        rect: QRectF,
    ) -> dict:
        """Calcule les zones du bloc, de la coupelle et de la flamme."""

        largeur_bloc = rect.width() * self.proportion_bloc_largeur

        hauteur_bloc = rect.height() * self.proportion_bloc_hauteur

        rect_bloc = QRectF(
            rect.center().x() - largeur_bloc / 2,
            rect.bottom() - hauteur_bloc,
            largeur_bloc,
            hauteur_bloc,
        )

        largeur_coupelle = rect.width() * 0.50
        hauteur_coupelle = rect.height() * 0.115

        rect_coupelle = QRectF(
            rect.center().x() - largeur_coupelle / 2,
            rect_bloc.top() - hauteur_coupelle * 0.57,
            largeur_coupelle,
            hauteur_coupelle,
        )

        hauteur_flamme = rect.height() * 0.39

        rect_flamme = QRectF(
            rect.center().x() - largeur_coupelle * 0.43,
            rect_coupelle.top() - hauteur_flamme * 0.89,
            largeur_coupelle * 0.86,
            hauteur_flamme,
        )

        return {
            "bloc": rect_bloc,
            "coupelle": rect_coupelle,
            "flamme": rect_flamme,
        }

    # 6 -- Bloc de marbre ------------------------------------------------------

    def _geometrie_bloc(
        self,
        rect: QRectF,
        point_fuite_x: float,
    ) -> dict:
        """
        Calcule les trois faces du bloc en orientant la perspective vers
        le point de fuite.
        """

        profondeur_max = min(
            rect.width() * 0.075,
            rect.height() * 0.12,
        )

        distance = point_fuite_x - rect.center().x()

        reference = max(
            rect.width() * 2.5,
            1.0,
        )

        intensite = max(
            -1.0,
            min(1.0, distance / reference),
        )

        # Le bloc central est quasiment vu de face ; plus il est éloigné
        # du centre, plus sa profondeur latérale devient visible.
        decalage_x = profondeur_max * intensite * 2.3

        hauteur_dessus = min(
            rect.height() * 0.12,
            profondeur_max * 0.85,
        )

        profondeur_visible = abs(decalage_x)

        if decalage_x >= 0:

            rect_face = QRectF(
                rect.left(),
                rect.top() + hauteur_dessus,
                rect.width() - profondeur_visible,
                rect.height() - hauteur_dessus,
            )

        else:

            rect_face = QRectF(
                rect.left() + profondeur_visible,
                rect.top() + hauteur_dessus,
                rect.width() - profondeur_visible,
                rect.height() - hauteur_dessus,
            )

        dessus = QPainterPath()

        dessus.moveTo(
            QPointF(
                rect_face.left(),
                rect_face.top(),
            )
        )

        dessus.lineTo(
            QPointF(
                rect_face.left() + decalage_x,
                rect.top(),
            )
        )

        dessus.lineTo(
            QPointF(
                rect_face.right() + decalage_x,
                rect.top(),
            )
        )

        dessus.lineTo(
            QPointF(
                rect_face.right(),
                rect_face.top(),
            )
        )

        dessus.closeSubpath()

        cote = QPainterPath()

        if decalage_x > 0:

            cote.moveTo(
                QPointF(
                    rect_face.right(),
                    rect_face.top(),
                )
            )

            cote.lineTo(
                QPointF(
                    rect_face.right() + decalage_x,
                    rect.top(),
                )
            )

            cote.lineTo(
                QPointF(
                    rect_face.right() + decalage_x,
                    rect.bottom() - hauteur_dessus,
                )
            )

            cote.lineTo(
                QPointF(
                    rect_face.right(),
                    rect.bottom(),
                )
            )

        elif decalage_x < 0:

            cote.moveTo(
                QPointF(
                    rect_face.left(),
                    rect_face.top(),
                )
            )

            cote.lineTo(
                QPointF(
                    rect_face.left() + decalage_x,
                    rect.top(),
                )
            )

            cote.lineTo(
                QPointF(
                    rect_face.left() + decalage_x,
                    rect.bottom() - hauteur_dessus,
                )
            )

            cote.lineTo(
                QPointF(
                    rect_face.left(),
                    rect.bottom(),
                )
            )

        cote.closeSubpath()

        return {
            "face": rect_face,
            "dessus": dessus,
            "cote": cote,
            "profondeur": profondeur_visible,
        }

    def _dessiner_bloc(
        self,
        painter: QPainter,
        rect: QRectF,
        point_fuite_x: float,
    ) -> None:
        """Dessine le bloc de marbre et ses veines."""

        geometrie = self._geometrie_bloc(
            rect=rect,
            point_fuite_x=point_fuite_x,
        )

        face = geometrie["face"]

        marbre_clair = self._melanger(
            self.couleur_marbre,
            QColor("#FFFFFF"),
            0.30,
        )

        marbre_ombre = self._melanger(
            self.couleur_marbre,
            QColor("#4F4A45"),
            0.34,
        )

        # Face avant
        degrade = QLinearGradient(
            face.left(),
            face.top(),
            face.right(),
            face.bottom(),
        )

        degrade.setColorAt(
            0.0,
            marbre_clair,
        )

        degrade.setColorAt(
            0.45,
            self.couleur_marbre,
        )

        degrade.setColorAt(
            1.0,
            marbre_ombre,
        )

        painter.setPen(
            QPen(
                self._avec_alpha(
                    marbre_ombre,
                    155,
                ),
                0.8,
            )
        )

        painter.setBrush(QBrush(degrade))

        painter.drawRect(face)

        # Dessus
        painter.setBrush(
            self._melanger(
                self.couleur_marbre,
                QColor("#FFFFFF"),
                0.42,
            )
        )

        painter.drawPath(geometrie["dessus"])

        # Côté visible
        if geometrie["profondeur"] > 0.5:

            painter.setBrush(
                self._melanger(
                    self.couleur_marbre,
                    QColor("#5A554E"),
                    0.30,
                )
            )

            painter.drawPath(geometrie["cote"])

        self._dessiner_marbrures(
            painter=painter,
            rect=face,
        )

        # Arête supérieure
        couleur_lumiere = self._melanger(
            self.couleur_marbre,
            QColor("#FFFFFF"),
            0.65,
        )

        painter.setPen(
            QPen(
                self._avec_alpha(
                    couleur_lumiere,
                    170,
                ),
                0.9,
            )
        )

        painter.drawLine(
            face.topLeft(),
            face.topRight(),
        )

    def _dessiner_marbrures(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Ajoute des veines minérales irrégulières au marbre."""

        rng = random.Random(self.graine)

        painter.save()
        painter.setClipRect(rect)

        for i in range(11):

            x = rng.uniform(
                rect.left() - rect.width() * 0.15,
                rect.right() - rect.width() * 0.30,
            )

            y = rng.uniform(
                rect.top(),
                rect.bottom(),
            )

            longueur = rng.uniform(
                rect.width() * 0.35,
                rect.width() * 0.85,
            )

            direction = rng.choice((-1, 1))

            hauteur = direction * rng.uniform(
                rect.height() * 0.10,
                rect.height() * 0.45,
            )

            chemin = QPainterPath(QPointF(x, y))

            chemin.cubicTo(
                QPointF(
                    x + longueur * 0.25,
                    y + hauteur * 0.10 + rng.uniform(-10, 10),
                ),
                QPointF(
                    x + longueur * 0.65,
                    y + hauteur * 0.85 + rng.uniform(-10, 10),
                ),
                QPointF(
                    x + longueur,
                    y + hauteur,
                ),
            )

            couleur = self._melanger(
                self.couleur_marbre,
                QColor("#66615C"),
                rng.uniform(0.40, 0.65),
            )

            couleur.setAlpha(rng.randint(22, 55))

            painter.setPen(
                QPen(
                    couleur,
                    rng.uniform(0.4, 1.3),
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                )
            )

            painter.drawPath(chemin)

        painter.restore()

    # 7 -- Support de la coupelle ----------------------------------------------

    def _dessiner_support(
        self,
        painter: QPainter,
        rect_coupelle: QRectF,
    ) -> None:
        """Dessine le petit pied métallique reliant la coupelle au marbre."""

        cx = rect_coupelle.center().x()

        hauteur = rect_coupelle.height() * 0.52
        largeur = rect_coupelle.width() * 0.12

        y_haut = rect_coupelle.center().y()
        y_bas = y_haut + hauteur

        degrade = QLinearGradient(
            cx - largeur / 2,
            0,
            cx + largeur / 2,
            0,
        )

        degrade.setColorAt(
            0.0,
            self._melanger(
                self.couleur_metal,
                QColor("#000000"),
                0.35,
            ),
        )

        degrade.setColorAt(
            0.42,
            self._melanger(
                self.couleur_bronze,
                QColor("#FFFFFF"),
                0.18,
            ),
        )

        degrade.setColorAt(
            1.0,
            self._melanger(
                self.couleur_metal,
                QColor("#000000"),
                0.48,
            ),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade)

        painter.drawRoundedRect(
            QRectF(
                cx - largeur / 2,
                y_haut,
                largeur,
                hauteur,
            ),
            largeur * 0.18,
            largeur * 0.18,
        )

        # Pied
        painter.drawEllipse(
            QRectF(
                cx - largeur * 1.20,
                y_bas - largeur * 0.22,
                largeur * 2.40,
                largeur * 0.55,
            )
        )

    # 8 -- Coupelle métallique -------------------------------------------------

    def _dessiner_coupelle(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine une coupelle lourde en bronze / métal sombre."""

        cx = rect.center().x()
        cy = rect.center().y()

        largeur = rect.width()
        hauteur = rect.height()

        # Corps inférieur de la coupelle
        corps = QPainterPath()

        corps.moveTo(
            QPointF(
                rect.left() + largeur * 0.05,
                cy,
            )
        )

        corps.cubicTo(
            QPointF(
                rect.left() + largeur * 0.13,
                rect.bottom() - hauteur * 0.05,
            ),
            QPointF(
                rect.right() - largeur * 0.13,
                rect.bottom() - hauteur * 0.05,
            ),
            QPointF(
                rect.right() - largeur * 0.05,
                cy,
            ),
        )

        corps.closeSubpath()

        degrade_corps = QLinearGradient(
            rect.left(),
            0,
            rect.right(),
            0,
        )

        degrade_corps.setColorAt(
            0.0,
            self._melanger(
                self.couleur_metal,
                QColor("#000000"),
                0.42,
            ),
        )

        degrade_corps.setColorAt(
            0.24,
            self.couleur_bronze,
        )

        degrade_corps.setColorAt(
            0.48,
            self._melanger(
                self.couleur_bronze,
                QColor("#E4CC9A"),
                0.16,
            ),
        )

        degrade_corps.setColorAt(
            0.72,
            self.couleur_metal,
        )

        degrade_corps.setColorAt(
            1.0,
            QColor("#211F1D"),
        )

        painter.setPen(
            QPen(
                QColor("#211F1D"),
                max(0.8, largeur * 0.008),
            )
        )

        painter.setBrush(QBrush(degrade_corps))

        painter.drawPath(corps)

        # Rebord épais
        rect_rebord = QRectF(
            rect.left(),
            rect.top() + hauteur * 0.18,
            largeur,
            hauteur * 0.36,
        )

        degrade_rebord = QLinearGradient(
            rect_rebord.left(),
            0,
            rect_rebord.right(),
            0,
        )

        degrade_rebord.setColorAt(
            0.0,
            QColor("#262321"),
        )

        degrade_rebord.setColorAt(
            0.35,
            self._melanger(
                self.couleur_bronze,
                QColor("#FFFFFF"),
                0.22,
            ),
        )

        degrade_rebord.setColorAt(
            0.62,
            self.couleur_bronze,
        )

        degrade_rebord.setColorAt(
            1.0,
            QColor("#211F1C"),
        )

        painter.setBrush(QBrush(degrade_rebord))

        painter.drawEllipse(rect_rebord)

        # Intérieur très sombre
        rect_interieur = rect_rebord.adjusted(
            largeur * 0.055,
            hauteur * 0.06,
            -largeur * 0.055,
            -hauteur * 0.06,
        )

        interieur = QRadialGradient(
            rect_interieur.center(),
            rect_interieur.width() / 2,
        )

        if self.flamme:

            interieur.setColorAt(
                0.0,
                QColor(115, 49, 15),
            )

            interieur.setColorAt(
                0.38,
                QColor(51, 29, 20),
            )

        else:

            interieur.setColorAt(
                0.0,
                QColor("#302B27"),
            )

        interieur.setColorAt(
            1.0,
            QColor("#11100F"),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(interieur)

        painter.drawEllipse(rect_interieur)

        # Reflet métallique sur le bord avant
        painter.setPen(
            QPen(
                QColor(208, 182, 135, 90),
                max(1.0, hauteur * 0.055),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )

        painter.drawArc(
            rect_rebord.adjusted(
                largeur * 0.055,
                hauteur * 0.055,
                -largeur * 0.055,
                -hauteur * 0.055,
            ),
            205 * 16,
            125 * 16,
        )

    # 9 -- Flamme : géométrie --------------------------------------------------

    def _chemin_flamme(
        self,
        rect: QRectF,
        hauteur: float,
        largeur: float,
        decalage_x: float,
        phase: float,
        nervosite: float,
    ) -> QPainterPath:
        """Crée une forme organique de flamme."""

        cx = rect.center().x() + decalage_x

        y_bas = rect.bottom()

        oscillation_1 = math.sin(phase * 5.8) * largeur * 0.09 * nervosite

        oscillation_2 = math.sin(phase * 9.1 + 1.4) * largeur * 0.055 * nervosite

        tip_x = cx + oscillation_1 + oscillation_2

        tip_y = y_bas - hauteur * (0.94 + 0.045 * math.sin(phase * 7.3))

        chemin = QPainterPath()

        chemin.moveTo(
            QPointF(
                cx,
                y_bas,
            )
        )

        # Bord gauche
        chemin.cubicTo(
            QPointF(
                cx - largeur * 0.48,
                y_bas - hauteur * 0.17,
            ),
            QPointF(
                cx - largeur * 0.43 + oscillation_1 * 0.30,
                y_bas - hauteur * 0.53,
            ),
            QPointF(
                tip_x,
                tip_y,
            ),
        )

        # Bord droit
        chemin.cubicTo(
            QPointF(
                cx + largeur * 0.31 + oscillation_2 * 0.50,
                y_bas - hauteur * 0.67,
            ),
            QPointF(
                cx + largeur * 0.55,
                y_bas - hauteur * 0.21,
            ),
            QPointF(
                cx,
                y_bas,
            ),
        )

        chemin.closeSubpath()

        return chemin

    # 10 -- Halo lumineux ------------------------------------------------------

    def _dessiner_halo(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine la lumière chaude diffusée autour de la flamme."""

        pulsation = 0.88 + 0.12 * math.sin(self._phase * 8.2)

        rayon = rect.width() * 0.75 * pulsation

        centre = QPointF(
            rect.center().x(),
            rect.bottom() - rect.height() * 0.32,
        )

        halo = QRadialGradient(
            centre,
            rayon,
        )

        halo.setColorAt(
            0.0,
            QColor(255, 177, 68, 65),
        )

        halo.setColorAt(
            0.40,
            QColor(255, 113, 31, 30),
        )

        halo.setColorAt(
            1.0,
            QColor(255, 90, 20, 0),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(halo)

        painter.drawEllipse(
            centre,
            rayon,
            rayon,
        )

    # 11 -- Flammes secondaires -----------------------------------------------

    def _dessiner_langue(
        self,
        painter: QPainter,
        rect: QRectF,
        decalage: float,
        hauteur: float,
        largeur: float,
        phase: float,
    ) -> None:
        """Dessine une petite langue de feu latérale."""

        chemin = self._chemin_flamme(
            rect=rect,
            hauteur=hauteur,
            largeur=largeur,
            decalage_x=decalage,
            phase=phase,
            nervosite=1.4,
        )

        degrade = QLinearGradient(
            0,
            rect.bottom(),
            0,
            rect.bottom() - hauteur,
        )

        degrade.setColorAt(
            0.0,
            QColor(255, 186, 44, 210),
        )

        degrade.setColorAt(
            0.55,
            QColor(255, 94, 18, 190),
        )

        degrade.setColorAt(
            1.0,
            QColor(210, 42, 8, 40),
        )

        painter.setBrush(degrade)
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawPath(chemin)

    # 12 -- Flamme principale --------------------------------------------------

    def _dessiner_flamme(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine une flamme multicouche avec halo et étincelles."""

        self._dessiner_halo(
            painter=painter,
            rect=rect,
        )

        cx = rect.center().x()
        hauteur = rect.height()
        largeur = rect.width()

        # Langues secondaires
        self._dessiner_langue(
            painter=painter,
            rect=rect,
            decalage=-largeur * 0.20,
            hauteur=hauteur * 0.52,
            largeur=largeur * 0.30,
            phase=self._phase + 1.3,
        )

        self._dessiner_langue(
            painter=painter,
            rect=rect,
            decalage=largeur * 0.21,
            hauteur=hauteur * 0.45,
            largeur=largeur * 0.27,
            phase=self._phase + 2.8,
        )

        # Flamme extérieure
        chemin_exterieur = self._chemin_flamme(
            rect=rect,
            hauteur=hauteur * 0.91,
            largeur=largeur * 0.53,
            decalage_x=0,
            phase=self._phase,
            nervosite=1.0,
        )

        degrade_exterieur = QLinearGradient(
            0,
            rect.bottom(),
            0,
            rect.top(),
        )

        degrade_exterieur.setColorAt(
            0.0,
            QColor("#FFB11F"),
        )

        degrade_exterieur.setColorAt(
            0.34,
            QColor("#FF7417"),
        )

        degrade_exterieur.setColorAt(
            0.70,
            QColor("#E8420D"),
        )

        degrade_exterieur.setColorAt(
            1.0,
            QColor(183, 31, 5, 80),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade_exterieur)

        painter.drawPath(chemin_exterieur)

        # Flamme intermédiaire
        chemin_milieu = self._chemin_flamme(
            rect=rect,
            hauteur=hauteur * 0.67,
            largeur=largeur * 0.38,
            decalage_x=largeur * 0.025 * math.sin(self._phase * 4.7),
            phase=self._phase + 0.65,
            nervosite=0.82,
        )

        degrade_milieu = QLinearGradient(
            0,
            rect.bottom(),
            0,
            rect.bottom() - hauteur * 0.67,
        )

        degrade_milieu.setColorAt(
            0.0,
            QColor("#FFF08A"),
        )

        degrade_milieu.setColorAt(
            0.38,
            QColor("#FFD735"),
        )

        degrade_milieu.setColorAt(
            0.77,
            QColor("#FF9222"),
        )

        degrade_milieu.setColorAt(
            1.0,
            QColor(255, 108, 18, 60),
        )

        painter.setBrush(degrade_milieu)

        painter.drawPath(chemin_milieu)

        # Cœur clair
        chemin_coeur = self._chemin_flamme(
            rect=rect,
            hauteur=hauteur * 0.42,
            largeur=largeur * 0.22,
            decalage_x=-largeur * 0.02,
            phase=self._phase + 1.7,
            nervosite=0.55,
        )

        degrade_coeur = QLinearGradient(
            0,
            rect.bottom(),
            0,
            rect.bottom() - hauteur * 0.42,
        )

        degrade_coeur.setColorAt(
            0.0,
            QColor("#FFFDE2"),
        )

        degrade_coeur.setColorAt(
            0.35,
            QColor("#FFF5A7"),
        )

        degrade_coeur.setColorAt(
            0.78,
            QColor("#FFD84D"),
        )

        degrade_coeur.setColorAt(
            1.0,
            QColor(255, 190, 49, 25),
        )

        painter.setBrush(degrade_coeur)

        painter.drawPath(chemin_coeur)

        self._dessiner_etincelles(
            painter=painter,
            rect=rect,
        )

    # 13 -- Étincelles ---------------------------------------------------------

    def _dessiner_etincelles(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine quelques particules incandescentes au-dessus du brasier."""

        painter.setPen(Qt.PenStyle.NoPen)

        for i, etincelle in enumerate(self._etincelles):

            progression = (
                etincelle["phase"] + self._phase * etincelle["vitesse"]
            ) % 1.0

            # Les étincelles apparaissent près de la flamme puis montent.
            y = rect.bottom() - rect.height() * (0.30 + progression * 0.90)

            oscillation = (
                math.sin(self._phase * 5.0 * etincelle["oscillation"] + i)
                * rect.width()
                * 0.055
            )

            x = rect.center().x() + etincelle["x"] * rect.width() * 0.58 + oscillation

            alpha = int(220 * (1 - progression) ** 1.4)

            rayon = (
                max(
                    0.7,
                    rect.width() * 0.012,
                )
                * etincelle["taille"]
                * (1 - progression * 0.45)
            )

            couleur = QColor(
                255,
                int(195 + 45 * (1 - progression)),
                70,
                alpha,
            )

            painter.setBrush(couleur)

            painter.drawEllipse(
                QPointF(x, y),
                rayon,
                rayon,
            )

    # 14 -- Dessin principal ---------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        rect: QRectF,
        point_fuite_x: float | None = None,
    ) -> None:
        """Dessine le bloc de marbre, la coupelle et l'éventuelle flamme."""

        if rect.width() <= 0 or rect.height() <= 0:
            return

        if point_fuite_x is None:
            point_fuite_x = rect.center().x()

        geometrie = self._geometrie(
            rect=rect,
        )

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        # Bloc de marbre
        self._dessiner_bloc(
            painter=painter,
            rect=geometrie["bloc"],
            point_fuite_x=point_fuite_x,
        )

        # Petit support métallique
        self._dessiner_support(
            painter=painter,
            rect_coupelle=geometrie["coupelle"],
        )

        # La flamme passe derrière le bord avant de la coupelle.
        if self.flamme:

            self._dessiner_flamme(
                painter=painter,
                rect=geometrie["flamme"],
            )

        # Coupelle au premier plan
        self._dessiner_coupelle(
            painter=painter,
            rect=geometrie["coupelle"],
        )

        painter.restore()
