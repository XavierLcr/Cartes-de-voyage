################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_2_application/2_2_1_traductions/                           #
# 2.2.1.2 – Fichier de traduction des pays et de l'interface                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys, time, textwrap
import google.genai

sys.path.append(os.getcwd())

from constantes import (
    direction_donnees_traductions,
    direction_donnees_autres,
    phrases_interface,
    liste_regions_monde,
    hierarchie_par_pays,
    liste_pays_groupes,
)
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_fichier,
    exporter_fichier,
    formater_temps_actuel,
    sleep_n_fois,
)

from clefs_et_mots_de_passe import clef_api_gemini, liste_langues, modeles_google

# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de traductions des pays et de l'interface -------------------


def creer_liste_pays_multilangue(
    liste_pays: list,
    modele_dict: dict,
    liste_deja_existante: dict,
    liste_langues: list,
    blabla: int,
    version: int,
):

    modele = modele_dict.get("modèle", "gemini-2.5-flash-lite")
    limite_api_minute = modele_dict.get("limite_appels_minute", 30)
    client = google.genai.Client(vertexai=False, api_key=clef_api_gemini)

    resultat = liste_deja_existante or {}
    global api_jour_modele

    for i in sorted(set(liste_pays)):

        premiere_trad = True

        # Récupération des traduction du pays
        resultat[i] = resultat.get(i, {})

        # Traduction dans chaque langue
        for j in liste_langues:

            temps_debut = time.time()

            if j in resultat[i]:
                resultat[i][j] = resultat[i][j].strip(" .'\n")
                continue
            elif api_jour_modele >= modele_dict.get("limite_appels_jour", 200):
                continue

            if blabla >= 1 and premiere_trad == True:
                print(textwrap.shorten(i.strip(" \n-="), width=50, placeholder="..."))
                premiere_trad = False

            if blabla >= 2:
                print("    • ", j)

            if (j == "anglais" and version == 0) or (j == "français" and version == 1):
                resultat[i][j] = i
                continue

            phrase = (
                f"Traduis le nom du pays (ou du groupe de pays) qui va t'être donné en {j} : {i}."
                if version == 0
                else f"Traduis la phrase qui va t'être donnée en {j} : {i}."
            )
            try:
                resultat[i][j] = client.models.generate_content(
                    model=modele,
                    contents=f"{phrase} "
                    "Ne donne que la traduction, rien d'autre. "
                    "N'inclus en aucun cas la prononciation. "
                    "Si tu n'es pas certain, renvoie le nom non traduit. ",
                ).text.strip("\n .'")
            except Exception as e:
                print(f"Erreur : {e}")
                pass

            # Attente si nécessaire
            sleep_n_fois(n=limite_api_minute, time_ref=temps_debut)

            # Mise à jour du nombre d'appels
            api_jour_modele = api_jour_modele + 1

    if blabla >= 1:
        print("")

    return resultat


# 2 -- Lecture des données -----------------------------------------------------


# Date du jour
date_jour = formater_temps_actuel(n=2)


## 2.1 -- Appels API déjà effectués --------------------------------------------


api_dict = ouvrir_fichier(
    direction_fichier=direction_donnees_autres,
    nom_fichier="appels_api_par_jour.yaml",
    defaut={},
    afficher_erreur="Fichier YAML des appels API non trouvé.",
)


## 2.2 -- Traductions des noms des pays ----------------------------------------


pays = ouvrir_fichier(
    direction_fichier=direction_donnees_traductions,
    nom_fichier="noms_pays_traduction.yaml",
    defaut={},
    afficher_erreur="Fichiers YAML des traductions des noms de pays non trouvé.",
)


## 2.3 -- Traductions de l'interface -------------------------------------------


interface = ouvrir_fichier(
    direction_fichier=direction_donnees_traductions,
    nom_fichier="phrases_interface_traduction.yaml",
    defaut={},
    afficher_erreur="Fichiers YAML des traductions des phrases de l'interface non trouvé.",
)


## 2.4 -- Liste des pays à traduire --------------------------------------------


## Monde
liste_pays = ["World Map", "World"]

# Continents
for continent in liste_regions_monde.keys():
    liste_pays.append(continent)
    if continent == "Middle East":
        liste_pays.append(f"Map of the {continent}")
    else:
        liste_pays.append(f"Map of {continent}")

# Pays regroupés
liste_pays.extend(gr["categorie"] for gr in liste_pays_groupes.values())

# Pays individuels
liste_pays.extend(list(hierarchie_par_pays.keys()))


# 3 -- Traductions -------------------------------------------------------------


for modele in modeles_google:

    # Appel API
    api_jour_modele = int(api_dict.get(date_jour, {}).get(modele["modèle"], 0))

    # Pays
    pays = creer_liste_pays_multilangue(
        liste_pays=liste_pays,
        modele_dict=modele,
        liste_deja_existante=pays,
        liste_langues=liste_langues,
        version=0,
        blabla=2,
    )

    # Interface
    interface = creer_liste_pays_multilangue(
        liste_pays=list(phrases_interface.values()),
        modele_dict=modele,
        liste_deja_existante=interface,
        liste_langues=liste_langues,
        version=1,
        blabla=2,
    )

    # Appels API
    if not date_jour in list(api_dict.keys()):
        api_dict[date_jour] = {}
    api_dict[date_jour][modele["modèle"]] = api_jour_modele


# 4 -- Export ------------------------------------------------------------------


## 4.1 -- Pays -----------------------------------------------------------------


exporter_fichier(
    objet=pays,
    direction_fichier=direction_donnees_traductions,
    nom_fichier="noms_pays_traduction.yaml",
    sort_keys=True,
)


## 4.2 -- Interface ------------------------------------------------------------


exporter_fichier(
    objet=interface,
    direction_fichier=direction_donnees_traductions,
    nom_fichier="phrases_interface_traduction.yaml",
    sort_keys=True,
)


## 4.3 -- Appels API effectués -------------------------------------------------


exporter_fichier(
    objet=api_dict,
    direction_fichier=direction_donnees_autres,
    nom_fichier="appels_api_par_jour.yaml",
    sort_keys=True,
)
