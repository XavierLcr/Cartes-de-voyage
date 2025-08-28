import os, pickle
import pandas as pd
import geopandas as gpd
from constantes import direction_donnees, direction_donnees_geographiques
from _0_Utilitaires._0_1_Fonctions_utiles import ouvrir_fichier, exporter_fichier

gdf = gpd.read_file(os.path.join(direction_donnees, "_1_1_Données_brutes", "gadm_410.gpkg"))[
    # Sélection de colonnes
    ["CONTINENT", "NAME_0", "NAME_1", "NAME_2", "NAME_3", "NAME_4", "NAME_5", "geometry"]
]

# === Remplacement de valeurs manquantes ===


# Allemagne
print("Allemagne", end=" ; ")
mask = (
    (gdf["NAME_0"] == "Germany")
    & (gdf[f"NAME_3"].str.contains("\(", na=False))
    & (gdf[f"NAME_3"].str.contains("\)", na=False) == False)
)
gdf.loc[mask, "NAME_3"] = gdf.loc[mask, "NAME_3"].str.replace(r"\(.*", "", regex=True)

gdf.loc[(gdf["NAME_0"] == "Germany") & (gdf["NAME_3"] == "Sch�ningen"), "NAME_3"] = (
    "Schöningen"
)

# Valeurs �
mask = (gdf["NAME_0"] == "Germany") & (gdf["NAME_1"] == "Bayern")
gdf.loc[mask, "NAME_3"] = gdf.loc[mask, "NAME_3"].map(
    lambda x: {
        "Bad K�nigshofen i. Grabfeld": "Bad Königshofen i. Grabfeld",
        "H�chstadt a.d. Aisch": "Höchstadt a.d. Aisch",
        "Gem�nden a. Main": "Gemünden a. Main",
        "Bad Br�ckenau": "Bad Brückenau",
        "Eichst�tt": "Eichstätt",
    }.get(x, x)
)


# Algérie
print("Algérie", end=" ; ")
gdf.loc[
    (gdf["NAME_0"] == "Algeria") & (gdf["NAME_1"] == "Biskra") & (gdf["NAME_2"] == "M_Ziraa"),
    "NAME_2",
] = "El Mizaraa"

# Autriche
print("Autriche", end=" ; ")
mask = (
    (gdf["NAME_0"] == "Austria")
    & (gdf["NAME_2"] == "Ried im Innkreis")
    & (gdf["NAME_3"] == "Sankt Martin im Innkreis")
)
gdf.loc[mask, "NAME_4"] = gdf.loc[mask, "NAME_4"].str.strip("*")

mask = gdf["NAME_3"].str.contains(r"Sankt Georgen bei Obernberg am \*$", na=False)
gdf.loc[mask, "NAME_4"] = gdf.loc[mask, "NAME_4"].str.replace(r"\*$", "Inn", regex=True)
gdf.loc[mask, "NAME_3"] = gdf.loc[mask, "NAME_3"].str.replace(r"\*$", "Inn", regex=True)

mask = gdf["NAME_3"].str.contains(r"Sankt Marienkirchen an der Pols*", na=False)
gdf.loc[mask, "NAME_4"] = gdf.loc[mask, "NAME_4"].str.replace("Pols*", "Polsenz", regex=False)
gdf.loc[mask, "NAME_3"] = gdf.loc[mask, "NAME_3"].str.replace("Pols*", "Polsenz", regex=False)

gdf.loc[
    (gdf["NAME_0"] == "Austria") & (gdf["NAME_4"] == "Nonndorf bei Raabs an der Tha*"),
    "NAME_4",
] = "Nondorf oder Nonndorf bei Raabs an der Thaya"

# Bénin
print("Bénin", end=" ; ")
gdf.loc[gdf["NAME_0"] == "Benin", "NAME_3"] = gdf.loc[
    gdf["NAME_0"] == "Benin", "NAME_3"
].str.replace("?", "é", regex=False)
gdf.loc[
    (gdf["NAME_0"] == "Benin")
    & (gdf["NAME_1"] == "Alibori")
    & (gdf["NAME_3"] == "Kokiborou*"),
    "NAME_3",
] = "Kokiborou"

# Burundi
print("Burundi", end=" ; ")
mask = (gdf["NAME_0"] == "Burundi") & (gdf["NAME_2"] == "Muyinga")
gdf.loc[mask, "NAME_3"] = gdf.loc[mask, "NAME_3"].str.replace("_", " ", regex=False)

# Croatie
print("Croatie", end=" ; ")
mask = (
    (gdf["NAME_0"] == "Croatia")
    & (gdf["NAME_1"] == "Brodsko-Posavska")
    & (gdf["NAME_2"] == "Unknown_1")
)
gdf.loc[mask, "NAME_2"] = "Bukovlje"

mask = (gdf["NAME_0"] == "Croatia") & (gdf["NAME_1"] == "Osjecko-Baranjska")
gdf.loc[mask & (gdf["NAME_2"].isin(["Osjecko-Baranjska", "Unknown_2"])), "NAME_2"] = (
    "Šodolovci"
)
gdf.loc[mask & (gdf["NAME_2"].isin(["Unknown_1"])), "NAME_2"] = (
    "Unknown municipality 1 (Osjecko-Baranjska)"
)
gdf.loc[mask & (gdf["NAME_2"].isin(["Unknown_3"])), "NAME_2"] = (
    "Unknown municipality 2 (Osjecko-Baranjska)"
)

# Canada
print("Canada", end=" ; ")
gdf.loc[
    (gdf["NAME_0"] == "Canada")
    & (gdf["NAME_1"] == "Manitoba")
    & (gdf["NAME_3"] == "Division ?"),
    "NAME_3",
] = "Finger"
gdf.loc[gdf["NAME_0"] == "Canada", "NAME_3"] = gdf.loc[
    gdf["NAME_0"] == "Canada", "NAME_3"
].str.replace("?", "Î", regex=False)

# Corée du Sud
print("Corée du Sud", end=" ; ")
mask = (gdf["NAME_1"] == "Gyeongsangnam-do") & (gdf["NAME_2"] == "Jinju")
gdf.loc[mask, "NAME_3"] = (
    gdf.loc[mask, "NAME_3"]
    .str.replace("_", " ", regex=False)  # supprime/transforme les underscores
    .str.title()  # met une majuscule à chaque mot
)

# France
print("France", end=" ; ")
mask = (
    (gdf["NAME_0"] == "France")
    & (gdf[f"NAME_5"].str.contains("\(", na=False))
    & (gdf[f"NAME_5"].str.contains("\)", na=False) == False)
)
gdf.loc[mask, "NAME_5"] = gdf.loc[mask, "NAME_5"].str.replace(r"\(.*", "", regex=True)


# Guatemala
print("Guatemala", end=" ; ")
gdf.loc[
    (gdf["NAME_0"] == "Guatemala") & (gdf["NAME_1"] == "Sololá") & (gdf["NAME_2"] == "?"),
    "NAME_2",
] = "Lake Atitlán"
gdf.loc[
    (gdf["NAME_0"] == "Guatemala") & (gdf["NAME_1"] == "Izabal") & (gdf["NAME_2"] == "?"),
    "NAME_2",
] = "Lake Izabal"

# Guyana
print("Guyana", end=" ; ")
mask = (
    (gdf["NAME_0"] == "Guyana")
    & (gdf[f"NAME_2"].str.contains("\(", na=False))
    & (gdf[f"NAME_2"].str.contains("\)", na=False) == False)
)
gdf.loc[mask, "NAME_2"] = gdf.loc[mask, "NAME_2"].str.replace(r"\(.*", "", regex=True)

# Iran
print("Iran", end=" ; ")
mask = (
    (gdf["NAME_0"] == "Iran")
    & (gdf["NAME_1"] == "Razavi Khorasan")
    & (gdf["NAME_2"] == "Chenaran")
)
gdf.loc[mask, "NAME_2"] = "Golbahar & Torqabeh and Shandiz"
for i in range(1, 4):
    mask = (gdf["NAME_0"] == "Iran") & (gdf["NAME_2"] == f"n.a. (0{i})")
    gdf.loc[mask, "NAME_2"] = {
        "1": "Salas-e Babajani",
        "2": "Boshruyeh, Eshqabad & Ferdows",
        "3": "Chenaran",
    }.get(f"{i}", f"n.a. (0{i})")

# Kenya
print("Kenya", end=" ; ")
mask = (
    (gdf["NAME_0"] == "Kenya") & (gdf["NAME_1"] == "Homa Bay") & (gdf["NAME_2"] == "unknown 6")
)
gdf.loc[mask, ["NAME_2", "NAME_3"]] = ["Karachuonyo", "Unknown (Karachuonyo)"]
mask = (
    (gdf["NAME_0"] == "Kenya") & (gdf["NAME_1"] == "Machakos") & (gdf["NAME_2"] == "unknown 7")
)
gdf.loc[mask, ["NAME_2", "NAME_3"]] = ["Kalama"] * 2
mask = (
    (gdf["NAME_0"] == "Kenya") & (gdf["NAME_1"] == "Mandera") & (gdf["NAME_2"] == "unknown 1")
)
gdf.loc[mask, ["NAME_2", "NAME_3"]] = ["Shimbir Fatuma & Fincharo"] * 2

# Liberia
mask = gdf["NAME_0"] == "Liberia"
gdf.loc[mask, "NAME_2"] = gdf.loc[mask, "NAME_2"].str.replace("#", "", regex=False)

# Népal
print("Népal", end=" ; ")
gdf.loc[
    (gdf["NAME_0"] == "Nepal")
    & (gdf["NAME_3"] == "Bara")
    & (gdf["NAME_4"].str.contains("n\.a\.", na=False))
    & (gdf["NAME_4"].str.contains("1", na=False)),
    "NAME_4",
] = "Kakadi (2)"

gdf.loc[
    (gdf["NAME_0"] == "Nepal")
    & (gdf["NAME_3"] == "Bara")
    & (gdf["NAME_4"].str.contains("n\.a\.", na=False))
    & (gdf["NAME_4"].str.contains("2", na=False)),
    "NAME_4",
] = "Rampurwa (2)"

# Ouganda
print("Ouganda", end=" ; ")
gdf.loc[
    (gdf["NAME_0"] == "Uganda")
    & (gdf["NAME_1"] == "Masindi")
    & (gdf["NAME_2"] == "Bujenje (?)"),
    "NAME_2",
] = "Buliisa"

# Rwanda
print("Rwanda", end=" ; ")
gdf.loc[
    (gdf["NAME_0"] == "Rwanda")
    & (gdf["NAME_1"] == "Iburengerazuba")
    & (gdf["NAME_2"] == "Rubavu")
    & (gdf["NAME_3"] == "Bugeshi")
    & (gdf["NAME_4"] == "Hehu")
    & (gdf["NAME_5"] == "?"),
    "NAME_5",
] = "Ngando"

# Soudan et Soudan du Sud
print("Soudan et Soudan du Sud", end=" ; ")
mask = gdf["NAME_0"].str.contains("Sudan", regex=False) & gdf["NAME_3"].str.contains(
    "_", regex=False
)
gdf.loc[mask, "NAME_3"] = gdf.loc[mask, "NAME_2"]

# Tonga
print("Tonga", end=" ; ")
mask = gdf["NAME_0"] == "Tonga"
gdf.loc[mask, "NAME_2"] = gdf.loc[mask, "NAME_2"].str.replace(pat="n.a.", repl="", regex=False)

# Tunisie
print("Tunisie", end=" ; ")
mask = (
    (gdf["NAME_0"] == "Tunisia")
    & (gdf["NAME_1"].isin(["Monastir"]))
    & (gdf["NAME_2"].isin(["Unknown1"]))
)
gdf.loc[mask, "NAME_2"] = "Kuriat Islands"
mask = (
    (gdf["NAME_0"] == "Tunisia")
    & (gdf["NAME_1"].isin(["Tunis"]))
    & (gdf["NAME_2"].isin(["Unknown"]))
)
gdf.loc[mask, "NAME_2"] = "Unknown 1 (Tunis)"

# Ukraine
print("Ukraine", end=".\n")
gdf.loc[(gdf["NAME_0"] == "Ukraine") & (gdf["NAME_1"] == "?"), ["NAME_1", "NAME_2"]] = [
    "Kiev City",
    "Darnytskyi",
]


print("Nettoyage général.")
for i in range(6):

    # Ajout d'une parenthèse pour les cas restants
    mask_i = (gdf[f"NAME_{i}"].str.contains("\(", na=False)) & (
        gdf[f"NAME_{i}"].str.contains("\)", na=False) == False
    )
    gdf.loc[mask, f"NAME_{i}"] = gdf.loc[mask, f"NAME_{i}"] + ")"

    print("Nettoyage général")
    # Nettoyage des espaces
    gdf[f"NAME_{i}"] = (
        gdf[f"NAME_{i}"]
        # Suppression des + et & inutiles
        .str.strip("+&")
        # Remplacement des espaces non classiques
        .str.replace(r"[\u200B\u200C\u200D\uFEFF]", "", regex=True)
        # Remplacement des + et | par &
        .str.replace("+", " & ", regex=False)
        .str.replace("|", " & ", regex=False)
        # Suppression des crochets (et ce qu'il y a dedans - ne concerne que le Laos et la Chine)
        .str.replace(r"[\[.*]", "", regex=True)
        .str.replace(r"[\]]", "", regex=True)
        # Suppression des espaces blancs multiples
        .str.replace(r"\s+", " ", regex=True)
        # Nettoyage des extrêmités
        .str.strip()
    )

print("Remplacement des valeurs ''.")
for i in range(0, 5):
    mask = gdf[f"NAME_{i+1}"] == ""
    gdf.loc[mask, f"NAME_{i+1}"] = gdf.loc[mask, f"NAME_{i}"]

print("Concaténation des valeurs dupliquées.")


def concatener_noms_si_dupliques(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pour chaque colonne NAME_i (en partant de NAME_n vers NAME_1), concatène les valeurs
    des colonnes NAME_0 à NAME_i si le couple (NAME_0, NAME_i) apparaît plusieurs fois.

    Paramètres :
    - df (pd.DataFrame) : Le DataFrame à traiter.

    Retour :
    - pd.DataFrame : Le DataFrame modifié.
    """

    # Identifier toutes les colonnes NAME_i et les trier selon l'indice croissant
    colonnes = sorted([col for col in gdf.columns if col.startswith("NAME_")])

    for i in range(len(colonnes) - 1, 1, -1):

        # Conservation des doublons qui ont une hiérarchie différente
        mask = (df.duplicated(subset=["NAME_0", f"NAME_{i}"], keep=False)) & (
            ~df.duplicated(subset=[f"NAME_{j}" for j in range(0, i + 1)], keep=False)
        )

        for k in range(i - 1, 0, -1):
            df.loc[mask, f"NAME_{i}"] = (
                df.loc[mask, f"NAME_{k}"] + " – " + df.loc[mask, f"NAME_{i}"]
            )

    return df


# === Tests ===


print("Tests...")
for i in range(6):

    # Aucun "?"
    assert (
        len(gdf[gdf[f"NAME_{i}"].str.contains("\?", na=False)]) == 0
    ), f"Il y a des '?' dans la colonne NAME_{i}"

    # Aucun "_"
    assert (
        len(gdf[gdf[f"NAME_{i}"].str.contains("_", na=False)]) == 0
    ), f"Il y a des '?' dans la colonne NAME_{i}"

    # Aucun
    assert (
        len(gdf[gdf[f"NAME_{i}"].str.contains("\ufffd", na=False)]) == 0
    ), f"Il y a des '�' dans la colonne NAME_{i}"

    # Aucun "*"
    if i != 3:
        assert (
            len(gdf[gdf[f"NAME_{i}"].str.contains("\*", na=False)]) == 0
        ), f"Il y a des '*' dans la colonne NAME_{i}"


# Export
with open(direction_donnees + "\\geodataframe_reduit.pkl", "wb") as f:
    pickle.dump(gdf, f)

# === Création des tables à une granularité plus faible ===

# Niveau 4
with open(direction_donnees + "\\carte_monde_niveau_4.pkl", "wb") as f:
    pickle.dump(
        gdf.dissolve(
            by=["NAME_0", "NAME_1", "NAME_2", "NAME_3", "NAME_4"],
            aggfunc={
                "NAME_0": "first",
                "NAME_1": "first",
                "NAME_2": "first",
                "NAME_3": "first",
                "NAME_4": "first",
            },
        ),
        f,
    )

# Niveau 3
with open(direction_donnees + "\\carte_monde_niveau_3.pkl", "wb") as f:
    pickle.dump(
        gdf.dissolve(
            by=["NAME_0", "NAME_1", "NAME_2", "NAME_3"],
            aggfunc={
                "NAME_0": "first",
                "NAME_1": "first",
                "NAME_2": "first",
                "NAME_3": "first",
            },
        ),
        f,
    )

# Niveau 2
with open(direction_donnees + "\\carte_monde_niveau_2.pkl", "wb") as f:
    pickle.dump(
        gdf.dissolve(
            by=["NAME_0", "NAME_1", "NAME_2"],
            aggfunc={
                "NAME_0": "first",
                "NAME_1": "first",
                "NAME_2": "first",
            },
        ),
        f,
    )

# Niveau 1
with open(direction_donnees + "\\carte_monde_niveau_1.pkl", "wb") as f:
    pickle.dump(
        gdf.dissolve(
            by=["NAME_0", "NAME_1"],
            aggfunc={
                "NAME_0": "first",
                "NAME_1": "first",
            },
        ),
        f,
    )

# Niveau 0
with open(direction_donnees + "\\carte_monde_niveau_0.pkl", "wb") as f:
    pickle.dump(
        gdf.dissolve(
            by=["NAME_0"],
            aggfunc={
                "NAME_0": "first",
            },
        ),
        f,
    )


def concatener_noms_si_dupliques(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pour chaque colonne NAME_i (en partant de NAME_n vers NAME_1), concatène les valeurs
    des colonnes NAME_0 à NAME_i si le couple (NAME_0, NAME_i) apparaît plusieurs fois.

    Paramètres :
    - df (pd.DataFrame) : Le DataFrame à traiter.

    Retour :
    - pd.DataFrame : Le DataFrame modifié.
    """

    # Identifier toutes les colonnes NAME_i et les trier selon l'indice croissant
    colonnes = sorted(
        [col for col in df.columns if col.startswith("NAME_")],
        key=lambda x: int(x.split("_")[1]),
    )

    # Récursivement, on part de NAME_n vers NAME_1 (on ne touche pas à NAME_0)
    for i in range(len(colonnes) - 1, 0, -1):
        col_courante = colonnes[i]
        # Vérifier les doublons (NAME_0, NAME_i)
        doublons = df.duplicated(subset=["NAME_0", col_courante], keep=False)

        # Colonnes à concaténer : NAME_0 à NAME_i
        colonnes_a_concat = colonnes[: i + 1]

        # Fonction de concaténation
        def concat_ligne(ligne):
            return "-".join(
                str(ligne[col]) for col in colonnes_a_concat if pd.notnull(ligne[col])
            ).strip("- ")

        # Appliquer la concaténation sur les doublons
        df.loc[doublons, col_courante] = df.loc[doublons, colonnes_a_concat].apply(
            concat_ligne, axis=1
        )

    return df


for i in range(2, 6):
    print(f"Granularité : {i}", end=". ")

    with open(
        os.path.join(
            direction_donnees_geographiques,
            "_1_2_Données_géographiques",
            f"carte_monde_niveau_{i}.pkl",
        ),
        "wb",
    ) as f:
        pickle.dump(
            concatener_noms_si_dupliques(
                ouvrir_fichier(
                    direction_fichier=direction_donnees_geographiques,
                    nom_fichier=f"carte_monde_niveau_{i}.pkl",
                    defaut=None,
                )
            ),
            f,
        )

    print("Terminé.")
