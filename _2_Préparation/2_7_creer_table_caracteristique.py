################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/                                                              #
# 2.7 – Script de consolidation des données propres aux pays                   #
################################################################################


import os, sys, unicodedata
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constantes
from _0_Utilitaires._0_1_Fonctions_utiles import (
    ouvrir_fichier,
    exporter_fichier,
    distance_haversine,
)


# 1 -- Fonctions utiles --------------------------------------------------------


## 1.1 -- Fonction de remplacement de valeurs au sein d'une colonne ------------


def remplacer_noms(df, colonne, mapping):
    """
    Remplace les valeurs d'une colonne selon un dictionnaire.

    Args:
        df (pd.DataFrame): ton DataFrame
        colonne (str): nom de la colonne à modifier
        mapping (dict): dictionnaire {ancien_nom: nouveau_nom}

    Returns:
        pd.DataFrame: le DataFrame modifié
    """
    df[colonne] = df[colonne].replace(mapping)
    return df


# Dictionnaire de remplacement des noms de pays
mapping = {
    # "Antigua And Barbuda": "Antigua and Barbuda",
    "Argentina urban": "Argentina",
    "Bahamas, The": "Bahamas",
    "The Bahamas": "Bahamas",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Brunei Darussalam": "Brunei",
    "Cape Verde": "Cabo Verde",
    "Central African Republic CAR": "Central African Republic",
    "Chili": "Chile",
    "Congo, Dem. Rep.": "Democratic Republic of the Congo",
    "Dem. Rep. Congo": "Democratic Republic of the Congo",
    "Congo Democratic Republic": "Democratic Republic of the Congo",
    "Congo, Rep.": "Republic of the Congo",
    "Congo Brazzaville": "Republic of the Congo",
    "Congo": "Republic of the Congo",
    "Republic of Congo": "Republic of the Congo",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Ivory Coast": "Côte d'Ivoire",
    "Curacao": "Curaçao",
    "Czech Republic": "Czechia",
    "Egypt, Arab Rep.": "Egypt",
    "Eswatini": "Swaziland",
    "Faeroe Islands": "Faroe Islands",
    "FInland": "Finland",
    "Gambia, The": "Gambia",
    "The Gambia": "Gambia",
    "Guinea Bissau": "Guinea-Bissau",
    "Holy See": "Vatican City",
    "Hong Kong SAR, China": "Hong Kong",
    "Iran, Islamic Rep.": "Iran",
    "Korea, Dem. People's Rep.": "North Korea",
    "Korea, Rep.": "South Korea",
    "Kyrgyz Republic": "Kyrgyzstan",
    "Lao PDR": "Laos",
    "Lao": "Laos",
    "Macedonia": "North Macedonia",
    "Mexico": "México",
    "Micronesia, Fed. Sts.": "Micronesia",
    "Federated States of Micronesia": "Micronesia",
    "Puerto Rico (US)": "Puerto Rico",
    "Russian Federation": "Russia",
    "Reunion": "Réunion",
    "St. Martin (French part)": "Saint-Martin",
    "Sint Maarten (Dutch part)": "Sint Maarten",
    "Sao Tome and Principe": "São Tomé and Príncipe",
    "Sao Tome & Principe": "São Tomé and Príncipe",
    "Slovak Republic": "Slovakia",
    "Saint Barthelemy": "Saint-Barthélemy",
    "St. Kitts and Nevis": "Saint Kitts and Nevis",
    "St. Lucia": "Saint Lucia",
    "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines",
    "Syrian Arab Republic": "Syria",
    # "Trinidad And Tobago": "Trinidad and Tobago",
    "Timor Leste": "Timor-Leste",
    "Turkiye": "Turkey",
    "Turks & Caicos Islands": "Turks and Caicos Islands",
    "United States of America": "United States",
    "Venezuela, RB": "Venezuela",
    "Virgin Islands (U.S.)": "Virgin Islands, US",
    "U.S. Virgin Islands": "Virgin Islands, US",
    "Viet Nam": "Vietnam",
    "Wallis and Futuna Islands": "Wallis and Futuna",
    "West Bank and Gaza": "Palestine",
    "Palestinian territories": "Palestine",
    "State of Palestine": "Palestine",
    "Yemen, Rep.": "Yemen",
}


## 1.2 -- Modifier les noms de colonnes avec des années ------------------------


def nettoyer_nom_colonne(nom):
    chiffres = "".join(filter(str.isdigit, nom))
    return chiffres if chiffres else nom


## 1.3 -- Fonction de sélection de la dernière valeur existante ---------------


def derniere_valeur_valide_par_ligne(df: pd.DataFrame) -> pd.Series:
    """
    Retourne la dernière valeur valide pour chaque ligne,
    en ne considérant que les colonnes dont le nom est un nombre entier.

    Args:
        df (pd.DataFrame): DataFrame d'entrée.

    Returns:
        pd.Series: Série contenant la dernière valeur valide pour chaque ligne.
    """
    # Filtrer les colonnes dont le nom est un nombre entier
    colonnes_chiffrees = [col for col in df.columns if str(col).isdigit()]

    # Extraire uniquement ces colonnes
    df_chiffres = df[colonnes_chiffrees]

    # Appliquer la logique pour obtenir la dernière valeur valide par ligne
    return df_chiffres.apply(
        lambda row: (
            row[row.last_valid_index()] if row.last_valid_index() is not None else pd.NA
        ),
        axis=1,
    )


# 2 -- Import des données ------------------------------------------------------


## 2.1 -- Données simples ------------------------------------------------------


# Table à compléter
gdf_1 = ouvrir_fichier(
    direction_fichier=constantes.direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_1.pkl",
    defaut=None,
    afficher_erreur="Table non trouvée...",
)

# Tables à intégrer
df_IDH = pd.read_csv(
    os.path.join(constantes.direction_donnees_brutes, "GDL-Subnational-HDI-data.csv")
)
df_temperature = pd.read_csv(
    os.path.join(
        constantes.direction_donnees_brutes,
        "GDL-Yearly-Average-Surface-Temperature-(ºC)-data.csv",
    )
)
df_pluie = pd.read_csv(
    os.path.join(
        constantes.direction_donnees_brutes,
        "GDL-Total-Yearly-Precipitation-(m)-data.csv",
    )
)
df_humidite = pd.read_csv(
    os.path.join(
        constantes.direction_donnees_brutes,
        "GDL-Yearly-Average-Relative-Humidity-(_)-data.csv",
    )
)
df_tourisme = pd.read_csv(
    os.path.join(
        constantes.direction_donnees_brutes, "API_ST.INT.ARVL_DS2_en_csv_v2_697553.csv"
    ),
    skiprows=4,
)
df_religion = pd.read_csv(
    os.path.join(
        constantes.direction_donnees_brutes,
        "Religious Composition 2010-2020 (percentages).csv",
    ),
)
df_urbanisme = pd.read_csv(
    os.path.join(
        constantes.direction_donnees_brutes,
        "GDL-_-population-in-urban-areas-data.csv",
    ),
)
df_justice = pd.read_csv(
    os.path.join(
        constantes.direction_donnees_brutes,
        "GDL-Comprehensive-Subnational-Corruption-Index-(SCI)-data.csv",
    ),
)


## 2.2 -- Données alimentaires -------------------------------------------------


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
    for f in os.listdir(
        os.path.join(constantes.direction_donnees_brutes, "Alimentation")
    )
    if f.endswith(".csv")
]

df_alimentation = pd.read_excel(
    os.path.join(
        constantes.direction_donnees_brutes,
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
            direction=os.path.join(constantes.direction_donnees_brutes, "Alimentation"),
            nom_fichier=csv_alimentation[i],
        ),
        how="outer",
        on="iso3",
        suffixes=("", f"_{i}"),
    )


## 2.3 -- Données environnementales --------------------------------------------


# Récupération des noms de fichiers
csv_environnement = [
    f
    for f in os.listdir(
        os.path.join(constantes.direction_donnees_brutes, "Environnement")
    )
    if f.endswith(".csv")
    and any(prefix in f for prefix in ["RMS", "FCL", "WWR", "UWD", "PAR"])
]


for i in range(len(csv_environnement)):

    df_temp = remplacer_noms(
        df=pd.read_csv(
            os.path.join(
                constantes.direction_donnees_brutes,
                "Environnement",
                csv_environnement[i],
            )
        ),
        colonne="country",
        mapping=mapping,
    )

    df_temp.columns = [nettoyer_nom_colonne(col) for col in df_temp.columns]
    df_temp.rename(columns={"country": "name_0"}, inplace=True)
    df_temp[f"environnement_{i}"] = derniere_valeur_valide_par_ligne(df_temp)
    df_temp = df_temp[["name_0", f"environnement_{i}"]]

    if i == 0:
        df_environnement = df_temp.copy()
    else:
        df_environnement = df_environnement.merge(
            right=df_temp, on="name_0", how="outer"
        )

# 3 -- Nettoyage ---------------------------------------------------------------


## 3.1 -- Données géographiques ------------------------------------------------


gdf_1["centroid"] = gdf_1["geometry"].centroid
gdf_1["superficie"] = gdf_1["geometry"].area
gdf_1["latitude"] = gdf_1["centroid"].y
gdf_1["longitude"] = gdf_1["centroid"].x
gdf_1 = gdf_1.drop(columns=["centroid"])
gdf_1 = gdf_1.drop(columns=["geometry"])


## 3.2 -- Données du Global Data Lab (GDL) -------------------------------------


### Fonction de nettoyage générique --------------------------------------------


def nettoyer_GDL(df: pd.DataFrame, gdf, mapping: dict, annee: str, nom_col: str):

    df = remplacer_noms(df, "Country", mapping=mapping)
    df["Country"] = df.apply(
        lambda row: (
            row["Region"]
            if row["Region"]
            in (set(df["Region"].unique()) & set(gdf["name_0"].unique()))
            else row["Country"]
        ),
        axis=1,
    )
    df = df.rename(columns={"Country": "name_0", "Region": "name_1", annee: nom_col})
    df = df.loc[df[nom_col].notna(), ["name_0", "name_1", nom_col]]

    df = df.groupby(["name_0", "name_1"], as_index=False)[nom_col].mean()

    # Test de granularité
    assert df.duplicated(subset=["name_0", "name_1"], keep=False).sum() == 0, df[
        df.duplicated(subset=["name_0", "name_1"], keep=False)
    ]

    return df


### Application ----------------------------------------------------------------


## IDH
df_IDH = nettoyer_GDL(
    df=df_IDH, gdf=gdf_1, mapping=mapping, annee="2022", nom_col="IDH"
)

## Températures
df_temperature = nettoyer_GDL(
    df=df_temperature, gdf=gdf_1, mapping=mapping, annee="2022", nom_col="temperature"
)

## Pluies
df_pluie = nettoyer_GDL(
    df=df_pluie, gdf=gdf_1, mapping=mapping, annee="2022", nom_col="pluie"
)

## Humidité
df_humidite = nettoyer_GDL(
    df=df_humidite, gdf=gdf_1, mapping=mapping, annee="2022", nom_col="humidite"
)
df_justice = nettoyer_GDL(
    df=df_justice, gdf=gdf_1, mapping=mapping, annee="2022", nom_col="corruption"
)

## Urbanisme
### Valeur la plus récente
df_urbanisme["recent"] = df_urbanisme[
    [col for col in df_urbanisme.columns if col.isdigit()]
].apply(
    lambda row: (
        row[row.last_valid_index()] if row.last_valid_index() is not None else pd.NA
    ),
    axis=1,
)
df_urbanisme = nettoyer_GDL(
    df=df_urbanisme, gdf=gdf_1, mapping=mapping, annee="recent", nom_col="urbanisation"
)


## 3.3 -- Table du tourisme ----------------------------------------------------


df_tourisme = df_tourisme.loc[
    :, df_tourisme.nunique(dropna=False) > 1
]  # Suppression des colonnes constantes
df_tourisme = df_tourisme.dropna(axis=1, how="all")  # Suppression des colonnes que NA
# Valeur la plus récente
df_tourisme["tourisme"] = df_tourisme[
    [col for col in df_tourisme.columns if col.isdigit()]
].apply(
    lambda row: (
        row[row.last_valid_index()] if row.last_valid_index() is not None else pd.NA
    ),
    axis=1,
)
df_tourisme = df_tourisme[["Country Name", "tourisme"]]
df_tourisme.rename(columns={"Country Name": "name_0"}, inplace=True)


## 3.4 -- Table des données religieuses ----------------------------------------


df_religion = df_religion[df_religion["Level"] == 1]  # Sélection des pays
df_religion = df_religion[df_religion["Year"] == 2020]  # Sélection de 2020
df_religion.drop(columns=["Year", "Level", "Countrycode", "Region"], inplace=True)
df_religion.rename(columns={"Country": "name_0"}, inplace=True)
df_religion.columns = df_religion.columns.str.lower()

# Remplacement des noms de pays différents
df_religion = remplacer_noms(df=df_religion, colonne="name_0", mapping=mapping)

# Gestion des îles anglo-normandes
mask = df_religion["name_0"] == "Channel Islands"

jersey = df_religion[mask].copy()
jersey["name_0"] = "Jersey"
jersey["population"] = 103_267

guernsey = df_religion[mask].copy()
guernsey["name_0"] = "Guernsey"
guernsey["population"] = 67_334

# On reconstruit le DataFrame
df_religion = pd.concat([df_religion[~mask], jersey, guernsey], ignore_index=True)
df_religion.drop("other_religions", axis=1, inplace=True)
df_religion.rename(
    columns={
        col: f"religion_{col}"
        for col in df_religion.columns
        if col not in ["name_0", "population"]
    },
    inplace=True,
)


## 3.5 -- Table des données alimentaires ---------------------------------------


df_alimentation.loc[df_alimentation["iso3"] == "SSD", "name_0"] = "South Sudan"
df_alimentation.drop("iso3", axis=1, inplace=True)
df_alimentation = remplacer_noms(df=df_alimentation, colonne="name_0", mapping=mapping)


# 4 -- Jointures ---------------------------------------------------------------


## 4.1 -- Avec les données GDL -------------------------------------------------


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


## 4.2 -- Jointures avec le reste des table ------------------------------------


### Table de tourisme ----------------------------------------------------------


# Test de granularité
assert df_tourisme.duplicated(subset=["name_0"], keep=False).sum() == 0, df_tourisme[
    df_tourisme.duplicated(subset=["name_0"], keep=False)
]

# Jointure
gdf_1 = gdf_1.merge(right=df_tourisme, how="left", on="name_0")


### Table des données religieuses ----------------------------------------------


# Test de granularité
assert df_religion.duplicated(subset=["name_0"], keep=False).sum() == 0, df_religion[
    df_religion.duplicated(subset=["name_0"], keep=False)
]

# Jointure
gdf_1 = gdf_1.merge(right=df_religion, how="left", on="name_0")


### Table des données alimentaires ---------------------------------------------


# Test de granularité
assert (
    df_alimentation.duplicated(subset=["name_0"], keep=False).sum() == 0
), df_alimentation[df_alimentation.duplicated(subset=["name_0"], keep=False)]

# Jointure
gdf_1 = gdf_1.merge(right=df_alimentation, how="left", on="name_0")


### Table des données environnementales ----------------------------------------


# Test de granularité
assert (
    df_environnement.duplicated(subset=["name_0"], keep=False).sum() == 0
), df_environnement[df_environnement.duplicated(subset=["name_0"], keep=False)]

# Jointure
gdf_1 = gdf_1.merge(right=df_environnement, how="left", on="name_0")


## 4.3 -- Ajout du nombre de NAs -----------------------------------------------


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


# 5 -- Imputation des valeurs manquantes et normalisation ----------------------


## 5.1 -- Imputation selon les régions les plus proches ------------------------


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

    for col in colonnes_a_imputer:

        print(col)
        # Masque des lignes où la colonne est manquante
        lignes_na = df_impute[col].isna()

        def imputer_ligne(ligne):
            # On récupère les autres lignes avec une valeur non manquante
            autres = df_impute.loc[
                ~df_impute[col].isna(), [col_lat, col_long, col]
            ].copy()

            # Calcul de la distance avec la ligne courante
            autres["distance"] = autres.apply(
                lambda r: distance_haversine(
                    ligne[col_lat], ligne[col_long], r[col_lat], r[col_long]
                ),
                axis=1,
            )

            # On garde les n voisins les plus proches et on calcule la moyenne
            voisins = autres.nsmallest(n_voisins, "distance")
            return (voisins[col] / voisins["distance"]).sum() / (
                1 / voisins["distance"]
            ).sum()

        # Application de l’imputation aux lignes manquantes
        df_impute.loc[lignes_na, col] = df_impute.loc[lignes_na].apply(
            imputer_ligne, axis=1
        )

    return df_impute


### Application ----------------------------------------------------------------


gdf_1 = imputation_geo_knn(
    df=gdf_1,
    n_voisins=10,
    colonnes_exclues=colonnes_a_exclure,
)


## 5.2 -- Normalisation des colonnes -------------------------------------------


### Normalisation entre le minimum (0) et le maximum (1) -----------------------


for col in gdf_1.columns:
    if col not in colonnes_a_exclure:
        gdf_1[col] = (gdf_1[col] - gdf_1[col].min()) / (
            gdf_1[col].max() - gdf_1[col].min()
        )


### Pondération des colonnes ---------------------------------------------------


for pattern, pondération in {
    "alimentation": 2,
    "religion": 1,
    "environnement": 1.5,
}.items():
    colonnes_i = [col for col in gdf_1.columns if pattern in col.lower()]
    for col in colonnes_i:
        gdf_1[col] = pondération * gdf_1[col] / len(colonnes_i)


### Assignation du type "float" aux colonnes -----------------------------------


for col in gdf_1.select_dtypes(include="object").columns:
    if col not in ["name_0", "name_1", "name_2"]:
        gdf_1[col] = gdf_1[col].astype(float)


# 6 -- Export ------------------------------------------------------------------


exporter_fichier(
    objet=gdf_1,
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="caracteristiques_des_regions.pkl",
)
