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
