################################################################################
# Projet de cartes de voyage                                                   #
# 2.1 – Fichier de traduction des différents paramètres et non de pays         #
################################################################################

import google.generativeai as genai
import os, sys, time, textwrap

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

            resultat[i][j] = modele.generate_content(
                f"Traduis le nom du pays qui va t'être donné en {j} : {i}. Ne donne que la traduction, rien d'autre. N'inclus en aucun cas la prononciation."
                if version == 0
                else f"Traduis la phrase qui va t'être donnée en {j} : {i}. Ne donne que la traduction, rien d'autre. N'inclus en aucun cas la prononciation."
            ).text.strip("\n .'")

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
    global appels_api_deja_faits

    if liste_deja_existante is None:
        resultat = {}
        liste_deja_existante = {}
    else:
        resultat = liste_deja_existante.get(nom_bouton, {})

    for i in list(set(liste_langues)):

        if blabla == 2:
            print(i, end=" : ")
        if blabla == 1:
            print(i, end=" – ")
        sys.stdout.flush()

        resultat[i] = resultat.get(i, {})
        for j in liste_parametres:

            temps_debut = time.time()
            if j not in list(resultat[i].keys()) and appels_api_deja_faits < modele_dict.get(
                "limite_appels_jour", 200
            ):

                if blabla == 2:
                    print(j, end=" ")
                    sys.stdout.flush()

                if i == "français":
                    resultat[i][j] = j
                    continue

                resultat[i][j] = modele.generate_content(
                    f"Traduis le mot ou l'expression suivante en {i} : '{j}'. Ne donne que la traduction, strictement rien d'autre - et aucune ponctuation. Le mot à traduire est à l'origine en français. N'oublie pas la majuscule en début d'expression quand c'est possible."
                ).text.strip(" .'\n")

                time.sleep(
                    max(
                        0,
                        60 / modele_dict.get("limite_appels_minute", 30)
                        - time.time()
                        + temps_debut,
                    )
                )
                appels_api_deja_faits = appels_api_deja_faits + 1

            elif j not in list(resultat[i].keys()):
                continue
            else:
                resultat[i][j] = resultat[i][j].strip(" .'\n")

        if blabla == 2:
            print("")

    if blabla == 1:
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
                resultat[i] = modele.generate_content(
                    f"""Le nom d'une langue va t'être donné en français. Donne le nom de cette langue dans sa version propre. Par exemple anglais donne English et allemand donne Deutsch. Mets une majuscule quand cela est possible. Ne renvoie rien d'autre et surtout pas de ponctuation ou de prononciation pour les langues exotiques.
                \nLa langue est : '{i}'."""
                ).text.strip(" .'\n")

                if blabla:
                    print(f"{i} : {resultat[i]}")
            except:
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


def verifier_doublons(data):
    for parametre, sous_dico in data.items():
        for pays, valeurs in sous_dico.items():
            seen = set()
            doublons = set()
            for cle, val in valeurs.items():
                doublons.add(val) if val in seen else seen.add(val)
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

    for modele_utilise in [
        {
            "modèle": "gemini-2.0-flash-lite",
            "limite_appels_minute": 28,
            "limite_appels_jour": 199,
        },
        {
            "modèle": "gemini-2.5-flash-lite-preview-06-17",
            "limite_appels_minute": 14,
            "limite_appels_jour": 999,
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
    ]:

        # === Variables générales au script ===

        # Clef API
        genai.configure(api_key=clef_api_gemini)

        # Choix du modèle de Google Gemini

        # Récupération du jour
        date_du_jour = time.localtime()
        date_du_jour = f"{date_du_jour.tm_year}-{date_du_jour.tm_mon}-{date_du_jour.tm_mday}"

        # Gestion de la limite d'appels API quotidienne
        liste_appels_api_deja_faits = ouvrir_fichier(
            direction_fichier=constantes.direction_donnees_autres,
            nom_fichier="appels_api_par_jour.yaml",
            defaut={},
            afficher_erreur="Fichier YAML des appels API non trouvé.",
        )
        appels_api_deja_faits = int(
            liste_appels_api_deja_faits.get(date_du_jour, {}).get(modele_utilise["modèle"], 0)
        )

        # === Traduction des paramètres ===

        # Ouverture des fichiers

        ## Traduction déjà existante des paramètres
        parametres_deja_trad = ouvrir_fichier(
            direction_fichier=constantes.direction_donnees_application,
            nom_fichier="parametres_cartes_traduction.yaml",
            defaut=None,
            afficher_erreur="Fichier YAML des traductions des paramètres non trouvé.",
        )

        ## YAML des teintes
        teintes_couleurs = ouvrir_fichier(
            direction_fichier=constantes.direction_donnees_application,
            nom_fichier="cartes_teintes.yaml",
            defaut={},
        )

        ## YAML des thèmes
        themes_cartes = ouvrir_fichier(
            direction_fichier=constantes.direction_donnees_application,
            nom_fichier="cartes_ambiances.yaml",
            defaut={},
        )

        # Traductions
        print("\n\n Traduction des paramètres : \n")
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
            modele_dict=modele_utilise,
            liste_langues=liste_langues,
            blabla=1,
        )

        parametres_traduits = creer_liste_parametres_multilangue(
            liste_parametres=list(themes_cartes.keys()),
            liste_deja_existante=parametres_traduits,
            nom_bouton="themes_cartes",
            modele_dict=modele_utilise,
            liste_langues=liste_langues,
            blabla=1,
        )

        parametres_traduits = creer_liste_parametres_multilangue(
            liste_parametres=list(teintes_couleurs.keys()),
            liste_deja_existante=parametres_traduits,
            nom_bouton="teintes_couleurs",
            modele_dict=modele_utilise,
            liste_langues=liste_langues,
            blabla=1,
        )

        # Export
        verifier_doublons(parametres_traduits)  # Vérification des doublons
        exporter_fichier(
            objet=parametres_traduits,
            direction_fichier=constantes.direction_donnees_application,
            nom_fichier="parametres_cartes_traduction.yaml",
            sort_keys=True,
        )

        time.sleep(1)

        # === Traduction des noms de langues ===

        print("\n\n Traduction des noms de langues : \n")
        exporter_fichier(
            objet=creer_dictionnaire_langues(
                modele_dict=modele_utilise,
                liste_deja_existante=ouvrir_fichier(
                    direction_fichier=constantes.direction_donnees_application,
                    nom_fichier="noms_langues_traduction.yaml",
                    defaut=None,
                    afficher_erreur="Fichier YAML des traductions des langues non trouvé.",
                ),
                blabla=True,
                liste_langues=liste_langues,
            ),
            direction_fichier=constantes.direction_donnees_application,
            nom_fichier="noms_langues_traduction.yaml",
            sort_keys=True,
        )

        time.sleep(1)

        # === Traduction de l'interface ===

        print("\n\n Traduction de l'interface graphique : \n")
        exporter_fichier(
            objet=creer_liste_pays_multilangue(
                liste_pays=list(
                    ouvrir_fichier(  # Phrases à traduire
                        direction_fichier=constantes.direction_donnees_application,
                        nom_fichier="phrases_interface.yaml",
                        defaut={},
                        afficher_erreur="Fichiers YAML des phrases de l'interface non trouvé.",
                    ).values()
                ),
                modele_dict=modele_utilise,
                liste_deja_existante=ouvrir_fichier(  # Traduction déjà existante
                    direction_fichier=constantes.direction_donnees_application,
                    nom_fichier="phrases_interface_traduction.yaml",
                    defaut=None,
                    afficher_erreur="Fichiers YAML des traductions des phrases de l'interface non trouvé.",
                ),
                liste_langues=liste_langues,
                version=1,
                blabla=1,
            ),
            direction_fichier=constantes.direction_donnees_application,
            nom_fichier="phrases_interface_traduction.yaml",
            sort_keys=True,
        )

        time.sleep(1)

        # === Traduction des noms de pays ===

        # Construction de la liste de pays, régions, continents, ...

        ## Liste des continents
        liste_pays = list(
            ouvrir_fichier(
                direction_fichier=constantes.direction_donnees_application,
                nom_fichier="continents.yaml",
                defaut={},
                afficher_erreur="Fichiers YAML des régions par pays non trouvé.",
            ).keys()
        ) + ["World Map", "World"]

        for continent in liste_pays[:]:
            liste_pays.append(continent)
            if continent == "Middle East":
                liste_pays.append(f"Map of the {continent}")
            else:
                liste_pays.append(f"Map of {continent}")

        ## Liste des pays regroupés
        liste_pays.extend(
            gr["categorie"]
            for gr in ouvrir_fichier(
                direction_fichier=constantes.direction_donnees_application,
                nom_fichier="cartes_pays_regroupements.yaml",
                defaut={},
                afficher_erreur="Fichiers YAML des regroupements de pays non trouvé.",
            ).values()
        )

        ## Liste des pays individuels
        liste_pays.extend(
            list(
                ouvrir_fichier(
                    direction_fichier=constantes.direction_donnees_application,
                    nom_fichier="regions_par_pays.yaml",
                    defaut={},
                    afficher_erreur="Fichiers YAML des regroupements de pays non trouvé.",
                ).keys()
            )
        )

        # Traduction et export
        print("\n\n Traduction des noms de pays et régions : \n")
        exporter_fichier(
            objet=creer_liste_pays_multilangue(
                liste_pays=liste_pays,
                modele_dict=modele_utilise,
                liste_deja_existante=ouvrir_fichier(
                    direction_fichier=constantes.direction_donnees_application,
                    nom_fichier="noms_pays_traduction.yaml",
                    defaut=None,
                    afficher_erreur="Fichiers YAML des traductions des noms de pays non trouvé.",
                ),
                liste_langues=liste_langues,
                blabla=1,
            ),
            direction_fichier=constantes.direction_donnees_application,
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
            direction_fichier=constantes.direction_donnees_autres,
            nom_fichier="appels_api_par_jour.yaml",
            sort_keys=True,
        )

    print("\nTerminé ✅.")
