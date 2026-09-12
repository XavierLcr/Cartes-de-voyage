################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6/onglet_4_6_1                   #
# Onglet 4.6.1.5 – Bocal de verre (géométrie + rendu du bocal)                 #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QBrush,
    QPen,
    QColor,
    QRadialGradient,
    QLinearGradient,
)

# 1 -- Classe du bocal ---------------------------------------------------------


class BocalVerre:
    """
    Porte toute la géométrie et le rendu "verre" du bocal du compteur
    circulaire (onglet_4_6_1) : calcul des mesures du corps et du col,
    tracé du contour (corps renflé + col légèrement évasé, bourrelet
    d'ouverture), teinte translucide du verre, dégradé du contour et
    reflets — indépendamment du remplissage de sable, de la pluie de
    grains ou du décor marin, qui restent gérés par `SableEtDecorMarin`.

    Le bocal est pensé pour être dessiné légèrement incliné : les
    méthodes de ce module ne s'occupent pas de la rotation elle-même
    (à la charge de l'appelant, autour du pied du bocal), seulement de
    sa forme et de son rendu une fois le repère mis en place.
    """

    def __init__(self, angle_inclinaison: float = 10.0, echelle: float = 0.6) -> None:
        # Légère inclinaison, comme un bocal planté un peu de travers dans
        # le sable plutôt que posé bien droit — l'angle est positif car
        # `QPainter.rotate` tourne dans le sens horaire : le col penche
        # donc vers la droite, dans le sens où la plage s'enfonce.
        self.angle_inclinaison = angle_inclinaison
        self.echelle = echelle

    # ---------------------------------------------------------------
    # Géométrie
    # ---------------------------------------------------------------
    def mesures(self, rect: QRectF) -> dict:
        """Calcule les dimensions clés du bocal à partir de son rectangle englobant."""
        w, h = rect.width(), rect.height()
        return {
            "x0": rect.left(),
            "x1": rect.right(),
            "y0": rect.top(),
            "y1": rect.bottom(),
            "cx": rect.center().x(),
            "corps_haut": rect.top() + h * 0.30,
            "col_largeur": w * 0.40,
            "rayon_coin": min(w, h) * 0.16,
        }

    def chemin_corps(self, m: dict) -> QPainterPath:
        x0, x1, y0, y1 = m["x0"], m["x1"], m["y0"], m["y1"]
        cx = m["cx"]
        corps_haut = m["corps_haut"]
        col_largeur = m["col_largeur"]
        r = m["rayon_coin"]
        haut_col = y0
        marge_epaule = (y1 - corps_haut) * 0.16

        # Léger évasement du bord du col (bourrelet), plutôt que des parois
        # parfaitement parallèles jusqu'en haut.
        evasement = col_largeur * 0.08
        col_x0_haut = cx - col_largeur / 2 - evasement
        col_x1_haut = cx + col_largeur / 2 + evasement
        col_x0_bas = cx - col_largeur / 2
        col_x1_bas = cx + col_largeur / 2

        # Renflement du corps : les parois bombent légèrement vers
        # l'extérieur au lieu d'être des lignes droites, comme un bocal
        # soufflé plutôt qu'un cylindre.
        bulge = (x1 - x0) * 0.045
        corps_milieu_y = corps_haut + (y1 - (corps_haut + marge_epaule)) * 0.55

        chemin = QPainterPath()
        chemin.moveTo(col_x0_haut, haut_col)
        chemin.lineTo(col_x0_bas, corps_haut)
        chemin.quadTo(x0 - bulge * 0.2, corps_haut, x0, corps_haut + marge_epaule)
        chemin.quadTo(x0 - bulge, corps_milieu_y, x0, y1 - r)
        chemin.quadTo(x0, y1, x0 + r, y1)
        chemin.lineTo(x1 - r, y1)
        chemin.quadTo(x1, y1, x1, y1 - r)
        chemin.quadTo(x1 + bulge, corps_milieu_y, x1, corps_haut + marge_epaule)
        chemin.quadTo(x1 + bulge * 0.2, corps_haut, col_x1_bas, corps_haut)
        chemin.lineTo(col_x1_haut, haut_col)
        chemin.closeSubpath()
        return chemin

    # ---------------------------------------------------------------
    # Rendu du verre
    # ---------------------------------------------------------------
    def dessiner_verre_corps(self, painter: QPainter, contour: QPainterPath) -> None:
        """Légère teinte bleu-vert translucide sur tout le corps, pour que les
        parois se lisent comme du verre même là où il n'y a pas encore de
        sable — plutôt qu'un bocal invisible tant qu'il n'est pas assez
        rempli."""
        painter.save()
        painter.setClipPath(contour)
        bbox = contour.boundingRect()
        gradient = QLinearGradient(bbox.left(), 0, bbox.right(), 0)
        c_bord = QColor("#BFD9E0")
        c_bord.setAlphaF(0.24)
        c_centre = QColor("#EAF5F7")
        c_centre.setAlphaF(0.09)
        gradient.setColorAt(0.0, c_bord)
        gradient.setColorAt(0.5, c_centre)
        gradient.setColorAt(1.0, c_bord)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(bbox)
        painter.restore()

    def dessiner_contour(
        self,
        painter: QPainter,
        m: dict,
        contour: QPainterPath,
        palette: dict,
        side: float,
    ) -> None:
        """Contour en dégradé horizontal (bords plus sombres, centre plus
        clair) pour suggérer la courbure/épaisseur du verre plutôt
        qu'un simple trait uni."""
        grad_contour = QLinearGradient(m["x0"], 0, m["x1"], 0)
        c_bord_sombre = QColor(palette["piste"]).darker(130)
        c_bord_sombre.setAlpha(palette["piste"].alpha())
        c_milieu = QColor(palette["piste"])
        c_milieu.setAlpha(int(palette["piste"].alpha() * 0.5))
        grad_contour.setColorAt(0.0, c_bord_sombre)
        grad_contour.setColorAt(0.5, c_milieu)
        grad_contour.setColorAt(1.0, c_bord_sombre)
        pen_contour = QPen(QBrush(grad_contour), max(1.2, side * 0.012))
        painter.setPen(pen_contour)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(contour)

    def dessiner_col(self, painter: QPainter, m: dict, palette: dict) -> None:
        """Petit raffinement du bocal : un léger bourrelet à l'ouverture du
        col, pour suggérer l'épaisseur du verre plutôt qu'une simple
        tranche plate, avec un discret reflet dessus comme sur le reste
        du bocal."""
        col_x0 = m["cx"] - m["col_largeur"] / 2
        col_x1 = m["cx"] + m["col_largeur"] / 2
        haut_col = m["y0"]
        rim_h = max(2.0, (col_x1 - col_x0) * 0.16)
        rect_rim = QRectF(col_x0, haut_col - rim_h * 0.5, col_x1 - col_x0, rim_h)

        painter.save()
        pen = QPen(palette["piste"])
        pen.setWidthF(max(1.0, rim_h * 0.35))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect_rim, 0, 180 * 16)

        reflet = QColor("#FFFFFF")
        reflet.setAlphaF(0.35)
        pen_reflet = QPen(reflet)
        pen_reflet.setWidthF(max(0.8, rim_h * 0.22))
        pen_reflet.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_reflet)
        rect_reflet = rect_rim.adjusted(rim_h * 0.3, rim_h * 0.15, -rim_h * 0.3, 0)
        painter.drawArc(rect_reflet, 20 * 16, 140 * 16)
        painter.restore()

    def dessiner_reflet(
        self, painter: QPainter, m: dict, contour: QPainterPath
    ) -> None:
        painter.save()
        painter.setClipPath(contour)

        # --- halo diffus ---
        foyer = QPointF(
            m["x0"] + (m["x1"] - m["x0"]) * 0.28,
            m["corps_haut"] + (m["y1"] - m["corps_haut"]) * 0.18,
        )
        rayon = (m["x1"] - m["x0"]) * 1.1
        gradient = QRadialGradient(foyer, rayon)
        couleur_centre = QColor("#FFFFFF")
        couleur_centre.setAlphaF(0.10)
        couleur_bord = QColor("#FFFFFF")
        couleur_bord.setAlphaF(0.0)
        gradient.setColorAt(0.0, couleur_centre)
        gradient.setColorAt(1.0, couleur_bord)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(QRectF(m["x0"], m["y0"], m["x1"] - m["x0"], m["y1"] - m["y0"]))

        # --- reflet linéaire (bande verticale), typique du verre courbe ---
        largeur = m["x1"] - m["x0"]
        streak_x = m["x0"] + largeur * 0.24
        streak_w = largeur * 0.09
        streak_rect = QRectF(
            streak_x - streak_w / 2,
            m["corps_haut"],
            streak_w,
            (m["y1"] - m["corps_haut"]) * 0.82,
        )
        grad_streak = QLinearGradient(streak_rect.left(), 0, streak_rect.right(), 0)
        c_out = QColor("#FFFFFF")
        c_out.setAlphaF(0.0)
        c_in = QColor("#FFFFFF")
        c_in.setAlphaF(0.22)
        grad_streak.setColorAt(0.0, c_out)
        grad_streak.setColorAt(0.5, c_in)
        grad_streak.setColorAt(1.0, c_out)
        chemin_streak = QPainterPath()
        chemin_streak.addRoundedRect(streak_rect, streak_w / 2, streak_w / 2)
        painter.setBrush(QBrush(grad_streak))
        painter.drawPath(chemin_streak)

        painter.restore()
