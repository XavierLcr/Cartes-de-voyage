################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1.5 – Bouton de création des cartes                                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import (
    Qt,
    QRectF,
    QPointF,
    QVariantAnimation,
    QEasingCurve,
)
from PyQt6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# 1 -- Bouton ------------------------------------------------------------------


class BoutonCreationCartes(QPushButton):
    """
    Bouton évoquant une carte routière pliée.

    Le fond est dessiné comme une feuille cartographique à trois panneaux.
    Un itinéraire discret se colore au survol et le bouton s'abaisse à l'appui.
    La fonction de traduction est facultative pour permettre une prévisualisation
    autonome.
    """

    def __init__(
        self,
        fonction_traduction=None,
        parent=None,
    ):
        super().__init__(parent)

        self.fonction_traduction = fonction_traduction

        self.setMinimumWidth(260)
        self.setFixedHeight(70)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Créer les cartes de voyage")

        self._survol = 0.0
        self._enfonce = False

        self._animation_survol = QVariantAnimation(self)
        self._animation_survol.setDuration(190)
        self._animation_survol.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation_survol.valueChanged.connect(self._mettre_a_jour_survol)

        # Le QPushButton natif ne dessine rien : tout est rendu dans paintEvent.
        self.setFlat(True)
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)

        if self.fonction_traduction is not None:
            self.set_langue()
        else:
            self.setText("Créer les cartes")

    # --------------------------------------------------------------------------
    # Langue
    # --------------------------------------------------------------------------

    def set_langue(self):
        """Met à jour le libellé et l'infobulle avec les clés de l'application."""
        if self.fonction_traduction is None:
            return

        self.setText(self.fonction_traduction("bouton_publier_cartes"))
        self.setToolTip(self.fonction_traduction("description_bouton_publier_cartes"))

    # --------------------------------------------------------------------------
    # Animation du survol
    # --------------------------------------------------------------------------

    def _mettre_a_jour_survol(self, valeur):
        self._survol = float(valeur)
        self.update()

    def _animer_survol(self, destination: float):
        self._animation_survol.stop()
        self._animation_survol.setStartValue(self._survol)
        self._animation_survol.setEndValue(destination)
        self._animation_survol.start()

    # --------------------------------------------------------------------------
    # Événements souris
    # --------------------------------------------------------------------------

    def enterEvent(self, event):
        if self.isEnabled():
            self._animer_survol(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animer_survol(0.0)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._enfonce = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._enfonce = False
        self.update()
        super().mouseReleaseEvent(event)

    def changeEvent(self, event):
        super().changeEvent(event)
        if not self.isEnabled():
            self._enfonce = False
            self._animer_survol(0.0)

    # --------------------------------------------------------------------------
    # Dessin
    # --------------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        largeur = self.width()
        hauteur = self.height()
        decalage_appui = 2 if self._enfonce else 0

        rect_carte = QRectF(
            5,
            4 + decalage_appui,
            largeur - 10,
            hauteur - 12,
        )

        # Palette légèrement désaturée quand le bouton est désactivé.
        desactive = not self.isEnabled()

        # Ombre portée courte pour donner à la carte un léger relief.
        if not self._enfonce:
            rect_ombre = QRectF(rect_carte)
            rect_ombre.translate(0, 4)

            couleur_ombre = QColor("#202A32")
            couleur_ombre.setAlpha(48 if not desactive else 20)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(couleur_ombre)
            painter.drawRoundedRect(rect_ombre, 11, 11)

        # Papier de la carte.
        couleur_haut = QColor("#FBF8EF")
        couleur_bas = QColor("#F0EBDD")
        couleur_contour = QColor("#AEB8B5")

        if desactive:
            couleur_haut = QColor("#F1F0EB")
            couleur_bas = QColor("#E8E6DF")
            couleur_contour = QColor("#C7C8C3")

        elif self._enfonce:
            couleur_haut = QColor("#EDE7D8")
            couleur_bas = QColor("#E6DECC")

        degrade_papier = QLinearGradient(
            rect_carte.topLeft(),
            rect_carte.bottomLeft(),
        )
        degrade_papier.setColorAt(0.0, couleur_haut)
        degrade_papier.setColorAt(1.0, couleur_bas)

        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(rect_carte, 11, 11)

        painter.setPen(QPen(couleur_contour, 1.1))
        painter.setBrush(degrade_papier)
        painter.drawPath(chemin_carte)

        # Panneaux légèrement nuancés, comme les plis d'une carte dépliable.
        painter.save()
        painter.setClipPath(chemin_carte)

        largeur_panneau = rect_carte.width() / 3
        intensite_survol = self._survol if not desactive else 0.0

        couleur_panneau = QColor("#DDE8E3")
        couleur_panneau.setAlpha(int(17 + 16 * intensite_survol))
        painter.fillRect(
            QRectF(
                rect_carte.left() + largeur_panneau,
                rect_carte.top(),
                largeur_panneau,
                rect_carte.height(),
            ),
            couleur_panneau,
        )

        couleur_panneau_droit = QColor("#D9E3E8")
        couleur_panneau_droit.setAlpha(int(17 + 20 * intensite_survol))
        painter.fillRect(
            QRectF(
                rect_carte.left() + 2 * largeur_panneau,
                rect_carte.top(),
                largeur_panneau,
                rect_carte.height(),
            ),
            couleur_panneau_droit,
        )

        # Plis : ombre et reflet très fins pour suggérer les panneaux.
        for index in (1, 2):
            x = rect_carte.left() + index * largeur_panneau
            x += (index - 1.5) * 2.0 * intensite_survol

            pen_pli = QPen(QColor(105, 126, 125, 52), 1.0)
            painter.setPen(pen_pli)
            painter.drawLine(
                QPointF(x, rect_carte.top() + 8),
                QPointF(x, rect_carte.bottom() - 8),
            )

            painter.setPen(QPen(QColor(255, 255, 255, 125), 1.0))
            painter.drawLine(
                QPointF(x + 2, rect_carte.top() + 9),
                QPointF(x + 2, rect_carte.bottom() - 9),
            )

        # Petit itinéraire dans le panneau gauche.
        couleur_itineraire = QColor("#557F79")
        couleur_itineraire.setAlpha(
            int(115 + 115 * intensite_survol) if not desactive else 75
        )

        x_debut = rect_carte.left() + 17
        x_fin = rect_carte.left() + largeur_panneau - 15
        y_centre = rect_carte.center().y()

        itineraire = QPainterPath()
        itineraire.moveTo(x_debut, y_centre + 8)
        itineraire.cubicTo(
            x_debut + 7,
            y_centre + 8,
            x_debut + 6,
            y_centre - 8,
            x_debut + 14,
            y_centre - 7,
        )
        itineraire.cubicTo(
            x_debut + 21,
            y_centre - 6,
            x_fin - 5,
            y_centre + 7,
            x_fin,
            y_centre - 2,
        )

        pen_route = QPen(
            couleur_itineraire,
            2.0 + 0.35 * intensite_survol,
            Qt.PenStyle.DashLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(pen_route)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(itineraire)

        # Point de départ.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#F8F5EB"))
        painter.drawEllipse(
            QPointF(x_debut, y_centre + 8),
            3.5,
            3.5,
        )
        painter.setPen(QPen(couleur_itineraire, 1.5))
        painter.setBrush(QColor("#F8F5EB"))
        painter.drawEllipse(
            QPointF(x_debut, y_centre + 8),
            3.5,
            3.5,
        )

        # Repère d'arrivée circulaire, simple et lisible à petite taille.
        point_arrivee = QPointF(x_fin, y_centre - 2)
        rayon = 4.2 + 0.5 * intensite_survol
        painter.setPen(QPen(couleur_itineraire, 1.5))
        painter.setBrush(QColor("#F8F5EB"))
        painter.drawEllipse(point_arrivee, rayon, rayon)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(couleur_itineraire)
        painter.drawEllipse(point_arrivee, 1.5, 1.5)

        painter.restore()

        # Libellé.
        rect_texte = QRectF(
            rect_carte.left() + largeur_panneau + 11,
            rect_carte.top() + 3,
            rect_carte.width() - largeur_panneau - 22,
            rect_carte.height() - 6,
        )

        police = QFont("Segoe UI", max(11, min(15, int(hauteur * 0.22))))
        police.setWeight(QFont.Weight.DemiBold)
        painter.setFont(police)

        couleur_texte = QColor("#263B3A")
        if desactive:
            couleur_texte = QColor("#888B87")
        painter.setPen(couleur_texte)

        painter.drawText(
            rect_texte,
            Qt.AlignmentFlag.AlignCenter,
            self.text(),
        )

        # Indication de focus clavier, discrète mais visible.
        if self.hasFocus() and self.isEnabled():
            rect_focus = rect_carte.adjusted(3, 3, -3, -3)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(
                QPen(
                    QColor("#648C86"),
                    1.2,
                    Qt.PenStyle.DashLine,
                )
            )
            painter.drawRoundedRect(rect_focus, 8, 8)

        painter.end()


# ==============================================================================
# Fenêtre de test autonome
# ==============================================================================


class FenetreTest(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aperçu — bouton de création des cartes")
        self.setMinimumSize(520, 220)

        contenu = QWidget()
        contenu.setStyleSheet("""
            QWidget {
                background-color: #F4F5F3;
                color: #263238;
                font-family: "Segoe UI";
            }
        """)

        disposition = QVBoxLayout(contenu)
        disposition.setContentsMargins(34, 28, 34, 28)
        disposition.setSpacing(18)

        titre = QLabel("Aperçu du bouton")
        titre.setStyleSheet("""
            QLabel {
                color: #263238;
                font-size: 17px;
                font-weight: 600;
            }
        """)

        aide = QLabel("Survole le bouton, clique dessus ou utilise la touche Tab.")
        aide.setStyleSheet("""
            QLabel {
                color: #6B7478;
                font-size: 12px;
            }
        """)

        self.bouton = BoutonCreationCartes()
        self.bouton.clicked.connect(self._bouton_clique)

        self.etat = QLabel(" ")
        self.etat.setStyleSheet("""
            QLabel {
                color: #557F79;
                font-size: 12px;
            }
        """)

        disposition.addWidget(titre)
        disposition.addWidget(aide)
        disposition.addWidget(self.bouton)
        disposition.addWidget(self.etat)
        disposition.addStretch()

        self.setCentralWidget(contenu)

    def _bouton_clique(self):
        self.etat.setText("Le bouton fonctionne !")


if __name__ == "__main__":
    import sys

    application = QApplication(sys.argv)
    fenetre = FenetreTest()
    fenetre.show()
    sys.exit(application.exec())
