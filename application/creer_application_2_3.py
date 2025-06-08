from cx_Freeze import setup, Executable
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constantes

setup(
    name="MesVoyages",
    version="2.0",
    description="Permet de créer ses cartes de voyages.",
    options={
        "build_exe": {
            "packages": [
                "os",
                "pandas",
                "sys",
                "PyQt6",
                "geopandas",
                "random",
                "matplotlib",
                "colorsys",
                "yaml",
                "gc",
                "numpy",
                "time",
                "pickle",
                "warnings",
                "json",
            ],
            "include_files": [
                r"C:\Users\xaruo\Documents\Voyages\liste_pays_departements.yaml",
                r"C:\Users\xaruo\Documents\Voyages\liste_pays_regions.yaml",
                r"C:\Users\xaruo\Documents\Voyages\LICENSE – MesVoyages.md",
                (constantes.direction_donnees_pickle, "Données pickle"),
                (constantes.direction_donnees_application, "Données application"),
            ],
        }
    },
    executables=[
        Executable(
            "PyQt_application.py",
            icon=os.path.join(
                constantes.direction_donnees_application, "icone_france.ico"
            ),
            target_name="MesVoyages.exe",
            base="Win32GUI",
        )
    ],
)
