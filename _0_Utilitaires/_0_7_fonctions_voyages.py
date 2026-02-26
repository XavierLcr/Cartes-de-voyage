################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.7 – Fonctions utiles afin de manupuler des voyages                         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from _0_Utilitaires._0_6_fonctions_utiles_traductions import traduire_pays


# 1 -- Création d'un voyage ----------------------------------------------------


def creer_voyage(
    nom: str, date_deb, date_fin, regions: dict, departements: dict, langue: str
):

    # Création du voyage
    resultat = {
        "nom": nom,
        "date_debut": date_deb,
        "date_fin": date_fin,
        "region": regions,
        "dep": departements,
    }

    # Nom automatique s'il est inexistant
    if not resultat.get("nom"):
        nom_temp = list((resultat.get("region", {})).keys()) + list(
            (resultat.get("dep", {})).keys()
        )

        resultat["nom"] = ", ".join(
            [traduire_pays(langue=langue, pays=pays) for pays in list(set(nom_temp))]
        )

    return resultat
