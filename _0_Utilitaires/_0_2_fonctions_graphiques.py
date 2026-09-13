################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.2 – Fonctions graphiques génériques et utiles à l'application              #
################################################################################


import os, random, math, colorsys
from PIL import Image
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap, QIcon

# 1 -- Générer une couleur aléatoire selon des contraintes HSV -----------------


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


# 2 -- Renvoie noir ou blanc selon la couleur en entrée ------------------------


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
    – str : La couleur de texte recommandée en format hexadécimal, soit "#E5E9F0" pour blanc, soit "#2C2C2C" pour noir.
    """

    # Convertir une couleur hexadécimale en RGB
    r, g, b = [int(bg_color[i : i + 2], 16) for i in (1, 3, 5)]

    # Si la luminosité est faible, mettre du texte blanc, sinon du texte noir
    return "#E5E9F0" if 0.299 * r + 0.587 * g + 0.114 * b < 128 else "#2C2C2C"


# 3 -- Fonction de couleur du texte selon la siutation -------------------------


def renvoyer_couleur_texte(style, couleur):
    if style == 0:
        return transformer_couleur_texte(couleur)
    elif style == 1:
        return transformer_couleur_texte("#FFFFFF")
    else:
        return transformer_couleur_texte("#000000")


# 4 -- Renvoyer une couleur selon les paramètres de l'application --------------


def renvoyer_couleur_widget(style, teinte, nuances, clair, sombre):
    if style == 0:
        return generer_couleur_aleatoire_hex(preset=nuances, teintes_autorisees=teinte)
    elif style == 1:
        return clair
    else:
        return sombre


# 5 -- Récupérer l'image du drapeau --------------------------------------------


## 5.1 -- Récupération du drapeau brut -----------------------------------------


def recuperer_drapeau(chemin: str, pays: str):

    # Construction du nom du fichier
    pays = f"{pays}.png"

    # Chargement (si le fichier existe)
    if pays in os.listdir(chemin):
        return Image.open(os.path.join(chemin, pays)).convert("RGB")
    else:
        return None


## 5.2 -- Exctraction d'une couleur --------------------------------------------


def couleur_depuis_drapeau(drapeau):

    if drapeau is not None:
        return random.choice(list(drapeau.getdata()))
    else:
        return None


## 5.3 -- Image en QIcon -------------------------------------------------------


def recuperer_drapeau_icon(
    chemin: str, pays: str, taille: int = 16, fallback_onu: bool = False
):
    fichier = f"{pays}.png"
    chemin_complet = os.path.join(chemin, fichier)

    if os.path.isfile(chemin_complet):
        pixmap = QPixmap(chemin_complet)
        # Redimensionner en gardant un rendu net
        pixmap = pixmap.scaled(
            taille,
            taille,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        return QIcon(pixmap)

    if fallback_onu == True:

        return recuperer_drapeau_icon(
            chemin=chemin, pays="United Nations", taille=taille, fallback_onu=False
        )

    return None


## 5.4 -- Création d'un dictionnaire des drapeaux ------------------------------


def creer_dictionnaire_drapeaux(
    chemin: str, liste_pays: list | None, taille: int, fallback_onu: bool
):

    # Initialisation du résultat
    dict_temp = {}

    # Liste des fichiers
    if liste_pays is None:
        liste_pays = sorted(os.listdir(chemin))

    # Boucle sur les fichiers disponibles
    for image_temp in liste_pays:

        # Nom du pays
        pays_temp, _ = os.path.splitext(image_temp)

        # Ajout au dictionnaire
        dict_temp[pays_temp] = recuperer_drapeau_icon(
            chemin=chemin, pays=pays_temp, taille=taille, fallback_onu=fallback_onu
        )

    # Renvoi
    return dict_temp


# 6 -- RGB vers hexadécimales --------------------------------------------------


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


# 7 -- Fonction d'interpolation de couleurs ------------------------------------


def interpoler_couleurs(
    couleurs,
    poids=None,
    retour="qcolor",
):
    """
    Interpole plusieurs couleurs en espace HSV.

    Paramètres
    ----------
    couleurs : list | tuple | dict
        Couleurs à interpoler. Les valeurs peuvent être des QColor ou des
        chaînes hexadécimales.

    poids : list | tuple | dict | None
        Poids associés aux couleurs. Si None, toutes les couleurs ont le
        même poids. Les poids sont normalisés automatiquement.

    retour : {"qcolor", "hexa", "hsv"}
        Format de sortie :
        - "qcolor" : renvoie un QColor ;
        - "hexa"   : renvoie une chaîne hexadécimale ;
        - "hsv"    : renvoie un tuple (h, s, v).

        Pour "hsv", h, s et v sont dans [0, 1].

    Retour
    ------
    QColor | str | tuple
        Couleur interpolée dans le format demandé.
    """

    # ------------------------------------------------------------------
    # Préparation des couleurs
    # ------------------------------------------------------------------

    if isinstance(couleurs, dict):
        couleurs = list(couleurs.values())

    couleurs = list(couleurs)

    if not couleurs:
        couleurs = ["#FFFFFF"]

    couleurs = [
        couleur if isinstance(couleur, QColor) else QColor(couleur)
        for couleur in couleurs
    ]

    if any(not couleur.isValid() for couleur in couleurs):
        raise ValueError("Une ou plusieurs couleurs sont invalides.")

    # ------------------------------------------------------------------
    # Préparation des poids
    # ------------------------------------------------------------------

    if poids is None:
        poids = [1.0] * len(couleurs)

    elif isinstance(poids, dict):
        poids = list(poids.values())

    else:
        poids = list(poids)

    somme_poids = sum(poids)

    if (
        len(poids) != len(couleurs)
        or any(poids_i < 0 for poids_i in poids)
        or somme_poids <= 0
    ):
        return interpoler_couleurs(couleurs=couleurs, poids=None, retour=retour)

    poids = [poids_i / somme_poids for poids_i in poids]

    # ------------------------------------------------------------------
    # Conversion HSV
    # ------------------------------------------------------------------

    hsv = []

    for couleur in couleurs:
        h, s, v, _ = couleur.getHsvF()

        # QColor renvoie -1 pour la teinte des couleurs achromatiques
        # (gris, blanc, noir...). On lui attribue ici une teinte neutre
        # pour éviter de faire tourner artificiellement la couleur.
        if h < 0:
            h = 0.0

        hsv.append((h, s, v))

    # ------------------------------------------------------------------
    # Interpolation de la teinte
    # ------------------------------------------------------------------

    # On calcule la moyenne circulaire des teintes sur le cercle HSV.
    # Cela évite par exemple que 350° + 10° donnent artificiellement 180°.

    x = 0.0
    y = 0.0

    for (h, _, _), poids_i in zip(hsv, poids):
        angle = h * math.tau
        x += math.cos(angle) * poids_i
        y += math.sin(angle) * poids_i

    if abs(x) < 1e-12 and abs(y) < 1e-12:
        h = 0.0
    else:
        h = (math.atan2(y, x) / math.tau) % 1.0

    # ------------------------------------------------------------------
    # Interpolation linéaire de saturation et luminosité
    # ------------------------------------------------------------------

    s = sum(s_i * poids_i for (_, s_i, _), poids_i in zip(hsv, poids))

    v = sum(v_i * poids_i for (_, _, v_i), poids_i in zip(hsv, poids))

    hsv_resultat = (h, s, v)

    # ------------------------------------------------------------------
    # Format de sortie
    # ------------------------------------------------------------------

    if retour == "hsv":
        return hsv_resultat

    resultat = QColor()
    resultat.setHsvF(h, s, v)

    if retour == "qcolor":
        return resultat

    if retour == "hexa":
        return resultat.name()

    return "#FFFFFF"
