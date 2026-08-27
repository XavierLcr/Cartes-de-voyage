################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_2                                #
# Onglet 4.2.2 – Widget du poduim pour le top 3 pays                           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer, QSize
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QFont,
    QLinearGradient,
    QRadialGradient,
    QPainterPath,
    QPen,
    QBrush,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    _trouver_police_disponible,
    _QColor_avec_alpha,
)

# 1 -- Classe du podium --------------------------------------------------------


class Podium(QWidget):
    """
    Podium des 3 pays les plus visités (par % de superficie).

    Style flat, dans le même esprit que les cartes du tableau de bord
    (onglet 4.6) : carte à coins arrondis, ombre douce, colonnes en
    dégradé plat à coins arrondis (comme les mini-graphiques en barres),
    badge circulaire numéroté, typographie plus joyeuse (avec repli
    automatique si la police n'est pas installée).

    Petites touches visuelles ajoutées, pour rester cohérent avec les
    cartes de classement voisines (rang 4+) :
    - liseré fin autour de la carte, pour la détacher du fond
    - reflet glacé en haut de la carte (en plus de celui, déjà présent,
      sur chaque colonne)
    - ligne de base légèrement soulignée sous les colonnes, comme un
      "sol" sur lequel repose le podium
    """

    # Dégradés "médaille" (début -> fin), plats, sans relief ni reflet —
    # même logique que les dégradés de badge utilisés ailleurs dans le
    # tableau de bord.
    COULEURS = {
        1: (QColor("#FBBF24"), QColor("#F59E0B")),  # or
        2: (QColor("#CBD5E1"), QColor("#94A3B8")),  # argent
        3: (QColor("#F0B27A"), QColor("#C2703D")),  # bronze
    }

    def __init__(self):
        super().__init__()
        self.setMinimumSize(220, 100)
        self._donnees = []
        self._anim_progress = 0.0  # 0 -> 1, pour l'animation de montée
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._anim_step)

        # Couleurs de la carte (fond / texte), dans la même convention
        # que les widgets du tableau de bord.
        self.couleur_fond = QColor("#fcfcfc")
        self.couleur_texte = QColor("#1c1f2b")
        self.couleur_sous_texte = QColor("#1c1f2b")
        self.couleur_sous_texte.setAlpha(140)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(30)
        self._ombre_effet.setOffset(0, 8)
        self._ombre_effet.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(self._ombre_effet)

        # Police un peu plus joyeuse que Segoe UI, avec repli automatique
        # sur une police sûre si aucune de la liste n'est installée.
        self.police_principale = _trouver_police_disponible(
            [
                "Baloo 2",
                "Fredoka",
                "Quicksand",
                "Century Gothic",
                "Comic Sans MS",
                "Segoe UI",
            ]
        )

    # ========= API PUBLIQUE =========

    def set_donnees(self, donnees):
        """
        donnees : liste de dicts {"nom_pays": str, "pct_superficie_pays": float, "pct_superficie_pays_label":str}
        Seuls les 3 premiers (triés par score décroissant) sont affichés.
        """
        self._donnees = sorted(
            donnees, key=lambda d: d["pct_superficie_pays"], reverse=True
        )[:3]
        self._anim_progress = 0.0
        self._timer.start(15)
        self.update()

    def _anim_step(self):
        self._anim_progress += 0.045
        if self._anim_progress >= 1.0:
            self._anim_progress = 1.0
            self._timer.stop()
        self.update()

    @staticmethod
    def _ease_out_back(t):
        c1 = 1.70158
        c3 = c1 + 1
        t = max(0.0, min(1.0, t))
        return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

    # ========= PAINT =========

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()

        self._dessiner_fond(painter, w, h)

        if not self._donnees:
            painter.setPen(self.couleur_sous_texte)
            font = QFont(self.police_principale, 11)
            painter.setFont(font)
            painter.drawText(
                QRectF(0, 0, w, h),
                Qt.AlignmentFlag.AlignCenter,
                "Aucun classement à afficher",
            )
            return

        # =========================================================
        # Disposition : 2e - 1er - 3e (ordre visuel classique)
        # =========================================================
        ordre_affichage = []
        if len(self._donnees) >= 2:
            ordre_affichage.append((2, self._donnees[1]))
        ordre_affichage.append((1, self._donnees[0]))
        if len(self._donnees) >= 3:
            ordre_affichage.append((3, self._donnees[2]))

        nb_marches = len(ordre_affichage)
        marge_h = w * 0.06
        largeur_dispo = w - 2 * marge_h
        largeur_marche = largeur_dispo / nb_marches
        largeur_bloc = largeur_marche * 0.72

        hauteur_relative = {1: 0.7, 2: 0.5, 3: 0.36}
        zone_texte_haut = h * 0.35  # était 0.22 — un peu plus de marge en haut
        base_y = h * 0.88

        # ligne de "sol" discrète sous les colonnes
        self._dessiner_ligne_base(painter, marge_h, w - marge_h, base_y)

        for i, (rang, pays) in enumerate(ordre_affichage):
            x = marge_h + i * largeur_marche + (largeur_marche - largeur_bloc) / 2

            hauteur_max = (h - zone_texte_haut - (h - base_y)) * hauteur_relative[rang]
            hauteur_marche = hauteur_max * self._ease_out_back(self._anim_progress)
            hauteur_marche = max(hauteur_marche, 2)

            y = base_y - hauteur_marche

            couleur_debut, couleur_fin = self.COULEURS[rang]

            self._dessiner_colonne(
                painter, x, y, largeur_bloc, hauteur_marche, couleur_debut, couleur_fin
            )

            if self._anim_progress > 0.55:
                alpha = min(1.0, (self._anim_progress - 0.55) / 0.45)
                self._dessiner_valeur(
                    painter,
                    x,
                    y,
                    largeur_bloc,
                    hauteur_marche,
                    pays["pct_superficie_pays_label"],
                    alpha,
                )

            if self._anim_progress > 0.7:
                alpha = min(1.0, (self._anim_progress - 0.7) / 0.3)
                zone_texte_y = y - zone_texte_haut

                cx = x + largeur_bloc / 2
                cy = zone_texte_y + zone_texte_haut * 0.30
                rayon_badge = zone_texte_haut * 0.16

                self._dessiner_anneau_progression(
                    painter,
                    cx,
                    cy,
                    rayon_badge,
                    pays["pct_superficie_pays"],
                    couleur_debut,
                    couleur_fin,
                    alpha,
                )

                self._dessiner_badge_rang(
                    painter,
                    x + largeur_bloc / 2,
                    zone_texte_y
                    + zone_texte_haut
                    * 0.30,  # était 0.20 — badge un peu plus bas dans SA zone
                    zone_texte_haut * 0.16,  # était 0.18 — badge légèrement plus petit
                    rang,
                    couleur_debut,
                    couleur_fin,
                    alpha,
                )

                self._dessiner_nom_pays(
                    painter, x, zone_texte_y, largeur_bloc, zone_texte_haut, pays, alpha
                )

    # ========= COMPOSANTS DE DESSIN =========

    def _dessiner_fond(self, painter, w, h):
        """Carte à coins arrondis, fond plat, avec un liseré fin et un
        reflet glacé en haut — même vocabulaire visuel que les cartes de
        classement (rang 4+) voisines."""
        rayon = min(24, min(w, h) * 0.12)
        chemin = QPainterPath()
        chemin.addRoundedRect(QRectF(0, 0, w, h), rayon, rayon)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.couleur_fond)
        painter.drawPath(chemin)

        # liseré fin, dans la teinte "or" du 1er badge, très transparent
        pen_contour = QPen(_QColor_avec_alpha(self.COULEURS[1][0], 55))
        pen_contour.setWidthF(1.1)
        painter.setPen(pen_contour)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(chemin)

        painter.setClipPath(chemin)

        # reflet glacé, discret, sur le tiers supérieur de la carte
        degrade_reflet = QLinearGradient(0, 0, 0, h * 0.45)
        degrade_reflet.setColorAt(0.0, _QColor_avec_alpha(QColor("#FFFFFF"), 35))
        degrade_reflet.setColorAt(1.0, _QColor_avec_alpha(QColor("#FFFFFF"), 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade_reflet)
        painter.drawRect(QRectF(0, 0, w, h * 0.45))

    def _dessiner_ligne_base(self, painter, x_gauche, x_droite, y):
        """Ligne fine sous les colonnes, façon socle du podium."""
        pen_base = QPen(_QColor_avec_alpha(self.couleur_sous_texte, 90))
        pen_base.setWidthF(1.2)
        painter.setPen(pen_base)
        painter.drawLine(QPointF(x_gauche, y), QPointF(x_droite, y))

    def _dessiner_colonne(
        self, painter, x, y, largeur, hauteur, couleur_debut, couleur_fin
    ):
        """Colonne à coins arrondis avec un dégradé à 3 arrêts (un peu de
        relief) et un léger reflet en haut — un entre-deux entre le plat
        pur et le bloc 3D isométrique d'origine."""
        rect_colonne = QRectF(x, y, largeur, hauteur)
        rayon = min(largeur * 0.22, hauteur * 0.22, 14)
        chemin = QPainterPath()
        chemin.addRoundedRect(rect_colonne, rayon, rayon)

        degrade = QLinearGradient(rect_colonne.topLeft(), rect_colonne.bottomLeft())
        degrade.setColorAt(0.0, couleur_debut.lighter(114))
        degrade.setColorAt(0.55, couleur_debut)
        degrade.setColorAt(1.0, couleur_fin.darker(112))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade)
        painter.drawPath(chemin)

        # reflet doux en haut de la colonne (touche de profondeur, sans
        # reflet diagonal "verre" comme dans la version 3D d'origine)
        painter.save()
        painter.setClipPath(chemin, Qt.ClipOperation.IntersectClip)
        rect_reflet = QRectF(
            rect_colonne.x(),
            rect_colonne.y(),
            rect_colonne.width(),
            rect_colonne.height() * 0.4,
        )
        degrade_reflet = QLinearGradient(
            rect_reflet.topLeft(), rect_reflet.bottomLeft()
        )
        degrade_reflet.setColorAt(0.0, QColor(255, 255, 255, 75))
        degrade_reflet.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade_reflet)
        painter.drawRect(rect_reflet)
        painter.restore()

        # fin liseré clair sur le contour de la colonne, pour la détacher
        # légèrement du fond de carte (cohérent avec le liseré de la carte)
        painter.save()
        pen_contour_colonne = QPen(_QColor_avec_alpha(QColor("#FFFFFF"), 90))
        pen_contour_colonne.setWidthF(1.0)
        painter.setPen(pen_contour_colonne)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(chemin)
        painter.restore()

    def _dessiner_valeur(self, painter, x, y, largeur, hauteur, texte, alpha):
        """Pourcentage affiché dans la colonne, en texte plat (pas de
        gravure/ombre décorative)."""
        painter.save()
        painter.setOpacity(alpha)

        font_valeur = QFont(
            self.police_principale, max(9, int(hauteur * 0.13 + 4)), QFont.Weight.Bold
        )
        painter.setFont(font_valeur)

        rect_valeur = QRectF(x, y + hauteur * 0.42, largeur, hauteur * 0.5)
        painter.setPen(self.couleur_texte)
        painter.drawText(rect_valeur, Qt.AlignmentFlag.AlignCenter, str(texte))
        painter.restore()

    def _dessiner_badge_rang(
        self, painter, cx, cy, rayon, rang, couleur_debut, couleur_fin, alpha
    ):
        """Badge circulaire numéroté, avec un peu de relief (ombre douce,
        liseré blanc, petit reflet) — remplace la couronne."""
        painter.save()
        painter.setOpacity(alpha)

        # ombre douce sous le badge
        rect_ombre = QRectF(
            cx - rayon * 1.15, cy - rayon * 0.9, rayon * 2.3, rayon * 2.3
        )
        degrade_ombre = QRadialGradient(QPointF(cx, cy + rayon * 0.3), rayon * 1.2)
        degrade_ombre.setColorAt(0.0, QColor(0, 0, 0, 55))
        degrade_ombre.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade_ombre)
        painter.drawEllipse(rect_ombre)

        rect_badge = QRectF(cx - rayon, cy - rayon, rayon * 2, rayon * 2)
        degrade = QLinearGradient(rect_badge.topLeft(), rect_badge.bottomRight())
        degrade.setColorAt(0.0, couleur_debut.lighter(110))
        degrade.setColorAt(1.0, couleur_fin)
        painter.setBrush(degrade)
        painter.drawEllipse(rect_badge)

        # liseré blanc fin
        pen_contour = QPen(QColor(255, 255, 255, 200))
        pen_contour.setWidthF(max(1.0, rayon * 0.09))
        painter.setPen(pen_contour)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect_badge)

        # petit reflet, coin haut-gauche
        rect_reflet = QRectF(
            cx - rayon * 0.55, cy - rayon * 0.75, rayon * 0.9, rayon * 0.6
        )
        degrade_reflet = QRadialGradient(rect_reflet.center(), rayon * 0.5)
        degrade_reflet.setColorAt(0.0, QColor(255, 255, 255, 110))
        degrade_reflet.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade_reflet)
        painter.drawEllipse(rect_reflet)

        font_rang = QFont(
            self.police_principale, max(7, int(rayon * 0.9)), QFont.Weight.Bold
        )
        painter.setFont(font_rang)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(rect_badge, Qt.AlignmentFlag.AlignCenter, str(rang))

        painter.restore()

    def _dessiner_nom_pays(
        self, painter, x, y_zone, largeur, hauteur_zone, pays, alpha
    ):
        painter.save()
        painter.setOpacity(alpha)

        zone_nom = QRectF(
            x - largeur * 0.15,
            y_zone + hauteur_zone * 0.52,
            largeur * 1.3,
            hauteur_zone * 0.5,
        )

        font_nom = QFont(self.police_principale, 10, QFont.Weight.DemiBold)
        painter.setFont(font_nom)
        painter.setPen(self.couleur_texte)

        self._dessiner_texte_wrap(painter, zone_nom, str(pays["nom_pays"]))

        painter.restore()

    def _dessiner_texte_wrap(self, painter, rect, texte):
        """
        Découpe `texte` en lignes qui tiennent dans la largeur de `rect`
        (calcul en pixels réels via QFontMetrics, pas en nb de caractères).
        Si le texte tient sur plusieurs lignes, le rectangle est agrandi
        verticalement (en restant centré sur la même zone) pour tout
        afficher sans jamais changer la taille de police.
        """
        metrics = painter.fontMetrics()
        largeur_max = rect.width() - 0.2

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

        hauteur_ligne = metrics.height()
        hauteur_totale = hauteur_ligne * len(lignes)

        # Agrandit le rect uniquement vers le HAUT si nécessaire,
        # pour ne pas empiéter sur le podium en dessous
        if hauteur_totale > rect.height():
            surplus = hauteur_totale - rect.height()
            rect = QRectF(
                rect.x(),
                rect.y() - surplus,
                rect.width(),
                hauteur_totale,
            )

        y_depart = rect.y() + (rect.height() - hauteur_totale) / 2
        for i, ligne in enumerate(lignes):
            rect_ligne = QRectF(
                rect.x(), y_depart + i * hauteur_ligne, rect.width(), hauteur_ligne
            )
            painter.drawText(rect_ligne, Qt.AlignmentFlag.AlignCenter, ligne)

    def sizeHint(self):
        return QSize(420, 300)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        ratio = 300 / 420
        return int(width * ratio)

    def set_style(self, style_parent):

        self.couleur_fond = style_parent.fond
        self.couleur_texte = style_parent.texte
        self.couleur_sous_texte = style_parent.texte
        self.couleur_sous_texte.setAlpha(140)

    def _dessiner_anneau_progression(
        self,
        painter,
        cx,
        cy,
        rayon_badge,
        valeur_pct,
        couleur_debut,
        couleur_fin,
        alpha,
    ):
        """Anneau de progression circulaire autour du badge de rang,
        représentant le pourcentage de superficie visitée, avec une
        poignée (point) marquant la valeur exacte en bout d'arc."""
        painter.save()
        painter.setOpacity(alpha)

        rayon_anneau = rayon_badge * 1.55
        epaisseur = max(2.0, rayon_badge * 0.16)
        rect_anneau = QRectF(
            cx - rayon_anneau, cy - rayon_anneau, rayon_anneau * 2, rayon_anneau * 2
        )

        # piste de fond
        pen_fond = QPen(_QColor_avec_alpha(QColor("#FFFFFF"), 130))
        pen_fond.setWidthF(epaisseur)
        pen_fond.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_fond)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect_anneau, 0, 360 * 16)

        # arc de progression
        valeur = max(0.0, min(100.0, valeur_pct))
        angle_deg = 360 * (valeur / 100.0)
        angle_parcouru = int(16 * angle_deg)
        if angle_parcouru > 0:
            degrade_arc = QLinearGradient(
                rect_anneau.topLeft(), rect_anneau.bottomRight()
            )
            degrade_arc.setColorAt(0.0, couleur_debut.lighter(125))
            degrade_arc.setColorAt(1.0, couleur_fin.lighter(115))
            pen_arc = QPen(QBrush(degrade_arc), epaisseur)
            pen_arc.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_arc)
            painter.drawArc(rect_anneau, 90 * 16, -angle_parcouru)

            # --- poignée : petit point plein au bout de l'arc ---
            import math

            angle_rad = math.radians(
                90 - angle_deg
            )  # même convention que Qt (0° = 3h, sens anti-horaire)
            px = cx + rayon_anneau * math.cos(angle_rad)
            py = cy - rayon_anneau * math.sin(angle_rad)

            rayon_poignee = epaisseur * 0.62

            # petite ombre douce sous la poignée
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(_QColor_avec_alpha(QColor("#000000"), 45))
            painter.drawEllipse(
                QPointF(px, py + rayon_poignee * 0.15), rayon_poignee, rayon_poignee
            )

            # poignée blanche avec liseré de la couleur de fin du dégradé
            painter.setBrush(QColor("#FFFFFF"))
            painter.drawEllipse(QPointF(px, py), rayon_poignee, rayon_poignee)

            pen_liseré = QPen(couleur_fin.lighter(110))
            pen_liseré.setWidthF(max(1.0, rayon_poignee * 0.35))
            painter.setPen(pen_liseré)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(
                QPointF(px, py), rayon_poignee * 0.75, rayon_poignee * 0.75
            )

        painter.restore()
