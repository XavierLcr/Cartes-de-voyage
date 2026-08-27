################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4.1.2 – Couleurs des continents                                       #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)

# 1 -- Classe de thème ---------------------------------------------------------


class ThemeHemicycle:
    def __init__(
        self,
        parent,
        style,
        teinte,
        nuances,
        limite_essais=20,
    ):

        self.continents_couleurs = {
            "Africa": "#D4C220",
            "Antarctica": "#A7C9E6",
            "Asia": "#EE211E",
            "Europe": "#9A0EE6",
            "North America": "#1310CE",
            "Oceania": "#1EC3CF",
            "South America": "#23E958",
        }

        self.couleur_texte = renvoyer_couleur_texte(
            style=style,
            couleur=parent.palette().color(parent.backgroundRole()).name(),
        )
