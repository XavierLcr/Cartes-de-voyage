################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.3 – Script de création de l'icône d'une jeune pousse                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen

# 1 -- Fonction de création de la jeune pousse ---------------------------------


def _dessiner_icone_pousse(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône printemps : tige en léger S, deux feuilles asymétriques
    attachées à des hauteurs différentes, et un petit bourgeon au
    sommet."""
    bas = QPointF(centre.x(), centre.y() + taille * 0.36)
    haut = QPointF(centre.x() + taille * 0.03, centre.y() - taille * 0.30)

    # --- tige, légère forme en S ---
    tige = QPainterPath()
    tige.moveTo(bas)
    tige.cubicTo(
        QPointF(bas.x() - taille * 0.09, bas.y() - taille * 0.32),
        QPointF(haut.x() + taille * 0.09, haut.y() + taille * 0.30),
        haut,
    )
    painter.setPen(
        QPen(
            QColor(255, 255, 255, 235),
            max(1.3, taille * 0.045),
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
        )
    )
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(tige)

    @staticmethod
    def _point_sur_tige(t: float) -> QPointF:
        """Point interpolé sur la courbe de tige (Bézier cubique), pour
        attacher les feuilles bien sur le tracé plutôt qu'à côté."""
        u = 1 - t
        c1 = QPointF(bas.x() - taille * 0.09, bas.y() - taille * 0.32)
        c2 = QPointF(haut.x() + taille * 0.09, haut.y() + taille * 0.30)
        x = (
            u**3 * bas.x()
            + 3 * u**2 * t * c1.x()
            + 3 * u * t**2 * c2.x()
            + t**3 * haut.x()
        )
        y = (
            u**3 * bas.y()
            + 3 * u**2 * t * c1.y()
            + 3 * u * t**2 * c2.y()
            + t**3 * haut.y()
        )
        return QPointF(x, y)

    def dessiner_feuille(
        attache: QPointF, signe: int, echelle: float, rotation_deg: float
    ) -> None:
        """Dessine une feuille en forme de goutte (asymétrique), avec
        une fine nervure centrale, attachée au point `attache` de la
        tige et orientée par `signe` (gauche/droite) et `rotation_deg`."""
        longueur = taille * 0.34 * echelle
        largeur = taille * 0.16 * echelle
        angle = math.radians(rotation_deg) * signe

        # direction principale de la feuille (vers l'extérieur et le haut)
        direction = QPointF(math.sin(angle) * signe, -math.cos(angle))
        normale = QPointF(-direction.y(), direction.x())

        pointe = QPointF(
            attache.x() + direction.x() * longueur,
            attache.y() + direction.y() * longueur,
        )
        # point le plus large de la feuille, décalé pour l'asymétrie
        large = QPointF(
            attache.x() + direction.x() * longueur * 0.42 + normale.x() * largeur,
            attache.y() + direction.y() * longueur * 0.42 + normale.y() * largeur,
        )

        feuille = QPainterPath()
        feuille.moveTo(attache)
        feuille.quadTo(large, pointe)
        feuille.quadTo(
            QPointF(
                attache.x()
                + direction.x() * longueur * 0.5
                - normale.x() * largeur * 0.35,
                attache.y()
                + direction.y() * longueur * 0.5
                - normale.y() * largeur * 0.35,
            ),
            attache,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 225)))
        painter.drawPath(feuille)

        # nervure centrale, légèrement incurvée
        nervure = QPainterPath()
        nervure.moveTo(attache)
        nervure.quadTo(large, pointe)
        painter.setPen(QPen(QColor(255, 255, 255, 130), max(0.8, taille * 0.02)))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(nervure)

    # feuille basse, plus grande, penchée vers la gauche
    dessiner_feuille(_point_sur_tige(0.42), signe=-1, echelle=1.0, rotation_deg=48)
    # feuille haute, plus petite, penchée vers la droite
    dessiner_feuille(_point_sur_tige(0.74), signe=1, echelle=0.75, rotation_deg=40)

    # --- petit bourgeon au sommet de la tige ---
    rayon_bourgeon = taille * 0.06
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
    painter.drawEllipse(haut, rayon_bourgeon, rayon_bourgeon)
