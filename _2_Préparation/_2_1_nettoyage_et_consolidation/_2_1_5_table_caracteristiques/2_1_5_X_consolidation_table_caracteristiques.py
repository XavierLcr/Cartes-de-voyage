################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation/_2_1_5_table_caracteristiques/  #
# 2.1.5.X – Script de consolidation des données propres aux pays               #
################################################################################


import os, sys, unicodedata
import numpy as np
import pandas as pd

from constantes import (
    direction_donnees_intermediaires,
    direction_donnees_brutes,
    direction_donnees_geographiques,
    direction_donnees_application,
)
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_fichier,
    exporter_fichier,
    distance_haversine,
)
from _0_Utilitaires._0_4_fonctions_utiles_nettoyage import (
    mapping_pays,
    remplacer_valeurs_colonne,
)
from _0_Utilitaires._0_5_isid import isid


# 1 -- Import des données ------------------------------------------------------


## 1.1 -- Données simples ------------------------------------------------------


### Table des données géographiques --------------------------------------------


gdf_1 = ouvrir_fichier(
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_1.pkl",
    defaut=None,
    afficher_erreur="Table non trouvée...",
)


### Table du Global Data Lab (GDL) ---------------------------------------------


# IDH
df_IDH = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="IDH.pkl",
    defaut=None,
)

# Températures
df_temperature = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="temperature.pkl",
    defaut=None,
)

# Pluies
df_pluie = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="pluie.pkl",
    defaut=None,
)

# Humidité
df_humidite = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="humidite.pkl",
    defaut=None,
)

# Urbanisme
df_urbanisme = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="urbanisme.pkl",
    defaut=None,
)

# Justice
df_justice = ouvrir_fichier(
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="justice.pkl",
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


## 1.2 -- Données alimentaires -------------------------------------------------


### Fonction générique ---------------------------------------------------------


def ouvrir_gdd(direction, nom_fichier):

    df_temp = pd.read_csv(os.path.join(direction, nom_fichier))
    df_temp = df_temp[
        (df_temp["year"] == 2018)
        & (df_temp["edu"] == 999)
        & (df_temp["age"] == 999)
        & (df_temp["female"] == 999)
        & (df_temp["urban"] == 999)
    ]
    df_temp = df_temp.rename(columns={"median": "alimentation"})

    # Test de granularité
    assert df_temp.duplicated(subset=["iso3"], keep=False).sum() == 0, df_temp[
        df_temp.duplicated(subset=["iso3"], keep=False)
    ]

    return df_temp[["iso3", "alimentation"]]


### Application ----------------------------------------------------------------


# Récupération des noms de fichiers
csv_alimentation = [
    f
    for f in os.listdir(os.path.join(direction_donnees_brutes, "Alimentation"))
    if f.endswith(".csv")
]

df_alimentation = pd.read_excel(
    os.path.join(
        direction_donnees_brutes,
        "Alimentation",
        "GDD 2018 Codebook_Jan 10 2022.xlsx",
    ),
    sheet_name="Stratum-level characteristics",
    skiprows=1,
)[["Label", "Code"]]
df_alimentation.rename(columns={"Label": "name_0", "Code": "iso3"}, inplace=True)

for i in range(len(csv_alimentation)):

    df_alimentation = df_alimentation.merge(
        right=ouvrir_gdd(
            direction=os.path.join(direction_donnees_brutes, "Alimentation"),
            nom_fichier=csv_alimentation[i],
        ),
        how="outer",
        on="iso3",
        suffixes=("", f"_{i}"),
    )


# 2 -- Nettoyage ---------------------------------------------------------------


## 2.1 -- Données géographiques ------------------------------------------------


gdf_1["centroid"] = gdf_1["geometry"].centroid
gdf_1["superficie"] = gdf_1["geometry"].area
gdf_1["latitude"] = gdf_1["centroid"].y
gdf_1["longitude"] = gdf_1["centroid"].x
gdf_1 = gdf_1.drop(columns=["centroid"])
gdf_1 = gdf_1.drop(columns=["geometry"])


## 2.2 -- Table des données alimentaires ---------------------------------------


df_alimentation.loc[df_alimentation["iso3"] == "SSD", "name_0"] = "South Sudan"
df_alimentation.drop("iso3", axis=1, inplace=True)
df_alimentation = remplacer_valeurs_colonne(
    df=df_alimentation, colonne="name_0", mapping=mapping_pays
)


# 3 -- Jointures ---------------------------------------------------------------


## 3.1 -- Avec les données GDL -------------------------------------------------


### Fonction générique de jointure avec une table GDL --------------------------


def normalize_string(s):
    if pd.isna(s):
        return ""
    s = "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )
    s = s.lower().replace(" ", "").replace("-", "").replace("'", "")
    return s


def merge_with_match(df1, df2):

    # Fonction interne pour trouver la correspondance pour une ligne
    def find_match_row(row):
        candidates = df2[df2["name_0"] == row["name_0"]].copy()

        name_1_row = normalize_string(row["name_1"])
        candidates["name_1_norm"] = candidates["name_1"].apply(normalize_string)

        match = candidates[candidates["name_1_norm"].str.contains(name_1_row, na=False)]

        if not match.empty:
            return match.iloc[0]
        else:
            total_match = candidates[candidates["name_1"].str.lower() == "total"]
            if not total_match.empty:
                return total_match.iloc[0]
            else:
                return pd.Series({col: pd.NA for col in df2.columns})

    # Appliquer la fonction à df1
    matched = df1.apply(find_match_row, axis=1)

    # Ne garder que les colonnes de df2 à ajouter (sauf name_0 et name_1)
    cols_to_add = [col for col in df2.columns if col not in ["name_0", "name_1"]]
    matched_filtered = matched[cols_to_add]

    # Combiner avec df1
    result = pd.concat(
        [df1.reset_index(drop=True), matched_filtered.reset_index(drop=True)], axis=1
    )

    return result


### Application ----------------------------------------------------------------


# Avec les tables GDL
gdf_1 = merge_with_match(gdf_1, df_IDH)
gdf_1 = merge_with_match(gdf_1, df_temperature)
gdf_1 = merge_with_match(gdf_1, df_pluie)
gdf_1 = merge_with_match(gdf_1, df_humidite)
gdf_1 = merge_with_match(gdf_1, df_urbanisme)
gdf_1 = merge_with_match(gdf_1, df_justice)


## 3.2 -- Jointures avec le reste des table ------------------------------------


### Table de tourisme ----------------------------------------------------------


# Test de granularité
assert isid(df=df_tourisme, colonnes="name_0", blabla=1)

# Jointure
gdf_1 = gdf_1.merge(right=df_tourisme, how="left", on="name_0")


### Table des données religieuses ----------------------------------------------


# Test de granularité
assert isid(df=df_religion, colonnes="name_0", blabla=1)

# Jointure
gdf_1 = gdf_1.merge(right=df_religion, how="left", on="name_0")


### Table des données alimentaires ---------------------------------------------


# Test de granularité
assert isid(df=df_alimentation, colonnes="name_0", blabla=1)

# Jointure
gdf_1 = gdf_1.merge(right=df_alimentation, how="left", on="name_0")


### Table des données environnementales ----------------------------------------


# Test de granularité
assert isid(df=df_environnement, colonnes="name_0", blabla=1)

# Jointure
gdf_1 = gdf_1.merge(right=df_environnement, how="left", on="name_0")


### Table des similarités linguistiques ----------------------------------------


# Test de granularité
assert isid(df=df_langues, colonnes="name_0", blabla=1)

# Jointure
gdf_1 = gdf_1.merge(right=df_langues, how="left", on="name_0")


## 3.3 -- Ajout du nombre de NAs -----------------------------------------------


colonnes_a_exclure = [
    "name_0",
    "name_1",
    "latitude",
    "longitude",
    "superficie",
    "population",
]
gdf_1["nombre_na"] = gdf_1.drop(columns=colonnes_a_exclure).isna().sum(axis=1) / (
    gdf_1.shape[1] - len(colonnes_a_exclure)
)


# 4 -- Imputation des valeurs manquantes et normalisation ----------------------


## 4.1 -- Imputation selon les régions les plus proches ------------------------


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


gdf_1 = imputation_geo_knn(
    df=gdf_1,
    n_voisins=10,
    colonnes_exclues=colonnes_a_exclure,
)


## 4.2 -- Normalisation des colonnes -------------------------------------------


### Normalisation entre le minimum (0) et le maximum (1) -----------------------


for col in gdf_1.columns:
    if col not in colonnes_a_exclure:
        gdf_1[col] = (gdf_1[col] - gdf_1[col].min()) / (
            gdf_1[col].max() - gdf_1[col].min()
        )


### Pondération des colonnes ---------------------------------------------------


for pattern, pondération in {
    "alimentation": 2.25,
    "religion": 1,
    "temperature": 2,
    "environnement": 1.6,
    "langue": 1.2,
}.items():
    colonnes_i = [col for col in gdf_1.columns if pattern in col.lower()]
    for col in colonnes_i:
        gdf_1[col] = pondération * gdf_1[col] / len(colonnes_i)


### Assignation du type "float" aux colonnes -----------------------------------


for col in gdf_1.select_dtypes(include="object").columns:
    if col not in ["name_0", "name_1", "name_2"]:
        gdf_1[col] = gdf_1[col].astype(float)


# 5 -- Export ------------------------------------------------------------------


exporter_fichier(
    objet=gdf_1,
    direction_fichier=direction_donnees_application,
    nom_fichier="caracteristiques_des_regions.pkl",
)
