################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.62 – Montgolfière                                                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math
import time

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QBrush,
    QLinearGradient,
    QRadialGradient,
)

# 1 -- Fonctions utilitaires ---------------------------------------------------


# 1.1 -- Conversion en QColor --------------------------------------------------


def _qcolor(
    couleur: QColor | str,
) -> QColor:
    """Convertit une couleur en QColor si nécessaire."""

    if isinstance(
        couleur,
        QColor,
    ):
        return QColor(
            couleur,
        )

    return QColor(
        couleur,
    )


# 1.2 -- Assombrissement d'une couleur ----------------------------------------


def _assombrir(
    couleur: QColor,
    facteur: int = 115,
) -> QColor:
    """
    Retourne une version légèrement plus sombre d'une couleur.

    Plus ``facteur`` est élevé, plus la couleur est sombre.
    """

    return couleur.darker(
        facteur,
    )


# 1.3 -- Éclaircissement d'une couleur ----------------------------------------


def _eclaircir(
    couleur: QColor,
    facteur: int = 115,
) -> QColor:
    """Retourne une version légèrement plus claire d'une couleur."""

    return couleur.lighter(
        facteur,
    )


# 2 -- Classe Montgolfiere -----------------------------------------------------


class Montgolfiere:
    """
    Dessine une montgolfière stylisée avec nacelle paramétrable.

    La nacelle peut être volontairement très large afin de servir ensuite
    de barre de Gantt.

    Toutes les dimensions sont exprimées relativement à ``taille``.
    """

    # 2.1 -- Initialisation ----------------------------------------------------

    def __init__(
        self,
        taille: float = 160,
        largeur_ballon: float = 0.72,
        hauteur_ballon: float = 0.82,
        largeur_nacelle: float = 0.28,
        hauteur_nacelle: float = 0.12,
        espace_nacelle: float = 0.08,
        couleur_ballon: QColor | str = "#D95F59",
        couleur_ballon_secondaire: QColor | str = "#F2C14E",
        couleur_ballon_centre: QColor | str = "#F7E3A1",
        couleur_nacelle: QColor | str = "#B4AB7E",
        couleur_nacelle_claire: QColor | str = "#E5D9B9",
        couleur_cordes: QColor | str = "#5F4A3A",
        couleur_contour: QColor | str = "#46352C",
        epaisseur_contour: float = 1.6,
        epaisseur_cordes: float = 1.4,
        nombre_bandes: int = 7,
        afficher_coutures: bool = True,
        afficher_tressage: bool = True,
        afficher_bruleur: bool = True,
    ):

        self.taille = float(
            taille,
        )

        # ----------------------------------------------------------------------
        # Dimensions relatives
        # ----------------------------------------------------------------------

        self.largeur_ballon = float(
            largeur_ballon,
        )

        self.hauteur_ballon = float(
            hauteur_ballon,
        )

        self.largeur_nacelle = float(
            largeur_nacelle,
        )

        self.hauteur_nacelle = float(
            hauteur_nacelle,
        )

        self.espace_nacelle = float(
            espace_nacelle,
        )

        # ----------------------------------------------------------------------
        # Couleurs
        # ----------------------------------------------------------------------

        self.couleur_ballon = _qcolor(
            couleur_ballon,
        )

        self.couleur_ballon_secondaire = _qcolor(
            couleur_ballon_secondaire,
        )

        self.couleur_ballon_centre = _qcolor(
            couleur_ballon_centre,
        )

        self.couleur_nacelle = _qcolor(
            couleur_nacelle,
        )

        self.couleur_nacelle_claire = _qcolor(
            couleur_nacelle_claire,
        )

        self.couleur_cordes = _qcolor(
            couleur_cordes,
        )

        self.couleur_contour = _qcolor(
            couleur_contour,
        )

        # ----------------------------------------------------------------------
        # Traits
        # ----------------------------------------------------------------------

        self.epaisseur_contour = float(
            epaisseur_contour,
        )

        self.epaisseur_cordes = float(
            epaisseur_cordes,
        )

        self.afficher_coutures = afficher_coutures
        self.afficher_tressage = afficher_tressage
        self.afficher_bruleur = afficher_bruleur

        self.nombre_bandes = max(
            3,
            int(nombre_bandes),
        )

    # 2.2 -- Dimensions absolues ----------------------------------------------

    def _dimensions(
        self,
        echelle: float,
    ) -> dict:

        taille = self.taille * echelle

        return {
            "taille": taille,
            "largeur_ballon": taille * self.largeur_ballon,
            "hauteur_ballon": taille * self.hauteur_ballon,
            "largeur_nacelle": taille * self.largeur_nacelle,
            "hauteur_nacelle": taille * self.hauteur_nacelle,
            "espace_nacelle": taille * self.espace_nacelle,
        }

    # 2.3 -- Création du contour du ballon ------------------------------------

    def _creer_chemin_ballon(
        self,
        centre_x: float,
        haut: float,
        largeur: float,
        hauteur: float,
    ) -> QPainterPath:
        """Forme une enveloppe ronde, légèrement resserrée vers son ouverture."""

        demi_largeur = largeur / 2
        y_ouverture = haut + hauteur * 0.96
        demi_ouverture = largeur * 0.105

        path = QPainterPath()
        # Sommet arrondi, épaules larges, puis bas resserré comme une vraie enveloppe.
        path.moveTo(centre_x, haut)
        path.cubicTo(
            centre_x + largeur * 0.34,
            haut - hauteur * 0.015,
            centre_x + demi_largeur * 1.02,
            haut + hauteur * 0.19,
            centre_x + demi_largeur,
            haut + hauteur * 0.43,
        )
        path.cubicTo(
            centre_x + demi_largeur * 0.98,
            haut + hauteur * 0.67,
            centre_x + largeur * 0.27,
            haut + hauteur * 0.89,
            centre_x + demi_ouverture,
            y_ouverture,
        )
        path.lineTo(centre_x - demi_ouverture, y_ouverture)
        path.cubicTo(
            centre_x - largeur * 0.27,
            haut + hauteur * 0.89,
            centre_x - demi_largeur * 0.98,
            haut + hauteur * 0.67,
            centre_x - demi_largeur,
            haut + hauteur * 0.43,
        )
        path.cubicTo(
            centre_x - demi_largeur * 1.02,
            haut + hauteur * 0.19,
            centre_x - largeur * 0.34,
            haut - hauteur * 0.015,
            centre_x,
            haut,
        )
        path.closeSubpath()
        return path

    # 2.4 -- Panneaux courbes de l'enveloppe -----------------------------------

    @staticmethod
    def _meridien(facteur: float) -> QPainterPath:
        """Couture dans un repère normalisé : largeur = hauteur = 1."""
        chemin = QPainterPath(QPointF(0, 0))
        chemin.cubicTo(
            facteur * 0.35,
            -0.015,
            facteur * 0.56,
            0.19,
            facteur * 0.50,
            0.43,
        )
        chemin.cubicTo(
            facteur * 0.49,
            0.67,
            facteur * 0.27,
            0.89,
            facteur * 0.105,
            0.96,
        )
        return chemin

    def _dessiner_ballon(self, painter, centre_x, haut, largeur, hauteur):
        # Travailler dans ce repère permet de garder les panneaux cohérents
        # lorsque largeur et hauteur sont modifiées indépendamment.
        import math

        contour = self._creer_chemin_ballon(0, 0, 1, 1)
        painter.save()
        painter.translate(centre_x, haut)
        painter.scale(largeur, hauteur)
        painter.setClipPath(contour, Qt.ClipOperation.IntersectClip)
        painter.setPen(Qt.PenStyle.NoPen)

        n = self.nombre_bandes
        limites = [-math.cos(math.pi * i / n) for i in range(n + 1)]
        palette = (
            self.couleur_ballon,
            self.couleur_ballon_secondaire,
            self.couleur_ballon_centre,
        )
        for i in range(n):
            gauche, droite = limites[i : i + 2]
            panneau = self._meridien(gauche)
            panneau.connectPath(self._meridien(droite).toReversed())
            panneau.closeSubpath()
            distance = abs(i - (n - 1) / 2)
            couleur = palette[int(distance + 0.5) % len(palette)]
            milieu = (gauche + droite) / 4
            degrade = QLinearGradient(gauche * 0.5, 0, droite * 0.5, 0.12)
            degrade.setColorAt(0, couleur.darker(113))
            degrade.setColorAt(0.45, couleur.lighter(112))
            degrade.setColorAt(1, couleur.darker(108))
            painter.setBrush(degrade)
            painter.drawPath(panneau)

        # Lumière commune aux panneaux : volume global et ombre latérale.
        volume = QLinearGradient(-0.5, 0, 0.5, 0.12)
        volume.setColorAt(0, QColor(35, 23, 30, 65))
        volume.setColorAt(0.38, QColor(255, 255, 240, 28))
        volume.setColorAt(0.64, QColor(255, 255, 255, 0))
        volume.setColorAt(1, QColor(35, 23, 30, 85))
        painter.fillPath(contour, volume)

        lumiere = QRadialGradient(QPointF(-0.17, 0.25), 0.46)
        lumiere.setColorAt(0, QColor(255, 253, 233, 75))
        lumiere.setColorAt(1, QColor(255, 255, 255, 0))
        painter.fillPath(contour, lumiere)

        if self.afficher_coutures:
            # Stylo cosmétique : les transformations ne déforment pas le trait.
            pen = QPen(QColor(70, 48, 40, 70))
            pen.setWidthF(max(0.45, self.epaisseur_contour * 0.45))
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for facteur in limites[1:-1]:
                painter.drawPath(self._meridien(facteur))

            # Deux coutures transversales légèrement bombées.
            pen.setColor(QColor(70, 48, 40, 35))
            painter.setPen(pen)
            for y, courbure in ((0.33, 0.055), (0.66, 0.045)):
                couture = QPainterPath(QPointF(-0.55, y))
                couture.cubicTo(-0.22, y + courbure, 0.22, y + courbure, 0.55, y)
                painter.drawPath(couture)
        painter.restore()

        path = self._creer_chemin_ballon(centre_x, haut, largeur, hauteur)
        painter.setPen(QPen(self.couleur_contour, self.epaisseur_contour))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Jupe légèrement évasée, avec une ouverture sombre en bas.
        col = QPainterPath()
        col.moveTo(centre_x - largeur * 0.108, haut + hauteur * 0.925)
        col.quadTo(
            centre_x,
            haut + hauteur * 0.95,
            centre_x + largeur * 0.108,
            haut + hauteur * 0.925,
        )
        col.lineTo(centre_x + largeur * 0.077, haut + hauteur)
        col.quadTo(
            centre_x, haut + hauteur * 1.016, centre_x - largeur * 0.077, haut + hauteur
        )
        col.closeSubpath()
        degrade = QLinearGradient(
            centre_x, haut + hauteur * 0.92, centre_x, haut + hauteur
        )
        degrade.setColorAt(0, self.couleur_ballon.darker(112))
        degrade.setColorAt(1, self.couleur_ballon.darker(155))
        painter.setBrush(degrade)
        painter.setPen(QPen(self.couleur_contour, self.epaisseur_contour * 0.7))
        painter.drawPath(col)
        painter.setBrush(self.couleur_contour)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            QRectF(
                centre_x - largeur * 0.077,
                haut + hauteur * 0.992,
                largeur * 0.154,
                hauteur * 0.018,
            )
        )

    def _dessiner_cordes(
        self,
        painter: QPainter,
        centre_x: float,
        bas_ballon: float,
        largeur_ballon: float,
        rect_nacelle: QRectF,
    ):

        pen = QPen(
            self.couleur_cordes,
            self.epaisseur_cordes,
        )

        pen.setCapStyle(
            Qt.PenCapStyle.RoundCap,
        )

        painter.setPen(
            pen,
        )

        # Points légèrement écartés sous l'enveloppe.
        x_depart_gauche = centre_x - largeur_ballon * 0.052

        x_depart_droite = centre_x + largeur_ballon * 0.052

        y_depart = bas_ballon

        # Les cordes arrivent légèrement à l'intérieur des bords de nacelle.
        x_fin_gauche = rect_nacelle.left() + rect_nacelle.width() * 0.10

        x_fin_droite = rect_nacelle.right() - rect_nacelle.width() * 0.10

        y_fin = rect_nacelle.top()

        painter.drawLine(
            QPointF(
                x_depart_gauche,
                y_depart,
            ),
            QPointF(
                x_fin_gauche,
                y_fin,
            ),
        )

        painter.drawLine(
            QPointF(
                x_depart_droite,
                y_depart,
            ),
            QPointF(
                x_fin_droite,
                y_fin,
            ),
        )

    # 2.5 -- Flamme animée, ancrée sur le brûleur ------------------------------

    @staticmethod
    def _chemin_flamme(rect, hauteur, largeur, phase, nervosite=1.0):
        """La base reste fixe ; seuls la pointe et les flancs ondulent."""
        cx = rect.center().x()
        bas = rect.bottom()
        pointe_x = cx + rect.width() * 0.15 * nervosite * math.sin(phase * 1.7)
        pointe_y = bas - hauteur * (0.94 + 0.06 * math.sin(phase * 2.3))
        ventre = rect.width() * 0.065 * nervosite * math.sin(phase * 2.1 + 0.8)
        chemin = QPainterPath(QPointF(cx - largeur * 0.5, bas))
        chemin.cubicTo(
            cx - largeur * 0.82 + ventre,
            bas - hauteur * 0.35,
            pointe_x - largeur * 0.34,
            bas - hauteur * 0.59,
            pointe_x,
            pointe_y,
        )
        chemin.cubicTo(
            pointe_x + largeur * 0.10,
            bas - hauteur * 0.66,
            cx + largeur * 0.90 + ventre,
            bas - hauteur * 0.32,
            cx + largeur * 0.5,
            bas,
        )
        chemin.quadTo(cx, bas + hauteur * 0.055, cx - largeur * 0.5, bas)
        chemin.closeSubpath()
        return chemin

    def _dessiner_bruleur(
        self, painter, centre_x, bas_ballon, largeur, rect, phase=0.0
    ):
        espace = rect.top() - bas_ballon
        if not self.afficher_bruleur or espace < 7:
            return

        # Le brûleur est porté par deux petits montants reliés à la nacelle.
        # La flamme part exactement du milieu de sa face supérieure.
        w = min(largeur * 0.105, rect.width() * 0.26, espace * 0.65)
        h = max(1.5, min(3.0, espace * 0.10))
        bas_bruleur = rect.top() - espace * 0.13
        haut_bruleur = bas_bruleur - h
        flamme = QRectF(
            centre_x - w * 0.62,
            bas_ballon + espace * 0.08,
            w * 1.24,
            haut_bruleur - bas_ballon - espace * 0.08,
        )
        painter.save()
        try:
            pen = QPen(self.couleur_contour, max(0.7, self.epaisseur_cordes * 0.65))
            painter.setPen(pen)
            for signe in (-1, 1):
                x = centre_x + signe * w * 0.37
                painter.drawLine(QPointF(x, bas_bruleur), QPointF(x, rect.top() + 0.8))

            # Halo contenu dans l'espace entre ballon et nacelle.
            painter.save()
            painter.setClipRect(
                QRectF(centre_x - w * 2, bas_ballon, w * 4, espace),
                Qt.ClipOperation.IntersectClip,
            )
            halo = QRadialGradient(
                QPointF(centre_x, flamme.center().y()),
                max(flamme.height(), w) * 0.72,
            )
            halo.setColorAt(0, QColor(255, 188, 55, 45))
            halo.setColorAt(1, QColor(255, 150, 25, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(halo)
            painter.drawEllipse(flamme.adjusted(-w * 0.55, 0, w * 0.55, h))
            painter.restore()

            # Trois couches qui partagent la même base, avec des phases décalées.
            for hauteur, largeur_rel, decalage, nervosite, couleurs in (
                (
                    1.00,
                    0.70,
                    0.00,
                    1.00,
                    ("#FFAD28", "#F5791E", "#E84812", QColor(225, 63, 12, 100)),
                ),
                (
                    0.73,
                    0.49,
                    0.65,
                    0.72,
                    ("#FFF39C", "#FFD33B", "#FF9D25", QColor(255, 135, 25, 90)),
                ),
                (
                    0.44,
                    0.28,
                    1.70,
                    0.40,
                    ("#FFFDE8", "#FFF5B4", "#FFD950", QColor(255, 206, 65, 50)),
                ),
            ):
                chemin = self._chemin_flamme(
                    flamme,
                    flamme.height() * hauteur,
                    flamme.width() * largeur_rel,
                    phase + decalage,
                    nervosite,
                )
                gradient = QLinearGradient(
                    0, flamme.bottom(), 0, flamme.bottom() - flamme.height() * hauteur
                )
                for position, couleur in zip((0.0, 0.38, 0.77, 1.0), couleurs):
                    gradient.setColorAt(position, QColor(couleur))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(gradient)
                painter.drawPath(chemin)

            # Dessiné après la flamme pour cacher proprement sa base.
            corps = QRectF(centre_x - w / 2, haut_bruleur, w, h)
            degrade = QLinearGradient(corps.topLeft(), corps.bottomLeft())
            degrade.setColorAt(0, self.couleur_contour.lighter(190))
            degrade.setColorAt(1, self.couleur_contour)
            painter.setBrush(degrade)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(corps, h * 0.3, h * 0.3)
        finally:
            painter.restore()

    # 2.6 -- Dessin de la nacelle ---------------------------------------------

    def _dessiner_nacelle(
        self,
        painter: QPainter,
        rect: QRectF,
    ):
        """Dessine une nacelle contemporaine, sobre et légèrement volumétrique."""

        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()

        h = rect.height()
        w = rect.width()

        # --------------------------------------------------------------------------
        # Silhouette générale
        # --------------------------------------------------------------------------

        rayon = min(h * 0.24, w * 0.12)

        capsule = QPainterPath()
        capsule.addRoundedRect(rect, rayon, rayon)

        # --------------------------------------------------------------------------
        # Ombre inférieure
        # --------------------------------------------------------------------------

        ombre = QRectF(
            rect.left() + rayon * 0.5,
            rect.top() + h * 0.12,
            w - rayon,
            h * 0.88,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(30, 45, 55, 35))
        painter.drawRoundedRect(
            ombre,
            rayon,
            rayon,
        )

        # --------------------------------------------------------------------------
        # Corps principal
        # --------------------------------------------------------------------------

        degrade = QLinearGradient(
            rect.left(),
            rect.top(),
            rect.left(),
            rect.bottom(),
        )

        degrade.setColorAt(
            0.0,
            self.couleur_nacelle_claire.lighter(108),
        )

        degrade.setColorAt(
            0.35,
            self.couleur_nacelle_claire,
        )

        degrade.setColorAt(
            1.0,
            self.couleur_nacelle,
        )

        contour = self.couleur_nacelle.darker(140)

        painter.setPen(
            QPen(
                contour,
                max(0.8, self.epaisseur_contour * 0.8),
            )
        )

        painter.setBrush(degrade)
        painter.drawPath(capsule)

        # --------------------------------------------------------------------------
        # Reflet supérieur
        # --------------------------------------------------------------------------

        marge = max(1.5, h * 0.13)

        reflet = QRectF(
            rect.left() + rayon * 0.8,
            rect.top() + marge,
            max(0.0, w - rayon * 1.6),
            max(0.8, h * 0.12),
        )

        lumiere = QColor("#FFFFFF")
        lumiere.setAlpha(65)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(lumiere)

        painter.drawRoundedRect(
            reflet,
            reflet.height() / 2,
            reflet.height() / 2,
        )

        # --------------------------------------------------------------------------
        # Liseré intérieur
        # --------------------------------------------------------------------------

        inset = max(1.0, min(h * 0.07, 2.0))

        interieur = rect.adjusted(
            inset,
            inset,
            -inset,
            -inset,
        )

        if interieur.width() > 0 and interieur.height() > 0:

            couleur = self.couleur_nacelle_claire
            couleur.setAlpha(95)

            painter.setPen(
                QPen(
                    couleur,
                    max(0.5, self.epaisseur_contour * 0.4),
                )
            )

            painter.setBrush(Qt.BrushStyle.NoBrush)

            painter.drawRoundedRect(
                interieur,
                max(0.0, rayon - inset),
                max(0.0, rayon - inset),
            )

        painter.restore()

    def dessiner(
        self,
        painter: QPainter,
        centre: QPointF,
        echelle: float = 1.0,
        largeur_nacelle: float | None = None,
        hauteur_nacelle: float | None = None,
        phase_flamme: float | None = None,
    ) -> QRectF:
        """
        Dessine la montgolfière.

        Paramètres
        ----------
        painter :
            QPainter déjà actif.

        centre :
            Position horizontale du centre de la montgolfière.
            ``centre.y()`` correspond au haut de l'enveloppe.

        echelle :
            Facteur multiplicatif global.

        largeur_nacelle :
            Permet de remplacer ponctuellement la largeur configurée dans
            ``__init__``. Très utile pour transformer la nacelle en barre
            de Gantt.

            La valeur est exprimée en pixels.

        hauteur_nacelle :
            Même principe pour la hauteur de la nacelle.

        phase_flamme :
            Phase en radians. None utilise une horloge monotone (animation
            automatique à chaque nouveau dessin). Fournir une valeur fixe
            pour figer la flamme ou exporter une image reproductible.
            Le QWidget hôte doit appeler update() avec un QTimer, par exemple
            toutes les 33 ms : cette classe de dessin ne possède aucun timer.

        Retour
        ------
        QRectF
            Rectangle réellement occupé par la nacelle. Cela pourra être
            pratique plus tard pour les tooltips / tests de survol.
        """

        if echelle <= 0 or self.taille <= 0:
            return QRectF()

        dimensions = self._dimensions(
            echelle=echelle,
        )

        largeur_ballon = dimensions["largeur_ballon"]

        hauteur_ballon = dimensions["hauteur_ballon"]

        largeur_nacelle_finale = (
            largeur_nacelle
            if largeur_nacelle is not None
            else dimensions["largeur_nacelle"]
        )

        hauteur_nacelle_finale = (
            hauteur_nacelle
            if hauteur_nacelle is not None
            else dimensions["hauteur_nacelle"]
        )

        espace_nacelle = dimensions["espace_nacelle"]

        centre_x = centre.x()

        haut = centre.y()

        bas_ballon = haut + hauteur_ballon

        # ----------------------------------------------------------------------
        # Rectangle de la nacelle
        # ----------------------------------------------------------------------

        y_nacelle = bas_ballon + espace_nacelle

        rect_nacelle = QRectF(
            centre_x - largeur_nacelle_finale / 2,
            y_nacelle,
            largeur_nacelle_finale,
            hauteur_nacelle_finale,
        )

        if (
            min(
                largeur_ballon,
                hauteur_ballon,
                largeur_nacelle_finale,
                hauteur_nacelle_finale,
            )
            <= 0
        ):
            return QRectF()

        # ----------------------------------------------------------------------
        # Dessin
        # ----------------------------------------------------------------------

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        self._dessiner_ballon(
            painter=painter,
            centre_x=centre_x,
            haut=haut,
            largeur=largeur_ballon,
            hauteur=hauteur_ballon,
        )

        self._dessiner_cordes(
            painter=painter,
            centre_x=centre_x,
            bas_ballon=bas_ballon,
            largeur_ballon=largeur_ballon,
            rect_nacelle=rect_nacelle,
        )

        phase = time.monotonic() * 4.0 if phase_flamme is None else phase_flamme
        self._dessiner_bruleur(
            painter,
            centre_x,
            bas_ballon,
            largeur_ballon,
            rect_nacelle,
            phase,
        )

        self._dessiner_nacelle(
            painter=painter,
            rect=rect_nacelle,
        )

        painter.restore()

        return rect_nacelle


# 3 -- Fenêtre de test autonome ------------------------------------------------

if __name__ == "__main__":

    import sys
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import (
        QApplication,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QSlider,
        QCheckBox,
    )

    class Apercu(QWidget):
        def __init__(self):
            super().__init__()
            self.largeur = 230
            self.bandes = 7
            self.details = True
            self.sombre = False
            self.timer = QTimer(self)
            self.timer.setInterval(33)
            self.timer.timeout.connect(self.update)
            self.timer.start()
            self.setMinimumSize(800, 450)

        def paintEvent(self, event):
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.fillRect(self.rect(), QColor("#18232F" if self.sombre else "#F5F2ED"))
            for x, largeur, couleurs in (
                (self.width() * 0.28, 85, ("#D86959", "#EDBD60", "#F6E3AE")),
                (self.width() * 0.71, self.largeur, ("#4C8C93", "#8BBBA5", "#E8DAAD")),
            ):
                ballon = Montgolfiere(
                    taille=290,
                    largeur_ballon=0.68,
                    hauteur_ballon=0.83,
                    espace_nacelle=0.11,
                    nombre_bandes=self.bandes,
                    couleur_ballon=couleurs[0],
                    couleur_ballon_secondaire=couleurs[1],
                    couleur_ballon_centre=couleurs[2],
                    afficher_coutures=self.details,
                    afficher_tressage=self.details,
                    afficher_bruleur=self.details,
                )
                r = ballon.dessiner(
                    p, QPointF(x, 45), largeur_nacelle=largeur, hauteur_nacelle=34
                )
                p.setPen(QColor("#543D2D"))
                p.drawText(
                    r,
                    Qt.AlignmentFlag.AlignCenter,
                    "Voyage" if largeur < 120 else "Un voyage au long cours",
                )
            p.end()

    app = QApplication(sys.argv)
    fenetre = QWidget()
    fenetre.setWindowTitle("Montgolfière — panneaux, volume et nacelle")
    disposition = QVBoxLayout(fenetre)
    apercu = Apercu()
    disposition.addWidget(apercu)
    commandes = QHBoxLayout()
    disposition.addLayout(commandes)

    def regler_largeur(valeur):
        apercu.largeur = valeur
        apercu.update()

    def regler_bandes(valeur):
        apercu.bandes = valeur
        apercu.update()

    def regler_details(valeur):
        apercu.details = bool(valeur)
        apercu.update()

    def regler_fond(valeur):
        apercu.sombre = bool(valeur)
        apercu.update()

    commandes.addWidget(QLabel("Largeur nacelle"))
    curseur = QSlider(Qt.Orientation.Horizontal)
    curseur.setRange(55, 350)
    curseur.setValue(230)
    curseur.valueChanged.connect(regler_largeur)
    commandes.addWidget(curseur)
    commandes.addWidget(QLabel("Panneaux"))
    panneaux = QSlider(Qt.Orientation.Horizontal)
    panneaux.setRange(3, 13)
    panneaux.setValue(7)
    panneaux.valueChanged.connect(regler_bandes)
    commandes.addWidget(panneaux)
    details = QCheckBox("Détails")
    details.setChecked(True)
    details.toggled.connect(regler_details)
    commandes.addWidget(details)
    fond = QCheckBox("Fond sombre")
    fond.toggled.connect(regler_fond)
    commandes.addWidget(fond)
    fenetre.resize(960, 550)
    fenetre.show()
    sys.exit(app.exec())
