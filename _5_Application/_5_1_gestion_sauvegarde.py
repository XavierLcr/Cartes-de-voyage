################################################################################
# Projet de cartes de voyage                                                   #
# _5_Application/                                                              #
# 5.1 – Classe de gestion de la sauvegarde                                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import copy

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    exporter_fichier,
    formater_temps_actuel,
)

# 1 -- Classe de sauvegarde ----------------------------------------------------


class Sauvegarde(dict):

    def __init__(self, chemin_sauvegarde, sauvegarde: dict = {}, parent=None):
        super().__init__()

        self.sauvegarde = sauvegarde or {}
        self.chemin_sauvegarde = chemin_sauvegarde
        self.nom_fichier = "sauvegarde_utilisateurs.yaml"

    def supprimer_profil(self, clef: str):
        """Permet de supprimer un profil s'il existe"""

        if clef in self.sauvegarde:
            del self.sauvegarde[clef]
            self.exporter_sauvegarde()
            return True
        else:
            return False

    def renvoyer_liste_profils(self):
        """Renvoie tous les profils existants, par ordre alphabétique"""
        return list(self.sauvegarde.keys())

    def exporter_sauvegarde(self):

        exporter_fichier(
            objet=self.sauvegarde,
            direction_fichier=self.chemin_sauvegarde,
            nom_fichier=self.nom_fichier,
            sort_keys=True,
        )

    def sauvegarde_vide(self):
        return self.sauvegarde == {}

    def actualiser_profil(self, parametres: dict, date_publication: bool):

        # Création d'un nom de profil si nécessaire
        if parametres["nom"] is None or parametres["nom"] in [""]:
            parametres["nom"] = formater_temps_actuel(n=0)

        self.sauvegarde[parametres["nom"]] = (
            copy.deepcopy(parametres)
            # Ajout de la cate de publication si souhaité
            | {
                "date_publication": self.sauvegarde.get(parametres["nom"], {}).get(
                    "date_publication", []
                )
                + ([formater_temps_actuel(n=1)] if date_publication else [])
            }
        )

        # Export
        self.exporter_sauvegarde()

    def renvoyer_profil(self, nom: str):
        return self.sauvegarde.get(nom, {})

    def profil_existant(self, profil):
        return profil in self.renvoyer_liste_profils()
