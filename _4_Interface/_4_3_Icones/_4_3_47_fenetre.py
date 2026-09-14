################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.47 – Classe de création d'une fenêtre de train                           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)

# 1 -- Classe de création d'une fenêtre ----------------------------------------


class FenetreTrain:
    """
    Dessine une fenêtre de train simple ou double.

    Une fenêtre double peut représenter deux pays indépendants et possède
    quatre états possibles :

        - gauche éteinte / droite éteinte ;
        - gauche allumée / droite éteinte ;
        - gauche éteinte / droite allumée ;
        - gauche allumée / droite allumée.

    La lumière d'une moitié allumée se diffuse légèrement dans l'ensemble
    du vitrage afin d'éviter une séparation lumineuse artificiellement nette.

    Après chaque appel à `peindre`, les zones interactives sont disponibles
    dans `zone_gauche` et `zone_droite`.
    """

    def __init__(
        self,
        couleur: QColor | str,
        double: bool = True,
        gauche_allumee: bool = False,
        droite_allumee: bool = False,
        couleur_cadre: QColor | str = "#3C454A",
        couleur_montant: QColor | str | None = None,
        intensite_lumiere: float = 1.0,
        halo: bool = True,
        reflets: bool = True,
    ):

        self.couleur = QColor(couleur)
        self.double = bool(double)

        self.gauche_allumee = bool(gauche_allumee)
        self.droite_allumee = bool(droite_allumee) if self.double else False

        self.couleur_cadre = QColor(couleur_cadre)

        self.couleur_montant = (
            QColor(couleur_montant)
            if couleur_montant is not None
            else self.couleur_cadre.lighter(110)
        )

        self.intensite_lumiere = max(
            0.0,
            min(float(intensite_lumiere), 1.5),
        )

        self.halo = bool(halo)
        self.reflets = bool(reflets)

        # Zones interactives mises à jour au dernier dessin
        self.zone_gauche = QRectF()
        self.zone_droite = QRectF()

    # --------------------------------------------------------------------------
    # États
    # --------------------------------------------------------------------------

    def set_etat(
        self,
        gauche: bool,
        droite: bool | None = None,
    ) -> None:
        """Met à jour l'état lumineux de la fenêtre."""

        self.gauche_allumee = bool(gauche)

        if self.double:
            self.droite_allumee = bool(droite) if droite is not None else False
        else:
            self.droite_allumee = False

    # --------------------------------------------------------------------------
    # Dessin principal
    # --------------------------------------------------------------------------

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        survol_gauche: bool = False,
        survol_droite: bool = False,
    ) -> None:

        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dimensions du cadre et du vitrage
        epaisseur_cadre = max(
            1.0,
            rect.height() * 0.075,
        )

        rect_vitre = rect.adjusted(
            epaisseur_cadre,
            epaisseur_cadre,
            -epaisseur_cadre,
            -epaisseur_cadre,
        )

        # Zones correspondant aux différents pays
        self._mettre_a_jour_zones(
            rect_vitre=rect_vitre,
        )

        # Halo extérieur
        if self.halo:
            self._dessiner_halo(
                painter=painter,
                rect=rect,
            )

        # Cadre
        self._dessiner_cadre(
            painter=painter,
            rect=rect,
        )

        # Vitrage sombre de base
        self._dessiner_fond_vitre(
            painter=painter,
            rect=rect_vitre,
        )

        # Lumière intérieure
        self._dessiner_lumiere(
            painter=painter,
            rect=rect_vitre,
        )

        # Montant central
        if self.double:
            self._dessiner_montant(
                painter=painter,
                rect=rect_vitre,
            )

        # Reflets sur la vitre
        if self.reflets:
            self._dessiner_reflets(
                painter=painter,
                rect=rect_vitre,
            )

        # Petite ombre intérieure pour donner de l'épaisseur au vitrage
        self._dessiner_profondeur(
            painter=painter,
            rect=rect_vitre,
        )

        # Survol éventuel
        if survol_gauche:
            self._dessiner_survol(
                painter=painter,
                rect=self.zone_gauche,
            )

        if self.double and survol_droite:
            self._dessiner_survol(
                painter=painter,
                rect=self.zone_droite,
            )

        painter.restore()

    # --------------------------------------------------------------------------
    # Cadre
    # --------------------------------------------------------------------------

    def _dessiner_cadre(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:

        rayon = rect.height() * 0.16

        degrade = QLinearGradient(
            rect.topLeft(),
            rect.bottomLeft(),
        )

        degrade.setColorAt(
            0.00,
            self.couleur_cadre.lighter(135),
        )

        degrade.setColorAt(
            0.38,
            self.couleur_cadre,
        )

        degrade.setColorAt(
            1.00,
            self.couleur_cadre.darker(135),
        )

        painter.setBrush(QBrush(degrade))

        painter.setPen(
            QPen(
                self.couleur_cadre.darker(165),
                max(1.0, rect.height() * 0.018),
            )
        )

        painter.drawRoundedRect(
            rect,
            rayon,
            rayon,
        )

    # --------------------------------------------------------------------------
    # Fond sombre de la vitre
    # --------------------------------------------------------------------------

    def _dessiner_fond_vitre(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:

        couleur_sombre = self._couleur_eteinte()

        degrade = QLinearGradient(
            rect.topLeft(),
            rect.bottomLeft(),
        )

        # Légèrement plus clair en haut, comme une vitre réfléchissante
        degrade.setColorAt(
            0.00,
            couleur_sombre.lighter(135),
        )

        degrade.setColorAt(
            0.35,
            couleur_sombre,
        )

        degrade.setColorAt(
            1.00,
            couleur_sombre.darker(135),
        )

        painter.setPen(
            QPen(
                couleur_sombre.darker(160),
                max(1.0, rect.height() * 0.020),
            )
        )

        painter.setBrush(QBrush(degrade))

        rayon = rect.height() * 0.11

        painter.drawRoundedRect(
            rect,
            rayon,
            rayon,
        )

    # --------------------------------------------------------------------------
    # Lumière
    # --------------------------------------------------------------------------

    def _dessiner_lumiere(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """
        Superpose plusieurs dégradés afin d'obtenir une lumière intérieure
        moins artificielle qu'un simple remplissage uniforme.
        """

        if not self.gauche_allumee and not self.droite_allumee:
            return

        chemin_vitre = QPainterPath()

        chemin_vitre.addRoundedRect(
            rect,
            rect.height() * 0.11,
            rect.height() * 0.11,
        )

        painter.save()
        painter.setClipPath(chemin_vitre)

        # Chaque moitié allumée produit sa propre source lumineuse.
        if self.gauche_allumee:

            centre_x = (
                rect.center().x()
                if not self.double
                else rect.left() + rect.width() * 0.27
            )

            self._dessiner_source_lumineuse(
                painter=painter,
                rect=rect,
                centre=QPointF(
                    centre_x,
                    rect.top() + rect.height() * 0.57,
                ),
            )

        if self.double and self.droite_allumee:

            self._dessiner_source_lumineuse(
                painter=painter,
                rect=rect,
                centre=QPointF(
                    rect.left() + rect.width() * 0.73,
                    rect.top() + rect.height() * 0.57,
                ),
            )

        # Lumière verticale plus diffuse rappelant l'éclairage intérieur
        self._dessiner_ambiance_lumineuse(
            painter=painter,
            rect=rect,
        )

        painter.restore()

    def _dessiner_source_lumineuse(
        self,
        painter: QPainter,
        rect: QRectF,
        centre: QPointF,
    ) -> None:
        """
        Une source lumineuse est volontairement suffisamment large pour
        déborder légèrement vers l'autre moitié d'une fenêtre double.
        """

        rayon = rect.width() * (0.72 if self.double else 0.85)

        gradient = QRadialGradient(
            centre,
            rayon,
        )

        couleur_0 = self.couleur.lighter(165)
        couleur_1 = self.couleur.lighter(125)
        couleur_2 = QColor(self.couleur)
        couleur_3 = QColor(self.couleur)

        facteur = self.intensite_lumiere

        couleur_0.setAlpha(min(int(235 * facteur), 255))

        couleur_1.setAlpha(min(int(205 * facteur), 255))

        couleur_2.setAlpha(min(int(115 * facteur), 255))

        couleur_3.setAlpha(0)

        gradient.setColorAt(
            0.00,
            couleur_0,
        )

        gradient.setColorAt(
            0.20,
            couleur_1,
        )

        gradient.setColorAt(
            0.52,
            couleur_2,
        )

        gradient.setColorAt(
            1.00,
            couleur_3,
        )

        painter.setPen(QPen())

        painter.setBrush(QBrush(gradient))

        painter.drawRect(rect)

    def _dessiner_ambiance_lumineuse(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:

        couleur_haut = QColor(self.couleur)
        couleur_centre = QColor(self.couleur)
        couleur_bas = QColor(self.couleur)

        facteur = self.intensite_lumiere

        couleur_haut.setAlpha(min(int(30 * facteur), 255))

        couleur_centre.setAlpha(min(int(70 * facteur), 255))

        couleur_bas.setAlpha(min(int(20 * facteur), 255))

        gradient = QLinearGradient(
            rect.topLeft(),
            rect.bottomLeft(),
        )

        gradient.setColorAt(
            0.00,
            couleur_haut,
        )

        gradient.setColorAt(
            0.45,
            couleur_centre,
        )

        gradient.setColorAt(
            1.00,
            couleur_bas,
        )

        painter.setPen(QPen())

        painter.setBrush(QBrush(gradient))

        painter.drawRect(rect)

    # --------------------------------------------------------------------------
    # Halo extérieur
    # --------------------------------------------------------------------------

    def _dessiner_halo(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:

        nb_allumees = int(self.gauche_allumee)

        if self.double:
            nb_allumees += int(self.droite_allumee)

        if nb_allumees == 0:
            return

        # Plusieurs couches donnent un halo plus doux qu'un unique rectangle.
        couches = (
            (0.10, 18),
            (0.065, 30),
            (0.035, 45),
        )

        for proportion, alpha in couches:

            marge = rect.height() * proportion

            rect_halo = rect.adjusted(
                -marge,
                -marge,
                marge,
                marge,
            )

            couleur = QColor(self.couleur)

            couleur.setAlpha(
                min(
                    int(alpha * self.intensite_lumiere),
                    255,
                )
            )

            painter.setPen(QPen())

            painter.setBrush(couleur)

            painter.drawRoundedRect(
                rect_halo,
                rect.height() * 0.19,
                rect.height() * 0.19,
            )

    # --------------------------------------------------------------------------
    # Montant central
    # --------------------------------------------------------------------------

    def _dessiner_montant(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:

        largeur = max(
            rect.width() * 0.026,
            rect.height() * 0.055,
        )

        rect_montant = QRectF(
            rect.center().x() - largeur / 2,
            rect.top(),
            largeur,
            rect.height(),
        )

        degrade = QLinearGradient(
            rect_montant.topLeft(),
            rect_montant.topRight(),
        )

        degrade.setColorAt(
            0.00,
            self.couleur_montant.darker(135),
        )

        degrade.setColorAt(
            0.45,
            self.couleur_montant.lighter(120),
        )

        degrade.setColorAt(
            1.00,
            self.couleur_montant.darker(145),
        )

        painter.setPen(QPen())

        painter.setBrush(QBrush(degrade))

        painter.drawRect(rect_montant)

        # Fine lumière sur l'arête du montant
        couleur_reflet = QColor(
            255,
            255,
            255,
            60,
        )

        painter.setPen(
            QPen(
                couleur_reflet,
                max(
                    1.0,
                    largeur * 0.10,
                ),
            )
        )

        painter.drawLine(
            QPointF(
                rect_montant.center().x(),
                rect_montant.top(),
            ),
            QPointF(
                rect_montant.center().x(),
                rect_montant.bottom(),
            ),
        )

    # --------------------------------------------------------------------------
    # Reflets
    # --------------------------------------------------------------------------

    def _dessiner_reflets(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:

        chemin_vitre = QPainterPath()

        chemin_vitre.addRoundedRect(
            rect,
            rect.height() * 0.11,
            rect.height() * 0.11,
        )

        painter.save()
        painter.setClipPath(chemin_vitre)

        # ----------------------------------------------------------------------
        # Grand reflet diagonal
        # ----------------------------------------------------------------------

        reflet = QPainterPath()

        reflet.moveTo(
            rect.left() + rect.width() * 0.08,
            rect.top(),
        )

        reflet.lineTo(
            rect.left() + rect.width() * 0.22,
            rect.top(),
        )

        reflet.lineTo(
            rect.left() + rect.width() * 0.48,
            rect.bottom(),
        )

        reflet.lineTo(
            rect.left() + rect.width() * 0.37,
            rect.bottom(),
        )

        reflet.closeSubpath()

        painter.setPen(QPen())

        painter.setBrush(
            QColor(
                255,
                255,
                255,
                26,
            )
        )

        painter.drawPath(reflet)

        # ----------------------------------------------------------------------
        # Reflet secondaire beaucoup plus fin
        # ----------------------------------------------------------------------

        reflet_fin = QPainterPath()

        reflet_fin.moveTo(
            rect.left() + rect.width() * 0.58,
            rect.top(),
        )

        reflet_fin.lineTo(
            rect.left() + rect.width() * 0.615,
            rect.top(),
        )

        reflet_fin.lineTo(
            rect.left() + rect.width() * 0.79,
            rect.bottom(),
        )

        reflet_fin.lineTo(
            rect.left() + rect.width() * 0.75,
            rect.bottom(),
        )

        reflet_fin.closeSubpath()

        painter.setBrush(
            QColor(
                255,
                255,
                255,
                15,
            )
        )

        painter.drawPath(reflet_fin)

        painter.restore()

    # --------------------------------------------------------------------------
    # Profondeur du vitrage
    # --------------------------------------------------------------------------

    def _dessiner_profondeur(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """
        Ajoute une légère ombre sur les bords afin que la vitre semble être
        légèrement en retrait dans la carrosserie.
        """

        epaisseur = max(
            1.0,
            rect.height() * 0.035,
        )

        couleur_ombre = QColor(
            0,
            0,
            0,
            65,
        )

        painter.setBrush(QBrush())

        painter.setPen(
            QPen(
                couleur_ombre,
                epaisseur,
            )
        )

        painter.drawRoundedRect(
            rect.adjusted(
                epaisseur / 2,
                epaisseur / 2,
                -epaisseur / 2,
                -epaisseur / 2,
            ),
            rect.height() * 0.09,
            rect.height() * 0.09,
        )

    # --------------------------------------------------------------------------
    # Survol
    # --------------------------------------------------------------------------

    def _dessiner_survol(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:

        if rect.isEmpty():
            return

        couleur = QColor(
            255,
            255,
            255,
            35,
        )

        painter.setPen(
            QPen(
                QColor(
                    255,
                    255,
                    255,
                    125,
                ),
                max(
                    1.0,
                    rect.height() * 0.025,
                ),
            )
        )

        painter.setBrush(couleur)

        painter.drawRoundedRect(
            rect.adjusted(
                1,
                1,
                -1,
                -1,
            ),
            rect.height() * 0.08,
            rect.height() * 0.08,
        )

    # --------------------------------------------------------------------------
    # Zones interactives
    # --------------------------------------------------------------------------

    def _mettre_a_jour_zones(
        self,
        rect_vitre: QRectF,
    ) -> None:

        if not self.double:

            self.zone_gauche = QRectF(rect_vitre)

            self.zone_droite = QRectF()

            return

        demi_largeur = rect_vitre.width() / 2

        self.zone_gauche = QRectF(
            rect_vitre.left(),
            rect_vitre.top(),
            demi_largeur,
            rect_vitre.height(),
        )

        self.zone_droite = QRectF(
            rect_vitre.left() + demi_largeur,
            rect_vitre.top(),
            demi_largeur,
            rect_vitre.height(),
        )

    def zone_survolee(
        self,
        position: QPointF,
    ) -> str | None:
        """
        Renvoie :
            - "gauche"
            - "droite"
            - None
        """

        if self.zone_gauche.contains(position):
            return "gauche"

        if self.double and self.zone_droite.contains(position):
            return "droite"

        return None

    # --------------------------------------------------------------------------
    # Couleurs
    # --------------------------------------------------------------------------

    def _couleur_eteinte(
        self,
    ) -> QColor:
        """
        Produit une vitre sombre tout en conservant une petite trace de la
        couleur du continent.
        """

        couleur = QColor(self.couleur)

        h, s, v, a = couleur.getHsv()

        if h < 0:
            h = 0

        couleur.setHsv(
            h,
            max(int(s * 0.24), 10),
            max(int(v * 0.30), 22),
            a,
        )

        return couleur
