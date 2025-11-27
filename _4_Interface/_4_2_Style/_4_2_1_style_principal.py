################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_2_Style                                                      #
# 4.2 – Script contenant les fonctions esthétiques                             #
################################################################################


from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
)


# 1 -- Fonction de gestion des situations où deux couleurs doivent différer ----


def renvoyer_couleur_widget_differente(
    style, teinte, nuances, clair, sombre, reference, essais=20
):
    for _ in range(essais):
        resultat = renvoyer_couleur_widget(
            style=style,
            teinte=teinte,
            nuances=nuances,
            clair=clair,
            sombre=sombre,
        )
        if resultat not in reference:
            break

    # Renvoi
    return resultat


# 2 -- Fonction de création du style complet de l'application ------------------


def style_dynamique_application(
    style,
    teinte=[i / 360 for i in range(0, 360, 45)],
    nuances={
        "min_luminosite": 0.8,
        "max_luminosite": 0.95,
        "min_saturation": 0.2,
        "max_saturation": 0.4,
    },
    limite_essais=20,
    font_size=12,
):

    # Cas général
    couleur_widget = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#F3F4F8", sombre="#07215E"
    )
    couleur_widget_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_widget,
    )

    # Groupboxes
    couleur_groupbox = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#E6E4F2", sombre="#2C3A82"
    )

    # Boutons
    couleur_push = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#D6E4F0", sombre="#3F51B5"
    )
    couleur_push_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_push,
    )
    couleur_push_hover = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#DAD3EB",
        sombre="#6A4FB3",
        reference=couleur_push,
        essais=limite_essais,
    )
    couleur_push_hover_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_push_hover,
    )

    # Boites
    couleur_box = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#EBF0F2", sombre="#1696A9"
    )
    couleur_box_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_box,
    )
    couleur_box_bord = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#C9D6E0", sombre="#1696A9"
    )

    # Lignes
    couleur_line = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#F1F2F4", sombre="#1E2734"
    )
    couleur_line_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_line,
    )
    couleur_line_bord = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#D4D4D8", sombre="#32475B"
    )

    # Sliders
    couleur_slider = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#C7DEE7", sombre="#26C6DA"
    )
    couleur_slider_hover = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#ADCEDB",
        sombre="#4DD0E1",
        reference=couleur_slider,
        essais=limite_essais,
    )

    # Onglet actuel
    onglet_actuel = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#C2D4E8", sombre="#2D3D80"
    )
    onglet_actuel_texte = couleur_line_texte = renvoyer_couleur_texte(
        style=style,
        couleur=onglet_actuel,
    )

    # Onglets
    onglet_fond = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#E8EAF1", sombre="#1A1F2B"
    )
    onglet_texte = couleur_line_texte = renvoyer_couleur_texte(
        style=style,
        couleur=onglet_fond,
    )
    onglet_hover = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#CFC4E2",
        sombre="#6A4FB3",
        reference=[onglet_actuel, onglet_fond],
        essais=limite_essais,
    )

    # Barre de progression
    couleur_barre_progression = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#ADCEDB", sombre="#26C6DA"
    )

    # Checkboxes
    couleur_checkbox_bord = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#6C7780",
        sombre="#2C3A82",
        reference=couleur_widget,
        essais=limite_essais,
    )
    couleur_checkbox_cochee_fond = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#ADCEDB",
        sombre="#26C6DA",
        reference=[couleur_widget, couleur_checkbox_bord],
        essais=limite_essais,
    )

    # Scroll area
    couleur_scroll_area_fond = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#F3F4F8", sombre="#1A1F2B"
    )
    couleur_scroll_area_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_scroll_area_fond,
    )
    couleur_scroll_area_bord = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#C9D6E0", sombre="#2C3A4F"
    )
    couleur_scroll_area_barre = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#ADCEDB", sombre="#3F7DDC"
    )
    couleur_scroll_area_barre_partie = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#DEDEDE",
        sombre="#27364D",
        reference=couleur_scroll_area_barre,
        essais=limite_essais,
    )
    couleur_scroll_area_barre_survol = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#C7DEE7",
        sombre="#5C9EFF",
        reference=[couleur_scroll_area_barre, couleur_scroll_area_barre_partie],
        essais=limite_essais,
    )

    # Liste de widgets
    couleur_widget_list_fond = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#F4F6FA", sombre="#222B3C"
    )
    couleur_widget_list_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_widget_list_fond,
    )
    couleur_widget_list_select = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#D6E4F0", sombre="#3F7DDC"
    )
    couleur_widget_list_survol_fond = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#E0EBF5",
        sombre="#2F456A",
        reference=[couleur_widget_list_select, couleur_widget_list_fond],
        essais=limite_essais,
    )

    return f"""
            QWidget {{
                background-color: {couleur_widget};
                color: {couleur_widget_texte};
                font-size: {font_size}px;
                font-family: Sylfaen;
            }}
            QPushButton {{
                background-color: {couleur_push};
                color: {couleur_push_texte};
                border-radius: 5px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: { couleur_push_hover};
                color: { couleur_push_hover_texte};
            }}
            QComboBox {{
                background-color: {couleur_box};
                color: {couleur_box_texte};
                border: 1px solid {couleur_box_bord};
                padding: 5px;
                border-radius: 5px;
            }}
            QLineEdit {{
                background-color: {couleur_line};
                color: {couleur_line_texte};
                border: 1px solid {couleur_line_bord};
                padding: 5px;
                border-radius: 5px;
            }}
            QSlider::groove:horizontal {{
                background: {couleur_slider};
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {couleur_slider_hover};
                width: 20px;
                border-radius: 12px;
                margin: -5px 0;
            }}
            QGroupBox {{
                border: 2px solid {couleur_groupbox};
                border-radius: 5px;
                padding: 10px;
            }}
            QTabBar::tab {{
                background: {onglet_fond};
                color: {onglet_texte};
                padding: 8px 16px;
                border: none;
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }}

            QTabBar::tab:selected {{
                background: {onglet_actuel};
                color: {onglet_actuel_texte};
                font-weight: bold;
            }}

            QTabBar::tab:hover {{
                background: {onglet_hover};
            }}
            QComboBox QAbstractItemView {{
                border: none;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 5px;
            }}
            QScrollArea {{
                background-color: transparent;
                border: 2px solid {couleur_scroll_area_bord};
                border-radius: 5px;
            }}

            QScrollArea > QWidget {{
                background-color: {couleur_scroll_area_fond};
                color: {couleur_scroll_area_texte};
                border-radius: 5px;
            }}

            QScrollArea > QWidget > QWidget {{
                background-color: {couleur_scroll_area_fond};
            }}
            QScrollBar:vertical {{
                background: {couleur_scroll_area_barre_partie}; /* cohérent avec couleur_box */
                width: 12px;
                margin: 2px;
                border-radius: 0px;
            }}
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
                background: {couleur_scroll_area_barre}; 
                border-radius: 0px;
            }}
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
                background: {couleur_scroll_area_barre_survol}; /* slider : bleu-vert doux */
            }}

            QCheckBox {{
                spacing: 6px;  /* 👈 espace entre la boîte et le texte */
                padding-left: 0px;  /* marge interne à gauche du tout */
            }}

            QCheckBox::indicator {{
                border: 1px solid {couleur_checkbox_bord}; /* couleur du cadre */
                background-color: transparent; 
                border-radius: 3px;
            }}

            QCheckBox::indicator:checked {{
                background-color: {couleur_checkbox_cochee_fond};  /* laisse Qt dessiner le tick */
                border: 1px solid {couleur_checkbox_bord};
            }}
            QProgressBar {{
                border: none; 
                text-align: right;
                color: {couleur_widget_texte};
                padding-left: 10px;
                padding-right: 130px;
                background-color: transparent;
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background-color: {couleur_barre_progression};
                width: 8px;
                margin: 0.5px;
            }}
            QListWidget {{
                background-color: {couleur_widget_list_fond}; /* Très proche de ton fond principal, mais un peu plus lumineux */
                color: {couleur_widget_list_texte};
                border: none;
                padding: 4px;
                border-radius: 5px;
            }}
            QListWidget::item {{
                padding-left: 6px;
                padding-right: 6px;
            }}
            QListWidget::item:selected {{
                background-color: {couleur_widget_list_select}; /* Bleu clair (déjà utilisé dans QPushButton) */
                color: {couleur_widget_list_texte};
                border-radius: 4px;
            }}
            QListWidget::indicator:checked {{
                background-color: {couleur_checkbox_cochee_fond}; /* Bleu clair (déjà utilisé dans QPushButton) */
                border: 1px solid {couleur_checkbox_bord};
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {couleur_widget_list_survol_fond};
                color: {couleur_widget_list_texte};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                background: none;
                border: none;
                height: 0px;
            }}

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                background: none;
                border: none;
                width: 0px;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {{
                background: none;
            }}
            QRadioButton {{
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 5px 7px;
            }}

            QRadioButton:hover {{
                border: 1px solid {couleur_push_hover};
            }}

            QRadioButton:checked {{
                border: 2px solid {couleur_checkbox_cochee_fond}; /* couleur de bordure quand sélectionné */
                background-color: transparent;
            }}
            QRadioButton::indicator {{
                width: 0px;
                height: 0px;
                border-radius: 7px;
                border: 0px transparent;
                background-color: transparent;
            }}

            QRadioButton::indicator:hover {{
                border: transparent;
            }}

            QRadioButton::indicator:checked {{
                width: 0px;
                height: 0px;
                border: 0px transparent; /* bordure du rond sélectionné */
                background-color: transparent;  /* couleur du centre */
            }}

        """
