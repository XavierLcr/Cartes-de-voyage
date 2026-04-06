################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4.1 – Partie hémicycle                                                #
################################################################################


import math, copy, textwrap, random, time
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont
from collections import defaultdict
from _0_Utilitaires._0_1_fonctions_utiles_gen import reordonner_dict


# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de calcul de sommes de sommes croissantes -------------------


def somme_filee(lignes, a, b):
    total = 0
    for i in range(lignes):
        total = total + a + i * b
    return total


## 1.2 -- Fonction de suppression des pays présents sur plusieurs continents ---


def valeurs_dans_plusieurs_listes(dictionnaire):
    valeur_cles = defaultdict(list)

    # On parcourt le dictionnaire et on enregistre pour chaque valeur les clés où elle apparaît
    for cle, liste in dictionnaire.items():
        for val in liste:
            valeur_cles[val].append(cle)

    # Ne garder que les valeurs qui apparaissent dans plusieurs listes
    return {val: cles for val, cles in valeur_cles.items() if len(cles) > 1}


## 1.3 -- Fonction de calcul du nombre de pays visités par continent -----------


def nb_pays_visites(
    dict_granu: dict,
    continents: dict,
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
        "North America": ["United States Minor Outlying Isl", "Grenada"],
        "South America": ["Bonaire, Sint Eustatius and Saba", "Panama"],
    },
):

    # Suppression du Moyen-Orient
    if "Middle East" in list(continents.keys()):
        del continents["Middle East"]

    # Suppression des doublons
    continents = {
        continent: [
            pays for pays in liste_pays if pays not in a_supprimer.get(continent, [])
        ]
        for continent, liste_pays in continents.items()
    }

    # Test de vérification de l'absence de doublons
    assert (
        valeurs_dans_plusieurs_listes(continents) == {}
    ), f"Pays en double :{valeurs_dans_plusieurs_listes(continents)}"

    resultat = {}
    for continent in list(continents.keys()):

        resultat[continent] = {
            # Nombre de pays dans le continents
            "total": len(continents[continent]),
            # Nombre de pays visités dans le continent
            "visites": len(
                [
                    i
                    for i in continents[continent]
                    if i
                    # Liste des pays visités
                    in list(
                        set(
                            list((dict_granu.get("region") or {}).keys())
                            + list((dict_granu.get("dep") or {}).keys())
                        )
                    )
                ]
            ),
        }

    return resultat


# 2 -- Classe de création de l'hémicycle des pays visités ----------------------


class HemicycleWidget(QWidget):

    def __init__(
        self,
        constantes,
    ):

        super().__init__()
        self.pays_visites = {"region": {}, "dep": {}}
        self.continents = constantes.liste_regions_monde
        self.constantes = constantes
        self.langue = "français"
        self.num_levels = max(
            min(constantes.parametres_application["n_rangees"], 20), 4
        )  # Nombre de niveaux dans l'hémicycle
        self.base_points = max(
            constantes.parametres_application["points_base"], 5
        )  # Nombre de points de base pour le premier niveau
        self.points_increment = max(
            constantes.parametres_application["points_increment"], 1
        )  # Incrément du nombre de points par niveau
        self.lighter_value = constantes.parametres_application["lighter_value"]
        self.ordre_clefs = [
            "Antarctica",
            "Africa",
            "Europe",
            "Asia",
            "Oceania",
            "North America",
            "South America",
        ]
        self.couleur_texte = "#2C2C2C"
        self.points_visites_position = -1

        # Ajustement du nombre de points par ligne
        self.decalage = len(
            list(self.constantes.hierarchie_par_pays.keys())
        ) - somme_filee(
            lignes=self.num_levels, a=self.base_points, b=self.points_increment
        )
        ## Si le total est trop haut
        while self.decalage < 0:
            self.base_points = max(self.base_points - 1, 10)
            self.points_increment = max(self.points_increment, 4)
            self.decalage = len(
                list(self.constantes.hierarchie_par_pays.keys())
            ) - somme_filee(
                lignes=self.num_levels, a=self.base_points, b=self.points_increment
            )

        # Couleurs pour chaque continent
        self.continent_colors = constantes.parametres_application["couleurs_continents"]
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
            radius = self.base_radius + level * self.level_distance
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

                x = self.center_x() + radius * math.cos(angle_rad)
                y = self.center_y() - radius * math.sin(angle_rad)

                coords_angles.append((x, y, angle, level))

        coords_angles = sorted(coords_angles, key=lambda t: (-t[2], -t[3]))
        assert len(coords_angles) == len(
            list(self.constantes.hierarchie_par_pays.keys())
        ), f"{len(coords_angles)} ≠ {len(list(self.constantes.hierarchie_par_pays.keys()))}"
        return coords_angles

    def relier_coordonnees_continent(self, coord: list, position: int):

        # Tri
        coord = sorted(coord, key=lambda t: (-t[2], -t[3]))

        resultat = []

        for cont in list(self.resume.keys()):

            total_i = self.resume.get(cont)["total"]
            visite_i = self.resume.get(cont)["visites"]

            if position == -1:
                visites_i = [val for val in range(0, visite_i)]
            elif position == 0:
                visites_i = random.sample(range(0, total_i), visite_i)
            else:
                visites_i = [val for val in range(total_i - visite_i, total_i)]

            coord_temp = coord[len(resultat) : (len(resultat) + total_i)]
            for i in range(len(coord_temp)):
                x, y, angle, level = coord_temp[i]
                resultat.append((x, y, angle, level, cont, i in visites_i))

        return resultat

    def renvoyer_couleur(self, visite: bool, continent: str, lighter_value: int):

        col = self.continent_colors.get(continent, None)

        if col is None:
            return QColor(255, 255, 255), QColor(0, 0, 0)
        else:
            return col if visite else col.lighter(lighter_value), col

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x, center_y = self.center_x(), self.center_y()  # Centre du cercle
        rayon_texte = 0  # Coefficient d'éloignement

        self.base_radius = int(
            45 + min(self.width(), self.height()) * 0.15
        )  # Rayon de base pour le premier niveau
        self.level_distance = max(1, int(min(self.width(), self.height()) * 0.09) - 10)
        self.diametre_point = int(min(self.width(), self.height()) * 0.023 - 2)

        coords_angles = self.relier_coordonnees_continent(
            coord=self.creer_coordonnées(), position=self.points_visites_position
        )
        continent_points = {}  # continent: list of (x, y)

        for coord in coords_angles:
            x, y, angle, level, continent, visite = coord
            rayon_texte = max(rayon_texte, abs(y - center_y))
            couleur, couleur_originale = self.renvoyer_couleur(
                continent=continent, visite=visite, lighter_value=self.lighter_value
            )

            # Ajoute le point au bon groupe
            continent_points.setdefault(continent, []).append((x, y))

            # Dessiner le point
            painter.setBrush(QBrush(couleur))  # Remplissage
            painter.setPen(
                QPen(couleur_originale, int(self.diametre_point * 1 / 3))
            )  # Couleur du contour
            painter.drawEllipse(
                QPointF(x, y),
                self.diametre_point,
                self.diametre_point,
            )

        # === Légendes : centrées sur le centroïde === #

        painter.setPen(QColor(self.couleur_texte))
        font = QFont()
        taille_police = max(int(8 + self.level_distance / 10), 1)
        font.setPointSize(taille_police)  # Taille en points

        painter.setFont(font)
        font_metrics = painter.fontMetrics()

        rayon_texte = int(rayon_texte + 9 + self.diametre_point / 1.5)
        for continent, points in continent_points.items():
            if not points:
                continue

            # Nom dans la bonne langue
            nom_affiche = self.constantes.pays_differentes_langues.get(
                continent, {}
            ).get(self.langue, continent)

            # Calcul de l'angle du point par rapport au centre
            theta = math.atan2(
                sum(p[1] for p in points) / len(points) - center_y,
                sum(p[0] for p in points) / len(points) - center_x,
            )

            painter.save()
            painter.translate(
                center_x + rayon_texte * math.cos(theta),
                center_y + rayon_texte * math.sin(theta),
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

    def creer_hemicycle(self):
        self.resume = reordonner_dict(
            nb_pays_visites(
                dict_granu=self.pays_visites,
                continents=copy.copy(self.constantes.liste_regions_monde),
            ),
            clefs=self.ordre_clefs,
        )

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
