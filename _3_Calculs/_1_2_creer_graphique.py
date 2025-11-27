################################################################################
# Projet de cartes de voyage                                                   #
# _3_Calculs/                                                                  #
# 3.2 – Fichier de création des graphiques cartes                              #
################################################################################


import os, json, math, textwrap
import matplotlib.pyplot as plt
from datetime import datetime
from shapely.geometry import box

from _0_Utilitaires._0_2_fonctions_graphiques import (
    generer_couleur_aleatoire_hex,
    transformer_couleur_texte,
)


# 1 -- Renvoyer les marges les limites de la carte -----------------------------


def renvoyer_limites_carte(gdf, marge):

    xmin_temp, ymin_temp, xmax_temp, ymax_temp = gdf.total_bounds
    xmin = xmin_temp - marge * (xmax_temp - xmin_temp)
    xmax = xmax_temp + marge * (xmax_temp - xmin_temp)
    ymin = ymin_temp - marge * (ymax_temp - ymin_temp)
    ymax = ymax_temp + marge * (ymax_temp - ymin_temp)

    return xmin, xmax, ymin, ymax


# 2 -- Fonction de limitation des tables complémentaires -----------------------


def selectionner_lieux(gdf, minx, maxx, miny, maxy):

    if gdf is None:
        return gdf
    else:
        return gdf[gdf.intersects(box(minx, miny, maxx, maxy))]


# 3 -- Fonction de création de la carte ----------------------------------------


def creer_nom_fichier(chemin: str, nom: str, max_cartes: int | None):

    # Crée la direction de sauvegarde du résultat si nécessaire
    if not os.path.exists(chemin):
        os.makedirs(chemin)

    # Suppression fichier le plus vieux si necessaire
    if max_cartes is not None:
        fichiers = [
            os.path.join(chemin, f)
            for f in os.listdir(chemin)
            if (
                os.path.isfile(os.path.join(chemin, f))
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

        if len(fichiers) >= max(max_cartes, 1):
            os.remove(min(fichiers, key=os.path.getmtime))

    # Création d'un nom qui non utilisé
    nom = os.path.join(chemin, nom)
    nom_simple, type_fichier = os.path.splitext(nom)
    compteur = 2
    while os.path.exists(nom):
        nom = f"{nom_simple} ({compteur}){type_fichier}"
        compteur = compteur + 1

    return nom


# 4 -- Fonction de création des métadonnées ------------------------------------


def renvoyer_metadonnees(
    nom: str, theme: dict, teintes: list | None, qualite: int, granularite: int
):

    if os.path.splitext(nom)[1].strip(". ") in ["png", "jpg", "jpeg", "tiff", "pdf"]:
        return {
            "Application": "MesVoyages",
            "Auteur": "Xavier Lacour",
            "Date": datetime.now().isoformat(),
            "HSV": json.dumps(
                {
                    "Bornes de luminosité et de saturation": theme,
                    "Teintes possibles": teintes,
                }
            ),
            "Qualité de l'image": str(qualite),
            "Granularité maximale": f"{granularite}",
        }
    else:
        return None


# 5 -- Fonction de création de la carte ----------------------------------------


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

    # Cree le graphique
    if blabla:
        print("Création du graphique.", end=" ")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_axis_off()
    ax.margins(0)
    fig.patch.set_facecolor(couleur_de_fond)

    # Sélection du périmètre – Ajout des pays aux alentours
    xmin, xmax, ymin, ymax = renvoyer_limites_carte(gdf=gdf, marge=0.03)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # Limitation des tables complémentaires
    gdf_monde = selectionner_lieux(
        gdf=gdf_monde, minx=xmin, maxx=xmax, miny=ymin, maxy=ymax
    )
    gdf_eau = selectionner_lieux(
        gdf=gdf_eau, minx=xmin, maxx=xmax, miny=ymin, maxy=ymax
    )

    # Ajout de la carte principale
    gdf.plot(ax=ax, color=gdf["Couleur"], edgecolor="black", linewidth=0.008, zorder=1)

    liste_pays = list(gdf["Pays"].unique())

    if gdf_monde is not None:

        # Ajout des frontières de façon plus marquée
        if blabla:
            print("Ajout des frontières nationales", end="")

        gdf_monde.plot(
            ax=ax,
            color=gdf_monde["name_0"].apply(
                lambda x: (
                    couleur_de_fond
                    if x == "Caspian Sea"
                    else ("none" if x in liste_pays else couleur_pays_contours)
                )
            ),
            edgecolor=gdf_monde["name_0"].apply(
                lambda x: "black" if x in liste_pays else "dimgrey"
            ),
            linewidth=0.04,
            zorder=3,
        )

    if gdf_regions is not None:

        gdf_regions = gdf_regions[
            gdf_regions["name_0"].isin(
                list(gdf.loc[(gdf["Granu"] >= 1), "Pays"].unique())
            )
        ]

        if len(gdf_regions) > 0:

            if blabla:
                print(", des régions", end="")

            gdf_regions.plot(
                ax=ax, color="none", edgecolor="black", linewidth=0.017, zorder=2
            )

    if gdf_eau is not None:

        if blabla:
            print(", des lacs", end="")

        if len(gdf_eau) > 0:
            gdf_eau.plot(ax=ax, color=couleur_lacs, edgecolor="none", alpha=1, zorder=4)

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

    plt.savefig(
        creer_nom_fichier(
            chemin=chemin_impression, nom=nom, max_cartes=max_cartes_additionnelles
        ),
        dpi=max(min(qualite, 4500), 100),
        bbox_inches="tight",
        metadata=renvoyer_metadonnees(
            nom=nom,
            theme=theme,
            teintes=teintes_autorisees,
            qualite=qualite,
            granularite=max(gdf["Granu"]),
        ),
        pad_inches=0,
    )
    plt.close(fig)

    if blabla == True:
        print("Terminé.")
