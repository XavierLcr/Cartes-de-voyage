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
    QScrollArea,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import vider_layout
from _0_Utilitaires._0_06_fonctions_utiles_traductions import traduire_pays

from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_1_calculs import (
    WorkerRecommandation,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_2_reco_par_pays import (
    CarteRecommandationPays,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_3_titre import (
    TitreRecommandations,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_4_reco_simple import (
    CarteRecommandationSimple,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_5_bouton import (
    BoutonRecommandation,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_3.onglet_4_3_6_spinbox import (
    SpinBoxGare,
)

# 1 -- Classe de recommandations ----------------------------------------------


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

        # Données générales
        self.df_caracteristiques = constantes.df_caracteristiques_pays
        self.table_superficie = table_superficie
        self.pays_traductions = constantes.pays_differentes_langues
        self.emojis_pays = constantes.emojis_pays
        self.fonction_traduire = fct_traduire

        # Paramètres des recommandations
        parametres = constantes.parametres_application

        self.alpha = min(max(parametres.get("recommandations_alpha", 0.05), 0), 1)
        self.beta = min(max(parametres.get("recommandations_beta", 1 / 3), 0), 1)

        self.n_par_pays = 3
        self.recommandations_par_ligne = 3
        self.recommandations_par_pays = par_pays

        # État courant
        self.langue = "français"
        self.dict_voyages = {}
        self.df = None

        # Thread de calcul
        self.thread_temp = None
        self.worker_temp = None

        self._creer_interface()

    # 2 -- Création de l'interface ---------------------------------------------

    def _creer_interface(self):

        layout_principal = QVBoxLayout(self)

        # Bouton de lancement
        self.bouton_recommandations = BoutonRecommandation(
            fonction_traduction=self.fonction_traduire
        )
        self.bouton_recommandations.clicked.connect(self.calculer_prochaine_destination)
        layout_principal.addWidget(self.bouton_recommandations)

        # Zone des recommandations
        self.corps_recommandations = QVBoxLayout()

        widget_scroll = QWidget()
        widget_scroll.setLayout(self.corps_recommandations)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(widget_scroll)

        layout_principal.addWidget(scroll_area)

        # Nombre de recommandations
        self.recommandations_nb = SpinBoxGare(minimum=5, maximum=100, pas=1)
        self.recommandations_nb.setSingleStep(1)

        layout_nb = QHBoxLayout()
        layout_nb.addStretch()
        layout_nb.addWidget(self.recommandations_nb)

        layout_principal.addLayout(layout_nb)

    # 3 -- Calcul des recommandations -----------------------------------------

    def calculer_prochaine_destination(self):

        self.vider_recommandations()
        self.bouton_recommandations.setEnabled(False)

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
        """Méthode appelée lorsque le calcul des recommandations est terminé."""

        self.df = df
        self.afficher_recommandation()
        self.bouton_recommandations.setEnabled(True)

    # 4 -- Affichage -----------------------------------------------------------

    def afficher_recommandation(self):

        self.vider_recommandations()

        if self.df is None:
            return

        self.corps_recommandations.addWidget(
            TitreRecommandations(texte=self.fonction_traduire("titre_recommandations"))
        )
        self.corps_recommandations.addSpacing(8)

        if self.df.empty:
            return

        if self.get_recommandations_par_pays():
            self._afficher_recommandations_par_pays()
        else:
            self._afficher_recommandations_simples()

        self.corps_recommandations.addSpacing(10)
        self.corps_recommandations.addStretch()

    def _afficher_recommandations_par_pays(self):

        for pays, df_pays in self.df.groupby("name_0", sort=False):

            pays_traduit = traduire_pays(
                pays=pays,
                langue=self.langue,
                referentiel=self.pays_traductions,
            )

            carte = CarteRecommandationPays(
                pays_nom=pays_traduit,
                emoji=self.emojis_pays.get(pays, ""),
                regions=df_pays["name_1"].tolist(),
            )

            self.corps_recommandations.addWidget(carte)

    def _afficher_recommandations_simples(self):

        n_colonnes = self.recommandations_par_ligne
        n_recommandations = len(self.df)

        for i, ligne in enumerate(self.df.itertuples(index=False)):

            colonne = i % n_colonnes

            if colonne == 0:
                layout_ligne = QGridLayout()
                layout_ligne.setSpacing(10)

                for c in range(n_colonnes):
                    layout_ligne.setColumnStretch(c, 1)

            pays = ligne.name_0

            pays_traduit = traduire_pays(
                pays=pays,
                langue=self.langue,
                referentiel=self.pays_traductions,
            )

            carte = CarteRecommandationSimple(
                rang=i + 1,
                pays_nom=pays_traduit,
                emoji=self.emojis_pays.get(pays, ""),
                region=str(ligne.name_1),
            )

            layout_ligne.addWidget(carte, 0, colonne)

            derniere_colonne = colonne == n_colonnes - 1
            derniere_recommandation = i == n_recommandations - 1

            if derniere_colonne or derniere_recommandation:
                self.corps_recommandations.addLayout(layout_ligne)
                self.corps_recommandations.addSpacing(10)

    # 5 -- Paramètres ----------------------------------------------------------

    def set_dicts_granu(self, dict_nv: dict):
        """Met à jour les destinations déjà sélectionnées."""

        self.dict_voyages = dict_nv

        if not self.dict_voyages:
            self.df = None
            self.afficher_recommandation()

    def set_langue(self, langue: str):

        self.langue = langue

        self.bouton_recommandations.set_langue()

        self.recommandations_nb.setSuffix(
            self.fonction_traduire(
                "recommandations_nb",
                prefixe=" ",
            )
        )

        self.afficher_recommandation()

    def get_recommandations_par_pays(self):
        return self.recommandations_par_pays

    def set_recommandations_par_pays(self, val: bool):
        self.recommandations_par_pays = val

    def get_recommandations_nb(self):
        return self.recommandations_nb.value()

    def set_recommandations_nb(self, val: int):
        self.recommandations_nb.setValue(val)

    # 6 -- Utilitaires ---------------------------------------------------------

    def vider_recommandations(self):
        vider_layout(self.corps_recommandations)

    def initialiser_onglet(self, **kwargs):

        self.vider_recommandations()

        self.set_recommandations_nb(kwargs.get("recommandations_nb", 20))
