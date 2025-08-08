################################################################################
# Projet de cartes de voyage                                                   #
# 2.2 - Classes utiles à l'application                                         #
################################################################################

import os
import sys
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QGridLayout,
)

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

        # Layout principal vertical
        statistiques = QVBoxLayout(self)

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

        statistiques.addLayout(layout_top_pays)

    def set_entete_regions(self, texte: str):
        self.entete_top_pays_regions.setText(texte)

    def set_entete_departements(self, texte: str):
        self.entete_top_pays_departements.setText(texte)

    def vider_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def lancer_classement_pays(
        self, granularite: int, top_n: int | None, vbox: QGridLayout
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
                label_pays = self.constantes.pays_differentes_langues.get(pays, {}).get(
                    self.langue_utilisee,
                    pays,
                )
                if i < 3:
                    label_pays = f"<b>{label_pays}</b>"

                label_pays = (
                    indice
                    + "<br>"
                    + f"{label_pays}<br>{round(100 * row['pct_superficie_dans_pays'])} %"
                )

                label_widget = QLabel(label_pays)
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
        """Permet de mettre à jour les sélections de granularité."""
        self.dicts_granu = dict_nv
        self.lancer_classement_par_region_departement(top_n=self.top_n)

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
