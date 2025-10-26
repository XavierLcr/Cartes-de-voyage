################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.1 - Fonctions utiles à l'application                                       #
################################################################################


import os, pickle, yaml, time, numba
import pandas as pd
import numpy as np
from datetime import date
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QFrame, QLabel, QGroupBox, QWidget
from PyQt6.QtCore import Qt


# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction créant un QLabel --------------------------------------------


def creer_QLabel_centre(
    alignement=Qt.AlignmentFlag.AlignCenter,
    text: str | None = None,
    parent=None,
    wordWrap=False,
):
    """
    Crée un QLabel avec un alignement vertical centré.

    Args:
        text (str|None): Texte à afficher dans le label (optionnel).
        parent (QWidget): Widget parent (optionnel).

    Returns:
        QLabel: Le label configuré.
    """
    label = QLabel(text, parent, wordWrap=wordWrap)
    label.setAlignment(alignement)
    return label


## 1.2 -- Retourne la première clef dont la valeur en vaut une de référence ----


def obtenir_clef_par_valeur(dictionnaire, valeur):
    """Retourne la clé associée à une valeur donnée dans un dictionnaire."""
    for clef, val in dictionnaire.items():
        if val == valeur:
            return clef
    return None


## 1.3 -- Remplace l'entièreté des valeurs d'un combo PyQt6 --------------------


def reset_combo(combo, items, set_index=True):

    combo.blockSignals(True)
    combo.clear()
    combo.addItems(items)
    if set_index:
        combo.setCurrentIndex(0)
    combo.blockSignals(False)


## 1.4 -- Vide l'entièreté d'un layout PyQt6 -----------------------------------


def vider_layout(layout):
    """Supprime tous les widgets d'un QLayout."""
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


## 1.5 -- Conserve la valeur d'un combo vidé en PyQt6 --------------------------


def restaurer_valeur_combo(combo, dict_parent, langue, valeur, defaut_index=0):
    """
    Met à jour un QComboBox avec une valeur trouvée dans un dictionnaire traduit.

    combo : QComboBox à mettre à jour
    dict_parent : dictionnaire contenant les traductions (ex: constantes.parametres_traduits["themes_cartes"])
    langue : langue courante
    valeur : valeur à restaurer en français
    defaut_index : index à mettre si aucune valeur trouvée
    """
    combo.blockSignals(True)

    if valeur is not None:
        traduction = dict_parent.get(langue, {}).get(valeur)
        if traduction is not None:
            idx = combo.findText(traduction)
            combo.setCurrentIndex(idx if idx != -1 else defaut_index)
        else:
            combo.setCurrentIndex(defaut_index)
    else:
        combo.setCurrentIndex(defaut_index)

    combo.blockSignals(False)


## 1.6 -- Assigne une couleur aux bouton de suppression et de réinitialisation -


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


## 1.7 -- Crée une ligne horizontale en PyQt6 ----------------------------------


def creer_ligne_separation(
    lStretch=1,
    ligne_largeur=4,
    rStretch=1,
    ligne_epaisseur=1,
    ligne_epaisseur_interieur=0,
    relief=QFrame.Shadow.Sunken,
):
    """Afficher une simple ligne horizontale."""

    widget = QWidget()
    layout_temp = QHBoxLayout(widget)
    layout_temp.setContentsMargins(0, 0, 0, 0)
    layout_temp.setSpacing(0)

    ligne = QFrame()
    ligne.setFixedHeight(2)
    ligne.setFrameShape(QFrame.Shape.HLine)
    ligne.setFrameShadow(relief)
    ligne.setLineWidth(ligne_epaisseur)
    ligne.setMidLineWidth(ligne_epaisseur_interieur)

    layout_temp.addStretch(lStretch)
    layout_temp.addWidget(ligne, ligne_largeur)
    layout_temp.addStretch(rStretch)

    return widget


## 1.8 -- Crée une ligne verticale en PyQt6 ------------------------------------


def creer_ligne_verticale():
    """Afficher une simple ligne verticale."""
    ligne = QFrame()
    ligne.setFrameShape(QFrame.Shape.VLine)
    ligne.setFrameShadow(QFrame.Shadow.Raised)
    return ligne


## 1.9 -- Ouvre un fichier de type .yaml ou .pkl -------------------------------


# Fonction d'ouverture dedonnées
def ouvrir_fichier(
    direction_fichier, nom_fichier, defaut, afficher_erreur: str | None = None
):
    """Ouvre un fichier de type YAML ou pickle."""

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


## 1.10 -- Fonction de chargement des .pkl principaux --------------------------


def charger_gdfs(liste_gdfs, direction_base, max_niveau=3):
    """
    Charge les fichiers pickle et remplit la liste_gdfs.
    """
    for i in range(max_niveau):
        liste_gdfs[i] = ouvrir_fichier(
            direction_fichier=direction_base,
            nom_fichier=f"carte_monde_niveau_{i}.pkl",
            defaut=None,
            afficher_erreur=f"Base de granularité {i} introuvable.",
        )  # mise à jour de la liste partagée


## 1.11 -- Fonction d'export de .yaml et de .pkl -------------------------------


def exporter_fichier(objet, direction_fichier, nom_fichier, sort_keys: bool = True):
    """Exporte un fichier de type YAML ou pickle."""

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
                objet,
                file,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=sort_keys,
            )

    elif extention == ".pkl":
        with open(
            nom_fichier,
            "wb",
        ) as f:
            pickle.dump(objet, f)

    else:
        print("Fichier non exportable.")


## 1.12 -- Fonction réordonnant un dictionnaire --------------------------------


def reordonner_dict(dictionnaire: dict, clefs: list):
    return {k: dictionnaire[k] for k in clefs if k in dictionnaire}


## 1.13 -- Fonction de formatage de l'heure et de la date actuelles ------------


def formater_temps_actuel():
    return time.strftime("%d-%m-%Y %Hh%M", time.localtime())


## 1.14 -- Fonction créant les .yaml Pays × Région/Département/... -------------


def cree_yaml_un_pays(
    gdf,
    direction_fichier,
    nom_fichier,
    nom_pays: None | list = None,
    granularite: int = 1,
):
    """Crée le yaml pour un pays à un niveau de granularité donné

    Args:
        gdf: la base geopandas.
        nom_pays (str): nom du pays dans la dataframe geopandas.
        granularite (int): 1 (faible) à 5 (forte). Sera réduite si inexistante.
        nom (str): nom du document.
    """

    if nom_pays is not None:
        gdf = gdf[gdf["name_0"].isin(nom_pays)]

    # Créer un DataFrame avec les résultats
    liste_combinaisons = (
        (
            pd.DataFrame(
                list(set(zip(gdf["name_0"], gdf[f"name_{granularite}"]))),
                columns=["nom1", "nom2"],
            )
            # Tri par nom2
            .sort_values(by="nom2", inplace=False)
        )
        .groupby("nom1")["nom2"]
        .apply(list)
        .to_dict()
    )

    if nom_fichier is None:
        return liste_combinaisons

    # Exporter vers YAML
    exporter_fichier(
        objet=liste_combinaisons,
        direction_fichier=direction_fichier,
        nom_fichier=nom_fichier,
        sort_keys=True,
    )


## 1.15 -- Fonction calculant la distance entre deux points sur terre ----------


@numba.njit
def distance_haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    return (
        2
        * 6371
        * np.arcsin(
            np.sqrt(
                np.sin((lat2 - lat1) / 2) ** 2
                + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
            )
        )
    )


## 1.16 -- Groupbox d'un widget ------------------------------------------------


def renvoyer_groupbox(objet, horizontal=True):

    layout = QHBoxLayout() if horizontal else QVBoxLayout()

    # Si l'objet est une liste de widgets
    if isinstance(objet, list):
        for widget in objet:
            layout.addWidget(widget)

    # Si l'objet est un widget unique
    else:
        layout.addWidget(objet)

    groupbox = QGroupBox()
    groupbox.setLayout(layout)
    return groupbox


## 1.17 -- Sommes-nous dans la période de Halloween ? --------------------------


def periode_particuliere() -> dict:

    mois = date.today().month
    jour = date.today().day

    # Halloween
    if mois == 10 and jour >= 20:
        return {"titre_police": "Chiller", "titre_police_coeff": 1.2, "emoji": " 🎃​"}

    # Noël
    elif mois == 12 and jour >= 15 and jour <= 28:
        return {
            "titre_police": "Edwardian Script ITC",
            "titre_police_coeff": 1.8,
            "emoji": " 🎄​​",
        }

    # Nouvel an
    elif (mois == 12 and jour >= 29) or (mois == 1 and jour <= 2):
        return {
            "titre_police": "Monotype Corsiva",
            "titre_police_coeff": 1.6,
            "emoji": " 🎆​​​",
        }

    # Printemps
    elif mois == 3 and jour in [19, 20, 21]:
        return {
            "titre_police": "Segoe Print",
            "titre_police_coeff": 1.4,
            "emoji": " 🌷​​​",
        }

    # Autômne
    elif mois == 9 and jour in [21, 22, 23]:
        return {
            "titre_police": "Constantia",
            "titre_police_coeff": 1,
            "emoji": " 🍂​​​",
        }

    # Saint-Valentin
    elif mois == 2 and jour in [12, 13, 14]:
        return {
            "titre_police": "French Script MT",
            "titre_police_coeff": 1,
            "emoji": " 💝​​​",
        }

    # Défaut
    else:
        return {
            "titre_police": "Vivaldi",
            "titre_police_coeff": 1,
            "emoji": "",
        }


## 1.18 -- Filtrer un dictionnaire en deux -------------------------------------


def separer_combinaisons(dico1, dico2):
    """Filtrer un dictionnaire en deux : les entrées présentes dans un second dictionnaire, et celles qui n’y sont pas."""

    result = {True: {}, False: {}}

    for pays in dico1:
        if pays not in result[True]:
            result[True][pays] = []
        if pays not in result[False]:
            result[False][pays] = []

        if dico1[pays] is not None:
            for region in dico1[pays]:
                if pays in dico2 and region in dico2[pays]:
                    result[True][pays].append(region)
                else:
                    result[False][pays].append(region)

    # Supprimer les pays sans régions
    result[True] = {pays: regions for pays, regions in result[True].items() if regions}
    result[False] = {
        pays: regions
        for pays, regions in result[False].items()
        if regions or (dico1[pays] is None or not dico1[pays])
    }

    return result
