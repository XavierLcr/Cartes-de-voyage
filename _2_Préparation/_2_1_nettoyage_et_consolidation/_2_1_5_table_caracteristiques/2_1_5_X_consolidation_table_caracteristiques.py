################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation/_2_1_5_table_caracteristiques/  #
# 2.1.5.X – Script de consolidation des données propres aux pays               #
################################################################################


import numpy as np
import pandas as pd

from constantes import (
    direction_donnees_intermediaires,
    direction_donnees_geographiques,
    direction_donnees_application,
)
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_fichier,
    exporter_fichier,
    distance_haversine,
)
from _0_Utilitaires._0_5_isid import isid

# 1 -- Import des données ------------------------------------------------------


### Table des données géographiques --------------------------------------------


gdf_1 = ouvrir_fichier(
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_1.pkl",
    defaut=None,
    afficher_erreur="Table non trouvée...",
)


### Table du Global Data Lab (GDL) ---------------------------------------------


# Données nationales
df_gdl_nat = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="gdl_nationale.pkl",
    defaut=None,
)

# Données régionales
df_gdl_reg = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="gdl_regionale.pkl",
    defaut=None,
)


### Langues --------------------------------------------------------------------


df_langues = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="langues.pkl",
    defaut=None,
)


### Religions ------------------------------------------------------------------


df_religion = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="religion.pkl",
    defaut=None,
)


### Tourisme -------------------------------------------------------------------


df_tourisme = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="tourisme.pkl",
    defaut=None,
)


### Données environnementales --------------------------------------------------


df_environnement = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="environnement.pkl",
    defaut=None,
)


### Données alimentaires -------------------------------------------------------


df_alimentation = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="alimentation.pkl",
    defaut=None,
)


# 2 -- Consolidation -----------------------------------------------------------


## 2.1 -- Données géographiques ------------------------------------------------


gdf_cons = gdf_1.assign(
    latitude=gdf_1["geometry"].centroid.y,
    longitude=gdf_1["geometry"].centroid.x,
    superficie=gdf_1["geometry"].area,
).drop(columns=["geometry"])


## 2.2 -- Jointures avec les différentes tables --------------------------------


### Tables du Global Data Lab --------------------------------------------------


# Tests de granularité
assert isid(df=df_gdl_reg, colonnes=["name_0", "name_1"], blabla=1)
assert isid(df=df_gdl_nat, colonnes="name_0", blabla=1)

# Jointures
gdf_cons = gdf_cons.merge(right=df_gdl_reg, on=["name_0", "name_1"], how="left").merge(
    right=df_gdl_nat, on=["name_0"], how="left", suffixes=("", "_nat")
)

# Remplacement des valeurs manquantes
for a, b in [
    ("IDH", "IDH_nat"),
    ("temperature", "temperature_nat"),
    ("humidite", "humidite_nat"),
    ("pluie", "pluie_nat"),
    ("urbanisation", "urbanisation_nat"),
    ("corruption", "corruption_nat"),
]:
    gdf_cons = (
        gdf_cons
        # Complétion des valeurs régionales manquantes avec les valeurs nationales
        .assign(temp=lambda df: df[a].fillna(df[b]))
        # Suppression de la colonne nationale, devenue obsolète
        .drop(columns=[a, b]).rename(columns={"temp": a})
    )


### Table de tourisme ----------------------------------------------------------


# Test de granularité
assert isid(df=df_tourisme, colonnes="name_0", blabla=1)

# Jointure
gdf_cons = gdf_cons.merge(right=df_tourisme, how="left", on="name_0")


### Table des données religieuses ----------------------------------------------


# Test de granularité
assert isid(df=df_religion, colonnes="name_0", blabla=1)

# Jointure
gdf_cons = gdf_cons.merge(right=df_religion, how="left", on="name_0")


### Table des données alimentaires ---------------------------------------------


# Test de granularité
assert isid(df=df_alimentation, colonnes="name_0", blabla=1)

# Jointure
gdf_cons = gdf_cons.merge(right=df_alimentation, how="left", on="name_0")


### Table des données environnementales ----------------------------------------


# Test de granularité
assert isid(df=df_environnement, colonnes="name_0", blabla=1)

# Jointure
gdf_cons = gdf_cons.merge(right=df_environnement, how="left", on="name_0")


### Table des similarités linguistiques ----------------------------------------


# Test de granularité
assert isid(df=df_langues, colonnes="name_0", blabla=1)

# Jointure
gdf_cons = gdf_cons.merge(right=df_langues, how="left", on="name_0")


## 2.4 -- Ajout du nombre de NAs -----------------------------------------------


colonnes_a_exclure = [
    "name_0",
    "name_1",
    "latitude",
    "longitude",
    "superficie",
    "population",
]
gdf_cons["nombre_na"] = gdf_cons.drop(columns=colonnes_a_exclure).isna().sum(axis=1) / (
    gdf_cons.shape[1] - len(colonnes_a_exclure)
)


# 3 -- Imputation des valeurs manquantes, normalisation et pondération ---------


## 3.1 -- Imputation selon les régions les plus proches ------------------------


### Fonction d'imputation ------------------------------------------------------


def imputation_geo_knn(
    df, n_voisins=5, colonnes_exclues=None, col_long="longitude", col_lat="latitude"
):
    """
    Remplace les valeurs manquantes (NaN) par la moyenne des n voisins
    géographiques les plus proches (selon la distance de Haversine).

    Paramètres
    ----------
    df : pd.DataFrame
        Table contenant les données avec colonnes latitude/longitude.
    n_voisins : int
        Nombre de voisins à utiliser pour calculer la moyenne.
    colonnes_exclues : list
        Colonnes à ne pas imputer (ex: identifiants, variables cibles).
    col_long : str
        Nom de la colonne longitude.
    col_lat : str
        Nom de la colonne latitude.

    Retour
    ------
    pd.DataFrame : copie du DataFrame avec les valeurs imputées.
    """

    if colonnes_exclues is None:
        colonnes_exclues = []

    # Colonnes sur lesquelles on applique l’imputation
    colonnes_a_imputer = [
        c for c in df.columns if c not in colonnes_exclues + [col_long, col_lat]
    ]
    df_impute = df.copy()

    # Pré-calcul des coordonnées pour éviter les accès répétés
    coords = df_impute[[col_lat, col_long]].values

    for col in colonnes_a_imputer:
        print(col)
        lignes_na = df_impute[col].isna()
        if not lignes_na.any():
            continue  # Aucune valeur manquante

        # Indices des lignes avec des valeurs valides
        indices_valides = df_impute[~lignes_na].index
        valeurs_valides = df_impute.loc[indices_valides, col].values

        for idx in df_impute[lignes_na].index:
            # Calcul des distances entre la ligne courante et toutes les lignes valides
            lat1, lon1 = coords[idx]
            distances = np.array(
                [
                    distance_haversine(lat1, lon1, lat2, lon2)
                    for lat2, lon2 in coords[indices_valides]
                ]
            )

            # Indices des n voisins les plus proches
            voisins_idx = np.argsort(distances)[:n_voisins]
            poids = 1 / (distances[voisins_idx] + 1e-10)  # Évite la division par zéro
            valeurs_voisins = valeurs_valides[voisins_idx]

            # Imputation pondérée
            df_impute.loc[idx, col] = np.sum(valeurs_voisins * poids) / np.sum(poids)

    return df_impute


### Application ----------------------------------------------------------------


gdf_cons = imputation_geo_knn(
    df=gdf_cons,
    n_voisins=10,
    colonnes_exclues=colonnes_a_exclure,
    col_long="longitude",
    col_lat="latitude",
)


## 3.2 -- Normalisation des colonnes -------------------------------------------


### Fonction de normalisation entre 0 et 1 des valeurs -------------------------


def normaliser_min_max(df: pd.DataFrame, colonnes_a_exclure: list = []):
    """
    Normalise les colonnes d'un GeoDataFrame ou DataFrame avec la formule :
    (valeur - min) / (max - min)
    pour toutes les colonnes sauf celles dans `colonnes_a_exclure`.

    Args:
        gdf (gpd.GeoDataFrame ou pd.DataFrame) : DataFrame à normaliser.
        colonnes_a_exclure (list) : Liste des noms de colonnes à exclure.

    Returns:
        gpd.GeoDataFrame ou pd.DataFrame : DataFrame normalisé.
    """

    df_temp = df.copy()

    for col in df_temp.columns:
        if col not in colonnes_a_exclure:
            min_val = df_temp[col].min()
            max_val = df_temp[col].max()

            # Évite la division par zéro si max_val == min_val
            if max_val != min_val:
                df_temp[col] = (df_temp[col] - min_val) / (max_val - min_val)
            else:
                # Suppression de la colonne
                df_temp.drop(columns=[col])

    return df_temp


### Application ----------------------------------------------------------------


gdf_cons = normaliser_min_max(gdf_cons, colonnes_a_exclure)


## 3.3 -- Pondération des colonnes ---------------------------------------------


for pattern, pondération in {
    "alimentation": 2.25,
    "religion": 1,
    "temperature": 2,
    "environnement": 1.6,
    "langue": 1.2,
}.items():
    colonnes_i = [col for col in gdf_cons.columns if pattern in col.lower()]
    for col in colonnes_i:
        gdf_cons[col] = pondération * gdf_cons[col] / len(colonnes_i)


## 3.4 -- Assignation du type "float" aux colonnes -----------------------------


for col in gdf_cons.select_dtypes(include="object").columns:
    if col not in ["name_0", "name_1", "name_2"]:
        print(col)
        gdf_cons[col] = gdf_cons[col].astype(float)


# 4 -- Export ------------------------------------------------------------------


# Test de granularité
assert isid(df=gdf_cons, colonnes=["name_0", "name_1"], blabla=1)

# Export
exporter_fichier(
    objet=gdf_cons,
    direction_fichier=direction_donnees_application,
    nom_fichier="caracteristiques_des_regions.pkl",
)
