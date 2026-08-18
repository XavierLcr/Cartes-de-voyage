################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_2_application/2_2_1_traductions/                           #
# 2.2.1.1 – Fichier de traduction des paramètres                               #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys, time
import google.genai

sys.path.append(os.getcwd())

from constantes import (
    direction_donnees_traductions,
    direction_donnees_autres,
    dictionnaire_arriere_plans,
    liste_ambiances,
    liste_couleurs,
)
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_fichier,
    exporter_fichier,
    formater_temps_actuel,
    sleep_n_fois,
)

from clefs_et_mots_de_passe import clef_api_gemini, modeles_google, liste_langues

# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de création du prompt ---------------------------------------


def prompt(langue: str, texte: str):

    return f"""
    Traduis ce libellé d'interface utilisateur du français vers {langue} :

    "{texte}"

    Règles impératives :
    - Retourne uniquement le libellé traduit, sans explication ni commentaire.
    - N'ajoute aucune ponctuation.
    - Ne mets pas de guillemets.
    - Le texte source est toujours en français.
    - Utilise une formulation naturelle et idiomatique pour une interface logicielle.
    - Privilégie une traduction courte et concise, adaptée à un menu déroulant,
    un paramètre ou une statistique.
    - Conserve exactement le sens du libellé.
    - Commence par une majuscule lorsque cela est naturel dans la langue cible.
    - Si plusieurs traductions sont possibles, choisis celle qui est la plus
    naturelle dans une application de voyages.

    Réponds uniquement avec la traduction finale.
    """


## 1.2 -- Fonction de traduction d'un lot de paramètres ------------------------


def creer_liste_parametres_multilangue(
    liste_parametres: list,
    nom_bouton: str,
    modele_dict: dict,
    liste_deja_existante: dict,
    liste_langues: list,
    blabla: int,
):

    global api_jour_modele
    modele = modele_dict.get("modèle", "gemini-2.5-flash-lite")
    limite_api = modele_dict.get("limite_appels_jour", 200)
    limite_api_minute = modele_dict.get("limite_appels_minute", 30)
    resultat = (liste_deja_existante or {}).get(nom_bouton, {})

    if blabla >= 1:
        print(nom_bouton)

    for i in sorted(liste_langues):

        client = google.genai.Client(vertexai=False, api_key=clef_api_gemini)

        if blabla >= 2:
            print("    ", i)

        resultat[i] = resultat.get(i, {})
        for j in liste_parametres:

            temps_debut = time.time()
            if j not in list(resultat[i].keys()) and api_jour_modele < limite_api:

                if blabla >= 3:
                    print("    • ", j)

                if i == "français":
                    resultat[i][j] = j
                    continue

                try:
                    resultat[i][j] = client.models.generate_content(
                        model=modele, contents=prompt(langue=i, texte=j)
                    ).text.strip(" .'\n")
                except Exception as e:
                    print(f"Erreur : {e}")
                    pass

                # Attente si nécessaire
                sleep_n_fois(n=limite_api_minute, time_ref=temps_debut)

                # Mise à jour du nombre d'appels
                api_jour_modele = api_jour_modele + 1

            elif j not in list(resultat[i].keys()):
                continue
            else:
                try:
                    resultat[i][j] = resultat[i][j].strip(" .'\n")
                except:
                    pass

    if blabla >= 1:
        print("")

    liste_deja_existante[nom_bouton] = resultat
    return liste_deja_existante


## 1.2 -- Fonction de vérification de l'existance de doublons de paramètres ----


def verifier_doublons(data):

    for parametre, sous_dico in data.items():
        for pays, valeurs in sous_dico.items():
            seen = set()
            doublons = set()
            for cle, val in valeurs.items():
                doublons.add(val) if val in seen else seen.add(val)
            if doublons:
                print(
                    f"❌ Doublons détectés dans '{parametre}' > '{pays}' : {doublons}"
                )


# 2 -- Lecture des données -----------------------------------------------------


date_jour = formater_temps_actuel(n=2)


## 2.1 -- Appels API déjà effectués --------------------------------------------


api_dict = ouvrir_fichier(
    direction_fichier=direction_donnees_autres,
    nom_fichier="appels_api_par_jour.yaml",
    defaut={},
    afficher_erreur="Fichier YAML des appels API non trouvé.",
)


## 2.2 -- Fichier de paramètres déjà traduits ----------------------------------


param_traduits = ouvrir_fichier(
    direction_fichier=direction_donnees_traductions,
    nom_fichier="parametres_cartes_traduction.yaml",
    defaut={},
    afficher_erreur="Fichier YAML des traductions des paramètres non trouvé.",
)


# 3 -- Traductions -------------------------------------------------------------


for modele in modeles_google:

    # Appel API
    api_jour_modele = int(api_dict.get(date_jour, {}).get(modele["modèle"], 0))

    # Granularité
    param_traduits = creer_liste_parametres_multilangue(
        liste_parametres=[
            "Pays",
            "Région",
            "Département",
            "Amusant",
            "Régions",
            "Départements",
        ],
        ## Traduction déjà existante des paramètres
        liste_deja_existante=param_traduits,
        nom_bouton="granularite",
        modele_dict=modele,
        liste_langues=liste_langues,
        blabla=1,
    )

    # Ambiances
    param_traduits = creer_liste_parametres_multilangue(
        liste_parametres=list(liste_ambiances.keys()),
        liste_deja_existante=param_traduits,
        nom_bouton="themes_cartes",
        modele_dict=modele,
        liste_langues=liste_langues,
        blabla=2,
    )

    # Teintes
    param_traduits = creer_liste_parametres_multilangue(
        liste_parametres=list(liste_couleurs.keys()),
        liste_deja_existante=param_traduits,
        nom_bouton="teintes_couleurs",
        modele_dict=modele,
        liste_langues=liste_langues,
        blabla=2,
    )

    # Arrière-plans
    param_traduits = creer_liste_parametres_multilangue(
        liste_parametres=list(dictionnaire_arriere_plans.keys()),
        liste_deja_existante=param_traduits,
        nom_bouton="arrière_plans",
        modele_dict=modele,
        liste_langues=liste_langues,
        blabla=1,
    )

    # Appels API
    if not date_jour in list(api_dict.keys()):
        api_dict[date_jour] = {}
    api_dict[date_jour][modele["modèle"]] = api_jour_modele


# 4 -- Export ------------------------------------------------------------------


## 4.1 -- Traductions ----------------------------------------------------------

# Vérification des doublons
verifier_doublons(param_traduits)

# Export
exporter_fichier(
    objet=param_traduits,
    direction_fichier=direction_donnees_traductions,
    nom_fichier="parametres_cartes_traduction.yaml",
    sort_keys=True,
)


## 4.2 -- Appels API effectués -------------------------------------------------


exporter_fichier(
    objet=api_dict,
    direction_fichier=direction_donnees_autres,
    nom_fichier="appels_api_par_jour.yaml",
    sort_keys=True,
)
