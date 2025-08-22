import os, pickle
import pandas as pd
import geopandas as gpd
from constantes import direction_donnees, direction_base

gdf = gpd.read_file(os.path.join(direction_base, "Donnees_granu_et_plus", "gadm_410.gpkg"))

# On ne garde que les colonnes utiles
gdf = gdf[["NAME_0", "NAME_1", "NAME_2", "NAME_3", "NAME_4", "NAME_5", "geometry"]]

with open(direction_donnees + "\\geodataframe_reduit.pkl", "wb") as f:
    pickle.dump(gdf, f)

## On crée les cartes du monde avec une plus faible granularité

# Niveau 4
gdf_niveau_4 = gdf.dissolve(
    by=["NAME_0", "NAME_1", "NAME_2", "NAME_3", "NAME_4"],
    aggfunc={
        "NAME_0": "first",
        "NAME_1": "first",
        "NAME_2": "first",
        "NAME_3": "first",
        "NAME_4": "first",
    },
)

with open(direction_donnees + "\\carte_monde_niveau_4.pkl", "wb") as f:
    pickle.dump(gdf_niveau_4, f)

gdf_niveau_4 = gdf.dissolve(
    by=["NAME_0", "NAME_1", "NAME_2", "NAME_3", "NAME_4"],
    aggfunc={
        "NAME_0": "first",
        "NAME_1": "first",
        "NAME_2": "first",
        "NAME_3": "first",
        "NAME_4": "first",
    },
)

with open(direction_donnees + "\\carte_monde_niveau_4.pkl", "wb") as f:
    pickle.dump(gdf_niveau_4, f)


gdf_niveau_3 = gdf.dissolve(
    by=["NAME_0", "NAME_1", "NAME_2", "NAME_3"],
    aggfunc={
        "NAME_0": "first",
        "NAME_1": "first",
        "NAME_2": "first",
        "NAME_3": "first",
    },
)

with open(direction_donnees + "\\carte_monde_niveau_3.pkl", "wb") as f:
    pickle.dump(gdf_niveau_3, f)

gdf_niveau_2 = gdf.dissolve(
    by=["NAME_0", "NAME_1", "NAME_2"],
    aggfunc={
        "NAME_0": "first",
        "NAME_1": "first",
        "NAME_2": "first",
    },
)

with open(direction_donnees + "\\carte_monde_niveau_2.pkl", "wb") as f:
    pickle.dump(gdf_niveau_2, f)

gdf_niveau_1 = gdf.dissolve(
    by=["NAME_0", "NAME_1"],
    aggfunc={
        "NAME_0": "first",
        "NAME_1": "first",
    },
)

with open(direction_donnees + "\\carte_monde_niveau_1.pkl", "wb") as f:
    pickle.dump(gdf_niveau_1, f)

gdf_niveau_0 = gdf.dissolve(
    by=["NAME_0"],
    aggfunc={
        "NAME_0": "first",
    },
)

with open(direction_donnees + "\\carte_monde_niveau_0.pkl", "wb") as f:
    pickle.dump(gdf_niveau_0, f)


def concatener_noms_si_dupliques(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pour chaque colonne NAME_i (en partant de NAME_n vers NAME_1), concatène les valeurs
    des colonnes NAME_0 à NAME_i si le couple (NAME_0, NAME_i) apparaît plusieurs fois.

    Paramètres :
    - df (pd.DataFrame) : Le DataFrame à traiter.

    Retour :
    - pd.DataFrame : Le DataFrame modifié.
    """

    # Identifier toutes les colonnes NAME_i et les trier selon l'indice croissant
    colonnes = sorted(
        [col for col in df.columns if col.startswith("NAME_")],
        key=lambda x: int(x.split("_")[1]),
    )

    # Récursivement, on part de NAME_n vers NAME_1 (on ne touche pas à NAME_0)
    for i in range(len(colonnes) - 1, 0, -1):
        col_courante = colonnes[i]
        # Vérifier les doublons (NAME_0, NAME_i)
        doublons = df.duplicated(subset=["NAME_0", col_courante], keep=False)

        # Colonnes à concaténer : NAME_0 à NAME_i
        colonnes_a_concat = colonnes[: i + 1]

        # Fonction de concaténation
        def concat_ligne(ligne):
            return "-".join(
                str(ligne[col]) for col in colonnes_a_concat if pd.notnull(ligne[col])
            ).strip("- ")

        # Appliquer la concaténation sur les doublons
        df.loc[doublons, col_courante] = df.loc[doublons, colonnes_a_concat].apply(
            concat_ligne, axis=1
        )

    return df


for i in range(3, 6):
    print(f"Granularité : {i}")
    with open(
        os.path.join(direction_base, "Donnees_granu_et_plus", f"carte_monde_niveau_{i}.pkl"),
        "rb",
    ) as f:
        gdf_niveau_i = pickle.load(f)

    gdf_nv_i = concatener_noms_si_dupliques(gdf_niveau_i)

    with open(
        os.path.join(direction_base, "Donnees_granu_et_plus", f"carte_monde_niveau_{i}.pkl"),
        "wb",
    ) as f:
        pickle.dump(gdf_nv_i, f)
