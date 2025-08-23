################################################################################
# Projet de cartes de voyage                                                   #
# application/classes/onglet_4                                                 #
# Onglet 4 – Partie hémicycle                                                  #
################################################################################


import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
)
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
from application.fonctions_utiles_2_0 import nb_pays_visites, reordonner_dict


# Classe de type hémicycle
class HemicycleWidget(QWidget):
    def __init__(
        self,
        constantes,
        continents,
        langue,
        n_rangees=9,
        points_base=15,
        points_increment=4,
        lighter_value=150,
        continent_colors: dict = {},
    ):

        super().__init__()
        self.pays_visites = {"region": {}, "dep": {}}
        self.continents = continents
        self.constantes = constantes
        self.langue = langue
        self.num_levels = n_rangees  # Nombre de niveaux dans l'hémicycle
        self.base_points = points_base  # Nombre de points de base pour le premier niveau
        self.points_increment = points_increment  # Incrément du nombre de points par niveau
        self.lighter_value = lighter_value
        self.ordre_clefs = [
            "Antarctica",
            "Africa",
            "Europe",
            "Asia",
            "Oceania",
            "North America",
            "South America",
        ]

        # Couleurs pour chaque continent
        self.continent_colors = {
            "Africa": QColor(continent_colors.get("Africa", "#3454D1")),
            "Antarctica": QColor(continent_colors.get("Antarctica", "#2E8B57")),
            "Asia": QColor(continent_colors.get("Asia", "#C3423F")),
            "Europe": QColor(continent_colors.get("Europe", "#7B4B94")),
            "North America": QColor(continent_colors.get("North America", "#2A7F9E")),
            "Oceania": QColor(continent_colors.get("Oceania", "#E27D60")),
            "South America": QColor(continent_colors.get("South America", "#4A7856")),
        }

        self.creer_hemicycle()

    def center_x(self):
        return self.width() / 2

    def center_y(self):
        return self.height() * 0.9

    # def resizeEvent(self, event):
    #     self.update()
    #     super().resizeEvent(event)

    def creer_coordonnées(self):
        coords_angles = []

        for level in range(self.num_levels):
            radius = self.base_radius + level * self.level_distance
            num_points = self.base_points + level * self.points_increment

            for i in range(num_points):
                angle = (180.0 / (num_points - 1)) * i if num_points > 1 else 90
                angle_rad = math.radians(angle)

                x = self.center_x() + radius * math.cos(angle_rad)
                y = self.center_y() - radius * math.sin(angle_rad)

                coords_angles.append((x, y, angle, level))

        coords_angles = sorted(coords_angles, key=lambda t: (-t[2], -t[3]))
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
        self.diametre_point = int(min(self.width(), self.height()) * 0.021 - 2)

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
                QPen(couleur_originale, int(self.diametre_point * 0.15))
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
        font_metrics = painter.fontMetrics()

        rayon_texte = rayon_texte + 10 + self.diametre_point / 2
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
