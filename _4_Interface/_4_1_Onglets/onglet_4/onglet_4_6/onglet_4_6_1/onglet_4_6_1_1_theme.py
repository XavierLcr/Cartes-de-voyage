################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6/onglet_4_6_1                   #
# Onglet 4.6.1.1 – Thème du compteur de pays visités                           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from _0_Utilitaires._0_2_fonctions_graphiques import interpoler_couleurs
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import _QColor_avec_alpha
from _0_Utilitaires._0_15_dates import phase_journee, _poids_moments
from _4_Interface._4_2_Style._4_2_1_style_principal import renvoyer_couleur_texte

# 1 -- Thème du widget ---------------------------------------------------------


class CompteurTheme:
    """
    Palette de couleurs du widget de compteur de pays visités.
    """

    def __init__(self):

        self._PALETTE = {
            "nuit": {
                "centre": "#232A52",
                "bord": "#12142B",
                "rim": "#B9C4E0",
                "fond": "#1A1F3D",
                "progression_debut": "#8A78C8",
                "progression_fin": "#C7B9F2",
                "cercle_tour": "#B9C4E0",
                "sable_debut": "#A99670",
                "sable_fin": "#C8B68A",
            },
            "aube": {
                "centre": "#FDE0B0",
                "bord": "#F3A66B",
                "rim": "#F7C88A",
                "fond": "#F2DAC0",
                "progression_debut": "#D98762",
                "progression_fin": "#F5C98D",
                "cercle_tour": "#F7C88A",
                "sable_debut": "#C8A46F",
                "sable_fin": "#D8B982",
            },
            "jour": {
                "centre": "#FFFCF2",
                "bord": "#FFF3D2",
                "rim": "#F0C452",
                "fond": "#E5EFF3",
                "progression_debut": "#C9902F",
                "progression_fin": "#F3D48C",
                "cercle_tour": "#FFCB61",
                "sable_debut": "#C9A45E",
                "sable_fin": "#E2C47D",
            },
            "crepuscule": {
                "centre": "#F6B27C",
                "bord": "#D96A5C",
                "rim": "#F2914F",
                "fond": "#EFD4DE",
                "progression_debut": "#C85F5A",
                "progression_fin": "#F3A66F",
                "cercle_tour": "#F2914F",
                "sable_debut": "#B88D61",
                "sable_fin": "#C9A16A",
            },
        }

        # Calcul de la bonne couleur
        self._PALETTE = self._teintes_palette()

        # -- Ajout de la couleur du texte
        self._PALETTE["texte"] = renvoyer_couleur_texte(
            style=0, couleur=self._PALETTE["centre"].name()
        )
        # -- Ajout de la couleur de la piste
        self._PALETTE["piste"] = _QColor_avec_alpha(self._PALETTE["texte"], alpha=25)

    def _teintes_palette(
        self, latitude: float = 50.63, longitude: float = 5.57
    ) -> dict:
        """Mélange pondéré des teintes centre/bord/rim selon les poids
        horaires actifs (transition continue, pas de bascule brutale)."""

        poids_temp = _poids_moments(
            phase_journee(), latitude=latitude, longitude=longitude
        )
        return {
            cle: interpoler_couleurs(
                {moment: self._PALETTE[moment][cle] for moment in poids_temp},
                poids=poids_temp,
                retour="qcolor",
            )
            for cle in self._PALETTE.get("nuit").keys()
        } | poids_temp
