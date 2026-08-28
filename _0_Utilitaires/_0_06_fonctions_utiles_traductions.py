################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.6 – Fonctions utiles aux traductions                                       #
################################################################################


# 1 -- Fonction de récupération du nom d'un pays -------------------------------


def traduire_pays(pays: str, langue: str, referentiel: dict = {}):
    return referentiel.get(pays, {}).get(langue, pays)
