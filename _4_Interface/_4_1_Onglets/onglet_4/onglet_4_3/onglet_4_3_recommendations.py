################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_3                                #
# Onglet 4.3.X – Suggestions de nouvelles destinations                         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import (
    QWidget,
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
from _0_Utilitaires._0_06_fonctions_utiles_traductions import traduire_pays

from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_1_calculs import (
    WorkerRecommandation,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_2_reco_par_pays import (
    CarteRecommandationPays,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_4_reco_simple import (
    CarteRecommandationSimple,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_3_titre import (
    TitreRecommandations,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_5_bouton import (
    BoutonRecommandation,
)

# 2 -- Classe de recommandations (déclenchement des calcul et affichage) -------


class PaysAVisiter(QWidget):

    def __init__(
        self,
        constantes,
        table_superficie,
        fct_traduire,
        parent=None,
        par_pays: bool = True,
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
        self.recommandations_par_pays = par_pays
        self.df = None

        layout = QVBoxLayout()
        # Bouton de lancement
        self.bouton_recommandations = BoutonRecommandation(
            fonction_traduction=fct_traduire
        )
        self.bouton_recommandations.clicked.connect(self.calculer_prochaine_destination)
        layout.addWidget(self.bouton_recommandations)

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
            TitreRecommandations(texte=self.fonction_traduire("titre_recommandations"))
        )
        self.corps_recommandations.addSpacing(8)

        if len(self.df) > 0:

            if not self.get_recommandations_par_pays():

                modulo = self.recommandations_par_ligne
                for i, ligne in self.df.iterrows():

                    if i % modulo == 0:
                        layout_temp = QGridLayout()
                        layout_temp.setSpacing(10)
                        for c in range(modulo):
                            layout_temp.setColumnStretch(c, 1)

                    pays_traduit = traduire_pays(
                        pays=ligne["name_0"],
                        langue=self.langue,
                        referentiel=self.pays_traductions,
                    )

                    layout_temp.addWidget(
                        CarteRecommandationSimple(
                            rang=i + 1,
                            pays_nom=pays_traduit,
                            emoji=self.emojis_pays.get(ligne["name_0"], ""),
                            region=str(ligne["name_1"]),
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

                    pays_traduit = traduire_pays(
                        pays=pays, langue=self.langue, referentiel=self.pays_traductions
                    )
                    regions = list(self.df.loc[self.df["name_0"] == pays, "name_1"])

                    self.corps_recommandations.addWidget(
                        CarteRecommandationPays(
                            pays_nom=pays_traduit,
                            emoji=self.emojis_pays.get(pays, ""),
                            regions=regions,
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

        # Bouton de recommandations
        self.bouton_recommandations.set_langue()

        self.recommandations_nb.setSuffix(
            self.fonction_traduire("recommandations_nb", prefixe=" ")
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
