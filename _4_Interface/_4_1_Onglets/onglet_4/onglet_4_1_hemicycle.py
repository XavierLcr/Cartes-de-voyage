################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4.1 – Partie hémicycle                                                #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


import math, copy, random, time
import pandas as pd
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QWidget, QToolTip
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QRadialGradient
from _0_Utilitaires._0_5_isid import isid

# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de calcul de sommes de sommes croissantes -------------------


def somme_filee(lignes, a, b):
    return lignes * a + b * (lignes * (lignes - 1) // 2)


## 1.2 -- Fonction de calcul du nombre de pays visités par continent -----------


def table_pays_visites(
    dict_granu: dict,
    continents: dict,
    palette: dict,
    clair_indice: float,
    a_supprimer: dict | None = None,
):

    continents = continents.copy()
    if a_supprimer is None:
        a_supprimer = {
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
        }

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
        self.points_hover = []

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

        self.set_pays_visites(pays_visites={"region": {}, "dep": {}})
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

    def peindre_points(self, painter, df: pd.DataFrame):

        # Coefficient d'éloignement du texte
        rayon_texte = 0

        self.points_hover = []

        epaisseur_bord = int(self.diametre_point * 1 / 3)

        for ligne_temp in df.itertuples(index=False):

            # Récupération des informations du point
            x = ligne_temp.x
            y = ligne_temp.y
            couleur_bord = ligne_temp.couleur_bord
            couleur_centre = ligne_temp.couleur_centre

            # Dégradé radial très subtil, juste pour donner un peu de volume
            gradient = QRadialGradient(
                QPointF(x - self.diametre_point * 0.25, y - self.diametre_point * 0.25),
                self.diametre_point * 1.3,
            )
            gradient.setColorAt(0.0, couleur_centre.lighter(120))
            gradient.setColorAt(1.0, couleur_centre)

            # Dessiner le point
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(couleur_bord, epaisseur_bord))
            painter.drawEllipse(
                QPointF(x, y),
                self.diametre_point,
                self.diametre_point,
            )

            self.points_hover.append((x, y, self.diametre_point, ligne_temp.pays_trad))

            # Calcul du rayon du texte
            rayon_texte = max(rayon_texte, abs(y - self.center_y()))

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
        self.diametre_point = int(min(self.width(), self.height()) * 0.023 - 2)

        # Création de la table des points
        df_temp = self.df_pays.pipe(
            # Ajout des coordonnées
            lambda x: ajouter_coordonnees(
                df=x,
                coordonnees=self.creer_coordonnées(),
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
        painter.setPen(QColor(self.couleur_texte))

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
            palette=self.continent_colors,
            clair_indice=self.lighter_value,
            a_supprimer=None,
        )
        self.graine_ordre = random.Random(int(time.time())).randint(0, 1_000_000)
        self.creer_hemicycle()

    def set_langue(self, langue):
        """Met à jour la langue."""
        self.langue = langue
        self.creer_hemicycle()

    def set_style(self, couleur):

        self.couleur_texte = couleur[0] if isinstance(couleur, tuple) else couleur
        self.creer_hemicycle()

    def mouseMoveEvent(self, event):

        pos = event.position()  # QPointF, coordonnées locales au widget

        for x, y, rayon, nom in self.points_hover:
            distance = math.hypot(pos.x() - x, pos.y() - y)
            # Marge de tolérance un peu plus large que le point lui-même
            if distance <= rayon * 1.1:
                QToolTip.showText(event.globalPosition().toPoint(), nom, self)
                return

        QToolTip.hideText()
