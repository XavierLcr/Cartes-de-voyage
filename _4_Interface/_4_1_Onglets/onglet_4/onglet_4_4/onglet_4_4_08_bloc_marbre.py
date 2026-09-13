################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_4                                #
# Onglet 4.4.8 – Bloc de marbre                                                #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import random

from PyQt6.QtCore import (
    QPointF,
    QRectF,
    Qt,
)

from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetricsF,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

# 1 -- Classe de création d'un bloc de marbre ---------------------------------


class BlocMarbre:
    """
    Représente un bloc de marbre avec un léger volume, des marbrures et
    éventuellement deux lignes de texte gravées sur sa face avant.

    Le bloc n'est pas un QWidget : il est directement dessiné dans le
    QPainter du widget parent.
    """

    def __init__(
        self,
        texte: str | None = None,
        sous_texte: str | None = None,
        couleur_marbre: str | QColor = "#D8D3C8",
        couleur_texte: str | QColor = "#57524D",
        graine: int = 42,
    ):

        self.texte = texte
        self.sous_texte = sous_texte

        self.couleur_marbre = QColor(couleur_marbre)
        self.couleur_texte = QColor(couleur_texte)

        self.graine = graine

        # Proportions du relief du bloc
        self.proportion_profondeur = 0.075
        self.proportion_dessus = 0.12

        # Marbrures
        self.n_marbrures_principales = 2
        self.n_marbrures_secondaires = random.randint(4, 6)

    # 2 -- Paramètres ----------------------------------------------------------

    def set_texte(
        self,
        texte: str | None,
        sous_texte: str | None = None,
    ) -> None:
        """Modifie le texte affiché sur le bloc."""

        self.texte = texte
        self.sous_texte = sous_texte

    def set_couleur_marbre(
        self,
        couleur: str | QColor,
    ) -> None:
        """Modifie la couleur principale du marbre."""

        self.couleur_marbre = QColor(couleur)

    def set_couleur_texte(
        self,
        couleur: str | QColor,
    ) -> None:
        """Modifie la couleur du texte gravé."""

        self.couleur_texte = QColor(couleur)

    # 3 -- Gestion des couleurs ------------------------------------------------

    @staticmethod
    def _modifier_couleur(
        couleur: QColor,
        facteur: float,
    ) -> QColor:
        """
        Éclaircit ou assombrit une couleur.

        facteur > 1 : éclaircit
        facteur < 1 : assombrit
        """

        return QColor(
            max(0, min(255, int(couleur.red() * facteur))),
            max(0, min(255, int(couleur.green() * facteur))),
            max(0, min(255, int(couleur.blue() * facteur))),
            couleur.alpha(),
        )

    @staticmethod
    def _couleur_marbre_aleatoire(
        couleur: QColor,
        rng: random.Random,
        variation: int = 18,
        luminosite_min: int = -15,
        luminosite_max: int = 8,
        alpha: int = 255,
    ) -> QColor:
        """
        Génère une couleur proche de la couleur de base.

        Une variation globale de luminosité est combinée à de très légères
        variations indépendantes des composantes RGB afin d'éviter des
        marbrures simplement grises.
        """

        variation_luminosite = rng.randint(
            luminosite_min,
            luminosite_max,
        )

        def canal(valeur: int) -> int:
            return max(
                0,
                min(
                    255,
                    valeur + variation_luminosite + rng.randint(-variation, variation),
                ),
            )

        return QColor(
            canal(couleur.red()),
            canal(couleur.green()),
            canal(couleur.blue()),
            alpha,
        )

    # 4 -- Géométrie -----------------------------------------------------------

    def _geometrie_bloc(
        self,
        rect: QRectF,
        point_fuite_x: float,
    ) -> dict:
        """
        Calcule les différentes faces du bloc.

        Plus le bloc est éloigné horizontalement du point de fuite,
        plus sa face latérale est visible.
        """

        profondeur_max = min(
            rect.width() * self.proportion_profondeur,
            rect.height() * 0.14,
        )

        # Distance horizontale entre le bloc et le point de fuite
        distance_fuite = rect.center().x() - point_fuite_x

        # Le signe détermine le côté visible
        if distance_fuite < 0:
            sens = 1
        elif distance_fuite > 0:
            sens = -1
        else:
            sens = 0

        # Intensité de la perspective.
        #
        # À environ 2 largeurs de bloc du point de fuite,
        # on atteint la profondeur maximale.
        distance_reference = rect.width() * 2.0

        intensite = min(
            1.0,
            abs(distance_fuite) / max(1.0, distance_reference),
        )

        # Petite courbe d'adoucissement :
        # évite que les blocs proches du centre deviennent trop plats.
        intensite = intensite**0.75

        profondeur = profondeur_max * intensite
        decalage_x = profondeur * sens

        # La visibilité du dessus dépend beaucoup moins de la position
        # horizontale : on conserve donc presque toute sa hauteur.
        hauteur_dessus_max = min(
            rect.height() * self.proportion_dessus,
            profondeur_max * 0.85,
        )

        hauteur_dessus = hauteur_dessus_max * (0.72 + 0.28 * intensite)

        # Face avant
        if sens >= 0:

            rect_face = QRectF(
                rect.left(),
                rect.top() + hauteur_dessus,
                rect.width() - profondeur,
                rect.height() - hauteur_dessus,
            )

        else:

            rect_face = QRectF(
                rect.left() + profondeur,
                rect.top() + hauteur_dessus,
                rect.width() - profondeur,
                rect.height() - hauteur_dessus,
            )

        # Dessus
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

        # Face latérale
        cote = QPainterPath()

        if sens > 0:

            cote.moveTo(
                QPointF(
                    rect_face.right(),
                    rect_face.top(),
                )
            )

            cote.lineTo(
                QPointF(
                    rect_face.right() + profondeur,
                    rect.top(),
                )
            )

            cote.lineTo(
                QPointF(
                    rect_face.right() + profondeur,
                    rect.bottom() - hauteur_dessus,
                )
            )

            cote.lineTo(
                QPointF(
                    rect_face.right(),
                    rect.bottom(),
                )
            )

        elif sens < 0:

            cote.moveTo(
                QPointF(
                    rect_face.left(),
                    rect_face.top(),
                )
            )

            cote.lineTo(
                QPointF(
                    rect_face.left() - profondeur,
                    rect.top(),
                )
            )

            cote.lineTo(
                QPointF(
                    rect_face.left() - profondeur,
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
            "sens": sens,
            "intensite_perspective": intensite,
        }

    # 5 -- Dessin du volume ----------------------------------------------------

    def _dessiner_volume(
        self,
        painter: QPainter,
        geometrie: dict,
    ) -> None:
        """Dessine les trois faces principales du bloc."""

        face = geometrie["face"]

        # Face avant
        degrade_face = QLinearGradient(
            face.left(),
            face.top(),
            face.right(),
            face.bottom(),
        )

        degrade_face.setColorAt(
            0.0,
            self._modifier_couleur(
                self.couleur_marbre,
                1.10,
            ),
        )

        degrade_face.setColorAt(
            0.45,
            self.couleur_marbre,
        )

        degrade_face.setColorAt(
            1.0,
            self._modifier_couleur(
                self.couleur_marbre,
                0.91,
            ),
        )

        painter.setBrush(QBrush(degrade_face))

        painter.setPen(
            QPen(
                self._modifier_couleur(
                    self.couleur_marbre,
                    0.72,
                ),
                0.8,
            )
        )

        painter.drawRect(face)

        # Dessus
        couleur_dessus = self._modifier_couleur(
            self.couleur_marbre,
            1.13,
        )

        painter.setBrush(couleur_dessus)

        painter.drawPath(geometrie["dessus"])

        # Côté
        couleur_cote = self._modifier_couleur(
            self.couleur_marbre,
            0.82,
        )

        painter.setBrush(couleur_cote)

        painter.drawPath(geometrie["cote"])

    # 6 -- Marbrures -----------------------------------------------------------

    def _creer_marbrure(
        self,
        rect: QRectF,
        rng: random.Random,
        importance: float,
    ) -> QPainterPath:
        """
        Crée une veine irrégulière composée de plusieurs courbes successives.
        """

        marge = rect.width() * 0.12

        x = rng.uniform(
            rect.left() - marge,
            rect.left() + rect.width() * 0.18,
        )

        y = rng.uniform(
            rect.top() - rect.height() * 0.10,
            rect.bottom() + rect.height() * 0.10,
        )

        chemin = QPainterPath(QPointF(x, y))

        direction_y = rng.choice((-1.0, 1.0))

        n_segments = rng.randint(
            4,
            6 if importance >= 0.8 else 5,
        )

        longueur_totale = rng.uniform(
            rect.width() * (0.50 + importance * 0.10),
            rect.width() * (0.85 + importance * 0.18),
        )

        pas_x = longueur_totale / n_segments

        # Inclinaison générale de la veine
        pente = direction_y * rng.uniform(
            rect.height() * 0.025,
            rect.height() * 0.10,
        )

        for _ in range(n_segments):

            x_depart = x
            y_depart = y

            x_fin = x_depart + pas_x * rng.uniform(0.85, 1.15)

            y_fin = (
                y_depart
                + pente
                + rng.uniform(
                    -rect.height() * 0.055,
                    rect.height() * 0.055,
                )
            )

            # Contrôles légèrement indépendants :
            # la veine change doucement de direction.
            controle_1 = QPointF(
                x_depart + (x_fin - x_depart) * 0.30,
                y_depart
                + rng.uniform(
                    -rect.height() * 0.045,
                    rect.height() * 0.045,
                ),
            )

            controle_2 = QPointF(
                x_depart + (x_fin - x_depart) * 0.72,
                y_fin
                + rng.uniform(
                    -rect.height() * 0.045,
                    rect.height() * 0.045,
                ),
            )

            chemin.cubicTo(
                controle_1,
                controle_2,
                QPointF(x_fin, y_fin),
            )

            x = x_fin
            y = y_fin

            # La pente elle-même dérive légèrement
            pente += rng.uniform(
                -rect.height() * 0.018,
                rect.height() * 0.018,
            )

        return chemin

    def _dessiner_marbrures(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine des veines minérales irrégulières et légèrement ramifiées."""

        rng = random.Random(self.graine)

        painter.save()
        painter.setClipRect(rect)

        # ------------------------------------------------------------------
        # Veines principales
        # ------------------------------------------------------------------

        for _ in range(self.n_marbrures_principales):

            chemin = self._creer_marbrure(
                rect=rect,
                rng=rng,
                importance=1.0,
            )

            couleur = self._couleur_marbre_aleatoire(
                couleur=self.couleur_marbre,
                rng=rng,
                variation=10,
                luminosite_min=-45,
                luminosite_max=-15,
            )

            epaisseur = rng.uniform(0.8, 1.45)

            # Halo diffus autour de la veine
            couleur_halo = QColor(couleur)
            couleur_halo.setAlpha(rng.randint(10, 22))

            painter.setPen(
                QPen(
                    couleur_halo,
                    epaisseur * rng.uniform(3.0, 4.8),
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )
            )

            painter.drawPath(chemin)

            # Corps de la veine
            couleur_corps = QColor(couleur)
            couleur_corps.setAlpha(rng.randint(32, 58))

            painter.setPen(
                QPen(
                    couleur_corps,
                    epaisseur,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )
            )

            painter.drawPath(chemin)

            # Très fine ligne centrale
            if rng.random() < 0.60:

                couleur_coeur = self._couleur_marbre_aleatoire(
                    couleur=self.couleur_marbre,
                    rng=rng,
                    variation=8,
                    luminosite_min=-58,
                    luminosite_max=-28,
                    alpha=rng.randint(22, 42),
                )

                painter.setPen(
                    QPen(
                        couleur_coeur,
                        epaisseur * rng.uniform(0.22, 0.42),
                        Qt.PenStyle.SolidLine,
                        Qt.PenCapStyle.RoundCap,
                        Qt.PenJoinStyle.RoundJoin,
                    )
                )

                painter.drawPath(chemin)

        # ------------------------------------------------------------------
        # Petites veines secondaires
        # ------------------------------------------------------------------

        for _ in range(self.n_marbrures_secondaires):

            chemin = self._creer_marbrure(
                rect=rect,
                rng=rng,
                importance=0.35,
            )

            couleur = self._couleur_marbre_aleatoire(
                couleur=self.couleur_marbre,
                rng=rng,
                variation=12,
                luminosite_min=-28,
                luminosite_max=12,
                alpha=rng.randint(14, 32),
            )

            painter.setPen(
                QPen(
                    couleur,
                    rng.uniform(0.25, 0.65),
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )
            )

            painter.drawPath(chemin)

        # ------------------------------------------------------------------
        # Nuances minérales claires
        # ------------------------------------------------------------------

        for _ in range(8):

            chemin = self._creer_marbrure(
                rect=rect,
                rng=rng,
                importance=0.20,
            )

            couleur = self._couleur_marbre_aleatoire(
                couleur=self.couleur_marbre,
                rng=rng,
                variation=9,
                luminosite_min=8,
                luminosite_max=28,
                alpha=rng.randint(10, 24),
            )

            painter.setPen(
                QPen(
                    couleur,
                    rng.uniform(0.35, 1.0),
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )
            )

            painter.drawPath(chemin)

        painter.restore()

    # 7 -- Ajustement des polices ---------------------------------------------

    @staticmethod
    def _police_adaptee(
        texte: str,
        largeur_max: float,
        taille_max: float,
        taille_min: float = 7.0,
    ) -> QFont:
        """Crée une police dont le texte tient dans la largeur disponible."""

        police = QFont()
        police.setWeight(QFont.Weight.DemiBold)

        taille = taille_max

        while taille > taille_min:

            police.setPointSizeF(taille)

            metrics = QFontMetricsF(police)

            if metrics.horizontalAdvance(texte) <= largeur_max:
                break

            taille -= 0.5

        return police

    # 8 -- Texte gravé ---------------------------------------------------------

    def _dessiner_texte_grave(
        self,
        painter: QPainter,
        rect: QRectF,
        texte: str,
        police: QFont,
        couleur: QColor,
    ) -> None:
        """
        Dessine un texte avec une impression de gravure dans le marbre.

        Un reflet en bas à droite et une ombre en haut à gauche donnent
        l'impression que les lettres sont creusées dans la pierre.
        """

        # Ombre intérieure
        couleur_ombre = self._modifier_couleur(
            couleur,
            0.52,
        )

        couleur_ombre.setAlpha(170)

        rect_ombre = QRectF(
            rect.left() - 0.8,
            rect.top() - 0.8,
            rect.width(),
            rect.height(),
        )

        painter.setFont(police)
        painter.setPen(couleur_ombre)

        painter.drawText(
            rect_ombre,
            Qt.AlignmentFlag.AlignCenter,
            texte,
        )

        # Reflet du bord inférieur de la gravure
        couleur_reflet = self._modifier_couleur(
            self.couleur_marbre,
            1.28,
        )

        couleur_reflet.setAlpha(190)

        rect_reflet = QRectF(
            rect.left() + 0.8,
            rect.top() + 0.8,
            rect.width(),
            rect.height(),
        )

        painter.setPen(couleur_reflet)

        painter.drawText(
            rect_reflet,
            Qt.AlignmentFlag.AlignCenter,
            texte,
        )

        # Corps de la gravure
        couleur_finale = QColor(couleur)

        couleur_finale.setAlpha(205)

        painter.setPen(couleur_finale)

        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            texte,
        )

    def _dessiner_textes(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine les éventuelles inscriptions du bloc."""

        if not self.texte and not self.sous_texte:
            return

        marge_x = rect.width() * 0.09
        marge_y = rect.height() * 0.10

        zone = rect.adjusted(
            marge_x,
            marge_y,
            -marge_x,
            -marge_y,
        )

        # Seulement une ligne
        if self.texte and not self.sous_texte:

            police = self._police_adaptee(
                texte=str(self.texte),
                largeur_max=zone.width(),
                taille_max=max(
                    8,
                    zone.height() * 0.27,
                ),
            )

            self._dessiner_texte_grave(
                painter=painter,
                rect=zone,
                texte=str(self.texte),
                police=police,
                couleur=self.couleur_texte,
            )

            return

        # Deux lignes : nom du pays + nombre de voyages
        hauteur_nom = zone.height() * 0.56

        rect_nom = QRectF(
            zone.left(),
            zone.top(),
            zone.width(),
            hauteur_nom,
        )

        rect_valeur = QRectF(
            zone.left(),
            zone.top() + hauteur_nom,
            zone.width(),
            zone.height() - hauteur_nom,
        )

        if self.texte:

            police_nom = self._police_adaptee(
                texte=str(self.texte),
                largeur_max=rect_nom.width(),
                taille_max=max(
                    8,
                    rect_nom.height() * 0.37,
                ),
            )

            police_nom.setWeight(QFont.Weight.Bold)

            self._dessiner_texte_grave(
                painter=painter,
                rect=rect_nom,
                texte=str(self.texte),
                police=police_nom,
                couleur=self.couleur_texte,
            )

        if self.sous_texte:

            police_valeur = self._police_adaptee(
                texte=str(self.sous_texte),
                largeur_max=rect_valeur.width(),
                taille_max=max(
                    7,
                    rect_valeur.height() * 0.34,
                ),
            )

            police_valeur.setWeight(QFont.Weight.Medium)

            couleur_secondaire = QColor(self.couleur_texte)

            couleur_secondaire.setAlpha(185)

            self._dessiner_texte_grave(
                painter=painter,
                rect=rect_valeur,
                texte=str(self.sous_texte),
                police=police_valeur,
                couleur=couleur_secondaire,
            )

    # 9 -- Arêtes et finitions -------------------------------------------------

    def _dessiner_finitions(
        self,
        painter: QPainter,
        geometrie: dict,
    ) -> None:
        """Ajoute quelques arêtes lumineuses pour renforcer le volume."""

        face = geometrie["face"]

        couleur_claire = self._modifier_couleur(
            self.couleur_marbre,
            1.24,
        )

        couleur_claire.setAlpha(175)

        painter.setPen(
            QPen(
                couleur_claire,
                0.9,
            )
        )

        # Arête supérieure
        painter.drawLine(
            QPointF(
                face.left(),
                face.top(),
            ),
            QPointF(
                face.right(),
                face.top(),
            ),
        )

        # Arête gauche
        painter.drawLine(
            QPointF(
                face.left(),
                face.top(),
            ),
            QPointF(
                face.left(),
                face.bottom(),
            ),
        )

    # 10 -- Dessin principal ---------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        rect: QRectF,
        point_fuite_x: float | None = None,
    ) -> None:
        """Dessine le bloc de marbre complet."""

        if rect.width() <= 0 or rect.height() <= 0:
            return

        if point_fuite_x is None:
            point_fuite_x = rect.center().x()

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        geometrie = self._geometrie_bloc(
            rect=rect,
            point_fuite_x=point_fuite_x,
        )

        self._dessiner_volume(
            painter=painter,
            geometrie=geometrie,
        )

        self._dessiner_marbrures(
            painter=painter,
            rect=geometrie["face"],
        )

        self._dessiner_textes(
            painter=painter,
            rect=geometrie["face"],
        )

        self._dessiner_finitions(
            painter=painter,
            geometrie=geometrie,
        )

        painter.restore()
