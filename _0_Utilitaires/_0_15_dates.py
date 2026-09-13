################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# 0.15 – Fonction en lien avec la date et le temps                             #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


import time
from datetime import date

# 1 -- Fonction de formatage de l'heure et de la date actuelles ----------------


def formater_temps_actuel(n: int = 0) -> str:
    formats = {
        0: "%d-%m-%Y %Hh%M",
        1: "%Y-%m-%d %H:%M",
        2: "%Y-%m-%d",
    }
    return time.strftime(formats.get(n, formats[0]), time.localtime())


# 2 -- Fonction faisant n pauses par minute ------------------------------------


def sleep_n_fois(n: float, time_ref: float | None):

    # Si pas de temps de référence, on prend l'instant actuel
    if time_ref is None:
        time_ref = time.time()

    # Attente
    time.sleep(
        max(
            0,
            60 / n - (time.time() - time_ref),
        )
    )


# 3 -- Fonction de mise en forme du titre selon les événements -----------------


def periode_particuliere(periodes: dict) -> dict:

    aujourdhui = date.today()
    mois_actuel = aujourdhui.month
    jour_actuel = aujourdhui.day

    # Parcourir les périodes pour trouver la bonne
    for nom, details in periodes.items():
        if "dates" in details:
            for plage in details["dates"]:
                debut_jour = plage.get("debut", {}).get("jour", 1)
                debut_mois = plage.get("debut", {}).get("mois", 1)
                fin_jour = plage.get("fin", {}).get("jour", 31)
                fin_mois = plage.get("fin", {}).get("mois", 12)

                if (
                    # Vérification que la date est supérieure à celle de début
                    mois_actuel > debut_mois
                    or (mois_actuel == debut_mois and jour_actuel >= debut_jour)
                ) and (
                    # Vérification que la date est inférieure à celle de fin
                    mois_actuel < fin_mois
                    or (mois_actuel == fin_mois and jour_actuel <= fin_jour)
                ):

                    return details["config"]

    # Retourner la configuration par défaut
    return periodes.get("Défaut", {}).get(
        "config",
        {
            "titre_police": "Vivaldi",
            "titre_police_coeff": 1,
            "emoji": "",
        },
    )
