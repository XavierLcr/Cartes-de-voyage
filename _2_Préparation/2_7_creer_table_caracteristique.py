################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/                                                              #
# 2.7 – Script de consolidation des données propres aux pays                   #
################################################################################


import os, unicodedata
import pandas as pd
import constantes
from _0_Utilitaires._0_1_Fonctions_utiles import ouvrir_fichier, exporter_fichier


# === Import des données === #


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
        constantes.direction_donnees_brutes, "GDL-Total-Yearly-Precipitation-(m)-data.csv"
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

# === Fonctions utiles === #


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
    "Bahamas, The": "Bahamas",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Brunei Darussalam": "Brunei",
    "Cape Verde": "Cabo Verde",
    "Congo, Dem. Rep.": "Democratic Republic of the Congo",
    "Congo, Rep.": "Republic of the Congo",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Ivory Coast": "Côte d'Ivoire",
    "Curacao": "Curaçao",
    "Czech Republic": "Czechia",
    "Egypt, Arab Rep.": "Egypt",
    "Eswatini": "Swaziland",
    "FInland": "Finland",
    "Gambia, The": "Gambia",
    "Hong Kong SAR, China": "Hong Kong",
    "Iran, Islamic Rep.": "Iran",
    "Korea, Dem. People's Rep.": "North Korea",
    "Korea, Rep.": "South Korea",
    "Kyrgyz Republic": "Kyrgyzstan",
    "Lao PDR": "Laos",
    "Mexico": "México",
    "Micronesia, Fed. Sts.": "Micronesia",
    "Federated States of Micronesia": "Micronesia",
    "Puerto Rico (US)": "Puerto Rico",
    "Russian Federation": "Russia",
    "Reunion": "Réunion",
    "St. Martin (French part)": "Saint-Martin",
    "Sint Maarten (Dutch part)": "Sint Maarten",
    "Sao Tome and Principe": "São Tomé and Príncipe",
    "Slovak Republic": "Slovakia",
    "St. Kitts and Nevis": "Saint Kitts and Nevis",
    "St. Lucia": "Saint Lucia",
    "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines",
    "Syrian Arab Republic": "Syria",
    # "Trinidad And Tobago": "Trinidad and Tobago",
    "Turkiye": "Turkey",
    "Turks & Caicos Islands": "Turks and Caicos Islands",
    "United States of America": "United States",
    "Venezuela, RB": "Venezuela",
    "Virgin Islands (U.S.)": "Virgin Islands, US",
    "U.S. Virgin Islands": "Virgin Islands, US",
    "Viet Nam": "Vietnam",
    "West Bank and Gaza": "Palestine",
    "Palestinian territories": "Palestine",
    "Yemen, Rep.": "Yemen",
}


# === Ajout de données géographiques === #
gdf_1["centroid"] = gdf_1["geometry"].centroid
gdf_1["superficie"] = gdf_1["geometry"].area
gdf_1["latitude"] = gdf_1["centroid"].y
gdf_1["longitude"] = gdf_1["centroid"].x
gdf_1 = gdf_1.drop(columns=["centroid"])
gdf_1 = gdf_1.drop(columns=["geometry"])


# === Nettoyage des données Global Data Lab === #


def nettoyer_GDL(df: pd.DataFrame, gdf, mapping: dict, annee: str, nom_col: str):

    df = remplacer_noms(df, "Country", mapping=mapping)
    df["Country"] = df.apply(
        lambda row: (
            row["Region"]
            if row["Region"] in (set(df["Region"].unique()) & set(gdf["name_0"].unique()))
            else row["Country"]
        ),
        axis=1,
    )
    df = df.rename(columns={"Country": "name_0", "Region": "name_1", annee: nom_col})
    df = df.loc[df[nom_col].notna(), ["name_0", "name_1", nom_col]]

    df = df.groupby(["name_0", "name_1"], as_index=False)[nom_col].mean()

    assert df.duplicated(subset=["name_0", "name_1"], keep=False).sum() == 0, df[
        df.duplicated(subset=["name_0", "name_1"], keep=False)
    ]

    return df


# Application
df_IDH = nettoyer_GDL(df=df_IDH, gdf=gdf_1, mapping=mapping, annee="2022", nom_col="IDH")
df_temperature = nettoyer_GDL(
    df=df_temperature, gdf=gdf_1, mapping=mapping, annee="2022", nom_col="temperature"
)
df_pluie = nettoyer_GDL(df=df_pluie, gdf=gdf_1, mapping=mapping, annee="2022", nom_col="pluie")
df_humidite = nettoyer_GDL(
    df=df_humidite, gdf=gdf_1, mapping=mapping, annee="2022", nom_col="humidite"
)


# === Nettoyage de la table de tourisme === #

df_tourisme = df_tourisme.loc[
    :, df_tourisme.nunique(dropna=False) > 1
]  # Suppression des colonnes constantes
df_tourisme = df_tourisme.dropna(axis=1, how="all")  # Suppression des colonnes que NA
# Valeur la plus récente
df_tourisme["tourisme"] = df_tourisme[
    [col for col in df_tourisme.columns if col.isdigit()]
].apply(
    lambda row: row[row.last_valid_index()] if row.last_valid_index() is not None else pd.NA,
    axis=1,
)
df_tourisme = df_tourisme[["Country Name", "tourisme"]]
df_tourisme.rename(columns={"Country Name": "name_0"}, inplace=True)


# === Nettoyage de la table des religions === #


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


# === Jointures === #


def normalize_string(s):
    if pd.isna(s):
        return ""
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = s.lower().replace(" ", "").replace("-", "").replace("'", "")
    return s


# Fonction pour trouver la correspondance
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


# Avec les tables GDL
gdf_1 = merge_with_match(gdf_1, df_IDH)
gdf_1 = merge_with_match(gdf_1, df_temperature)
gdf_1 = merge_with_match(gdf_1, df_pluie)
gdf_1 = merge_with_match(gdf_1, df_humidite)

# Avec la table du tourisme
assert df_tourisme.duplicated(subset=["name_0"], keep=False).sum() == 0, df_tourisme[
    df_tourisme.duplicated(subset=["name_0"], keep=False)
]
gdf_1 = gdf_1.merge(right=df_tourisme, how="left", on="name_0")
# gdf_1.loc[(gdf_1["name_0"] == "China") & (gdf_1["name_1"] == "Hong Kong"), "tourisme"] = (
#     df_tourisme.loc[df_tourisme["name_0"] == "Hong Kong", "tourisme"].iloc[0]
# )

# Avec la table des religion
assert df_religion.duplicated(subset=["name_0"], keep=False).sum() == 0, df_religion[
    df_religion.duplicated(subset=["name_0"], keep=False)
]
gdf_1 = gdf_1.merge(right=df_religion, how="left", on="name_0")


# === Export === #

exporter_fichier(
    objet=gdf_1,
    direction_fichier=constantes.direction_donnees_application,
    nom_fichier="caracteristiques_des_regions.pkl",
)
