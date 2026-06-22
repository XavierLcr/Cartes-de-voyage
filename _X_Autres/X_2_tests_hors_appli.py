################################################################################
# Projet de cartes de voyage                                                   #
# _X_Autres/                                                                   #
# X.2 – Script de tests de publication des cartes hors application             #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, sys
from PIL import Image

sys.path.append(os.getcwd())

import constantes

# 1 -- Paramétrisation et import des données -----------------------------------


image = Image.open(
    os.path.join(constantes.direction_donnees_application, "Drapeaux", "France.svg")
).convert("RGB")


# 2 -- Tests -------------------------------------------------------------------
