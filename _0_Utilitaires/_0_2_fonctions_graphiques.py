################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.2 – Fonctions graphiques génériques et utiles à l'application              #
################################################################################


import os, random, colorsys, re
from PIL import Image

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
    – str : La couleur de texte recommandée en format hexadécimal, soit "#FFFFFF" pour blanc, soit "#000000" pour noir.
    """

    # Convertir une couleur hexadécimale en RGB
    r, g, b = [int(bg_color[i : i + 2], 16) for i in (1, 3, 5)]

    # Si la luminosité est faible, mettre du texte blanc, sinon du texte noir
    return "#FFFFFF" if 0.299 * r + 0.587 * g + 0.114 * b < 128 else "#000000"


# 3 -- Fonction de couleur du texte selon la siutation -------------------------


def renvoyer_couleur_texte(style, couleur):
    if style == 0:
        return transformer_couleur_texte(couleur)
    elif style == 1:
        return ("#2C2C2C",)
    else:
        return "#FFFFFF"


# 4 -- Renvoyer une couleur selon les paramètres de l'application --------------


def renvoyer_couleur_widget(style, teinte, nuances, clair, sombre):
    if style == 0:
        return generer_couleur_aleatoire_hex(preset=nuances, teintes_autorisees=teinte)
    elif style == 1:
        return clair
    else:
        return sombre


# 5 -- Récupérer l'image du drapeau --------------------------------------------


def recuperer_drapeau(chemin: str, pays: str):

    # Construire le motif regex (insensible à la casse)
    motif = re.compile(rf".*{re.escape(pays)}.*", re.IGNORECASE)

    # Parcourir les fichiers du dossier
    for fichier in os.listdir(chemin):
        if motif.search(fichier):
            couleurs = list(
                Image.open(os.path.join(chemin, fichier)).convert("RGB").getdata()
            )
            return random.choice(couleurs)

    # Si le fichier n'est pas trouvé
    return None


# 6 -- RGB vers hexadécimales --------------------------------------------------


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)
