import os, sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from constantes import (
    direction_donnees_autres,
    direction_donnees_application,
)
from _0_Utilitaires._0_1_Fonctions_utiles import ouvrir_fichier, exporter_fichier


def cree_yaml_un_pays(
    gdf,
    direction_fichier,
    nom_fichier,
    nom_pays: None | list = ["France"],
    granularite: int = 1,
):
    """Crée le yaml pour un pays à un niveau de granularité donné

    Args:
        gdf: la base geopandas.
        nom_pays (str): nom du pays dans la dataframe geopandas.
        granularite (int): 1 (faible) à 5 (forte). Sera réduite si inexistante.
        nom (str): nom du document.
    """

    if nom_pays is not None:
        gdf = gdf[gdf["name_0"].isin(nom_pays)]

    # On garde le pays et la subdivision voulue
    gdf = set(zip(gdf["name_0"], gdf[f"name_{granularite}"]))

    # Créer un DataFrame avec les résultats
    liste_combinaisons = (
        pd.DataFrame(list(gdf), columns=["nom1", "nom2"])
        # Tri par nom2
        .sort_values(by="nom2", inplace=False)
    )

    if granularite > 1 and len(liste_combinaisons) == 1:
        cree_yaml_un_pays(
            gdf=gdf,
            nom_pays=nom_pays,
            granularite=granularite - 1,
            direction_fichier=direction_fichier,
            nom_fichier=nom_fichier,
        )
    else:

        # Exporter vers YAML
        exporter_fichier(
            objet=liste_combinaisons.groupby("nom1")["nom2"].apply(list).to_dict(),
            direction_fichier=direction_fichier,
            nom_fichier=nom_fichier,
            sort_keys=True,
        )


for granularite in range(6):

    print(granularite, end=" ; ")

    gdf = ouvrir_fichier(
        direction_fichier=direction_donnees_autres,
        nom_fichier=f"carte_monde_niveau_{granularite}.pkl",
        defaut=None,
        afficher_erreur="Base non trouvée.",
    )

    cree_yaml_un_pays(
        gdf=gdf,
        nom_pays=None,
        granularite=granularite,
        direction_fichier=direction_donnees_autres,
        nom_fichier=f"liste_pays_granularite_{granularite}.yaml",
    )
