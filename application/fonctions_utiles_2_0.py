################################################################################
# Projet de cartes de voyage                                                   #
# 2.0 - Fonctions utiles à l'application                                       #
################################################################################

from PyQt6.QtWidgets import QHBoxLayout, QFrame


def obtenir_clef_par_valeur(dictionnaire, valeur):
    """Retourne la clé associée à une valeur donnée dans un dictionnaire."""
    for clef, val in dictionnaire.items():
        if val == valeur:
            return clef
    return None


def style_bouton_de_suppression(sombre):
    return f"""QPushButton {{
                            background-color:{"#000000" if sombre else "#f8d7da"};
                            color: {"#E6E6E6" if sombre else "#2C2C2C"};
                            font-size: 12px;
                            border: none;
                            border-radius: 5px;
                            padding: 8px;
                            }}
                QPushButton:hover {{
                                    background-color: {"#85040d" if sombre else "#f5c6cb"};
                                  }}
            """


def creer_classement_pays(
    gdf_visite,
    table_superficie,
    granularite: int = 1,
    top_n: int | None = None,
):

    gdf_visite = gdf_visite[gdf_visite["Granu"] == granularite]
    gdf_visite["Visite"] = gdf_visite["Visite"].astype(int)
    gdf_visite["Visite"] = gdf_visite.groupby("Region")["Visite"].transform("max")
    gdf_visite = gdf_visite[gdf_visite["Visite"] == 1]

    gdf_visite = (
        gdf_visite[["Pays", "Region", "Granu", "Visite"]]
        .merge(
            table_superficie,
            how="left",
            left_on=["Pays", "Region"],
            right_on=["NAME_0", f"NAME_{granularite}"],
        )
        .groupby("Pays")[["pct_superficie_dans_pays", "superficie"]]
        .sum()
        .reset_index()
        .sort_values(
            by=["pct_superficie_dans_pays", "superficie"], ascending=[False, False]
        )
    )

    return gdf_visite if top_n is None else gdf_visite.head(top_n)


def creer_ligne_separation(lStretch=1, ligne_largeur=4, rStretch=1):
    layout_temp = QHBoxLayout()
    ligne = QFrame()
    ligne.setFixedHeight(2)
    ligne.setFrameShape(QFrame.Shape.HLine)  # Ligne horizontale
    ligne.setFrameShadow(QFrame.Shadow.Sunken)  # Style de relief
    layout_temp.addStretch(lStretch)
    layout_temp.addWidget(ligne, ligne_largeur)
    layout_temp.addStretch(rStretch)
    return layout_temp
