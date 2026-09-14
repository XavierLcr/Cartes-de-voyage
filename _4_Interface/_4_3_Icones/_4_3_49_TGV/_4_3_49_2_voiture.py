################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones/_4_3_49_TGV                                         #
# 4.3.49.2 – Classe de création d'une voiture de TGV                           #
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

from _4_Interface._4_3_Icones._4_3_47_fenetre import FenetreTrain

# 1 -- Classe de création d'une voiture de TGV ---------------------------------


class VoitureTGV:
    """
    Dessine une voiture voyageurs de TGV classique ou Duplex.

    Chaque emplacement correspond à un pays.

    Les emplacements sont regroupés deux par deux dans des fenêtres doubles.
    Si une rangée contient un nombre impair de pays, le dernier emplacement
    utilise automatiquement une fenêtre simple.

    Pour un Duplex, les pays sont répartis entre les deux étages :
        - étage supérieur : ceil(n / 2)
        - étage inférieur : floor(n / 2)

    La largeur optimale de la voiture dépend automatiquement du nombre de
    modules de fenêtres de la rangée la plus chargée.
    """

    def __init__(
        self,
        nb_pays: int,
        couleur_fenetres: QColor | str,
        duplex: bool = False,
        pays_allumes: list[bool] | None = None,
        couleur_caisse: QColor | str = "#E7E9E8",
        couleur_secondaire: QColor | str = "#59646A",
        couleur_toit: QColor | str | None = None,
        couleur_cadre_fenetres: QColor | str = "#3C454A",
        portes: bool = True,
        halo_fenetres: bool = True,
        reflets_fenetres: bool = True,
    ):

        self.nb_pays = max(int(nb_pays), 0)
        self.duplex = bool(duplex)

        self.couleur_fenetres = QColor(couleur_fenetres)
        self.couleur_caisse = QColor(couleur_caisse)
        self.couleur_secondaire = QColor(couleur_secondaire)
        self.couleur_cadre_fenetres = QColor(couleur_cadre_fenetres)

        self.couleur_toit = (
            QColor(couleur_toit)
            if couleur_toit is not None
            else self.couleur_caisse.darker(108)
        )

        self.portes = bool(portes)
        self.halo_fenetres = bool(halo_fenetres)
        self.reflets_fenetres = bool(reflets_fenetres)

        # ----------------------------------------------------------------------
        # État des pays
        # ----------------------------------------------------------------------

        if pays_allumes is None:

            self.pays_allumes = [True for _ in range(self.nb_pays)]

        else:

            if len(pays_allumes) != self.nb_pays:
                raise ValueError(
                    "pays_allumes doit contenir exactement " f"{self.nb_pays} valeurs."
                )

            self.pays_allumes = list(pays_allumes)

        # ----------------------------------------------------------------------
        # Zones interactives
        # ----------------------------------------------------------------------

        # zones_pays[i] correspond au pays d'indice i.
        self.zones_pays = [QRectF() for _ in range(self.nb_pays)]

    # --------------------------------------------------------------------------
    # Répartition des pays
    # --------------------------------------------------------------------------

    def repartition_pays(
        self,
    ) -> tuple[list[int], list[int]]:
        """
        Renvoie les indices des pays placés sur chacune des deux rangées.

        Pour un TGV simple :
            ([0, 1, 2, ...], [])

        Pour un Duplex :
            ([étage supérieur], [étage inférieur])
        """

        indices = list(range(self.nb_pays))

        if not self.duplex:
            return indices, []

        nb_haut = (self.nb_pays + 1) // 2

        return (
            indices[:nb_haut],
            indices[nb_haut:],
        )

    # --------------------------------------------------------------------------
    # Nombre de modules de fenêtres
    # --------------------------------------------------------------------------

    @staticmethod
    def _nb_modules(
        nb_pays: int,
    ) -> int:
        """
        Deux pays peuvent partager une fenêtre double.

        6 pays -> 3 modules
        7 pays -> 4 modules
        """

        return (nb_pays + 1) // 2

    def nb_modules_max(
        self,
    ) -> int:
        """Nombre de fenêtres physiques de la rangée la plus chargée."""

        haut, bas = self.repartition_pays()

        return max(
            self._nb_modules(len(haut)),
            self._nb_modules(len(bas)),
            1,
        )

    # --------------------------------------------------------------------------
    # Largeur recommandée
    # --------------------------------------------------------------------------

    def largeur_recommandee(
        self,
        hauteur: float,
    ) -> float:
        """
        Calcule une largeur de voiture adaptée à son contenu.

        Cette largeur préserve approximativement :
            - la taille naturelle des fenêtres ;
            - les espacements ;
            - les portes ;
            - les zones d'articulation.

        Le widget final reste libre de fournir une largeur différente :
        les fenêtres seront alors automatiquement redimensionnées.
        """

        if hauteur <= 0:
            return 0.0

        indices_haut, indices_bas = self.repartition_pays()

        largeur_haut = self._largeur_rangee_recommandee(
            nb_pays=len(indices_haut),
            hauteur=hauteur,
        )

        largeur_bas = self._largeur_rangee_recommandee(
            nb_pays=len(indices_bas),
            hauteur=hauteur,
        )

        largeur_rangee = max(
            largeur_haut,
            largeur_bas,
        )

        # Espace réservé aux portes et articulations
        marge_ext = hauteur * 0.10

        largeur_porte = hauteur * 0.15 if self.portes else 0

        espace_porte = hauteur * 0.055 if self.portes else hauteur * 0.03

        largeur = largeur_rangee + 2 * largeur_porte + 2 * espace_porte + 2 * marge_ext

        # Une voiture très peu remplie ne doit pas ressembler à un cube.
        largeur_minimale = hauteur * 2.55

        return max(
            largeur,
            largeur_minimale,
        )

    def _largeur_rangee_recommandee(
        self,
        nb_pays: int,
        hauteur: float,
    ) -> float:

        if nb_pays <= 0:
            return 0.0

        nb_doubles = nb_pays // 2

        nb_simples = nb_pays % 2

        # Une fenêtre simple représente environ 55 % de la largeur d'une double.
        largeur_double = hauteur * (0.34 if self.duplex else 0.38)

        largeur_simple = largeur_double * 0.56

        nb_modules = nb_doubles + nb_simples

        espacement = hauteur * 0.035

        largeur = nb_doubles * largeur_double + nb_simples * largeur_simple

        if nb_modules > 1:
            largeur += (nb_modules - 1) * espacement

        return largeur

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
        bogie_gauche: bool = True,
        bogie_droit: bool = True,
    ) -> None:

        if rect.width() <= 0 or rect.height() <= 0:
            return

        perspective = max(
            0.0,
            min(
                float(perspective),
                0.18,
            ),
        )

        sens = 1 if sens >= 0 else -1

        # Réinitialisation
        self.zones_pays = [QRectF() for _ in range(self.nb_pays)]

        painter.save()

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.translate(
            rect.left(),
            rect.top(),
        )

        if sens == -1:

            painter.translate(
                rect.width(),
                0,
            )

            painter.scale(
                -1,
                1,
            )

        largeur = rect.width()
        hauteur = rect.height()

        # ----------------------------------------------------------------------
        # Arrière-plan mécanique
        # ----------------------------------------------------------------------

        if ombre:

            self._dessiner_ombre(
                painter,
                largeur,
                hauteur,
            )

        if bogie_gauche:

            self._dessiner_bogie_articule(
                painter=painter,
                centre_x=largeur * 0.035,
                hauteur=hauteur,
            )

        if bogie_droit:

            self._dessiner_bogie_articule(
                painter=painter,
                centre_x=largeur * 0.965,
                hauteur=hauteur,
            )

        # ----------------------------------------------------------------------
        # Carrosserie
        # ----------------------------------------------------------------------

        self._dessiner_toit(
            painter=painter,
            largeur=largeur,
            hauteur=hauteur,
            perspective=perspective,
        )

        self._dessiner_caisse(
            painter=painter,
            largeur=largeur,
            hauteur=hauteur,
        )

        self._dessiner_bandeau_bas(
            painter=painter,
            largeur=largeur,
            hauteur=hauteur,
        )

        self._dessiner_articulations(
            painter=painter,
            largeur=largeur,
            hauteur=hauteur,
        )

        # ----------------------------------------------------------------------
        # Portes
        # ----------------------------------------------------------------------

        if self.portes:

            rect_porte_gauche = self._rect_porte(
                largeur=largeur,
                hauteur=hauteur,
                gauche=True,
            )

            rect_porte_droite = self._rect_porte(
                largeur=largeur,
                hauteur=hauteur,
                gauche=False,
            )

            self._dessiner_porte(
                painter=painter,
                rect=rect_porte_gauche,
                hauteur_reference=hauteur,
            )

            self._dessiner_porte(
                painter=painter,
                rect=rect_porte_droite,
                hauteur_reference=hauteur,
            )

        # ----------------------------------------------------------------------
        # Fenêtres
        # ----------------------------------------------------------------------

        geometries = self._calculer_geometrie_fenetres(
            largeur=largeur,
            hauteur=hauteur,
        )

        for module in geometries:

            indices = module["indices"]
            rect_fenetre = module["rect"]

            double = len(indices) == 2

            indice_gauche = indices[0]

            indice_droite = indices[1] if double else None

            fenetre = FenetreTrain(
                couleur=self.couleur_fenetres,
                double=double,
                gauche_allumee=(self.pays_allumes[indice_gauche]),
                droite_allumee=(
                    self.pays_allumes[indice_droite]
                    if indice_droite is not None
                    else False
                ),
                couleur_cadre=(self.couleur_cadre_fenetres),
                halo=self.halo_fenetres,
                reflets=self.reflets_fenetres,
            )

            fenetre.peindre(
                painter=painter,
                rect=rect_fenetre,
            )

            # ------------------------------------------------------------------
            # Zones interactives locales
            # ------------------------------------------------------------------

            self.zones_pays[indice_gauche] = QRectF(fenetre.zone_gauche)

            if indice_droite is not None:

                self.zones_pays[indice_droite] = QRectF(fenetre.zone_droite)

        painter.restore()

        # ----------------------------------------------------------------------
        # Conversion vers les coordonnées du widget
        # ----------------------------------------------------------------------

        self.zones_pays = [
            self._zone_locale_vers_globale(
                zone=zone,
                rect=rect,
                sens=sens,
            )
            for zone in self.zones_pays
        ]

    # --------------------------------------------------------------------------
    # Géométrie des fenêtres
    # --------------------------------------------------------------------------

    def _calculer_geometrie_fenetres(
        self,
        largeur: float,
        hauteur: float,
    ) -> list[dict]:

        haut, bas = self.repartition_pays()

        # Zone horizontale réellement utilisable
        marge = hauteur * 0.15

        largeur_porte = hauteur * 0.14 if self.portes else 0

        espace_porte = hauteur * 0.045 if self.portes else hauteur * 0.04

        x_min = marge + largeur_porte + espace_porte

        x_max = largeur - marge - largeur_porte - espace_porte

        # Sécurité pour des widgets volontairement minuscules
        if x_max <= x_min:

            x_min = largeur * 0.20

            x_max = largeur * 0.80

        if self.duplex:

            return self._calculer_rangee(
                indices=haut,
                x_min=x_min,
                x_max=x_max,
                y=hauteur * 0.285,
                hauteur_fenetre=(hauteur * 0.115),
            ) + self._calculer_rangee(
                indices=bas,
                x_min=x_min,
                x_max=x_max,
                y=hauteur * 0.495,
                hauteur_fenetre=(hauteur * 0.115),
            )

        return self._calculer_rangee(
            indices=haut,
            x_min=x_min,
            x_max=x_max,
            y=hauteur * 0.405,
            hauteur_fenetre=(hauteur * 0.150),
        )

    def _calculer_rangee(
        self,
        indices: list[int],
        x_min: float,
        x_max: float,
        y: float,
        hauteur_fenetre: float,
    ) -> list[dict]:

        if not indices:
            return []

        # ----------------------------------------------------------------------
        # Regroupement des pays par deux
        # ----------------------------------------------------------------------

        groupes = [
            indices[i : i + 2]
            for i in range(
                0,
                len(indices),
                2,
            )
        ]

        largeur_zone = x_max - x_min

        # Taille idéale d'une fenêtre double
        largeur_double = hauteur_fenetre * 2.10

        largeur_simple = largeur_double * 0.56

        espacement = hauteur_fenetre * 0.45

        largeurs = [
            (largeur_double if len(groupe) == 2 else largeur_simple)
            for groupe in groupes
        ]

        largeur_ideale = sum(largeurs) + espacement * max(
            len(groupes) - 1,
            0,
        )

        # ----------------------------------------------------------------------
        # Réduction automatique en cas de manque de place
        # ----------------------------------------------------------------------

        facteur = min(
            1.0,
            largeur_zone
            / max(
                largeur_ideale,
                1,
            ),
        )

        largeurs = [largeur * facteur for largeur in largeurs]

        espacement *= facteur

        largeur_groupe = sum(largeurs) + espacement * max(
            len(groupes) - 1,
            0,
        )

        # Centrage de la rangée
        x = x_min + (largeur_zone - largeur_groupe) / 2

        resultat = []

        for groupe, largeur_fenetre in zip(
            groupes,
            largeurs,
        ):

            resultat.append(
                {
                    "indices": groupe,
                    "rect": QRectF(
                        x,
                        y,
                        largeur_fenetre,
                        hauteur_fenetre,
                    ),
                }
            )

            x += largeur_fenetre + espacement

        return resultat

    # --------------------------------------------------------------------------
    # Caisse
    # --------------------------------------------------------------------------

    def _borne_haute_caisse(
        self,
        hauteur: float,
    ) -> float:

        return hauteur * (0.185 if self.duplex else 0.300)

    def _chemin_caisse(
        self,
        largeur: float,
        hauteur: float,
    ) -> QPainterPath:

        y_haut = self._borne_haute_caisse(hauteur)

        chemin = QPainterPath()

        chemin.moveTo(
            largeur * 0.025,
            hauteur * 0.685,
        )

        chemin.lineTo(
            largeur * 0.025,
            y_haut + hauteur * 0.035,
        )

        chemin.quadTo(
            largeur * 0.035,
            y_haut,
            largeur * 0.075,
            y_haut,
        )

        chemin.lineTo(
            largeur * 0.925,
            y_haut,
        )

        chemin.quadTo(
            largeur * 0.965,
            y_haut,
            largeur * 0.975,
            y_haut + hauteur * 0.035,
        )

        chemin.lineTo(
            largeur * 0.975,
            hauteur * 0.685,
        )

        # Léger ventre inférieur
        chemin.quadTo(
            largeur * 0.900,
            hauteur * 0.735,
            largeur * 0.820,
            hauteur * 0.735,
        )

        chemin.lineTo(
            largeur * 0.180,
            hauteur * 0.735,
        )

        chemin.quadTo(
            largeur * 0.100,
            hauteur * 0.735,
            largeur * 0.025,
            hauteur * 0.685,
        )

        chemin.closeSubpath()

        return chemin

    def _dessiner_caisse(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        y_haut = self._borne_haute_caisse(hauteur)

        degrade = QLinearGradient(
            0,
            y_haut,
            0,
            hauteur * 0.74,
        )

        degrade.setColorAt(
            0.00,
            self.couleur_caisse.lighter(112),
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
                max(
                    1.0,
                    hauteur * 0.007,
                ),
            )
        )

        painter.drawPath(
            self._chemin_caisse(
                largeur=largeur,
                hauteur=hauteur,
            )
        )

    # --------------------------------------------------------------------------
    # Toit avec légère perspective
    # --------------------------------------------------------------------------

    def _dessiner_toit(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
        perspective: float,
    ) -> None:

        y = self._borne_haute_caisse(hauteur)

        dy = hauteur * perspective

        dx = dy * 0.30

        chemin = QPainterPath()

        chemin.moveTo(
            largeur * 0.075,
            y,
        )

        chemin.lineTo(
            largeur * 0.925,
            y,
        )

        chemin.lineTo(
            largeur * 0.925 - dx,
            y - dy,
        )

        chemin.lineTo(
            largeur * 0.075 - dx,
            y - dy,
        )

        chemin.closeSubpath()

        degrade = QLinearGradient(
            0,
            y - dy,
            0,
            y,
        )

        degrade.setColorAt(
            0,
            self.couleur_toit.lighter(110),
        )

        degrade.setColorAt(
            1,
            self.couleur_toit,
        )

        painter.setBrush(QBrush(degrade))

        painter.setPen(
            QPen(
                self.couleur_toit.darker(130),
                max(
                    1.0,
                    hauteur * 0.006,
                ),
            )
        )

        painter.drawPath(chemin)

    # --------------------------------------------------------------------------
    # Portes
    # --------------------------------------------------------------------------

    def _rect_porte(
        self,
        largeur: float,
        hauteur: float,
        gauche: bool,
    ) -> QRectF:

        largeur_porte = hauteur * 0.14

        # Éloignement par rapport à l'articulation
        marge_exterieure = hauteur * 0.15

        x = marge_exterieure if gauche else largeur - marge_exterieure - largeur_porte

        if self.duplex:

            y = hauteur * 0.385

            hauteur_porte = hauteur * 0.255

        else:

            y = hauteur * 0.355

            hauteur_porte = hauteur * 0.275

        return QRectF(
            x,
            y,
            largeur_porte,
            hauteur_porte,
        )

    def _dessiner_porte(
        self,
        painter: QPainter,
        rect: QRectF,
        hauteur_reference: float,
    ) -> None:

        painter.setBrush(self.couleur_caisse.darker(104))

        painter.setPen(
            QPen(
                self.couleur_caisse.darker(145),
                max(
                    1.0,
                    hauteur_reference * 0.006,
                ),
            )
        )

        rayon = hauteur_reference * 0.012

        painter.drawRoundedRect(
            rect,
            rayon,
            rayon,
        )

        # Petite vitre verticale
        rect_vitre = QRectF(
            rect.left() + rect.width() * 0.24,
            rect.top() + rect.height() * 0.10,
            rect.width() * 0.52,
            rect.height() * 0.35,
        )

        painter.setBrush(self.couleur_secondaire.darker(120))

        painter.drawRoundedRect(
            rect_vitre,
            rayon * 0.65,
            rayon * 0.65,
        )

        # Poignée
        painter.setPen(
            QPen(
                self.couleur_secondaire.darker(150),
                max(
                    1.0,
                    hauteur_reference * 0.007,
                ),
            )
        )

        painter.drawLine(
            QPointF(
                rect.right() - rect.width() * 0.18,
                rect.top() + rect.height() * 0.56,
            ),
            QPointF(
                rect.right() - rect.width() * 0.18,
                rect.top() + rect.height() * 0.68,
            ),
        )

    # --------------------------------------------------------------------------
    # Articulations
    # --------------------------------------------------------------------------

    def _dessiner_articulations(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        y_haut = self._borne_haute_caisse(hauteur)

        for x in (
            largeur * 0.008,
            largeur * 0.965,
        ):

            rect = QRectF(
                x,
                y_haut + hauteur * 0.040,
                largeur * 0.027,
                hauteur * 0.455,
            )

            painter.setPen(Qt.PenStyle.NoPen)

            painter.setBrush(QColor("#272C2F"))

            painter.drawRoundedRect(
                rect,
                hauteur * 0.008,
                hauteur * 0.008,
            )

            # Plis verticaux du soufflet
            painter.setPen(
                QPen(
                    QColor("#4A5054"),
                    max(
                        1.0,
                        hauteur * 0.004,
                    ),
                )
            )

            for i in range(1, 5):

                x_ligne = rect.left() + rect.width() * i / 5

                painter.drawLine(
                    QPointF(
                        x_ligne,
                        rect.top(),
                    ),
                    QPointF(
                        x_ligne,
                        rect.bottom(),
                    ),
                )

    # --------------------------------------------------------------------------
    # Bogies articulés
    # --------------------------------------------------------------------------

    def _dessiner_bogie_articule(
        self,
        painter: QPainter,
        centre_x: float,
        hauteur: float,
    ) -> None:
        """
        Dessine un bogie placé sous l'articulation.

        Dans la future rame complète, on pourra demander à une seule des deux
        voitures adjacentes de dessiner le bogie partagé.
        """

        largeur_bogie = hauteur * 0.34

        rect_bogie = QRectF(
            centre_x - largeur_bogie / 2,
            hauteur * 0.695,
            largeur_bogie,
            hauteur * 0.072,
        )

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QColor("#34393D"))

        painter.drawRoundedRect(
            rect_bogie,
            hauteur * 0.017,
            hauteur * 0.017,
        )

        for decalage in (
            -largeur_bogie * 0.27,
            largeur_bogie * 0.27,
        ):

            centre = QPointF(
                centre_x + decalage,
                hauteur * 0.765,
            )

            rayon = hauteur * 0.050

            painter.setBrush(QColor("#1D2225"))

            painter.drawEllipse(
                centre,
                rayon,
                rayon,
            )

            painter.setBrush(QColor("#626C72"))

            painter.drawEllipse(
                centre,
                rayon * 0.52,
                rayon * 0.52,
            )

            painter.setBrush(QColor("#22272A"))

            painter.drawEllipse(
                centre,
                rayon * 0.19,
                rayon * 0.19,
            )

    # --------------------------------------------------------------------------
    # Bas de caisse
    # --------------------------------------------------------------------------

    def _dessiner_bandeau_bas(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        couleur = QColor(self.couleur_secondaire)

        couleur.setAlpha(210)

        chemin = QPainterPath()

        chemin.moveTo(
            largeur * 0.030,
            hauteur * 0.650,
        )

        chemin.lineTo(
            largeur * 0.970,
            hauteur * 0.650,
        )

        chemin.lineTo(
            largeur * 0.970,
            hauteur * 0.690,
        )

        chemin.quadTo(
            largeur * 0.900,
            hauteur * 0.730,
            largeur * 0.820,
            hauteur * 0.730,
        )

        chemin.lineTo(
            largeur * 0.180,
            hauteur * 0.730,
        )

        chemin.quadTo(
            largeur * 0.100,
            hauteur * 0.730,
            largeur * 0.030,
            hauteur * 0.690,
        )

        chemin.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(couleur)

        painter.drawPath(chemin)

    # --------------------------------------------------------------------------
    # Ombre
    # --------------------------------------------------------------------------

    def _dessiner_ombre(
        self,
        painter: QPainter,
        largeur: float,
        hauteur: float,
    ) -> None:

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(
            QColor(
                0,
                0,
                0,
                45,
            )
        )

        painter.drawEllipse(
            QRectF(
                largeur * 0.025,
                hauteur * 0.795,
                largeur * 0.950,
                hauteur * 0.075,
            )
        )

    # --------------------------------------------------------------------------
    # Zones interactives
    # --------------------------------------------------------------------------

    @staticmethod
    def _zone_locale_vers_globale(
        zone: QRectF,
        rect: QRectF,
        sens: int,
    ) -> QRectF:

        if zone.isEmpty():
            return QRectF()

        if sens == 1:

            x = rect.left() + zone.left()

        else:

            x = rect.left() + rect.width() - zone.right()

        return QRectF(
            x,
            rect.top() + zone.top(),
            zone.width(),
            zone.height(),
        )

    def pays_survole(
        self,
        position: QPointF,
    ) -> int | None:
        """
        Renvoie l'indice du pays correspondant à la fenêtre survolée.
        """

        for indice, zone in enumerate(self.zones_pays):

            if zone.contains(position):
                return indice

        return None
