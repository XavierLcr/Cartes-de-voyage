################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/                                                              #
# 2.4 – Fichier de création de la table de superficie utile à l'onglet n°4     #
################################################################################

import os, sys, pickle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constantes
from _0_Utilitaires._0_1_Fonctions_utiles import ouvrir_fichier


### Fonction de calcul de la superficie ----------------------------------------


def calculer_superficie(gdf, espg):

    gdf = gdf.to_crs(epsg=espg).assign(
        superficie=lambda x: x.geometry.area,
        superficie_par_pays=lambda x: x.groupby("name_0")["superficie"].transform(
            "sum"
        ),
        pct_superficie_dans_pays=lambda x: x["superficie"] / x["superficie_par_pays"],
    )

    liste_cols = list(gdf.columns)
    liste_cols.remove("geometry")
    liste_cols.remove("superficie_par_pays")

    return gdf[liste_cols]


### Application ----------------------------------------------------------------


with open(
    os.path.join(constantes.direction_donnees_application, "table_superficie.pkl"), "wb"
) as f:

    # Export
    pickle.dump(
        # Calcul de la superficie
        calculer_superficie(
            # Import des données
            ouvrir_fichier(
                direction_fichier=constantes.direction_donnees_geographiques,
                nom_fichier="carte_monde_niveau_2.pkl",
                defaut=None,
            ).reset_index(drop=True),
            espg=8857,
        ),
        f,
    )
