################################################################################
# Projet de cartes de voyage                                                   #
# _3_Calculs/                                                                  #
# 3.2 – Fichier de création des graphiques cartes                              #
################################################################################


import os, random, json, colorsys, math, textwrap
import matplotlib.pyplot as plt
from datetime import datetime


# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Générer une couleur aléatoire selon des contraintes HSV --------------


def generer_couleur_aleatoire_hex(
    preset: dict = {},
    teintes_autorisees: list | None = None,
):
    """
    Génère une couleur aléatoire au format hexadécimal avec des restrictions basées sur un preset.

    Args:
    – preset (dict) : Un dictionnaire contenant les luminosités et saturations minimales et maximales autorisées (entre 0 et 1).
    – teintes_autorisees (list): Liste de teintes spécifiques (de 0.0 à 1.0) pour restreindre la génération de couleurs. Défaut : None (toutes les teintes sont autorisées).

    Returns:
    – couleur_hex (str): Couleur au format hexadécimal.
    """
    # Récupération du préset
    config = {
        param: max(0, min(preset.get(param, 0.5), 1))
        for param in [
            "min_luminosite",
            "max_luminosite",
            "min_saturation",
            "max_saturation",
        ]
    }

    # Conversion HSV –> RGB
    r, g, b = colorsys.hsv_to_rgb(
        (
            random.choice(teintes_autorisees) if teintes_autorisees else random.random()
        ),  # Teinte
        random.uniform(
            config["min_saturation"], config["max_saturation"]
        ),  # Saturation
        random.uniform(
            config["min_luminosite"], config["max_luminosite"]
        ),  # Luminosité
    )

    # Conversion RGB –> Hex
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


## 1.2 -- Fonction de création de la carte -------------------------------------


def creer_image_carte(
    gdf,
    gdf_monde=None,
    gdf_regions=None,
    gdf_eau=None,
    theme: dict = {
        "min_luminosite": 0.8,
        "max_luminosite": 0.95,
        "min_saturation": 0.2,
        "max_saturation": 0.4,
    },
    teintes_autorisees: None | list = None,
    couleur_non_visites: str = "#ECEBED",
    couleur_pays_contours: str = "#F7F7F7",
    couleur_de_fond: str = "#FFFFFF",
    couleur_lacs: str = "#CEE3F5",
    chemin_impression: str = os.path.dirname(os.path.abspath(__file__)),
    nom: str = "Carte.jpg",
    qualite: int = 400,
    blabla=True,
    max_cartes_additionnelles: int | None = 10,
    afficher_nom_lieu: bool = True,
):
    r"""
    Crée une image de carte à partir d'un GeoDataFrame et l'exporte dans un fichier d'image.

    Cette fonction génère une carte basée sur un GeoDataFrame donné, applique une couleur spécifique à chaque ligne
    (en fonction de la colonne "Visite"), puis exporte l'image dans un fichier au format spécifié par le nom de fichier.

    Paramètres :
    – gdf (GeoDataFrame) : Le GeoDataFrame contenant la carte à créer.
    – gdf_monde (GeoDataFrame, optionnel) : Le GeoDataFrame contenant les frontières nationales. Par défaut, `None`.
    – gdf_regions (GeoDataFrame, optionnel) : Le GeoDataFrame contenant les frontières régionales. Par défaut, `None`.
    – gdf_eau (GeoDataFrame, optionnel) : Le GeoDataFrame contenant les surfaces d'eau. Par défaut, `None`.
    – theme (dict, optionnel) : Un dictionnaire définissant les paramètres de luminosité et de saturation pour le thème de la carte. Par défaut, il contient des valeurs prédéfinies pour la luminosité et la saturation.
    – teintes_autorisees (list, optionnel) : Une liste de teintes spécifiques (valeurs comprises entre 0.0 et 1.0) qui limitent les couleurs générées à certains types (par exemple, pour cibler certaines nuances). Par défaut, `None`, ce qui signifie que toutes les teintes peuvent être utilisées.
    – couleur_non_visites (str) : La couleur à utiliser pour les éléments où la variable "Visite" est False (par exemple, couleur grise pour les éléments non visités). Par défaut, `"#ecebed"`.
    – couleur_de_fond (str) : La couleur de fond de la carte. Par défaut, `"#FFFFFF"`.
    – couleur_lacs (str) : La couleur utilisée pour les lacs et autres plans d'eau. Par défaut, `"#cee3f5"`.
    – chemin_impression (str) : Le chemin où le fichier d'image sera sauvegardé. Par défaut, le répertoire du fichier courant.
    – nom (str) : Le nom du fichier image exporté. Par défaut, "Carte.jpg".
    – qualite (int) : La qualité de l'image exportée, exprimée en DPI (points par pouce). Par défaut, 400 DPI.
    – blabla (bool, optionnel) : Un paramètre booléen permettant l'affichage du suivi d'éxecution de la fonction. Par défaut, `True`.
    – max_cartes_additionnelles (int, optionnel) : Le nombre maximum de cartes additionnelles à générer. Par défaut, `10`.

    Retourne :
    – Aucune valeur retournée, mais l'image est enregistrée à l'emplacement spécifié dans chemin_impression.
    """

    # On ajoute la couleur de chaque ligne
    gdf["Couleur"] = gdf["Visite"].apply(
        lambda x: (
            generer_couleur_aleatoire_hex(
                preset=theme,
                teintes_autorisees=teintes_autorisees,
            )
            if x
            else couleur_non_visites
        )
    )
    # On gère la mère Caspienne
    gdf.loc[gdf["Pays"] == "Caspian Sea", "Couleur"] = couleur_de_fond

    # Crée la direction de sauvegarde du résultat si nécessaire
    if not os.path.exists(chemin_impression):
        os.makedirs(chemin_impression)

    # Cree le graphique
    if blabla:
        print("Création du graphique.", end=" ")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_axis_off()
    ax.margins(0)
    fig.patch.set_facecolor(couleur_de_fond)

    gdf.plot(ax=ax, color=gdf["Couleur"], edgecolor="black", linewidth=0.008, zorder=1)

    liste_pays = list(gdf["Pays"].unique())

    if gdf_monde is not None:

        # Ajout des pays aux alentours
        marge = 0.03
        xmin, ymin, xmax, ymax = gdf.total_bounds
        ax.set_xlim(xmin - marge * (xmax - xmin), xmax + marge * (xmax - xmin))
        ax.set_ylim(ymin - marge * (ymax - ymin), ymax + marge * (ymax - ymin))

        # Ajout des frontières de façon plus marquée
        if blabla:
            print("Ajout des frontières nationales", end="")

        gdf_monde.plot(
            ax=ax,
            color=gdf_monde["name_0"].apply(
                lambda x: (
                    couleur_de_fond
                    if x == "Caspian Sea"
                    else "none" if x in liste_pays else couleur_pays_contours
                )
            ),
            edgecolor=gdf_monde["name_0"].apply(
                lambda x: "black" if x in liste_pays else "dimgrey"
            ),
            linewidth=0.04,
            zorder=3,
        )

    if gdf_regions is not None:

        liste_pays_regions = list(gdf.loc[(gdf["Granu"] >= 1), "Pays"].unique())
        gdf_regions = gdf_regions[gdf_regions["name_0"].isin(liste_pays_regions)]

        if len(gdf_regions) > 0:

            if blabla:
                print(", des régions", end="")

            gdf_regions.plot(
                ax=ax, color="none", edgecolor="black", linewidth=0.017, zorder=2
            )

    if gdf_eau is not None:

        if blabla:
            print(", des lacs", end="")

        gdf_eau = gdf_eau[gdf_eau["name_0"].isin(liste_pays)]
        if len(gdf_eau) > 0:
            gdf_eau.plot(ax=ax, color=couleur_lacs, edgecolor="none", alpha=1, zorder=3)

    # Affichage du nom de la région
    if afficher_nom_lieu:
        # Calcul des dimensions des régions
        bounds = gdf.geometry.bounds
        gdf["largeur"] = bounds["maxx"] - bounds["minx"]
        gdf["hauteur"] = bounds["maxy"] - bounds["miny"]

        # Taille du texte selon la surface (plus douce grâce à log1p)
        gdf["taille_texte"] = gdf["largeur"].apply(
            lambda a: math.log1p(max(0.01, a * 0.5 * a / (a + 30)))
        )

        for x, y, label, couleur, taille, largeur in zip(
            gdf.geometry.centroid.x,
            gdf.geometry.centroid.y,
            gdf["Region"],
            gdf["Couleur"],
            gdf["taille_texte"],
            gdf["largeur"],
        ):

            ax.text(
                x,
                y,
                "\n".join(
                    textwrap.wrap(
                        label, width=max(5, int(largeur * 3)), break_long_words=False
                    )
                ),
                fontsize=taille,
                ha="center",
                va="center",
                color=transformer_couleur_texte(couleur),
                linespacing=0.8,
            )

    # Enregistrer la carte dans un fichier sans l'afficher
    if blabla:
        print(". Sauvegarde de l'image.", end=" ")

    # On supprime le fichier le plus vieux si necessaire
    if max_cartes_additionnelles is not None:
        fichiers = [
            os.path.join(chemin_impression, f)
            for f in os.listdir(chemin_impression)
            if (
                os.path.isfile(os.path.join(chemin_impression, f))
                and os.path.splitext(f)[1].lower()
                in [
                    ".eps",
                    ".jpg",
                    ".jpeg",
                    ".pdf",
                    ".pgf",
                    ".png",
                    ".ps",
                    ".raw",
                    ".rgba",
                    ".svg",
                    ".svgz",
                    ".tif",
                    ".tiff",
                    ".webp",
                ]
            )
        ]

        if len(fichiers) >= max(max_cartes_additionnelles, 1):
            os.remove(min(fichiers, key=os.path.getmtime))

    # On cree un nom qui n'existe pas encore si nécessaire
    nom = os.path.join(chemin_impression, nom)
    nom_simple, type_fichier = os.path.splitext(nom)
    compteur = 2
    while os.path.exists(nom):
        nom = f"{nom_simple} ({compteur}){type_fichier}"
        compteur = compteur + 1

    # Création des métadata
    metadata = None
    if type_fichier.strip(". ") in ["png", "jpg", "jpeg", "tiff", "pdf"]:
        metadata = {
            "Application": "MesVoyages",
            "Auteur": "Xavier Lacour",
            "Date": datetime.now().isoformat(),
            "HSV": json.dumps(
                {
                    "Bornes de luminosité et de saturation": theme,
                    "Teintes possibles": teintes_autorisees,
                }
            ),
            "Qualité de l'image": str(qualite),
            "Granularité maximale": f"{max(gdf['Granu'])}",
        }

    plt.savefig(
        nom,
        dpi=max(min(qualite, 4500), 100),
        bbox_inches="tight",
        metadata=metadata,
        pad_inches=0,
    )
    plt.close(fig)

    if blabla == True:
        print("Terminé.")


## 1.3 -- Renvoie noir ou blanc selon la couleur en entrée ---------------------


def transformer_couleur_texte(bg_color):
    """
    Détermine la couleur de texte optimale (noir ou blanc) en fonction de la couleur de fond donnée en hexadécimal.

    Cette fonction convertit une couleur de fond donnée en format hexadécimal en ses composantes RGB,
    calcule la luminosité de cette couleur selon la formule standard WCAG, puis décide de la couleur
    de texte à utiliser pour assurer une bonne lisibilité. Si la luminosité est faible, le texte sera blanc,
    sinon il sera noir.

    Paramètres :
    – bg_color (str) : La couleur de fond en format hexadécimal (par exemple, "#RRGGBB").

    Retourne :
    – str : La couleur de texte recommandée en format hexadécimal, soit "#FFFFFF" pour blanc, soit "#000000" pour noir.
    """

    # Convertir une couleur hexadécimale en RGB
    r, g, b = [int(bg_color[i : i + 2], 16) for i in (1, 3, 5)]

    # Si la luminosité est faible, mettre du texte blanc, sinon du texte noir
    return "#FFFFFF" if 0.299 * r + 0.587 * g + 0.114 * b < 128 else "#000000"


## 1.4 -- Renvoyer une couleur selon les paramètres de l'application -----------


def renvoyer_couleur_widget(style, teinte, nuances, clair, sombre):
    if style == 0:
        return generer_couleur_aleatoire_hex(preset=nuances, teintes_autorisees=teinte)
    elif style == 1:
        return clair
    else:
        return sombre


## 1.5 -- Fonction de gestion des situations où deux couleurs doivent différer -


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


## 1.6 -- Fonction de couleur du texte selon la siutation ----------------------


def renvoyer_couleur_texte(style, couleur):
    if style == 0:
        return transformer_couleur_texte(couleur)
    elif style == 1:
        return ("#2C2C2C",)
    else:
        return "#FFFFFF"


## 1.7 -- Fonction de création du style complet de l'application ---------------


def utiliser_style_dynamique(
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
        clair="#EBF0F2",
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
            QListWidget {{
            background-color: {couleur_widget_list_fond}; /* Très proche de ton fond principal, mais un peu plus lumineux */
            color: {couleur_widget_list_texte};
            border: none;
            padding: 4px;
            border-radius: 5px;
        }}
        QListWidget::item:selected {{
            background-color: {couleur_widget_list_select}; /* Bleu clair (déjà utilisé dans QPushButton) */
            color: {couleur_widget_list_texte};
            border-radius: 4px;
        }}
        QListWidget::item:hover {{
            background-color: {couleur_widget_list_survol_fond};
            color: {couleur_widget_list_texte};
        }}
        QScrollArea {{
            background-color: {couleur_scroll_area_fond}; 
            color : {couleur_scroll_area_texte};
            border: 2px solid {couleur_scroll_area_bord};
            border-radius: 5px;
        }}
        QScrollBar:vertical {{
            background: {couleur_scroll_area_barre_partie}; /* cohérent avec couleur_box */
            width: 12px;
            margin: 2px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: {couleur_scroll_area_barre}; /* slider2 : bleu-vert soutenu */
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {couleur_scroll_area_barre_survol}; /* slider : bleu-vert doux */
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
            height: 0;
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

        """
