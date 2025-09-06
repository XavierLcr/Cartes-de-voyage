################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/                                                                #
# 4.2 – Création du .exe de l'application                                      #
################################################################################


from cx_Freeze import setup, Executable
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constantes


# Définition de la liste des fichiers/dossiers à inclure
include_files = [
    r"C:\Users\xaruo\Documents\Voyages\liste_pays_departements.yaml",
    r"C:\Users\xaruo\Documents\Voyages\liste_pays_regions.yaml",
    r"C:\Users\xaruo\Documents\Voyages\LICENSE – MesVoyages.md",
    (constantes.direction_donnees_application, "Données application"),
]
for f in os.listdir(constantes.direction_donnees_pickle):
    if f.endswith(".pkl") and not any(chiffre in f for chiffre in ["3", "4", "5"]):
        chemin_absolu = os.path.join(constantes.direction_donnees_pickle, f)
        chemin_destination = f"Données pickle/{f}"
        include_files.append((chemin_absolu, chemin_destination))


setup(
    name="MesVoyages",
    version=constantes.version_logiciel,
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
            "include_files": include_files,
        }
    },
    executables=[
        Executable(
            "PyQt_application_main.py",
            icon=os.path.join(
                constantes.direction_donnees_application, "icone_application.ico"
            ),
            target_name="MesVoyages.exe",
            base="Win32GUI",
        )
    ],
)
