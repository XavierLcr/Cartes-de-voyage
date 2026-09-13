################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_4                                #
# Onglet 4.4.3 – Classe du thème                                               #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtGui import QColor

from _0_Utilitaires._0_2_fonctions_graphiques import interpoler_couleurs
from _0_Utilitaires._0_15_dates import phase_journee, _poids_moments

# 1 -- Classe du thème ---------------------------------------------------------


class ThemeLeveeDrapeaux:
    """
    Gère l'ensemble des couleurs de la scène selon le moment de la journée.
    """

    def __init__(
        self,
        latitude: float = 50.63,
        longitude: float = 5.57,
    ):

        self.latitude = latitude
        self.longitude = longitude

        self._PALETTE = {
            "nuit": {
                "ciel_haut": "#11182F",
                "ciel_milieu": "#26365B",
                "ciel_bas": "#55698A",
                "montagne_loin": "#39445E",
                "montagne_proche": "#252D42",
                "pierre_claire": "#85878B",
                "pierre_foncee": "#55585E",
            },
            "aube": {
                "ciel_haut": "#718AB5",
                "ciel_milieu": "#C49AA1",
                "ciel_bas": "#F1C6A0",
                "montagne_loin": "#9B8990",
                "montagne_proche": "#716C72",
                "pierre_claire": "#C1B4A8",
                "pierre_foncee": "#8C8179",
            },
            "jour": {
                "ciel_haut": "#78BCE5",
                "ciel_milieu": "#A9D7EF",
                "ciel_bas": "#DDEEF5",
                "montagne_loin": "#9CAEB2",
                "montagne_proche": "#77898A",
                "pierre_claire": "#D6D2C9",
                "pierre_foncee": "#A29D94",
            },
            "crepuscule": {
                "ciel_haut": "#515B88",
                "ciel_milieu": "#B06F7E",
                "ciel_bas": "#EEA275",
                "montagne_loin": "#88717C",
                "montagne_proche": "#5E5261",
                "pierre_claire": "#B69E94",
                "pierre_foncee": "#7F6D69",
            },
        }

        self._TEINTES = {}
        self.actualiser()

    def actualiser(self) -> None:
        """Actualise toutes les couleurs de la scène."""

        poids = _poids_moments(
            phase=phase_journee(),
            latitude=self.latitude,
            longitude=self.longitude,
        )

        self._TEINTES = {
            cle: interpoler_couleurs(
                couleurs={moment: self._PALETTE[moment][cle] for moment in poids},
                poids=poids,
                retour="qcolor",
            )
            for cle in self._PALETTE["nuit"]
        }

        self._TEINTES |= poids

    def couleur(self, cle: str) -> QColor:
        """Renvoie une couleur du thème."""

        return self._TEINTES[cle]
