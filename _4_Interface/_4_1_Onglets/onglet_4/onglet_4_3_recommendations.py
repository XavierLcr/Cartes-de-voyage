################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.3 – Suggestions de nouvelles destinations                           #
################################################################################


import copy, numba
import numpy as np
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QScrollArea,
)

from _0_Utilitaires._0_1_Fonctions_utiles import (
    distance_haversine,
    vider_layout,
    creer_QLabel_centre,
    creer_ligne_separation,
)


# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de calcul des scores entre régions --------------------------


@numba.njit
def calculer_score_region(
    lats_visite,
    lons_visite,
    vals_visite,
    na_visite,
    superficie_visite,
    lats_reste,
    lons_reste,
    vals_reste,
    na_reste,
    alpha,
):
    n_reste = lats_reste.shape[0]
    n_visite = lats_visite.shape[0]
    scores = np.zeros(n_reste)
    for i in range(n_reste):
        s = 0.0
        total_i = 0.0
        for j in range(n_visite):
            geo_dist = distance_haversine(
                lats_reste[i], lons_reste[i], lats_visite[j], lons_visite[j]
            )
            s += (
                (1 / (1 + np.linalg.norm(vals_reste[i] - vals_visite[j])))
                / ((1 + geo_dist) ** alpha)
                * superficie_visite[j]
                * (1 - na_visite[j])
                * (1 - na_reste[i])
            )
            total_i += superficie_visite[j]
        scores[i] = 100 * s / total_i if n_visite > 0 else 0.0
    return scores


## 1.2 -- Fonction renvoyant les régions recommandées, à l'aide des scores -----


def calculer_recommandation(
    df,
    dict_visite,
    top_n=10,
    alpha=1 / 3,
    par_pays=True,
    lignes_extra_par_pays=5,
    max_par_pays=5,
):

    # Séparer les colonnes
    mask_visite = np.array(
        [
            (row[0], row[1])
            in {(p, r) for p, regions in dict_visite.items() for r in regions}
            for row in df[["name_0", "name_1"]].values
        ]
    )
    mask_reste = ~mask_visite

    df_visite = df.iloc[mask_visite]
    df_reste = df.iloc[mask_reste]

    # Extraire arrays NumPy
    cols_val = [
        c
        for c in df.columns
        if c
        not in [
            "name_0",
            "name_1",
            "name_2",
            "latitude",
            "longitude",
            "superficie",
            "population",
            "nombre_na",
        ]
    ]
    lats_visite = df_visite["latitude"].to_numpy()
    lons_visite = df_visite["longitude"].to_numpy()
    vals_visite = df_visite[cols_val].to_numpy()
    na_visite = df_visite["nombre_na"].to_numpy()
    superficie_visite = df_visite["superficie"].to_numpy()

    lats_reste = df_reste["latitude"].to_numpy()
    lons_reste = df_reste["longitude"].to_numpy()
    vals_reste = df_reste[cols_val].to_numpy()
    na_reste = df_reste["nombre_na"].to_numpy()

    # Calcul des scores
    scores = calculer_score_region(
        lats_visite=lats_visite,
        lons_visite=lons_visite,
        vals_visite=vals_visite,
        na_visite=na_visite,
        superficie_visite=superficie_visite,
        lats_reste=lats_reste,
        lons_reste=lons_reste,
        vals_reste=vals_reste,
        na_reste=na_reste,
        alpha=alpha,
    )

    df_reste = df_reste.copy()
    df_reste["score_region"] = scores
    df_reste["score_pays"] = df_reste.groupby("name_0")["score_region"].transform("sum")
    df_reste = df_reste.sort_values("score_region", ascending=False)

    if not par_pays:
        return df_reste.head(top_n)
    else:

        top_pays = []
        for idx, pays in enumerate(df_reste["name_0"]):
            if pays not in top_pays:
                top_pays.append(pays)
                if len(top_pays) == top_n + 1:
                    limite = idx
                    break

        df_reste = df_reste.head(limite + lignes_extra_par_pays)
        df_reste = df_reste[df_reste["name_0"].isin(top_pays[:-1])]

        return (
            df_reste.groupby("name_0", group_keys=False)
            .apply(lambda g: g.nlargest(max_par_pays, "score_region"))
            .reset_index(drop=True)
            .sort_values(["score_pays", "score_region"], ascending=[False, False])
        )


# 2 -- Classe de calcul du tableau de recommandations --------------------------


class WorkerRecommandation(QObject):
    finished = pyqtSignal(object)  # Signal pour retourner le résultat

    def __init__(self, constantes, dict_visite):
        super().__init__()
        self.constantes = constantes
        self.dict_visite = dict_visite

    def calculer(self):
        """Méthode exécutée dans le thread."""
        df = (
            calculer_recommandation(
                df=self.constantes.df_caracteristiques_pays,
                dict_visite=self.dict_visite,
                top_n=self.constantes.parametres_application.get(
                    "n_recommandations", 10
                ),
                par_pays=self.constantes.parametres_application.get("par_pays", True),
                lignes_extra_par_pays=self.constantes.parametres_application.get(
                    "lignes_supp_apres_dernier_pays", 5
                ),
                alpha=self.constantes.parametres_application.get(
                    "coeff_distance", 0.05
                ),
                max_par_pays=self.constantes.parametres_application.get(
                    "max_regions_par_pays", 5
                ),
            ).reset_index()
            if self.dict_visite != {}
            else None
        )
        self.finished.emit(df)  # Émet le résultat


# 3 -- Classe de recommandations (déclenchement des calcul et affichage) -------


class PaysAVisiter(QWidget):

    def __init__(
        self,
        constantes,
        table_superficie,
        fct_traduire,
        parent=None,
    ):
        super().__init__(parent)

        self.langue = "français"
        self.constantes = constantes
        self.fonction_traduire = fct_traduire
        self.dict_granu = {"region": {}, "dep": {}}
        self.df = None
        self.table_superficie = table_superficie

        layout = QVBoxLayout()
        # Bouton de lancement
        self.bouton_recommandations = QPushButton()
        self.bouton_recommandations.setStyleSheet(
            f"""
        QPushButton {{
            background-color: {"#C8E6C9"};  /* pastel bleu-vert */
            color: #2C2C2C;              /* texte bleu foncé pour contraste doux */
            border-radius: 12px;
            padding: 10px 22px;
            font-size: 14px;
            font-weight: bold;
            border:  none;   /* bord subtil légèrement plus clair */
        }}
        QPushButton:hover {{
            background-color: #B7E4C7;   /* légèrement plus saturé au survol */
            border-color: none;
        }}
        QPushButton:pressed {{
            background-color: #77B0AD;   /* un peu plus foncé à l’appui */
            border-color: none;
        }}
    """
        )

        layout.addWidget(self.bouton_recommandations)
        self.bouton_recommandations.clicked.connect(self.calculer_prochaine_destination)

        # Scroll area pour les recommandations
        scroll_widget = QWidget()  # widget qui contiendra le layout des recommandations
        self.corps_recommandations = QVBoxLayout()  # layout pour les QLabel
        scroll_widget.setLayout(self.corps_recommandations)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(
            True
        )  # permet au scroll de s’adapter à la taille
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def calculer_prochaine_destination(self):

        vider_layout(self.corps_recommandations)

        # Ajout des régions des départements
        dt_temp = self.table_superficie[
            self.table_superficie.apply(
                lambda row: (row["name_0"], row["name_2"])
                in {
                    (p, r)
                    for p, dep in (self.dict_granu.get("dep") or {}).items()
                    for r in dep
                },
                axis=1,
            )
        ]
        dict_temp = copy.deepcopy(self.dict_granu.get("region"))
        for pays, groupe in dt_temp.groupby("name_0"):
            regions = groupe["name_1"].tolist()
            if pays in dict_temp:
                # Ajouter les nouvelles régions sans doublons
                dict_temp[pays] = list(set(dict_temp[pays]) | set(regions))
            else:
                # Ajouter le pays s'il n'existait pas encore
                dict_temp[pays] = regions

        dict_temp = {
            k: list(dict.fromkeys(v)) for k, v in dict_temp.items() if v is not None
        }

        self.thread_temp = QThread()
        self.worker_temp = WorkerRecommandation(
            constantes=self.constantes,
            dict_visite=dict_temp,
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
        vider_layout(self.corps_recommandations)
        if self.df is None:
            return
        self.corps_recommandations.addWidget(
            creer_QLabel_centre(
                text=self.fonction_traduire(
                    "titre_recommandations", prefixe="<b>", suffixe="</b> :"
                )
            )
        )
        self.corps_recommandations.addLayout(
            creer_ligne_separation(lStretch=2, rStretch=2)
        )
        self.corps_recommandations.addWidget(QLabel(""))

        if self.df is not None:
            if len(self.df) > 0:

                if not self.constantes.parametres_application.get("par_pays", True):

                    modulo = 4
                    for i, ligne in self.df.iterrows():

                        if i % modulo == 0:
                            layout_temp = QGridLayout()

                        layout_temp.addWidget(
                            QLabel(
                                # Numéro
                                f"{i + 1}. "
                                # Pays avec emoji
                                f"<b>{ligne['name_0']}</b> {self.constantes.emojis_pays.get(ligne['name_0'], '')}: "
                                # Régions si affichage regroupé
                                f"{ligne['name_1']}",
                                wordWrap=True,
                            ),
                            0,
                            i % modulo,
                        )

                        if (i + 1) % modulo == 0:
                            self.corps_recommandations.addLayout(layout_temp)
                            self.corps_recommandations.addWidget(QLabel())

                    self.corps_recommandations.addStretch()

                else:

                    for pays in list(self.df["name_0"].unique()):

                        self.corps_recommandations.addWidget(
                            creer_QLabel_centre(
                                text=(
                                    # Pays avec emoji
                                    f"{self.constantes.emojis_pays.get(pays, '')} "
                                    f"<b>{pays}</b>"
                                    f" {self.constantes.emojis_pays.get(pays, '')}"
                                )
                            )
                        )

                        layout_temp = QHBoxLayout()
                        layout_temp.setSpacing(5)
                        layout_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)

                        region_temp = list(
                            self.df.loc[self.df["name_0"] == pays, "name_1"]
                        )
                        for i, region in enumerate(region_temp):
                            layout_temp.addWidget(creer_QLabel_centre(text=region))
                            if (
                                i < len(region_temp) - 1
                            ):  # pas de séparateur après le dernier
                                layout_temp.addWidget(QLabel("–"))

                        conteneur = QWidget()
                        conteneur.setLayout(layout_temp)
                        self.corps_recommandations.addWidget(conteneur)
                        self.corps_recommandations.addWidget(QLabel(""))

    def set_dicts_granu(self, dict_nv: dict):
        """Permet de mettre à jour les sélections de destinations."""
        self.dict_granu = dict_nv
        if self.dict_granu == {"region": {}, "dep": {}}:
            self.calculer_prochaine_destination()

    def set_langue(self, langue: str):
        self.langue = langue
        self.bouton_recommandations.setText(
            self.fonction_traduire("bouton_recommandations")
        )
        self.bouton_recommandations.setToolTip(
            self.fonction_traduire("recommandation_passeport")
        )
        self.afficher_recommandation()
