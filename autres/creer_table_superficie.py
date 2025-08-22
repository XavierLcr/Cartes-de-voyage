import pickle
import constantes
import os


# Fonction de calcul de la superficie
def calculer_superficie(gdf, espg):

    gdf = gdf.to_crs(epsg=espg)
    gdf["superficie"] = gdf.geometry.area

    gdf["superficie_par_pays"] = gdf.groupby("NAME_0")["superficie"].transform("sum")

    gdf["pct_superficie_dans_pays"] = gdf["superficie"] / gdf["superficie_par_pays"]

    liste_cols = list(gdf.columns)
    liste_cols.remove("geometry")
    liste_cols.remove("superficie_par_pays")

    return gdf[liste_cols]


# Téléchargement de la table
with open(
    os.path.join(constantes.direction_donnees_application, "carte_monde_niveau_2.pkl"),
    "rb",
) as f:
    gdf = pickle.load(f)

gdf = gdf.reset_index(drop=True)
gdf_sup = calculer_superficie(gdf, espg=8857)

with open(os.path.join(constantes.direction_donnees, "table_superficie.pkl"), "wb") as f:
    pickle.dump(gdf_sup, f)
