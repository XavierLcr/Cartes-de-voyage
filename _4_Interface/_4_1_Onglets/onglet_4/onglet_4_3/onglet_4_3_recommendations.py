################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_3                                #
# Onglet 4.3.X – Suggestions de nouvelles destinations                         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QSizePolicy,
    QSpacerItem,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import vider_layout

from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_1_calculs import (
    WorkerRecommandation,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_2_ui import (
    ThemeRecommandation,
    CarteRecommandationSimple,
    CarteRecommandationPays,
    creer_entete_recommandations,
)
from _4_Interface._4_2_Style._4_2_2_styles_complementaires import (
    style_bouton_recommandation,
)

# 2 -- Classe de recommandations (déclenchement des calcul et affichage) -------


class PaysAVisiter(QWidget):

    def __init__(
        self,
        constantes,
        table_superficie,
        fct_traduire,
        parent=None,
    ):
        super().__init__(parent)

        # Données
        self.df_caracteristiques = constantes.df_caracteristiques_pays
        self.table_superficie = table_superficie
        self.n_par_pays = 3
        self.recommandations_par_ligne = 3
        self.alpha = constantes.parametres_application.get(
            "recommandations_alpha", 0.05
        )
        self.alpha = min(max(self.alpha, 0), 1)
        self.beta = constantes.parametres_application.get("recommandations_beta", 1 / 3)
        self.beta = min(max(self.beta, 0), 1)
        self.pays_traductions = constantes.pays_differentes_langues
        self.emojis_pays = constantes.emojis_pays
        self.fonction_traduire = fct_traduire

        # Paramètres utilisateur
        self.langue = "français"
        self.dict_voyages = {}
        self.recommandations_par_pays = True
        self.df = None

        # Thème par défaut (clair) — mis à jour via `set_bouton_recommandation`
        # lorsque le widget parent branche cet onglet sur le système de
        # thème clair/sombre de l'appli.
        self.style = ThemeRecommandation(
            style=1,
            teinte=[i / 360 for i in range(0, 360, 45)],
            nuances={
                "min_luminosite": 0.8,
                "max_luminosite": 0.95,
                "min_saturation": 0.2,
                "max_saturation": 0.4,
            },
        )

        layout = QVBoxLayout()
        # Bouton de lancement
        self.bouton_recommandations = QPushButton()

        layout.addWidget(self.bouton_recommandations)
        self.bouton_recommandations.clicked.connect(self.calculer_prochaine_destination)

        # Scroll area pour les recommandations
        scroll_widget = QWidget()  # widget qui contiendra le layout des recommandations
        self.corps_recommandations = QVBoxLayout()  # layout pour les cartes
        scroll_widget.setLayout(self.corps_recommandations)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(
            True
        )  # permet au scroll de s’adapter à la taille
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Nombre de recommandations
        self.recommandations_nb = QSpinBox()
        recommandations_layout = QHBoxLayout()
        self.recommandations_nb.setMinimum(5)
        self.recommandations_nb.setMaximum(100)
        self.recommandations_nb.setSingleStep(1)
        recommandations_layout.addStretch()
        recommandations_layout.addWidget(self.recommandations_nb)
        layout.addLayout(recommandations_layout)

        self.setLayout(layout)

    def calculer_prochaine_destination(self):

        vider_layout(self.corps_recommandations)

        self.thread_temp = QThread()
        self.worker_temp = WorkerRecommandation(
            df_caracteristiques=self.df_caracteristiques,
            df_superficie=self.table_superficie,
            alpha=self.alpha,
            beta=self.beta,
            top_n=self.get_recommandations_nb(),
            par_pays=self.get_recommandations_par_pays(),
            dict_voyages=self.dict_voyages,
            n_par_pays=self.n_par_pays,
        )
        self.worker_temp.moveToThread(self.thread_temp)
        self.thread_temp.started.connect(self.worker_temp.calculer)
        self.worker_temp.finished.connect(self.on_calcul_fini)
        self.worker_temp.finished.connect(self.thread_temp.quit)
        self.worker_temp.finished.connect(self.worker_temp.deleteLater)
        self.thread_temp.finished.connect(self.thread_temp.deleteLater)
        self.thread_temp.start()

    def on_calcul_fini(self, df):
        """Méthode appelée quand le calcul est terminé."""
        self.df = df
        self.afficher_recommandation()

    def afficher_recommandation(self):

        # Affichage
        self.vider_recommandations()
        if self.df is None:
            return

        self.corps_recommandations.addWidget(
            creer_entete_recommandations(
                texte=self.fonction_traduire("titre_recommandations"),
                theme=self.style,
            )
        )
        self.corps_recommandations.addWidget(QLabel(""))

        if len(self.df) > 0:

            if not self.get_recommandations_par_pays():

                modulo = self.recommandations_par_ligne
                for i, ligne in self.df.iterrows():

                    if i % modulo == 0:
                        layout_temp = QGridLayout()
                        layout_temp.setSpacing(10)
                        for c in range(modulo):
                            layout_temp.setColumnStretch(c, 1)

                    pays_traduit = self.pays_traductions.get(ligne["name_0"], {}).get(
                        self.langue, ligne["name_0"]
                    )

                    layout_temp.addWidget(
                        CarteRecommandationSimple(
                            rang=i + 1,
                            pays_nom=pays_traduit,
                            emoji=self.emojis_pays.get(ligne["name_0"], ""),
                            region=str(ligne["name_1"]),
                            style=self.style,
                        ),
                        0,
                        i % modulo,
                    )

                    if (i + 1) % modulo == 0 or len(self.df) == (i + 1):
                        self.corps_recommandations.addLayout(layout_temp)
                        self.corps_recommandations.addWidget(QLabel(""))

                self.corps_recommandations.addStretch()

            else:

                for pays in list(self.df["name_0"].unique()):

                    pays_traduit = self.pays_traductions.get(pays, {}).get(
                        self.langue, pays
                    )
                    regions = list(self.df.loc[self.df["name_0"] == pays, "name_1"])

                    self.corps_recommandations.addWidget(
                        CarteRecommandationPays(
                            pays_nom=pays_traduit,
                            emoji=self.emojis_pays.get(pays, ""),
                            regions=regions,
                            style=self.style,
                        )
                    )
                    self.corps_recommandations.addSpacerItem(
                        QSpacerItem(
                            0, 5, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
                        )
                    )

                self.corps_recommandations.addStretch()

    def set_dicts_granu(self, dict_nv: dict):
        """Permet de mettre à jour les sélections de destinations."""
        self.dict_voyages = dict_nv
        if self.dict_voyages == {}:
            self.df = None
            self.afficher_recommandation()

    def set_langue(self, langue: str):
        self.langue = langue
        self.bouton_recommandations.setText(
            self.fonction_traduire("bouton_recommandations")
        )
        self.bouton_recommandations.setToolTip(
            self.fonction_traduire("recommandation_passeport")
        )
        self.recommandations_nb.setSuffix(
            self.fonction_traduire("recommandations_nb", prefixe=" ")
        )
        self.afficher_recommandation()

    def set_bouton_recommandation(self, style, teinte, nuances):

        # Thème des cartes de recommandation, aligné sur le style
        # clair/sombre courant de l'appli (mêmes paramètres que le
        # bouton, réutilisés pour cohérence visuelle).
        self.style = ThemeRecommandation(
            style=style, teinte=teinte, nuances=nuances, limite_essais=20
        )

        self.bouton_recommandations.setStyleSheet(
            style_bouton_recommandation(style=style, teinte=teinte, nuances=nuances)
        )

        self.afficher_recommandation()

    def get_recommandations_par_pays(self):
        return self.recommandations_par_pays

    def set_recommandations_par_pays(self, val: bool):
        self.recommandations_par_pays = val

    def vider_recommandations(self):
        vider_layout(self.corps_recommandations)
        self.corps_recommandations.update()

    def get_recommandations_nb(self):
        return self.recommandations_nb.value()

    def set_recommandations_nb(self, val: int):
        self.recommandations_nb.setValue(val)

    def initialiser_onglet(self, **kwargs):
        self.vider_recommandations()

        # Recommandations
        recommandations_nb = kwargs.get("recommandations_nb", 20)
        self.set_recommandations_nb(val=recommandations_nb)
