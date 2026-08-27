################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_2                                #
# Onglet 4.2.4 – Widget de titre d'un classement                               #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QFont,
    QLinearGradient,
    QPainterPath,
    QBrush,
    QPen,
    QRadialGradient,
    QConicalGradient,
)
from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    _trouver_police_disponible,
    _QColor_avec_transparence,
)

# 1 -- Classe de création du titre ---------------------------------------------


class TitreClassement(QWidget):
    """
    Carte titre pour les sections de classement du tableau de bord.

    Reprend le vocabulaire visuel de `CarteClassementPays` : carte à
    coins arrondis, ombre douce, même police "joyeuse" que le podium
    (avec repli automatique). Le badge est un médaillon vectoriel en
    forme de boussole (anneau gradué + aiguille bicolore) dans les
    couleurs du thème, avec un dégradé de fond volontairement adouci
    par transparence.
    """

    def __init__(self, titre, sous_titre="", style=None, parent=None):
        super().__init__(parent)

        self.titre = titre
        self.sous_titre = sous_titre
        self.theme = style

        # Même police que le podium / les cartes de classement.
        self.police_principale = _trouver_police_disponible(
            [
                "Segoe UI",
                "Fredoka",
                "Quicksand",
                "Century Gothic",
            ]
        )

        self.setMinimumHeight(92)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.ombre = QGraphicsDropShadowEffect(self)
        self.ombre.setBlurRadius(26)
        self.ombre.setOffset(0, 7)
        self.ombre.setColor(self.theme.ombre)
        self.setGraphicsEffect(self.ombre)

    @staticmethod
    def _point_polaire(centre: QPointF, rayon: float, angle_rad: float) -> QPointF:
        import math

        return QPointF(
            centre.x() + rayon * math.cos(angle_rad),
            centre.y() + rayon * math.sin(angle_rad),
        )

    def paintEvent(self, event):
        import math

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()
        rect = QRectF(2, 2, w - 4, h - 4)
        rayon_carte = min(22, h * 0.25)

        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(rect, rayon_carte, rayon_carte)

        # --- 1) aplat de base : le fond "carte" du thème, opaque ---
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.theme.fond))
        painter.drawPath(chemin_carte)

        # --- 2) dégradé diagonal, mais adouci : on pose les couleurs du
        # badge en semi-transparence sur l'aplat plutôt qu'en pleine
        # opacité, pour un rendu plus feutré. ---
        painter.save()
        painter.setClipPath(chemin_carte)

        degrade = QLinearGradient(rect.topLeft(), rect.bottomRight())
        degrade.setColorAt(0, _QColor_avec_transparence(self.theme.badge_debut, 150))
        degrade.setColorAt(1, _QColor_avec_transparence(self.theme.badge_fin, 150))
        painter.setBrush(QBrush(degrade))
        painter.drawRect(rect)

        # --- 3) reflet "verre" en haut de carte : léger voile blanc qui
        # s'estompe vers le bas, pour donner du volume sans durcir la
        # teinte. ---
        reflet = QLinearGradient(
            rect.topLeft(), QPointF(rect.left(), rect.top() + h * 0.7)
        )
        reflet.setColorAt(0, QColor(255, 255, 255, 40))
        reflet.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(reflet))
        painter.drawRect(rect)

        painter.restore()

        # --- 4) liseré fin qui détache la carte du fond général ---
        painter.setPen(QPen(QColor(255, 255, 255, 45), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(chemin_carte)

        # --- médaillon (badge de rang, en forme de boussole) ---
        rayon_badge = h * 0.27
        centre = QPointF(w * 0.15, h * 0.5)

        # ombre portée propre au médaillon (distincte de l'ombre du
        # widget), pour le détacher nettement du dégradé de fond
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 40))
        painter.drawEllipse(
            QPointF(centre.x() + 1.2, centre.y() + 2.4),
            rayon_badge * 1.02,
            rayon_badge * 1.02,
        )

        # lunette extérieure "métal brossé" : dégradé conique qui fait
        # tourner la lumière autour de l'anneau (badge_fin -> blanc ->
        # badge_debut -> blanc), au lieu d'un anneau à couleur plate
        degrade_lunette = QConicalGradient(centre, 90)
        teinte_fin = _QColor_avec_transparence(self.theme.badge_fin, 235)
        teinte_debut = _QColor_avec_transparence(self.theme.badge_debut, 235)
        reflet_clair = QColor(255, 255, 255, 225)
        degrade_lunette.setColorAt(0.00, teinte_fin)
        degrade_lunette.setColorAt(0.22, reflet_clair)
        degrade_lunette.setColorAt(0.50, teinte_debut)
        degrade_lunette.setColorAt(0.78, reflet_clair)
        degrade_lunette.setColorAt(1.00, teinte_fin)
        painter.setBrush(QBrush(degrade_lunette))
        painter.drawEllipse(centre, rayon_badge, rayon_badge)

        # cadran intérieur, légèrement décentré pour un dégradé radial
        # asymétrique (source de lumière en haut-gauche) — plus vivant
        # qu'un dégradé parfaitement concentrique
        rayon_cadran = rayon_badge * 0.8
        foyer = QPointF(
            centre.x() - rayon_cadran * 0.3, centre.y() - rayon_cadran * 0.3
        )
        degrade_cadran = QRadialGradient(centre, rayon_cadran * 1.15, foyer)
        degrade_cadran.setColorAt(0.0, QColor(255, 255, 255, 250))
        degrade_cadran.setColorAt(0.75, QColor(255, 255, 255, 228))
        degrade_cadran.setColorAt(1.0, QColor(240, 242, 248, 205))
        painter.setBrush(QBrush(degrade_cadran))
        painter.drawEllipse(centre, rayon_cadran, rayon_cadran)

        # ombre interne au bord du cadran : dégradé radial du transparent
        # vers un léger noir, pour suggérer un rebord creusé sans tracer
        # de trait dur
        degrade_rebord = QRadialGradient(centre, rayon_cadran)
        degrade_rebord.setColorAt(0.82, QColor(0, 0, 0, 0))
        degrade_rebord.setColorAt(1.0, QColor(0, 0, 0, 38))
        painter.setBrush(QBrush(degrade_rebord))
        painter.drawEllipse(centre, rayon_cadran, rayon_cadran)

        # repère nord : fin triangle "gravé" (ombre + lumière superposées,
        # légèrement décalées) plutôt qu'un point ou un trait plat
        pointe_repere = self._point_polaire(centre, rayon_cadran * 0.9, -math.pi / 2)
        base_repere_g = self._point_polaire(
            centre, rayon_cadran * 0.74, -math.pi / 2 - math.radians(5)
        )
        base_repere_d = self._point_polaire(
            centre, rayon_cadran * 0.74, -math.pi / 2 + math.radians(5)
        )

        chemin_repere = QPainterPath()
        chemin_repere.moveTo(pointe_repere)
        chemin_repere.lineTo(base_repere_g)
        chemin_repere.lineTo(base_repere_d)
        chemin_repere.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 20))
        painter.drawPath(chemin_repere.translated(0, 0.6))
        painter.setBrush(_QColor_avec_transparence(self.theme.badge_fin, 150))
        painter.drawPath(chemin_repere.translated(0, -0.3))

        # aiguille bicolore, légèrement inclinée pour du dynamisme
        angle_aiguille = -math.pi / 2 - math.radians(16)
        angle_oppose = angle_aiguille + math.pi
        longueur_nord = rayon_cadran * 0.75
        longueur_sud = rayon_cadran * 0.5
        largeur_base = rayon_cadran * 0.075

        pointe_nord = self._point_polaire(centre, longueur_nord, angle_aiguille)
        pointe_sud = self._point_polaire(centre, longueur_sud, angle_oppose)
        base_gauche = self._point_polaire(
            centre, largeur_base, angle_aiguille + math.pi / 2
        )
        base_droite = self._point_polaire(
            centre, largeur_base, angle_aiguille - math.pi / 2
        )

        # ombre portée de l'aiguille sur le cadran
        painter.setPen(Qt.PenStyle.NoPen)
        aiguille_ombre = QPainterPath()
        aiguille_ombre.moveTo(pointe_nord + QPointF(0.8, 1.0))
        aiguille_ombre.lineTo(base_gauche + QPointF(0.8, 1.0))
        aiguille_ombre.lineTo(pointe_sud + QPointF(0.8, 1.0))
        aiguille_ombre.lineTo(base_droite + QPointF(0.8, 1.0))
        aiguille_ombre.closeSubpath()
        painter.setBrush(QColor(0, 0, 0, 28))
        painter.drawPath(aiguille_ombre)

        # moitié nord : dégradé (pas une couleur plate) pour un effet de
        # matière, du centre vers la pointe, plus un fin liseré sombre
        moitie_nord = QPainterPath()
        moitie_nord.moveTo(pointe_nord)
        moitie_nord.lineTo(base_gauche)
        moitie_nord.lineTo(centre)
        moitie_nord.lineTo(base_droite)
        moitie_nord.closeSubpath()

        degrade_nord = QLinearGradient(centre, pointe_nord)
        degrade_nord.setColorAt(
            0.0, _QColor_avec_transparence(self.theme.badge_fin, 255)
        )
        degrade_nord.setColorAt(
            1.0, _QColor_avec_transparence(self.theme.badge_fin, 195)
        )
        painter.setBrush(QBrush(degrade_nord))
        painter.drawPath(moitie_nord)
        painter.setPen(QPen(QColor(0, 0, 0, 35), 0.6))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(moitie_nord)

        # moitié sud : même logique, teinte claire, plus atténuée à la pointe
        moitie_sud = QPainterPath()
        moitie_sud.moveTo(pointe_sud)
        moitie_sud.lineTo(base_gauche)
        moitie_sud.lineTo(centre)
        moitie_sud.lineTo(base_droite)
        moitie_sud.closeSubpath()

        degrade_sud = QLinearGradient(centre, pointe_sud)
        degrade_sud.setColorAt(
            0.0, _QColor_avec_transparence(self.theme.badge_debut, 245)
        )
        degrade_sud.setColorAt(
            1.0, _QColor_avec_transparence(self.theme.badge_debut, 150)
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(degrade_sud))
        painter.drawPath(moitie_sud)

        # pivot central façon petite pierre sertie : disque à dégradé
        # radial + minuscule reflet spéculaire décalé, pour un effet
        # de brillance plutôt qu'un rond plat
        rayon_pivot = rayon_badge * 0.1
        degrade_pivot = QRadialGradient(
            QPointF(centre.x() - rayon_pivot * 0.3, centre.y() - rayon_pivot * 0.3),
            rayon_pivot * 1.4,
        )
        degrade_pivot.setColorAt(0.0, QColor(255, 255, 255, 255))
        degrade_pivot.setColorAt(
            0.4, _QColor_avec_transparence(self.theme.badge_fin, 255)
        )
        degrade_pivot.setColorAt(
            1.0, _QColor_avec_transparence(self.theme.badge_fin, 220)
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(degrade_pivot))
        painter.drawEllipse(centre, rayon_pivot, rayon_pivot)

        painter.setBrush(QColor(255, 255, 255, 210))
        painter.drawEllipse(
            QPointF(centre.x() - rayon_pivot * 0.32, centre.y() - rayon_pivot * 0.32),
            rayon_pivot * 0.3,
            rayon_pivot * 0.3,
        )

        # --- zone de texte (titre + sous-titre), centrée verticalement ---
        marge_apres_badge = rayon_badge * 0.85
        x_texte = centre.x() + rayon_badge + marge_apres_badge
        zone_texte = QRectF(x_texte, 0, w - x_texte - w * 0.04, h)

        police_titre = QFont(
            self.police_principale, max(10, int(h * 0.13)), QFont.Weight.DemiBold
        )
        police_titre.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 101)
        painter.setFont(police_titre)
        metrics_titre = painter.fontMetrics()
        titre_affiche = metrics_titre.elidedText(
            self.titre, Qt.TextElideMode.ElideRight, int(zone_texte.width())
        )

        police_sous_titre = QFont(self.police_principale, max(7, int(h * 0.1)))
        police_sous_titre.setItalic(True)
        hauteur_sous_titre = 0
        if self.sous_titre:
            painter.setFont(police_sous_titre)
            hauteur_sous_titre = painter.fontMetrics().height()

        hauteur_titre = metrics_titre.height()
        espace = 3 if self.sous_titre else 0
        hauteur_bloc = hauteur_titre + espace + hauteur_sous_titre
        y_depart = zone_texte.y() + max(0.0, (h - hauteur_bloc) / 2)

        painter.setFont(police_titre)
        painter.setPen(self.theme.texte)
        painter.drawText(
            QRectF(zone_texte.x(), y_depart, zone_texte.width(), hauteur_titre),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            titre_affiche,
        )

        if self.sous_titre:
            painter.setFont(police_sous_titre)
            painter.setPen(self.theme.sous_texte)
            sous_titre_affiche = painter.fontMetrics().elidedText(
                self.sous_titre, Qt.TextElideMode.ElideRight, int(zone_texte.width())
            )
            painter.drawText(
                QRectF(
                    zone_texte.x(),
                    y_depart + hauteur_titre + espace,
                    zone_texte.width(),
                    hauteur_sous_titre,
                ),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                sous_titre_affiche,
            )
