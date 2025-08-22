################################################################################
# Projet de cartes de voyage                                                   #
# 2.0 - Fonctions utiles à l'application                                       #
################################################################################


import os, pickle, yaml
from PyQt6.QtWidgets import QHBoxLayout, QFrame, QLabel
from PyQt6.QtCore import Qt


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

    gdf_visite = gdf_visite[gdf_visite["Granu"] == granularite]
    gdf_visite["Visite"] = gdf_visite["Visite"].astype(int)
    gdf_visite["Visite"] = gdf_visite.groupby("Region")["Visite"].transform("max")
    gdf_visite = gdf_visite[gdf_visite["Visite"] == 1]

    gdf_visite = (
        gdf_visite[["Pays", "Region", "Granu", "Visite"]]
        .merge(
            table_superficie,
            how="left",
            left_on=["Pays", "Region"],
            right_on=["NAME_0", f"NAME_{granularite}"],
        )
        .groupby("Pays")[["pct_superficie_dans_pays", "superficie"]]
        .sum()
        .reset_index()
        .sort_values(by=["pct_superficie_dans_pays", "superficie"], ascending=[False, False])
    )

    return gdf_visite if top_n is None else gdf_visite.head(top_n)


def nb_pays_visites(dict_granu: dict, continents: dict):

    # Conservation des lieux visités
    pays_visites = list(dict_granu["region"].keys()) + list(dict_granu["dep"].keys())
    pays_visites = list(set(pays_visites))

    resultat = {}
    for continent in list(continents.keys()):

        resultat[continent] = {}
        resultat[continent]["total"] = len(continents[continent])
        resultat[continent]["visites"] = len(
            [i for i in continents[continent] if i in pays_visites]
        )

    if "Middle East" in list(continents.keys()):
        del resultat["Middle East"]

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
def ouvrir_fichier(direction_fichier, nom_fichier, defaut):

    nom_fichier = os.path.join(direction_fichier, nom_fichier)
    nom, extention = os.path.splitext(nom_fichier)

    try:

        if extention == ".pkl":

            with open(
                nom_fichier,
                "rb",
            ) as file:
                fichier = pickle.load(file)

        elif extention == ".yaml":

            with open(
                nom_fichier,
                "r",
                encoding="utf-8",
            ) as file:
                fichier = yaml.safe_load(file)
    except:
        fichier = defaut

    return fichier
