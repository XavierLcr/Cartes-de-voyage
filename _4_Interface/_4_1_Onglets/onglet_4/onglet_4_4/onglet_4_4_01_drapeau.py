################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_4                                #
# Onglet 4.4.1 – Classe graphique – Drapeau animé                              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
)

# 1 -- Classe de création d'un drapeau -----------------------------------------


class Drapeau:
    """
    Représente un drapeau complet :
        - mât ;
        - pommeau ;
        - socle ;
        - pavillon ;
        - animation de hissage ;
        - ondulation du tissu.

    La classe ne possède pas sa propre surface graphique. Elle est dessinée
    directement dans le QPainter du widget hôte via `dessiner()`.
    """

    # Réglages de l'ondulation
    N_BANDES = 100
    AMPLITUDE_RATIO = 0.07
    N_ONDES = 1.6
    VITESSE_ONDULATION = 2.0
    VITESSE_PHASE = 2.65

    def __init__(
        self,
        chemin_image: str | None,
        couleur_repli: str,
        ratio: float,
    ) -> None:

        # Données
        self.ratio = max(0.0, min(1.0, ratio))
        self.couleur_repli = QColor(couleur_repli)

        # Image
        self.pixmap = None
        self._pixmap_haute_res = None

        if chemin_image:
            pixmap = QPixmap(chemin_image)

            if not pixmap.isNull():
                self.pixmap = pixmap

        # Etat de l'animation
        self._progression_hissage = 0.0
        self._phase = 0.0

        # Paramètres de l'animation
        self._delai_ms = 0
        self._duree_ms = 900

    # 1.1 -- Gestion de l'animation --------------------------------------------

    def demarrer_animation(
        self,
        delai_ms: int = 0,
        duree_ms: int = 900,
    ) -> None:
        """Réinitialise les paramètres de l'animation de hissage."""

        self._progression_hissage = 0.0
        self._phase = 0.0

        self._delai_ms = max(0, int(delai_ms))
        self._duree_ms = max(1, int(duree_ms))

    def animer(
        self,
        temps_ecoule_ms: float,
        delta_s: float,
    ) -> None:
        """
        Met à jour l'état du drapeau.

        `temps_ecoule_ms` correspond au temps écoulé depuis le lancement
        global des animations.
        """

        if temps_ecoule_ms < self._delai_ms:
            return

        # Animation du hissage
        temps_hissage = temps_ecoule_ms - self._delai_ms
        progression = min(1.0, temps_hissage / self._duree_ms)

        # Equivalent approximatif d'un OutCubic
        self._progression_hissage = 1.0 - (1.0 - progression) ** 3

        # Ondulation du tissu
        self._phase += self.VITESSE_PHASE * delta_s

    # 1.2 -- Géométrie ---------------------------------------------------------

    def _geometrie(self, rect: QRectF) -> dict:
        """Calcule les différents éléments géométriques du drapeau."""

        largeur = rect.width()
        hauteur = rect.height()

        pole_x = rect.left() + largeur * 0.17
        pole_top = rect.top() + hauteur * 0.04
        pole_bottom = rect.bottom() - hauteur * 0.02

        marge_droite = largeur * 0.12
        flag_w = largeur - (pole_x - rect.left()) - marge_droite
        flag_h = flag_w * 0.62

        plage_max = max(
            (pole_bottom - pole_top) - flag_h,
            1.0,
        )

        hauteur_actuelle = self._progression_hissage * self.ratio * plage_max

        flag_bottom_y = pole_bottom - hauteur_actuelle
        flag_top_y = flag_bottom_y - flag_h

        return {
            "pole_x": pole_x,
            "pole_top": pole_top,
            "pole_bottom": pole_bottom,
            "flag_w": flag_w,
            "flag_h": flag_h,
            "flag_top_y": flag_top_y,
            "flag_bottom_y": flag_bottom_y,
            "hauteur_actuelle": hauteur_actuelle,
        }

    # 1.3 -- Dessin du pavillon ------------------------------------------------

    def _dessiner_drapeau_ondule(
        self,
        painter: QPainter,
        rect_drapeau: QRectF,
    ) -> None:
        """Dessine le pavillon sous forme de bandes verticales ondulées."""

        x0 = rect_drapeau.left()
        y0 = rect_drapeau.top()
        w = rect_drapeau.width()
        h = rect_drapeau.height()

        n_bandes = self.N_BANDES
        largeur_bande = w / n_bandes
        amplitude_max = h * self.AMPLITUDE_RATIO

        # Pavillon à partir d'une image
        if self.pixmap is not None:

            largeur_cible = max(int(w * 2), 1)
            hauteur_cible = max(int(h * 2), 1)

            if (
                self._pixmap_haute_res is None
                or self._pixmap_haute_res.width() != largeur_cible
                or self._pixmap_haute_res.height() != hauteur_cible
            ):
                self._pixmap_haute_res = self.pixmap.scaled(
                    largeur_cible,
                    hauteur_cible,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

            pixmap = self._pixmap_haute_res
            source_w = pixmap.width() / n_bandes

            for i in range(n_bandes):

                t = i / (n_bandes - 1)

                amplitude = amplitude_max * t

                decalage = amplitude * math.sin(
                    t * 2 * math.pi * self.N_ONDES
                    - self._phase * self.VITESSE_ONDULATION
                )

                destination = QRectF(
                    x0 + i * largeur_bande,
                    y0 + decalage,
                    largeur_bande + 0.6,
                    h,
                )

                source = QRectF(
                    i * source_w,
                    0,
                    source_w,
                    pixmap.height(),
                )

                painter.drawPixmap(
                    destination,
                    pixmap,
                    source,
                )

        # Pavillon de couleur si aucune image n'est disponible
        else:

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self.couleur_repli)

            chemin = QPainterPath()

            points_haut = []
            points_bas = []

            n_points = 24

            for i in range(n_points + 1):

                t = i / n_points

                amplitude = amplitude_max * t

                decalage = amplitude * math.sin(
                    t * 2 * math.pi * self.N_ONDES
                    - self._phase * self.VITESSE_ONDULATION
                )

                x = x0 + t * w

                points_haut.append((x, y0 + decalage))

                points_bas.append((x, y0 + h + decalage))

            chemin.moveTo(*points_haut[0])

            for point in points_haut[1:]:
                chemin.lineTo(*point)

            for point in reversed(points_bas):
                chemin.lineTo(*point)

            chemin.closeSubpath()

            painter.drawPath(chemin)

    # 1.4 -- Dessin complet ----------------------------------------------------

    def dessiner(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine le mât et son pavillon dans le rectangle fourni."""

        geo = self._geometrie(rect)

        pole_x = geo["pole_x"]
        pole_top = geo["pole_top"]
        pole_bottom = geo["pole_bottom"]

        flag_w = geo["flag_w"]
        flag_h = geo["flag_h"]

        flag_top_y = geo["flag_top_y"]
        flag_bottom_y = geo["flag_bottom_y"]

        hauteur_actuelle = geo["hauteur_actuelle"]

        # Mât ------------------------------------------------------------------

        largeur_mat = max(3.0, rect.width() * 0.045)

        gradient_mat = QLinearGradient(
            pole_x - largeur_mat / 2,
            0,
            pole_x + largeur_mat / 2,
            0,
        )

        gradient_mat.setColorAt(
            0.0,
            QColor("#D5D5D5"),
        )

        gradient_mat.setColorAt(
            0.5,
            QColor("#EEEEEE"),
        )

        gradient_mat.setColorAt(
            1.0,
            QColor("#8E8E8E"),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient_mat)

        painter.drawRoundedRect(
            QRectF(
                pole_x - largeur_mat / 2,
                pole_top,
                largeur_mat,
                pole_bottom - pole_top,
            ),
            largeur_mat / 2,
            largeur_mat / 2,
        )

        # Pommeau --------------------------------------------------------------

        rayon_pommeau = max(4.0, rect.width() * 0.04)

        painter.setBrush(QColor("#D8B24A"))

        painter.drawEllipse(
            QRectF(
                pole_x - rayon_pommeau,
                pole_top - rayon_pommeau * 1.6,
                rayon_pommeau * 2,
                rayon_pommeau * 2,
            )
        )

        # Socle ----------------------------------------------------------------

        largeur_socle = max(
            20.0,
            rect.width() * 0.22,
        )

        hauteur_socle = max(
            5.0,
            rect.height() * 0.025,
        )

        gradient_socle = QLinearGradient(
            0,
            pole_bottom,
            0,
            pole_bottom + hauteur_socle,
        )

        gradient_socle.setColorAt(
            0.0,
            QColor("#CBCBCB"),
        )

        gradient_socle.setColorAt(
            1.0,
            QColor("#929292"),
        )

        painter.setBrush(gradient_socle)

        painter.drawRoundedRect(
            QRectF(
                pole_x - largeur_socle / 2,
                pole_bottom - hauteur_socle / 2,
                largeur_socle,
                hauteur_socle,
            ),
            hauteur_socle * 0.4,
            hauteur_socle * 0.4,
        )

        # Pavillon -------------------------------------------------------------

        if hauteur_actuelle <= 1:
            return

        rect_drapeau = QRectF(
            pole_x,
            flag_top_y,
            flag_w,
            flag_h,
        )

        # Petites attaches au mât
        painter.setPen(QColor("#8E8E8E"))

        painter.drawLine(
            int(pole_x - 1),
            int(flag_top_y + 3),
            int(pole_x + 3),
            int(flag_top_y + 3),
        )

        painter.drawLine(
            int(pole_x - 1),
            int(flag_bottom_y - 3),
            int(pole_x + 3),
            int(flag_bottom_y - 3),
        )

        # Zone de clip élargie pour l'ondulation
        amplitude_max = flag_h * self.AMPLITUDE_RATIO

        zone_clip = QRectF(
            rect_drapeau.left() - 1,
            rect_drapeau.top() - amplitude_max - 1,
            rect_drapeau.width() + 2,
            rect_drapeau.height() + 2 * amplitude_max + 2,
        )

        chemin_clip = QPainterPath()
        chemin_clip.addRoundedRect(
            zone_clip,
            2,
            2,
        )

        painter.save()
        painter.setClipPath(chemin_clip)

        self._dessiner_drapeau_ondule(
            painter=painter,
            rect_drapeau=rect_drapeau,
        )

        painter.restore()
