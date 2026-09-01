################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.29 – Script de création de l'icône adresse email                         #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QFont,
    QLinearGradient,
    QRadialGradient,
    QPainterPath,
)

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_icone_email(painter: QPainter, centre: QPointF, taille: float) -> None:
    """Icône "adresse email" : enveloppe stylisée (corps + rabat replié en V)
    avec dégradé doux, ombre portée légère et reflet glossy, complétée d'un
    badge rond "@" en bas à droite pour préciser l'idée d'adresse (et pas
    juste de courrier). Même esprit que les autres icônes du projet."""

    COULEUR_CORPS = QColor("#6CD9F1")
    COULEUR_BADGE = QColor("#F58E3B")

    cx, cy = centre.x(), centre.y()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    largeur = taille * 0.86
    hauteur = taille * 0.60
    arrondi = taille * 0.07

    x0 = cx - largeur / 2
    y0 = cy - hauteur / 2
    x1 = cx + largeur / 2
    y1 = cy + hauteur / 2

    # -- Ombre douce sous l'enveloppe ------------------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    ombre = QRadialGradient(QPointF(cx, y1 + taille * 0.06), taille * 0.42)
    ombre.setColorAt(0.0, QColor(0, 0, 0, 45))
    ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.setBrush(QBrush(ombre))
    painter.drawEllipse(QPointF(cx, y1 + taille * 0.05), largeur * 0.42, taille * 0.05)

    # ============================================================
    # CORPS DE L'ENVELOPPE (rectangle arrondi)
    # ============================================================
    chemin_corps = QPainterPath()
    chemin_corps.addRoundedRect(QRectF(x0, y0, largeur, hauteur), arrondi, arrondi)

    degrade_corps = QLinearGradient(QPointF(x0, y0), QPointF(x0, y1))
    degrade_corps.setColorAt(0.0, COULEUR_CORPS.lighter(125))
    degrade_corps.setColorAt(1.0, COULEUR_CORPS.darker(110))

    pen_corps = QPen(COULEUR_CORPS.darker(140))
    pen_corps.setWidthF(taille * 0.008)
    pen_corps.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen_corps)
    painter.setBrush(QBrush(degrade_corps))
    painter.drawPath(chemin_corps)

    # ============================================================
    # RABAT (triangle replié, en V, légèrement plus clair)
    # ============================================================
    painter.save()
    painter.setClipPath(chemin_corps)

    chemin_rabat = QPainterPath()
    chemin_rabat.moveTo(x0, y0)
    chemin_rabat.lineTo(cx, cy + hauteur * 0.05)
    chemin_rabat.lineTo(x1, y0)
    chemin_rabat.lineTo(x1, y0 - taille * 0.02)
    chemin_rabat.lineTo(x0, y0 - taille * 0.02)
    chemin_rabat.closeSubpath()

    degrade_rabat = QLinearGradient(QPointF(x0, y0), QPointF(x1, cy))
    degrade_rabat.setColorAt(0.0, COULEUR_CORPS.lighter(145))
    degrade_rabat.setColorAt(0.5, COULEUR_CORPS.lighter(110))
    degrade_rabat.setColorAt(1.0, COULEUR_CORPS.lighter(145))

    pen_rabat = QPen(COULEUR_CORPS.darker(150))
    pen_rabat.setWidthF(taille * 0.007)
    pen_rabat.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen_rabat)
    painter.setBrush(QBrush(degrade_rabat))
    painter.drawPath(chemin_rabat)

    # -- Petite ombre portée du rabat sur le corps -----------------------------
    pen_ombre_rabat = QPen(QColor(0, 0, 0, 35))
    pen_ombre_rabat.setWidthF(taille * 0.012)
    pen_ombre_rabat.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_ombre_rabat)
    painter.drawLine(QPointF(x0, y0), QPointF(cx, cy + hauteur * 0.05))
    painter.drawLine(QPointF(x1, y0), QPointF(cx, cy + hauteur * 0.05))

    painter.restore()

    # -- Reflet glossy discret sur le corps -------------------------------------
    painter.setPen(Qt.PenStyle.NoPen)
    reflet = QColor(255, 255, 255, 55)
    painter.setBrush(QBrush(reflet))
    painter.drawEllipse(
        QPointF(x0 + largeur * 0.16, y1 - hauteur * 0.16),
        largeur * 0.10,
        hauteur * 0.07,
    )

    # ============================================================
    # BADGE "@" (bas droite), glossy comme le reste du set
    # ============================================================
    rayon_badge = taille * 0.22  # légèrement réduit pour mieux respirer
    marge_bord = taille * 0.04  # marge de sécurité par rapport au bord du canvas

    # Le centre est calculé pour que le bord EXTÉRIEUR du badge (ombre incluse,
    # d'où le facteur 1.15) ne dépasse jamais le bord du canvas de l'icône.
    centre_badge = QPointF(
        min(x1 - taille * 0.02, cx + taille * 0.5 - rayon_badge * 1.15 - marge_bord),
        y1 - taille * 0.02,
    )

    painter.setPen(Qt.PenStyle.NoPen)
    ombre_badge = QRadialGradient(centre_badge, rayon_badge * 1.3)
    ombre_badge.setColorAt(0.0, QColor(0, 0, 0, 50))
    ombre_badge.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.setBrush(QBrush(ombre_badge))
    painter.drawEllipse(centre_badge, rayon_badge * 1.15, rayon_badge * 1.15)

    degrade_badge = QRadialGradient(
        QPointF(
            centre_badge.x() - rayon_badge * 0.3, centre_badge.y() - rayon_badge * 0.35
        ),
        rayon_badge * 1.6,
    )
    degrade_badge.setColorAt(0.0, COULEUR_BADGE.lighter(150))
    degrade_badge.setColorAt(0.55, COULEUR_BADGE)
    degrade_badge.setColorAt(1.0, COULEUR_BADGE.darker(115))

    pen_badge = QPen(QColor("#FFFFFF"))
    pen_badge.setWidthF(taille * 0.015)
    painter.setPen(pen_badge)
    painter.setBrush(QBrush(degrade_badge))
    painter.drawEllipse(centre_badge, rayon_badge, rayon_badge)

    # -- Symbole "@" en blanc, centré dans le badge ------------------------------
    police = QFont("Arial")
    police.setBold(True)
    police.setPixelSize(int(rayon_badge * 1.3))
    painter.setFont(police)
    painter.setPen(QPen(QColor("#FFFFFF")))
    zone_texte = QRectF(
        centre_badge.x() - rayon_badge,
        centre_badge.y() - rayon_badge,
        rayon_badge * 2,
        rayon_badge * 2,
    )
    painter.drawText(zone_texte, Qt.AlignmentFlag.AlignCenter, "@")
