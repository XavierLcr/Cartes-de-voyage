################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.9 – Fonction générique créant un diagramme de Gantt                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from matplotlib.figure import Figure

# 1 -- Fonction ----------------------------------------------------------------


def plot_diagramme_gantt(
    data,
    voyage_label: str,
    date_min_label: str,
    date_max_label: str,
    palette_couleurs: list,
    date_min: str | None = None,
    date_max: str | None = None,
    titre: str = "",
):

    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot(111)

    liste_temp = []

    # nettoyage
    for _, item in data.items():

        label_temp = item.get(voyage_label, "")
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

    # Ajout des barres (on garde une référence patch <-> label <-> couleur)
    infos_survol = []
    for i, item in enumerate(liste_temp):
        couleur_barre = palette_couleurs[i % len(palette_couleurs)]
        barre = ax.barh(
            y=i,
            width=max(
                item["fin_temp"] - item["deb_temp"],
                pd.Timedelta(days=0.8),
            ),
            left=item["deb_temp"],
            height=0.9,
            align="center",
            color=couleur_barre,
        )
        infos_survol.append((barre[0], item["label_temp"], couleur_barre))

    # Y axis : plus de labels d'événement, juste les traits
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)

    if date_min is not None:
        ax.set_xlim(left=pd.to_datetime(date_min))

    if date_max is not None:
        ax.set_xlim(right=pd.to_datetime(date_max))

    # X axis plus propre
    locator = mdates.AutoDateLocator(minticks=4, maxticks=6)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    # Suppression des bords droit et supérieur
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_title(titre)

    # Annotation "infobulle", invisible tant qu'on ne survole rien
    annotation = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(16, 14),
        textcoords="offset points",
        fontsize=9.5,
        fontfamily="Segoe UI",
        color="#1c1f2b",
        bbox=dict(
            boxstyle="round,pad=0.55,rounding_size=0.6",
            facecolor="white",
            edgecolor="#10B981",
            linewidth=1.1,
            alpha=0.97,
        ),
        arrowprops=dict(
            arrowstyle="-",
            color="#10B981",
            linewidth=1.1,
            shrinkA=0,
            shrinkB=6,
            connectionstyle="arc3,rad=0.15",
        ),
        zorder=10,
    )
    annotation.set_visible(False)

    # Métadonnées exploitées par conteneur_graphique_simple pour le survol
    ax.infos_survol_gantt = infos_survol
    ax.annotation_gantt = annotation

    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    return fig
