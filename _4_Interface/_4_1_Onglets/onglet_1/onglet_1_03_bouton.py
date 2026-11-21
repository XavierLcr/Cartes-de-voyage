################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1.03 – Bouton de création des cartes                                  #
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
    Bouton évoquant une presse cartographique ancienne.

    Une petite presse en bois imprime une feuille d'atlas détaillée. Le dessin
    est entièrement réalisé dans paintEvent et les animations restent discrètes.
    """

    def __init__(
        self,
        fonction_traduction=None,
        parent=None,
    ):
        super().__init__(parent)

        self.fonction_traduction = fonction_traduction

        self.setMinimumWidth(280)
        self.setFixedHeight(76)
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
        self._animation_survol.setDuration(210)
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
    # Dessin de la feuille cartographique
    # --------------------------------------------------------------------------

    def _dessiner_feuille(
        self,
        painter: QPainter,
        x: float,
        y: float,
        largeur: float,
        hauteur: float,
        opacite: float = 1.0,
    ) -> None:
        """Dessine une feuille d'atlas avec relief, frontières et repères."""

        painter.save()
        painter.setOpacity(opacite)

        feuille = QPainterPath()
        feuille.moveTo(x, y + 1)
        feuille.lineTo(x + largeur - 7, y)
        feuille.lineTo(x + largeur, y + 6)
        feuille.lineTo(x + largeur - 1, y + hauteur - 3)
        feuille.quadTo(
            x + largeur * 0.52,
            y + hauteur + 2,
            x,
            y + hauteur - 1,
        )
        feuille.closeSubpath()

        # Ombre et papier.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(77, 66, 51, 24))
        painter.drawPath(feuille.translated(0.8, 1.2))

        degrade_papier = QLinearGradient(x, y, x, y + hauteur)
        degrade_papier.setColorAt(0.0, QColor("#FFFEF8"))
        degrade_papier.setColorAt(1.0, QColor("#F0EBDD"))
        painter.setPen(QPen(QColor("#C9BDA8"), 0.8))
        painter.setBrush(degrade_papier)
        painter.drawPath(feuille)

        # Petit coin replié.
        pli = QPainterPath()
        pli.moveTo(x + largeur - 7, y)
        pli.lineTo(x + largeur - 7, y + 6)
        pli.lineTo(x + largeur, y + 6)
        painter.setPen(QPen(QColor("#D2C5AF"), 0.65))
        painter.setBrush(QColor("#E8E0D0"))
        painter.drawPath(pli)

        # Cadre intérieur de la carte.
        cadre = QRectF(
            x + 5,
            y + 4,
            largeur - 11,
            hauteur - 9,
        )
        painter.setPen(QPen(QColor("#D9D0BE"), 0.55))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(cadre)

        # Forme d'un continent stylisé.
        continent = QPainterPath()
        continent.moveTo(x + largeur * 0.17, y + hauteur * 0.37)
        continent.cubicTo(
            x + largeur * 0.20,
            y + hauteur * 0.18,
            x + largeur * 0.34,
            y + hauteur * 0.22,
            x + largeur * 0.40,
            y + hauteur * 0.31,
        )
        continent.cubicTo(
            x + largeur * 0.49,
            y + hauteur * 0.22,
            x + largeur * 0.59,
            y + hauteur * 0.28,
            x + largeur * 0.58,
            y + hauteur * 0.39,
        )
        continent.cubicTo(
            x + largeur * 0.72,
            y + hauteur * 0.34,
            x + largeur * 0.83,
            y + hauteur * 0.43,
            x + largeur * 0.76,
            y + hauteur * 0.55,
        )
        continent.cubicTo(
            x + largeur * 0.71,
            y + hauteur * 0.65,
            x + largeur * 0.60,
            y + hauteur * 0.61,
            x + largeur * 0.55,
            y + hauteur * 0.76,
        )
        continent.cubicTo(
            x + largeur * 0.43,
            y + hauteur * 0.82,
            x + largeur * 0.39,
            y + hauteur * 0.65,
            x + largeur * 0.28,
            y + hauteur * 0.69,
        )
        continent.cubicTo(
            x + largeur * 0.17,
            y + hauteur * 0.66,
            x + largeur * 0.12,
            y + hauteur * 0.49,
            x + largeur * 0.17,
            y + hauteur * 0.37,
        )
        painter.setPen(QPen(QColor("#82978B"), 0.8))
        painter.setBrush(QColor("#DCE3D6"))
        painter.drawPath(continent)

        # Frontières intérieures.
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(
            QPen(
                QColor("#A6B09F"),
                0.55,
                Qt.PenStyle.DashLine,
            )
        )
        painter.drawPath(QPainterPath())
        painter.drawLine(
            QPointF(x + largeur * 0.31, y + hauteur * 0.27),
            QPointF(x + largeur * 0.36, y + hauteur * 0.69),
        )
        painter.drawLine(
            QPointF(x + largeur * 0.47, y + hauteur * 0.29),
            QPointF(x + largeur * 0.45, y + hauteur * 0.76),
        )
        painter.drawLine(
            QPointF(x + largeur * 0.62, y + hauteur * 0.34),
            QPointF(x + largeur * 0.57, y + hauteur * 0.66),
        )
        painter.drawLine(
            QPointF(x + largeur * 0.20, y + hauteur * 0.49),
            QPointF(x + largeur * 0.77, y + hauteur * 0.47),
        )

        # Courbe de niveau et cours d'eau.
        eau = QPainterPath()
        eau.moveTo(x + largeur * 0.19, y + hauteur * 0.57)
        eau.cubicTo(
            x + largeur * 0.33,
            y + hauteur * 0.43,
            x + largeur * 0.43,
            y + hauteur * 0.62,
            x + largeur * 0.58,
            y + hauteur * 0.49,
        )
        eau.cubicTo(
            x + largeur * 0.68,
            y + hauteur * 0.41,
            x + largeur * 0.72,
            y + hauteur * 0.55,
            x + largeur * 0.81,
            y + hauteur * 0.51,
        )
        painter.setPen(QPen(QColor("#8FAEB0"), 0.75))
        painter.drawPath(eau)

        # Repère de localisation.
        repere = QPointF(x + largeur * 0.53, y + hauteur * 0.43)
        painter.setPen(QPen(QColor("#A8755C"), 0.8))
        painter.setBrush(QColor("#C58D70"))
        painter.drawEllipse(repere, 1.6, 1.6)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(repere, 3.0, 3.0)

        # Rose des vents miniature dans un angle.
        rose = QPointF(x + largeur * 0.86, y + hauteur * 0.78)
        painter.setPen(QPen(QColor("#9B8C75"), 0.65))
        painter.drawLine(
            QPointF(rose.x(), rose.y() - 3),
            QPointF(rose.x(), rose.y() + 3),
        )
        painter.drawLine(
            QPointF(rose.x() - 3, rose.y()),
            QPointF(rose.x() + 3, rose.y()),
        )
        painter.setBrush(QColor("#9B8C75"))
        painter.drawEllipse(rose, 0.8, 0.8)

        painter.restore()

    # --------------------------------------------------------------------------
    # Dessin de la presse
    # --------------------------------------------------------------------------

    def _dessiner_presse(
        self,
        painter: QPainter,
        x: float,
        y: float,
        echelle: float,
        intensite: float,
    ) -> None:
        """Dessine une presse typographique ancienne avec ses détails mécaniques."""

        painter.save()
        painter.translate(x, y)
        painter.scale(echelle, echelle)

        bois = QColor("#987657")
        bois_clair = QColor("#B89975")
        bois_lumiere = QColor("#D0B18B")
        bois_fonce = QColor("#71543F")
        metal = QColor("#77877F")
        metal_clair = QColor("#C1C9BF")
        metal_ombre = QColor("#58665F")

        # Socle inférieur et ses deux moulures.
        painter.setPen(QPen(bois_fonce, 0.9))
        painter.setBrush(bois)
        painter.drawRoundedRect(QRectF(0, 49, 105, 7), 2, 2)
        painter.setPen(QPen(bois_lumiere, 0.7))
        painter.drawLine(QPointF(3, 51), QPointF(102, 51))
        painter.setPen(QPen(bois_fonce, 0.65))
        painter.drawLine(QPointF(4, 55), QPointF(101, 55))

        # Pieds et montants latéraux.
        painter.setPen(QPen(bois_fonce, 0.9))
        painter.setBrush(bois_clair)
        painter.drawRoundedRect(QRectF(8, 12, 8, 39), 1.5, 1.5)
        painter.drawRoundedRect(QRectF(89, 12, 8, 39), 1.5, 1.5)

        # Arêtes éclairées des montants.
        painter.setPen(QPen(bois_lumiere, 0.75))
        painter.drawLine(QPointF(10, 15), QPointF(10, 48))
        painter.drawLine(QPointF(91, 15), QPointF(91, 48))

        # Renforts obliques reliant les montants au socle.
        renfort_gauche = QPainterPath()
        renfort_gauche.moveTo(16, 39)
        renfort_gauche.lineTo(27, 49)
        renfort_gauche.lineTo(16, 49)
        renfort_gauche.closeSubpath()
        renfort_droit = QPainterPath()
        renfort_droit.moveTo(89, 39)
        renfort_droit.lineTo(78, 49)
        renfort_droit.lineTo(89, 49)
        renfort_droit.closeSubpath()
        painter.setPen(QPen(bois_fonce, 0.7))
        painter.setBrush(bois)
        painter.drawPath(renfort_gauche)
        painter.drawPath(renfort_droit)

        # Traverse supérieure, avec moulure.
        painter.setPen(QPen(bois_fonce, 1.0))
        painter.setBrush(bois)
        painter.drawRoundedRect(QRectF(3, 6, 99, 10), 2, 2)
        painter.setPen(QPen(bois_lumiere, 0.8))
        painter.drawLine(QPointF(7, 8), QPointF(98, 8))
        painter.setPen(QPen(bois_fonce, 0.6))
        painter.drawLine(QPointF(6, 15), QPointF(99, 15))

        # Grain du bois : traits courts et discrets.
        painter.setPen(QPen(QColor("#795D45"), 0.45))
        painter.drawLine(QPointF(20, 10), QPointF(29, 10))
        painter.drawLine(QPointF(66, 12), QPointF(77, 12))
        painter.drawLine(QPointF(12, 23), QPointF(12, 32))
        painter.drawLine(QPointF(93, 26), QPointF(93, 35))

        # Chapeaux / assemblages métalliques sur les montants.
        painter.setPen(QPen(metal_ombre, 0.65))
        painter.setBrush(metal_clair)
        painter.drawEllipse(QPointF(12, 12), 1.5, 1.5)
        painter.drawEllipse(QPointF(93, 12), 1.5, 1.5)
        painter.setPen(QPen(QColor("#F1E9D8"), 0.5))
        painter.drawLine(QPointF(11, 11.5), QPointF(12.5, 11.5))
        painter.drawLine(QPointF(92, 11.5), QPointF(93.5, 11.5))

        # Vis centrale filetée.
        decalage_plaque = 1.5 * intensite
        painter.setPen(
            QPen(metal_ombre, 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        )
        painter.drawLine(
            QPointF(52.5, 14),
            QPointF(52.5, 29 + decalage_plaque),
        )
        painter.setPen(QPen(metal_clair, 1.0))
        for i in range(4):
            yy = 17 + i * 3.0 + decalage_plaque * (i / 4)
            painter.drawLine(QPointF(50.8, yy), QPointF(54.2, yy - 1.1))

        # Volant / poignée en T au sommet de la vis.
        painter.setPen(
            QPen(metal_ombre, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        )
        painter.drawLine(QPointF(42, 18), QPointF(63, 18))
        painter.setPen(
            QPen(metal_clair, 1.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        )
        painter.drawLine(QPointF(43, 17.2), QPointF(62, 17.2))
        painter.setPen(QPen(metal_ombre, 1.7))
        painter.drawEllipse(QPointF(52.5, 18), 2.1, 2.1)
        painter.setBrush(metal_clair)
        painter.drawEllipse(QPointF(52.5, 18), 0.9, 0.9)

        # Tête de pression et plaque mobile.
        painter.setPen(QPen(bois_fonce, 0.8))
        painter.setBrush(bois_clair)
        painter.drawRoundedRect(
            QRectF(32, 28 + decalage_plaque, 41, 6),
            1.5,
            1.5,
        )
        painter.setPen(QPen(bois_lumiere, 0.7))
        painter.drawLine(
            QPointF(35, 29 + decalage_plaque),
            QPointF(70, 29 + decalage_plaque),
        )

        # Petite plaque métallique sous le bloc de pression.
        painter.setPen(QPen(metal_ombre, 0.7))
        painter.setBrush(metal)
        painter.drawRoundedRect(
            QRectF(35, 34 + decalage_plaque, 35, 2.2),
            0.7,
            0.7,
        )
        painter.setPen(QPen(metal_clair, 0.5))
        painter.drawLine(
            QPointF(37, 34.5 + decalage_plaque),
            QPointF(68, 34.5 + decalage_plaque),
        )

        # Rouleaux latéraux et axes.
        for cx in (24, 81):
            painter.setPen(QPen(bois_fonce, 0.7))
            painter.setBrush(QColor("#B69A78"))
            painter.drawEllipse(QPointF(cx, 43), 3.0, 3.0)
            painter.setPen(QPen(metal_ombre, 0.7))
            painter.setBrush(metal_clair)
            painter.drawEllipse(QPointF(cx, 43), 1.1, 1.1)

        # Rails de guidage de la feuille.
        painter.setPen(QPen(metal, 0.8))
        painter.drawLine(QPointF(19, 47), QPointF(86, 47))
        painter.setPen(QPen(metal_clair, 0.45))
        painter.drawLine(QPointF(20, 46), QPointF(85, 46))

        # Petites vis du bâti.
        painter.setPen(QPen(metal_ombre, 0.65))
        painter.setBrush(metal_clair)
        for cx, cy in ((12, 37), (93, 37), (12, 19), (93, 19)):
            painter.drawEllipse(QPointF(cx, cy), 1.1, 1.1)
            painter.setPen(QPen(metal_ombre, 0.45))
            painter.drawLine(QPointF(cx - 0.6, cy), QPointF(cx + 0.6, cy))
            painter.setPen(QPen(metal_ombre, 0.65))

        painter.restore()

    # --------------------------------------------------------------------------
    # Dessin
    # --------------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        largeur = self.width()
        hauteur = self.height()
        decalage_appui = 1.5 if self._enfonce else 0.0
        desactive = not self.isEnabled()
        intensite_survol = self._survol if not desactive else 0.0

        rect_bouton = QRectF(
            5,
            4 + decalage_appui,
            largeur - 10,
            hauteur - 11,
        )

        # Ombre portée.
        if not self._enfonce:
            rect_ombre = QRectF(rect_bouton)
            rect_ombre.translate(0, 3)

            couleur_ombre = QColor("#37352E")
            couleur_ombre.setAlpha(35 if not desactive else 17)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(couleur_ombre)
            painter.drawRoundedRect(rect_ombre, 11, 11)

        # Fond papier.
        couleur_haut = QColor("#F8F6EF")
        couleur_bas = QColor("#EEEAE0")
        couleur_contour = QColor("#D1C8B8")

        if desactive:
            couleur_haut = QColor("#F0EFE9")
            couleur_bas = QColor("#E9E7E0")
            couleur_contour = QColor("#D8D5CD")
        elif self._enfonce:
            couleur_haut = QColor("#EEE9DD")
            couleur_bas = QColor("#E7E0D2")

        degrade_papier = QLinearGradient(
            rect_bouton.topLeft(),
            rect_bouton.bottomLeft(),
        )
        degrade_papier.setColorAt(0.0, couleur_haut)
        degrade_papier.setColorAt(1.0, couleur_bas)

        chemin_bouton = QPainterPath()
        chemin_bouton.addRoundedRect(rect_bouton, 11, 11)

        painter.setPen(QPen(couleur_contour, 1.0))
        painter.setBrush(degrade_papier)
        painter.drawPath(chemin_bouton)

        # Fibres très discrètes dans le papier.
        painter.save()
        painter.setClipPath(chemin_bouton)
        couleur_fibre = QColor("#BEB5A5")
        couleur_fibre.setAlpha(22 if not desactive else 10)
        painter.setPen(QPen(couleur_fibre, 0.55))
        for i in range(7):
            y = rect_bouton.top() + 8 + i * 8
            painter.drawLine(
                QPointF(rect_bouton.left() + 8, y),
                QPointF(rect_bouton.right() - 8, y - 1.5),
            )
        painter.restore()

        # Presse et feuille imprimée.
        zone_dessin_x = rect_bouton.left() + 10
        zone_dessin_y = rect_bouton.top() + 4
        echelle = min(0.72, (hauteur - 17) / 62)
        echelle = max(0.62, echelle)

        avance_feuille = 2.5 * intensite_survol
        self._dessiner_feuille(
            painter,
            zone_dessin_x + 20 + avance_feuille,
            rect_bouton.top() + 43 - 1.0 * intensite_survol,
            77,
            21,
            0.96 if not desactive else 0.65,
        )

        self._dessiner_presse(
            painter,
            zone_dessin_x,
            zone_dessin_y,
            echelle,
            intensite_survol,
        )

        # Libellé centré dans l'espace restant.
        zone_texte = rect_bouton.adjusted(125, 0, -34, 0)

        police = QFont("Segoe UI", max(11, min(15, int(hauteur * 0.19))))
        police.setWeight(QFont.Weight.DemiBold)
        painter.setFont(police)

        texte_affiche = painter.fontMetrics().elidedText(
            self.text(),
            Qt.TextElideMode.ElideRight,
            max(1, int(zone_texte.width() - 8)),
        )

        painter.setPen(QColor("#3D4944") if not desactive else QColor("#96958D"))
        painter.drawText(
            zone_texte,
            Qt.AlignmentFlag.AlignCenter,
            texte_affiche,
        )

        # Petite flèche discrète à droite.
        couleur_fleche = QColor("#89958A")
        couleur_fleche.setAlpha(115 if not desactive else 55)
        painter.setPen(
            QPen(
                couleur_fleche,
                1.35,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )

        centre_fleche = QPointF(
            rect_bouton.right() - 17,
            rect_bouton.center().y(),
        )
        fleche = QPainterPath()
        fleche.moveTo(centre_fleche.x() - 3, centre_fleche.y() - 4)
        fleche.lineTo(centre_fleche.x() + 1, centre_fleche.y())
        fleche.lineTo(centre_fleche.x() - 3, centre_fleche.y() + 4)
        painter.drawPath(fleche)

        # Indication de focus clavier.
        if self.hasFocus() and self.isEnabled():
            rect_focus = rect_bouton.adjusted(3, 3, -3, -3)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(
                QPen(
                    QColor("#879B8F"),
                    1.1,
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

        self.setWindowTitle("Aperçu — presse cartographique")
        self.setMinimumSize(540, 220)

        contenu = QWidget()
        contenu.setStyleSheet("""
            QWidget {
                background-color: #F3F2ED;
                color: #3D4944;
                font-family: "Segoe UI";
            }
        """)

        disposition = QVBoxLayout(contenu)
        disposition.setContentsMargins(34, 28, 34, 28)
        disposition.setSpacing(13)

        titre = QLabel("Atelier cartographique")
        titre.setStyleSheet("""
            QLabel {
                color: #3D4944;
                font-size: 17px;
                font-weight: 600;
            }
        """)

        aide = QLabel("Survole le bouton, clique dessus ou utilise la touche Tab.")
        aide.setStyleSheet("""
            QLabel {
                color: #777B73;
                font-size: 12px;
            }
        """)

        self.bouton = BoutonCreationCartes()
        self.bouton.clicked.connect(self._bouton_clique)

        self.etat = QLabel(" ")
        self.etat.setStyleSheet("""
            QLabel {
                color: #71877B;
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
        self.etat.setText("La presse cartographique est prête !")


if __name__ == "__main__":
    import sys, os

    sys.path.append(os.getcwd())

    application = QApplication(sys.argv)
    fenetre = FenetreTest()
    fenetre.show()
    sys.exit(application.exec())
