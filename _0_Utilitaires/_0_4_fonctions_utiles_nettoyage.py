################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.4 – Fonctions utiles au nettoyage d'une table de données                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


# 1 -- Remplacement des noms des pays dans une colonne -------------------------


### Dictionnaire de mapping ----------------------------------------------------


mapping_pays = {
    "Aland Islands": "Åland",
    "Argentina urban": "Argentina",
    "Bahamas, The": "Bahamas",
    "Bahamas, The ": "Bahamas",
    "The Bahamas": "Bahamas",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Brunei Darussalam": "Brunei",
    "Cape Verde": "Cabo Verde",
    "Central African Republic CAR": "Central African Republic",
    "Chili": "Chile",
    "Cocos (Keeling) Islands": "Cocos Islands",
    "Congo, Dem. Rep.": "Democratic Republic of the Congo",
    "Dem. Rep. Congo": "Democratic Republic of the Congo",
    "Congo Democratic Republic": "Democratic Republic of the Congo",
    "Congo, Democratic Republic of the": "Democratic Republic of the Congo",
    "Congo": "Republic of the Congo",
    "Congo Brazzaville": "Republic of the Congo",
    "Congo, Rep.": "Republic of the Congo",
    "Congo, Republic of the ": "Republic of the Congo",
    "Republic of Congo": "Republic of the Congo",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Ivory Coast": "Côte d'Ivoire",
    "Curacao": "Curaçao",
    "Czech Republic": "Czechia",
    "Egypt, Arab Rep.": "Egypt",
    "Eswatini": "Swaziland",
    "Faeroe Islands": "Faroe Islands",
    "FInland": "Finland",
    "Gambia, The": "Gambia",
    "The Gambia": "Gambia",
    "Guinea Bissau": "Guinea-Bissau",
    "Holy See": "Vatican City",
    "Hong Kong SAR, China": "Hong Kong",
    "Iran, Islamic Rep.": "Iran",
    "Korea, North": "North Korea",
    "Korea, Dem. People's Rep.": "North Korea",
    "Korea, Rep.": "South Korea",
    "Korea, South": "South Korea",
    "Kyrgyz Republic": "Kyrgyzstan",
    "Lao PDR": "Laos",
    "Lao": "Laos",
    "Macedonia": "North Macedonia",
    "Mexico": "México",
    "Micronesia, Fed. Sts.": "Micronesia",
    "Micronesia, Federated States of ": "Micronesia",
    "Federated States of Micronesia": "Micronesia",
    "Netherlands Antilles": "Bonaire, Sint Eustatius and Saba",
    "Northern Marianas": "Northern Mariana Islands",
    "Pitcairn": "Pitcairn Islands",
    "Puerto Rico (US)": "Puerto Rico",
    "Russian Federation": "Russia",
    "Reunion": "Réunion",
    "St. Martin (French part)": "Saint-Martin",
    "Sint Maarten (Dutch part)": "Sint Maarten",
    "Sao Tome and Principe": "São Tomé and Príncipe",
    "Sao Tome & Principe": "São Tomé and Príncipe",
    "Slovak Republic": "Slovakia",
    "Saint Barthelemy": "Saint-Barthélemy",
    "Saint Helena, Ascension, and Tristan da Cunha": "Saint Helena, Ascension and Tris",
    "St. Kitts and Nevis": "Saint Kitts and Nevis",
    "St. Lucia": "Saint Lucia",
    "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines",
    "Syrian Arab Republic": "Syria",
    "Timor Leste": "Timor-Leste",
    "East Timor": "Timor-Leste",
    "Turkiye": "Turkey",
    "Turks & Caicos Islands": "Turks and Caicos Islands",
    "United States of America": "United States",
    "Venezuela, RB": "Venezuela",
    "Virgin Islands (U.S.)": "Virgin Islands, US",
    "U.S. Virgin Islands": "Virgin Islands, US",
    "Viet Nam": "Vietnam",
    "Wallis and Futuna Islands": "Wallis and Futuna",
    "West Bank and Gaza": "Palestine",
    "Palestinian territories": "Palestine",
    "State of Palestine": "Palestine",
    "Yemen, Rep.": "Yemen",
}


### Fonction générique de remplacement de valeurs dans une colonne -------------


def remplacer_valeurs_colonne(df, colonne, mapping):
    """
    Remplace les valeurs d'une colonne selon un dictionnaire.

    Args:
        df (pd.DataFrame): ton DataFrame
        colonne (str): nom de la colonne à modifier
        mapping (dict): dictionnaire {ancien_nom: nouveau_nom}

    Returns:
        pd.DataFrame: le DataFrame modifié
    """
    df[colonne] = df[colonne].replace(mapping)
    return df
