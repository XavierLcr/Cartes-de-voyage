################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_2_application/                                             #
# 2.2.2 – Fichier de traduction des différents paramètres et non de pays       #
################################################################################


import os, sys, time, textwrap
import google.genai

sys.path.append(os.getcwd())

from constantes import (
    direction_donnees_traductions,
    direction_donnees_autres,
    dict_langues_dispo,
    phrases_interface,
    liste_regions_monde,
    hierarchie_par_pays,
    liste_pays_groupes,
)
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_fichier,
    exporter_fichier,
    formater_temps_actuel,
)

from clefs_et_mots_de_passe import clef_api_gemini, liste_langues, modeles_google


# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de traductions des pays et de l'interface -------------------


def creer_liste_pays_multilangue(
    liste_pays,
    modele_dict,
    liste_deja_existante=None,
    liste_langues=[
        "français",
        "allemand",
        "russe",
        "arabe",
        "espagnol",
        "italien",
        "norvégien",
    ],
    blabla=2,  # 0 = Non, 1 = Pays, 2 = Pays x langues
    version=0,
):

    modele = modele_dict.get("modèle", "gemini-2.5-flash-lite")
    client = google.genai.Client(vertexai=False, api_key=clef_api_gemini)

    resultat = {} if liste_deja_existante is None else liste_deja_existante
    global appels_api_deja_faits

    for i in list(set(liste_pays)):

        if blabla > 0:
            print(
                textwrap.shorten(i.strip(" \n-="), width=50, placeholder="..."),
                end=" : " if blabla == 2 else " – ",
            )
            sys.stdout.flush()

        resultat[i] = resultat.get(i, {})
        for j in liste_langues:

            temps_debut = time.time()

            if j in resultat[i]:
                resultat[i][j] = resultat[i][j].strip(" .'\n")
                continue
            elif appels_api_deja_faits >= modele_dict.get("limite_appels_jour", 200):
                continue

            if blabla == 2:
                print(j, end=" ")
                sys.stdout.flush()

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

            time.sleep(
                max(
                    0,
                    60 / modele_dict.get("limite_appels_minute", 30)
                    - time.time()
                    + temps_debut,
                )
            )
            appels_api_deja_faits = appels_api_deja_faits + 1

        if blabla == 2:
            print("")

    return resultat


## 1.2 -- Fonction de traduction des langues -----------------------------------


### Fonction générique ---------------------------------------------------------


def creer_dictionnaire_langues(
    modele_dict,
    liste_deja_existante=None,
    liste_langues=[
        "français",
        "allemand",
        "russe",
        "arabe",
        "espagnol",
        "italien",
        "norvégien",
    ],
    blabla=True,
):

    modele = modele_dict.get("modèle", "gemini-2.5-flash-lite")
    client = google.genai.Client(vertexai=False, api_key=clef_api_gemini)
    resultat = {} if liste_deja_existante is None else liste_deja_existante
    global appels_api_deja_faits

    for i in list(set(liste_langues)):

        if i not in list(resultat.keys()) and appels_api_deja_faits < modele_dict.get(
            "limite_appels_jour", 200
        ):

            temps_debut = time.time()
            appels_api_deja_faits = appels_api_deja_faits + 1

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

                if blabla:
                    print(f"{i} : {resultat[i]}")
            except Exception as e:
                print(f"Erreur : {e}")
                continue

            time.sleep(
                max(
                    0,
                    60 / modele_dict.get("limite_appels_minute", 30)
                    + time.time()
                    - temps_debut,
                )
            )

    return resultat


### Fonction d'application -----------------------------------------------------


def maj_langues_dispo(modele: dict):

    print("Traduction des noms de langues...")
    exporter_fichier(
        objet=creer_dictionnaire_langues(
            modele_dict=modele,
            liste_deja_existante=dict_langues_dispo,
            blabla=True,
            liste_langues=liste_langues,
        ),
        direction_fichier=direction_donnees_traductions,
        nom_fichier="noms_langues_traduction.yaml",
        sort_keys=True,
    )


# 2 -- Application -------------------------------------------------------------


if __name__ == "__main__":

    for modele_utilise in modeles_google:

        # === Variables générales au script === #

        # for m in genai.list_models():
        #     print(m.name)

        # Récupération du jour
        date_du_jour = time.localtime()
        date_du_jour = (
            f"{date_du_jour.tm_year}-{date_du_jour.tm_mon}-{date_du_jour.tm_mday}"
        )

        # Gestion de la limite d'appels API quotidienne
        liste_appels_api_deja_faits = ouvrir_fichier(
            direction_fichier=direction_donnees_autres,
            nom_fichier="appels_api_par_jour.yaml",
            defaut={},
            afficher_erreur="Fichier YAML des appels API non trouvé.",
        )
        appels_api_deja_faits = int(
            liste_appels_api_deja_faits.get(date_du_jour, {}).get(
                modele_utilise["modèle"], 0
            )
        )

        # === Traduction des noms de langues === #

        maj_langues_dispo(modele=modele_utilise)
        time.sleep(1)

        # === Traduction de l'interface === #

        print("\n\n Traduction de l'interface graphique : \n")
        exporter_fichier(
            objet=creer_liste_pays_multilangue(
                liste_pays=list(phrases_interface.values()),
                modele_dict=modele_utilise,
                liste_deja_existante=ouvrir_fichier(  # Traduction déjà existante
                    direction_fichier=direction_donnees_traductions,
                    nom_fichier="phrases_interface_traduction.yaml",
                    defaut=None,
                    afficher_erreur="Fichiers YAML des traductions des phrases de l'interface non trouvé.",
                ),
                liste_langues=liste_langues,
                version=1,
                blabla=2,
            ),
            direction_fichier=direction_donnees_traductions,
            nom_fichier="phrases_interface_traduction.yaml",
            sort_keys=True,
        )

        time.sleep(1)

        # === Traduction des noms de pays ===

        # Construction de la liste de pays, régions, continents, ...

        ## Liste des continents
        liste_pays = ["World Map", "World"]

        for continent in liste_regions_monde.keys():
            liste_pays.append(continent)
            if continent == "Middle East":
                liste_pays.append(f"Map of the {continent}")
            else:
                liste_pays.append(f"Map of {continent}")

        ## Liste des pays regroupés
        liste_pays.extend(gr["categorie"] for gr in liste_pays_groupes.values())

        ## Liste des pays individuels
        liste_pays.extend(list(hierarchie_par_pays.keys()))

        # Traduction et export
        print("\n\n Traduction des noms de pays et régions : \n")
        exporter_fichier(
            objet=creer_liste_pays_multilangue(
                liste_pays=liste_pays,
                modele_dict=modele_utilise,
                liste_deja_existante=ouvrir_fichier(
                    direction_fichier=direction_donnees_traductions,
                    nom_fichier="noms_pays_traduction.yaml",
                    defaut=None,
                    afficher_erreur="Fichiers YAML des traductions des noms de pays non trouvé.",
                ),
                liste_langues=liste_langues,
                blabla=2,
            ),
            direction_fichier=direction_donnees_traductions,
            nom_fichier="noms_pays_traduction.yaml",
            sort_keys=True,
        )

        time.sleep(1)

        # === Mise à jour du fichiers des appel API ===

        if not date_du_jour in list(liste_appels_api_deja_faits.keys()):
            liste_appels_api_deja_faits[date_du_jour] = {}

        liste_appels_api_deja_faits[date_du_jour][
            modele_utilise["modèle"]
        ] = appels_api_deja_faits

        # Export
        exporter_fichier(
            objet=liste_appels_api_deja_faits,
            direction_fichier=direction_donnees_autres,
            nom_fichier="appels_api_par_jour.yaml",
            sort_keys=True,
        )

    print("\nTerminé ✅.")
