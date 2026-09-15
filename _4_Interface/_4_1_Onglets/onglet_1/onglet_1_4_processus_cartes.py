################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1.X – Processus de création des cartes                                #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import traceback
import importlib

from _4_Interface._4_1_Onglets.onglet_1.onglet_1_1_creation_cartes import (
    CreerCartes,
)

# 1 -- Processus ---------------------------------------------------------------


def executer_creation_cartes(
    params,
    nom_module_constantes,
    file_messages,
):
    """
    Exécute CreerCartes dans un processus Python indépendant.

    Les signaux PyQt restent internes au processus et sont convertis
    en petits messages transmis à l'interface principale.
    """

    constantes = importlib.import_module(nom_module_constantes)

    try:

        creation_cartes = CreerCartes(
            params=params,
            constantes=constantes,
        )

        # Nombre total de cartes
        creation_cartes.nb_graphes.connect(
            lambda n: file_messages.put(
                (
                    "nb_graphes",
                    n,
                )
            )
        )

        # Une carte terminée
        creation_cartes.tracker_signal.connect(
            lambda nom_pays: file_messages.put(
                (
                    "progression",
                    nom_pays,
                )
            )
        )

        # Fin
        creation_cartes.finished.connect(
            lambda: file_messages.put(
                (
                    "finished",
                    None,
                )
            )
        )

        creation_cartes.run()

    except Exception:

        file_messages.put(
            (
                "erreur",
                traceback.format_exc(),
            )
        )
