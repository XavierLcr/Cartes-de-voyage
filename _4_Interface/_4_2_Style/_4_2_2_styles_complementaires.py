################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_2_Style                                                      #
# 4.2.2 – Script contenant des styles complémentaires                          #
################################################################################


from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
)


# 1 -- Génération du style des boutons de suppression et de réinitialisation ---


def style_bouton_de_suppression(sombre: bool):
    return f"""
        QPushButton {{
            background-color:{"#430404" if sombre else "#f8d7da"};
            color: {"#E6E6E6" if sombre else "#2C2C2C"};
            font-size: 12px;
            border: none;
            border-radius: 5px;
            padding: 8px;
        }}
        QPushButton:hover {{
            background-color: {"#85040d" if sombre else "#f5c6cb"};
        }}
    """


# 2 -- Couleur du bouton montrant la posssibilité de télécharger des YAMLs -----


def style_bouton_yaml(style: int, teinte, nuances):

    bg_couleur = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#D6F0EE", sombre="#742C82"
    )
    bg_couleur_survol = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#EBD3E6", sombre="#B34FA9"
    )
    bg_couleur_click = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#A8AFEA", sombre="#6E0D73"
    )

    return f"""
        QPushButton {{
            background-color: {bg_couleur};
            color: {renvoyer_couleur_texte(style=style, couleur=bg_couleur)}; 
            border-radius: 8px;
            padding: 10px 22px;
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


# 3 -- Fonction de choix de la couleur du bouton de recommandation -------------------------------


def style_bouton_recommandation(style: int, teinte, nuances):

    bg_couleur = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#C8E6C9", sombre="#512B52"
    )
    bg_couleur_survol = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#B7E4C7", sombre="#A01C6E"
    )
    bg_couleur_click = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#77B0AD", sombre="#000000"
    )

    return f"""
        QPushButton {{
            background-color: {bg_couleur};  /* pastel bleu-vert */
            color: {renvoyer_couleur_texte(style=style, couleur=bg_couleur)};              /* texte bleu foncé pour contraste doux */
            border-radius: 12px;
            padding: 10px 22px;
            font-size: 14px;
            font-weight: bold;
            border:  none;   /* bord subtil légèrement plus clair */
        }}
        QPushButton:hover {{
            background-color: {bg_couleur_survol};   /* légèrement plus saturé au survol */
            color: {renvoyer_couleur_texte(style=style, couleur=bg_couleur_survol)};  
            border-color: none;
        }}
        QPushButton:pressed {{
            background-color: {bg_couleur_click};   /* un peu plus foncé à l’appui */
            color: {renvoyer_couleur_texte(style=style, couleur=bg_couleur_click)};   
            border-color: none;
        }}
    """


# 4 -- Fonction du style du bouton d'ajout de profils --------------------------


def style_bouton_ajout_profil(style: int, teinte, nuances):

    bg_couleur = renvoyer_couleur_widget(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="transparent",
        sombre="#14689C",
    )

    bg_couleur_survol = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#D6F0EE", sombre="#79E3DA"
    )

    return f"""
        QPushButton {{
            font-weight: bold;
            background-color: {bg_couleur};
            border: none;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background-color:{bg_couleur_survol}
        }}
        """
