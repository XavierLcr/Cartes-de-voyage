import os, yaml, pickle
import pandas as pd
from constantes import direction_donnees


def cree_yaml_un_pays(
    gdf,
    nom_pays: None | list = ["France"],
    granularite: int = 1,
    nom="subdivisions_pays.yaml",
):
    """Crée le yaml pour un pays à un niveau de granularité donné

    Args:
        gdf: la base geopandas.
        nom_pays (str): nom du pays dans la dataframe geopandas.
        granularite (int): 1 (faible) à 5 (forte). Sera réduite si inexistante.
        nom (str): nom du document.
    """

    if nom_pays is not None:
        gdf = gdf[gdf["NAME_0"].isin(nom_pays)]

    # On garde le pays et la subdivision voulue
    gdf = set(zip(gdf["NAME_0"], gdf[f"NAME_{granularite}"]))

    # Créer un DataFrame avec les résultats
    liste_combinaisons = pd.DataFrame(list(gdf), columns=["nom1", "nom2"])

    # Trier le DataFrame par 'nom2' (la deuxième colonne)
    liste_combinaisons.sort_values(by="nom2", inplace=True)

    # Grouper par 'nom1' et collecter les 'nom2' dans une liste
    df_dict = liste_combinaisons.groupby("nom1")["nom2"].apply(list).to_dict()

    if granularite > 1 and len(liste_combinaisons) == 1:
        cree_yaml_un_pays(gdf=gdf, nom_pays=nom_pays, granularite=granularite - 1, nom=nom)
    else:

        # Exporter vers YAML
        with open(nom, "w", encoding="utf-8") as file:
            yaml.dump(df_dict, file, default_flow_style=False, allow_unicode=True)


# with open(direction_donnees + "\\carte_monde_niveau_5.pkl", "rb") as f:
#     gdf = pickle.load(f)

granularite = 2
with open(
    os.path.join(direction_donnees, f"carte_monde_niveau_{granularite}_bis.pkl"),
    "rb",
) as f:
    gdf = pickle.load(f)

cree_yaml_un_pays(
    gdf=gdf,
    nom_pays=None,
    granularite=2,
    nom=r"C:\Users\xaruo\Documents\Voyages\liste_pays_departements.yaml",
)
