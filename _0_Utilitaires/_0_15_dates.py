################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# 0.15 – Fonction en lien avec la date et le temps                             #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


import time

# 1 -- Fonction de formatage de l'heure et de la date actuelles ----------------


def formater_temps_actuel(n: int = 0) -> str:
    formats = {
        0: "%d-%m-%Y %Hh%M",
        1: "%Y-%m-%d %H:%M",
        2: "%Y-%m-%d",
    }
    return time.strftime(formats.get(n, formats[0]), time.localtime())
