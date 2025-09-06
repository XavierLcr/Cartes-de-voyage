################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/                                                                #
# 4.2 – Création du .exe de l'application                                      #
################################################################################


from cx_Freeze import setup, Executable
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from constantes import (
    direction_donnees_geographiques,
    direction_donnees_application,
    direction_donnees_traductions,
    direction_donnees_autres,
    version_logiciel,
)


setup(
    name="Mes Voyages",
    version=version_logiciel,
    description="Créez facilement vos cartes de voyages personnalisées et suivez vos aventures autour du monde !",
    options={
        "build_exe": {
            "build_exe": r"C:\Users\xaruo\Documents\Voyages\Application",
            "packages": [
                "os",
                "sys",
                "gc",
                "time",
                "threading",
                "warnings",
                "copy",
                "PyQt6",
                "numpy",
                "pandas",
                "geopandas",
                "math",
                "random",
                "matplotlib",
                "colorsys",
                "yaml",
                "pickle",
                "json",
                "textwrap",
            ],
            # Liste des fichiers/dossiers à inclure
            "include_files": (
                # YAMLs des régions et départements
                [
                    os.path.join(direction_donnees_application, nom)
                    for nom in [
                        "liste_pays_granularite_1.yaml",
                        "liste_pays_granularite_2.yaml",
                    ]
                ]
                + [
                    # Licence
                    os.path.join(direction_donnees_autres, "LICENSE – MesVoyages.md"),
                    # Paramètres, interface, ...
                    (direction_donnees_application, "2 – Données application"),
                    # Traductions
                    (direction_donnees_traductions, "3 – Traductions"),
                ]
                # Données pickle des frontières géographiques
                + [
                    (
                        os.path.join(direction_donnees_geographiques, f),
                        os.path.join("1 – Données géographiques", f),
                    )
                    for f in os.listdir(direction_donnees_geographiques)
                    if not any(chiffre in f for chiffre in "345")
                ]
            ),
        }
    },
    executables=[
        Executable(
            "PyQt_application_main.py",
            icon=os.path.join(direction_donnees_application, "icone_application.ico"),
            target_name="Mes Voyages.exe",
            base="Win32GUI",
        )
    ],
)
