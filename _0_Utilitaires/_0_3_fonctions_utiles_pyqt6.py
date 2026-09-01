################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires/                                                              #
# 0.3 – Fonctions génériques utiles - PyQt6                                    #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtWidgets import (
    QHBoxLayout,
    QFrame,
    QLabel,
    QWidget,
    QApplication,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import (
    QFontInfo,
    QFont,
    QColor,
    QPixmap,
    QIcon,
    QPainter,
    QPen,
    QPainterPath,
    QBrush,
    QRadialGradient,
)

# 1 -- Fonctions sur les combos ------------------------------------------------


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


# 4 -- Fonctions sur les layouts -----------------------------------------------


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


# 5 -- Création d'un scroll ----------------------------------------------------


def creer_scroll(layout):

    # Widget conteneur
    widget_temp = QWidget()
    widget_temp.setLayout(layout)

    # Scroll
    scroll_temp = QScrollArea()
    scroll_temp.setWidgetResizable(True)
    scroll_temp.setWidget(widget_temp)
    return scroll_temp


# 6 -- Sélection d'une police disponible parmi une liste -----------------------


def _trouver_police_disponible(candidats):
    """Renvoie le premier nom de police réellement installé parmi
    `candidats` (le dernier élément sert de repli garanti)."""
    for nom in candidats[:-1]:
        if QFontInfo(QFont(nom)).exactMatch():
            return nom
    return candidats[-1]


# 7 -- Fonctions sur les couleurs ----------------------------------------------


## 7.1 -- Renvoie une QColor avec un certain niveau de transparence ------------


def _QColor_avec_alpha(couleur: QColor, alpha: int) -> QColor:
    """Copie une QColor du thème avec une opacité réduite, pour ne
    jamais muter les couleurs originales du thème."""
    c = QColor(couleur)
    c.setAlpha(alpha)
    return c


# 8 -- Fonction de création d'une icône ----------------------------------------


def creer_icone(fonction_dessin, taille_px: int = 50) -> QIcon:
    """Rend une icône QPainter (ex: _dessiner_icone_drapeaux) en QIcon utilisable partout."""
    pixmap = QPixmap(taille_px, taille_px)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    centre = QPointF(taille_px / 2, taille_px / 2)
    fonction_dessin(painter, centre, taille_px)
    painter.end()

    return QIcon(pixmap)


# 9 -- Pastille de validation --------------------------------------------------


def _dessiner_badge_validation(
    painter: QPainter, centre: QPointF, taille: float
) -> None:
    """Dessine un badge de validation (cercle vert + coche blanche) en bas
    à droite du centre donné. Réutilisable dans n'importe quelle icône."""

    COULEUR_VALIDATION = QColor("#3DDC84")

    cx, cy = centre.x(), centre.y()

    rayon_badge = taille * 0.26
    x_badge = cx + taille * 0.24
    y_badge = cy + taille * 0.24

    degrade_badge = QRadialGradient(
        QPointF(x_badge, y_badge - rayon_badge * 0.2), rayon_badge * 1.5
    )
    degrade_badge.setColorAt(0.0, COULEUR_VALIDATION.lighter(125))
    degrade_badge.setColorAt(1.0, COULEUR_VALIDATION.darker(105))

    pen_badge = QPen(QColor("#FFFFFF"))
    pen_badge.setWidthF(taille * 0.014)
    painter.setPen(pen_badge)
    painter.setBrush(QBrush(degrade_badge))
    painter.drawEllipse(QPointF(x_badge, y_badge), rayon_badge, rayon_badge)

    # -- Coche blanche --------------------------------------------------
    pen_coche = QPen(QColor("#FFFFFF"))
    pen_coche.setWidthF(rayon_badge * 0.26)
    pen_coche.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen_coche.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen_coche)
    chemin_coche = QPainterPath()
    chemin_coche.moveTo(x_badge - rayon_badge * 0.45, y_badge + rayon_badge * 0.02)
    chemin_coche.lineTo(x_badge - rayon_badge * 0.12, y_badge + rayon_badge * 0.35)
    chemin_coche.lineTo(x_badge + rayon_badge * 0.48, y_badge - rayon_badge * 0.35)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(chemin_coche)
