################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# 0.16 – Sélecteur de valeurs                                                  #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import sys

from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
    QVariantAnimation,
    QEasingCurve,
    QSize,
    QRectF,
)
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QFont,
    QLinearGradient,
)
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QSizePolicy,
)

# 1 -- Sélecteur de valeurs ----------------------------------------------------


class SelecteurValeurs(QWidget):

    valeur_changee = pyqtSignal(int)

    # Styles graphiques
    STYLES = {
        "clair": {
            "fond": "#E5E9F1",
            "bordure_fond": "#D3DAE7",
            "selection_haut": "#E6E0F3",
            "selection_bas": "#CEC5E5",
            "bordure_selection": "#B9AED7",
            "reflet": "#FFFFFF",
            "texte": "#737D91",
            "texte_selection": "#403B59",
            "texte_survol": "#514B6D",
            "survol": "#FFFFFF",
            "ombre": "#85809C",
        },
        "sombre": {
            "fond": "#292F40",
            "bordure_fond": "#414C63",
            "selection_haut": "#D1CBE8",
            "selection_bas": "#AFA6D2",
            "bordure_selection": "#E2DDF2",
            "reflet": "#FFFFFF",
            "texte": "#C0C9D9",
            "texte_selection": "#29273D",
            "texte_survol": "#FFFFFF",
            "survol": "#FFFFFF",
            "ombre": "#101522",
        },
    }

    # Dimensions
    HAUTEUR = 44
    MARGE = 4
    RAYON_FOND = 13
    RAYON_SELECTION = 10

    # Animation
    DUREE_ANIMATION = 360
    ETIREMENT_MAX = 13

    def __init__(
        self,
        valeurs,
        valeur_initiale_index=0,
        layout_horizontal=True,
        style="sombre",
        parent=None,
    ):

        super().__init__(parent)

        self.valeurs = []
        self.index = None
        self.layout_horizontal = layout_horizontal
        self.style_actuel = None

        self.index_survole = -1
        self.indices_desactives = set()

        # Géométrie animée
        self.position_animation = 0.0
        self.position_depart = 0.0
        self.position_arrivee = 0.0
        self.etirement = 0.0

        # Initialisation
        self._initialiser_animation()

        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            (
                QSizePolicy.Policy.Fixed
                if layout_horizontal
                else QSizePolicy.Policy.Expanding
            ),
        )

        self.setMinimumHeight(self.HAUTEUR if layout_horizontal else 100)

        self.definir_valeurs(
            valeurs,
            valeur_initiale_index=valeur_initiale_index,
        )

        self.set_style(style)

    # 1.1 -- Initialisation ----------------------------------------------------

    def _initialiser_animation(self):

        self.animation = QVariantAnimation(self)

        self.animation.setDuration(self.DUREE_ANIMATION)

        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)

        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.animation.valueChanged.connect(self._actualiser_animation)

    def sizeHint(self):

        return QSize(
            300 if self.layout_horizontal else 110,
            self.HAUTEUR if self.layout_horizontal else 200,
        )

    def minimumSizeHint(self):

        return QSize(
            80 if self.layout_horizontal else 70,
            self.HAUTEUR if self.layout_horizontal else 80,
        )

    # 1.2 -- Gestion des styles ------------------------------------------------

    def set_style(self, style="clair"):

        if style not in self.STYLES:

            raise ValueError(
                f"Style inconnu : {style}. "
                f"Valeurs possibles : {', '.join(self.STYLES)}."
            )

        self.style_actuel = style

        self.update()

    # 1.3 -- Géométrie ---------------------------------------------------------

    def _obtenir_zone(self):

        return QRectF(self.rect()).adjusted(
            self.MARGE,
            self.MARGE,
            -self.MARGE,
            -self.MARGE,
        )

    def _obtenir_largeur_segment(self):

        zone = self._obtenir_zone()

        if not self.valeurs:
            return 0

        if self.layout_horizontal:
            return zone.width() / len(self.valeurs)

        return zone.height() / len(self.valeurs)

    def _obtenir_rectangle_segment(self, index):

        zone = self._obtenir_zone()

        largeur = self._obtenir_largeur_segment()

        if self.layout_horizontal:

            return QRectF(
                zone.x() + index * largeur,
                zone.y(),
                largeur,
                zone.height(),
            )

        return QRectF(
            zone.x(),
            zone.y() + index * largeur,
            zone.width(),
            largeur,
        )

    def _obtenir_rectangle_selection(self):

        if self.index is None or not self.valeurs:
            return QRectF()

        zone = self._obtenir_zone()

        largeur = self._obtenir_largeur_segment()

        position = self.position_animation

        etirement = self.etirement

        if self.layout_horizontal:

            x = zone.x() + position * largeur
            y = zone.y() + 1

            largeur_selection = largeur - 2

            if etirement > 0:
                x -= etirement

            return QRectF(
                x,
                y,
                largeur_selection + etirement,
                zone.height() - 2,
            )

        y = zone.y() + position * largeur
        x = zone.x() + 1

        hauteur_selection = largeur - 2

        if etirement > 0:
            y -= etirement

        return QRectF(
            x,
            y,
            zone.width() - 2,
            hauteur_selection + etirement,
        )

    # 1.4 -- Animation ---------------------------------------------------------

    def _actualiser_animation(self, progression):

        progression = float(progression)

        position = (
            self.position_depart
            + (self.position_arrivee - self.position_depart) * progression
        )

        self.position_animation = position

        # Etirement dans le sens du déplacement
        amplitude = self.ETIREMENT_MAX * 4 * progression * (1 - progression)

        self.etirement = amplitude

        self.update()

    def _deplacer_selection(self, index, animer=True):

        self.animation.stop()

        self.position_depart = self.position_animation
        self.position_arrivee = float(index)

        if not animer or not self.isVisible():

            self.position_animation = float(index)
            self.etirement = 0

            self.update()

            return

        if abs(self.position_arrivee - self.position_depart) < 0.001:

            return

        self.animation.start()

    # 1.5 -- Dessin du rail ----------------------------------------------------

    def _dessiner_fond(self, peintre):

        c = self.STYLES[self.style_actuel]

        zone = self._obtenir_zone()

        peintre.setPen(
            QPen(
                QColor(c["bordure_fond"]),
                1,
            )
        )

        peintre.setBrush(QColor(c["fond"]))

        peintre.drawRoundedRect(
            zone,
            self.RAYON_FOND,
            self.RAYON_FOND,
        )

    # 1.6 -- Dessin de la sélection --------------------------------------------

    def _dessiner_selection(self, peintre):

        if self.index is None or not self.valeurs:
            return

        c = self.STYLES[self.style_actuel]

        rectangle = self._obtenir_rectangle_selection()

        if rectangle.isEmpty():
            return

        rayon = self.RAYON_SELECTION

        # Ombre diffuse simulée
        for i, alpha in enumerate((8, 12, 17)):

            peintre.setPen(Qt.PenStyle.NoPen)
            col_temp = QColor(c["ombre"])
            col_temp.setAlpha(alpha)
            peintre.setBrush(col_temp)

            peintre.drawRoundedRect(
                rectangle.adjusted(
                    -i * 0.5,
                    1 + i * 0.7,
                    i * 0.5,
                    2 + i * 0.7,
                ),
                rayon + i,
                rayon + i,
            )

        # Dégradé de verre
        gradient = QLinearGradient(
            rectangle.topLeft(),
            rectangle.bottomLeft(),
        )

        gradient.setColorAt(
            0.0,
            QColor(c["selection_haut"]),
        )

        gradient.setColorAt(
            1.0,
            QColor(c["selection_bas"]),
        )

        peintre.setPen(
            QPen(
                QColor(c["bordure_selection"]),
                1,
            )
        )

        peintre.setBrush(gradient)

        peintre.drawRoundedRect(
            rectangle,
            rayon,
            rayon,
        )

        # Reflet supérieur
        reflet = QLinearGradient(
            rectangle.topLeft(),
            rectangle.bottomLeft(),
        )

        couleur_reflet = QColor(c["reflet"])
        couleur_reflet.setAlpha(105)

        reflet.setColorAt(0.0, couleur_reflet)
        col_temp = QColor(c["reflet"])
        col_temp.setAlpha(0)
        reflet.setColorAt(0.55, col_temp)
        reflet.setColorAt(1.0, col_temp)

        interieur = rectangle.adjusted(1, 1, -1, -1)

        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(reflet)

        peintre.drawRoundedRect(
            interieur,
            rayon - 1,
            rayon - 1,
        )

        # Fin contour intérieur
        peintre.setBrush(Qt.BrushStyle.NoBrush)
        col_temp = QColor(c["reflet"])
        col_temp.setAlpha(75)
        peintre.setPen(QPen(col_temp, 0.7))

        peintre.drawRoundedRect(
            interieur,
            rayon - 1,
            rayon - 1,
        )

    # 1.7 -- Dessin des libellés -----------------------------------------------

    def _dessiner_libelles(self, peintre):

        if not self.valeurs:
            return

        c = self.STYLES[self.style_actuel]

        font = QFont(self.font())
        font.setPointSizeF(10)
        font.setWeight(QFont.Weight.Medium)

        peintre.setFont(font)

        for i, valeur in enumerate(self.valeurs):

            rectangle = self._obtenir_rectangle_segment(i)

            if i in self.indices_desactives:

                couleur = QColor(c["texte"])
                couleur.setAlpha(100)

            elif i == self.index:

                couleur = QColor(c["texte_selection"])

                font_selection = QFont(font)
                font_selection.setWeight(QFont.Weight.DemiBold)

                peintre.setFont(font_selection)

            elif i == self.index_survole:

                couleur = QColor(c["texte_survol"])

            else:

                couleur = QColor(c["texte"])

            peintre.setPen(couleur)

            peintre.drawText(
                rectangle,
                Qt.AlignmentFlag.AlignCenter,
                valeur,
            )

            peintre.setFont(font)

    # 1.8 -- Événement de dessin -----------------------------------------------

    def paintEvent(self, event):

        if self.style_actuel is None:
            return

        peintre = QPainter(self)

        peintre.setRenderHint(QPainter.RenderHint.Antialiasing)

        peintre.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # Ordre des couches
        self._dessiner_fond(peintre)
        self._dessiner_selection(peintre)
        self._dessiner_survol(peintre)
        self._dessiner_libelles(peintre)

        peintre.end()

    def _dessiner_survol(self, peintre):

        if self.index_survole < 0:
            return

        if self.index_survole == self.index:
            return

        if self.index_survole in self.indices_desactives:
            return

        c = self.STYLES[self.style_actuel]

        rectangle = self._obtenir_rectangle_segment(self.index_survole)

        peintre.setPen(Qt.PenStyle.NoPen)
        col_temp = QColor(c["survol"])
        col_temp.setAlpha(75)
        peintre.setBrush(col_temp)

        peintre.drawRoundedRect(
            rectangle.adjusted(2, 2, -2, -2),
            self.RAYON_SELECTION,
            self.RAYON_SELECTION,
        )

    # 1.9 -- Interaction souris ------------------------------------------------

    def _obtenir_index_souris(self, position):

        if not self.valeurs:
            return -1

        zone = self._obtenir_zone()

        if not zone.contains(position):
            return -1

        if self.layout_horizontal:

            largeur = self._obtenir_largeur_segment()

            index = int((position.x() - zone.x()) / largeur)

        else:

            hauteur = self._obtenir_largeur_segment()

            index = int((position.y() - zone.y()) / hauteur)

        return max(0, min(index, len(self.valeurs) - 1))

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            index = self._obtenir_index_souris(event.position())

            if index >= 0 and index not in self.indices_desactives:

                self.definir_valeur(
                    index,
                    emettre_signal=True,
                )

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        index = self._obtenir_index_souris(event.position())

        if index != self.index_survole:

            self.index_survole = index
            self.update()

        super().mouseMoveEvent(event)

    def leaveEvent(self, event):

        self.index_survole = -1
        self.update()

        super().leaveEvent(event)

    # 1.10 -- Gestion des valeurs ----------------------------------------------

    def _valider_valeurs(self, valeurs, valeur_initiale_index):

        if not valeurs:
            raise ValueError("Le sélecteur doit contenir au moins une valeur.")

        if not all(isinstance(v, str) for v in valeurs):
            raise ValueError("Les libellés doivent être des chaînes de caractères.")

        if not isinstance(valeur_initiale_index, int) or isinstance(
            valeur_initiale_index, bool
        ):
            raise ValueError("L'index initial doit être un entier.")

        if not 0 <= valeur_initiale_index < len(valeurs):
            raise ValueError("L'index initial est en dehors des valeurs proposées.")

    def definir_valeurs(
        self,
        valeurs,
        valeur_initiale_index=None,
        emettre_signal=False,
    ):

        valeurs = list(valeurs) if valeurs is not None else []

        ancien_index = self.index

        if valeur_initiale_index is not None:

            nouvel_index = valeur_initiale_index

        elif ancien_index is not None and ancien_index < len(valeurs):

            nouvel_index = ancien_index

        else:

            nouvel_index = 0

        self._valider_valeurs(
            valeurs,
            nouvel_index,
        )

        self.animation.stop()

        self.valeurs = valeurs
        self.index = nouvel_index

        self.indices_desactives.clear()
        self.index_survole = -1

        self.position_animation = float(nouvel_index)
        self.position_depart = float(nouvel_index)
        self.position_arrivee = float(nouvel_index)
        self.etirement = 0

        self.update()

        if emettre_signal and ancien_index != nouvel_index:
            self.valeur_changee.emit(nouvel_index)

    # 1.11 -- Gestion de la sélection ------------------------------------------

    def definir_valeur(self, index, emettre_signal=False):

        if not isinstance(index, int) or index not in range(len(self.valeurs)):
            raise ValueError(f"Index inconnu : {index}")

        if index in self.indices_desactives:
            return

        if index == self.index:
            return

        self.index = index

        self._deplacer_selection(index)

        if emettre_signal:
            self.valeur_changee.emit(index)

    def _changer_valeur(self, index):

        self.definir_valeur(
            index,
            emettre_signal=True,
        )

    def obtenir_valeur(self, index: bool = True):
        if index:
            return self.index
        else:
            return self.valeurs[self.index]

    # 1.12 -- Gestion de l'activation ------------------------------------------

    def definir_activation(self, index, actif=True):

        if index not in range(len(self.valeurs)):
            raise ValueError(f"Index inconnu : {index}")

        if actif:

            self.indices_desactives.discard(index)

        else:

            self.indices_desactives.add(index)

        self.update()

    # 1.13 -- Redimensionnement ------------------------------------------------

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self.update()


# 2 -- Visualisation -----------------------------------------------------------


if __name__ == "__main__":

    app = QApplication(sys.argv)

    fenetre = QWidget()
    fenetre.setWindowTitle("Test - Sélecteur de valeurs")
    fenetre.resize(540, 360)

    fenetre.setStyleSheet("""
        QWidget {
            background-color: #F3F4F8;
        }
    """)

    layout = QVBoxLayout(fenetre)

    layout.setContentsMargins(35, 35, 35, 35)
    layout.setSpacing(20)

    titre = QLabel("Granularité géographique")

    titre.setStyleSheet("""
        color: #55516F;
        font-size: 12pt;
        font-weight: 600;
        background: transparent;
    """)

    selecteur = SelecteurValeurs(
        valeurs=[
            "Pays",
            "Continents",
            "Régions",
            "Départements",
        ],
        valeur_initiale_index=2,
        style="clair",
    )

    resultat = QLabel(f"Index sélectionné : {selecteur.obtenir_valeur()}")

    resultat.setStyleSheet("""
        color: #737D91;
        font-size: 10pt;
        background: transparent;
    """)

    selecteur.valeur_changee.connect(
        lambda i: resultat.setText(f"Index sélectionné : {i}")
    )

    bouton_style = QPushButton("Changer de thème")

    bouton_style.clicked.connect(
        lambda: selecteur.set_style(
            "sombre" if selecteur.style_actuel == "clair" else "clair"
        )
    )

    # Version verticale
    selecteur_vertical = SelecteurValeurs(
        valeurs=["Jour", "Semaine", "Mois"],
        valeur_initiale_index=1,
        layout_horizontal=False,
        style="sombre",
    )

    selecteur_vertical.setFixedWidth(125)
    selecteur_vertical.setFixedHeight(150)

    layout.addWidget(titre)
    layout.addWidget(selecteur)
    layout.addWidget(resultat)
    layout.addWidget(bouton_style)
    layout.addWidget(selecteur_vertical)
    layout.addStretch()

    fenetre.show()

    sys.exit(app.exec())
