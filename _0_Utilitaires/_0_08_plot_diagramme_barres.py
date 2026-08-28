################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.8 – Fonction générique créant un diagramme en barres                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FuncFormatter

from _0_Utilitaires._0_5_isid import isid

# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de mise en forme des nombres --------------------------------


def creer_formateur(decimals):
    def formateur(value, _):
        texte_temp = f"{value:,.{decimals}f}"
        return texte_temp.replace(",", " ").replace(".", ",")

    return formateur


## 1.2 -- Fonction de création du diagramme en barres --------------------------


def plot_diagramme_barre(
    df: pd.DataFrame,
    var_x: str,
    var_y,
    var_color: str | None = None,
    var_wrap: str | None = None,
    titre: str = "",
    x_label: str = "",
    y_label: str = "",
    color_label: str | None = "",
    palette: list = [
        "#7DC8E8",
        "#F5E474",
        "#E15759",
        "#76B7B2",
        "#59A14F",
        "#EDC948",
        "#B07AA1",
        "#FF9DA7",
        "#9C755F",
        "#BAB0AC",
    ],
    figsize: tuple = (6, 4),
    wrap_ncol: int = 3,
    y_decimales: int = 0,
):

    df_temp = df.copy()

    # Gestion de la couleur
    if var_color is None:
        var_color = "couleur"
        df_temp[var_color] = "Constant"
    val_color = list(df_temp[var_color].unique())

    # Gestion du facetwrap
    if var_wrap is None:
        var_wrap = "wrap"
        df_temp[var_wrap] = "Unique"
    val_wrap = list(df_temp[var_wrap].unique())
    wrap_ncol = min(len(val_wrap), wrap_ncol)

    # Test de granularité
    assert isid(
        df=df_temp, colonnes=[var_x, var_color, var_wrap], blabla=0
    ), "Des doublons sont présents"

    # Création de la figure
    fig = Figure(figsize=(10, 5))
    gs = GridSpec(
        wrap_ncol,
        int(np.ceil(len(val_wrap) / wrap_ncol)),
        figure=fig,
    )

    global_x_order = df_temp[var_x].unique()
    axes = []

    for i, wrap_val in enumerate(val_wrap):
        ax = fig.add_subplot(gs[i])
        axes.append(ax)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        subset = df_temp[df_temp[var_wrap] == wrap_val]
        bar_width = 0.8 / len(val_color)
        x_pos = np.arange(len(global_x_order))

        for j, color_val in enumerate(val_color):
            y_values = []
            for x_val in global_x_order:
                color_data = subset[
                    (subset[var_color] == color_val) & (subset[var_x] == x_val)
                ]
                y_values.append(
                    color_data[var_y].iloc[0] if not color_data.empty else 0
                )
            ax.bar(
                x_pos + j * bar_width,
                y_values,
                width=bar_width,
                label=color_val,
                color=palette[j % len(palette)],
                zorder=1,
            )

        # Gestion des libellés et légendes
        ax.yaxis.set_major_formatter(FuncFormatter(creer_formateur(y_decimales)))
        ax.grid(axis="y", linestyle="--", alpha=0.7, color="#F2F2F2", zorder=0)
        ax.set_xticks(x_pos + (len(val_color) - 1) * bar_width / 2)
        ax.set_xticklabels(global_x_order)
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.set_title(f"{wrap_val}" if len(val_wrap) > 1 else "")
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)
        if len(val_color) > 1:
            ax.legend(title=color_label if color_label is not None else var_color)

    for ax in axes:
        ax.set_ylim(bottom=0)

    if titre:
        fig.suptitle(titre)

    fig.tight_layout()
    return fig
