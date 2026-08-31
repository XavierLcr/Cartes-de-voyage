################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.25 – Script de création de l'icône de sauvegarde (disquette)             #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QRadialGradient,
    QLinearGradient,
    QPainterPath,
)

# 1 -- Fonction de création de l'icône -------------------------------------------


def _dessiner_icone_disquette(
    painter: QPainter, centre: QPointF, taille: float, validee: bool = False
) -> None:
    """Icône "sauvegarder" : disquette stylisée (corps + coin coupé, volet
    métallique, étiquette). Pas d'ombre portée. Si validee=True, ajoute un
    badge check vert en bas à droite pour signaler une sauvegarde réussie
    (remplace l'emoji 💾 ou 💾✅ selon le cas)."""

    COULEUR_CORPS = QColor("#4A5568")
    COULEUR_VOLET = QColor("#CBD3DC")
    COULEUR_LABEL = QColor("#F4F6F8")
    COULEUR_VALIDATION = QColor("#3DDC84")

    cx, cy = centre.x(), centre.y()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # -- Dimensions de base ---------------------------------------------
    taille_corps = taille * 0.90
    arrondi = taille * 0.06
    coin_coupe = taille * 0.16

    x0 = cx - taille_corps / 2
    y0 = cy - taille_corps / 2
    x1 = cx + taille_corps / 2
    y1 = cy + taille_corps / 2

    # ============================================================
    # CORPS DE LA DISQUETTE (carré arrondi, coin haut-droit coupé)
    # ============================================================
    chemin_corps = QPainterPath()
    chemin_corps.moveTo(x0 + arrondi, y0)
    chemin_corps.lineTo(x1 - coin_coupe, y0)
    chemin_corps.lineTo(x1, y0 + coin_coupe)
    chemin_corps.lineTo(x1, y1 - arrondi)
    chemin_corps.quadTo(x1, y1, x1 - arrondi, y1)
    chemin_corps.lineTo(x0 + arrondi, y1)
    chemin_corps.quadTo(x0, y1, x0, y1 - arrondi)
    chemin_corps.lineTo(x0, y0 + arrondi)
    chemin_corps.quadTo(x0, y0, x0 + arrondi, y0)
    chemin_corps.closeSubpath()

    degrade_corps = QLinearGradient(QPointF(x0, y0), QPointF(x1, y1))
    degrade_corps.setColorAt(0.0, COULEUR_CORPS.lighter(120))
    degrade_corps.setColorAt(1.0, COULEUR_CORPS.darker(110))

    pen_corps = QPen(COULEUR_CORPS.darker(135))
    pen_corps.setWidthF(taille * 0.005)
    pen_corps.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen_corps)
    painter.setBrush(QBrush(degrade_corps))
    painter.drawPath(chemin_corps)

    # ============================================================
    # VOLET MÉTALLIQUE (bande supérieure)
    # ============================================================
    largeur_volet = taille_corps * 0.60
    hauteur_volet = taille_corps * 0.28
    x_volet = cx - largeur_volet / 2
    y_volet = y0 + taille_corps * 0.07

    chemin_volet = QPainterPath()
    chemin_volet.addRoundedRect(
        x_volet, y_volet, largeur_volet, hauteur_volet, taille * 0.015, taille * 0.015
    )

    degrade_volet = QLinearGradient(
        QPointF(x_volet, y_volet), QPointF(x_volet, y_volet + hauteur_volet)
    )
    degrade_volet.setColorAt(0.0, COULEUR_VOLET.lighter(115))
    degrade_volet.setColorAt(1.0, COULEUR_VOLET.darker(110))

    pen_volet = QPen(COULEUR_VOLET.darker(140))
    pen_volet.setWidthF(taille * 0.003)
    painter.setPen(pen_volet)
    painter.setBrush(QBrush(degrade_volet))
    painter.drawPath(chemin_volet)

    # -- Encoche du volet (petit rectangle sombre, style protection écriture) --
    largeur_encoche = largeur_volet * 0.22
    hauteur_encoche = hauteur_volet * 0.55
    x_encoche = x_volet + largeur_volet * 0.62
    y_encoche = y_volet + (hauteur_volet - hauteur_encoche) / 2

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(COULEUR_CORPS.darker(120)))
    painter.drawRoundedRect(
        QRectF(x_encoche, y_encoche, largeur_encoche, hauteur_encoche),
        taille * 0.006,
        taille * 0.006,
    )

    # ============================================================
    # ÉTIQUETTE (rectangle clair, bas de la disquette)
    # ============================================================
    largeur_label = taille_corps * 0.70
    hauteur_label = taille_corps * 0.32
    x_label = cx - largeur_label / 2
    y_label = y_volet + hauteur_volet + taille_corps * 0.08

    chemin_label = QPainterPath()
    chemin_label.addRoundedRect(
        x_label, y_label, largeur_label, hauteur_label, taille * 0.012, taille * 0.012
    )

    degrade_label = QLinearGradient(
        QPointF(x_label, y_label), QPointF(x_label, y_label + hauteur_label)
    )
    degrade_label.setColorAt(0.0, COULEUR_LABEL)
    degrade_label.setColorAt(1.0, COULEUR_LABEL.darker(104))

    pen_label = QPen(COULEUR_CORPS.lighter(60))
    pen_label.setWidthF(taille * 0.003)
    painter.setPen(pen_label)
    painter.setBrush(QBrush(degrade_label))
    painter.drawPath(chemin_label)

    # -- Petites lignes de texte sur l'étiquette (détail discret) -----------
    pen_ligne = QPen(COULEUR_CORPS.lighter(40))
    pen_ligne.setWidthF(taille * 0.012)
    pen_ligne.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_ligne)
    for i, frac in enumerate([0.30, 0.55, 0.80]):
        y_l = y_label + hauteur_label * frac
        longueur = largeur_label * (0.7 if i < 2 else 0.45)
        painter.drawLine(
            QPointF(x_label + largeur_label * 0.15, y_l),
            QPointF(x_label + largeur_label * 0.15 + longueur, y_l),
        )

    # -- Reflet glossy discret sur le corps ----------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    reflet = QColor(255, 255, 255, 45)
    painter.setBrush(QBrush(reflet))
    painter.drawEllipse(
        QPointF(x0 + taille_corps * 0.20, y0 + taille_corps * 0.20),
        taille_corps * 0.10,
        taille_corps * 0.06,
    )

    # ============================================================
    # BADGE DE VALIDATION (optionnel) : check vert bas-droite
    # ============================================================
    if validee:
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
