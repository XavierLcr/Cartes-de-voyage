################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/                                                              #
# 2.6 – Script de création du logo de l'application                            #
################################################################################


import os, sys
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from constantes import direction_donnees_application
from clefs_et_mots_de_passe import png_pour_icone


# 1 -- Import des données ------------------------------------------------------


image = Image.open(png_pour_icone)


# 2 -- Recadrage de l'image ----------------------------------------------------


## 2.1 -- Fonction de création de l'icône de l'application ---------------------


def rendre_carre(image: Image.Image, mode: str = "marges") -> Image.Image:
    """
    Transforme une image en carré.

    Args:
        image (Image.Image): L'image d'entrée (PIL).
        mode (str): "recadrer" pour élaguer les bords,
                    "marges" pour ajouter des marges transparentes.

    Returns:
        Image.Image: Une image carrée.
    """

    largeur, hauteur = image.size
    cote = min(largeur, hauteur) if mode == "recadrer" else max(largeur, hauteur)

    if mode == "recadrer":
        gauche = (largeur - cote) // 2
        haut = (hauteur - cote) // 2
        return image.crop(box=(gauche, haut, gauche + cote, haut + cote))

    elif mode == "marges":
        nouvelle_image = Image.new("RGBA", (cote, cote), (0, 0, 0, 0))  # transparent
        nouvelle_image.paste(image, ((cote - largeur) // 2, (cote - hauteur) // 2))
        return nouvelle_image

    else:
        raise ValueError("Le mode doit être 'recadrer' ou 'marges'")


## 2.2 -- Application ----------------------------------------------------------


image = rendre_carre(image=image, mode="recadrer")


# 3 -- Export ------------------------------------------------------------------


image.save(
    os.path.join(direction_donnees_application, "icone_application.ico"),
    format="ICO",
    sizes=[(256, 256)],
)
