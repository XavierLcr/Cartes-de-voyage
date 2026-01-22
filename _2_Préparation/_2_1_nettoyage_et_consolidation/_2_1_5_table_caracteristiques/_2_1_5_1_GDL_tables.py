################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation/_2_1_5_table_caracteristiques/  #
# 2.1.5.1 – Script de nettoyage des données du Global Data Lab (GDL)           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, re
import pandas as pd

import constantes
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_fichier,
    exporter_fichier,
)
from _0_Utilitaires._0_4_fonctions_utiles_nettoyage import (
    mapping_pays,
    remplacer_valeurs_colonne,
    valeurs_contenues,
)
from _0_Utilitaires._0_5_isid import isid


# 1 -- Import des données ------------------------------------------------------


## 1.1 -- Données GDL ----------------------------------------------------------


# IDH
df_IDH = pd.read_csv(
    os.path.join(constantes.direction_donnees_brutes, "GDL-Subnational-HDI-data.csv")
)

# Températures
df_temperature = pd.read_csv(
    os.path.join(
        constantes.direction_donnees_brutes,
        "GDL-Yearly-Average-Surface-Temperature-(ºC)-data.csv",
    )
)

# Pluies
df_pluie = pd.read_csv(
    os.path.join(
        constantes.direction_donnees_brutes,
        "GDL-Total-Yearly-Precipitation-(m)-data.csv",
    )
)

# Humidité
df_humidite = pd.read_csv(
    os.path.join(
        constantes.direction_donnees_brutes,
        "GDL-Yearly-Average-Relative-Humidity-(_)-data.csv",
    )
)

# Niveau d'urbanisme
df_urbanisme = pd.read_csv(
    os.path.join(
        constantes.direction_donnees_brutes,
        "GDL-_-population-in-urban-areas-data.csv",
    ),
)

# Qualité de la justice
df_justice = pd.read_csv(
    os.path.join(
        constantes.direction_donnees_brutes,
        "GDL-Comprehensive-Subnational-Corruption-Index-(SCI)-data.csv",
    ),
)


## 1.2 -- Table du GADM (Granularité 1) ----------------------------------------


gdf_1 = ouvrir_fichier(
    direction_fichier=constantes.direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_1.pkl",
    defaut=None,
    afficher_erreur="Table non trouvée...",
)[["name_0", "name_1"]]


# 2 -- Fonctions ---------------------------------------------------------------


## 2.1 -- Fonction de séparation des lignes avec des parenthèses ---------------


def eclater_parentheses(texte):
    correspondance = re.match(r"^(.*?)\s*\((.*?)\)\s*$", texte)

    # S'il n'y a pas de parenthèses, on renvoie le texte tel quel
    if not correspondance:
        return [texte]

    base = correspondance.group(1)
    contenu = correspondance.group(2).strip()

    # RÈGLE : s'il y a une virgule, on découpe uniquement sur les virgules
    if "," in contenu:
        elements = [e.strip() for e in contenu.split(",")]
    else:
        elements = contenu.split()

    return [base] + elements


## 2.2 -- Fonction de nettoyage ------------------------------------------------


def nettoyer_GDL(df: pd.DataFrame, gdf, mapping: dict, annee: str, nom_col: str):

    # Adaptation des noms de pays à ceux de la table du GADM
    df = remplacer_valeurs_colonne(df, "Country", mapping=mapping)

    # Décalage des régions qui sont des pays dans la table du GADM
    df["Country"] = df.apply(
        lambda row: (
            row["Region"]
            if row["Region"]
            in (set(df["Region"].unique()) & set(gdf["name_0"].unique()))
            else row["Country"]
        ),
        axis=1,
    )

    # Renommage
    df = df.rename(columns={"Country": "name_0", "Region": "name_1", annee: nom_col})

    # Suppression des colonnes sans valeur
    df = df.loc[df[nom_col].notna(), ["name_0", "name_1", nom_col]]

    # Séparation des régions regroupées entre parenthèses
    df["name_1"] = df["name_1"].apply(eclater_parentheses)
    df = df.explode("name_1")

    # Homogénéisation des valeurs si nécessaire (conservation de la moyenne si doublons)
    df = df.groupby(["name_0", "name_1"], as_index=False)[nom_col].mean()

    # Pays non traduits
    pays_hors_gdf = valeurs_contenues(df1=df, col1="name_0", df2=gdf, col2="name_0")
    if len(pays_hors_gdf) > 0:
        print(pays_hors_gdf)

    # Test de granularité
    assert isid(df=df, colonnes=["name_0", "name_1"], blabla=1)

    # Renvoi
    return df


# 3 -- Application et export  --------------------------------------------------


## 3.1 -- IDH ------------------------------------------------------------------


df_IDH = nettoyer_GDL(
    df=df_IDH, gdf=gdf_1, mapping=mapping_pays, annee="2022", nom_col="IDH"
)

exporter_fichier(
    objet=df_IDH,
    direction_fichier=constantes.direction_donnees_intermediaires,
    nom_fichier="IDH.pkl",
)


## 3.2 -- Températures ---------------------------------------------------------


df_temperature = nettoyer_GDL(
    df=df_temperature,
    gdf=gdf_1,
    mapping=mapping_pays,
    annee="2022",
    nom_col="temperature",
)

exporter_fichier(
    objet=df_temperature,
    direction_fichier=constantes.direction_donnees_intermediaires,
    nom_fichier="temperature.pkl",
)

## 3.3 -- Pluies ---------------------------------------------------------------


df_pluie = nettoyer_GDL(
    df=df_pluie, gdf=gdf_1, mapping=mapping_pays, annee="2022", nom_col="pluie"
)

exporter_fichier(
    objet=df_pluie,
    direction_fichier=constantes.direction_donnees_intermediaires,
    nom_fichier="pluie.pkl",
)


## 3.4 -- Humidité -------------------------------------------------------------


df_humidite = nettoyer_GDL(
    df=df_humidite, gdf=gdf_1, mapping=mapping_pays, annee="2022", nom_col="humidite"
)

exporter_fichier(
    objet=df_humidite,
    direction_fichier=constantes.direction_donnees_intermediaires,
    nom_fichier="humidite.pkl",
)


## 3.5 -- Urbanisme ------------------------------------------------------------


df_urbanisme["recent"] = df_urbanisme[
    [col for col in df_urbanisme.columns if col.isdigit()]
].apply(
    lambda row: (
        row[row.last_valid_index()] if row.last_valid_index() is not None else pd.NA
    ),
    axis=1,
)

df_urbanisme = nettoyer_GDL(
    df=df_urbanisme,
    gdf=gdf_1,
    mapping=mapping_pays,
    annee="recent",
    nom_col="urbanisation",
)

exporter_fichier(
    objet=df_urbanisme,
    direction_fichier=constantes.direction_donnees_intermediaires,
    nom_fichier="urbanisme.pkl",
)


## 3.6 -- Justice --------------------------------------------------------------


df_justice = nettoyer_GDL(
    df=df_justice, gdf=gdf_1, mapping=mapping_pays, annee="2022", nom_col="corruption"
)

exporter_fichier(
    objet=df_justice,
    direction_fichier=constantes.direction_donnees_intermediaires,
    nom_fichier="justice.pkl",
)
