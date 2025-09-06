################################################################################
# Projet de cartes de voyage                                                   #
# _2_Préparation/                                                              #
# 2.6 – Script de création du logo de l'application                            #
################################################################################


import os, sys
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constantes


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
        droite = gauche + cote
        bas = haut + cote
        return image.crop(box=(gauche, haut, droite, bas))

    elif mode == "marges":
        nouvelle_image = Image.new("RGBA", (cote, cote), (0, 0, 0, 0))  # transparent
        position = ((cote - largeur) // 2, (cote - hauteur) // 2)
        nouvelle_image.paste(image, position)
        return nouvelle_image

    else:
        raise ValueError("Le mode doit être 'recadrer' ou 'marges'")


# Ouverture de l'image à utiliser
img = Image.open(
    os.path.join(
        "C:\\Users\\xaruo",
        "Documents",
        "Voyages",
        "Xavier – Cartes de voyage",
        "France, Monaco et Îles Anglo-Normandes",
        "Xavier – France, Monaco et Îles Anglo-Normandes (5).png",
    )
)


carre = rendre_carre(img, mode="recadrer")
carre.save(
    os.path.join(constantes.direction_donnees_application, "icone_france.ico"),
    format="ICO",
    # sizes=[(256, 256)],
    sizes=[(256, 256)],
)
