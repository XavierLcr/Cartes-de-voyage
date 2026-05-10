################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.9 – Fonction générique créant un diagramme de Gantt                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates

# 1 -- Fonction ----------------------------------------------------------------


def plot_diagramme_grantt(
    data,
    voyage_label: str,
    date_min_label: str,
    date_max_label: str,
    palette_couleurs: list,
    date_min: str | None = None,
    date_max: str | None = None,
    titre: str = "",
):

    fig, ax = plt.subplots(figsize=(10, 5))

    liste_temp = []

    # nettoyage
    for _, item in data.items():

        label_temp = item.get(voyage_label)
        deb_temp = item.get(date_min_label)
        fin_temp = item.get(date_max_label)

        if not label_temp or not deb_temp or not fin_temp:
            continue

        deb_temp = pd.to_datetime(deb_temp, errors="coerce")
        fin_temp = pd.to_datetime(fin_temp, errors="coerce")

        if pd.isna(deb_temp) or pd.isna(fin_temp):
            continue

        if date_min and fin_temp < pd.to_datetime(date_min):
            continue
        if date_max and deb_temp > pd.to_datetime(date_max):
            continue

        liste_temp.append(
            {"label_temp": label_temp, "deb_temp": deb_temp, "fin_temp": fin_temp}
        )

    # Tri
    liste_temp.sort(key=lambda x: (x["deb_temp"], x["fin_temp"], x["label_temp"]))

    # Ajout des barres
    for i, item in enumerate(liste_temp):
        ax.barh(
            y=i,
            width=max(
                item["fin_temp"] - item["deb_temp"],
                pd.Timedelta(days=0.8),
            ),
            left=item["deb_temp"],
            height=0.4,
            align="center",
            color=palette_couleurs[i % len(palette_couleurs)],
        )

    # Y axis
    ax.set_yticks(range(len(liste_temp)))
    ax.set_yticklabels([d["label_temp"] for d in liste_temp])

    if date_min is not None:
        ax.set_xlim(left=pd.to_datetime(date_min))

    if date_max is not None:
        ax.set_xlim(right=pd.to_datetime(date_max))

    # X axis plus propre
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    # Suppression des bords droit et supérieur
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_title(titre)

    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    return fig
