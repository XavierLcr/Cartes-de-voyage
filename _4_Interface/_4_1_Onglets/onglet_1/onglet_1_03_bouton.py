################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1.03 – Bouton de création des cartes                                  #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import (
    Qt,
    QRectF,
    QPointF,
    QVariantAnimation,
    QEasingCurve,
)
from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QLinearGradient,
    QRadialGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from math import cos, sin

# Dimensions logiques de l'illustration (presse + feuille).
LARGEUR_ILLUSTRATION = 102.0
HAUTEUR_ILLUSTRATION = 58.0

# Course maximale de la platine lorsque la presse imprime.
COURSE_PLATINE = 4.6

# Palette de l'illustration.
BOIS_LUMIERE = QColor("#D9BC95")
BOIS_CLAIR = QColor("#BE9C73")
BOIS = QColor("#A07C58")
BOIS_FONCE = QColor("#6A4B33")

METAL_LUMIERE = QColor("#E3E8E1")
METAL_CLAIR = QColor("#B3BEB7")
METAL = QColor("#7F8E86")
METAL_OMBRE = QColor("#4F5D57")

PAPIER_CLAIR = QColor("#FFFEF8")
PAPIER = QColor("#F1ECDD")
PAPIER_CONTOUR = QColor("#C9BCA4")

ENCRE = QColor("#3F6B63")
MER = QColor("#DCE9E8")
TERRE = QColor("#E6E8D2")
ROUTE = QColor("#C2674A")


# 1 -- Outils ------------------------------------------------------------------


def _borner(valeur: float, mini: float = 0.0, maxi: float = 1.0) -> float:
    return max(mini, min(maxi, valeur))


def _lisser(u: float) -> float:
    """Interpolation douce (smoothstep) entre 0 et 1."""
    u = _borner(u)
    return u * u * (3.0 - 2.0 * u)


def _melanger(c1: QColor, c2: QColor, t: float) -> QColor:
    """Mélange linéaire de deux couleurs (t = 0 → c1, t = 1 → c2)."""
    t = _borner(t)
    return QColor(
        round(c1.red() + (c2.red() - c1.red()) * t),
        round(c1.green() + (c2.green() - c1.green()) * t),
        round(c1.blue() + (c2.blue() - c1.blue()) * t),
        round(c1.alpha() + (c2.alpha() - c1.alpha()) * t),
    )


def _degrade(x0, y0, x1, y1, *couleurs) -> QLinearGradient:
    """Dégradé linéaire régulièrement réparti entre les couleurs données."""
    degrade = QLinearGradient(x0, y0, x1, y1)
    n = len(couleurs) - 1
    for i, couleur in enumerate(couleurs):
        degrade.setColorAt(i / n, couleur)
    return degrade


def _degrade_vertical(rect: QRectF, *couleurs) -> QLinearGradient:
    return _degrade(0, rect.top(), 0, rect.bottom(), *couleurs)


def _degrade_horizontal(rect: QRectF, *couleurs) -> QLinearGradient:
    return _degrade(rect.left(), 0, rect.right(), 0, *couleurs)


def _etat_impression(t: float):
    """
    Chorégraphie de l'impression (t de 0 à 1).

    Retourne (enfoncement de la platine, opacité de la feuille,
    décalage x, décalage y de la feuille). À t = 0 comme à t = 1, tout est au
    repos : la presse est relevée et la feuille est à sa place.
    """
    # Platine : descend, marque une pause, puis remonte.
    if t < 0.08:
        platine = 0.0
    elif t < 0.36:
        platine = _lisser((t - 0.08) / 0.28)
    elif t < 0.48:
        platine = 1.0
    elif t < 0.78:
        platine = 1.0 - _lisser((t - 0.48) / 0.30)
    else:
        platine = 0.0

    # Feuille : l'ancienne est retirée, puis la nouvelle apparaît.
    if t < 0.36:
        opacite, dx, dy = 1.0, 0.0, 0.0
    elif t < 0.50:
        u = _lisser((t - 0.36) / 0.14)
        opacite, dx, dy = 1.0 - u, 7.0 * u, 0.0
    elif t < 0.60:
        opacite, dx, dy = 0.0, 0.0, 0.0
    else:
        u = _lisser((t - 0.60) / 0.40)
        opacite, dx, dy = u, 0.0, 4.0 * (1.0 - u)

    return platine, opacite, dx, dy


# 2 -- Bouton ------------------------------------------------------------------


class BoutonCreationCartes(QPushButton):
    """
    Bouton évoquant une presse cartographique ancienne.

    Une presse à vis en bois imprime une feuille d'atlas. Tout est dessiné dans
    paintEvent, dans un repère logique unique (aucun trait ultra-fin) pour que
    l'illustration reste nette à toutes les tailles :

    - au survol, la vis tourne légèrement et la platine s'abaisse un peu ;
    - au clic, la presse fait un cycle complet et sort une nouvelle feuille.
    """

    def __init__(
        self,
        fonction_traduction=None,
        parent=None,
    ):
        super().__init__(parent)

        self.fonction_traduction = fonction_traduction

        self.setMinimumWidth(280)
        self.setFixedHeight(76)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Créer les cartes de voyage")

        self._survol = 0.0
        self._impression = 0.0
        self._enfonce = False

        self._animation_survol = QVariantAnimation(self)
        self._animation_survol.setDuration(210)
        self._animation_survol.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation_survol.valueChanged.connect(self._mettre_a_jour_survol)

        self._animation_impression = QVariantAnimation(self)
        self._animation_impression.setDuration(900)
        self._animation_impression.setStartValue(0.0)
        self._animation_impression.setEndValue(1.0)
        self._animation_impression.setEasingCurve(QEasingCurve.Type.Linear)
        self._animation_impression.valueChanged.connect(self._mettre_a_jour_impression)

        self.clicked.connect(self._lancer_impression)

        # Le QPushButton natif ne dessine rien : tout est rendu dans paintEvent.
        self.setFlat(True)
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)

        if self.fonction_traduction is not None:
            self.set_langue()
        else:
            self.setText("Créer les cartes")

    # --------------------------------------------------------------------------
    # Langue
    # --------------------------------------------------------------------------

    def set_langue(self):
        """Met à jour le libellé et l'infobulle avec les clés de l'application."""
        if self.fonction_traduction is None:
            return

        self.setText(self.fonction_traduction("bouton_publier_cartes"))
        self.setToolTip(self.fonction_traduction("description_bouton_publier_cartes"))

    # --------------------------------------------------------------------------
    # Animations
    # --------------------------------------------------------------------------

    def _mettre_a_jour_survol(self, valeur):
        self._survol = float(valeur)
        self.update()

    def _animer_survol(self, destination: float):
        self._animation_survol.stop()
        self._animation_survol.setStartValue(self._survol)
        self._animation_survol.setEndValue(destination)
        self._animation_survol.start()

    def _mettre_a_jour_impression(self, valeur):
        self._impression = float(valeur)
        self.update()

    def _lancer_impression(self):
        """Cycle d'impression : la presse descend, remonte, une feuille sort."""
        self._animation_impression.stop()
        self._animation_impression.start()

    # --------------------------------------------------------------------------
    # Événements souris
    # --------------------------------------------------------------------------

    def enterEvent(self, event):
        if self.isEnabled():
            self._animer_survol(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animer_survol(0.0)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._enfonce = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._enfonce = False
        self.update()
        super().mouseReleaseEvent(event)

    def changeEvent(self, event):
        super().changeEvent(event)
        if not self.isEnabled():
            self._enfonce = False
            self._animer_survol(0.0)

    # --------------------------------------------------------------------------
    # Dessin de la presse
    # --------------------------------------------------------------------------

    def _dessiner_presse(
        self,
        painter: QPainter,
        profondeur: float,
        angle: float,
    ) -> None:
        """
        Presse à vis, vue de face.

        profondeur : 0 = platine relevée, 1 = platine appuyée sur le papier.
        angle      : orientation de la barre de manœuvre autour de la vis.
        """
        d = COURSE_PLATINE * profondeur
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)

        # Ombre portée au sol.
        painter.setBrush(QColor(55, 45, 32, 38))
        painter.drawEllipse(QRectF(2, 52.5, 72, 5))

        # Socle.
        socle = QRectF(3, 46, 68, 8)
        painter.setPen(QPen(BOIS_FONCE, 0.9))
        painter.setBrush(_degrade_vertical(socle, BOIS_CLAIR, BOIS))
        painter.drawRoundedRect(socle, 2, 2)
        painter.setPen(QPen(BOIS_LUMIERE, 0.8))
        painter.drawLine(QPointF(5.5, 47.4), QPointF(68.5, 47.4))

        # Montants.
        for x in (11, 56):
            montant = QRectF(x, 19, 7, 28)
            painter.setPen(QPen(BOIS_FONCE, 0.9))
            painter.setBrush(
                _degrade_horizontal(montant, BOIS_LUMIERE, BOIS_CLAIR, BOIS)
            )
            painter.drawRect(montant)

        # Table de marbre (là où repose la feuille) et papier à imprimer.
        table = QRectF(18, 41, 38, 5)
        painter.setPen(QPen(METAL_OMBRE, 0.8))
        painter.setBrush(_degrade_vertical(table, METAL_CLAIR, METAL))
        painter.drawRect(table)
        painter.setPen(QPen(PAPIER_CONTOUR, 0.6))
        painter.setBrush(PAPIER_CLAIR)
        painter.drawRect(QRectF(22, 39.6, 30, 1.4))

        # Traverse supérieure.
        traverse = QRectF(7, 10, 56, 10)
        painter.setPen(QPen(BOIS_FONCE, 1.0))
        painter.setBrush(_degrade_vertical(traverse, BOIS_CLAIR, BOIS))
        painter.drawRoundedRect(traverse, 2.2, 2.2)
        painter.setPen(QPen(BOIS_LUMIERE, 0.9))
        painter.drawLine(QPointF(9.5, 11.6), QPointF(60.5, 11.6))
        painter.setPen(QPen(QColor(106, 75, 51, 120), 0.8))
        painter.drawLine(QPointF(9.5, 18.6), QPointF(60.5, 18.6))

        # Boulons de la traverse.
        painter.setPen(QPen(METAL_OMBRE, 0.7))
        painter.setBrush(METAL_CLAIR)
        painter.drawEllipse(QPointF(11.5, 15), 1.3, 1.3)
        painter.drawEllipse(QPointF(58.5, 15), 1.3, 1.3)

        # Vis filetée, sous la traverse : elle s'allonge quand la platine descend.
        vis = QRectF(32.5, 20, 5, 8 + d)
        painter.setPen(QPen(METAL_OMBRE, 0.8))
        painter.setBrush(_degrade_horizontal(vis, METAL_OMBRE, METAL_LUMIERE, METAL))
        painter.drawRect(vis)
        painter.save()
        painter.setClipRect(vis)
        painter.setPen(QPen(QColor(79, 93, 87, 190), 0.8))
        decalage_filet = (angle * 1.1) % 3.0
        k = -1
        while 20 + k * 3.0 + decalage_filet < vis.bottom() + 3:
            y = 20 + k * 3.0 + decalage_filet
            painter.drawLine(
                QPointF(vis.left(), y + 1.2), QPointF(vis.right(), y - 1.2)
            )
            k += 1
        painter.restore()

        # Platine en bois et sa plaque de fer.
        platine = QRectF(22, 28 + d, 26, 5)
        painter.setPen(QPen(BOIS_FONCE, 0.9))
        painter.setBrush(_degrade_vertical(platine, BOIS_CLAIR, BOIS))
        painter.drawRoundedRect(platine, 1.4, 1.4)
        painter.setPen(QPen(BOIS_LUMIERE, 0.7))
        painter.drawLine(QPointF(23.8, 29.2 + d), QPointF(46.2, 29.2 + d))
        plaque = QRectF(24, 33 + d, 22, 2)
        painter.setPen(QPen(METAL_OMBRE, 0.7))
        painter.setBrush(_degrade_vertical(plaque, METAL_CLAIR, METAL))
        painter.drawRect(plaque)

        # Écrou de la vis, posé sur la traverse.
        ecrou = QRectF(29.5, 9, 11, 3.4)
        painter.setPen(QPen(METAL_OMBRE, 0.8))
        painter.setBrush(_degrade_vertical(ecrou, METAL_LUMIERE, METAL))
        painter.drawRoundedRect(ecrou, 1, 1)

        # Barre de manœuvre : vue en perspective, elle se raccourcit en tournant.
        decalage_barre = 2.4 * profondeur
        y_barre = 6.0 + decalage_barre
        c = cos(angle)
        s = sin(angle)
        proche = QPointF(35 + 25 * c, y_barre + 1.8 * s)
        loin = QPointF(35 - 25 * c, y_barre - 1.8 * s)
        r_proche = 2.5 + 0.5 * s
        r_loin = 2.5 - 0.5 * s
        centre = QPointF(35, y_barre)

        def barre(extremite: QPointF) -> None:
            painter.setPen(
                QPen(METAL_OMBRE, 2.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            )
            painter.drawLine(centre, extremite)
            painter.setPen(
                QPen(METAL_CLAIR, 0.9, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            )
            painter.drawLine(
                QPointF(centre.x(), centre.y() - 0.6),
                QPointF(extremite.x(), extremite.y() - 0.6),
            )

        def boule(position: QPointF, rayon: float) -> None:
            degrade = QRadialGradient(
                position.x() - rayon * 0.35,
                position.y() - rayon * 0.35,
                rayon * 1.5,
            )
            degrade.setColorAt(0.0, METAL_LUMIERE)
            degrade.setColorAt(0.55, METAL)
            degrade.setColorAt(1.0, METAL_OMBRE)
            painter.setPen(QPen(METAL_OMBRE, 0.7))
            painter.setBrush(degrade)
            painter.drawEllipse(position, rayon, rayon)

        # La moitié éloignée passe derrière le moyeu, la proche devant.
        barre(loin)
        boule(loin, r_loin)

        moyeu = QRectF(31.5, y_barre - 2.8, 7, 5.6)
        painter.setPen(QPen(METAL_OMBRE, 0.8))
        painter.setBrush(_degrade_horizontal(moyeu, METAL, METAL_LUMIERE, METAL_OMBRE))
        painter.drawRoundedRect(moyeu, 1.2, 1.2)

        barre(proche)
        boule(proche, r_proche)

        painter.restore()

    # --------------------------------------------------------------------------
    # Dessin de la feuille imprimée
    # --------------------------------------------------------------------------

    def _dessiner_feuille(
        self,
        painter: QPainter,
        cx: float,
        cy: float,
        opacite: float,
    ) -> None:
        """Feuille d'atlas simplifiée : mer, île, tracé de voyage et repère."""

        if opacite <= 0.01:
            return

        largeur, hauteur = 34.0, 28.0

        painter.save()
        painter.setOpacity(painter.opacity() * opacite)
        painter.translate(cx, cy)
        painter.rotate(-4)

        feuille = QRectF(-largeur / 2, -hauteur / 2, largeur, hauteur)

        # Ombre et papier.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(60, 48, 30, 48))
        painter.drawRoundedRect(feuille.translated(1.2, 1.8), 1.5, 1.5)

        painter.setPen(QPen(PAPIER_CONTOUR, 0.9))
        painter.setBrush(_degrade_vertical(feuille, PAPIER_CLAIR, PAPIER))
        painter.drawRoundedRect(feuille, 1.5, 1.5)

        # Zone cartographique.
        carte = feuille.adjusted(3, 3, -3, -3)

        def pt(u: float, v: float) -> QPointF:
            return QPointF(
                carte.left() + u * carte.width(),
                carte.top() + v * carte.height(),
            )

        painter.save()
        painter.setClipRect(carte)

        # Mer.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(MER)
        painter.drawRect(carte)

        # Graticule très discret.
        painter.setPen(QPen(QColor(63, 107, 99, 38), 0.5))
        for u in (0.33, 0.66):
            painter.drawLine(pt(u, 0), pt(u, 1))
        for v in (0.40, 0.75):
            painter.drawLine(pt(0, v), pt(1, v))

        # Île.
        ile = QPainterPath()
        ile.moveTo(pt(0.16, 0.56))
        ile.cubicTo(pt(0.12, 0.24), pt(0.40, 0.10), pt(0.55, 0.24))
        ile.cubicTo(pt(0.70, 0.08), pt(0.94, 0.28), pt(0.86, 0.52))
        ile.cubicTo(pt(0.84, 0.80), pt(0.62, 0.90), pt(0.48, 0.80))
        ile.cubicTo(pt(0.34, 0.96), pt(0.10, 0.84), pt(0.16, 0.56))
        painter.setPen(QPen(ENCRE, 0.9))
        painter.setBrush(TERRE)
        painter.drawPath(ile)

        # Tracé du voyage : pointillé entre un départ et une destination.
        depart = pt(0.27, 0.68)
        arrivee = pt(0.72, 0.42)
        trace = QPainterPath()
        trace.moveTo(depart)
        trace.cubicTo(pt(0.38, 0.34), pt(0.52, 0.90), arrivee)
        pointille = QPen(
            ROUTE, 1.0, Qt.PenStyle.CustomDashLine, Qt.PenCapStyle.RoundCap
        )
        pointille.setDashPattern([0.4, 2.2])
        painter.setPen(pointille)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(trace)

        painter.setPen(QPen(ROUTE, 0.9))
        painter.setBrush(PAPIER_CLAIR)
        painter.drawEllipse(depart, 1.4, 1.4)

        # Épingle de destination.
        epingle = QPainterPath()
        tete = QPointF(arrivee.x(), arrivee.y() - 3.8)
        epingle.addEllipse(tete, 2.4, 2.4)
        pointe = QPainterPath()
        pointe.moveTo(tete.x() - 1.9, tete.y() + 1.5)
        pointe.lineTo(arrivee)
        pointe.lineTo(tete.x() + 1.9, tete.y() + 1.5)
        pointe.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ROUTE)
        painter.drawPath(epingle.united(pointe))
        painter.setBrush(PAPIER_CLAIR)
        painter.drawEllipse(tete, 0.9, 0.9)

        painter.restore()

        # Filet d'encadrement de la carte.
        painter.setPen(QPen(ENCRE, 0.8))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(carte)

        # Coin replié.
        pli = QPainterPath()
        pli.moveTo(feuille.right() - 4.5, feuille.top())
        pli.lineTo(feuille.right() - 4.5, feuille.top() + 4.5)
        pli.lineTo(feuille.right(), feuille.top() + 4.5)
        pli.closeSubpath()
        painter.setPen(QPen(PAPIER_CONTOUR, 0.6))
        painter.setBrush(QColor("#E6DDC9"))
        painter.drawPath(pli)

        painter.restore()

    # --------------------------------------------------------------------------
    # Dessin
    # --------------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        largeur = self.width()
        hauteur = self.height()
        decalage_appui = 1.5 if self._enfonce else 0.0
        desactive = not self.isEnabled()
        survol = self._survol if not desactive else 0.0

        rect_bouton = QRectF(
            5,
            4 + decalage_appui,
            largeur - 10,
            hauteur - 11,
        )

        # Ombre portée.
        if not self._enfonce:
            rect_ombre = QRectF(rect_bouton)
            rect_ombre.translate(0, 3)

            couleur_ombre = QColor("#37352E")
            couleur_ombre.setAlpha(35 if not desactive else 17)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(couleur_ombre)
            painter.drawRoundedRect(rect_ombre, 11, 11)

        # Fond papier, légèrement éclairci et teinté de vert au survol.
        couleur_haut = _melanger(QColor("#F8F6EF"), QColor("#FCFBF6"), survol)
        couleur_bas = _melanger(QColor("#EEEAE0"), QColor("#F4F1E7"), survol)
        couleur_contour = _melanger(QColor("#D1C8B8"), QColor("#9DB3A6"), survol)

        if desactive:
            couleur_haut = QColor("#F0EFE9")
            couleur_bas = QColor("#E9E7E0")
            couleur_contour = QColor("#D8D5CD")
        elif self._enfonce:
            couleur_haut = QColor("#EEE9DD")
            couleur_bas = QColor("#E7E0D2")

        chemin_bouton = QPainterPath()
        chemin_bouton.addRoundedRect(rect_bouton, 11, 11)

        painter.setPen(QPen(couleur_contour, 1.0))
        painter.setBrush(_degrade_vertical(rect_bouton, couleur_haut, couleur_bas))
        painter.drawPath(chemin_bouton)

        painter.save()
        painter.setClipPath(chemin_bouton)

        # Fibres très discrètes dans le papier.
        couleur_fibre = QColor("#BEB5A5")
        couleur_fibre.setAlpha(22 if not desactive else 10)
        painter.setPen(QPen(couleur_fibre, 0.55))
        for i in range(7):
            y = rect_bouton.top() + 8 + i * 8
            painter.drawLine(
                QPointF(rect_bouton.left() + 8, y),
                QPointF(rect_bouton.right() - 8, y - 1.5),
            )

        # Liseré lumineux le long du bord supérieur.
        painter.setPen(QPen(QColor(255, 255, 255, 150 if not desactive else 60), 1.0))
        painter.drawLine(
            QPointF(rect_bouton.left() + 10, rect_bouton.top() + 1.5),
            QPointF(rect_bouton.right() - 10, rect_bouton.top() + 1.5),
        )
        painter.restore()

        # Illustration : presse et feuille.
        echelle = min(1.0, (rect_bouton.height() - 8) / HAUTEUR_ILLUSTRATION)
        x_illustration = rect_bouton.left() + 12
        y_illustration = (
            rect_bouton.top()
            + (rect_bouton.height() - HAUTEUR_ILLUSTRATION * echelle) / 2
        )

        impression, opacite_feuille, dx_feuille, dy_feuille = _etat_impression(
            self._impression
        )
        profondeur = max(0.18 * survol, 0.5 if self._enfonce else 0.0, impression)
        angle = 0.35 + 0.6 * survol + 2.8 * impression

        painter.save()
        painter.translate(x_illustration, y_illustration)
        painter.scale(echelle, echelle)
        if desactive:
            painter.setOpacity(0.5)

        self._dessiner_presse(painter, profondeur, angle)
        self._dessiner_feuille(
            painter,
            83 + dx_feuille,
            39 + dy_feuille,
            opacite_feuille,
        )
        painter.restore()

        # Séparateur en pointillés, comme une ligne de perforation.
        x_texte = x_illustration + LARGEUR_ILLUSTRATION * echelle + 14
        perforation = QPen(QColor("#CFC6B4"), 1.0, Qt.PenStyle.CustomDashLine)
        perforation.setDashPattern([2.0, 3.0])
        perforation.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(perforation)
        painter.drawLine(
            QPointF(x_texte - 7, rect_bouton.top() + 11),
            QPointF(x_texte - 7, rect_bouton.bottom() - 11),
        )

        # Libellé : la taille s'adapte pour éviter de couper le texte.
        zone_texte = QRectF(
            x_texte,
            rect_bouton.top(),
            max(1.0, rect_bouton.right() - 34 - x_texte),
            rect_bouton.height(),
        )

        police = QFont()
        police.setFamilies(["Segoe UI", "Inter", "Helvetica Neue", "Arial"])
        police.setWeight(QFont.Weight.DemiBold)
        taille = max(11, min(15, int(hauteur * 0.19)))
        police.setPointSize(taille)
        largeur_disponible = max(1.0, zone_texte.width() - 4)
        while (
            taille > 10
            and QFontMetricsF(police).horizontalAdvance(self.text())
            > largeur_disponible
        ):
            taille -= 1
            police.setPointSize(taille)
        painter.setFont(police)

        texte_affiche = QFontMetricsF(police).elidedText(
            self.text(),
            Qt.TextElideMode.ElideRight,
            largeur_disponible,
        )

        couleur_texte = _melanger(QColor("#3D4944"), QColor("#2F5A51"), survol)
        painter.setPen(couleur_texte if not desactive else QColor("#96958D"))
        painter.drawText(
            zone_texte,
            Qt.AlignmentFlag.AlignCenter,
            texte_affiche,
        )

        # Flèche discrète à droite, qui avance légèrement au survol.
        couleur_fleche = _melanger(QColor("#89958A"), QColor("#4F7D70"), survol)
        couleur_fleche.setAlpha(int(115 + 100 * survol) if not desactive else 55)
        painter.setPen(
            QPen(
                couleur_fleche,
                1.5,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )

        centre_fleche = QPointF(
            rect_bouton.right() - 17 + 2.5 * survol,
            rect_bouton.center().y(),
        )
        fleche = QPainterPath()
        fleche.moveTo(centre_fleche.x() - 3, centre_fleche.y() - 4)
        fleche.lineTo(centre_fleche.x() + 1, centre_fleche.y())
        fleche.lineTo(centre_fleche.x() - 3, centre_fleche.y() + 4)
        painter.drawPath(fleche)

        # Indication de focus clavier.
        if self.hasFocus() and self.isEnabled():
            rect_focus = rect_bouton.adjusted(3, 3, -3, -3)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(
                QPen(
                    QColor("#879B8F"),
                    1.1,
                    Qt.PenStyle.DashLine,
                )
            )
            painter.drawRoundedRect(rect_focus, 8, 8)

        painter.end()


# ==============================================================================
# Fenêtre de test autonome
# ==============================================================================


class FenetreTest(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aperçu — presse cartographique")
        self.setMinimumSize(540, 220)

        contenu = QWidget()
        contenu.setStyleSheet("""
            QWidget {
                background-color: #F3F2ED;
                color: #3D4944;
                font-family: "Segoe UI";
            }
        """)

        disposition = QVBoxLayout(contenu)
        disposition.setContentsMargins(34, 28, 34, 28)
        disposition.setSpacing(13)

        titre = QLabel("Atelier cartographique")
        titre.setStyleSheet("""
            QLabel {
                color: #3D4944;
                font-size: 17px;
                font-weight: 600;
            }
        """)

        aide = QLabel("Survole le bouton, clique dessus ou utilise la touche Tab.")
        aide.setStyleSheet("""
            QLabel {
                color: #777B73;
                font-size: 12px;
            }
        """)

        self.bouton = BoutonCreationCartes()
        self.bouton.clicked.connect(self._bouton_clique)

        self.etat = QLabel(" ")
        self.etat.setStyleSheet("""
            QLabel {
                color: #71877B;
                font-size: 12px;
            }
        """)

        disposition.addWidget(titre)
        disposition.addWidget(aide)
        disposition.addWidget(self.bouton)
        disposition.addWidget(self.etat)
        disposition.addStretch()

        self.setCentralWidget(contenu)

    def _bouton_clique(self):
        self.etat.setText("La presse cartographique est prête !")


if __name__ == "__main__":
    import sys, os

    sys.path.append(os.getcwd())

    application = QApplication(sys.argv)
    fenetre = FenetreTest()
    fenetre.show()
    sys.exit(application.exec())
