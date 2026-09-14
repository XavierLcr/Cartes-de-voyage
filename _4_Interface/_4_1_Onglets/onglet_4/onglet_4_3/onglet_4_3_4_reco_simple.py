################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_3                                #
# Onglet 4.3.4 – Suggestions de nouvelles destinations – Reco. simples         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtWidgets import QWidget, QSizePolicy, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient, QPen, QPainterPath

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import _trouver_police_disponible

# 1 -- Classe des recommandations simples --------------------------------------


class CarteRecommandationSimple(QWidget):
    """
    Billet ferroviaire compact au format proche de 4:3.

    La partie principale affiche le pays et la région recommandée.
    Un talon détachable à droite contient le rang de la recommandation.
    """

    def __init__(
        self,
        rang: int,
        pays_nom: str,
        emoji: str,
        region: str,
        parent=None,
    ):
        super().__init__(parent)

        self.rang = str(rang)
        self.pays_nom = pays_nom
        self.emoji = emoji
        self.region = region

        self.setMinimumSize(150, 112)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Ombre
        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(17)
        self._ombre_effet.setOffset(0, 4)

        couleur_ombre = QColor("#000000")
        couleur_ombre.setAlpha(75)

        self._ombre_effet.setColor(couleur_ombre)
        self.setGraphicsEffect(self._ombre_effet)

        # Polices
        self.police_principale = _trouver_police_disponible(
            [
                "CormorantGaramond",
                "Book Antiqua",
                "Georgia",
                "Palatino Linotype",
                "Times New Roman",
            ]
        )

        self.police_technique = _trouver_police_disponible(
            [
                "Century Gothic",
                "Segoe UI",
                "Arial",
            ]
        )

    # --------------------------------------------------------------------------
    # Dessin
    # --------------------------------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()
        cote = min(w, h)

        rect = QRectF(
            6,
            6,
            w - 12,
            h - 12,
        )

        # Talon à droite : environ 23 % du billet
        x_separation = rect.left() + rect.width() * 0.77

        # ----------------------------------------------------------------------
        # Forme générale du billet
        # ----------------------------------------------------------------------

        chemin_ticket = QPainterPath()

        chemin_ticket.addRoundedRect(
            rect,
            cote * 0.045,
            cote * 0.045,
        )

        # Encoches entre billet et talon
        rayon_encoche = cote * 0.045

        for y in (
            rect.top(),
            rect.bottom(),
        ):

            encoche = QPainterPath()

            encoche.addEllipse(
                QRectF(
                    x_separation - rayon_encoche,
                    y - rayon_encoche,
                    rayon_encoche * 2,
                    rayon_encoche * 2,
                )
            )

            chemin_ticket = chemin_ticket.subtracted(encoche)

        # ----------------------------------------------------------------------
        # Papier cartonné
        # ----------------------------------------------------------------------

        degrade_papier = QLinearGradient(
            rect.topLeft(),
            rect.bottomLeft(),
        )

        degrade_papier.setColorAt(0.00, QColor("#F5E9CB"))
        degrade_papier.setColorAt(0.20, QColor("#EFE0BC"))
        degrade_papier.setColorAt(0.55, QColor("#F3E5C5"))
        degrade_papier.setColorAt(0.82, QColor("#E9D6AC"))
        degrade_papier.setColorAt(1.00, QColor("#F2E3BF"))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade_papier)
        painter.drawPath(chemin_ticket)

        # ----------------------------------------------------------------------
        # Texture discrète du papier
        # ----------------------------------------------------------------------

        painter.save()
        painter.setClipPath(chemin_ticket)

        couleur_fibre = QColor("#806F54")
        couleur_fibre.setAlpha(18)

        painter.setPen(
            QPen(
                couleur_fibre,
                0.6,
            )
        )

        for i in range(12):

            y = rect.top() + rect.height() * (i + 0.7) / 13

            decalage = ((i * 7) % 11) - 5

            painter.drawLine(
                QPointF(
                    rect.left() + 8,
                    y,
                ),
                QPointF(
                    rect.right() - 8,
                    y + decalage * 0.15,
                ),
            )

        # ----------------------------------------------------------------------
        # Talon détachable
        # ----------------------------------------------------------------------

        couleur_talon = QColor("#DDC79B")
        couleur_talon.setAlpha(145)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(couleur_talon)

        painter.drawRect(
            QRectF(
                x_separation,
                rect.top(),
                rect.right() - x_separation,
                rect.height(),
            )
        )

        painter.restore()

        # ----------------------------------------------------------------------
        # Bordure
        # ----------------------------------------------------------------------

        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.setPen(
            QPen(
                QColor("#75634B"),
                max(0.8, cote * 0.007),
            )
        )

        painter.drawPath(chemin_ticket)

        # Filet intérieur
        rect_interieur = rect.adjusted(
            cote * 0.025,
            cote * 0.025,
            -cote * 0.025,
            -cote * 0.025,
        )

        couleur_filet = QColor("#8B785A")
        couleur_filet.setAlpha(95)

        painter.setPen(
            QPen(
                couleur_filet,
                0.7,
            )
        )

        painter.drawRoundedRect(
            rect_interieur,
            cote * 0.025,
            cote * 0.025,
        )

        # ----------------------------------------------------------------------
        # Ligne perforée
        # ----------------------------------------------------------------------

        couleur_perforation = QColor("#64533E")
        couleur_perforation.setAlpha(120)

        stylo_perforation = QPen(
            couleur_perforation,
            max(0.8, cote * 0.008),
            Qt.PenStyle.DashLine,
        )

        painter.setPen(stylo_perforation)

        painter.drawLine(
            QPointF(
                x_separation,
                rect.top() + rayon_encoche,
            ),
            QPointF(
                x_separation,
                rect.bottom() - rayon_encoche,
            ),
        )

        # ----------------------------------------------------------------------
        # Zone principale
        # ----------------------------------------------------------------------

        marge_x = rect.width() * 0.045

        zone_principale = QRectF(
            rect.left() + marge_x,
            rect.top(),
            x_separation - rect.left() - 2 * marge_x,
            rect.height(),
        )

        # Petit train
        taille_train = min(
            cote * 0.16,
            zone_principale.width() * 0.18,
        )

        centre_train = QPointF(
            zone_principale.left() + taille_train * 0.65,
            rect.top() + rect.height() * 0.22,
        )

        self._dessiner_train(
            painter,
            centre_train,
            taille_train,
        )

        # ----------------------------------------------------------------------
        # Pays
        # ----------------------------------------------------------------------

        rect_pays = QRectF(
            centre_train.x() + taille_train * 0.70,
            rect.top() + rect.height() * 0.09,
            zone_principale.right() - centre_train.x() - taille_train * 0.78,
            rect.height() * 0.24,
        )

        painter.setFont(
            QFont(
                self.police_technique,
                max(7, int(cote * 0.075)),
                QFont.Weight.DemiBold,
            )
        )

        painter.setPen(QColor("#28343A"))

        self._dessiner_texte_wrap(
            painter,
            rect_pays,
            f"{self.emoji} {self.pays_nom}".strip(),
            alignement=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )

        # ----------------------------------------------------------------------
        # Petite ligne ferroviaire
        # ----------------------------------------------------------------------

        y_ligne = rect.top() + rect.height() * 0.40

        x_debut = zone_principale.left()
        x_fin = zone_principale.right()

        couleur_rail = QColor("#565148")

        painter.setPen(
            QPen(
                couleur_rail,
                max(0.9, cote * 0.008),
            )
        )

        painter.drawLine(
            QPointF(x_debut, y_ligne),
            QPointF(x_fin, y_ligne),
        )

        # Point de départ
        painter.setBrush(QColor("#F1E3C2"))
        painter.setPen(
            QPen(
                couleur_rail,
                max(0.8, cote * 0.007),
            )
        )

        rayon_point = cote * 0.018

        painter.drawEllipse(
            QPointF(
                x_debut + rayon_point,
                y_ligne,
            ),
            rayon_point,
            rayon_point,
        )

        # Destination
        painter.setBrush(QColor("#8A3E32"))
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawEllipse(
            QPointF(
                x_fin - rayon_point,
                y_ligne,
            ),
            rayon_point * 1.25,
            rayon_point * 1.25,
        )

        # ----------------------------------------------------------------------
        # Région : élément principal du billet
        # ----------------------------------------------------------------------

        rect_region = QRectF(
            zone_principale.left(),
            rect.top() + rect.height() * 0.48,
            zone_principale.width(),
            rect.height() * 0.38,
        )

        painter.setFont(
            QFont(
                self.police_principale,
                max(10, int(cote * 0.12)),
                QFont.Weight.DemiBold,
            )
        )

        painter.setPen(QColor("#282A29"))

        self._dessiner_texte_adaptatif(
            painter=painter,
            rect=rect_region,
            texte=self.region,
            taille_max=max(10, int(cote * 0.12)),
            taille_min=max(7, int(cote * 0.065)),
        )

        # ----------------------------------------------------------------------
        # Talon : numéro de recommandation
        # ----------------------------------------------------------------------

        largeur_talon = rect.right() - x_separation

        rect_numero = QRectF(
            x_separation + largeur_talon * 0.08,
            rect.top() + rect.height() * 0.09,
            largeur_talon * 0.84,
            rect.height() * 0.35,
        )

        painter.setFont(
            QFont(
                self.police_technique,
                max(7, int(cote * 0.055)),
                QFont.Weight.DemiBold,
            )
        )

        painter.setPen(QColor("#6E5C42"))

        painter.drawText(
            QRectF(
                rect_numero.x(),
                rect_numero.y(),
                rect_numero.width(),
                rect_numero.height() * 0.30,
            ),
            Qt.AlignmentFlag.AlignCenter,
            "N°",
        )

        painter.setFont(
            QFont(
                self.police_principale,
                max(12, int(cote * 0.18)),
                QFont.Weight.Bold,
            )
        )

        painter.setPen(QColor("#7D352D"))

        painter.drawText(
            QRectF(
                rect_numero.x(),
                rect_numero.y() + rect_numero.height() * 0.20,
                rect_numero.width(),
                rect_numero.height() * 0.80,
            ),
            Qt.AlignmentFlag.AlignCenter,
            self.rang.zfill(2),
        )

        # ----------------------------------------------------------------------
        # Faux code de contrôle
        # ----------------------------------------------------------------------

        self._dessiner_code_controle(
            painter=painter,
            rect=QRectF(
                x_separation + largeur_talon * 0.20,
                rect.top() + rect.height() * 0.56,
                largeur_talon * 0.60,
                rect.height() * 0.27,
            ),
        )

    # --------------------------------------------------------------------------
    # Petit train
    # --------------------------------------------------------------------------

    def _dessiner_train(
        self,
        painter: QPainter,
        centre: QPointF,
        taille: float,
    ):

        x = centre.x()
        y = centre.y()

        largeur = taille
        hauteur = taille * 0.62

        couleur_train = QColor("#304A56")
        couleur_vitre = QColor("#9FB8BC")
        couleur_metal = QColor("#5F625E")

        # Caisse
        rect_caisse = QRectF(
            x - largeur / 2,
            y - hauteur / 2,
            largeur,
            hauteur * 0.70,
        )

        painter.setPen(
            QPen(
                QColor("#22343C"),
                max(0.6, taille * 0.025),
            )
        )
        painter.setBrush(couleur_train)

        painter.drawRoundedRect(
            rect_caisse,
            taille * 0.08,
            taille * 0.08,
        )

        # Pare-brise
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(couleur_vitre)

        largeur_vitre = largeur * 0.27

        for decalage in (-0.18, 0.18):

            painter.drawRoundedRect(
                QRectF(
                    x + largeur * decalage - largeur_vitre / 2,
                    rect_caisse.top() + hauteur * 0.10,
                    largeur_vitre,
                    hauteur * 0.23,
                ),
                taille * 0.025,
                taille * 0.025,
            )

        # Bas métallique
        painter.setBrush(couleur_metal)

        painter.drawRect(
            QRectF(
                rect_caisse.left() + largeur * 0.10,
                rect_caisse.bottom() - hauteur * 0.13,
                largeur * 0.80,
                hauteur * 0.13,
            )
        )

        # Roues
        painter.setBrush(QColor("#373735"))

        rayon = taille * 0.075

        for decalage in (-0.27, 0.27):

            painter.drawEllipse(
                QPointF(
                    x + largeur * decalage,
                    rect_caisse.bottom() + rayon * 0.40,
                ),
                rayon,
                rayon,
            )

    # --------------------------------------------------------------------------
    # Faux code de contrôle
    # --------------------------------------------------------------------------

    def _dessiner_code_controle(
        self,
        painter: QPainter,
        rect: QRectF,
    ):

        painter.save()

        couleur = QColor("#554B3B")
        couleur.setAlpha(185)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(couleur)

        motifs = [
            1.0,
            0.45,
            0.75,
            0.35,
            1.0,
            0.55,
            0.35,
            0.80,
            0.45,
        ]

        espace = rect.width() / (len(motifs) * 1.8)

        x = rect.left()

        for i, facteur in enumerate(motifs):

            largeur = max(
                0.8,
                espace * facteur,
            )

            painter.drawRect(
                QRectF(
                    x,
                    rect.top(),
                    largeur,
                    rect.height(),
                )
            )

            x += espace * 1.8

        painter.restore()

    # --------------------------------------------------------------------------
    # Texte avec retour à la ligne
    # --------------------------------------------------------------------------

    def _dessiner_texte_wrap(
        self,
        painter,
        rect,
        texte,
        alignement=Qt.AlignmentFlag.AlignCenter,
    ):

        metrics = painter.fontMetrics()
        largeur_max = rect.width() - 1

        mots = texte.split()
        lignes = []
        ligne_courante = ""

        for mot in mots:

            essai = f"{ligne_courante} {mot}".strip()

            if metrics.horizontalAdvance(essai) <= largeur_max:

                ligne_courante = essai

            else:

                if ligne_courante:
                    lignes.append(ligne_courante)

                ligne_courante = mot

        if ligne_courante:
            lignes.append(ligne_courante)

        if not lignes:
            lignes = [""]

        # Maximum deux lignes pour conserver le caractère compact du billet
        if len(lignes) > 2:

            lignes = [
                lignes[0],
                " ".join(lignes[1:]),
            ]

        hauteur_ligne = metrics.height()
        hauteur_totale = hauteur_ligne * len(lignes)

        y_depart = rect.y() + max(
            0,
            (rect.height() - hauteur_totale) / 2,
        )

        for i, ligne in enumerate(lignes):

            rect_ligne = QRectF(
                rect.x(),
                y_depart + i * hauteur_ligne,
                rect.width(),
                hauteur_ligne,
            )

            painter.drawText(
                rect_ligne,
                alignement,
                ligne,
            )

    def _dessiner_texte_adaptatif(
        self,
        painter: QPainter,
        rect: QRectF,
        texte: str,
        taille_max: int,
        taille_min: int,
    ):
        """
        Dessine un texte sur une ou deux lignes en réduisant automatiquement
        la police jusqu'à ce que le texte tienne dans la zone disponible.
        """

        for taille in range(taille_max, taille_min - 1, -1):

            police = QFont(
                self.police_principale,
                taille,
                QFont.Weight.DemiBold,
            )

            painter.setFont(police)
            metrics = painter.fontMetrics()

            # ------------------------------------------------------------------
            # Recherche d'une disposition sur une ou deux lignes
            # ------------------------------------------------------------------

            mots = texte.split()

            meilleures_lignes = None

            # Une seule ligne si possible
            if metrics.horizontalAdvance(texte) <= rect.width():

                meilleures_lignes = [texte]

            # Sinon recherche de la meilleure coupure en deux lignes
            else:

                meilleure_largeur = float("inf")

                for i in range(1, len(mots)):

                    ligne_1 = " ".join(mots[:i])
                    ligne_2 = " ".join(mots[i:])

                    largeur_1 = metrics.horizontalAdvance(ligne_1)
                    largeur_2 = metrics.horizontalAdvance(ligne_2)

                    largeur_max = max(
                        largeur_1,
                        largeur_2,
                    )

                    if (
                        largeur_1 <= rect.width()
                        and largeur_2 <= rect.width()
                        and largeur_max < meilleure_largeur
                    ):

                        meilleure_largeur = largeur_max

                        meilleures_lignes = [
                            ligne_1,
                            ligne_2,
                        ]

            # ------------------------------------------------------------------
            # Vérification verticale
            # ------------------------------------------------------------------

            if meilleures_lignes is None:
                continue

            hauteur_totale = metrics.height() * len(meilleures_lignes)

            if hauteur_totale > rect.height():
                continue

            # ------------------------------------------------------------------
            # Dessin
            # ------------------------------------------------------------------

            y = rect.center().y() - hauteur_totale / 2

            for ligne in meilleures_lignes:

                rect_ligne = QRectF(
                    rect.left(),
                    y,
                    rect.width(),
                    metrics.height(),
                )

                painter.drawText(
                    rect_ligne,
                    Qt.AlignmentFlag.AlignCenter,
                    ligne,
                )

                y += metrics.height()

            return
