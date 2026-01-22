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
    derniere_valeur_valide_par_ligne,
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


# 3 -- Application -------------------------------------------------------------


## 3.1 -- IDH ------------------------------------------------------------------


df_IDH = nettoyer_GDL(
    df=df_IDH, gdf=gdf_1, mapping=mapping_pays, annee="2022", nom_col="IDH"
)


## 3.2 -- Températures ---------------------------------------------------------


df_temperature = nettoyer_GDL(
    df=df_temperature,
    gdf=gdf_1,
    mapping=mapping_pays,
    annee="2022",
    nom_col="temperature",
)

## 3.3 -- Pluies ---------------------------------------------------------------


df_pluie = nettoyer_GDL(
    df=df_pluie, gdf=gdf_1, mapping=mapping_pays, annee="2022", nom_col="pluie"
)


## 3.4 -- Humidité -------------------------------------------------------------


df_humidite = nettoyer_GDL(
    df=df_humidite, gdf=gdf_1, mapping=mapping_pays, annee="2022", nom_col="humidite"
)


## 3.5 -- Urbanisme ------------------------------------------------------------


df_urbanisme = df_urbanisme.assign(
    recent=lambda df: derniere_valeur_valide_par_ligne(df=df)
).pipe(
    nettoyer_GDL,
    gdf=gdf_1,
    mapping=mapping_pays,
    annee="recent",
    nom_col="urbanisation",
)


## 3.6 -- Justice --------------------------------------------------------------


df_justice = nettoyer_GDL(
    df=df_justice, gdf=gdf_1, mapping=mapping_pays, annee="2022", nom_col="corruption"
)


# 4 -- Jointures des différentes tables ----------------------------------------


# Tests de granularité
assert isid(df=df_IDH, colonnes=["name_0", "name_1"], blabla=1)
assert isid(df=df_temperature, colonnes=["name_0", "name_1"], blabla=1)
assert isid(df=df_pluie, colonnes=["name_0", "name_1"], blabla=1)
assert isid(df=df_humidite, colonnes=["name_0", "name_1"], blabla=1)
assert isid(df=df_urbanisme, colonnes=["name_0", "name_1"], blabla=1)
assert isid(df=df_justice, colonnes=["name_0", "name_1"], blabla=1)

# Jointures
df_gdl = (
    df_IDH.merge(right=df_temperature, on=["name_0", "name_1"], how="outer")
    .merge(right=df_pluie, on=["name_0", "name_1"], how="outer")
    .merge(right=df_humidite, on=["name_0", "name_1"], how="outer")
    .merge(right=df_urbanisme, on=["name_0", "name_1"], how="outer")
    .merge(right=df_justice, on=["name_0", "name_1"], how="outer")
)


# 5 -- Séparation des tables nationale et locale -------------------------------


df_gdl_nat = df_gdl[df_gdl["name_1"] == "Total"].drop(columns="name_1")
df_gdl_reg = df_gdl[df_gdl["name_1"] != "Total"]


# Test de longueur
assert len(df_gdl_nat) + len(df_gdl_reg) == len(df_gdl)


# 6 -- Export ------------------------------------------------------------------


## 6.1 -- Table nationale ------------------------------------------------------


# Test de granularité
assert isid(df=df_gdl_nat, colonnes=["name_0"], blabla=1)

# Export
exporter_fichier(
    objet=df_gdl_nat,
    direction_fichier=constantes.direction_donnees_intermediaires,
    nom_fichier="gdl_nationale.pkl",
)


## 6.2 -- Table régionale ------------------------------------------------------


# Test de granularité
assert isid(df=df_gdl_reg, colonnes=["name_0", "name_1"], blabla=1)

# Export
exporter_fichier(
    objet=df_gdl_reg,
    direction_fichier=constantes.direction_donnees_intermediaires,
    nom_fichier="gdl_regionale.pkl",
)
