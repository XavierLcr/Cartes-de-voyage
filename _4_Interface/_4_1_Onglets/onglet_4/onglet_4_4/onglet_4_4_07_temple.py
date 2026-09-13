################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_4                                #
# Onglet 4.4.7 – Temple grec                                                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

# 1 -- Classe du temple grec ---------------------------------------------------


class TempleGrec:
    """
    Dessine un temple grec monumental.

    Le temple est composé :
        - d'un soubassement à plusieurs degrés ;
        - d'un naos sombre en arrière-plan ;
        - de colonnes cannelées ;
        - de chapiteaux décorés ;
        - d'un entablement avec architrave et frise ;
        - d'un fronton triangulaire ;
        - de plusieurs éléments décoratifs.

    Les couleurs sont dérivées du thème général du widget.
    """

    def __init__(
        self,
        proportion_largeur: float = 0.84,
        proportion_hauteur: float = 0.70,
        proportion_sol: float = 0.40,
        n_colonnes: int = 6,
    ):

        self.proportion_largeur = proportion_largeur
        self.proportion_hauteur = proportion_hauteur
        self.proportion_sol = proportion_sol

        self.n_colonnes = max(4, n_colonnes)

    # 2 -- Couleurs ------------------------------------------------------------

    @staticmethod
    def _melanger(
        couleur_1: QColor,
        couleur_2: QColor,
        poids: float,
    ) -> QColor:
        """Interpole simplement deux couleurs en RGB."""

        poids = max(0.0, min(1.0, poids))

        return QColor(
            int(couleur_1.red() * (1 - poids) + couleur_2.red() * poids),
            int(couleur_1.green() * (1 - poids) + couleur_2.green() * poids),
            int(couleur_1.blue() * (1 - poids) + couleur_2.blue() * poids),
        )

    @staticmethod
    def _couleur_theme(
        theme,
        cle: str,
        repli: str,
    ) -> QColor:
        """Récupère une couleur du thème avec une couleur de repli."""

        try:
            couleur = theme.couleur(cle)

            if isinstance(couleur, QColor):
                return QColor(couleur)

            return QColor(couleur)

        except (KeyError, AttributeError, TypeError):
            return QColor(repli)

    def _palette(
        self,
        theme,
    ) -> dict:
        """Construit les différentes nuances du marbre."""

        clair = self._couleur_theme(
            theme,
            "pierre_claire",
            "#DDD6C8",
        )

        fonce = self._couleur_theme(
            theme,
            "pierre_foncee",
            "#968D81",
        )

        blanc = QColor("#FFFDF8")
        noir = QColor("#413D39")
        dore = QColor("#B89A5A")

        return {
            "marbre": self._melanger(clair, blanc, 0.28),
            "marbre_clair": self._melanger(clair, blanc, 0.55),
            "marbre_lumiere": self._melanger(clair, blanc, 0.78),
            "marbre_moyen": clair,
            "marbre_ombre": self._melanger(clair, fonce, 0.52),
            "marbre_fonce": self._melanger(fonce, noir, 0.18),
            "joint": self._melanger(fonce, noir, 0.22),
            "interieur": self._melanger(fonce, noir, 0.60),
            "interieur_clair": self._melanger(fonce, noir, 0.38),
            "dore": dore,
        }

    # 3 -- Géométrie générale --------------------------------------------------

    def _rect_temple(
        self,
        rect_scene: QRectF,
    ) -> QRectF:
        """Calcule la zone générale occupée par le temple."""

        largeur = rect_scene.width() * self.proportion_largeur
        hauteur = rect_scene.height() * self.proportion_hauteur

        # Début du sol
        y_sol = rect_scene.bottom() - rect_scene.height() * self.proportion_sol

        # Le temple pénètre légèrement dans le sol afin de paraître posé dessus.
        y_bas = y_sol + rect_scene.height() * self.proportion_sol * 1 / 3

        return QRectF(
            rect_scene.center().x() - largeur / 2,
            y_bas - hauteur,
            largeur,
            hauteur,
        )

    @staticmethod
    def _trapeze(
        gauche_haut: float,
        droite_haut: float,
        gauche_bas: float,
        droite_bas: float,
        y_haut: float,
        y_bas: float,
    ) -> QPainterPath:
        """Crée un trapèze."""

        chemin = QPainterPath()

        chemin.moveTo(QPointF(gauche_haut, y_haut))

        chemin.lineTo(QPointF(droite_haut, y_haut))

        chemin.lineTo(QPointF(droite_bas, y_bas))

        chemin.lineTo(QPointF(gauche_bas, y_bas))

        chemin.closeSubpath()

        return chemin

    # 4 -- Ombre générale ------------------------------------------------------

    def _dessiner_ombre(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine une ombre discrète derrière le temple."""

        couleur = QColor(20, 20, 20, 40)

        ombre = QRectF(
            rect.left() + rect.width() * 0.025,
            rect.bottom() - rect.height() * 0.045,
            rect.width() * 0.95,
            rect.height() * 0.07,
        )

        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(couleur)

        painter.drawEllipse(ombre)

    # 5 -- Soubassement --------------------------------------------------------

    def _dessiner_degres(
        self,
        painter: QPainter,
        rect: QRectF,
        palette: dict,
    ) -> float:
        """
        Dessine les trois degrés du temple.

        Retourne la coordonnée Y du sommet du soubassement.
        """

        hauteur_totale = rect.height() * 0.115
        hauteur_degre = hauteur_totale / 3

        marges = (
            0.00,
            0.025,
            0.050,
        )

        couleurs = (
            palette["marbre_ombre"],
            palette["marbre_moyen"],
            palette["marbre_clair"],
        )

        y_bas = rect.bottom()

        for i in range(3):

            marge = rect.width() * marges[i]

            y_haut = y_bas - hauteur_degre

            degrade = QLinearGradient(
                0,
                y_haut,
                0,
                y_bas,
            )

            degrade.setColorAt(
                0.0,
                self._melanger(
                    couleurs[i],
                    QColor("#FFFFFF"),
                    0.20,
                ),
            )

            degrade.setColorAt(
                1.0,
                couleurs[i],
            )

            painter.setBrush(QBrush(degrade))

            painter.setPen(
                QPen(
                    palette["joint"],
                    0.8,
                )
            )

            painter.drawRect(
                QRectF(
                    rect.left() + marge,
                    y_haut,
                    rect.width() - 2 * marge,
                    hauteur_degre,
                )
            )

            # Arête lumineuse
            lumiere = QColor(palette["marbre_lumiere"])

            lumiere.setAlpha(150)

            painter.setPen(
                QPen(
                    lumiere,
                    1.0,
                )
            )

            painter.drawLine(
                QPointF(
                    rect.left() + marge,
                    y_haut,
                ),
                QPointF(
                    rect.right() - marge,
                    y_haut,
                ),
            )

            y_bas = y_haut

        return y_bas

    # 6 -- Naos ----------------------------------------------------------------

    def _dessiner_naos(
        self,
        painter: QPainter,
        rect: QRectF,
        y_haut: float,
        y_bas: float,
        palette: dict,
    ) -> None:
        """Dessine la partie sombre située derrière les colonnes."""

        largeur = rect.width() * 0.59

        rect_naos = QRectF(
            rect.center().x() - largeur / 2,
            y_haut,
            largeur,
            y_bas - y_haut,
        )

        degrade = QLinearGradient(
            rect_naos.left(),
            rect_naos.top(),
            rect_naos.right(),
            rect_naos.bottom(),
        )

        degrade.setColorAt(
            0.0,
            palette["interieur_clair"],
        )

        degrade.setColorAt(
            0.50,
            palette["interieur"],
        )

        degrade.setColorAt(
            1.0,
            palette["interieur_clair"],
        )

        painter.setPen(
            QPen(
                palette["marbre_ombre"],
                1.3,
            )
        )

        painter.setBrush(QBrush(degrade))

        painter.drawRect(rect_naos)

        # Grande porte centrale
        largeur_porte = rect_naos.width() * 0.30

        rect_porte = QRectF(
            rect_naos.center().x() - largeur_porte / 2,
            rect_naos.top() + rect_naos.height() * 0.12,
            largeur_porte,
            rect_naos.height() * 0.88,
        )

        porte = QLinearGradient(
            rect_porte.left(),
            rect_porte.top(),
            rect_porte.right(),
            rect_porte.bottom(),
        )

        porte.setColorAt(
            0.0,
            QColor("#393737"),
        )

        porte.setColorAt(
            1.0,
            QColor("#171819"),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(porte)

        painter.drawRect(rect_porte)

    # 7 -- Colonnes ------------------------------------------------------------

    def _dessiner_colonne(
        self,
        painter: QPainter,
        rect: QRectF,
        palette: dict,
    ) -> None:
        """Dessine une colonne cannelée avec base et chapiteau."""

        largeur = rect.width()
        hauteur = rect.height()

        hauteur_base = hauteur * 0.095
        hauteur_chapiteau = hauteur * 0.13

        # -- Ombre de la colonne
        ombre = QRectF(
            rect.left() + largeur * 0.08,
            rect.top() + hauteur_chapiteau,
            largeur,
            hauteur - hauteur_chapiteau,
        )

        couleur_ombre = QColor(20, 20, 20, 32)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(couleur_ombre)

        painter.drawRoundedRect(
            ombre,
            largeur * 0.10,
            largeur * 0.10,
        )

        # -- Base
        y_base = rect.bottom() - hauteur_base

        niveaux_base = (
            (1.00, 0.30),
            (0.84, 0.27),
            (0.72, 0.43),
        )

        y = rect.bottom()

        for facteur_largeur, facteur_hauteur in niveaux_base:

            h = hauteur_base * facteur_hauteur
            w = largeur * facteur_largeur

            y -= h

            degrade = QLinearGradient(
                rect.center().x() - w / 2,
                0,
                rect.center().x() + w / 2,
                0,
            )

            degrade.setColorAt(
                0.0,
                palette["marbre_ombre"],
            )

            degrade.setColorAt(
                0.32,
                palette["marbre_lumiere"],
            )

            degrade.setColorAt(
                0.72,
                palette["marbre"],
            )

            degrade.setColorAt(
                1.0,
                palette["marbre_ombre"],
            )

            painter.setBrush(degrade)

            painter.setPen(
                QPen(
                    palette["joint"],
                    0.65,
                )
            )

            painter.drawRoundedRect(
                QRectF(
                    rect.center().x() - w / 2,
                    y,
                    w,
                    h,
                ),
                h * 0.18,
                h * 0.18,
            )

        # -- Fût légèrement effilé
        y_fut_haut = rect.top() + hauteur_chapiteau
        y_fut_bas = y_base

        largeur_bas = largeur * 0.62
        largeur_haut = largeur * 0.52

        fut = self._trapeze(
            rect.center().x() - largeur_haut / 2,
            rect.center().x() + largeur_haut / 2,
            rect.center().x() - largeur_bas / 2,
            rect.center().x() + largeur_bas / 2,
            y_fut_haut,
            y_fut_bas,
        )

        degrade_fut = QLinearGradient(
            rect.center().x() - largeur_bas / 2,
            0,
            rect.center().x() + largeur_bas / 2,
            0,
        )

        degrade_fut.setColorAt(
            0.0,
            palette["marbre_ombre"],
        )

        degrade_fut.setColorAt(
            0.18,
            palette["marbre_clair"],
        )

        degrade_fut.setColorAt(
            0.43,
            palette["marbre_lumiere"],
        )

        degrade_fut.setColorAt(
            0.70,
            palette["marbre"],
        )

        degrade_fut.setColorAt(
            1.0,
            palette["marbre_ombre"],
        )

        painter.setBrush(QBrush(degrade_fut))

        painter.setPen(
            QPen(
                palette["joint"],
                0.65,
            )
        )

        painter.drawPath(fut)

        # -- Cannelures
        painter.save()

        painter.setClipPath(fut)

        n_cannelures = 9

        for i in range(1, n_cannelures):

            t = i / n_cannelures

            x_bas = rect.center().x() - largeur_bas / 2 + largeur_bas * t

            x_haut = rect.center().x() - largeur_haut / 2 + largeur_haut * t

            ombre_cannelure = QColor(palette["marbre_fonce"])

            ombre_cannelure.setAlpha(75)

            painter.setPen(
                QPen(
                    ombre_cannelure,
                    max(0.55, largeur * 0.012),
                )
            )

            painter.drawLine(
                QPointF(
                    x_haut,
                    y_fut_haut,
                ),
                QPointF(
                    x_bas,
                    y_fut_bas,
                ),
            )

            # Petit reflet juste à côté
            reflet = QColor(palette["marbre_lumiere"])

            reflet.setAlpha(70)

            painter.setPen(
                QPen(
                    reflet,
                    max(0.4, largeur * 0.007),
                )
            )

            painter.drawLine(
                QPointF(
                    x_haut + largeur * 0.018,
                    y_fut_haut,
                ),
                QPointF(
                    x_bas + largeur * 0.018,
                    y_fut_bas,
                ),
            )

        painter.restore()

        self._dessiner_chapiteau(
            painter=painter,
            rect=QRectF(
                rect.left(),
                rect.top(),
                largeur,
                hauteur_chapiteau,
            ),
            palette=palette,
        )

    # 8 -- Chapiteau -----------------------------------------------------------

    def _dessiner_chapiteau(
        self,
        painter: QPainter,
        rect: QRectF,
        palette: dict,
    ) -> None:
        """
        Dessine un chapiteau inspiré des ordres ionique et corinthien.

        Le but est ici davantage décoratif qu'archéologiquement exact.
        """

        cx = rect.center().x()

        # Col de la colonne
        rect_col = QRectF(
            cx - rect.width() * 0.28,
            rect.bottom() - rect.height() * 0.28,
            rect.width() * 0.56,
            rect.height() * 0.20,
        )

        painter.setPen(
            QPen(
                palette["joint"],
                0.6,
            )
        )

        painter.setBrush(palette["marbre_clair"])

        painter.drawRoundedRect(
            rect_col,
            2,
            2,
        )

        # Échine
        rect_echine = QRectF(
            cx - rect.width() * 0.37,
            rect.top() + rect.height() * 0.40,
            rect.width() * 0.74,
            rect.height() * 0.30,
        )

        degrade = QLinearGradient(
            rect_echine.left(),
            0,
            rect_echine.right(),
            0,
        )

        degrade.setColorAt(
            0.0,
            palette["marbre_ombre"],
        )

        degrade.setColorAt(
            0.50,
            palette["marbre_lumiere"],
        )

        degrade.setColorAt(
            1.0,
            palette["marbre_ombre"],
        )

        painter.setBrush(degrade)

        painter.drawRoundedRect(
            rect_echine,
            rect.height() * 0.10,
            rect.height() * 0.10,
        )

        # Abaque supérieur
        rect_abaque = QRectF(
            rect.left() + rect.width() * 0.04,
            rect.top() + rect.height() * 0.18,
            rect.width() * 0.92,
            rect.height() * 0.23,
        )

        painter.setBrush(palette["marbre_clair"])

        painter.drawRoundedRect(
            rect_abaque,
            2,
            2,
        )

        # Volutes
        rayon = rect.width() * 0.115

        for sens in (-1, 1):

            centre_x = cx + sens * rect.width() * 0.31

            centre_y = rect.top() + rect.height() * 0.56

            painter.setBrush(palette["marbre"])

            painter.setPen(
                QPen(
                    palette["marbre_fonce"],
                    0.8,
                )
            )

            painter.drawEllipse(
                QPointF(
                    centre_x,
                    centre_y,
                ),
                rayon,
                rayon,
            )

            painter.setBrush(palette["marbre_ombre"])

            painter.drawEllipse(
                QPointF(
                    centre_x,
                    centre_y,
                ),
                rayon * 0.42,
                rayon * 0.42,
            )

        # Petites feuilles décoratives
        painter.setBrush(palette["marbre_clair"])

        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(3):

            x = cx + (i - 1) * rect.width() * 0.14

            feuille = QPainterPath()

            feuille.moveTo(
                QPointF(
                    x,
                    rect.bottom() - rect.height() * 0.10,
                )
            )

            feuille.lineTo(
                QPointF(
                    x - rect.width() * 0.065,
                    rect.bottom() - rect.height() * 0.31,
                )
            )

            feuille.lineTo(
                QPointF(
                    x,
                    rect.bottom() - rect.height() * 0.23,
                )
            )

            feuille.lineTo(
                QPointF(
                    x + rect.width() * 0.065,
                    rect.bottom() - rect.height() * 0.31,
                )
            )

            feuille.closeSubpath()

            painter.drawPath(feuille)

    # 9 -- Entablement ---------------------------------------------------------

    def _dessiner_entablement(
        self,
        painter: QPainter,
        rect: QRectF,
        palette: dict,
    ) -> None:
        """Dessine architrave, frise et corniche."""

        # Architrave
        h_architrave = rect.height() * 0.34

        rect_architrave = QRectF(
            rect.left() + rect.width() * 0.015,
            rect.bottom() - h_architrave,
            rect.width() * 0.97,
            h_architrave,
        )

        degrade = QLinearGradient(
            0,
            rect_architrave.top(),
            0,
            rect_architrave.bottom(),
        )

        degrade.setColorAt(
            0.0,
            palette["marbre_clair"],
        )

        degrade.setColorAt(
            1.0,
            palette["marbre_ombre"],
        )

        painter.setBrush(degrade)

        painter.setPen(
            QPen(
                palette["joint"],
                0.8,
            )
        )

        painter.drawRect(rect_architrave)

        # Frise
        h_frise = rect.height() * 0.36

        rect_frise = QRectF(
            rect.left(),
            rect_architrave.top() - h_frise,
            rect.width(),
            h_frise,
        )

        painter.setBrush(palette["marbre"])

        painter.drawRect(rect_frise)

        # Triglyphes décoratifs
        n_blocs = self.n_colonnes * 2 - 1
        largeur_bloc = rect_frise.width() / n_blocs

        for i in range(n_blocs):

            if i % 2 != 0:
                continue

            x = rect_frise.left() + i * largeur_bloc + largeur_bloc * 0.28

            bloc = QRectF(
                x,
                rect_frise.top() + rect_frise.height() * 0.15,
                largeur_bloc * 0.44,
                rect_frise.height() * 0.70,
            )

            painter.setBrush(palette["marbre_ombre"])

            painter.setPen(Qt.PenStyle.NoPen)

            painter.drawRect(bloc)

            # Deux entailles lumineuses
            painter.setPen(
                QPen(
                    palette["marbre_clair"],
                    0.8,
                )
            )

            for j in (1, 2):

                xx = bloc.left() + bloc.width() * j / 3

                painter.drawLine(
                    QPointF(
                        xx,
                        bloc.top(),
                    ),
                    QPointF(
                        xx,
                        bloc.bottom(),
                    ),
                )

        # Corniche supérieure
        h_corniche = rect.height() * 0.22

        rect_corniche = QRectF(
            rect.left() - rect.width() * 0.025,
            rect_frise.top() - h_corniche,
            rect.width() * 1.05,
            h_corniche,
        )

        painter.setBrush(palette["marbre_clair"])

        painter.setPen(
            QPen(
                palette["joint"],
                0.8,
            )
        )

        painter.drawRoundedRect(
            rect_corniche,
            2,
            2,
        )

    # 10 -- Fronton ------------------------------------------------------------

    def _dessiner_fronton(
        self,
        painter: QPainter,
        rect: QRectF,
        palette: dict,
    ) -> None:
        """Dessine le grand fronton triangulaire."""

        depassement = rect.width() * 0.025

        gauche = QPointF(
            rect.left() - depassement,
            rect.bottom(),
        )

        droite = QPointF(
            rect.right() + depassement,
            rect.bottom(),
        )

        sommet = QPointF(
            rect.center().x(),
            rect.top(),
        )

        # Ombre derrière le toit
        ombre = QPainterPath()

        ombre.moveTo(
            QPointF(
                gauche.x() + 3,
                gauche.y() + 4,
            )
        )

        ombre.lineTo(
            QPointF(
                sommet.x() + 3,
                sommet.y() + 4,
            )
        )

        ombre.lineTo(
            QPointF(
                droite.x() + 3,
                droite.y() + 4,
            )
        )

        ombre.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(20, 20, 20, 35))

        painter.drawPath(ombre)

        # Triangle principal
        fronton = QPainterPath()

        fronton.moveTo(gauche)
        fronton.lineTo(sommet)
        fronton.lineTo(droite)
        fronton.closeSubpath()

        degrade = QLinearGradient(
            rect.left(),
            rect.top(),
            rect.right(),
            rect.bottom(),
        )

        degrade.setColorAt(
            0.0,
            palette["marbre_lumiere"],
        )

        degrade.setColorAt(
            0.55,
            palette["marbre_clair"],
        )

        degrade.setColorAt(
            1.0,
            palette["marbre_ombre"],
        )

        painter.setBrush(degrade)

        painter.setPen(
            QPen(
                palette["joint"],
                1.0,
            )
        )

        painter.drawPath(fronton)

        # Triangle intérieur
        marge_x = rect.width() * 0.07
        marge_y = rect.height() * 0.20

        interieur = QPainterPath()

        interieur.moveTo(
            QPointF(
                rect.left() + marge_x,
                rect.bottom() - marge_y * 0.25,
            )
        )

        interieur.lineTo(
            QPointF(
                rect.center().x(),
                rect.top() + marge_y,
            )
        )

        interieur.lineTo(
            QPointF(
                rect.right() - marge_x,
                rect.bottom() - marge_y * 0.25,
            )
        )

        interieur.closeSubpath()

        couleur_interieur = QColor(palette["marbre_ombre"])

        couleur_interieur.setAlpha(70)

        painter.setBrush(couleur_interieur)

        painter.setPen(
            QPen(
                palette["marbre_ombre"],
                0.8,
            )
        )

        painter.drawPath(interieur)

        self._dessiner_rosace_fronton(
            painter=painter,
            rect=rect,
            palette=palette,
        )

        # Corniches inclinées épaisses
        largeur_corniche = max(
            2.0,
            rect.height() * 0.065,
        )

        painter.setPen(
            QPen(
                palette["marbre_lumiere"],
                largeur_corniche,
            )
        )

        painter.drawLine(
            gauche,
            sommet,
        )

        painter.drawLine(
            sommet,
            droite,
        )

        # Ombre sous les corniches
        ombre_toit = QColor(palette["marbre_fonce"])

        ombre_toit.setAlpha(100)

        painter.setPen(
            QPen(
                ombre_toit,
                max(1.0, largeur_corniche * 0.28),
            )
        )

        painter.drawLine(
            QPointF(
                gauche.x(),
                gauche.y() + largeur_corniche * 0.45,
            ),
            QPointF(
                sommet.x(),
                sommet.y() + largeur_corniche * 0.45,
            ),
        )

        painter.drawLine(
            QPointF(
                sommet.x(),
                sommet.y() + largeur_corniche * 0.45,
            ),
            QPointF(
                droite.x(),
                droite.y() + largeur_corniche * 0.45,
            ),
        )

    # 11 -- Rosace du fronton --------------------------------------------------

    def _dessiner_rosace_fronton(
        self,
        painter: QPainter,
        rect: QRectF,
        palette: dict,
    ) -> None:
        """Dessine un petit soleil décoratif au centre du fronton."""

        centre = QPointF(
            rect.center().x(),
            rect.top() + rect.height() * 0.58,
        )

        rayon = (
            min(
                rect.width(),
                rect.height(),
            )
            * 0.085
        )

        couleur = QColor(palette["dore"])

        couleur.setAlpha(170)

        painter.setPen(
            QPen(
                couleur,
                max(0.8, rayon * 0.10),
            )
        )

        # Rayons
        for i in range(12):

            angle = i / 12 * math.tau

            x1 = centre.x() + math.cos(angle) * rayon * 1.25

            y1 = centre.y() + math.sin(angle) * rayon * 1.25

            x2 = centre.x() + math.cos(angle) * rayon * 1.75

            y2 = centre.y() + math.sin(angle) * rayon * 1.75

            painter.drawLine(
                QPointF(x1, y1),
                QPointF(x2, y2),
            )

        painter.setBrush(couleur)

        painter.drawEllipse(
            centre,
            rayon,
            rayon,
        )

        centre_clair = QColor(palette["marbre_lumiere"])

        centre_clair.setAlpha(190)

        painter.setBrush(centre_clair)

        painter.drawEllipse(
            centre,
            rayon * 0.45,
            rayon * 0.45,
        )

    # 12 -- Acrotères ----------------------------------------------------------

    def _dessiner_acroteres(
        self,
        painter: QPainter,
        rect: QRectF,
        palette: dict,
    ) -> None:
        """Ajoute trois ornements au sommet du toit."""

        taille = rect.height() * 0.16

        positions = (
            QPointF(
                rect.left(),
                rect.bottom(),
            ),
            QPointF(
                rect.center().x(),
                rect.top(),
            ),
            QPointF(
                rect.right(),
                rect.bottom(),
            ),
        )

        for centre in positions:

            base = QRectF(
                centre.x() - taille * 0.34,
                centre.y() - taille * 0.20,
                taille * 0.68,
                taille * 0.22,
            )

            painter.setPen(
                QPen(
                    palette["joint"],
                    0.6,
                )
            )

            painter.setBrush(palette["marbre_clair"])

            painter.drawRoundedRect(
                base,
                1.5,
                1.5,
            )

            ornement = QPainterPath()

            ornement.moveTo(
                QPointF(
                    centre.x(),
                    base.top() - taille * 0.75,
                )
            )

            ornement.lineTo(
                QPointF(
                    centre.x() - taille * 0.20,
                    base.top(),
                )
            )

            ornement.lineTo(
                QPointF(
                    centre.x(),
                    base.top() - taille * 0.20,
                )
            )

            ornement.lineTo(
                QPointF(
                    centre.x() + taille * 0.20,
                    base.top(),
                )
            )

            ornement.closeSubpath()

            painter.drawPath(ornement)

    # 13 -- Dessin principal ---------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        theme,
    ) -> None:
        """Dessine l'ensemble du temple grec."""

        rect = self._rect_temple(
            rect_scene=rect_scene,
        )

        palette = self._palette(
            theme=theme,
        )

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        # Proportions verticales
        hauteur_fronton = rect.height() * 0.215
        hauteur_entablement = rect.height() * 0.115
        hauteur_degres = rect.height() * 0.115

        y_fronton_bas = rect.top() + hauteur_fronton

        y_entablement_bas = y_fronton_bas + hauteur_entablement

        y_colonnes_bas = rect.bottom() - hauteur_degres

        # Ombre générale
        self._dessiner_ombre(
            painter=painter,
            rect=rect,
        )

        # Soubassement
        y_colonnes_bas = self._dessiner_degres(
            painter=painter,
            rect=rect,
            palette=palette,
        )

        # Naos en arrière-plan
        self._dessiner_naos(
            painter=painter,
            rect=rect,
            y_haut=y_entablement_bas,
            y_bas=y_colonnes_bas,
            palette=palette,
        )

        # Colonnes
        marge_colonnes = rect.width() * 0.075

        largeur_disponible = rect.width() - 2 * marge_colonnes

        hauteur_colonne = y_colonnes_bas - y_entablement_bas

        largeur_colonne = min(
            largeur_disponible / (self.n_colonnes * 1.65),
            hauteur_colonne * 0.17,
        )

        if self.n_colonnes > 1:

            espace = (largeur_disponible - largeur_colonne) / (self.n_colonnes - 1)

        else:
            espace = 0

        for i in range(self.n_colonnes):

            centre_x = rect.left() + marge_colonnes + largeur_colonne / 2 + i * espace

            rect_colonne = QRectF(
                centre_x - largeur_colonne / 2,
                y_entablement_bas,
                largeur_colonne,
                hauteur_colonne,
            )

            self._dessiner_colonne(
                painter=painter,
                rect=rect_colonne,
                palette=palette,
            )

        # Entablement
        rect_entablement = QRectF(
            rect.left() + rect.width() * 0.045,
            y_fronton_bas,
            rect.width() * 0.91,
            hauteur_entablement,
        )

        self._dessiner_entablement(
            painter=painter,
            rect=rect_entablement,
            palette=palette,
        )

        # Fronton
        rect_fronton = QRectF(
            rect.left() + rect.width() * 0.025,
            rect.top() + rect.height() * 0.025,
            rect.width() * 0.95,
            hauteur_fronton * 0.98,
        )

        self._dessiner_fronton(
            painter=painter,
            rect=rect_fronton,
            palette=palette,
        )

        # Acrotères
        self._dessiner_acroteres(
            painter=painter,
            rect=rect_fronton,
            palette=palette,
        )

        painter.restore()
