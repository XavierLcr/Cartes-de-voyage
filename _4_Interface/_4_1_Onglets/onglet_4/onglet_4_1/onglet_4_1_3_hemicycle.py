################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4.1.3 – Partie hémicycle                                              #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


import math, copy, random, time
import pandas as pd

from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QWidget, QToolTip
from PyQt6.QtGui import QPainter, QColor

from _0_Utilitaires._0_7_fonctions_voyages import table_pays_visites
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_1.onglet_4_1_1_point import PointPays
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_1.onglet_4_1_2_theme import (
    ThemeHemicycle,
)

# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction d'ajout des coordonnées -------------------------------------


def ajouter_coordonnees(
    df: pd.DataFrame,
    coordonnees: list,
    alignement: int,
    traduction: dict,
    langue: str,
    graine: int = None,
):

    df_temp = (
        df.copy()
        .assign(
            continent_cat=lambda x: pd.Categorical(
                x["continent"],
                categories=[
                    "Antarctica",
                    "Africa",
                    "Europe",
                    "Asia",
                    "Oceania",
                    "North America",
                    "South America",
                ],
                ordered=True,
            )
        )
        .assign(
            continent_trad=lambda x: x["continent"].map(
                lambda c: traduction.get(c, {}).get(langue, c)
            ),
            pays_trad=lambda x: x["pays"].map(
                lambda c: traduction.get(c, {}).get(langue, c)
            ),
        )
    )

    # Tri des pays dans l'ordre souhaité
    if abs(alignement) == 1:

        df_temp = df_temp.sort_values(
            by=["continent_cat", "visite"],
            inplace=False,
            ascending=(True, alignement == 1),
        ).reset_index(drop=True)

    elif alignement == 2:
        df_temp = df_temp.sort_values(
            by=["continent_cat", "pays_trad"],
            inplace=False,
            ascending=(True, True),
        ).reset_index(drop=True)

    else:

        df_temp = (
            df_temp.sample(frac=1, random_state=graine)
            .sort_values("continent_cat", kind="stable")
            .reset_index(drop=True)
        )

    # Test de cohérence
    assert len(coordonnees) == len(df_temp), f"{len(coordonnees)} != {len(df_temp)}"

    # Ajout des coordonnées
    df_temp[["x", "y", "angle", "niveau"]] = sorted(
        coordonnees, key=lambda t: (-t[2], -t[3])
    )

    # Renvoi
    return df_temp.drop(columns=["angle", "niveau"], inplace=False)


# 2 -- Classe de création de l'hémicycle des pays visités ----------------------


class HemicycleWidget(QWidget):

    def __init__(
        self,
        constantes,
    ):

        super().__init__()

        self.setMouseTracking(True)
        self.points = []  # Liste d'objets PointPays affichés au dernier paintEvent

        self.continents = constantes.liste_regions_monde
        self.traductions_pays = constantes.pays_differentes_langues
        self.liste_pays = list(constantes.hierarchie_par_pays.keys())
        self.langue = "français"
        self.graine_ordre = None

        # Nombre de niveaux dans l'hémicycle
        self.num_levels = max(
            min(constantes.parametres_application["n_rangees"], 20), 4
        )

        # Nombre de points de base pour le premier niveau
        self.base_points = max(constantes.parametres_application["points_base"], 5)

        # Incrément du nombre de points par niveau
        self.points_increment = max(
            constantes.parametres_application["points_increment"], 1
        )

        # Paramètres esthétiques
        self.transparence_alpha = constantes.parametres_application.get(
            "transparence_alpha"
        )
        self.points_visites_position = -1

        # Pays actuellement survolé par la souris
        self.pays_survole = None

        # Ajustement du nombre de points par ligne
        self.decalage = len(self.liste_pays) - self.somme_filee()
        ## Si le total est trop haut
        while self.decalage < 0:
            self.base_points = max(self.base_points - 1, 10)
            self.points_increment = max(self.points_increment, 4)
            self.decalage = len(self.liste_pays) - self.somme_filee()

        self.set_style()
        self.set_pays_visites(pays_visites={"region": {}, "dep": {}})

    def center_x(self):
        return self.width() / 2

    def center_y(self):
        return self.height() * 0.9

    def somme_filee(self):

        # Récupération des valeurs
        lignes = self.num_levels
        a = self.base_points
        b = self.points_increment

        # Calcul et renvoi
        return lignes * a + b * (lignes * (lignes - 1) // 2)

    def set_points_visites_position(self, position):
        self.points_visites_position = position

    def get_points_visites_position(self):
        return self.points_visites_position

    def creer_coordonnees(self):

        coords_angles = []

        for level in range(self.num_levels):

            num_points = (
                # Points de base
                self.base_points
                + self.decalage // self.num_levels
                # Incément
                + level * self.points_increment
                # Écart
                + (
                    1
                    if (self.decalage % self.num_levels) >= (self.num_levels - level)
                    else 0
                )
            )

            for i in range(num_points):
                angle = (180.0 / (num_points - 1)) * i if num_points > 1 else 90
                angle_rad = math.radians(angle)

                radius = self.base_radius + level * self.level_distance
                x = self.center_x() + radius * math.cos(angle_rad)
                y = self.center_y() - radius * math.sin(angle_rad)

                coords_angles.append((x, y, angle, level))

        # Renvoi
        return coords_angles

    def creer_points(self, df: pd.DataFrame) -> list:
        """Construit la liste des objets PointPays à partir de la table de données."""

        return [
            PointPays(
                x=ligne_temp.x,
                y=ligne_temp.y,
                pays=ligne_temp.pays,
                pays_trad=ligne_temp.pays_trad,
                continent=ligne_temp.continent,
                visite=ligne_temp.visite,
                couleur=ligne_temp.couleur,
                eclaircissement=self.transparence_alpha,
            )
            for ligne_temp in df.itertuples(index=False)
        ]

    def peindre_points(self, painter, df: pd.DataFrame):

        # Coefficient d'éloignement du texte
        rayon_texte = 0

        # Construction des points à partir de la table
        self.points = self.creer_points(df=df)

        epaisseur_bord = int(self.diametre_point * 1 / 3)

        for point in self.points:

            point.peindre(
                painter=painter,
                diametre=self.diametre_point,
                epaisseur_bord=epaisseur_bord,
                survole=(point.pays_trad == self.pays_survole),
            )

            # Calcul du rayon du texte
            rayon_texte = max(rayon_texte, abs(point.y - self.center_y()))

        # Renvoi
        return rayon_texte

    def _peindre_texte_par_continent(self, painter, df, rayon, taille_police, texte_fn):
        font = painter.font()
        font.setPointSize(taille_police)
        painter.setFont(font)
        font_metrics = painter.fontMetrics()

        for continent in df["continent"].unique():
            df_temp = df[df["continent"] == continent]
            if df_temp.empty:
                continue

            texte = texte_fn(df_temp)
            theta = math.atan2(
                df_temp["y"].mean() - self.center_y(),
                df_temp["x"].mean() - self.center_x(),
            )

            painter.save()
            painter.translate(
                self.center_x() + rayon * math.cos(theta),
                self.center_y() + rayon * math.sin(theta),
            )
            painter.rotate(math.degrees(theta) + 90)
            painter.drawText(
                QPointF(
                    -font_metrics.horizontalAdvance(texte) / 2,
                    -font_metrics.height() / 2,
                ),
                texte,
            )
            painter.restore()

    def peindre_noms_continents(self, painter, df, rayon):
        self._peindre_texte_par_continent(
            painter,
            df,
            rayon,
            self.calculer_taille_police(),
            lambda d: d["continent_trad"].unique()[0],
        )

    def peindre_ratios_visites(self, painter, df, rayon):
        self._peindre_texte_par_continent(
            painter,
            df,
            rayon,
            max(self.calculer_taille_police() - 1, 1),
            lambda d: f"{d['visite'].sum()}/{len(d)}",
        )

    def calculer_taille_police(self):
        return max(int(7 + self.level_distance / 8), 1)

    def paintEvent(self, event):

        # Initialisation
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x, center_y = self.center_x(), self.center_y()  # Centre du cercle

        # Mise à jour des dimensions du graphique
        self.base_radius = int(
            45 + min(self.width(), self.height()) * 0.15
        )  # Rayon de base pour le premier niveau
        self.level_distance = max(1, int(min(self.width(), self.height()) * 0.09) - 10)
        self.diametre_point = max(int(min(self.width(), self.height()) * 0.023 - 2), 1)

        # Création de la table des points
        df_temp = self.df_pays.pipe(
            # Ajout des coordonnées
            lambda x: ajouter_coordonnees(
                df=x,
                coordonnees=self.creer_coordonnees(),
                alignement=self.points_visites_position,
                traduction=self.traductions_pays,
                langue=self.langue,
                graine=self.graine_ordre,
            )
        )

        # Test de cohérence entre les pays
        assert len(set(self.liste_pays) - set(df_temp["pays"])) == 0
        assert len(set(df_temp["pays"]) - set(self.liste_pays)) == 0

        # Ajout des points
        rayon_texte = self.peindre_points(painter=painter, df=df_temp)

        # Distance du texte
        rayon_texte = int(rayon_texte + 4 + self.diametre_point / 1.5)

        # Application des caractéristiques
        painter.setPen(QColor(self.theme.couleur_texte))

        # Ajout des ratios de pays visités
        self.peindre_ratios_visites(painter=painter, df=df_temp, rayon=rayon_texte)

        # Ajout du nom des continents
        self.peindre_noms_continents(
            painter=painter,
            df=df_temp,
            rayon=rayon_texte + 10 + self.diametre_point / 1.5,
        )

    def creer_hemicycle(self):
        self.update()

    def set_pays_visites(self, pays_visites):
        """Met à jour la table des pays visités."""
        # Création de la table des pays
        self.df_pays = table_pays_visites(
            dict_granu=pays_visites,
            continents=copy.copy(self.continents),
            palette=self.theme.continents_couleurs,
            a_supprimer=None,
        )
        self.graine_ordre = random.Random(int(time.time())).randint(0, 1_000_000)
        self.creer_hemicycle()

    def set_langue(self, langue):
        """Met à jour la langue."""
        self.langue = langue
        self.creer_hemicycle()

    def set_style(self, style: int = 1, teinte=None, nuances={}):

        self.theme = ThemeHemicycle(
            parent=self, style=style, teinte=teinte, nuances=nuances
        )

        self.creer_hemicycle()

    def mouseMoveEvent(self, event):

        pos = event.position()  # QPointF, coordonnées locales au widget
        nouveau_survol = None

        for point in self.points:
            if point.est_survole(pos.x(), pos.y(), self.diametre_point):
                QToolTip.showText(
                    event.globalPosition().toPoint(), point.pays_trad, self
                )
                nouveau_survol = point.pays_trad
                break

        if nouveau_survol is None:
            QToolTip.hideText()

        # Redessiner uniquement si le pays survolé a changé, pour éviter
        # de redessiner l'hémicycle à chaque micro-mouvement de la souris
        if nouveau_survol != self.pays_survole:
            self.pays_survole = nouveau_survol
            self.creer_hemicycle()
