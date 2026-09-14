################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4.1.3 – Partie hémicycle                                              #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


import copy, random, time
import pandas as pd

from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QWidget, QToolTip
from PyQt6.QtGui import QPainter, QColor

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
    ):

        super().__init__()

        self.setMouseTracking(True)

        self.points = []
        self.positions_ecran = {}

        self.continents = constantes.liste_regions_monde
        self.traductions_pays = constantes.pays_differentes_langues
        self.liste_pays = list(constantes.hierarchie_par_pays.keys())

        self.graphe_pays = constantes.graphe_pays

        self.langue = "français"
        self.graine_ordre = None

        # Zone actuellement affichée
        self.zoom_continent = "World"

        # Conservé pour compatibilité avec l'ancienne version
        self.points_visites_position = -1

        # Pays actuellement survolé
        self.pays_survole = None

        # Paramètres esthétiques
        self.transparence_alpha = constantes.parametres_application.get(
            "transparence_alpha"
        )

        self.set_style()

        self.set_pays_visites(
            pays_visites={
                "region": {},
                "dep": {},
            }
        )

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

    def _calculer_positions_ecran(
        self,
    ):
        """
        Transforme les coordonnées EPSG:8857 contenues dans le graphe en
        coordonnées locales du widget.

        Pour ``World``, le cadrage utilise tous les pays. Pour un continent,
        le cadrage est calculé uniquement sur les pays de ce continent, mais
        tous les pays du graphe restent transformés et dessinés. Les pays hors
        de la zone sélectionnée sortent donc naturellement du widget.

        L'échelle reste identique sur X et Y afin de ne jamais déformer la
        géographie.
        """

        centres = self.graphe_pays.get(
            "centres",
            {},
        )

        # On ne conserve que les pays connus de l'application
        centres = {
            pays: coordonnees
            for pays, coordonnees in centres.items()
            if pays in self.liste_pays
        }

        if not centres:
            self.positions_ecran = {}
            return

        # ----------------------------------------------------------------------
        # Étendue géographique du monde entier
        # ----------------------------------------------------------------------

        xs_monde = [coordonnees[0] for coordonnees in centres.values()]
        ys_monde = [coordonnees[1] for coordonnees in centres.values()]

        amplitude_x_monde = max(
            max(xs_monde) - min(xs_monde),
            1,
        )

        amplitude_y_monde = max(
            max(ys_monde) - min(ys_monde),
            1,
        )

        # ----------------------------------------------------------------------
        # Pays utilisés pour déterminer le cadrage
        # ----------------------------------------------------------------------

        centres_cadrage = centres

        if self.zoom_continent != "World" and hasattr(self, "df_pays"):

            pays_continent = set(
                self.df_pays.loc[
                    self.df_pays["continent"] == self.zoom_continent,
                    "pays",
                ]
            )

            centres_continent = {
                pays: coordonnees
                for pays, coordonnees in centres.items()
                if pays in pays_continent
            }

            # Sécurité si le nom du continent n'existe pas dans les données
            if centres_continent:
                centres_cadrage = centres_continent

        xs = [coordonnees[0] for coordonnees in centres_cadrage.values()]
        ys = [coordonnees[1] for coordonnees in centres_cadrage.values()]

        x_min = min(xs)
        x_max = max(xs)

        y_min = min(ys)
        y_max = max(ys)

        centre_x_geo = (x_min + x_max) / 2
        centre_y_geo = (y_min + y_max) / 2

        amplitude_x = max(
            x_max - x_min,
            1,
        )

        amplitude_y = max(
            y_max - y_min,
            1,
        )

        # Un continent très petit ou ne contenant qu'un seul point ne doit pas
        # provoquer un zoom démesuré. On impose donc une fenêtre géographique
        # minimale par rapport à l'étendue du monde.
        if self.zoom_continent != "World":

            amplitude_x = max(
                amplitude_x,
                amplitude_x_monde * 0.18,
            )

            amplitude_y = max(
                amplitude_y,
                amplitude_y_monde * 0.18,
            )

        # ----------------------------------------------------------------------
        # Passage aux coordonnées du widget
        # ----------------------------------------------------------------------

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

        # Une seule échelle : pas de déformation
        echelle = min(
            largeur_disponible / amplitude_x,
            hauteur_disponible / amplitude_y,
        )

        centre_x_widget = self.width() / 2
        centre_y_widget = self.height() / 2

        self.positions_ecran = {}

        for pays, (
            x_geo,
            y_geo,
        ) in centres.items():

            x = centre_x_widget + (x_geo - centre_x_geo) * echelle

            # L'axe Y de QPainter est inversé
            y = centre_y_widget - (y_geo - centre_y_geo) * echelle

            self.positions_ecran[pays] = QPointF(
                x,
                y,
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

            # Une arête est renforcée si elle touche le pays survolé
            survolee = pays_1 == self.pays_survole or pays_2 == self.pays_survole

            # ------------------------------------------------------------------
            # Deux pays visités
            # ------------------------------------------------------------------

            if visite_1 and visite_2:

                self._peindre_arete_allumee(
                    painter=painter,
                    p1=p1,
                    p2=p2,
                    couleur_1=couleur_1,
                    couleur_2=couleur_2,
                    survolee=survolee,
                )

            # ------------------------------------------------------------------
            # Un seul pays visité
            # ------------------------------------------------------------------

            elif visite_1 or visite_2:

                self._peindre_arete_partielle(
                    painter=painter,
                    p1=p1,
                    p2=p2,
                    couleur_1=couleur_1,
                    couleur_2=couleur_2,
                    premier_visite=visite_1,
                    survolee=survolee,
                )

            # ------------------------------------------------------------------
            # Aucun pays visité
            # ------------------------------------------------------------------

            else:

                self._peindre_arete_eteinte(
                    painter=painter,
                    p1=p1,
                    p2=p2,
                    couleur_1=couleur_1,
                    couleur_2=couleur_2,
                    survolee=survolee,
                )

    # --------------------------------------------------------------------------
    # Zoom
    # --------------------------------------------------------------------------

    def set_zoom_continent(
        self,
        continent: str = "World",
    ):
        """
        Sélectionne la zone géographique utilisée pour cadrer le graphe.

        ``World`` correspond à l'absence de zoom. Les autres valeurs doivent
        être les références anglaises utilisées dans ``df_pays["continent"]``.
        """

        self.zoom_continent = continent
        self.pays_survole = None
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
        # Les lignes sont dessinées en premier
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
    # Survol
    # --------------------------------------------------------------------------

    def mouseMoveEvent(
        self,
        event,
    ):

        pos = event.position()

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
