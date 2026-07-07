################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/_2_2_application/2_2_1_traductions/                           #
# 2.2.1.3 – Fichier de traduction des noms de langues                          #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


import os, sys

sys.path.append(os.getcwd())

from constantes import direction_donnees_traductions
from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    ouvrir_fichier,
    exporter_fichier,
)
from _0_Utilitaires._0_13_LLM import LLMClient
from clefs_et_mots_de_passe import liste_langues

# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de création du prompt ---------------------------------------


def creer_prompt(langue: str):

    prompt_temp = f"""
        Tu es un expert en langues du monde.

        Ta mission est de convertir un nom de langue écrit en français vers son nom dans cette langue (son endonyme).

        Règles :
        - Ne renvoie que le nom de la langue.
        - N'ajoute aucune explication.
        - N'ajoute aucune ponctuation.
        - N'ajoute aucune prononciation, translittération ou traduction.
        - Utilise l'écriture native lorsque la langue possède son propre alphabet.
        - Mets une majuscule uniquement lorsqu'elle est utilisée dans la langue concernée.

        Exemples :
        anglais → English
        allemand → Deutsch
        espagnol → Español
        français → français
        italien → Italiano
        grec → Ελληνικά
        russe → Русский
        japonais → 日本語
        coréen → 한국어
        chinois mandarin → 普通话
        ourdou → اردو
        persan → فارسی
        hindi → हिन्दी
        thaï → ไทย
        tibétain → བོད་སྐད།

        Langue française :
        {langue}

        Réponse :
        """

    return prompt_temp


## 1.2 -- Fonction de traduction des langues -----------------------------------


def creer_dictionnaire_langues(
    modele: str,
    liste_deja_existante: dict,
    liste_langues: list,
    blabla: bool = True,
):

    resultat = liste_deja_existante or {}

    for i in sorted(liste_langues):

        if i not in list(resultat.keys()):

            if blabla:
                print(f"{i}")

            # Traduction
            try:
                llm_temp = LLMClient(
                    model=modele,
                    url="http://localhost:11434/api/generate",
                    timeout=300,
                    temperature=0,
                )
                llm_temp.set_prompt(prompt=creer_prompt(langue=i))
                resultat[i] = llm_temp.generate().strip(" .'\n")

            except Exception as e:
                print(f"Erreur : {e}")
                continue

    return resultat


# 2 -- Lecture des données -----------------------------------------------------


langues = ouvrir_fichier(
    direction_fichier=direction_donnees_traductions,
    nom_fichier="noms_langues_traduction.yaml",
    defaut={},
    afficher_erreur="Fichiers YAML des traductions des noms de langues non trouvé.",
)


# 3 -- Traduction --------------------------------------------------------------


langues_trad = creer_dictionnaire_langues(
    modele="mistral:7b",
    liste_deja_existante=langues,
    liste_langues=liste_langues,
    blabla=True,
)


# 4 -- Export ------------------------------------------------------------------


langues = exporter_fichier(
    objet=langues,
    direction_fichier=direction_donnees_traductions,
    nom_fichier="noms_langues_traduction.yaml",
    sort_keys=True,
)
