################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_2_application/2_2_1_traductions/                           #
# 2.2.1.3 – Fichier de traduction des noms de langues                          #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


import os, sys, time
import google.genai

sys.path.append(os.getcwd())

from constantes import (
    direction_donnees_traductions,
    direction_donnees_autres,
    dict_langues_dispo,
)
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_fichier,
    exporter_fichier,
    formater_temps_actuel,
    sleep_n_fois,
)

from clefs_et_mots_de_passe import clef_api_gemini, liste_langues, modeles_google


# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de traduction des langues -----------------------------------


### Fonction générique ---------------------------------------------------------


def creer_dictionnaire_langues(
    modele_dict: dict,
    liste_deja_existante: dict,
    liste_langues: list,
    blabla: bool = True,
):

    modele = modele_dict.get("modèle", "gemini-2.5-flash-lite")
    modele_limite_jour = modele_dict.get("limite_appels_jour", 200)
    modele_limite_minute = modele_dict.get("limite_appels_minute", 30)
    client = google.genai.Client(vertexai=False, api_key=clef_api_gemini)
    resultat = {} if liste_deja_existante is None else liste_deja_existante
    global api_jour_modele

    for i in list(set(liste_langues)):

        if i not in list(resultat.keys()) and api_jour_modele < modele_limite_jour:

            temps_debut = time.time()

            if blabla:
                print(f"{i} : {resultat[i]}")

            # Traduction
            try:
                resultat[i] = client.models.generate_content(
                    model=modele,
                    contents=f"Le nom d'une langue va t'être donné en français. "
                    "Donne le nom de cette langue dans sa version propre. "
                    "Par exemple anglais donne English et allemand donne Deutsch. "
                    "Mets une majuscule quand cela est possible. "
                    "Ne renvoie rien d'autre et surtout pas de ponctuation ou de prononciation pour les langues exotiques. "
                    f"\nLa langue est : '{i}'.",
                ).text.strip(" .'\n")

            except Exception as e:
                print(f"Erreur : {e}")
                continue

            # Attente si nécessaire
            sleep_n_fois(n=modele_limite_minute, time_ref=temps_debut)

            # Mise à jour du nombre d'appels
            api_jour_modele = api_jour_modele + 1

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


## 2.2 -- Traductions de langues ------------------------------------------------


langues = ouvrir_fichier(
    direction_fichier=direction_donnees_traductions,
    nom_fichier="noms_langues_traduction.yaml",
    defaut={},
    afficher_erreur="Fichiers YAML des traductions des noms de langues non trouvé.",
)


# 3 -- Traduction --------------------------------------------------------------


for modele in modeles_google:

    # Appel API
    api_jour_modele = int(api_dict.get(date_jour, {}).get(modele["modèle"], 0))

    # Traduction des langues
    langues = creer_dictionnaire_langues(
        modele_dict=modele,
        liste_deja_existante=langues,
        liste_langues=liste_langues,
        blabla=True,
    )

    # Appels API
    if not date_jour in list(api_dict.keys()):
        api_dict[date_jour] = {}
    api_dict[date_jour][modele["modèle"]] = api_jour_modele


# 4 -- Export ------------------------------------------------------------------


## 4.1 -- Pays -----------------------------------------------------------------


exporter_fichier(
    objet=langues,
    direction_fichier=direction_donnees_traductions,
    nom_fichier="noms_langues_traduction.yaml",
    sort_keys=True,
)


## 4.2 -- Appels API effectués -------------------------------------------------


exporter_fichier(
    objet=api_dict,
    direction_fichier=direction_donnees_autres,
    nom_fichier="appels_api_par_jour.yaml",
    sort_keys=True,
)
