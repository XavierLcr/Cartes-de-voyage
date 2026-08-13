################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_2_Style                                                      #
# 4.2.2 – Script contenant des styles complémentaires                          #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
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


# 2 -- Fonction de choix de la couleur du bouton de recommandation -------------------------------


def style_bouton_recommandation(style: int, teinte, nuances):

    bg_couleur = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#F7CC76", sombre="#D9576F"
    )
    bg_couleur_survol = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#F46363", sombre="#E67A4F"
    )
    bg_couleur_click = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#EE77AC", sombre="#A83E56"
    )

    return f"""
        QPushButton {{
            background-color: {bg_couleur};
            color: {renvoyer_couleur_texte(style=style, couleur=bg_couleur)};
            border-radius: 12px;
            padding: 10px 22px;
            font-size: 14px;
            font-weight: bold;
            border:  none; 
        }}
        QPushButton:hover {{
            background-color: {bg_couleur_survol};
            color: {renvoyer_couleur_texte(style=style, couleur=bg_couleur_survol)};  
            border-color: none;
        }}
        QPushButton:pressed {{
            background-color: {bg_couleur_click};
            color: {renvoyer_couleur_texte(style=style, couleur=bg_couleur_click)};   
            border-color: none;
        }}
    """


# 3 -- Fonction du style du bouton d'ajout de profils --------------------------


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
