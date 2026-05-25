################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.3 – Fonctions génériques utiles - PyQt6                                    #
################################################################################


from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QLabel,
    QWidget,
    QPushButton,
    QApplication,
)
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_widget,
)

# 1 -- Fonctions sur les combo -------------------------------------------------


## 1.1 -- Fonction remplaçant l'entièreté des valeurs d'un combo ---------------


def reset_combo(combo, items, set_index=True):

    combo.blockSignals(True)
    combo.clear()
    combo.addItems(items)
    if set_index:
        combo.setCurrentIndex(0)
    combo.blockSignals(False)


## 1.2 -- Fonction conservant la valeur d'un combo vidé en PyQt6 ---------------


def restaurer_valeur_combo(combo, dict_parent, langue, valeur, defaut_index=0):
    """
    Met à jour un QComboBox avec une valeur trouvée dans un dictionnaire traduit.

    combo : QComboBox à mettre à jour
    dict_parent : dictionnaire contenant les traductions (ex: constantes.parametres_traduits["themes_cartes"])
    langue : langue courante
    valeur : valeur à restaurer en français
    defaut_index : index à mettre si aucune valeur trouvée
    """
    combo.blockSignals(True)

    if valeur is not None:
        traduction = dict_parent.get(langue, {}).get(valeur)
        if traduction is not None:
            idx = combo.findText(traduction)
            combo.setCurrentIndex(idx if idx != -1 else defaut_index)
        else:
            combo.setCurrentIndex(defaut_index)
    else:
        combo.setCurrentIndex(defaut_index)

    combo.blockSignals(False)


# 2 -- Fonctions sur les QLabel ------------------------------------------------


## 2.1 -- Fonction créant un QLabel --------------------------------------------


def creer_QLabel_centre(
    alignement=Qt.AlignmentFlag.AlignCenter,
    text: str | None = None,
    parent=None,
    wordWrap=False,
):
    """
    Crée un QLabel avec un alignement vertical centré.

    Args:
        text (str|None): Texte à afficher dans le label (optionnel).
        parent (QWidget): Widget parent (optionnel).

    Returns:
        QLabel: Le label configuré.
    """
    label = QLabel(text, parent, wordWrap=wordWrap)
    label.setAlignment(alignement)
    return label


# 3 -- Fonctions de création de lignes -----------------------------------------


## 3.1 -- Fonction de création d'une ligne horizontale -------------------------


def creer_ligne_horizontale(
    lStretch=1,
    ligne_largeur=4,
    rStretch=1,
    ligne_epaisseur=1,
    ligne_epaisseur_interieur=0,
    relief=QFrame.Shadow.Sunken,
):
    """Afficher une simple ligne horizontale."""

    widget = QWidget()
    layout_temp = QHBoxLayout(widget)
    layout_temp.setContentsMargins(0, 0, 0, 0)
    layout_temp.setSpacing(0)

    ligne = QFrame()
    ligne.setFixedHeight(2)
    ligne.setFrameShape(QFrame.Shape.HLine)
    ligne.setFrameShadow(relief)
    ligne.setLineWidth(ligne_epaisseur)
    ligne.setMidLineWidth(ligne_epaisseur_interieur)

    layout_temp.addStretch(lStretch)
    layout_temp.addWidget(ligne, ligne_largeur)
    layout_temp.addStretch(rStretch)

    return widget


## 3.2 -- Fonction de création d'une ligne verticale ---------------------------


def creer_ligne_verticale():
    """Afficher une simple ligne verticale."""
    ligne = QFrame()
    ligne.setFrameShape(QFrame.Shape.VLine)
    ligne.setFrameShadow(QFrame.Shadow.Raised)
    return ligne


# 4 -- Fonctions sur les layout ------------------------------------------------


## 4.1 -- Vide l'entièreté d'un layout PyQt6 -----------------------------------


def vider_layout(layout):

    if layout is None:
        return

    while layout.count():
        item = layout.takeAt(0)

        widget = item.widget()
        if widget:
            widget.setParent(None)
            widget.deleteLater()

        sublayout = item.layout()
        if sublayout:
            vider_layout(sublayout)

    QApplication.processEvents()


# 5 -- Fonction sur les QPushButton --------------------------------------------


## 5.1 -- Fonction de validation visuelle de la sauvegarde ---------------------


def set_emoji_sauvegarde(widget: QPushButton, temps_ms: int):

    widget.setText("💾✅")
    QTimer.singleShot(temps_ms, lambda: widget.setText("💾"))


# 6 -- Style d'insertion des graphiques ----------------------------------------


## 6.1 -- Conteneur simple -----------------------------------------------------


def conteneur_graphique_simple(fig, style, teinte, nuances):

    container = QFrame()
    couleur = renvoyer_couleur_widget(
        style=style, teinte=teinte, nuances=nuances, clair="#C9D6E0", sombre="#26C6DA"
    )
    container.setStyleSheet(f"""
        QFrame {{
            background: white;
            border: 3px solid {couleur};
            border-radius: 10px;
            padding: 12px;
        }}
    """)

    # Ajouter le canvas au conteneur
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(0, 0, 0, 0)
    container_layout.addWidget(FigureCanvas(fig))

    return container
