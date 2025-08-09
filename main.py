################################################################################
# MesVoyages                                                                   #
# Exécution de l'application principale principale                             #
################################################################################

import os
import sys
import constantes
import yaml


# Paramères
# Paramètres d'application
application_position_largeur = 250
application_position_hauteur = 40
application_largeur = 750
application_hauteur = 250

## Paramètres d'interface
interface_foncee = False
inclure_emojis_onglets = True
inclure_emojis = True

# Paramètres des statistiques
top_n_pays = None
min_width = 500
min_height: int = 300
n_rangees: int = 9
points_base: int = 15
points_increment: int = 4
lighter_value: int = 150

## Paramètres des cartes
qualite_min = 200
qualite_max = 4000
