################################################################################
# Projet de cartes de voyage                                                   #
# 2.1 – Fichier de traduction des différents paramètres et non de pays         #
################################################################################

import google.generativeai as genai
import time
import os
import sys
import textwrap

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constantes
from application.fonctions_utiles_2_0 import ouvrir_fichier, exporter_fichier

from clefs_et_mots_de_passe import clef_api_gemini


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

    modele = genai.GenerativeModel(modele_dict.get("modèle", "gemini-2.0-flash-lite"))
    nb_max_requetes_par_minute = modele_dict.get("limite_appels_minute", 30)
    nb_max_requetes_par_jour = modele_dict.get("limite_appels_jour", 200)
    global appels_api_deja_faits

    liste_pays = list(set(liste_pays))
    liste_pays.sort()

    if liste_deja_existante is not None:
        resultat = liste_deja_existante
    else:
        resultat = {}
    for i in liste_pays:

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
            elif appels_api_deja_faits >= nb_max_requetes_par_jour:
                continue

            if blabla == 2:
                print(j, end=" ")
                sys.stdout.flush()

            if (j == "anglais" and version == 0) or (j == "français" and version == 1):
                resultat[i][j] = i
                continue

            if version == 0:
                reponse = modele.generate_content(
                    f"Traduis le nom du pays qui va t'être donné en {j} : {i}. Ne donne que la traduction, rien d'autre. N'inclus en aucun cas la prononciation."
                ).text

            else:
                reponse = modele.generate_content(
                    f"Traduis la phrase qui va t'être donnée en {j} : {i}. Ne donne que la traduction, rien d'autre. N'inclus en aucun cas la prononciation."
                ).text

            resultat[i][j] = reponse.strip("\n .'")

            time.sleep(max(0, 60 / nb_max_requetes_par_minute - time.time() + temps_debut))
            appels_api_deja_faits = appels_api_deja_faits + 1

        if blabla == 2:
            print("")

    return resultat


def creer_liste_parametres_multilangue(
    liste_parametres,
    nom_bouton,
    modele_dict,
    liste_deja_existante=None,
    liste_langues=[
        "français",
        "anglais",
        "allemand",
    ],
    blabla=1,  # 0 = Non, 1 = Pays, 2 = Pays x langues
):

    modele = genai.GenerativeModel(modele_dict.get("modèle", "gemini-2.0-flash-lite"))
    nb_max_requetes_par_minute = modele_dict.get("limite_appels_minute", 30)
    nb_max_requetes_par_jour = modele_dict.get("limite_appels_jour", 200)
    global appels_api_deja_faits

    if liste_deja_existante is None:
        resultat = {}
        liste_deja_existante = {}
    else:
        resultat = liste_deja_existante.get(nom_bouton, {})

    for i in liste_langues:

        if blabla == 2:
            print(i, end=" : ")
        if blabla == 1:
            print(i, end=" – ")
        sys.stdout.flush()

        if i not in list(resultat.keys()):
            resultat[i] = {}

        for j in liste_parametres:

            temps_debut = time.time()

            if (
                j not in list(resultat[i].keys())
                and appels_api_deja_faits < nb_max_requetes_par_jour
            ):

                if blabla == 2:
                    print(j, end=" ")
                    sys.stdout.flush()

                if i == "français":
                    resultat[i][j] = j
                    continue

                reponse_ij = modele.generate_content(
                    f"Traduis le mot ou l'expression suivante en {i} : '{j}'. Ne donne que la traduction, strictement rien d'autre - et aucune ponctuation. Le mot à traduire est à l'origine en français. N'oublie pas la majuscule en début d'expression quand c'est possible."
                ).text

                time.sleep(max(0, 60 / nb_max_requetes_par_minute - time.time() + temps_debut))

                appels_api_deja_faits = appels_api_deja_faits + 1

            elif j not in list(resultat[i].keys()):
                continue
            else:
                reponse_ij = resultat[i][j]

            resultat[i][j] = reponse_ij.strip(" .'\n")

        if blabla == 2:
            print("")

    liste_deja_existante[nom_bouton] = resultat
    return liste_deja_existante


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

    modele = genai.GenerativeModel(modele_dict.get("modèle", "gemini-2.0-flash-lite"))
    nb_max_requetes_par_minute = modele_dict.get("limite_appels_minute", 30)
    nb_max_requetes_par_jour = modele_dict.get("limite_appels_jour", 200)
    global appels_api_deja_faits

    liste_langues.sort()

    if liste_deja_existante is None:
        resultat = {}
    else:
        resultat = liste_deja_existante

    for i in liste_langues:

        if i not in list(resultat.keys()) and appels_api_deja_faits < nb_max_requetes_par_jour:

            temps_debut = time.time()
            appels_api_deja_faits = appels_api_deja_faits + 1

            # Traduction
            try:
                reponse_i = modele.generate_content(
                    f"""Le nom d'une langue va t'être donné en français. Donne le nom de cette langue dans sa version propre. Par exemple anglais donne English et allemand donne Deutsch. Mets une majuscule quand cela est possible. Ne renvoie rien d'autre et surtout pas de ponctuation ou de prononciation pour les langues exotiques.
                \nLa langue est : '{i}'."""
                ).text
            except:
                continue

            reponse_i = reponse_i.strip(" .'\n")
            resultat[i] = reponse_i
            if blabla:
                print(f"{i} : {reponse_i}")

            time.sleep(max(0, 60 / nb_max_requetes_par_minute + time.time() - temps_debut))

    return resultat


def verifier_doublons(data):
    for parametre, sous_dico in data.items():
        for pays, valeurs in sous_dico.items():
            seen = set()
            doublons = set()
            for cle, val in valeurs.items():
                if val in seen:
                    doublons.add(val)
                else:
                    seen.add(val)
            if doublons:
                print(f"❌ Doublons détectés dans '{parametre}' > '{pays}' : {doublons}")


liste_langues = [
    "afrikaans",
    "albanais",
    "allemand",
    "anglais",
    "arabe",
    "arménien",
    "basque",
    "bengali",
    "birman",
    "breton",
    "bulgare",
    "catalan",
    "coréen",
    "corse",
    "danois",
    "espagnol",
    "esperanto",
    "estonien",
    "finnois",
    "français",
    "gallois",
    "géorgien",
    "grec",
    "grec ancien",
    "hindi",
    "hongrois",
    "indonésien",
    "irlandais",
    "islandais",
    "italien",
    "japonais",
    "kazakh",
    "kirghize",
    "kurde",
    "latin",
    "letton",
    "lituanien",
    "luxembourgeois",
    "macédonien",
    "malais",
    "malgache",
    "maltais",
    "mandarin standard",
    "mongol",
    "népalais",
    "norvégien",
    "néerlandais",
    "ourdou",
    "ouzbek",
    "pachto",
    "persan",
    "polonais",
    "portugais",
    "roumain",
    "russe",
    "serbo-croate",
    "slovaque",
    "slovène",
    "suédois",
    "swahili",
    "tadjik",
    "tamoul",
    "thaï",
    "tibétain",
    "tchèque",
    "turc",
    "turkmène",
    "vietnamien",
    "ukrainien",
    "zoulou",
]

if __name__ == "__main__":

    # Clef API
    genai.configure(api_key=clef_api_gemini)

    # Choix du modèle de Google Gemini
    liste_modeles = [
        {
            "modèle": "gemini-2.5-flash-lite-preview-06-17",
            "limite_appels_minute": 14,
            "limite_appels_jour": 999,
        },
        {
            "modèle": "gemini-2.0-flash-lite",
            "limite_appels_minute": 28,
            "limite_appels_jour": 199,
        },
        {
            "modèle": "gemini-2.0-flash",
            "limite_appels_minute": 14,
            "limite_appels_jour": 199,
        },
        {
            "modèle": "gemini-2.5-flash",
            "limite_appels_minute": 9,
            "limite_appels_jour": 249,
        },
    ]
    numero_modele = 0

    # Récupération du jour
    date_du_jour = time.localtime()
    date_du_jour = f"{date_du_jour.tm_year}-{date_du_jour.tm_mon}-{date_du_jour.tm_mday}"

    # YAML des régions
    liste_regions = ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="continents.yaml",
        defaut={},
        afficher_erreur="Fichiers YAML des régions par pays non trouvé.",
    )

    # YAML des pays regroupés
    liste_pays_groupes = ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="cartes_pays_regroupements.yaml",
        defaut={},
        afficher_erreur="Fichiers YAML des regroupements de pays non trouvé.",
    )

    # Traduction des noms de pays
    pays_deja_traduits = ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="noms_pays_traduction.yaml",
        defaut=None,
        afficher_erreur="Fichiers YAML des traductions des noms de pays non trouvé.",
    )

    # Phrases de l'interface
    phrases_a_traduire = ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="phrases_interface.yaml",
        defaut={},
        afficher_erreur="Fichiers YAML des phrases de l'interface non trouvé.",
    )

    # Traduction de l'interface PyQt
    outil_deja_trad = ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="phrases_interface_traduction.yaml",
        defaut=None,
        afficher_erreur="Fichiers YAML des traductions des phrases de l'interface non trouvé.",
    )

    # Traduction des paramètres
    parametres_deja_trad = ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="parametres_cartes_traduction.yaml",
        defaut=None,
        afficher_erreur="Fichier YAML des traductions des paramètres non trouvé.",
    )

    # Traduction des langues
    langues_deja_traduites = ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="noms_langues_traduction.yaml",
        defaut=None,
        afficher_erreur="Fichier YAML des traductions des langues non trouvé.",
    )

    # Gestion de la limite d'appels API quotidienne
    liste_appels_api_deja_faits = ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_autres,
        nom_fichier="appels_api_par_jour.yaml",
        defaut={},
        afficher_erreur="Fichier YAML des appels API non trouvé.",
    )
    appels_api_deja_faits = int(
        liste_appels_api_deja_faits.get(date_du_jour, {}).get(
            liste_modeles[numero_modele]["modèle"], 0
        )
    )

    # YAML des teintes
    teintes_couleurs = ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="cartes_teintes.yaml",
        defaut={},
    )

    # YAML des thèmes
    themes_cartes = ouvrir_fichier(
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="cartes_ambiances.yaml",
        defaut={},
    )

    ## Pays
    # Liste des pays
    liste_pays = list(liste_regions.keys()) + ["World Map", "World"]

    # Ajout des continents et leurs cartes
    continents = [
        "Europe",
        "Africa",
        "Asia",
        "Oceania",
        "America",
        "South America",
        "North America",
        "Middle East",
    ]

    for continent in continents:
        liste_pays.append(continent)
        if continent == "Middle East":
            liste_pays.append(f"Map of the {continent}")
        else:
            liste_pays.append(f"Map of {continent}")

    for gr_pays in liste_pays_groupes.values():
        liste_pays.append(gr_pays["categorie"])

    print("\n\n Traduction des paramètres : \n")
    print("Granularité :")
    parametres_traduits = creer_liste_parametres_multilangue(
        liste_parametres=[
            "Pays",
            "Région",
            "Département",
            "Amusant",
            "Régions",
            "Départements",
        ],
        liste_deja_existante=parametres_deja_trad,
        nom_bouton="granularite",
        modele_dict=liste_modeles[numero_modele],
        liste_langues=liste_langues,
        blabla=1,
    )

    print("\nThèmes :")
    parametres_traduits = creer_liste_parametres_multilangue(
        liste_parametres=list(themes_cartes.keys()),
        liste_deja_existante=parametres_traduits,
        nom_bouton="themes_cartes",
        modele_dict=liste_modeles[numero_modele],
        liste_langues=liste_langues,
        blabla=1,
    )

    print("\n Teintes de couleurs :")
    parametres_traduits = creer_liste_parametres_multilangue(
        liste_parametres=list(teintes_couleurs.keys()),
        liste_deja_existante=parametres_traduits,
        nom_bouton="teintes_couleurs",
        modele_dict=liste_modeles[numero_modele],
        liste_langues=liste_langues,
        blabla=1,
    )

    # Export
    exporter_fichier(
        objet=parametres_traduits,
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="parametres_cartes_traduction.yaml",
        sort_keys=True,
    )

    print("\n\n Traduction des noms de langues : \n")
    langues_deja_traduites = creer_dictionnaire_langues(
        modele_dict=liste_modeles[numero_modele],
        liste_deja_existante=langues_deja_traduites,
        blabla=True,
        liste_langues=liste_langues,
    )

    # Export et vérification des doublons
    exporter_fichier(
        objet=langues_deja_traduites,
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="noms_langues_traduction.yaml",
        sort_keys=True,
    )
    verifier_doublons(parametres_traduits)

    ## PyQt - Interfaces
    print("\n\n Traduction de l'interface graphique : \n")
    phrases_pays_langues = creer_liste_pays_multilangue(
        liste_pays=list(phrases_a_traduire.values()),
        modele_dict=liste_modeles[numero_modele],
        liste_deja_existante=outil_deja_trad,
        liste_langues=liste_langues,
        version=1,
        blabla=1,
    )

    # Export
    exporter_fichier(
        objet=phrases_pays_langues,
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="phrases_interface_traduction.yaml",
        sort_keys=True,
    )

    # Nom des pays dans les cartes sauvegardées
    print("\n\n Traduction des noms de pays et régions : \n")
    dict_pays_langues = creer_liste_pays_multilangue(
        liste_pays=liste_pays,
        modele_dict=liste_modeles[numero_modele],
        liste_deja_existante=pays_deja_traduits,
        liste_langues=liste_langues,
        blabla=1,
    )

    # Export
    exporter_fichier(
        objet=dict_pays_langues,
        direction_fichier=constantes.direction_donnees_application,
        nom_fichier="noms_pays_traduction.yaml",
        sort_keys=True,
    )

    # Mise à jour des appels API faits
    if not date_du_jour in list(liste_appels_api_deja_faits.keys()):
        liste_appels_api_deja_faits[date_du_jour] = {}
    liste_appels_api_deja_faits[date_du_jour][
        liste_modeles[numero_modele]["modèle"]
    ] = appels_api_deja_faits

    exporter_fichier(
        objet=liste_appels_api_deja_faits,
        direction_fichier=constantes.direction_donnees_autres,
        nom_fichier="appels_api_par_jour.yaml",
        sort_keys=True,
    )

    print("\nTerminé ✅.")
