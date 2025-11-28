################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.1 – Fonctions génériques utiles - PyQt6                                    #
################################################################################


from PyQt6.QtWidgets import QHBoxLayout, QFrame, QLabel, QWidget
from PyQt6.QtCore import Qt


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
    """Supprime tous les widgets d'un QLayout."""
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
