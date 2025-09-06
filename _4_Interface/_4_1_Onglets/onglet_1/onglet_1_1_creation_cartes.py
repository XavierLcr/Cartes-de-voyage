################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1.1 – Création des cartes                                             #
################################################################################


from PyQt6.QtCore import pyqtSignal, QObject
from _3_Calculs._1_3_carte_main import cree_graphe_depuis_debut


# Classe de suivi du pays en cours de cartographie
class TrackerPays(QObject):
    tracker_pays_en_cours = pyqtSignal(str)

    def notify(self, libelle_pays: str):
        self.tracker_pays_en_cours.emit(libelle_pays)


# Classe de création des cartes
class CreerCartes(QObject):
    finished = pyqtSignal()
    tracker_signal = pyqtSignal(str)
    nb_graphes = pyqtSignal(int)

    def __init__(self, gdf_eau, params, constantes):

        super().__init__()

        self.gdf_eau = gdf_eau
        self.parametres = params
        self.constantes = constantes

    def run(self):

        # === Ajustement des variables ===
        self.granularite = {"Pays": 0, "Région": 1, "Département": 2}.get(
            self.parametres.get("granularite"), -1
        )

        self.liste_regions_temp = {
            region: self.constantes.liste_regions_monde[region]
            for cle_param, regions in {
                "moyen_orient": ["Middle East"],
                "europe": ["Europe"],
                "amerique": ["South America", "North America"],
                "afrique": ["Africa"],
                "asie": ["Asia"],
            }.items()
            if self.parametres.get(cle_param, False)
            for region in regions
        }

        if self.parametres.get("autres_regions", False):
            self.liste_regions_temp.update(
                {
                    k: v
                    for k, v in self.constantes.liste_regions_monde.items()
                    if k not in set(self.liste_regions_temp.keys())
                }
            )

        dict_regions = self.parametres["dictionnaire_regions"]
        if self.parametres["dictionnaire_departements"] is not None:
            if self.parametres["dictionnaire_departements"] != {} and dict_regions is not None:
                dict_regions = {
                    k: v
                    for k, v in self.parametres["dictionnaire_regions"].items()
                    if k not in self.parametres["dictionnaire_departements"]
                }

        if self.parametres["dictionnaire_departements"] == {}:
            self.parametres["dictionnaire_departements"] = None
        if dict_regions == {}:
            dict_regions = None

        self.nb_graphes.emit(
            self.calculer_nb_total_graphes(
                dict_regions=dict_regions,
                dict_departement=self.parametres["dictionnaire_departements"],
            )
        )

        # --- Partie calcul cartes ---
        tracker = TrackerPays()
        tracker.tracker_pays_en_cours.connect(self.tracker_signal.emit)

        cree_graphe_depuis_debut(
            liste_dfs=self.parametres["liste_dfs"],
            liste_dicts=[dict_regions, self.parametres["dictionnaire_departements"]],
            gdf_eau=self.gdf_eau,
            noms_pays=self.constantes.pays_differentes_langues,
            dictionnaire_pays_unis=self.constantes.liste_pays_groupes,
            nom_indiv=self.parametres["nom"],
            direction_resultat=self.parametres["dossier_stockage"],
            langue=self.parametres["langue"],
            granularite_visite=self.granularite,
            granularite_reste={"Pays": 0, "Région": 1}.get(
                self.parametres.get("granularite_fond"), 2
            ),
            theme=self.constantes.liste_ambiances[self.parametres["theme"]],
            teinte=self.constantes.liste_couleurs[self.parametres["couleur"]],
            couleur_fond="none",
            # couleur_fond="#CDEAF7" if self.parametres["couleur_fond_carte"] else "#FFFFFF",
            couleur_non_visites="#ECEBED",
            couleur_lacs="#CEE3F5",
            format=self.parametres["format"],
            qualite=self.parametres["qualite"],
            carte_du_monde=self.parametres["carte_du_monde"],
            liste_regions=self.liste_regions_temp,
            pays_individuel=self.parametres["cartes_des_pays"],
            max_cartes_additionnelles=self.parametres["max_cartes_additionnelles"],
            sortir_cartes_granu_inf=self.parametres["sortir_cartes_granu_inf"],
            tracker=tracker,
            blabla=False,
            afficher_nom_lieu=False,
        )

        self.finished.emit()

    def calculer_nb_total_graphes(self, dict_regions, dict_departement):

        return (
            (
                (len(list(dict_regions.keys())) if dict_regions is not None else 0)
                * int((self.parametres["sortir_cartes_granu_inf"] or self.granularite < 2))
                + (len(list(dict_departement.keys())) if dict_departement is not None else 0)
            )
            * self.parametres["cartes_des_pays"]
            * int(self.granularite != 0)
            + len(self.liste_regions_temp)
            + int(self.parametres["carte_du_monde"])
        )
