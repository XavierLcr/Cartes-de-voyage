################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.6 – Fonctions utiles aux traductions                                       #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


from constantes import pays_differentes_langues


# 1 -- Fonction de récupération du nom d'un pays -------------------------------


def traduire_pays(pays: str, langue: str):
    return pays_differentes_langues.get(pays, {}).get(langue, pays)
