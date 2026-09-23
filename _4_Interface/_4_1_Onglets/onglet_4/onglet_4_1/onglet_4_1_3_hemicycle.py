################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4.1.3 – Partie hémicycle                                              #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


import copy, random, time
import pandas as pd

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtWidgets import QWidget, QToolTip
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QPen

from _0_Utilitaires._0_2_fonctions_graphiques import interpoler_couleurs
from _0_Utilitaires._0_07_fonctions_voyages import table_pays_visites
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_1.onglet_4_1_1_point import PointPays
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_1.onglet_4_1_2_theme import (
    ThemeHemicycle,
)

# 1 -- Classe de création de l'hémicycle des pays visités ----------------------


class HemicycleWidget(QWidget):

    def __init__(
        self,
        constantes,
        df_continents,
    ):

        super().__init__()

        self.setMouseTracking(True)

        self.points = []
        self.positions_ecran = {}

        self.continents = constantes.liste_regions_monde
        self.traductions_pays = constantes.pays_differentes_langues
        self.liste_pays = list(constantes.hierarchie_par_pays.keys())
        # Fond cartographique : on le projette et on le simplifie UNE SEULE FOIS.
        # Une tolérance de 25 km est largement suffisante pour une couche de fond
        # très transparente, y compris avec un zoom assez important.
        self.tolerance_simplification_continents = 25_000.0

        self.df_continents = df_continents

        self._chemins_continents = self._precalculer_chemins_continents(
            self.df_continents
        )

        self.graphe_pays = constantes.graphe_pays

        self.langue = "français"
        self.graine_ordre = None

        self.proportion_min_visible = 0.15

        self._y_min_monde = None
        self._y_max_monde = None

        # ----------------------------------------------------------------------
        # Caméra interactive
        # ----------------------------------------------------------------------

        # Facteur de zoom. À 1.0, le monde entier est cadré comme auparavant.
        self.facteur_zoom = 1.0
        self.facteur_zoom_min = 1.0
        self.facteur_zoom_max = 12.0

        # Centre de la caméra dans les coordonnées projetées EPSG:8857.
        # L'axe X est cyclique : il est ramené en permanence dans une période
        # complète du monde.
        self.centre_camera_x = None
        self.centre_camera_y = None

        # Paramètres géographiques déterminés à partir des données.
        # La largeur cyclique n'est volontairement pas imposée ici : les centres
        # peuvent être en EPSG:8857, en degrés ou dans une autre normalisation.
        self._largeur_monde_geo = None
        self._centre_x_monde = 0.0
        self._centre_y_monde = 0.0
        self._centre_cycle_x = 0.0

        # Paramètres recalculés à chaque peinture. Ils permettent de convertir
        # proprement les déplacements de la souris en coordonnées géographiques.
        self._echelle_monde = 1.0
        self._largeur_monde_ecran = 1.0

        # État du déplacement à la souris.
        self._deplacement_actif = False
        self._derniere_position_souris = None

        # Conservé pour compatibilité avec l'ancienne version
        self.points_visites_position = -1

        # Pays actuellement survolé
        self.pays_survole = None

        # Paramètres esthétiques
        self.transparence_alpha = constantes.parametres_application.get(
            "transparence_alpha"
        )

        # Fond cartographique des continents. Même à 100 % de pays visités,
        # la carte reste volontairement discrète derrière les arêtes et les points.
        self.couleur_continent_neutre = QColor("#8B9098")
        self.alpha_continent_min = 18
        self.alpha_continent_max = 64
        self.alpha_bord_continent = 26

        self.set_style()

        self.set_pays_visites(
            pays_visites={
                "region": {},
                "dep": {},
            }
        )

    # --------------------------------------------------------------------------
    # Pré-calcul des chemins cartographiques
    # --------------------------------------------------------------------------

    @staticmethod
    def _iterer_polygones(geometry):
        """Itère récursivement sur les Polygon contenus dans une géométrie Shapely."""

        if geometry is None or getattr(geometry, "is_empty", True):
            return

        geom_type = getattr(geometry, "geom_type", "")

        if geom_type == "Polygon":
            yield geometry
            return

        if geom_type in {"MultiPolygon", "GeometryCollection"}:
            for sous_geometrie in geometry.geoms:
                yield from HemicycleWidget._iterer_polygones(sous_geometrie)

    @staticmethod
    def _deplier_anneau_geo(
        coordonnees,
        largeur_monde: float,
        reference_x: float | None = None,
    ) -> list[QPointF]:
        """
        Déplie un anneau autour de l'antiméridien dans les coordonnées EPSG:8857.

        Le résultat reste en coordonnées géographiques/projetées, PAS en pixels.
        Cela permet de construire les QPainterPath une seule fois puis de laisser
        QPainter effectuer zoom et déplacement par simple transformation affine.
        """

        coords = list(coordonnees)

        if len(coords) < 3:
            return []

        points = []
        x_precedent = None

        for coord in coords:
            x = float(coord[0])
            y = float(coord[1])

            if x_precedent is not None and largeur_monde > 0:
                while x - x_precedent > largeur_monde / 2:
                    x -= largeur_monde

                while x - x_precedent < -largeur_monde / 2:
                    x += largeur_monde

            points.append(QPointF(x, y))
            x_precedent = x

        # Replace l'anneau dans la période la plus proche de la référence.
        if largeur_monde > 0 and points:
            moyenne_x = sum(point.x() for point in points) / len(points)

            if reference_x is None:
                reference_x = 0.0

            decalages = round((reference_x - moyenne_x) / largeur_monde)

            if decalages:
                decalage_x = decalages * largeur_monde
                points = [
                    QPointF(point.x() + decalage_x, point.y()) for point in points
                ]

        return points

    @staticmethod
    def _ajouter_points_au_chemin(
        chemin: QPainterPath,
        points: list[QPointF],
    ):
        if len(points) < 3:
            return

        chemin.moveTo(points[0])

        for point in points[1:]:
            chemin.lineTo(point)

        chemin.closeSubpath()

    @classmethod
    def _precalculer_chemins_continents(cls, df_continents) -> dict:
        """
        Transforme les géométries Shapely simplifiées en QPainterPath UNE FOIS.

        C'est le gros gain de performance : lors d'un drag ou d'un zoom, Python ne
        reparcourt plus des dizaines/centaines de milliers de sommets. QPainter ne
        fait qu'appliquer une matrice de transformation à quelques chemins déjà prêts.
        """

        if df_continents is None or getattr(df_continents, "empty", True):
            return {}

        # Largeur théorique mondiale de l'Equal Earth EPSG:8857.
        largeur_monde = 34_487_918.12
        chemins = {}

        for ligne in df_continents.itertuples(index=False):
            continent = getattr(ligne, "continent", None)
            geometry = getattr(ligne, "geometry", None)

            if continent is None or geometry is None:
                continue

            chemin_continent = chemins.setdefault(continent, QPainterPath())
            chemin_continent.setFillRule(Qt.FillRule.OddEvenFill)

            for polygone in cls._iterer_polygones(geometry):
                exterieur = cls._deplier_anneau_geo(
                    coordonnees=polygone.exterior.coords,
                    largeur_monde=largeur_monde,
                    reference_x=0.0,
                )

                if len(exterieur) < 3:
                    continue

                reference_polygone = sum(p.x() for p in exterieur) / len(exterieur)

                cls._ajouter_points_au_chemin(
                    chemin=chemin_continent,
                    points=exterieur,
                )

                for interieur in polygone.interiors:
                    trou = cls._deplier_anneau_geo(
                        coordonnees=interieur.coords,
                        largeur_monde=largeur_monde,
                        reference_x=reference_polygone,
                    )

                    cls._ajouter_points_au_chemin(
                        chemin=chemin_continent,
                        points=trou,
                    )

        return chemins

    # --------------------------------------------------------------------------
    # Centre du widget
    # --------------------------------------------------------------------------

    def center_x(self):
        return self.width() / 2

    def center_y(self):
        return self.height() / 2

    # --------------------------------------------------------------------------
    # Compatibilité avec l'ancienne interface
    # --------------------------------------------------------------------------

    def set_points_visites_position(
        self,
        position,
    ):

        self.points_visites_position = position
        self.creer_hemicycle()

    # --------------------------------------------------------------------------
    # Transformation géographique -> écran
    # --------------------------------------------------------------------------

    @staticmethod
    def _delta_x_cyclique(
        x: float,
        centre_x: float,
        largeur_monde: float,
    ) -> float:
        """
        Renvoie l'écart horizontal le plus court entre ``x`` et ``centre_x``.

        L'axe X est considéré comme périodique : passer à droite de l'antiméridien
        fait donc réapparaître naturellement le monde par la gauche, et inversement.
        """

        if largeur_monde <= 0:
            return x - centre_x

        demi_largeur = largeur_monde / 2

        return ((x - centre_x + demi_largeur) % largeur_monde) - demi_largeur

    @staticmethod
    def _determiner_largeur_monde_geo(
        xs: list,
    ) -> tuple[float, float]:
        """
        Détermine la période horizontale des coordonnées.

        Le graphe de l'application peut contenir des coordonnées projetées en
        EPSG:8857, mais cette fonction reste robuste si elles sont finalement
        stockées en degrés ou dans une autre échelle.

        Retourne :
            - la largeur d'un tour du monde ;
            - le centre de référence utilisé pour normaliser la caméra.
        """

        x_min = min(xs)
        x_max = max(xs)
        amplitude = max(x_max - x_min, 1e-12)
        max_abs = max(abs(x) for x in xs)
        centre_donnees = (x_min + x_max) / 2

        # Coordonnées géographiques classiques en degrés.
        if max_abs <= 360.0 and 180.0 <= amplitude <= 360.0:
            return 360.0, 0.0

        # EPSG:8857 (Equal Earth), dont l'étendue mondiale horizontale vaut
        # environ 34 487 918 m. On ne l'utilise que si l'ordre de grandeur des
        # données est compatible, pour ne jamais écraser une autre normalisation.
        largeur_epsg_8857 = 34_487_918.12

        if max_abs >= 1_000_000:
            ratio = amplitude / largeur_epsg_8857

            if 0.55 <= ratio <= 1.08:
                return largeur_epsg_8857, 0.0

        # Cas générique : on prend l'étendue observée avec une petite marge.
        # Ce n'est pas une connaissance géodésique exacte du monde, mais cela
        # garantit un comportement cyclique cohérent sans modifier l'échelle.
        return amplitude * 1.04, centre_donnees

    def _normaliser_camera_x(
        self,
    ):
        """Ramène le centre horizontal de la caméra dans une période du monde."""

        largeur = self._largeur_monde_geo

        if not largeur or largeur <= 0 or self.centre_camera_x is None:
            return

        demi_largeur = largeur / 2
        centre_cycle = self._centre_cycle_x

        self.centre_camera_x = (
            centre_cycle
            + ((self.centre_camera_x - centre_cycle + demi_largeur) % largeur)
            - demi_largeur
        )

    def _calculer_positions_ecran(
        self,
    ):
        """
        Transforme les coordonnées du graphe en coordonnées locales du widget.

        Point important : le cadrage initial est calculé sur l'étendue RÉELLE
        des centres, exactement comme dans la version non interactive. La largeur
        cyclique sert uniquement au bouclage horizontal et ne participe jamais
        au calcul de l'échelle initiale.
        """

        centres = self.graphe_pays.get(
            "centres",
            {},
        )

        centres = {
            pays: coordonnees
            for pays, coordonnees in centres.items()
            if pays in self.liste_pays
        }

        if not centres:
            self.positions_ecran = {}
            return

        xs = [coordonnees[0] for coordonnees in centres.values()]
        ys = [coordonnees[1] for coordonnees in centres.values()]

        x_min = min(xs)
        x_max = max(xs)
        y_min = min(ys)
        y_max = max(ys)

        self._y_min_monde = y_min
        self._y_max_monde = y_max

        amplitude_x = max(
            x_max - x_min,
            1e-12,
        )

        amplitude_y = max(
            y_max - y_min,
            1e-12,
        )

        self._centre_x_monde = (x_min + x_max) / 2
        self._centre_y_monde = (y_min + y_max) / 2

        # La période horizontale est indépendante de l'échelle d'affichage.
        (
            self._largeur_monde_geo,
            self._centre_cycle_x,
        ) = self._determiner_largeur_monde_geo(xs)

        # Initialisation de la caméra au premier affichage. Cela reproduit le
        # cadrage de l'ancien script, même si les coordonnées ne sont pas
        # centrées exactement autour de x = 0.
        if self.centre_camera_x is None:
            self.centre_camera_x = self._centre_x_monde

        if self.centre_camera_y is None:
            self.centre_camera_y = self._centre_y_monde

        # Marge autour du graphe.
        marge = max(
            18,
            min(
                self.width(),
                self.height(),
            )
            * 0.055,
        )

        largeur_disponible = max(
            self.width() - 2 * marge,
            1,
        )

        hauteur_disponible = max(
            self.height() - 2 * marge,
            1,
        )

        # IMPORTANT : même calcul que dans le script d'origine.
        # On n'utilise surtout pas _largeur_monde_geo ici.
        self._echelle_monde = min(
            largeur_disponible / amplitude_x,
            hauteur_disponible / amplitude_y,
        )

        echelle = self._echelle_monde * self.facteur_zoom

        self._largeur_monde_ecran = self._largeur_monde_geo * echelle

        centre_x_widget = self.width() / 2
        centre_y_widget = self.height() / 2

        self.positions_ecran = {}

        for pays, (
            x_geo,
            y_geo,
        ) in centres.items():

            dx_geo = self._delta_x_cyclique(
                x=x_geo,
                centre_x=self.centre_camera_x,
                largeur_monde=self._largeur_monde_geo,
            )

            x = centre_x_widget + dx_geo * echelle

            # L'axe Y de QPainter est inversé.
            y = centre_y_widget - (y_geo - self.centre_camera_y) * echelle

            self.positions_ecran[pays] = QPointF(
                x,
                y,
            )

    def _contraindre_camera(
        self,
    ):
        """
        Contraint la caméra afin d'éviter de perdre complètement la carte.

        Horizontalement, le monde reste cyclique.
        Verticalement, une petite partie du monde doit toujours rester visible.
        """

        # --------------------------------------------------------------------------
        # Axe horizontal : monde cyclique
        # --------------------------------------------------------------------------

        self._normaliser_camera_x()

        # --------------------------------------------------------------------------
        # Axe vertical
        # --------------------------------------------------------------------------

        if (
            self.centre_camera_y is None
            or self._y_min_monde is None
            or self._y_max_monde is None
        ):
            return

        echelle = self._echelle_monde * self.facteur_zoom

        if echelle <= 0:
            return

        hauteur_vue_geo = self.height() / echelle

        # Partie de la fenêtre que l'on autorise à dépasser du monde.
        depassement = hauteur_vue_geo * (1.0 - self.proportion_min_visible)

        y_min_camera = self._y_min_monde - depassement
        y_max_camera = self._y_max_monde + depassement

        self.centre_camera_y = max(
            y_min_camera,
            min(
                self.centre_camera_y,
                y_max_camera,
            ),
        )

    # --------------------------------------------------------------------------
    # Table des pays du graphe
    # --------------------------------------------------------------------------

    def _creer_table_graphe(
        self,
    ) -> pd.DataFrame:

        df = self.df_pays.copy()

        # Traductions
        df["pays_trad"] = df["pays"].map(
            lambda pays: self.traductions_pays.get(
                pays,
                {},
            ).get(
                self.langue,
                pays,
            )
        )

        df["continent_trad"] = df["continent"].map(
            lambda continent: self.traductions_pays.get(
                continent,
                {},
            ).get(
                self.langue,
                continent,
            )
        )

        # On retire les éventuels pays absents du graphe
        df = df.loc[df["pays"].isin(self.positions_ecran)].copy()

        # Coordonnées écran
        df["x"] = df["pays"].map(lambda pays: self.positions_ecran[pays].x())

        df["y"] = df["pays"].map(lambda pays: self.positions_ecran[pays].y())

        return df

    # --------------------------------------------------------------------------
    # Création des points
    # --------------------------------------------------------------------------

    def creer_points(
        self,
        df: pd.DataFrame,
    ) -> list:

        return [
            PointPays(
                x=ligne.x,
                y=ligne.y,
                pays=ligne.pays,
                pays_trad=ligne.pays_trad,
                continent=ligne.continent,
                visite=ligne.visite,
                couleur=ligne.couleur,
                eclaircissement=self.transparence_alpha,
            )
            for ligne in df.itertuples(index=False)
        ]

    # --------------------------------------------------------------------------
    # Carte de fond des continents
    # --------------------------------------------------------------------------

    def _proportions_continents_visites(self) -> dict:
        """Renvoie, pour chaque continent, la part de pays visités entre 0 et 1."""

        if not hasattr(self, "df_pays") or self.df_pays is None or self.df_pays.empty:
            return {}

        if (
            "continent" not in self.df_pays.columns
            or "visite" not in self.df_pays.columns
        ):
            return {}

        df = self.df_pays[["continent", "visite"]].copy()
        df = df.loc[df["continent"].notna()].copy()

        if df.empty:
            return {}

        df["visite"] = df["visite"].astype(bool).astype(float)

        return (
            df.groupby("continent", dropna=True)["visite"]
            .mean()
            .clip(0.0, 1.0)
            .to_dict()
        )

    def _couleur_fond_continent(
        self,
        continent,
        proportion_visitee: float,
    ) -> QColor:
        """
        Interpole un gris neutre vers la couleur du continent selon la part visitée.
        """

        proportion_visitee = max(0.0, min(float(proportion_visitee), 1.0))

        couleur_theme = QColor(
            self.theme.continents_couleurs.get(
                continent,
                self.couleur_continent_neutre,
            )
        )

        couleur = QColor(
            interpoler_couleurs(
                couleurs=[
                    QColor(self.couleur_continent_neutre),
                    couleur_theme,
                ],
                poids=[
                    1.0 - proportion_visitee,
                    proportion_visitee,
                ],
            )
        )

        alpha = self.alpha_continent_min + proportion_visitee * (
            self.alpha_continent_max - self.alpha_continent_min
        )
        couleur.setAlpha(int(round(alpha)))

        return couleur

    def peindre_carte_continents(
        self,
        painter: QPainter,
    ):
        """
        Peint le fond cartographique avec la même caméra que le réseau.

        Les QPainterPath ont déjà été construits au chargement. Ici, aucun sommet
        Shapely n'est reparcouru : zoom et déplacement ne font qu'appliquer une
        transformation affine, ce qui est beaucoup plus léger.
        """

        if not self._chemins_continents:
            return

        if self.centre_camera_x is None or self.centre_camera_y is None:
            return

        echelle = self._echelle_monde * self.facteur_zoom

        if echelle <= 0:
            return

        proportions = self._proportions_continents_visites()

        # Les chemins ont été préparés en EPSG:8857, dont la période horizontale
        # exacte vaut environ 34,49 millions de mètres.
        largeur_monde = 34_487_918.12

        painter.save()

        # Coordonnées projetées -> coordonnées écran.
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(echelle, -echelle)
        painter.translate(-self.centre_camera_x, -self.centre_camera_y)

        for continent, chemin in self._chemins_continents.items():
            proportion = proportions.get(continent, 0.0)

            couleur_remplissage = self._couleur_fond_continent(
                continent=continent,
                proportion_visitee=proportion,
            )

            couleur_bord = QColor(couleur_remplissage)
            couleur_bord.setAlpha(self.alpha_bord_continent)

            pen = QPen(couleur_bord)
            pen.setWidthF(0.8)

            # Le contour reste ~0.8 pixel quelle que soit l'échelle cartographique.
            pen.setCosmetic(True)

            painter.setPen(pen)
            painter.setBrush(couleur_remplissage)

            # Trois périodes suffisent puisque le zoom minimal montre au maximum
            # environ un monde entier. QPainter coupe naturellement le hors-écran.
            for decalage_x in (-largeur_monde, 0.0, largeur_monde):
                painter.save()
                painter.translate(decalage_x, 0.0)
                painter.drawPath(chemin)
                painter.restore()

        painter.restore()

    # --------------------------------------------------------------------------
    # Dessin d'un segment d'arête
    # --------------------------------------------------------------------------

    def _dessiner_segment_arete(
        self,
        painter,
        p1,
        p2,
        couleur,
        epaisseur,
        alpha,
    ):

        couleur = QColor(couleur)

        couleur.setAlpha(
            max(
                0,
                min(
                    int(alpha),
                    255,
                ),
            )
        )

        pen = painter.pen()

        pen.setColor(couleur)

        pen.setWidthF(epaisseur)

        painter.setPen(pen)

        painter.drawLine(
            p1,
            p2,
        )

    # --------------------------------------------------------------------------
    # Interpolation d'un point sur une arête
    # --------------------------------------------------------------------------

    @staticmethod
    def _interpoler_point(
        p1,
        p2,
        t,
    ):

        return QPointF(
            p1.x() + (p2.x() - p1.x()) * t,
            p1.y() + (p2.y() - p1.y()) * t,
        )

    # --------------------------------------------------------------------------
    # Couleur entre deux continents
    # --------------------------------------------------------------------------

    def _couleur_arete(
        self,
        couleur_1,
        couleur_2,
        t=0.5,
    ):

        return interpoler_couleurs(
            couleurs=[
                QColor(couleur_1),
                QColor(couleur_2),
            ],
            poids=[
                1 - t,
                t,
            ],
        )

    # --------------------------------------------------------------------------
    # Dessin d'une arête complètement allumée
    # --------------------------------------------------------------------------

    def _peindre_arete_allumee(
        self,
        painter,
        p1,
        p2,
        couleur_1,
        couleur_2,
        survolee=False,
    ):

        nb_segments = 10

        epaisseur = max(
            1.1,
            self.diametre_point * 0.33,
        )

        # ----------------------------------------------------------------------
        # Halo
        # ----------------------------------------------------------------------

        couleur_halo = self._couleur_arete(
            couleur_1,
            couleur_2,
            0.5,
        )

        self._dessiner_segment_arete(
            painter=painter,
            p1=p1,
            p2=p2,
            couleur=couleur_halo,
            epaisseur=epaisseur * 3.3,
            alpha=55 if survolee else 32,
        )

        # ----------------------------------------------------------------------
        # Trait principal avec transition entre couleurs des continents
        # ----------------------------------------------------------------------

        for i in range(nb_segments):

            t1 = i / nb_segments

            t2 = (i + 1) / nb_segments

            tm = (t1 + t2) / 2

            debut = self._interpoler_point(
                p1,
                p2,
                t1,
            )

            fin = self._interpoler_point(
                p1,
                p2,
                t2,
            )

            couleur = self._couleur_arete(
                couleur_1,
                couleur_2,
                tm,
            )

            self._dessiner_segment_arete(
                painter=painter,
                p1=debut,
                p2=fin,
                couleur=couleur,
                epaisseur=(epaisseur * 1.25 if survolee else epaisseur),
                alpha=235,
            )

    # --------------------------------------------------------------------------
    # Dessin d'une arête partiellement allumée
    # --------------------------------------------------------------------------

    def _peindre_arete_partielle(
        self,
        painter,
        p1,
        p2,
        couleur_1,
        couleur_2,
        premier_visite,
        survolee=False,
    ):
        """
        Si un seul pays est visité, la lumière décroît progressivement en
        s'éloignant de celui-ci.
        """

        nb_segments = 12

        epaisseur = max(
            0.9,
            self.diametre_point * 0.27,
        )

        for i in range(nb_segments):

            t1 = i / nb_segments

            t2 = (i + 1) / nb_segments

            tm = (t1 + t2) / 2

            debut = self._interpoler_point(
                p1,
                p2,
                t1,
            )

            fin = self._interpoler_point(
                p1,
                p2,
                t2,
            )

            # Intensité maximale côté pays visité
            progression = 1 - tm if premier_visite else tm

            # Courbe non linéaire :
            # la lumière tient un peu au départ puis s'éteint
            intensite = progression**1.6

            alpha = 25 + intensite * 165

            if survolee:
                alpha += 25

            couleur = self._couleur_arete(
                couleur_1,
                couleur_2,
                tm,
            )

            self._dessiner_segment_arete(
                painter=painter,
                p1=debut,
                p2=fin,
                couleur=couleur,
                epaisseur=epaisseur,
                alpha=alpha,
            )

    # --------------------------------------------------------------------------
    # Dessin d'une arête éteinte
    # --------------------------------------------------------------------------

    def _peindre_arete_eteinte(
        self,
        painter,
        p1,
        p2,
        couleur_1,
        couleur_2,
        survolee=False,
    ):

        couleur = self._couleur_arete(
            couleur_1,
            couleur_2,
            0.5,
        )

        self._dessiner_segment_arete(
            painter=painter,
            p1=p1,
            p2=p2,
            couleur=couleur,
            epaisseur=max(
                0.7,
                self.diametre_point * 0.20,
            ),
            alpha=(70 if survolee else 30),
        )

    # --------------------------------------------------------------------------
    # Gestion cyclique des arêtes
    # --------------------------------------------------------------------------

    def _copies_arete_cyclique(
        self,
        p1: QPointF,
        p2: QPointF,
    ) -> list:
        """
        Renvoie les copies utiles d'une arête sur le monde cyclique.

        On commence par relier les deux sommets par le chemin horizontal le plus
        court. On dessine ensuite cette arête sur trois périodes voisines. QPainter
        coupe automatiquement ce qui se trouve hors du widget ; cela permet aux
        arêtes de sortir d'un bord et de réapparaître proprement de l'autre.
        """

        largeur = self._largeur_monde_ecran

        if largeur <= 0:
            return [(QPointF(p1), QPointF(p2))]

        x1 = p1.x()
        x2 = p2.x()

        dx = x2 - x1

        if dx > largeur / 2:
            x2 -= largeur
        elif dx < -largeur / 2:
            x2 += largeur

        resultat = []
        marge = max(
            40.0,
            self.diametre_point * 8,
        )

        for decalage in (-largeur, 0.0, largeur):

            q1 = QPointF(
                x1 + decalage,
                p1.y(),
            )

            q2 = QPointF(
                x2 + decalage,
                p2.y(),
            )

            # Évite de peindre inutilement une copie située très loin du widget.
            if (
                max(q1.x(), q2.x()) < -marge
                or min(q1.x(), q2.x()) > self.width() + marge
                or max(q1.y(), q2.y()) < -marge
                or min(q1.y(), q2.y()) > self.height() + marge
            ):
                continue

            resultat.append((q1, q2))

        return resultat

    # --------------------------------------------------------------------------
    # Dessin de toutes les arêtes
    # --------------------------------------------------------------------------

    def peindre_aretes(
        self,
        painter,
        df,
    ):

        if df.empty:
            return

        infos = df.set_index("pays")[
            [
                "continent",
                "visite",
            ]
        ].to_dict(orient="index")

        for (
            pays_1,
            pays_2,
        ) in self.graphe_pays.get(
            "aretes",
            [],
        ):

            if (
                pays_1 not in self.positions_ecran
                or pays_2 not in self.positions_ecran
                or pays_1 not in infos
                or pays_2 not in infos
            ):
                continue

            p1 = self.positions_ecran[pays_1]
            p2 = self.positions_ecran[pays_2]

            info_1 = infos[pays_1]
            info_2 = infos[pays_2]

            visite_1 = bool(info_1["visite"])
            visite_2 = bool(info_2["visite"])

            couleur_1 = self.theme.continents_couleurs.get(
                info_1["continent"],
                "#808080",
            )

            couleur_2 = self.theme.continents_couleurs.get(
                info_2["continent"],
                "#808080",
            )

            # Une arête est renforcée si elle touche le pays survolé.
            survolee = pays_1 == self.pays_survole or pays_2 == self.pays_survole

            # Sur un monde cyclique, une même arête peut apparaître à cheval sur
            # les deux bords de l'écran.
            copies = self._copies_arete_cyclique(
                p1=p1,
                p2=p2,
            )

            for p1_cyclique, p2_cyclique in copies:

                # --------------------------------------------------------------
                # Deux pays visités
                # --------------------------------------------------------------

                if visite_1 and visite_2:

                    self._peindre_arete_allumee(
                        painter=painter,
                        p1=p1_cyclique,
                        p2=p2_cyclique,
                        couleur_1=couleur_1,
                        couleur_2=couleur_2,
                        survolee=survolee,
                    )

                # --------------------------------------------------------------
                # Un seul pays visité
                # --------------------------------------------------------------

                elif visite_1 or visite_2:

                    self._peindre_arete_partielle(
                        painter=painter,
                        p1=p1_cyclique,
                        p2=p2_cyclique,
                        couleur_1=couleur_1,
                        couleur_2=couleur_2,
                        premier_visite=visite_1,
                        survolee=survolee,
                    )

                # --------------------------------------------------------------
                # Aucun pays visité
                # --------------------------------------------------------------

                else:

                    self._peindre_arete_eteinte(
                        painter=painter,
                        p1=p1_cyclique,
                        p2=p2_cyclique,
                        couleur_1=couleur_1,
                        couleur_2=couleur_2,
                        survolee=survolee,
                    )

    # --------------------------------------------------------------------------
    # Caméra interactive
    # --------------------------------------------------------------------------

    def reinitialiser_vue(
        self,
    ):
        """Rétablit le cadrage mondial initial."""

        self.facteur_zoom = 1.0
        self.centre_camera_x = self._centre_x_monde
        self.centre_camera_y = self._centre_y_monde

        self.pays_survole = None
        QToolTip.hideText()

        self.creer_hemicycle()

    def _zoomer_sur_position(
        self,
        position: QPointF,
        nouveau_zoom: float,
    ):
        """
        Modifie le zoom en conservant sous la souris le même point géographique.
        """

        ancien_zoom = self.facteur_zoom

        nouveau_zoom = max(
            self.facteur_zoom_min,
            min(
                nouveau_zoom,
                self.facteur_zoom_max,
            ),
        )

        if abs(nouveau_zoom - ancien_zoom) < 1e-12:
            return

        if self._echelle_monde <= 0:
            return

        if self.centre_camera_y is None:
            self.centre_camera_y = self._centre_y_monde

        centre_x_widget = self.width() / 2
        centre_y_widget = self.height() / 2

        # Coordonnée géographique actuellement située sous le curseur.
        x_geo_souris = self.centre_camera_x + (position.x() - centre_x_widget) / (
            self._echelle_monde * ancien_zoom
        )

        y_geo_souris = self.centre_camera_y - (position.y() - centre_y_widget) / (
            self._echelle_monde * ancien_zoom
        )

        self.facteur_zoom = nouveau_zoom

        # Nouveau centre nécessaire pour que ce même point géographique reste
        # exactement sous le curseur après le changement d'échelle.
        self.centre_camera_x = x_geo_souris - (position.x() - centre_x_widget) / (
            self._echelle_monde * nouveau_zoom
        )

        self.centre_camera_y = y_geo_souris + (position.y() - centre_y_widget) / (
            self._echelle_monde * nouveau_zoom
        )

        self._contraindre_camera()

        self.creer_hemicycle()

    # --------------------------------------------------------------------------
    # Dessin des points
    # --------------------------------------------------------------------------

    def peindre_points(
        self,
        painter,
        df,
    ):

        self.points = self.creer_points(df=df)

        epaisseur_bord = max(
            0.8,
            self.diametre_point * 0.28,
        )

        for point in self.points:

            point.peindre(
                painter=painter,
                diametre=self.diametre_point,
                epaisseur_bord=epaisseur_bord,
                survole=(point.pays == self.pays_survole),
                facteur_survol=1.55,
            )

    # --------------------------------------------------------------------------
    # Dessin principal
    # --------------------------------------------------------------------------

    def paintEvent(
        self,
        event,
    ):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ----------------------------------------------------------------------
        # Taille des stations
        # ----------------------------------------------------------------------

        dimension = min(
            self.width(),
            self.height(),
        )

        # Attention : PointPays utilise cette valeur comme rayon.
        self.diametre_point = max(
            2.5,
            dimension * 0.008,
        )

        # ----------------------------------------------------------------------
        # Positionnement géographique
        # ----------------------------------------------------------------------

        self._calculer_positions_ecran()

        df_temp = self._creer_table_graphe()

        # ----------------------------------------------------------------------
        # Carte de fond : elle suit exactement la même caméra que le réseau
        # ----------------------------------------------------------------------

        self.peindre_carte_continents(
            painter=painter,
        )

        # ----------------------------------------------------------------------
        # Les lignes sont dessinées au-dessus de la carte
        # ----------------------------------------------------------------------

        self.peindre_aretes(
            painter=painter,
            df=df_temp,
        )

        # ----------------------------------------------------------------------
        # Stations au-dessus
        # ----------------------------------------------------------------------

        self.peindre_points(
            painter=painter,
            df=df_temp,
        )

    # --------------------------------------------------------------------------
    # Rafraîchissement
    # --------------------------------------------------------------------------

    def creer_hemicycle(
        self,
    ):

        self.update()

    # --------------------------------------------------------------------------
    # Pays visités
    # --------------------------------------------------------------------------

    def set_pays_visites(
        self,
        pays_visites,
    ):

        self.df_pays = table_pays_visites(
            dict_granu=pays_visites,
            continents=copy.copy(self.continents),
            palette=(self.theme.continents_couleurs),
            a_supprimer=None,
        )

        self.graine_ordre = random.Random(int(time.time())).randint(
            0,
            1_000_000,
        )

        self.creer_hemicycle()

    # --------------------------------------------------------------------------
    # Langue
    # --------------------------------------------------------------------------

    def set_langue(
        self,
        langue,
    ):

        self.langue = langue
        self.creer_hemicycle()

    # --------------------------------------------------------------------------
    # Style
    # --------------------------------------------------------------------------

    def set_style(
        self,
        style: int = 1,
        teinte=None,
        nuances={},
    ):

        self.theme = ThemeHemicycle(
            parent=self,
            style=style,
            teinte=teinte,
            nuances=nuances,
        )

        self.creer_hemicycle()

    # --------------------------------------------------------------------------
    # Interaction à la souris
    # --------------------------------------------------------------------------

    def wheelEvent(
        self,
        event,
    ):
        """Zoom à la molette, centré sur la position du curseur."""

        delta = event.angleDelta().y()

        if delta == 0:
            event.ignore()
            return

        # Une graduation classique de molette correspond à 120 unités.
        nb_pas = delta / 120.0
        facteur = 1.18**nb_pas

        self._zoomer_sur_position(
            position=event.position(),
            nouveau_zoom=self.facteur_zoom * facteur,
        )

        event.accept()

    def mousePressEvent(
        self,
        event,
    ):
        """Démarre le déplacement de la carte au clic gauche."""

        if event.button() == Qt.MouseButton.LeftButton:

            self._deplacement_actif = True
            self._derniere_position_souris = event.position()

            self.pays_survole = None
            QToolTip.hideText()

            self.setCursor(Qt.CursorShape.ClosedHandCursor)

            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(
        self,
        event,
    ):

        pos = event.position()

        # ----------------------------------------------------------------------
        # Déplacement de la caméra
        # ----------------------------------------------------------------------

        if self._deplacement_actif and self._derniere_position_souris is not None:

            delta = pos - self._derniere_position_souris
            self._derniere_position_souris = pos

            echelle = self._echelle_monde * self.facteur_zoom

            if echelle > 0:

                # Déplacer la souris vers la droite fait glisser le contenu vers
                # la droite : le centre géographique de la caméra part donc vers
                # la gauche. Pour Y, l'axe écran est inversé.
                self.centre_camera_x -= delta.x() / echelle

                if self.centre_camera_y is None:
                    self.centre_camera_y = self._centre_y_monde

                self.centre_camera_y += delta.y() / echelle

                self._contraindre_camera()

                self.creer_hemicycle()

            event.accept()
            return

        # ----------------------------------------------------------------------
        # Survol des pays
        # ----------------------------------------------------------------------

        nouveau_survol = None

        for point in self.points:

            if point.est_survole(
                pos.x(),
                pos.y(),
                self.diametre_point,
                tolerance=1.45,
            ):

                QToolTip.showText(
                    event.globalPosition().toPoint(),
                    point.pays_trad,
                    self,
                )

                nouveau_survol = point.pays

                break

        if nouveau_survol is None:
            QToolTip.hideText()

        # Les arêtes connectées au pays survolé sont également renforcées.
        if nouveau_survol != self.pays_survole:

            self.pays_survole = nouveau_survol
            self.creer_hemicycle()

    def mouseReleaseEvent(
        self,
        event,
    ):
        """Termine le déplacement de la carte."""

        if event.button() == Qt.MouseButton.LeftButton:

            self._deplacement_actif = False
            self._derniere_position_souris = None

            self.unsetCursor()

            event.accept()
            return

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(
        self,
        event,
    ):
        """Un double-clic gauche rétablit la vue mondiale."""

        if event.button() == Qt.MouseButton.LeftButton:

            self.reinitialiser_vue()
            event.accept()
            return

        super().mouseDoubleClickEvent(event)
