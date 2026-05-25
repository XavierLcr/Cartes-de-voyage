################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4.1 – Partie hémicycle                                                #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


import math, copy, random, time
import pandas as pd
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
from collections import defaultdict
from _0_Utilitaires._0_5_isid import isid

# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de calcul de sommes de sommes croissantes -------------------


def somme_filee(lignes, a, b):
    total = 0
    for i in range(lignes):
        total = total + a + i * b
    return total


## 1.2 -- Fonction de calcul du nombre de pays visités par continent -----------


def table_pays_visites(
    dict_granu: dict,
    continents: dict,
    palette: dict,
    clair_indice: float,
    a_supprimer: dict = {
        "Africa": [
            "French Southern Territories",
            "Portugal",
            "Saint Helena, Ascension and Tris",
            "Spain",
        ],
        "Asia": [
            "Akrotiri and Dhekelia",
            "Armenia",
            "Azerbaijan",
            "Cyprus",
            "Egypt",
            "Georgia",
            "Northern Cyprus",
            "Turkey",
        ],
        "Oceania": ["Indonesia"],
        "North America": [
            "United States Minor Outlying Isl",
            "Grenada",
        ],
        "South America": [
            "Bonaire, Sint Eustatius and Saba",
            "Panama",
        ],
    },
):

    continents = continents.copy()

    # Suppression du Moyen-Orient
    if "Middle East" in continents:
        del continents["Middle East"]

    # Suppression doublons
    continents = {
        continent: [
            pays for pays in liste_pays if pays not in a_supprimer.get(continent, [])
        ]
        for continent, liste_pays in continents.items()
    }

    # Récupération des pays visités
    pays_visites = set(
        list((dict_granu.get("region") or {}).keys())
        + list((dict_granu.get("dep") or {}).keys())
    )

    # Création de la table
    lignes = []
    for continent, liste_pays in continents.items():

        # Couleur du continent
        couleur_bord = palette.get(continent, None)
        couleur_centre = (
            couleur_bord.lighter(clair_indice) if couleur_bord else QColor("#FFFFFF")
        )

        for pays in sorted(liste_pays):

            if pays == "Caspian Sea":
                continue

            lignes.append(
                {
                    "continent": continent,
                    "pays": pays,
                    "visite": pays in pays_visites,
                    "couleur_centre": (
                        couleur_bord if pays in pays_visites else couleur_centre
                    ),
                    "couleur_bord": couleur_bord if couleur_bord else QColor("#000000"),
                }
            )

    # Mise au format DataFrame
    df_temp = pd.DataFrame(lignes)

    # Test de granularité
    assert isid(df=df_temp, colonnes="pays", blabla=0)

    # Renvoi
    return df_temp


## 1.3 -- Fonction d'ajout des coordonnées -------------------------------------


def ajouter_coordonnees(df: pd.DataFrame, coordonnees: list, alignement: int):

    df_temp = df.copy().assign(
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

    # Tri des pays dans l'ordre souhaité
    if abs(alignement) == 1:

        df_temp = df_temp.sort_values(
            by=["continent_cat", "visite"],
            inplace=False,
            ascending=(True, alignement == 1),
        ).reset_index(drop=True)

    else:

        df_temp = (
            df_temp.groupby("continent_cat", group_keys=False)
            .apply(lambda x: x.sample(frac=1))
            .reset_index(drop=True)
        )

    # Test de cohérence
    assert len(coordonnees) == len(df_temp), f"{len(coordonnees)} != {len(df_temp)}"

    # Ajout des coordonnées
    df_temp[["x", "y", "angle", "niveau"]] = sorted(
        coordonnees, key=lambda t: (-t[2], -t[3])
    )

    # Renvoi
    return df_temp.drop(columns=["angle", "niveau", "visite"], inplace=False)


# 2 -- Classe de création de l'hémicycle des pays visités ----------------------


class HemicycleWidget(QWidget):

    def __init__(
        self,
        constantes,
    ):

        super().__init__()
        self.pays_visites = {"region": {}, "dep": {}}
        self.continents = constantes.liste_regions_monde
        self.traductions_pays = constantes.pays_differentes_langues
        self.liste_pays = list(constantes.hierarchie_par_pays.keys())
        self.langue = "français"

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
        self.lighter_value = constantes.parametres_application.get("lighter_value")
        self.couleur_texte = "#2C2C2C"
        self.points_visites_position = -1

        # Ajustement du nombre de points par ligne
        self.decalage = len(self.liste_pays) - somme_filee(
            lignes=self.num_levels, a=self.base_points, b=self.points_increment
        )
        ## Si le total est trop haut
        while self.decalage < 0:
            self.base_points = max(self.base_points - 1, 10)
            self.points_increment = max(self.points_increment, 4)
            self.decalage = len(self.liste_pays) - somme_filee(
                lignes=self.num_levels, a=self.base_points, b=self.points_increment
            )

        # Couleurs pour chaque continent
        self.continent_colors = constantes.parametres_application.get(
            "couleurs_continents"
        )
        self.continent_colors = {
            continent: QColor(self.continent_colors.get(continent, col))
            for continent, col in {
                "Africa": "#D1A734",
                "Antarctica": "#20C065",
                "Asia": "#C3423F",
                "Europe": "#7B4B94",
                "North America": "#2A369E",
                "Oceania": "#60B9E2",
                "South America": "#4A7856",
            }.items()
        }

        self.creer_hemicycle()

    def center_x(self):
        return self.width() / 2

    def center_y(self):
        return self.height() * 0.9

    def set_points_visites_position(self, position):
        self.points_visites_position = position

    def get_points_visites_position(self):
        return self.points_visites_position

    def creer_coordonnées(self):

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

    def creer_table_pays_coordonnees(self):

        return (
            # Création de la table des pays
            table_pays_visites(
                dict_granu=self.pays_visites,
                continents=copy.copy(self.continents),
                palette=self.continent_colors,
                clair_indice=self.lighter_value,
            ).pipe(
                # Ajout des coordonnées
                lambda x: ajouter_coordonnees(
                    df=x,
                    coordonnees=self.creer_coordonnées(),
                    alignement=self.points_visites_position,
                )
            )
        )

    def peindre_points(self, painter, df: pd.DataFrame):

        # Coefficient d'éloignement du texte
        rayon_texte = 0

        # Ajout des points
        for row in df.itertuples(index=False):

            # Récupération des informations du point
            x = row.x
            y = row.y
            continent = row.continent
            couleur_bord = row.couleur_bord
            couleur_centre = row.couleur_centre

            # Dessiner le point
            painter.setBrush(QBrush(couleur_centre))
            painter.setPen(QPen(couleur_bord, int(self.diametre_point * 1 / 3)))
            painter.drawEllipse(
                QPointF(x, y),
                self.diametre_point,
                self.diametre_point,
            )

            # Calcul du rayon du texte
            rayon_texte = max(rayon_texte, abs(y - self.center_y()))

        # Renvoi
        return rayon_texte

    def peindre_noms_continents(self, painter, df: pd.DataFrame, rayon: int):

        # Taille du texte
        font_metrics = painter.fontMetrics()

        for continent in list(df["continent"].unique()):

            df_temp = df[df["continent"] == continent].copy()

            if len(df_temp) == 0:
                continue

            # Nom du continent
            nom_affiche = self.traductions_pays.get(continent, {}).get(
                self.langue, continent
            )

            # Calcul de l'angle du point par rapport au centre
            theta = math.atan2(
                df_temp["y"].mean() - self.center_y(),
                df_temp["x"].mean() - self.center_x(),
            )

            painter.save()
            painter.translate(
                self.center_x() + rayon * math.cos(theta),
                self.center_y() + rayon * math.sin(theta),
            )
            # Angle en degrés
            painter.rotate(math.degrees(theta) + 90)

            # Décaler légèrement le texte pour qu’il ne touche pas le point
            painter.drawText(
                QPointF(
                    -font_metrics.horizontalAdvance(nom_affiche) / 2,
                    -font_metrics.height() / 2,
                ),
                nom_affiche,
            )
            painter.restore()

    def calculer_taille_police(self):
        return max(int(8 + self.level_distance / 10), 1)

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
        self.diametre_point = int(min(self.width(), self.height()) * 0.023 - 2)

        # Création de la table des points
        df_temp = self.creer_table_pays_coordonnees()

        # Test de cohérence entre les pays
        assert len(set(self.liste_pays) - set(df_temp["pays"])) == 0
        assert len(set(df_temp["pays"]) - set(self.liste_pays)) == 0

        # Ajout des points
        rayon_texte = self.peindre_points(painter=painter, df=df_temp)

        # Distance du texte
        rayon_texte = int(rayon_texte + 9 + self.diametre_point / 1.5)

        # Application des caractéristiques
        painter.setPen(QColor(self.couleur_texte))
        font = painter.font()
        font.setPointSize(self.calculer_taille_police())
        painter.setFont(font)

        self.peindre_noms_continents(painter=painter, df=df_temp, rayon=rayon_texte)

    def creer_hemicycle(self):
        self.update()

    def set_pays_visites(self, pays_visites):
        """Met à jour la liste des pays visités."""
        self.pays_visites = pays_visites
        random.seed(int(time.time()))
        self.creer_hemicycle()

    def set_langue(self, langue):
        """Met à jour la langue."""
        self.langue = langue
        self.creer_hemicycle()

    def set_style(self, couleur):

        self.couleur_texte = couleur[0] if isinstance(couleur, tuple) else couleur
        self.creer_hemicycle()
