################################################################################
# Projet de cartes de voyage                                                   #
# 2.2 - Classes utiles à l'application                                         #
################################################################################

import os
import sys
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPointF
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QGridLayout,
    QCheckBox,
    QTabWidget,
)
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from application import fonctions_utiles_2_0
from production_cartes import creer_carte_1_1, carte_main_1_3


# Classe de suivi du pays en cours de cartographie
class TrackerPays(QObject):
    tracker_pays_en_cours = pyqtSignal(str)

    def notify(self, libelle_pays: str):
        self.tracker_pays_en_cours.emit(libelle_pays)


# Classe de création des cartes
class CreerCartes(QObject):
    finished = pyqtSignal()
    tracker_signal = pyqtSignal(str)
    avancer = pyqtSignal(int)

    def __init__(self, params):
        super().__init__()
        self.parametres = params

    def run(self):
        tracker = TrackerPays()
        tracker.tracker_pays_en_cours.connect(self.tracker_signal.emit)

        carte_main_1_3.cree_graphe_depuis_debut(
            **self.parametres, tracker=tracker, blabla=False, afficher_nom_lieu=False
        )

        self.finished.emit()


# Troisième onglet
class OngletResumeDestinations(QWidget):
    def __init__(
        self,
        traduire_depuis_id,
        constantes,
        langue_utilisee,
        dicts_granu,
        parent=None,
    ):
        super().__init__(parent)

        self.traduire_depuis_id = traduire_depuis_id
        self.constantes = constantes
        self.dicts_granu = dicts_granu
        self.langue_utilisee = langue_utilisee

        self.layout_onglet_3 = QVBoxLayout()
        self.layout_resume_pays = QHBoxLayout()

        # Layout régions
        self.layout_resume_regions = QVBoxLayout()
        self.scroll_regions = self._creer_scroll(self.layout_resume_regions)

        # Layout départements
        self.layout_resume_departements = QVBoxLayout()
        self.scroll_departements = self._creer_scroll(self.layout_resume_departements)

        # Bouton de mise en forme
        self.mise_en_forme = QCheckBox()
        self.mise_en_forme.stateChanged.connect(self.maj_layout_resume)

        # Assembler les widgets
        self.layout_resume_pays.addWidget(self.scroll_regions)
        self.layout_resume_pays.addWidget(self.scroll_departements)

        self.layout_onglet_3.addLayout(self.layout_resume_pays)
        self.layout_onglet_3.addWidget(self.mise_en_forme)

        self.setLayout(self.layout_onglet_3)

    def set_dicts_granu(self, dict_nv: dict):
        """Permet de mettre à jour les sélections de destinations."""
        self.dicts_granu = dict_nv
        self.maj_layout_resume()

    def set_langue(self, nouvelle_langue):
        """Permet de mettre à jour la langue."""
        self.langue_utilisee = nouvelle_langue
        self.mise_en_forme.setText(
            self.traduire_depuis_id(clef="mise_en_forme_onglet_3")
        )
        self.maj_layout_resume()

    def _creer_scroll(self, vbox):
        widget = QWidget()
        widget.setLayout(vbox)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        return scroll

    def ajouter_partie_a_layout(
        self, granu, pays_donnees, vbox, affichage_groupe=True, inclure_emojis=True
    ):
        label_titre = QLabel(
            self.traduire_depuis_id(clef=granu, prefixe="<b>", suffixe="</b>")
        )
        label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(label_titre)

        vbox.addLayout(fonctions_utiles_2_0.creer_ligne_separation())
        vbox.addWidget(QLabel(""))

        for pays, items in pays_donnees.items():
            emoji_i = (
                f"{self.constantes.emojis_pays.get(pays, '')} "
                if inclure_emojis
                else ""
            )

            if affichage_groupe:
                texte_items = ", ".join(items) if items else "Aucun élément"
                texte = f"<b>{pays}</b> {emoji_i}: {texte_items}"
                label = QLabel(texte)
                label.setWordWrap(True)
                vbox.addWidget(label)
            else:
                vbox.addWidget(QLabel(f"<b>{pays}</b> {emoji_i}:"))
                if items:
                    for item in items:
                        label = QLabel(f"   • {item}")
                        label.setWordWrap(True)
                        vbox.addWidget(label)

            label_sep = QLabel("– " * 3)
            label_sep.setAlignment(
                Qt.AlignmentFlag.AlignCenter
                if affichage_groupe
                else Qt.AlignmentFlag.AlignLeft
            )
            vbox.addWidget(label_sep)

        vbox.addStretch()

    def vider_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def maj_layout_resume(self):
        self.vider_layout(self.layout_resume_regions)
        self.vider_layout(self.layout_resume_departements)

        self.ajouter_partie_a_layout(
            "titre_regions_visitees",
            self.dicts_granu.get("region", {}),
            self.layout_resume_regions,
            affichage_groupe=self.mise_en_forme.isChecked(),
        )
        self.ajouter_partie_a_layout(
            "titre_departements_visites",
            self.dicts_granu.get("dep", {}),
            self.layout_resume_departements,
            affichage_groupe=self.mise_en_forme.isChecked(),
        )


# Classe de type hémicycle
class HemicycleWidget(QWidget):
    def __init__(
        self,
        constantes,
        continents,
        min_width=500,
        min_height=300,
        n_rangees=9,
        points_base=15,
        points_increment=4,
    ):

        super().__init__()
        self.setMinimumSize(min_width, min_height)
        self.pays_visites = {"region": {}, "dep": {}}
        self.continents = continents
        self.constantes = constantes
        self.num_levels = n_rangees  # Nombre de niveaux dans l'hémicycle
        self.base_radius = 90  # Rayon de base pour le premier niveau
        self.level_distance = 30  # Distance entre les niveaux
        self.base_points = (
            points_base  # Nombre de points de base pour le premier niveau
        )
        self.points_increment = (
            points_increment  # Incrément du nombre de points par niveau
        )

        # Couleurs pour chaque continent
        self.continent_colors = {
            "Africa": QColor("#3454D1"),  # Bleu roi
            "Antarctica": QColor("#2E8B57"),  # Vert océan
            "Asia": QColor("#C3423F"),  # Rouge cerise
            "Europe": QColor("#7B4B94"),  # Violet prune
            "North America": QColor("#2A7F9E"),  # Bleu sarcelle
            "Oceania": QColor("#E27D60"),  # Orange chaud
            "South America": QColor("#4A7856"),  # Vert forêt clair
        }

        self.creer_hemicycle()

    def creer_coordonnées(self):
        coords_angles = []

        center_x = self.width() / 2
        center_y = self.height() * 0.9  # comme dans ton paintEvent

        for level in range(self.num_levels):
            radius = self.base_radius + level * self.level_distance
            num_points = self.base_points + level * self.points_increment

            for i in range(num_points):
                angle = (180.0 / (num_points - 1)) * i if num_points > 1 else 90
                angle_rad = math.radians(angle)

                x = center_x + radius * math.cos(angle_rad)
                y = center_y - radius * math.sin(angle_rad)

                coords_angles.append((x, y, angle, level))

        coords_angles = sorted(coords_angles, key=lambda t: (-t[2], t[3]))
        return coords_angles

    def renvoyer_couleur(self, i: int, lighter_value: int):

        total = 0
        for cont in list(self.resume.keys()):

            # Choix du continent
            if i >= 0 and i < total + self.resume[cont]["total"]:
                couleur = self.continent_colors[cont]

                # Visité ?
                if (
                    total + self.resume[cont]["total"] - i
                    > self.resume[cont]["visites"]
                ):
                    couleur = couleur.lighter(lighter_value)

                return couleur

            else:
                total = total + self.resume[cont]["total"]

        return QColor(0, 0, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Récupération des coordonnées
        liste_coordonnees = self.creer_coordonnées()

        i = 0
        for coord in liste_coordonnees:

            painter.setBrush(QBrush(self.renvoyer_couleur(i=i, lighter_value=150)))
            painter.drawEllipse(QPointF(coord[0], coord[1]), 5, 5)

            i = i + 1

        margin = 20
        spacing = 100
        rect_size = 12
        y_legend = self.height() - margin

        for idx, (continent, color) in enumerate(self.continent_colors.items()):
            x_legend = margin + idx * spacing

            # Dessin du carré de couleur
            painter.setBrush(QBrush(color))
            painter.drawRect(x_legend, y_legend - rect_size, rect_size, rect_size)

            # Dessin du texte
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(x_legend + rect_size + 5, y_legend, continent)

    def set_pays_visites(self, pays_visites):
        self.pays_visites = pays_visites
        self.creer_hemicycle()

    def creer_hemicycle(self):
        self.resume = fonctions_utiles_2_0.nb_pays_visites(
            dict_granu=self.pays_visites,
            continents=self.constantes.liste_regions_monde,
        )
        self.update()


# Quatrième onglet
class OngletTopPays(QWidget):
    def __init__(
        self,
        dicts_granu: dict,
        constantes,
        liste_gdfs: list,
        langue_utilisee: str,
        top_n: int | None,
        parent=None,
    ):
        super().__init__(parent)

        # Variables passées en paramètre
        self.constantes = constantes
        self.liste_gdfs = liste_gdfs
        self.langue_utilisee = langue_utilisee
        self.dicts_granu = dicts_granu
        self.top_n = top_n

        # Création de l'hémicycle
        self.hemicycle = HemicycleWidget(
            continents=self.constantes.liste_regions_monde, constantes=self.constantes
        )

        # Classement
        layout_top_pays = QHBoxLayout()

        # --- Bloc "Top pays par région" ---
        self.entete_top_pays_regions = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        layout_entete_top_pays_regions = QVBoxLayout()
        layout_entete_top_pays_regions.addWidget(self.entete_top_pays_regions)

        layout_entete_top_pays_regions.addLayout(
            fonctions_utiles_2_0.creer_ligne_separation()
        )
        layout_entete_top_pays_regions.addWidget(QLabel(""))

        self.layout_top_pays_regions = QGridLayout()
        layout_entete_top_pays_regions.addLayout(self.layout_top_pays_regions)
        layout_entete_top_pays_regions.addStretch()

        widget_top_pays_regions = QWidget()
        widget_top_pays_regions.setLayout(layout_entete_top_pays_regions)

        scroll_top_pays_regions = QScrollArea()
        scroll_top_pays_regions.setWidgetResizable(True)
        scroll_top_pays_regions.setWidget(widget_top_pays_regions)

        # --- Bloc "Top pays par département" ---
        self.entete_top_pays_departements = QLabel(
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout_entete_top_pays_departements = QVBoxLayout()
        layout_entete_top_pays_departements.addWidget(self.entete_top_pays_departements)

        layout_entete_top_pays_departements.addLayout(
            fonctions_utiles_2_0.creer_ligne_separation()
        )
        layout_entete_top_pays_departements.addWidget(QLabel(""))

        self.layout_top_pays_deps = QGridLayout()
        layout_entete_top_pays_departements.addLayout(self.layout_top_pays_deps)
        layout_entete_top_pays_departements.addStretch()

        widget_top_pays_deps = QWidget()
        widget_top_pays_deps.setLayout(layout_entete_top_pays_departements)

        scroll_top_pays_deps = QScrollArea()
        scroll_top_pays_deps.setWidgetResizable(True)
        scroll_top_pays_deps.setWidget(widget_top_pays_deps)

        # --- Ajout des deux scrolls au layout principal ---
        layout_top_pays.addWidget(scroll_top_pays_regions)
        layout_top_pays.addWidget(scroll_top_pays_deps)

        # Layout principal vertical
        statistiques = QVBoxLayout(self)

        # Création d'un QTabWidget pour les sous-onglets
        self.sous_onglets = QTabWidget()

        # ---------- Onglet 1 : Hémicycle ----------
        self.page_hemicycle = QWidget()
        layout_hemicycle = QVBoxLayout(self.page_hemicycle)
        layout_hemicycle.addWidget(self.hemicycle)
        self.sous_onglets.addTab(self.page_hemicycle, "Hémicycle")

        # ---------- Onglet 2 : Top pays ----------
        self.page_top_pays = QWidget()
        layout_top_pays_page = QVBoxLayout(self.page_top_pays)
        layout_top_pays_page.addLayout(layout_top_pays)  # ton layout existant
        self.sous_onglets.addTab(self.page_top_pays, "Top Pays")

        # Ajouter le QTabWidget au layout principal
        statistiques.addWidget(self.sous_onglets)

    def set_entetes(
        self,
        texte_region: str,
        texte_departement: str,
        texte_onglet_1: str,
        texte_onglet_2: str,
    ):
        self.entete_top_pays_regions.setText(texte_region)
        self.entete_top_pays_departements.setText(texte_departement)
        self.sous_onglets.setTabText(
            self.sous_onglets.indexOf(self.page_hemicycle), texte_onglet_1
        )
        self.sous_onglets.setTabText(
            self.sous_onglets.indexOf(self.page_top_pays), texte_onglet_2
        )

    def vider_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def lancer_classement_pays(
        self, granularite: int, top_n: int | None, vbox: QGridLayout, ndigits=0
    ):
        dict_regions = self.dicts_granu["region"] or None
        dict_departements = self.dicts_granu["dep"] or None

        if dict_departements and dict_regions:
            dict_regions = {
                k: v for k, v in dict_regions.items() if k not in dict_departements
            }

        self.vider_layout(vbox)

        try:
            gdf = creer_carte_1_1.cree_base_toutes_granularites(
                liste_dfs=self.liste_gdfs,
                liste_dicts=[dict_regions, dict_departements],
                granularite_objectif=granularite,
            )

            classement = fonctions_utiles_2_0.creer_classement_pays(
                gdf,
                self.constantes.table_superficie,
                granularite=granularite,
                top_n=top_n,
            )

            for i, (_, row) in enumerate(classement.iterrows()):
                pays = row["Pays"]

                indice = ["🥇", "🥈", "🥉"][i] if i < 3 else f"<b>{i + 1}.</b>"
                label_widget = self.constantes.pays_differentes_langues.get(
                    pays, {}
                ).get(
                    self.langue_utilisee,
                    pays,
                )
                if i < 3:
                    label_widget = f"<b>{label_widget}</b>"

                label_widget = (
                    indice
                    + "<br>"
                    + f"{label_widget}<br>{round(100 * row['pct_superficie_dans_pays'], ndigits=ndigits)} %"
                ).replace(".", ",")

                label_widget = QLabel(label_widget)
                label_widget.setAlignment(
                    Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
                )

                if i == 0:
                    couronne_g = QLabel("👑")
                    couronne_g.setAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                    vbox.addWidget(couronne_g, i, 0)
                    vbox.addWidget(label_widget, i, 1)
                    couronne_d = QLabel("👑")
                    couronne_d.setAlignment(
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                    )
                    vbox.addWidget(couronne_d, i, 2)
                elif i in [1, 2]:
                    vbox.addWidget(label_widget, 1, 2 * i - 2)
                else:
                    vbox.addWidget(label_widget, (i + 3) // 3, i % 3)

        except:
            pass

    def lancer_classement_par_region_departement(self, top_n: int | None = 10):
        self.lancer_classement_pays(
            granularite=1, top_n=top_n, vbox=self.layout_top_pays_regions
        )
        self.lancer_classement_pays(
            granularite=2, top_n=top_n, vbox=self.layout_top_pays_deps
        )

    def set_dicts_granu(self, dict_nv: dict):
        """Permet de mettre à jour les sélections de destinations."""
        self.dicts_granu = dict_nv
        self.lancer_classement_par_region_departement(top_n=self.top_n)
        self.hemicycle.set_pays_visites(pays_visites=dict_nv)

    def set_langue(self, nouvelle_langue):
        """Permet de mettre à jour la langue."""
        self.langue_utilisee = nouvelle_langue
        self.lancer_classement_par_region_departement(top_n=self.top_n)


# Cinquième onglet
class OngletInformations(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.label = QLabel()
        self.label.setWordWrap(True)
        self.scroll_area.setWidget(self.label)

        layout.addWidget(self.scroll_area)

    def set_description(self, texte_html: str):
        """Permet de mettre à jour le texte affiché."""
        self.label.setText(texte_html)
