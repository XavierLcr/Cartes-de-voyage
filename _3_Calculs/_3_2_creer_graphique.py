################################################################################
# Projet de cartes de voyage                                                   #
# _3_Calculs/                                                                  #
# 3.2 – Fichier de création des graphiques cartes                              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, json, textwrap
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import box
from PIL import Image
from shapely.ops import polylabel

from _0_Utilitaires._0_1_fonctions_utiles_gen import formater_temps_actuel
from _0_Utilitaires._0_2_fonctions_graphiques import (
    generer_couleur_aleatoire_hex,
    transformer_couleur_texte,
)
from _0_Utilitaires._0_6_fonctions_utiles_traductions import traduire_pays
from _3_Calculs._3_3_envoyer_email import envoyer_email_avec_piece_jointe_smtp

# 1 -- Renvoyer les marges les limites de la carte -----------------------------


def renvoyer_limites_carte(gdf, marge):

    xmin_temp, ymin_temp, xmax_temp, ymax_temp = gdf.total_bounds
    xmin = xmin_temp - marge * (xmax_temp - xmin_temp)
    xmax = xmax_temp + marge * (xmax_temp - xmin_temp)
    ymin = ymin_temp - marge * (ymax_temp - ymin_temp)
    ymax = ymax_temp + marge * (ymax_temp - ymin_temp)

    return xmin, xmax, ymin, ymax


# 2 -- Fonction de limitation des tables complémentaires -----------------------


### Fonction de gestion des cas extrêmes ---------------------------------------


def minmax_lon_wrap(gdf, minimum):
    """
    Pour un GeoDataFrame, renvoie :
    - le min positif > 0 si disponible
    - sinon le max négatif < 0

    Prend en compte toutes les géométries du GeoDataFrame.
    """
    # Exploser les géométries multipolygones pour traiter chaque partie séparément
    gdf_exp = gdf.explode(index_parts=False)

    # Récupérer toutes les longitudes
    longitudes = []
    for geom in gdf_exp.geometry:
        try:
            # Pour polygones et multipoints
            coords = getattr(geom, "exterior", geom).coords
        except AttributeError:
            # Pour points simples
            coords = [geom.coords[0]]
        for x, y in coords:
            longitudes.append(x)

    # Filtrer longitudes positives et négatives
    pos_lon = [x for x in longitudes if x > 0]
    neg_lon = [x for x in longitudes if x < 0]

    if minimum and pos_lon:
        return min(pos_lon)
    elif minimum:
        return -180
    elif (not minimum) and neg_lon:
        return max(neg_lon)
    else:
        180


### Fonction générique ---------------------------------------------------------


def selectionner_lieux(gdf, gdf_ref, extreme, marge):

    minx, maxx, miny, maxy = renvoyer_limites_carte(gdf=gdf_ref, marge=marge)

    if gdf is None:
        return gdf
    elif extreme:

        return gdf[
            (
                gdf.intersects(
                    box(minmax_lon_wrap(gdf=gdf_ref, minimum=True), miny, 180, maxy)
                )
            )
            | (
                gdf.intersects(
                    box(-180, miny, minmax_lon_wrap(gdf=gdf_ref, minimum=False), maxy)
                )
            )
        ]

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


def renvoyer_metadonnees(nom: str, **kwargs) -> dict | None:

    if os.path.splitext(nom)[1].strip(". ") not in [
        "png",
        "jpg",
        "tiff",
        "pdf",
    ]:
        return None

    # Métadonnées par défaut
    metadonnees = {
        "Application": "MesVoyages",
        "Auteur": "Xavier Lacour",
        "Date": formater_temps_actuel(),
    }

    # Ajoute les métadonnées depuis kwargs
    if "theme" in kwargs:
        metadonnees["HSV"] = json.dumps(
            {
                "Bornes de luminosité et de saturation": kwargs["theme"],
                "Teintes possibles": kwargs.get("teintes"),
            }
        )

    if "qualite" in kwargs:
        metadonnees["Résolution de l'image"] = str(kwargs["qualite"])

    if "granularite" in kwargs:
        metadonnees["Granularité maximale"] = str(kwargs["granularite"])

    # Ajoute les autres kwargs (sauf ceux déjà traités)
    for key, value in kwargs.items():
        if key not in {"theme", "teintes", "qualite", "granularite"}:
            metadonnees[key] = value

    return metadonnees


# 5 -- Recentrer la longitude d'une table --------------------------------------


## 5.1 -- Fonction de calcul des coordonnées du centre -------------------------


def calculer_centre(gdf):
    """
    Calcule le centre géographique (longitude, latitude) d'un GeoDataFrame.

    Retour :
    - tuple (lon_centre, lat_centre)
    """

    def ligne_valide(geom):
        # Récupérer toutes les coordonnées
        coords = []
        if geom.geom_type == "Polygon":
            coords = list(geom.exterior.coords)
        elif geom.geom_type == "MultiPolygon":
            for poly in geom.geoms:
                coords.extend(list(poly.exterior.coords))
        # Vérifier si une longitude est trop proche de ±180
        return not any(abs(x) >= 179.75 for x, y in coords)

    gdf_filtre = gdf[gdf.geometry.apply(ligne_valide)]

    if gdf_filtre.empty:
        # fallback si toutes les lignes sont filtrées
        return (0, 0)

    minx, miny, maxx, maxy = gdf_filtre.total_bounds
    return (minx + maxx) / 2, (miny + maxy) / 2


## 5.2 -- Calcul de reprojection d'une carte -----------------------------------


def reprojeter_gdf(gdf, type_proj: str, centre=None):
    """
    Reprojette un GeoDataFrame selon le type de projection choisi.

    Paramètres :
    - gdf : GeoDataFrame à reprojeter
    - type_proj : type de projection. Options disponibles :
        "laea"   : Lambert Azimuthal Equal-Area
        "lcc"    : Lambert Conformal Conic
        "mercator" : Mercator
        "robinson" : Robinson
        "wgs84"  : lat/lon WGS84 (EPSG:4326)
        "auto"   : choisit automatiquement selon la latitude
        None     : ne fait rien, renvoie le GeoDataFrame tel quel
    - centre : tuple (lon, lat) pour centrer la projection. Si None, centre calculé automatiquement.

    Retour :
    - GeoDataFrame reprojeté
    """

    # Si le gdf est None, on renvoie None
    if gdf is None:
        return gdf

    # Si type_proj est None, on renvoie le GeoDataFrame sans modification
    if type_proj is None:
        return gdf.copy()

    # Calcul du centre si nécessaire
    lon, lat = centre if centre is not None else calculer_centre(gdf)

    # Dictionnaire des projections statiques
    projections = {
        "mercator": "EPSG:3395",
        "wgs84": "EPSG:4326",
        "arctic_ps": f"EPSG:3995",
        "antarctic_ps": f"EPSG:3786",
    }

    # Reprojeter et renvoyer
    return gdf.copy().to_crs(projections.get(type_proj, "wgs84"))


# 6 -- Ajout des noms des territoires ------------------------------------------


## 6.1 -- Fonction de séparation des exclaves ----------------------------------


def point_isolement(geom):
    if geom.geom_type == "MultiPolygon":
        geom = max(geom.geoms, key=lambda g: g.area)

    return polylabel(geom)


## 6.2 -- Fonction d'ajout des noms des territoires ----------------------------


def ajouter_labels_carte(
    ax,
    gdf,
    colonne_label="subdivision",
    colonne_couleur="couleur",
    largeur_min=5,
    facteur_retour_ligne=3,
    espacement_lignes=0.8,
    facteur_taille=0.5,
    seuil_superficie: float = 0.3,
    langue: None | str = None,
    dict_trad_pays: dict = {},
):
    """
    Ajoute automatiquement des labels centrés sur une carte GeoPandas.

    Parameters
    ----------
    ax : matplotlib axis
        Axe matplotlib.

    gdf : GeoDataFrame
        GeoDataFrame contenant les géométries.

    colonne_label : str
        Colonne contenant les labels.

    colonne_couleur : str
        Colonne contenant les couleurs associées.

    largeur_min : int
        Largeur minimale des retours à la ligne.

    facteur_retour_ligne : float
        Facteur utilisé pour le wrapping du texte.

    espacement_lignes : float
        Espacement vertical des lignes.

    facteur_taille : float
        Facteur de taille du texte.

    """

    gdf = gdf.copy()

    # Dimensions des géométries
    bounds = gdf.geometry.bounds
    gdf["surface"] = gdf.geometry.area

    gdf["largeur"] = bounds["maxx"] - bounds["minx"]
    gdf["hauteur"] = bounds["maxy"] - bounds["miny"]

    # Taille du texte adaptative
    gdf["taille_texte"] = (
        (np.minimum(gdf["largeur"], gdf["hauteur"]) * facteur_taille)
        / np.sqrt(gdf[colonne_label].str.len())
    ).clip(lower=0.005, upper=2)

    # Centroïdes
    centroïdes = gdf.geometry.apply(point_isolement)

    for x, y, label, couleur, taille, largeur, surface in zip(
        centroïdes.x,
        centroïdes.y,
        gdf[colonne_label],
        gdf[colonne_couleur],
        gdf["taille_texte"],
        gdf["largeur"],
        gdf["surface"],
    ):

        if surface < seuil_superficie:
            continue

        label_retour_ligne = "\n".join(
            textwrap.wrap(
                traduire_pays(pays=label, langue=langue, referentiel=dict_trad_pays),
                width=max(largeur_min, int(largeur * facteur_retour_ligne)),
                break_long_words=False,
            )
        )

        ax.text(
            x,
            y,
            label_retour_ligne,
            fontsize=taille,
            fontfamily="Lucida Handwriting",
            ha="center",
            va="center",
            color=transformer_couleur_texte(couleur),
            linespacing=espacement_lignes,
            zorder=5,
        )


# 7 -- Fonction de création de la carte ----------------------------------------


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
    limite_n_cartes: int | None = 10,
    afficher_nom_lieu: bool = True,
    marge_carte=0.03,
    reprojeter: bool = True,
    adresse_email: str | None = None,
    langue: None | str = None,
    dict_trad_pays: dict = {},
):
    r"""
    Crée une image de carte à partir d'un GeoDataFrame et l'exporte dans un fichier d'image.

    Cette fonction génère une carte basée sur un GeoDataFrame donné, applique une couleur spécifique à chaque ligne
    (en fonction de la colonne "visite"), puis exporte l'image dans un fichier au format spécifié par le nom de fichier.

    Paramètres :
    – gdf (GeoDataFrame) : Le GeoDataFrame contenant la carte à créer.
    – gdf_monde (GeoDataFrame, optionnel) : Le GeoDataFrame contenant les frontières nationales. Par défaut, `None`.
    – gdf_regions (GeoDataFrame, optionnel) : Le GeoDataFrame contenant les frontières régionales. Par défaut, `None`.
    – gdf_eau (GeoDataFrame, optionnel) : Le GeoDataFrame contenant les surfaces d'eau. Par défaut, `None`.
    – theme (dict, optionnel) : Un dictionnaire définissant les paramètres de luminosité et de saturation pour le thème de la carte. Par défaut, il contient des valeurs prédéfinies pour la luminosité et la saturation.
    – teintes_autorisees (list, optionnel) : Une liste de teintes spécifiques (valeurs comprises entre 0.0 et 1.0) qui limitent les couleurs générées à certains types (par exemple, pour cibler certaines nuances). Par défaut, `None`, ce qui signifie que toutes les teintes peuvent être utilisées.
    – couleur_non_visites (str) : La couleur à utiliser pour les éléments où la variable "visite" est False (par exemple, couleur grise pour les éléments non visités). Par défaut, `"#ecebed"`.
    – couleur_de_fond (str) : La couleur de fond de la carte. Par défaut, `"#FFFFFF"`.
    – couleur_lacs (str) : La couleur utilisée pour les lacs et autres plans d'eau. Par défaut, `"#cee3f5"`.
    – chemin_impression (str) : Le chemin où le fichier d'image sera sauvegardé. Par défaut, le répertoire du fichier courant.
    – nom (str) : Le nom du fichier image exporté. Par défaut, "Carte.jpg".
    – qualite (int) : La qualité de l'image exportée, exprimée en DPI (points par pouce). Par défaut, 400 DPI.
    – blabla (bool, optionnel) : Un paramètre booléen permettant l'affichage du suivi d'éxecution de la fonction. Par défaut, `True`.
    – limite_n_cartes (int, optionnel) : Le nombre maximum de cartes additionnelles à générer. Par défaut, `10`.

    Retourne :
    – Aucune valeur retournée, mais l'image est enregistrée à l'emplacement spécifié dans chemin_impression.
    """

    # Pays présents
    liste_pays = list(gdf["Pays"].unique())

    # On ajoute la couleur de chaque ligne
    gdf["couleur"] = gdf["visite"].apply(
        lambda x: (
            generer_couleur_aleatoire_hex(
                preset=theme,
                teintes_autorisees=teintes_autorisees,
            )
            if x
            else couleur_non_visites
        )
    )
    # Gestion de la mer Caspienne
    gdf.loc[gdf["Pays"] == "Caspian Sea", "couleur"] = couleur_de_fond

    # Limitation des tables complémentaires
    gdf_monde = selectionner_lieux(
        gdf=gdf_monde, gdf_ref=gdf, extreme=reprojeter, marge=marge_carte
    )
    gdf_eau = selectionner_lieux(
        gdf=gdf_eau, gdf_ref=gdf, extreme=reprojeter, marge=marge_carte
    )

    # Reprojection des cartes si néessaire
    if reprojeter:
        centre = calculer_centre(gdf)
        type_proj = "antarctic_ps" if centre[1] < 0 else "arctic_ps"
        gdf = reprojeter_gdf(gdf=gdf, type_proj=type_proj, centre=centre)
        gdf_eau = reprojeter_gdf(gdf=gdf_eau, type_proj=type_proj, centre=centre)
        gdf_monde = reprojeter_gdf(gdf=gdf_monde, type_proj=type_proj, centre=centre)
        gdf_regions = reprojeter_gdf(
            gdf=gdf_regions, type_proj=type_proj, centre=centre
        )
        marge_carte = 0.75 * marge_carte

    # Crée le graphique
    if blabla:
        print("Création du graphique.", end=" ")

    # Sélection du périmètre – Ajout des pays aux alentours
    xmin, xmax, ymin, ymax = renvoyer_limites_carte(gdf=gdf, marge=marge_carte)
    fig, ax = plt.subplots(figsize=(10, 10 / ((xmax - xmin) / (ymax - ymin))))
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    ax.set_axis_off()
    ax.margins(0)
    fig.patch.set_facecolor(couleur_de_fond)

    # Ajout de la carte principale
    gdf.plot(ax=ax, color=gdf["couleur"], edgecolor="black", linewidth=0.008, zorder=1)

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
        ajouter_labels_carte(
            ax=ax,
            gdf=gdf,
            colonne_label="subdivision",
            colonne_couleur="couleur",
            largeur_min=5,
            facteur_retour_ligne=3,
            espacement_lignes=0.8,
            facteur_taille=0.5,
            langue=langue,
            dict_trad_pays=dict_trad_pays,
        )

    # Enregistrer la carte dans un fichier sans l'afficher
    if blabla:
        print(". Sauvegarde de l'image.", end=" ")

    nom_fig = creer_nom_fichier(
        chemin=chemin_impression, nom=nom, max_cartes=limite_n_cartes
    )
    plt.savefig(
        nom_fig,
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

    if reprojeter:
        image = Image.open(nom_fig)
        image = image.rotate(90 * (2 * (centre[0] < 0) - 1), expand=True)
        image.save(nom_fig)

    if adresse_email is not None:

        if blabla:
            print("Envoi par e-mail.")

        envoyer_email_avec_piece_jointe_smtp(
            email_destinataire=adresse_email,
            sujet=os.path.splitext(nom)[0],
            contenu="",
            chemin_fichier=chemin_impression,
            nom_fichier_destinataire=os.path.basename(nom_fig),
        )

    if blabla == True:
        print("Terminé.")
