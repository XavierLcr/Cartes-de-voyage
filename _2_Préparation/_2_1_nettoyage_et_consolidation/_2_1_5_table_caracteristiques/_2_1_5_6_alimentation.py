################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_1_nettoyage_et_considation/_2_1_5_table_caracteristiques/  #
# 2.1.5.6 – Script de nettoyage des données d'alimentation                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os
import pandas as pd

from constantes import (
    direction_donnees_intermediaires,
    direction_donnees_brutes,
    direction_donnees_geographiques,
)
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


### Table du GADM (granularité 1) ----------------------------------------------


gdf_1 = ouvrir_fichier(
    direction_fichier=direction_donnees_geographiques,
    nom_fichier="carte_monde_niveau_1.pkl",
    defaut=None,
    afficher_erreur="Table non trouvée...",
)[["name_0", "name_1"]]


### Référenciel ----------------------------------------------------------------


ref_alim = pd.read_excel(
    os.path.join(
        direction_donnees_brutes, "Alimentation", "GDD 2018 Codebook_Jan 10 2022.xlsx"
    ),
    sheet_name="File nomenclature",
    skiprows=1,
)


ref_pays = pd.read_excel(
    os.path.join(
        direction_donnees_brutes,
        "Alimentation",
        "GDD 2018 Codebook_Jan 10 2022.xlsx",
    ),
    sheet_name="Stratum-level characteristics",
    skiprows=1,
)


# 2 -- Fonctions ---------------------------------------------------------------


## 2.1 -- Fonction générique ---------------------------------------------------


def ouvrir_gdd(direction, nom_fichier, suffixe: str = ""):

    df_temp = pd.read_csv(os.path.join(direction, nom_fichier))
    df_temp = df_temp[
        (df_temp["year"] == 2018)
        & (df_temp["edu"] == 999)
        & (df_temp["age"] == 999)
        & (df_temp["female"] == 999)
        & (df_temp["urban"] == 999)
    ]

    # Mise en forme des noms de colonnes
    if suffixe:
        suffixe = f"_{suffixe}"
    nouveau_nom = f"alimentation{suffixe}"
    df_temp = df_temp.rename(columns={"median": nouveau_nom})

    # Test de granularité
    assert df_temp.duplicated(subset=["iso3"], keep=False).sum() == 0, df_temp[
        df_temp.duplicated(subset=["iso3"], keep=False)
    ]

    return df_temp[["iso3", nouveau_nom]]


## 2.2 -- Consolidation des tables ---------------------------------------------


def joindre_gdd(chemin: str, nums: list | None, correspondances_code: dict = {}):

    csv_alimentation = [f for f in os.listdir(chemin) if f.endswith(".csv")]

    if nums is not None:
        csv_alimentation = [
            f for f in csv_alimentation if any(num in f for num in nums)
        ]

    for i in range(len(csv_alimentation)):

        nom_i = csv_alimentation[i]
        print(nom_i)

        df_temp = ouvrir_gdd(
            direction=chemin,
            nom_fichier=nom_i,
            suffixe=correspondances_code.get(nom_i[0:3], ""),
        )

        if i == 0:
            df_res = df_temp.copy()

        else:

            df_res = df_res.merge(
                right=df_temp,
                how="outer",
                on="iso3",
                suffixes=("", f"_{nom_i}"),
            )

    return df_res


# 3 -- Nettoyage des données ---------------------------------------------------


## 3.1 -- Référentiel des codes alimentaires -----------------------------------


ref_alim.columns = ref_alim.columns.str.lower().str.strip().str.replace(" ", "_")
ref_alim = ref_alim[["numeric_code", "gdd_variable_label"]]
ref_alim["gdd_variable_label"] = (
    ref_alim["gdd_variable_label"]
    .str.lower()
    .str.strip()
    .str.replace(" ", "_")
    .str.replace("-", "_")
    .str.replace(r"\(.*", "")
)

# Tests de granularité
assert isid(df=ref_alim, colonnes="numeric_code", blabla=0)
assert isid(df=ref_alim, colonnes="gdd_variable_label", blabla=0)

# Transformation en dictionnaire
ref_alim = ref_alim.set_index("numeric_code")["gdd_variable_label"].to_dict()


## 3.2 -- Nettoyage du référentiel des pays ------------------------------------


ref_pays.columns = ref_pays.columns.str.lower().str.strip().str.replace(" ", "_")
ref_pays.rename(columns={"label": "name_0", "code": "iso3"}, inplace=True)
ref_pays = ref_pays[["name_0", "iso3"]]


# Tests de granularité
assert isid(df=ref_pays, colonnes="name_0", blabla=0)
assert isid(df=ref_pays, colonnes="iso3", blabla=0)


## 3.3 -- Nettoyage de la table alimentaire ------------------------------------


df_alim = joindre_gdd(
    chemin=os.path.join(
        direction_donnees_brutes,
        "Alimentation",
    ),
    nums=None,
    correspondances_code=ref_alim,
)

# Test de granularité
assert isid(df=df_alim, colonnes="iso3", blabla=0)


## 3.4 -- Consolidation --------------------------------------------------------


df_final = ref_pays.merge(right=df_alim, on="iso3", how="outer")

df_final.loc[df_final["iso3"] == "SSD", "name_0"] = "South Sudan"
df_final.drop("iso3", axis=1, inplace=True)
df_final = remplacer_valeurs_colonne(
    df=df_final, colonne="name_0", mapping=mapping_pays
)

# Test
assert (
    len(valeurs_contenues(df1=df_final, col1="name_0", df2=gdf_1, col2="name_0")) == 0
)


# 4 -- Export ------------------------------------------------------------------


# Test de granularité
assert isid(df=df_final, colonnes="name_0", blabla=0)

exporter_fichier(
    objet=df_final,
    direction_fichier=direction_donnees_intermediaires,
    nom_fichier="alimentation.pkl",
    sort_keys=True,
)
