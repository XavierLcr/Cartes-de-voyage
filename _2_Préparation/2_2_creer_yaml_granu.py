import os, sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from constantes import (
    direction_donnees_autres,
    direction_donnees_application,
)
from _0_Utilitaires._0_1_Fonctions_utiles import ouvrir_fichier, cree_yaml_un_pays


for granularite in range(1, 6):

    print(granularite)

    gdf = ouvrir_fichier(
        direction_fichier=direction_donnees_application,
        nom_fichier=f"carte_monde_niveau_{granularite}.pkl",
        defaut=None,
        afficher_erreur="Base non trouvée.",
    )

    cree_yaml_un_pays(
        gdf=gdf,
        nom_pays=None,
        granularite=granularite,
        direction_fichier=direction_donnees_application,
        nom_fichier=f"liste_pays_granularite_{granularite}.yaml",
    )
