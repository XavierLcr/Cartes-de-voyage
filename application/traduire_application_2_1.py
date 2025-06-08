################################################################################
# Projet de cartes de voyage                                                   #
# Fichier de traduction des différents paramètres et non de pays               #
################################################################################

import google.generativeai as genai
import yaml
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constantes

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

        if blabla == 2:
            print(i, end=" : ")
        if blabla == 1:
            print(i, end=" - ")
        sys.stdout.flush()

        resultat[i] = resultat.get(i, {})
        for j in liste_langues:

            temps_debut = time.time()

            if j in resultat[i] or appels_api_deja_faits >= nb_max_requetes_par_jour:
                resultat[i][j] = resultat[i][j].strip(" .'\n")
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

            time.sleep(
                max(0, 60 / nb_max_requetes_par_minute - time.time() + temps_debut)
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
    blabla=2,  # 0 = Non, 1 = Pays, 2 = Pays x langues
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
            print(i, end=" - ")
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

                time.sleep(
                    max(0, 60 / nb_max_requetes_par_minute - time.time() + temps_debut)
                )

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

        if (
            i not in list(resultat.keys())
            and appels_api_deja_faits < nb_max_requetes_par_jour
        ):

            temps_debut = time.time()

            reponse_i = modele.generate_content(
                f"""Le nom d'une langue va t'être donné en français. Donne le nom de cette langue dans sa version propre. Par exemple anglais donne English et allemand donne Deutsch. Mets une majuscule quand cela est possible. Ne renvoie rien d'autre et surtout pas de ponctuation ou de prononciation pour les langues exotiques.
                \nLa langue est : '{i}'."""
            ).text
            reponse_i = reponse_i.strip(" .'")
            resultat[i] = reponse_i
            if blabla:
                print(f"{i} : {reponse_i}")

            time.sleep(
                max(0, 60 / nb_max_requetes_par_minute + time.time() - temps_debut)
            )
            appels_api_deja_faits = appels_api_deja_faits + 1

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
                print(
                    f"❌ Doublons détectés dans '{parametre}' > '{pays}' : {doublons}"
                )


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
    "danois",
    "espagnol",
    "esperanto",
    "estonien",
    "finnois",
    "français",
    "gallois",
    "géorgien",
    "grec",
    "hindi",
    "hongrois",
    "indonésien",
    "irlandais",
    "islandais",
    "italien",
    "japonais",
    "kazakh",
    "kurde",
    "latin",
    "letton",
    "lituanien",
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
            "modèle": "gemini-2.0-flash-lite",
            "limite_appels_minute": 28,
            "limite_appels_jour": 1500,
        },
        {
            "modèle": "gemini-2.0-flash",
            "limite_appels_minute": 14,
            "limite_appels_jour": 1500,
        },
        {
            "modèle": "gemini-1.5-flash",
            "limite_appels_minute": 14,
            "limite_appels_jour": 1500,
        },
    ]
    numero_modele = 0

    # Récupération du jour
    date_du_jour = time.localtime()
    date_du_jour = (
        f"{date_du_jour.tm_year}-{date_du_jour.tm_mon}-{date_du_jour.tm_mday}"
    )

    # YAML des régions
    try:
        with open(
            os.path.join(
                constantes.direction_donnees_application, "liste_pays_regions.yaml"
            ),
            "r",
            encoding="utf-8",
        ) as file:
            liste_regions = yaml.safe_load(file)

    except:
        liste_regions = {}
        print("Fichiers YAML des régions par pays non trouvé.")

    # YAML des pays regroupés
    try:
        with open(
            os.path.join(
                constantes.direction_donnees_application, "liste_pays_groupes.yaml"
            ),
            "r",
            encoding="utf-8",
        ) as file:
            liste_pays_groupes = yaml.safe_load(file)
    except:
        print("Fichiers YAML des regroupements de pays non trouvé.")
        liste_pays_groupes = {}

    # Traduction des nomms de pays
    try:
        with open(
            os.path.join(
                constantes.direction_donnees_application, "traductions_nom_pays.yaml"
            ),
            "r",
            encoding="utf-8",
        ) as file:
            pays_deja_traduits = yaml.safe_load(file)

    except:
        pays_deja_traduits = None

    # Traduction de l'interface PyQt
    try:
        with open(
            os.path.join(
                constantes.direction_donnees_application,
                "traductions_phrase_outil.yaml",
            ),
            "r",
            encoding="utf-8",
        ) as file:
            outil_deja_trad = yaml.safe_load(file)
    except:
        outil_deja_trad = None

    # Traduction des paramètres
    try:
        with open(
            os.path.join(
                constantes.direction_donnees_application, "traductions_parametres.yaml"
            ),
            "r",
            encoding="utf-8",
        ) as file:
            parametres_deja_trad = yaml.safe_load(file)

    except:
        parametres_deja_trad = None

    # Traduction des langues
    try:
        with open(
            os.path.join(
                constantes.direction_donnees_application,
                "traductions_noms_langues.yaml",
            ),
            "r",
            encoding="utf-8",
        ) as file:
            langues_deja_traduites = yaml.safe_load(file)

    except:
        langues_deja_traduites = None

    # Pour que la limite API arrête de crasher
    try:
        with open(
            os.path.join(
                constantes.direction_donnees_autres, "appels_api_par_jour.yaml"
            ),
            "r",
            encoding="utf-8",
        ) as file:
            liste_appels_api_deja_faits = yaml.safe_load(file)
            appels_api_deja_faits = liste_appels_api_deja_faits.get(
                date_du_jour, {}
            ).get(liste_modeles[numero_modele]["modèle"], 0)
            appels_api_deja_faits = int(appels_api_deja_faits)

    except:
        appels_api_deja_faits = 0
        liste_appels_api_deja_faits = {}

    # YAML des teintes
    try:
        with open(
            os.path.join(
                constantes.direction_donnees_application, "teintes_couleurs.yaml"
            ),
            "r",
            encoding="utf-8",
        ) as file:
            teintes_couleurs = yaml.safe_load(file)
    except:
        teintes_couleurs = {}

    # YAML des thèmes
    try:
        with open(
            os.path.join(
                constantes.direction_donnees_application, "themes_cartes.yaml"
            ),
            "r",
            encoding="utf-8",
        ) as file:
            themes_cartes = yaml.safe_load(file)
    except:
        themes_cartes = {}

    ## Pays
    # Liste des pays
    liste_pays = list(liste_regions.keys())
    liste_pays.append("World Map")
    liste_pays.append("World")

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
        blabla=2,
    )

    print("\nThèmes :")

    parametres_traduits = creer_liste_parametres_multilangue(
        liste_parametres=list(themes_cartes.keys()),
        liste_deja_existante=parametres_traduits,
        nom_bouton="themes_cartes",
        modele_dict=liste_modeles[numero_modele],
        liste_langues=liste_langues,
        blabla=2,
    )

    print("\n Teintes de couleurs :")

    parametres_traduits = creer_liste_parametres_multilangue(
        liste_parametres=list(teintes_couleurs.keys()),
        liste_deja_existante=parametres_traduits,
        nom_bouton="teintes_couleurs",
        modele_dict=liste_modeles[numero_modele],
        liste_langues=liste_langues,
        blabla=2,
    )

    with open(
        os.path.join(
            constantes.direction_donnees_application, "traductions_parametres.yaml"
        ),
        "w",
        encoding="utf-8",
    ) as f:
        yaml.dump(parametres_traduits, f, allow_unicode=True, default_flow_style=False)

    print("\n\n Traduction des noms de langues : \n")

    langues_deja_traduites = creer_dictionnaire_langues(
        modele_dict=liste_modeles[numero_modele],
        liste_deja_existante=langues_deja_traduites,
        blabla=True,
        liste_langues=liste_langues,
    )

    with open(
        os.path.join(
            constantes.direction_donnees_application, "traductions_noms_langues.yaml"
        ),
        "w",
        encoding="utf-8",
    ) as f:
        yaml.dump(
            langues_deja_traduites, f, allow_unicode=True, default_flow_style=False
        )

    verifier_doublons(parametres_traduits)

    print("\n\n Traduction de l'interface graphique : \n")

    ## PyQt - Interfaces
    phrases_a_traduire = [
        "Afrique",
        "Amérique",
        "Asie",
        "Aucun lieu n'a été coché",
        "Autres régions du monde",
        "Carte du monde",
        "Cartes de voyage",
        "Cartes des pays visités",
        "Cartes des régions visitées",
        "Cartes à publier",
        "Chargement de l'application",
        "Chargement des fichiers YAML",
        "Charger la liste des départements visités",
        "Charger la liste des régions visitées",
        "Charger un fichier YAML",
        "Choisir le dossier de stockage des cartes",
        "Cinq cartes",
        "Couleur",
        "Couleur du fond de la carte",
        "Création de la liste des pays visités",
        "Création des cartes",
        "Créer les graphes !",
        "Dix cartes",
        "Début de l'opération.",
        "Départements",
        "Également publier les cartes pour lesquelles la granularité souhaitée n'est pas disponible",
        "Europe",
        "Faible",
        "Format",
        "Granularité des cartes",
        "Il faut choisir un répertoire de destination.",
        "Langue",
        "Pour un pays donné, si des départements sont cochés, ils sont prioritaires sur les régions cochées. Dans ce cas, la liste des régions visitées est automatiquement reconstituée à partir de la liste des départements. Il n'est donc plus nécessaire de cocher les régions visitées (les régions peuvent rester cochées mais ne seront pas prises en compte)",
        "Les cartes ont été créées avec succès !",
        "Liste des lieux visités",
        "Moyen-Orient",
        "Nombre maximal de versions d'une carte",
        "Nombre de versions conservées pour chaque carte",
        "ou charger manuellement un fichier YAML contenant la liste des lieux visités",
        "Outil de création de cartes",
        "Paramètres",
        "Paramètres de publication des cartes",
        "Paramètres de l'individu",
        "Paramètres esthétiques",
        "Pas de limite",
        "Pays les plus visités",
        "Pays non visités",
        "Pays visités",
        "Problème.",
        "Publier les cartes !",
        "Qualité de l'image",
        "Quinze cartes",
        "Régions",
        "Réinitialiser l'interface",
        "Sauvegarder mes paramètres",
        "Selon les départements visités",
        "Selon les régions visitées",
        "Sélection des lieux visités",
        "Sélectionner un dossier",
        "Supprimer ce profil",
        "Thème",
        "Réinitialiser l'application",
        "Utiliser le style dans l'application",
        "Élevée",
    ]

    phrases_pays_langues = creer_liste_pays_multilangue(
        liste_pays=phrases_a_traduire,
        modele_dict=liste_modeles[numero_modele],
        liste_deja_existante=outil_deja_trad,
        liste_langues=liste_langues,
        version=1,
        blabla=2,
    )

    with open(
        os.path.join(
            constantes.direction_donnees_application, "traductions_phrase_outil.yaml"
        ),
        "w",
        encoding="utf-8",
    ) as f:
        yaml.dump(phrases_pays_langues, f, allow_unicode=True, default_flow_style=False)

    print("\n\n Traduction des noms de pays et régions : \n")

    # Nom des pays dans les cartes sauvegardées
    dict_pays_langues = creer_liste_pays_multilangue(
        liste_pays=liste_pays,
        modele_dict=liste_modeles[numero_modele],
        liste_deja_existante=pays_deja_traduits,
        liste_langues=liste_langues,
        blabla=2,
    )

    with open(
        os.path.join(
            constantes.direction_donnees_application, "traductions_nom_pays.yaml"
        ),
        "w",
        encoding="utf-8",
    ) as f:
        yaml.dump(dict_pays_langues, f, allow_unicode=True, default_flow_style=False)

    # Mise à jour des appels API faits
    if not date_du_jour in list(liste_appels_api_deja_faits.keys()):
        liste_appels_api_deja_faits[date_du_jour] = {}
    liste_appels_api_deja_faits[date_du_jour][
        liste_modeles[numero_modele]["modèle"]
    ] = appels_api_deja_faits

    with open(
        os.path.join(constantes.direction_donnees_autres, "appels_api_par_jour.yaml"),
        "w",
        encoding="utf-8",
    ) as f:
        yaml.dump(
            liste_appels_api_deja_faits, f, allow_unicode=True, default_flow_style=False
        )

    print("\nTerminé ✅.")
