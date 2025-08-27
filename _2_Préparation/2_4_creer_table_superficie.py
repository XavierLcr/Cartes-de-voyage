import pickle
import constantes
import os
from _0_Utilitaires._0_1_Fonctions_utiles import ouvrir_fichier


# Fonction de calcul de la superficie
def calculer_superficie(gdf, espg):

    gdf = gdf.to_crs(epsg=espg).assign(
        superficie=lambda x: x.geometry.area,
        superficie_par_pays=lambda x: x.groupby("NAME_0")["superficie"].transform("sum"),
        pct_superficie_dans_pays=lambda x: x["superficie"] / x["superficie_par_pays"],
    )

    liste_cols = list(gdf.columns)
    liste_cols.remove("geometry")
    liste_cols.remove("superficie_par_pays")

    return gdf[liste_cols]


# Téléchargement des données
gdf = ouvrir_fichier(
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="carte_monde_niveau_2.pkl",
    defaut=None,
).reset_index(drop=True)

# Export de la table
with open(os.path.join(constantes.direction_donnees, "table_superficie.pkl"), "wb") as f:
    pickle.dump(calculer_superficie(gdf, espg=8857), f)
