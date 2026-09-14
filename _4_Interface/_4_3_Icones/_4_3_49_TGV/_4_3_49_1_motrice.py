################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones/_4_3_49_TGV                                         #
# 4.3.49.1 – Classe de création d'une motrice de TGV                           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

# 1 -- Classe de création d'une motrice TGV ------------------------------------


class MotriceTGV:
    """
    Dessine une motrice de TGV vue principalement de profil, avec une légère
    perspective verticale permettant de voir une partie du toit.

    La motrice peut être utilisée avec une rame classique ou Duplex. La
    différence porte essentiellement sur le raccord arrière avec les voitures.

    Paramètres
    ----------
    couleur_caisse : QColor | str
        Couleur principale de la carrosserie.

    couleur_secondaire : QColor | str
        Couleur utilisée pour le bandeau inférieur et certains détails.

    couleur_vitres : QColor | str
        Couleur des vitres de la cabine.

    couleur_toit : QColor | str | None
        Couleur de la partie supérieure. Si None, elle est dérivée de la caisse.

    duplex : bool
        Si True, adapte le raccord arrière à une voiture Duplex.

    pantographe : bool
        Affiche ou non le pantographe.

    feux : bool
        Affiche ou non les feux avant.
    """

    def __init__(
        self,
        couleur_caisse: QColor | str = "#E7E9E8",
        couleur_secondaire: QColor | str = "#59646A",
        couleur_vitres: QColor | str = "#314954",
        couleur_toit: QColor | str | None = None,
        duplex: bool = False,
        pantographe: bool = True,
        feux: bool = True,
    ):

        self.couleur_caisse = QColor(couleur_caisse)
        self.couleur_secondaire = QColor(couleur_secondaire)
        self.couleur_vitres = QColor(couleur_vitres)

        self.couleur_toit = (
            QColor(couleur_toit)
            if couleur_toit is not None
            else self.couleur_caisse.darker(108)
        )

        self.duplex = duplex
        self.pantographe = pantographe
        self.feux = feux

    # --------------------------------------------------------------------------
    # Dessin principal
    # --------------------------------------------------------------------------

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        sens: int = 1,
        perspective: float = 0.07,
        ombre: bool = True,
    ) -> None:
        """
        Dessine la motrice dans `rect`.

        sens
        ----
        1  : nez vers la droite.
        -1 : nez vers la gauche.

        perspective
        -----------
        Intensité de la vue légèrement plongeante.
        Une valeur autour de 0.05 à 0.10 fonctionne bien.
        """

        if rect.width() <= 0 or rect.height() <= 0:
            return

        perspective = max(0.0, min(float(perspective), 0.18))
        sens = 1 if sens >= 0 else -1

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Passage dans un système local : (0, 0) -> (largeur, hauteur)
        painter.translate(rect.left(), rect.top())

        if sens == -1:
            painter.translate(rect.width(), 0)
            painter.scale(-1, 1)

        largeur = rect.width()
        hauteur = rect.height()

        # Ombre générale sous la motrice
        if ombre:
            self._dessiner_ombre(
                painter=painter,
                largeur=largeur,
                hauteur=hauteur,
            )

        # Les bogies sont dessinés derrière la caisse
        self._dessiner_bogies(
            painter=painter,
            largeur=largeur,
            hauteur=hauteur,
        )

        # Partie du toit visible grâce à la perspective
        self._dessiner_toit(
            painter=painter,
            largeur=largeur,
            hauteur=hauteur,
            perspective=perspective,
        )

        # Caisse principale
        self._dessiner_caisse(
            painter=painter,
            largeur=largeur,
            hauteur=hauteur,
        )

        # Détails mécaniques et graphiques
        self._dessiner_bandeau_bas(painter, largeur, hauteur)
        self._dessiner_cabine(painter, largeur, hauteur)
        self._dessiner_porte(painter, largeur, hauteur)
        self._dessiner_grilles(painter, largeur, hauteur)
        self._dessiner_joint_arriere(painter, largeur, hauteur)

        if self.feux:
            self._dessiner_feux(painter, largeur, hauteur)

        if self.pantographe:
            self._dessiner_pantographe(
                painter=painter,
                largeur=largeur,
                hauteur=hauteur,
                perspective=perspective,
            )

        painter.restore()

    # --------------------------------------------------------------------------
    # Géométrie de la caisse
    # --------------------------------------------------------------------------

    def _chemin_caisse(
        self,
        largeur: float,
        hauteur: float,
    ) -> QPainterPath:

        # Le raccord arrière est plus haut avec une voiture Duplex.
        y_arriere = hauteur * (0.205 if self.duplex else 0.315)

        chemin = QPainterPath()

        # Raccord avec la rame
        chemin.moveTo(
            largeur * 0.035,
            y_arriere,
        )

        # Partie arrière du toit
        chemin.cubicTo(
            largeur * 0.080,
            y_arriere,
            largeur * 0.100,
            hauteur * 0.260,
            largeur * 0.170,
            hauteur * 0.250,
        )

        # Long toit presque horizontal
        chemin.cubicTo(
            largeur * 0.300,
            hauteur * 0.235,
            largeur * 0.500,
            hauteur * 0.240,
            largeur * 0.600,
            hauteur * 0.270,
        )

        # Début de la cabine
        chemin.cubicTo(
            largeur * 0.675,
            hauteur * 0.285,
            largeur * 0.735,
            hauteur * 0.335,
            largeur * 0.790,
            hauteur * 0.420,
        )

        # Descente du pare-brise vers le nez
        chemin.cubicTo(
            largeur * 0.845,
            hauteur * 0.500,
            largeur * 0.920,
            hauteur * 0.545,
            largeur * 0.975,
            hauteur * 0.585,
        )

        # Pointe du nez
        chemin.cubicTo(
            largeur * 0.995,
            hauteur * 0.600,
            largeur * 0.995,
            hauteur * 0.620,
            largeur * 0.975,
            hauteur * 0.640,
        )

        # Retour sous le nez
        chemin.cubicTo(
            largeur * 0.940,
            hauteur * 0.675,
            largeur * 0.900,
            hauteur * 0.705,
            largeur * 0.835,
            hauteur * 0.725,
        )

        # Bas de caisse
        chemin.lineTo(
            largeur * 0.090,
            hauteur * 0.750,
        )

        # Partie basse du raccord arrière
        chemin.quadTo(
            largeur * 0.040,
            hauteur * 0.750,
            largeur * 0.035,
            hauteur * 0.700,
        )

        chemin.closeSubpath()

        return chemin

    # --------------------------------------------------------------------------
    # Caisse
    # --------------------------------------------------------------------------

    def _dessiner_caisse(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        chemin = self._chemin_caisse(
            largeur=largeur,
            hauteur=hauteur,
        )

        degrade = QLinearGradient(
            0,
            hauteur * 0.20,
            0,
            hauteur * 0.76,
        )

        degrade.setColorAt(
            0.00,
            self.couleur_caisse.lighter(113),
        )
        degrade.setColorAt(
            0.38,
            self.couleur_caisse,
        )
        degrade.setColorAt(
            1.00,
            self.couleur_caisse.darker(112),
        )

        painter.setBrush(QBrush(degrade))
        painter.setPen(
            QPen(
                self.couleur_caisse.darker(145),
                max(1.0, hauteur * 0.008),
            )
        )

        painter.drawPath(chemin)

    # --------------------------------------------------------------------------
    # Toit et perspective
    # --------------------------------------------------------------------------

    def _dessiner_toit(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
        perspective: float,
    ) -> None:

        decalage_y = hauteur * perspective
        decalage_x = decalage_y * 0.30

        y_arriere = hauteur * (0.205 if self.duplex else 0.315)

        chemin = QPainterPath()

        # Ligne latérale du toit
        chemin.moveTo(
            largeur * 0.040,
            y_arriere,
        )

        # Ligne supérieure décalée par la perspective
        chemin.lineTo(
            largeur * 0.040 - decalage_x,
            y_arriere - decalage_y,
        )

        chemin.cubicTo(
            largeur * 0.150 - decalage_x,
            hauteur * 0.230 - decalage_y,
            largeur * 0.450 - decalage_x,
            hauteur * 0.220 - decalage_y,
            largeur * 0.600 - decalage_x,
            hauteur * 0.270 - decalage_y,
        )

        chemin.cubicTo(
            largeur * 0.680 - decalage_x,
            hauteur * 0.290 - decalage_y,
            largeur * 0.735 - decalage_x,
            hauteur * 0.330 - decalage_y,
            largeur * 0.790 - decalage_x,
            hauteur * 0.420 - decalage_y,
        )

        # Retour sur la ligne latérale
        chemin.lineTo(
            largeur * 0.790,
            hauteur * 0.420,
        )

        chemin.cubicTo(
            largeur * 0.735,
            hauteur * 0.335,
            largeur * 0.675,
            hauteur * 0.285,
            largeur * 0.600,
            hauteur * 0.270,
        )

        chemin.cubicTo(
            largeur * 0.450,
            hauteur * 0.230,
            largeur * 0.150,
            hauteur * 0.235,
            largeur * 0.040,
            y_arriere,
        )

        chemin.closeSubpath()

        painter.setPen(
            QPen(
                self.couleur_toit.darker(130),
                max(1.0, hauteur * 0.006),
            )
        )
        painter.setBrush(self.couleur_toit)

        painter.drawPath(chemin)

    # --------------------------------------------------------------------------
    # Bandeau inférieur
    # --------------------------------------------------------------------------

    def _dessiner_bandeau_bas(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        chemin = QPainterPath()

        chemin.moveTo(
            largeur * 0.070,
            hauteur * 0.665,
        )

        chemin.lineTo(
            largeur * 0.875,
            hauteur * 0.650,
        )

        chemin.cubicTo(
            largeur * 0.910,
            hauteur * 0.650,
            largeur * 0.935,
            hauteur * 0.630,
            largeur * 0.963,
            hauteur * 0.608,
        )

        chemin.cubicTo(
            largeur * 0.930,
            hauteur * 0.685,
            largeur * 0.880,
            hauteur * 0.715,
            largeur * 0.820,
            hauteur * 0.730,
        )

        chemin.lineTo(
            largeur * 0.080,
            hauteur * 0.750,
        )

        chemin.closeSubpath()

        couleur = QColor(self.couleur_secondaire)
        couleur.setAlpha(210)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(couleur)
        painter.drawPath(chemin)

    # --------------------------------------------------------------------------
    # Cabine
    # --------------------------------------------------------------------------

    def _dessiner_cabine(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        # Pare-brise latéral
        vitre = QPainterPath()

        vitre.moveTo(
            largeur * 0.690,
            hauteur * 0.315,
        )

        vitre.cubicTo(
            largeur * 0.725,
            hauteur * 0.320,
            largeur * 0.755,
            hauteur * 0.350,
            largeur * 0.790,
            hauteur * 0.415,
        )

        vitre.lineTo(
            largeur * 0.755,
            hauteur * 0.455,
        )

        vitre.cubicTo(
            largeur * 0.725,
            hauteur * 0.405,
            largeur * 0.700,
            hauteur * 0.375,
            largeur * 0.660,
            hauteur * 0.365,
        )

        vitre.closeSubpath()

        degrade = QLinearGradient(
            largeur * 0.68,
            hauteur * 0.32,
            largeur * 0.78,
            hauteur * 0.45,
        )

        degrade.setColorAt(
            0,
            self.couleur_vitres.lighter(135),
        )
        degrade.setColorAt(
            1,
            self.couleur_vitres.darker(130),
        )

        painter.setBrush(QBrush(degrade))
        painter.setPen(
            QPen(
                self.couleur_vitres.darker(170),
                max(1.0, hauteur * 0.009),
            )
        )

        painter.drawPath(vitre)

        # Reflet dans le pare-brise
        reflet = QPainterPath()

        reflet.moveTo(
            largeur * 0.690,
            hauteur * 0.330,
        )
        reflet.lineTo(
            largeur * 0.715,
            hauteur * 0.340,
        )
        reflet.lineTo(
            largeur * 0.755,
            hauteur * 0.395,
        )

        painter.setPen(
            QPen(
                QColor(255, 255, 255, 80),
                max(1.0, hauteur * 0.010),
            )
        )
        painter.drawPath(reflet)

    # --------------------------------------------------------------------------
    # Porte latérale
    # --------------------------------------------------------------------------

    def _dessiner_porte(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        rect_porte = QRectF(
            largeur * 0.570,
            hauteur * 0.345,
            largeur * 0.070,
            hauteur * 0.310,
        )

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(
            QPen(
                self.couleur_caisse.darker(135),
                max(1.0, hauteur * 0.006),
            )
        )

        painter.drawRoundedRect(
            rect_porte,
            hauteur * 0.012,
            hauteur * 0.012,
        )

        # Petite vitre
        rect_vitre = QRectF(
            largeur * 0.580,
            hauteur * 0.375,
            largeur * 0.050,
            hauteur * 0.095,
        )

        painter.setBrush(self.couleur_vitres.darker(110))
        painter.drawRoundedRect(
            rect_vitre,
            hauteur * 0.008,
            hauteur * 0.008,
        )

        # Poignée
        painter.setPen(
            QPen(
                self.couleur_secondaire.darker(130),
                max(1.0, hauteur * 0.007),
            )
        )

        painter.drawLine(
            QPointF(
                largeur * 0.625,
                hauteur * 0.515,
            ),
            QPointF(
                largeur * 0.625,
                hauteur * 0.550,
            ),
        )

    # --------------------------------------------------------------------------
    # Grilles techniques
    # --------------------------------------------------------------------------

    def _dessiner_grilles(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        positions = (
            (0.155, 0.355, 0.115, 0.180),
            (0.290, 0.355, 0.105, 0.180),
            (0.415, 0.365, 0.090, 0.165),
        )

        for x, y, w, h in positions:

            rect = QRectF(
                largeur * x,
                hauteur * y,
                largeur * w,
                hauteur * h,
            )

            self._dessiner_grille(
                painter=painter,
                rect=rect,
                hauteur_reference=hauteur,
            )

    def _dessiner_grille(
        self,
        painter: QPainter,
        rect: QRectF,
        hauteur_reference: float,
    ) -> None:

        fond = QColor(self.couleur_secondaire)
        fond.setAlpha(115)

        painter.setPen(
            QPen(
                self.couleur_secondaire.darker(135),
                max(1.0, hauteur_reference * 0.004),
            )
        )
        painter.setBrush(fond)

        painter.drawRoundedRect(
            rect,
            hauteur_reference * 0.008,
            hauteur_reference * 0.008,
        )

        painter.setPen(
            QPen(
                QColor(30, 35, 38, 115),
                max(1.0, hauteur_reference * 0.004),
            )
        )

        nombre_lames = 6

        for i in range(1, nombre_lames + 1):

            y = rect.top() + rect.height() * i / (nombre_lames + 1)

            painter.drawLine(
                QPointF(
                    rect.left() + rect.width() * 0.08,
                    y,
                ),
                QPointF(
                    rect.right() - rect.width() * 0.08,
                    y,
                ),
            )

    # --------------------------------------------------------------------------
    # Bogies et roues
    # --------------------------------------------------------------------------

    def _dessiner_bogies(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        for centre_x in (largeur * 0.235, largeur * 0.735):

            largeur_bogie = largeur * 0.150
            hauteur_bogie = hauteur * 0.075

            rect_bogie = QRectF(
                centre_x - largeur_bogie / 2,
                hauteur * 0.705,
                largeur_bogie,
                hauteur_bogie,
            )

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#34393D"))
            painter.drawRoundedRect(
                rect_bogie,
                hauteur * 0.018,
                hauteur * 0.018,
            )

            # Deux roues par bogie
            for decalage in (-largeur_bogie * 0.28, largeur_bogie * 0.28):

                centre_roue = QPointF(
                    centre_x + decalage,
                    hauteur * 0.770,
                )

                rayon = hauteur * 0.058

                painter.setBrush(QColor("#202427"))
                painter.drawEllipse(
                    centre_roue,
                    rayon,
                    rayon,
                )

                painter.setBrush(QColor("#667078"))
                painter.drawEllipse(
                    centre_roue,
                    rayon * 0.54,
                    rayon * 0.54,
                )

                painter.setBrush(QColor("#25292C"))
                painter.drawEllipse(
                    centre_roue,
                    rayon * 0.22,
                    rayon * 0.22,
                )

    # --------------------------------------------------------------------------
    # Pantographe
    # --------------------------------------------------------------------------

    def _dessiner_pantographe(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
        perspective: float,
    ) -> None:

        centre_x = largeur * 0.335

        y_base = hauteur * 0.245 - hauteur * perspective

        largeur_base = largeur * 0.105

        painter.setPen(
            QPen(
                QColor("#484C4F"),
                max(1.2, hauteur * 0.010),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )

        # Base
        painter.drawLine(
            QPointF(
                centre_x - largeur_base / 2,
                y_base,
            ),
            QPointF(
                centre_x + largeur_base / 2,
                y_base,
            ),
        )

        # Isolateurs
        for dx in (-largeur_base * 0.32, largeur_base * 0.32):

            painter.drawLine(
                QPointF(
                    centre_x + dx,
                    y_base,
                ),
                QPointF(
                    centre_x + dx,
                    y_base - hauteur * 0.035,
                ),
            )

        y_milieu = y_base - hauteur * 0.120
        y_haut = y_base - hauteur * 0.215

        largeur_milieu = largeur * 0.075
        largeur_haut = largeur * 0.095

        # Structure en losange
        painter.drawLine(
            QPointF(
                centre_x - largeur_base * 0.35,
                y_base - hauteur * 0.030,
            ),
            QPointF(
                centre_x + largeur_milieu / 2,
                y_milieu,
            ),
        )

        painter.drawLine(
            QPointF(
                centre_x + largeur_base * 0.35,
                y_base - hauteur * 0.030,
            ),
            QPointF(
                centre_x - largeur_milieu / 2,
                y_milieu,
            ),
        )

        painter.drawLine(
            QPointF(
                centre_x - largeur_milieu / 2,
                y_milieu,
            ),
            QPointF(
                centre_x + largeur_haut / 2,
                y_haut,
            ),
        )

        painter.drawLine(
            QPointF(
                centre_x + largeur_milieu / 2,
                y_milieu,
            ),
            QPointF(
                centre_x - largeur_haut / 2,
                y_haut,
            ),
        )

        # Archet supérieur
        painter.setPen(
            QPen(
                QColor("#2F3234"),
                max(1.4, hauteur * 0.012),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )

        painter.drawLine(
            QPointF(
                centre_x - largeur_haut * 0.75,
                y_haut,
            ),
            QPointF(
                centre_x + largeur_haut * 0.75,
                y_haut,
            ),
        )

    # --------------------------------------------------------------------------
    # Feux
    # --------------------------------------------------------------------------

    def _dessiner_feux(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        centre = QPointF(
            largeur * 0.931,
            hauteur * 0.595,
        )

        rayon = hauteur * 0.018

        # Halo
        halo = QColor("#FFF7C7")
        halo.setAlpha(80)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(halo)

        painter.drawEllipse(
            centre,
            rayon * 2.2,
            rayon * 2.2,
        )

        # Feu
        painter.setBrush(QColor("#FFF4B0"))

        painter.drawEllipse(
            centre,
            rayon,
            rayon,
        )

    # --------------------------------------------------------------------------
    # Raccord arrière
    # --------------------------------------------------------------------------

    def _dessiner_joint_arriere(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        y_haut = hauteur * (0.205 if self.duplex else 0.315)

        rect = QRectF(
            largeur * 0.018,
            y_haut + hauteur * 0.020,
            largeur * 0.028,
            hauteur * 0.440,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#292E31"))

        painter.drawRoundedRect(
            rect,
            hauteur * 0.008,
            hauteur * 0.008,
        )

    # --------------------------------------------------------------------------
    # Ombre
    # --------------------------------------------------------------------------

    def _dessiner_ombre(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        couleur = QColor(0, 0, 0, 50)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(couleur)

        painter.drawEllipse(
            QRectF(
                largeur * 0.065,
                hauteur * 0.795,
                largeur * 0.855,
                hauteur * 0.080,
            )
        )
