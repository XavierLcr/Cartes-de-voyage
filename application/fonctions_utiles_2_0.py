def obtenir_clef_par_valeur(dictionnaire, valeur):
    """Retourne la clé associée à une valeur donnée dans un dictionnaire."""
    for clef, val in dictionnaire.items():
        if val == valeur:
            return clef
    return None


def creer_classement_pays(gdf_visite, table_superficie, granularite=1, top_n=10):

    gdf_visite = gdf_visite[gdf_visite["Granu"] == granularite]
    gdf_visite["Visite"] = gdf_visite["Visite"].astype(int)
    gdf_visite["Visite"] = gdf_visite.groupby("Region")["Visite"].transform("max")
    gdf_visite = gdf_visite[gdf_visite["Visite"] == 1]

    gdf_visite = gdf_visite[["Pays", "Region", "Granu", "Visite"]].merge(
        table_superficie,
        how="left",
        left_on=["Pays", "Region"],
        right_on=["NAME_0", f"NAME_{granularite}"],
    )

    gdf_visite = (
        gdf_visite.groupby("Pays")[["pct_superficie_dans_pays", "superficie"]]
        .sum()
        .reset_index()
    )

    gdf_visite = gdf_visite.sort_values(
        by=["pct_superficie_dans_pays", "superficie"], ascending=[False, False]
    ).head(top_n)

    return gdf_visite
