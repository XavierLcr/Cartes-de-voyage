################################################################################
# Projet de cartes de voyage                                                   #
# application/onglets/onglet_4                                                 #
# Onglet 4 – Partie hémicycle                                                  #
################################################################################


import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont
from collections import defaultdict
from application.fonctions_utiles_2_0 import reordonner_dict


def somme_filee(lignes, a, b):
    total = 0
    for i in range(lignes):
        total = total + a + i * b
    return total


def valeurs_dans_plusieurs_listes(dictionnaire):
    valeur_cles = defaultdict(list)

    # On parcourt le dictionnaire et on enregistre pour chaque valeur les clés où elle apparaît
    for cle, liste in dictionnaire.items():
        for val in liste:
            valeur_cles[val].append(cle)

    # Ne garder que les valeurs qui apparaissent dans plusieurs listes
    return {val: cles for val, cles in valeur_cles.items() if len(cles) > 1}


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
        continent: [pays for pays in liste_pays if pays not in a_supprimer.get(continent, [])]
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
                        set(list(dict_granu["region"].keys()) + list(dict_granu["dep"].keys()))
                    )
                ]
            ),
        }

    return resultat


# Classe de type hémicycle
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

        # Ajustement du nombre de points par ligne
        self.decalage = len(list(self.constantes.departements_par_pays.keys())) - somme_filee(
            lignes=self.num_levels, a=self.base_points, b=self.points_increment
        )
        ## Si le total est trop haut
        while self.decalage < 0:
            self.base_points = max(self.base_points - 1, 10)
            self.points_increment = max(self.points_increment, 4)
            self.decalage = len(
                list(self.constantes.departements_par_pays.keys())
            ) - somme_filee(
                lignes=self.num_levels, a=self.base_points, b=self.points_increment
            )

        # Couleurs pour chaque continent
        self.continent_colors = constantes.parametres_application["couleurs_continents"]
        self.continent_colors = {
            "Africa": QColor(self.continent_colors.get("Africa", "#3454D1")),
            "Antarctica": QColor(self.continent_colors.get("Antarctica", "#2E8B57")),
            "Asia": QColor(self.continent_colors.get("Asia", "#C3423F")),
            "Europe": QColor(self.continent_colors.get("Europe", "#7B4B94")),
            "North America": QColor(self.continent_colors.get("North America", "#2A7F9E")),
            "Oceania": QColor(self.continent_colors.get("Oceania", "#E27D60")),
            "South America": QColor(self.continent_colors.get("South America", "#4A7856")),
        }

        self.creer_hemicycle()

    def center_x(self):
        return self.width() / 2

    def center_y(self):
        return self.height() * 0.9

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
                + (1 if (self.decalage % self.num_levels) >= (self.num_levels - level) else 0)
            )

            for i in range(num_points):
                angle = (180.0 / (num_points - 1)) * i if num_points > 1 else 90
                angle_rad = math.radians(angle)

                x = self.center_x() + radius * math.cos(angle_rad)
                y = self.center_y() - radius * math.sin(angle_rad)

                coords_angles.append((x, y, angle, level))

        coords_angles = sorted(coords_angles, key=lambda t: (-t[2], -t[3]))
        assert len(coords_angles) == len(
            list(self.constantes.departements_par_pays.keys())
        ), f"{len(coords_angles)} ≠ {len(list(self.constantes.departements_par_pays.keys()))}"
        return coords_angles

    def renvoyer_couleur(self, i: int, lighter_value: int):

        total = 0
        for cont in list(self.resume.keys()):

            # Choix du continent
            if i >= total and i < total + self.resume[cont]["total"]:
                couleur = self.continent_colors[cont]

                # Visité ?
                if i - total > self.resume[cont]["visites"] - 1:
                    couleur = couleur.lighter(lighter_value)

                return couleur, self.continent_colors[cont], cont

            else:
                total = total + self.resume[cont]["total"]

        return QColor(255, 255, 255), QColor(0, 0, 0), "Problème"

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

        coords_angles = self.creer_coordonnées()
        continent_points = {}  # continent: list of (x, y)

        i = 0
        for coord in coords_angles:
            x, y, angle, level = coord
            rayon_texte = max(rayon_texte, abs(y - center_y))
            couleur, couleur_originale, continent = self.renvoyer_couleur(
                i=i, lighter_value=self.lighter_value
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

            # Incrément
            i = i + 1

        # === Légendes : centrées sur le centroïde ===
        painter.setPen(Qt.GlobalColor.black)
        font = QFont()
        font.setPointSize(int(8 + self.level_distance / 10))  # Taille en points
        # font.setPixelSize(20) # Alternative en pixels
        painter.setFont(font)
        font_metrics = painter.fontMetrics()

        rayon_texte = rayon_texte + 10 + self.diametre_point / 1.5
        for continent, points in continent_points.items():
            if not points:
                continue

            # Nom dans la bonne langue
            nom_affiche = self.constantes.pays_differentes_langues.get(continent, {}).get(
                self.langue, continent
            )

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

    def set_pays_visites(self, pays_visites):
        self.pays_visites = pays_visites
        self.creer_hemicycle()

    def set_langue(self, langue):
        self.langue = langue
        self.creer_hemicycle()

    def creer_hemicycle(self):
        self.resume = reordonner_dict(
            nb_pays_visites(
                dict_granu=self.pays_visites,
                continents=self.constantes.liste_regions_monde,
            ),
            clefs=self.ordre_clefs,
        )

        self.update()
