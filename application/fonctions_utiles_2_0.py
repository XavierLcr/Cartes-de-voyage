################################################################################
# Projet de cartes de voyage                                                   #
# 2.0 - Fonctions utiles à l'application                                       #
################################################################################


import os, pickle, yaml
from PyQt6.QtWidgets import QHBoxLayout, QFrame, QLabel
from PyQt6.QtCore import Qt
from collections import defaultdict


def creer_QLabel_centre(text: str | None = None, parent=None):
    """
    Crée un QLabel avec un alignement vertical centré.

    Args:
        text (str|None): Texte à afficher dans le label (optionnel).
        parent (QWidget): Widget parent (optionnel).

    Returns:
        QLabel: Le label configuré.
    """
    label = QLabel(text, parent)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label


def obtenir_clef_par_valeur(dictionnaire, valeur):
    """Retourne la clé associée à une valeur donnée dans un dictionnaire."""
    for clef, val in dictionnaire.items():
        if val == valeur:
            return clef
    return None


def reset_combo(combo, items, set_index=True):
    combo.clear()
    combo.addItems(items)
    if set_index:
        combo.setCurrentIndex(0)


def style_bouton_de_suppression(sombre):
    return f"""QPushButton {{
                            background-color:{"#000000" if sombre else "#f8d7da"};
                            color: {"#E6E6E6" if sombre else "#2C2C2C"};
                            font-size: 12px;
                            border: none;
                            border-radius: 5px;
                            padding: 8px;
                            }}
                QPushButton:hover {{
                                    background-color: {"#85040d" if sombre else "#f5c6cb"};
                                  }}
            """


def creer_classement_pays(
    gdf_visite,
    table_superficie,
    granularite: int = 1,
    top_n: int | None = None,
):

    # gdf_visite = (
    #     gdf_visite.loc[gdf_visite["Granu"] == granularite]
    #     .assign(Visite=lambda x: x["Visite"].astype(int))
    #     .assign(Visite=lambda x: x.groupby("Region")["Visite"].transform("max"))
    #     .loc[lambda x: x["Visite"] == 1]
    # )

    gdf_visite = (
        # Filtre sur la granularité
        gdf_visite.loc[gdf_visite["Granu"] == granularite]
        # Conversion en nombre en entier de l'indicatrice
        .assign(Visite=lambda x: x["Visite"].astype(int))
        # Sélection de ces régions et des colonnes utiles
        .loc[lambda x: x["Visite"] == 1][["Pays", "Region", "Granu", "Visite"]]
        # Ajout des superficies
        .merge(
            table_superficie,
            how="left",
            left_on=["Pays", "Region"],
            right_on=["NAME_0", f"NAME_{granularite}"],
        )
        # Somme par pays des superficies visitées
        .groupby("Pays")[["pct_superficie_dans_pays", "superficie"]]
        .sum()
        .reset_index()
        # Tri des valeurs par ordre décroissant
        .sort_values(by=["pct_superficie_dans_pays", "superficie"], ascending=[False, False])
    )

    return gdf_visite if top_n is None else gdf_visite.head(top_n)


def valeurs_dans_plusieurs_listes(d):
    valeur_cles = defaultdict(list)

    # On parcourt le dictionnaire et on enregistre pour chaque valeur les clés où elle apparaît
    for cle, liste in d.items():
        for val in liste:
            valeur_cles[val].append(cle)

    # Ne garder que les valeurs qui apparaissent dans plusieurs listes
    return {val: cles for val, cles in valeur_cles.items() if len(cles) > 1}


def nb_pays_visites(
    dict_granu: dict,
    continents: dict,
    a_supprimer: dict = {
        "Africa": [
            "French Southern Territories",
            "Portugal",
            "Saint Helena, Ascension and Tris",
            "Spain",
        ],
        "Asia": [
            "Akrotiri and Dhekelia",
            "Armenia",
            "Azerbaijan",
            "Cyprus",
            "Egypt",
            "Georgia",
            "Northern Cyprus",
            "Turkey",
        ],
        "Oceania": ["Indonesia"],
        "North America": ["United States Minor Outlying Isl", "Grenada"],
        "South America": ["Bonaire, Sint Eustatius and Saba", "Panama"],
    },
):

    # Suppression du Moyen-Orient
    if "Middle East" in list(continents.keys()):
        del continents["Middle East"]

    # Suppression des doublons
    continents = {
        continent: [pays for pays in liste_pays if pays not in a_supprimer.get(continent, [])]
        for continent, liste_pays in continents.items()
    }

    print(valeurs_dans_plusieurs_listes(continents), end="\n\n")

    resultat = {}
    for continent in list(continents.keys()):

        resultat[continent] = {
            # Nombre de pays dans le continents
            "total": len(continents[continent]),
            # Nombre de pays visités dans le continent
            "visites": len(
                [
                    i
                    for i in continents[continent]
                    if i
                    # Liste des pays visités
                    in list(set(list(dict_granu["region"].keys()) + list(dict_granu["dep"].keys())))
                ]
            ),
        }

    print(resultat, end="\n\n")
    return resultat


def creer_ligne_separation(lStretch=1, ligne_largeur=4, rStretch=1):
    """Afficher une simple ligne horizontale."""
    layout_temp = QHBoxLayout()
    ligne = QFrame()
    ligne.setFixedHeight(2)
    ligne.setFrameShape(QFrame.Shape.HLine)  # Ligne horizontale
    ligne.setFrameShadow(QFrame.Shadow.Sunken)  # Style de relief
    layout_temp.addStretch(lStretch)
    layout_temp.addWidget(ligne, ligne_largeur)
    layout_temp.addStretch(rStretch)
    return layout_temp


def creer_ligne_verticale():
    """Afficher une simple ligne verticale."""
    ligne = QFrame()
    ligne.setFrameShape(QFrame.Shape.VLine)
    ligne.setFrameShadow(QFrame.Shadow.Raised)
    return ligne


# Fonction d'ouverture dedonnées
def ouvrir_fichier(direction_fichier, nom_fichier, defaut, afficher_erreur: str | None = None):

    nom_fichier = os.path.join(direction_fichier, nom_fichier)
    nom, extention = os.path.splitext(nom_fichier)

    try:

        if extention == ".pkl":

            with open(
                nom_fichier,
                "rb",
            ) as file:
                return pickle.load(file)

        elif extention == ".yaml":

            with open(
                nom_fichier,
                "r",
                encoding="utf-8",
            ) as file:
                return yaml.safe_load(file)
    except:

        if afficher_erreur is not None:
            print(afficher_erreur)

        return defaut


def exporter_fichier(objet, direction_fichier, nom_fichier, sort_keys: bool = True):

    nom_fichier = os.path.join(direction_fichier, nom_fichier)
    nom, extention = os.path.splitext(nom_fichier)

    # Création de la direction de sauvegarde du résultat si nécessaire
    if not os.path.exists(direction_fichier):
        os.makedirs(direction_fichier)

    if extention == ".yaml":

        with open(
            nom_fichier,
            "w",
            encoding="utf-8",
        ) as file:
            yaml.dump(
                objet, file, allow_unicode=True, default_flow_style=False, sort_keys=sort_keys
            )


def reordonner_dict(dictionnaire: dict, clefs: list):
    return {k: dictionnaire[k] for k in clefs if k in dictionnaire}
