################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.6 – Fonctions utiles aux traductions                                       #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


from constantes import pays_differentes_langues


# 1 -- Fonction de récupération du nom d'un pays -------------------------------


def traduire_pays(dictionnaire: dict, pays: str, langue: str):
    return dictionnaire.get(pays, {}).get(langue, pays)
