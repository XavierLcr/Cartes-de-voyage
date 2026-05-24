################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1.1 – Création des cartes                                             #
################################################################################


from PyQt6.QtCore import pyqtSignal, QObject
from _3_Calculs._3_4_carte_main import (
    cree_graphe_depuis_debut,
    creer_multiples_cartes,
    lister_cartes_a_publier,
)
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    voyages_vers_destinations_une_granu,
)

# 1 -- Classe de suivi de l'avancement de la publication des cartes ------------


class TrackerPays(QObject):
    tracker_pays_en_cours = pyqtSignal(str)

    def notify(self, libelle_pays: str):
        self.tracker_pays_en_cours.emit(libelle_pays)


# 2 -- Classe de création des cartes -------------------------------------------


class CreerCartes(QObject):

    finished = pyqtSignal()
    tracker_signal = pyqtSignal(str)
    nb_graphes = pyqtSignal(int)

    def __init__(self, params, constantes):

        super().__init__()

        # Récupération des paramètres
        self.parametres = params
        self.constantes = constantes

        # Liste des cartes à publier
        self.liste_cartes = lister_cartes_a_publier(
            regroupements_pays_ref=constantes.liste_pays_groupes,
            continents_ref=constantes.liste_regions_monde,
            traductions_ref=constantes.pays_differentes_langues,
            langue=self.parametres["langue"],
            pays=self.parametres["cartes_des_pays"],
            monde=self.parametres["carte_du_monde"],
            continents=self.recuperer_continents(),
            voyages=self.parametres.get("dictionnaire_voyages", {}),
            sortir_cartes_granu_inf=self.parametres.get(
                "sortir_cartes_granu_inf", False
            ),
            granularite_objectif=self.recuperer_granularite(clef="granularite"),
        )

    def recuperer_granularite(self, clef: str):
        return {"Pays": 0, "Région": 1, "Département": 2}.get(
            self.parametres.get(clef), -1
        )

    def recuperer_continents(self):

        dict_bouton_continent = {
            "afrique": ["Africa"],
            "amerique": ["South America", "North America"],
            "asie": ["Asia"],
            "europe": ["Europe"],
            "moyen_orient": ["Middle East"],
        }

        # Ajout des continents souhaités
        liste_regions_temp = {
            region: self.constantes.liste_regions_monde[region]
            for cle_param, regions in dict_bouton_continent.items()
            if self.parametres.get(cle_param, False)
            for region in regions
        }

        # Ajout des régions complémentaires (si souhaité)
        if self.parametres.get("autres_regions", False):

            liste_regions_temp.update(
                {
                    k: v
                    for k, v in self.constantes.liste_regions_monde.items()
                    if k
                    not in [
                        region
                        for regions in dict_bouton_continent.values()
                        for region in regions
                    ]
                }
            )

        # Renvoi
        return liste_regions_temp

    def run(self):

        # === Ajustement des variables ===

        dict_regions = voyages_vers_destinations_une_granu(
            dict_voyages=self.parametres.get("dictionnaire_voyages", {}), clef="region"
        )
        dict_deps = voyages_vers_destinations_une_granu(
            dict_voyages=self.parametres.get("dictionnaire_voyages", {}), clef="dep"
        )

        if dict_deps is not None:
            if dict_deps != {} and dict_regions is not None:
                dict_regions = {
                    k: v for k, v in dict_regions.items() if k not in dict_deps
                }

        if dict_deps == {}:
            dict_deps = None
        if dict_regions == {}:
            dict_regions = None

        self.nb_graphes.emit(self.calculer_nb_total_graphes())

        # Gestion de l'e-mail
        if not self.parametres.get("adresse_email") or not self.parametres.get(
            "envoi_email"
        ):
            self.parametres["adresse_email"] = None

        # --- Partie calcul cartes ---
        tracker = TrackerPays()
        tracker.tracker_pays_en_cours.connect(self.tracker_signal.emit)

        cree_graphe_depuis_debut(
            liste_dfs=self.parametres["liste_dfs"],
            liste_dicts=[dict_regions, dict_deps],
            gdf_eau=self.parametres["gdf_eau"],
            noms_pays=self.constantes.pays_differentes_langues,
            dictionnaire_pays_unis=self.constantes.liste_pays_groupes,
            nom_indiv=self.parametres["nom"],
            direction_resultat=self.parametres["dossier_stockage"],
            ouvrir_direction_resultat=self.parametres["ouvrir_dossier_stockage"],
            langue=self.parametres["langue"],
            granularite_visite=self.recuperer_granularite(clef="granularite"),
            granularite_reste=self.recuperer_granularite(clef="granularite_fond"),
            theme=self.constantes.liste_ambiances[
                self.parametres.get("theme", "Pastel")
            ],
            teinte=self.constantes.liste_couleurs[
                self.parametres.get("couleur", "Multicolore")
            ],
            couleur_fond=self.constantes.dictionnaire_arriere_plans[
                self.parametres.get("couleur_fond_carte", "Blanc")
            ],
            couleur_non_visites="#DFDFDF",
            couleur_pays_contours="#EBEBEB",
            couleur_lacs="#CDEAF7",
            format=self.parametres["format"],
            qualite=self.parametres["qualite"],
            carte_du_monde=self.parametres["carte_du_monde"],
            liste_regions=self.recuperer_continents(),
            pays_individuel=self.parametres["cartes_des_pays"],
            limite_n_cartes=self.parametres["limite_n_cartes"],
            sortir_cartes_granu_inf=self.parametres["sortir_cartes_granu_inf"],
            tracker=tracker,
            blabla=False,
            afficher_nom_lieu=False,
            adresse_email=self.parametres.get("adresse_email"),
        )

        self.finished.emit()

    def calculer_nb_total_graphes(self):
        return len(self.liste_cartes.keys())
