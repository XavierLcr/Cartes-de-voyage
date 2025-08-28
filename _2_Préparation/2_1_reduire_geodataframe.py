import os, pickle
import pandas as pd
import geopandas as gpd
from constantes import direction_donnees, direction_donnees_geographiques
from _0_Utilitaires._0_1_Fonctions_utiles import ouvrir_fichier, exporter_fichier

gdf = gpd.read_file(os.path.join(direction_donnees, "_1_1_Données_brutes", "gadm_410.gpkg"))[
    # Sélection de colonnes
    ["NAME_0", "NAME_1", "NAME_2", "NAME_3", "NAME_4", "NAME_5", "geometry"]
]
gdf.columns = gdf.columns.str.lower()

# === Remplacement de valeurs manquantes ===


# Allemagne
print("Allemagne", end=" ; ")
mask = (
    (gdf["name_0"] == "Germany")
    & (gdf[f"name_3"].str.contains("\(", na=False))
    & (gdf[f"name_3"].str.contains("\)", na=False) == False)
)
gdf.loc[mask, "name_3"] = gdf.loc[mask, "name_3"].str.replace(r"\(.*", "", regex=True)

gdf.loc[(gdf["name_0"] == "Germany") & (gdf["name_3"] == "Sch�ningen"), "name_3"] = (
    "Schöningen"
)

# Valeurs �
mask = (gdf["name_0"] == "Germany") & (gdf["name_1"] == "Bayern")
gdf.loc[mask, "name_3"] = gdf.loc[mask, "name_3"].map(
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
    (gdf["name_0"] == "Algeria") & (gdf["name_1"] == "Biskra") & (gdf["name_2"] == "M_Ziraa"),
    "name_2",
] = "El Mizaraa"

# Autriche
print("Autriche", end=" ; ")
mask = (
    (gdf["name_0"] == "Austria")
    & (gdf["name_2"] == "Ried im Innkreis")
    & (gdf["name_3"] == "Sankt Martin im Innkreis")
)
gdf.loc[mask, "name_4"] = gdf.loc[mask, "name_4"].str.strip("*")

mask = gdf["name_3"].str.contains(r"Sankt Georgen bei Obernberg am \*$", na=False)
gdf.loc[mask, "name_4"] = gdf.loc[mask, "name_4"].str.replace(r"\*$", "Inn", regex=True)
gdf.loc[mask, "name_3"] = gdf.loc[mask, "name_3"].str.replace(r"\*$", "Inn", regex=True)

mask = gdf["name_3"].str.contains(r"Sankt Marienkirchen an der Pols*", na=False)
gdf.loc[mask, "name_4"] = gdf.loc[mask, "name_4"].str.replace("Pols*", "Polsenz", regex=False)
gdf.loc[mask, "name_3"] = gdf.loc[mask, "name_3"].str.replace("Pols*", "Polsenz", regex=False)

gdf.loc[
    (gdf["name_0"] == "Austria") & (gdf["name_4"] == "Nonndorf bei Raabs an der Tha*"),
    "name_4",
] = "Nondorf oder Nonndorf bei Raabs an der Thaya"

# Bénin
print("Bénin", end=" ; ")
gdf.loc[gdf["name_0"] == "Benin", "name_3"] = gdf.loc[
    gdf["name_0"] == "Benin", "name_3"
].str.replace("?", "é", regex=False)
gdf.loc[
    (gdf["name_0"] == "Benin")
    & (gdf["name_1"] == "Alibori")
    & (gdf["name_3"] == "Kokiborou*"),
    "name_3",
] = "Kokiborou"

# Burundi
print("Burundi", end=" ; ")
mask = (gdf["name_0"] == "Burundi") & (gdf["name_2"] == "Muyinga")
gdf.loc[mask, "name_3"] = gdf.loc[mask, "name_3"].str.replace("_", " ", regex=False)

# Croatie
print("Croatie", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Croatia")
    & (gdf["name_1"] == "Brodsko-Posavska")
    & (gdf["name_2"] == "Unknown_1"),
    "name_2",
] = "Bukovlje"

mask = (gdf["name_0"] == "Croatia") & (gdf["name_1"] == "Osjecko-Baranjska")
gdf.loc[mask & (gdf["name_2"].isin(["Osjecko-Baranjska", "Unknown_2"])), "name_2"] = (
    "Šodolovci"
)
gdf.loc[mask & (gdf["name_2"].isin(["Unknown_1"])), "name_2"] = "Unknown 1 (Osjecko-Baranjska)"
gdf.loc[mask & (gdf["name_2"].isin(["Unknown_3"])), "name_2"] = "Unknown 2 (Osjecko-Baranjska)"

# Canada
print("Canada", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Canada")
    & (gdf["name_1"] == "Manitoba")
    & (gdf["name_3"] == "Division ?"),
    "name_3",
] = "Finger"
gdf.loc[gdf["name_0"] == "Canada", "name_3"] = gdf.loc[
    gdf["name_0"] == "Canada", "name_3"
].str.replace("?", "Î", regex=False)

# Corée du Sud
print("Corée du Sud", end=" ; ")
mask = (gdf["name_1"] == "Gyeongsangnam-do") & (gdf["name_2"] == "Jinju")
gdf.loc[mask, "name_3"] = (
    gdf.loc[mask, "name_3"]
    .str.replace("_", " ", regex=False)  # supprime/transforme les underscores
    .str.title()  # met une majuscule à chaque mot
)

# France
print("France", end=" ; ")
mask = (
    (gdf["name_0"] == "France")
    & (gdf[f"name_5"].str.contains("\(", na=False))
    & (gdf[f"name_5"].str.contains("\)", na=False) == False)
)
gdf.loc[mask, "name_5"] = gdf.loc[mask, "name_5"].str.replace(r"\(.*", "", regex=True)


# Guatemala
print("Guatemala", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Guatemala") & (gdf["name_1"] == "Sololá") & (gdf["name_2"] == "?"),
    "name_2",
] = "Lake Atitlán"
gdf.loc[
    (gdf["name_0"] == "Guatemala") & (gdf["name_1"] == "Izabal") & (gdf["name_2"] == "?"),
    "name_2",
] = "Lake Izabal"

# Guinée
print("Guinée", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Guinea")
    & (gdf["name_1"] == "Kindia")
    & (gdf["name_2"] == "Coyah")
    & (gdf["name_3"].isin(["Unknown"])),
    "name_3",
] = "Manéah"
gdf.loc[
    (gdf["name_0"] == "Guinea")
    & (gdf["name_1"] == "Labé")
    & (gdf["name_2"] == "Labé")
    & (gdf["name_3"].isin(["Unknown"])),
    "name_3",
] = "Labé-Centre"


# Guyana
print("Guyana", end=" ; ")
mask = (
    (gdf["name_0"] == "Guyana")
    & (gdf[f"name_2"].str.contains("\(", na=False))
    & (gdf[f"name_2"].str.contains("\)", na=False) == False)
)
gdf.loc[mask, "name_2"] = gdf.loc[mask, "name_2"].str.replace(r"\(.*", "", regex=True)

# Iran
print("Iran", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Iran")
    & (gdf["name_1"] == "Razavi Khorasan")
    & (gdf["name_2"] == "Chenaran"),
    "name_2",
] = "Golbahar & Torqabeh and Shandiz"
for i in range(1, 4):
    mask = (gdf["name_0"] == "Iran") & (gdf["name_2"] == f"n.a. (0{i})")
    gdf.loc[mask, "name_2"] = {
        "1": "Salas-e Babajani",
        "2": "Boshruyeh, Eshqabad & Ferdows",
        "3": "Chenaran",
    }.get(f"{i}", f"n.a. (0{i})")

# Italie
print("Italie", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Italy")
    & (gdf["name_1"] == "Sicily")
    & (gdf["name_2"] == "Messina")
    & (gdf["name_3"].isin(["Unknown1"])),
    "name_3",
] = "Lipari"
gdf.loc[
    (gdf["name_0"] == "Italy")
    & (gdf["name_1"] == "Toscana")
    & (gdf["name_2"] == "Grosseto")
    & (gdf["name_3"].isin(["Unknown4"])),
    ["name_2", "name_3"],
] = ["Livorno", "Portoferraio"]
gdf.loc[
    (gdf["name_0"] == "Italy")
    & (gdf["name_1"] == "Toscana")
    & (gdf["name_2"] == "Livorno")
    & (gdf["name_3"] == "Unknown2"),
    "name_3",
] = "Campo Nell' Elba & Gorgona Island"
gdf.loc[
    (gdf["name_0"] == "Italy")
    & (gdf["name_1"] == "Toscana")
    & (gdf["name_2"] == "Livorno")
    & (gdf["name_3"] == "Unknown3"),
    "name_3",
] = "Capoliveri"

# Kenya
print("Kenya", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Kenya")
    & (gdf["name_1"] == "Homa Bay")
    & (gdf["name_2"] == "unknown 6"),
    ["name_2", "name_3"],
] = ["Karachuonyo", "Unknown (Karachuonyo)"]
gdf.loc[
    (gdf["name_0"] == "Kenya")
    & (gdf["name_1"] == "Machakos")
    & (gdf["name_2"] == "unknown 7"),
    ["name_2", "name_3"],
] = ["Machakos Town", "Kalama"]
gdf.loc[
    (gdf["name_0"] == "Kenya") & (gdf["name_1"] == "Mandera") & (gdf["name_2"] == "unknown 1"),
    ["name_2", "name_3"],
] = ["Mandera South", "Shimbir Fatuma & Fincharo"]
gdf.loc[
    (gdf["name_0"] == "Kenya")
    & (gdf["name_1"] == "Trans Nzoia")
    & (gdf["name_2"] == "unknown 4"),
    ["name_2", "name_3"],
] = ["Kwanza", "Kapomboi"]
gdf.loc[
    (gdf["name_0"] == "Kenya") & (gdf["name_1"] == "Turkana") & (gdf["name_2"] == "unknown 2"),
    ["name_2", "name_3"],
] = ["Turkana East", "Lokori/Kachodin"]
gdf.loc[
    (gdf["name_0"] == "Kenya")
    & (gdf["name_1"] == "West Pokot")
    & (gdf["name_2"] == "unknown 3"),
    ["name_2", "name_3"],
] = ["Kapenguria", "Riwo"]
gdf.loc[
    (gdf["name_0"] == "Kenya") & (gdf["name_1"] == "Meru") & (gdf["name_2"] == "unknown 5"),
    ["name_2", "name_3"],
] = ["Central Imenti", "Kiagu"]

# Liberia
mask = gdf["name_0"] == "Liberia"
gdf.loc[mask, "name_2"] = gdf.loc[mask, "name_2"].str.replace("#", "", regex=False)

# Maroc
print("Maroc", end=" ; ")
mask = (gdf["name_0"] == "Morocco") & (gdf["name_3"].str.contains("NA", na=False, case=True))
gdf.loc[mask, "name_3"] = (
    gdf.loc[mask, "name_3"].str.replace("\)", "").str.replace("NA \(", "")
)
mask = (gdf["name_0"] == "Morocco") & (
    gdf["name_3"].str.contains("Sans nom", na=False, case=False)
)
gdf.loc[mask, "name_3"] = gdf.loc[mask, "name_4"]

# Népal
print("Népal", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Nepal")
    & (gdf["name_3"] == "Bara")
    & (gdf["name_4"].str.contains("n\.a\.", na=False))
    & (gdf["name_4"].str.contains("1", na=False)),
    "name_4",
] = "Kakadi (2)"

gdf.loc[
    (gdf["name_0"] == "Nepal")
    & (gdf["name_3"] == "Bara")
    & (gdf["name_4"].str.contains("n\.a\.", na=False))
    & (gdf["name_4"].str.contains("2", na=False)),
    "name_4",
] = "Rampurwa (2)"

# Ouganda
print("Ouganda", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Uganda")
    & (gdf["name_1"] == "Masindi")
    & (gdf["name_2"] == "Bujenje (?)"),
    "name_2",
] = "Buliisa"

# Portugal
print("Portugaal", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Portugal")
    & (gdf["name_1"] == "Viana do Castelo")
    & (gdf["name_2"] == "Viana do Castelo")
    & (gdf["name_3"].isin(["unknown-1"])),
    "name_3",
] = "Geraz Do Lima"


# Russie
print("Russie", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Russia")
    & (gdf["name_1"] == "Sverdlovsk")
    & (gdf["name_2"].isin(["NA (2)"])),
    "name_2",
] = "Artemovskiy"

# Rwanda
print("Rwanda", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Rwanda")
    & (gdf["name_1"] == "Iburengerazuba")
    & (gdf["name_2"] == "Rubavu")
    & (gdf["name_3"] == "Bugeshi")
    & (gdf["name_4"] == "Hehu")
    & (gdf["name_5"] == "?"),
    "name_5",
] = "Ngando"

# Soudan et Soudan du Sud
print("Soudan et Soudan du Sud", end=" ; ")
mask = gdf["name_0"].str.contains("Sudan", regex=False) & gdf["name_3"].str.contains(
    "_", regex=False
)
gdf.loc[mask, "name_3"] = gdf.loc[mask, "name_2"]
mask = (
    (gdf["name_0"] == "Sudan")
    & (gdf["name_1"] == "Kassala")
    & (gdf["name_2"] == "Seteet")
    & (gdf["name_3"].isin(["Unknown1"]))
)
gdf.loc[mask, "name_3"] = gdf.loc[mask, "name_2"]

# Suisse
print("Suisse", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Switzerland")
    & (gdf["name_1"] == "Ticino")
    & (gdf["name_2"] == "Lugano")
    & (
        gdf["name_3"].isin(
            ["Astano", "Bedigliora" "Curio", "Miglieglia", "Novaggio", "Unknown"]
        )
    ),
    "name_3",
] = "Lema"

# Tonga
print("Tonga", end=" ; ")
mask = gdf["name_0"] == "Tonga"
gdf.loc[mask, "name_2"] = gdf.loc[mask, "name_2"].str.replace(pat="n.a.", repl="", regex=False)

# Tunisie
print("Tunisie", end=" ; ")
gdf.loc[
    (gdf["name_0"] == "Tunisia")
    & (gdf["name_1"].isin(["Monastir"]))
    & (gdf["name_2"].isin(["Unknown1"])),
    "name_2",
] = "Kuriat Islands"
gdf.loc[
    (gdf["name_0"] == "Tunisia")
    & (gdf["name_1"].isin(["Tunis"]))
    & (gdf["name_2"].isin(["Unknown"])),
    "name_2",
] = "Unknown 1 (Tunis)"

# Ukraine
print("Ukraine", end=".\n")
gdf.loc[(gdf["name_0"] == "Ukraine") & (gdf["name_1"] == "?"), ["name_1", "name_2"]] = [
    "Kiev City",
    "Darnytskyi",
]


print("Nettoyage général.")
for i in range(6):

    # Ajout d'une parenthèse pour les cas restants
    mask = (gdf[f"name_{i}"].str.contains("\(", na=False)) & (
        gdf[f"name_{i}"].str.contains("\)", na=False) == False
    )
    gdf.loc[mask, f"name_{i}"] = gdf.loc[mask, f"name_{i}"] + ")"

    # Remplacement des NA par Unknown et ajout du niveau précédent dans la valeur
    if i >= 1:
        mask = gdf[f"name_{i}"].str.contains("n\.a\.", na=False, case=False)
        gdf.loc[mask, f"name_{i}"] = (
            gdf.loc[mask, f"name_{i-1}"]
            + " – "
            + gdf.loc[mask, f"name_{i}"].str.replace(
                "n.a.", "Unknown", regex=False, case=False
            )
        ).str.replace("( ", "(", regex=False, case=False)

    # Nettoyage des espaces
    gdf[f"name_{i}"] = (
        gdf[f"name_{i}"]
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
    mask = gdf[f"name_{i+1}"] == ""
    gdf.loc[mask, f"name_{i+1}"] = gdf.loc[mask, f"name_{i}"]

print("Concaténation des valeurs dupliquées.")


def concatener_noms_si_dupliques(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pour chaque colonne name_i (en partant de name_n vers name_1), concatène les valeurs
    des colonnes name_0 à name_i si le couple (name_0, name_i) apparaît plusieurs fois.

    Paramètres :
    - df (pd.DataFrame) : Le DataFrame à traiter.

    Retour :
    - pd.DataFrame : Le DataFrame modifié.
    """

    # Identifier toutes les colonnes name_i et les trier selon l'indice croissant
    colonnes = sorted([col for col in gdf.columns if col.startswith("name_")])

    for i in range(len(colonnes) - 1, 1, -1):

        # Conservation des doublons qui ont une hiérarchie différente
        mask = (df.duplicated(subset=["name_0", f"name_{i}"], keep=False)) & (
            ~df.duplicated(subset=[f"name_{j}" for j in range(0, i + 1)], keep=False)
        )

        for k in range(i - 1, 0, -1):
            df.loc[mask, f"name_{i}"] = (
                df.loc[mask, f"name_{k}"] + " – " + df.loc[mask, f"name_{i}"]
            )

    return df


# === Tests ===


print("Tests...")
for i in range(6):

    # Aucun "?"
    assert (
        len(gdf[gdf[f"name_{i}"].str.contains("\?", na=False)]) == 0
    ), f"Il y a des '?' dans la colonne name_{i}"

    # Aucun "_"
    assert (
        len(gdf[gdf[f"name_{i}"].str.contains("_", na=False)]) == 0
    ), f"Il y a des '?' dans la colonne name_{i}"

    # Aucun
    assert (
        len(gdf[gdf[f"name_{i}"].str.contains("\ufffd", na=False)]) == 0
    ), f"Il y a des '�' dans la colonne name_{i}"

    # Aucun "*"
    if i != 3:
        assert (
            len(gdf[gdf[f"name_{i}"].str.contains("\*", na=False)]) == 0
        ), f"Il y a des '*' dans la colonne name_{i}"


# Export
with open(direction_donnees + "\\geodataframe_reduit.pkl", "wb") as f:
    pickle.dump(gdf, f)

# === Création des tables à une granularité plus faible ===

# Niveau 4
with open(direction_donnees + "\\carte_monde_niveau_4.pkl", "wb") as f:
    pickle.dump(
        gdf.dissolve(
            by=["name_0", "name_1", "name_2", "name_3", "name_4"],
            aggfunc={
                "name_0": "first",
                "name_1": "first",
                "name_2": "first",
                "name_3": "first",
                "name_4": "first",
            },
        ),
        f,
    )

# Niveau 3
with open(direction_donnees + "\\carte_monde_niveau_3.pkl", "wb") as f:
    pickle.dump(
        gdf.dissolve(
            by=["name_0", "name_1", "name_2", "name_3"],
            aggfunc={
                "name_0": "first",
                "name_1": "first",
                "name_2": "first",
                "name_3": "first",
            },
        ),
        f,
    )

# Niveau 2
with open(direction_donnees + "\\carte_monde_niveau_2.pkl", "wb") as f:
    pickle.dump(
        gdf.dissolve(
            by=["name_0", "name_1", "name_2"],
            aggfunc={
                "name_0": "first",
                "name_1": "first",
                "name_2": "first",
            },
        ),
        f,
    )

# Niveau 1
with open(direction_donnees + "\\carte_monde_niveau_1.pkl", "wb") as f:
    pickle.dump(
        gdf.dissolve(
            by=["name_0", "name_1"],
            aggfunc={
                "name_0": "first",
                "name_1": "first",
            },
        ),
        f,
    )

# Niveau 0
with open(direction_donnees + "\\carte_monde_niveau_0.pkl", "wb") as f:
    pickle.dump(
        gdf.dissolve(
            by=["name_0"],
            aggfunc={
                "name_0": "first",
            },
        ),
        f,
    )


def concatener_noms_si_dupliques(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pour chaque colonne name_i (en partant de name_n vers name_1), concatène les valeurs
    des colonnes name_0 à name_i si le couple (name_0, name_i) apparaît plusieurs fois.

    Paramètres :
    - df (pd.DataFrame) : Le DataFrame à traiter.

    Retour :
    - pd.DataFrame : Le DataFrame modifié.
    """

    # Identifier toutes les colonnes name_i et les trier selon l'indice croissant
    colonnes = sorted(
        [col for col in df.columns if col.startswith("name_")],
        key=lambda x: int(x.split("_")[1]),
    )

    # Récursivement, on part de name_n vers name_1 (on ne touche pas à name_0)
    for i in range(len(colonnes) - 1, 0, -1):
        col_courante = colonnes[i]
        # Vérifier les doublons (name_0, name_i)
        doublons = df.duplicated(subset=["name_0", col_courante], keep=False)

        # Colonnes à concaténer : name_0 à name_i
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
