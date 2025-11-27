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


def style_bouton_de_suppression(sombre):
    return f"""QPushButton {{
                            background-color:{"#000000" if sombre else "#f8d7da"};
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
        style=style, teinte=teinte, nuances=nuances, clair="#C8E6C9", sombre="#2B523B"
    )
    bg_couleur_survol = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#B7E4C7", sombre="#0B9437"
    )
    bg_couleur_click = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#77B0AD", sombre="#0D7344"
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
            background-color: #B7E4C7;   /* légèrement plus saturé au survol */
            color: {renvoyer_couleur_texte(style=style, couleur=bg_couleur_survol)};  
            border-color: none;
        }}
        QPushButton:pressed {{
            background-color: {bg_couleur_click};   /* un peu plus foncé à l’appui */
            color: {renvoyer_couleur_texte(style=style, couleur=bg_couleur_click)};   
            border-color: none;
        }}
    """
