################################################################################
# Projet de cartes de voyage                                                   #
# _X_Autres/                                                                   #
# X.1 – Ancien script de création de cartes (SVG) avec la bibliothèque wordmap #
################################################################################


import os, yaml
import worldmap as wm
from translate import Translator

# Nom de la personne
nom = "Xavier"

# Directions et adresses
base_dir = os.path.join(os.path.expanduser("~"), "Documents", "Voyages")
direction_dossier = os.path.join(base_dir, f"{nom} – Cartes de voyage")
yaml_fichier = os.path.join(base_dir, f"Liste_destinations_{nom}.yaml")

# Ouverture et lecture le fichier YAML
with open(yaml_fichier, "r", encoding="utf-8") as file:
    destinations = yaml.safe_load(file)


# Crée la carte pour un pays à partir d'un fichier Yaml
def cree_carte_pays(
    nom_pays,
    liste_destinations,
    direction=None,
    couleur="rainbow",
    blabla=False,
    personne="",
    langue="fr",
):

    # Création du nom du fichier
    nom_fichier = (
        "Oman" if nom_pays == "Oman" else Translator(to_lang=langue).translate(nom_pays)
    )
    nom_fichier = f"{(personne + ' – ') if personne else ''}{nom_fichier}.svg"
    if direction != None:
        nom_fichier = os.path.join(direction, nom_fichier)

    # Édition de la carte si cela est possible
    if nom_pays in list(liste_destinations.keys()) and nom_pays != "United States":

        if liste_destinations[nom_pays] != None:
            return wm.plot(
                liste_destinations[nom_pays],
                map_name=nom_pays,
                cmap=couleur,
                filename=nom_fichier,
                verbose=blabla,
                showfig=False,
            )
        else:
            print(nom_pays, "ne contient pas le détail des destinations effectuées.")

    elif nom_pays == "United States":

        if liste_destinations[nom_pays] != None:
            return wm.plot(
                liste_destinations[nom_pays],
                map_name="usa",
                cmap=couleur,
                filename=nom_fichier,
                verbose=blabla,
                showfig=False,
            )
        else:
            print(nom_pays, "ne contient pas le détail des destinations effectuées.")

    else:
        print(nom_pays, "ne fait pas partie de la liste des pays visités.")


# Crée l'entièreté des cartes à partir du yaml
def cree_toutes_les_cartes(
    liste_destinations,
    direction=None,
    bulgarie=False,
    langue="fr",
    personne="",
    blabla=False,
    couleur="rainbow",
):

    # Vérification et création du dossier
    if not os.path.exists(direction):
        os.makedirs(direction)

    ## Récupération de la liste des pays
    pays = list(liste_destinations.keys())

    ## Crée la carte du monde
    # Création du nom du fichier
    nom_fichier = f"{personne} – Carte du monde.svg" if personne else "Carte du monde.svg"
    if direction != None:
        nom_fichier = os.path.join(direction, nom_fichier)

    # Création du fichier
    wm.plot(pays, map_name="world", cmap=couleur, filename=nom_fichier, showfig=False)

    ## Crée la carte de chaque pays où cela est possible - Sauf potentiellement la Bulgarie
    for p in pays:
        if p != "Bulgaria" or bulgarie == True:
            cree_carte_pays(
                nom_pays=p,
                liste_destinations=liste_destinations,
                personne=personne,
                direction=direction,
                langue=langue,
                couleur=couleur,
                blabla=blabla,
            )
