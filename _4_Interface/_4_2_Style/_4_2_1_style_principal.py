################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_2_Style                                                      #
# 4.2.1 – Script contenant les fonctions esthétiques                           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtGui import QColor

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
        style=style, teinte=teinte, nuances=nuances, clair="#F5F5FA", sombre="#10141C"
    )
    couleur_widget_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_widget,
    )

    # Groupboxes
    couleur_groupbox = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#E6E4F2", sombre="#1C4E5E"
    )

    # Boutons
    couleur_push = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#D6E4F0", sombre="#1C7A94"
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
        sombre="#24A0BD",
        reference=couleur_push,
        essais=limite_essais,
    )
    couleur_push_hover_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_push_hover,
    )
    couleur_push_presse = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#C3B9DE",
        sombre="#14586E",
        reference=couleur_push_hover,
        essais=limite_essais,
    )
    couleur_push_texte_presse = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_push_presse,
    )
    couleur_push_desactive = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#E4E9F0", sombre="#2A2E3D"
    )
    couleur_push_texte_desactive = QColor(
        renvoyer_couleur_texte(
            style=style,
            couleur=couleur_push_desactive,
        )
    )
    couleur_push_texte_desactive = (
        f"rgba("
        f"{couleur_push_texte_desactive.red()}, "
        f"{couleur_push_texte_desactive.green()}, "
        f"{couleur_push_texte_desactive.blue()}, "
        f"127)"
    )
    # Boites
    couleur_box = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#E8EEE1", sombre="#1696A9"
    )
    couleur_box_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_box,
    )
    couleur_QComboBox_hover = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#919191", sombre="#5599A3"
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
    couleur_line_selection = "rgba(30, 127, 163, 0.35)"
    couleur_line_placeholder = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#9AA5B1", sombre="#5F6472"
    )

    # Sliders
    couleur_slider = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#C7DEE7", sombre="#16495A"
    )
    couleur_slider_hover = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#72BAD6",
        sombre="#1FA4B6",
        reference=couleur_slider,
        essais=limite_essais,
    )
    couleur_slider_rempli = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#31ABD8", sombre="#26C6DA"
    )
    couleur_slider_handle_survol = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#186A87", sombre="#22B3C7"
    )
    couleur_slider_handle_presse = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#125571", sombre="#1D9BAC"
    )

    # Onglet actuel
    onglet_actuel = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#C2D4E8", sombre="#1C7A94"
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
        sombre="#2C5A6C",
        reference=[onglet_actuel, onglet_fond],
        essais=limite_essais,
    )

    # Barre de progression
    couleur_barre_progression_debut = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#ADCEDB", sombre="#26C6DA"
    )
    couleur_barre_progression_fin = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#1E7FA3", sombre="#0891A8"
    )

    # Checkboxes
    couleur_checkbox_bord = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#90AAB4",
        sombre="#2C5A6C",
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
        style=style, teinte=teinte, nuances=nuances, clair="#F3F4F8", sombre="#10141C"
    )
    couleur_scroll_area_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_scroll_area_fond,
    )
    couleur_scroll_area_bord = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#C9D6E0", sombre="#2C3A4F"
    )
    couleur_scroll_area_barre = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#ADCEDB", sombre="#1FA4B6"
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
        sombre="#26C6DA",
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
        style=style, teinte=teinte, nuances=nuances, clair="#D6E4F0", sombre="#1C7A94"
    )
    couleur_widget_list_survol_fond = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#E0EBF5",
        sombre="#24384A",
        reference=[couleur_widget_list_select, couleur_widget_list_fond],
        essais=limite_essais,
    )

    # Barre d'outils (QToolBar / QToolButton)
    couleur_toolbar_separateur = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#C9D3E0", sombre="#32475B"
    )
    couleur_toolbutton_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_widget,
    )
    couleur_toolbutton_hover_fond = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#DCEBFA", sombre="#1E3A4D"
    )
    couleur_toolbutton_hover_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_toolbutton_hover_fond,
    )
    couleur_toolbutton_hover_bord = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#9FC6F0", sombre="#2C8AA6"
    )
    couleur_toolbutton_presse = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#C2DCFA",
        sombre="#155E73",
        reference=couleur_toolbutton_hover_fond,
        essais=limite_essais,
    )
    couleur_toolbutton_presse_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_toolbutton_presse,
    )
    couleur_toolbutton_coche_fond = renvoyer_couleur_widget_differente(
        style=style,
        teinte=teinte,
        nuances=nuances,
        clair="#B4D6FA",
        sombre="#1C7A94",
        reference=[couleur_toolbutton_hover_fond, couleur_toolbutton_presse],
        essais=limite_essais,
    )
    couleur_toolbutton_coche_texte = renvoyer_couleur_texte(
        style=style,
        couleur=couleur_toolbutton_coche_fond,
    )
    couleur_toolbutton_coche_bord = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#5C9CEF", sombre="#26C6DA"
    )
    couleur_toolbutton_desactive_texte = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#A6ACB8", sombre="#565E70"
    )

    return f"""
            QWidget {{
                background-color: {couleur_widget};
                color: {couleur_widget_texte};
                font-size: {font_size}px;
                font-family: Nunito;
                
            }}
            QPushButton {{
                background-color: {couleur_push};
                color: {couleur_push_texte};
                border: none;
                border-radius: 10px;
                padding: 9px 18px;
            }}
            QPushButton:pressed {{
                background-color: {couleur_push_presse};
                color: {couleur_push_texte_presse};
                padding: 10px 18px 8px 18px;
            }}
            QPushButton:disabled {{
                background-color: {couleur_push_desactive};
                color: {couleur_push_texte_desactive};
            }}
            QPushButton:hover {{
                background-color: {couleur_push_hover};
                color: {couleur_push_hover_texte};
            }}

            QLineEdit {{
                background-color: {couleur_line};
                color: {couleur_line_texte};
                border: 1px solid {couleur_line_bord};
                padding: 8px 12px;
                border-radius: 10px;
                selection-background-color: {couleur_line_selection};
            }}
            QLineEdit::placeholder {{
                color: {couleur_line_placeholder};
            }}

            QSlider::groove:horizontal {{
                background: {couleur_slider};
                height: 6px;
                border-radius: 3px;
            }}

            QSlider::sub-page:horizontal {{
                background: {couleur_slider_rempli};
                height: 6px;
                border-radius: 3px;
            }}

            QSlider::add-page:horizontal {{
                background: {couleur_slider};
                height: 6px;
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                background: {couleur_slider_hover};
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -6px 0;
                
            }}

            QSlider::handle:horizontal:hover {{
                background: {couleur_slider_handle_survol};
            }}

            QSlider::handle:horizontal:pressed {{
                background: {couleur_slider_handle_presse};
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: -7px -1px;
            }}

            QGroupBox {{
                border: 2px solid {couleur_groupbox};
                border-radius: 14px;
                margin-top: 7px;
                padding: 18px 14px 14px 14px;
                font-weight: 500;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;

                left: 14px;
                padding: 0px 8px;

            }}
            QTabBar::tab {{
                background: {onglet_fond};
                color: {onglet_texte};
                padding: 8px 18px;
                margin-right: 4px;
                border: 1px solid rgba(255,255,255,25);
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}

            QTabBar::tab:selected {{
                background: {onglet_actuel};
                color: {onglet_actuel_texte};
                font-weight: 600;

                border: 1px solid rgba(255,255,255,45);
                border-bottom: 2px solid {onglet_actuel};
                margin-bottom: -1px;
            }}
            QTabBar::tab:hover {{
                background: {onglet_hover};
            }}
            QTabWidget::pane {{
                border: 1px solid rgba(255,255,255,0);
                border-radius: 10px;
                
                top: -1px;
            }}

            QComboBox {{
                background-color: {couleur_box};
                color: {couleur_box_texte};
                border: 1px solid rgba(255,255,255,40);
                padding: 7px 12px;
                border-radius: 10px;
            }}
            QComboBox QAbstractItemView {{ 
                border: none; outline: none; 
            }} 
            QComboBox QAbstractItemView::item {{ 
                padding: 5px; height: 20px; /* Hauteur de chaque élément de la liste */ 
            }}
            QComboBox::drop-down {{
                border: 0px;
                width: 20px;
                height: 20px;
            }}
            QComboBox::down-arrow {{
                width: 32px;
                border: none;
            }}
            QComboBox::disabled {{
                background-color: {couleur_push_desactive};
                color: {couleur_push_texte_desactive};
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

            QCheckBox {{
                spacing: 8px;
                color: {couleur_widget_texte};
            }}
            QCheckBox {{
                spacing: 6px;  /* 👈 espace entre la boîte et le texte */
                padding-left: 0px;  /* marge interne à gauche du tout */
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {couleur_checkbox_bord}; /* couleur du cadre */
                background-color: transparent; 
                border-radius: 5px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {couleur_checkbox_cochee_fond};  /* laisse Qt dessiner le tick */
                border: 2px solid {couleur_checkbox_bord};
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
                border-radius: 12px;
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {couleur_barre_progression_debut},
                    stop: 1 {couleur_barre_progression_fin}
                );
                margin: 0px;
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

            QScrollBar:vertical {{
                background: transparent;
                width: 15px;
                margin: 3px;
            }}
            QScrollBar::handle:vertical {{
                border-radius: 5px;
                margin: 2px;
                min-height: 35px;
            }}
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
                background: {couleur_scroll_area_barre}; 
                border-radius: 0px;
            }}
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
                background: {couleur_scroll_area_barre_survol}; /* slider : bleu-vert doux */
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

            QToolBar {{
                background: transparent;
                border: none;
                spacing: 8px;
                padding: 6px 8px;
            }}

            QToolBar::separator {{
                width: 1px;
                background: {couleur_toolbar_separateur};
                margin: 6px 8px;
            }}

            QToolButton {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: 10px;
                padding: 8px 14px;
                color: {couleur_toolbutton_texte};
                font-size: {font_size}px;
                font-weight: 500;
            }}

            QToolButton:hover {{
                background: {couleur_toolbutton_hover_fond};
                color: {couleur_toolbutton_hover_texte};
                border: 1px solid {couleur_toolbutton_hover_bord};
            }}

            QToolButton:pressed {{
                background: {couleur_toolbutton_presse};
                color: {couleur_toolbutton_presse_texte};
                border: 1px solid {couleur_toolbutton_hover_bord};
            }}

            QToolButton:checked {{
                background: {couleur_toolbutton_coche_fond};
                color: {couleur_toolbutton_coche_texte};
                border: 1px solid {couleur_toolbutton_coche_bord};
                font-weight: 600;
            }}

            QToolButton:disabled {{
                color: {couleur_toolbutton_desactive_texte};
            }}
        """
