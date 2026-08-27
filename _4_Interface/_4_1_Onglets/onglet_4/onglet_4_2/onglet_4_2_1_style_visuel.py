################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_2                                #
# Onglet 4.2.1 – Style de l'onglet des pays les plus visistés (superficie      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtGui import QColor

from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)

# 1 -- Classe du style ---------------------------------------------------------


class ThemeCarteClassement:
    def __init__(
        self,
        style,
        teinte=[i / 360 for i in range(0, 360, 45)],
        nuances={
            "min_luminosite": 0.8,
            "max_luminosite": 0.95,
            "min_saturation": 0.2,
            "max_saturation": 0.4,
        },
        limite_essais=20,
    ):
        # Fond de carte : légèrement plus clair/blanc que le fond d'appli
        # (clair), légèrement plus clair que le quasi-noir de fond (sombre)
        # — la carte doit se détacher sans jurer avec le fond général.
        self.fond = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#F6FED8",
                sombre="#1B2130",  # bleu-gris sombre, un cran au-dessus de #10141C
            )
        )
        self.texte = QColor(
            str(renvoyer_couleur_texte(style=style, couleur=self.fond.name()))
        )
        self.sous_texte = QColor(self.texte)
        self.sous_texte.setAlpha(140)

        # Dégradé du badge de rang : indigo doux sur fond clair, turquoise
        # lumineux sur fond très sombre — contraste net dans les deux cas,
        # sans concurrencer l'or/argent/bronze du podium.
        self.badge_debut = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#FAD27D",  # indigo doux
                sombre="#3DD6C6",  # turquoise clair
            )
        )
        self.badge_fin = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#F54B1C",  # indigo plus profond
                sombre="#1F9E92",  # turquoise plus profond
                reference=self.badge_debut.name(),
                essais=limite_essais,
            )
        )

        # Ombre toujours foncée, quel que soit le style — une ombre
        # blanche/claire rend mal, l'effet de profondeur ne fonctionne
        # que sur une teinte sombre.
        self.ombre = QColor("#000000")
        self.ombre.setAlpha(60 if style == 1 else 120)
