################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_2_Style                                                      #
# 4.2.2 – Script contenant des styles complémentaires                          #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_widget,
    transformer_couleur_texte,
)

# 1 -- Génération du style des boutons de suppression et de réinitialisation ---


def style_bouton_de_suppression(sombre: bool):

    couleur_fond = "#5C2028" if sombre else "#f8d7da"
    couleur_texte = transformer_couleur_texte(bg_color=couleur_fond)
    couleur_hover = "#74282F" if sombre else "#f5c6cb"

    return f"""
        QPushButton {{
            background-color:{couleur_fond};
            color: {couleur_texte};
            font-size: 12px;
            border: none;
            border-radius: 10px;
            padding: 8px;
        }}
        QPushButton:hover {{
            background-color: {couleur_hover};
        }}
    """


# 2 -- Fonction du style du bouton d'ajout de profils --------------------------


def style_bouton_ajout_profil(style: int, teinte, nuances):

    bg_couleur = renvoyer_couleur_widget(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#D6F0EE",
        sombre="#14689C",
    )

    bg_couleur_survol = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#B1DDD9", sombre="#79E3DA"
    )

    return f"""
        QPushButton {{
            font-weight: bold;
            background-color: {bg_couleur};
            color: #8B0000;  /* rouge foncé */
            border: none;
            font-size: 12px;
            border-radius: 10px;
            font-weight: bold;

        }}
        QPushButton:hover {{
            background-color:{bg_couleur_survol}
        }}
        """
