################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_2                                #
# Onglet 4.2.1 – Partie classement des pays visités                            #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer, QSize
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QFont,
    QLinearGradient,
    QRadialGradient,
    QPainterPath,
    QPen,
    QPolygonF,
    QFontInfo,
)

# 1 -- Classe du podium --------------------------------------------------------


class Podium(QWidget):

    # (couleur claire, couleur sombre, couleur du liseré)
    COULEURS = {
        # Or
        1: (QColor(255, 224, 102), QColor(198, 150, 20), QColor(255, 245, 200)),
        # Argent
        2: (
            QColor(220, 220, 225),
            QColor(150, 150, 158),
            QColor(245, 245, 248),
        ),
        # Bronze
        3: (
            QColor(224, 155, 100),
            QColor(160, 95, 45),
            QColor(250, 210, 175),
        ),
    }

    MEDAILLE = {
        1: QColor(255, 205, 60),
        2: QColor(205, 205, 210),
        3: QColor(210, 140, 80),
    }

    def __init__(self):
        super().__init__()
        self.setMinimumSize(220, 100)
        # self.setMaximumWidth(500)
        self._donnees = []
        self._anim_progress = 0.0  # 0 -> 1, pour l'animation de montée
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._anim_step)

    # ========= API PUBLIQUE =========

    def set_donnees(self, donnees):
        """
        donnees : liste de dicts {"nom_pays": str, "pct_superficie_dans_pays": float, "pct_superficie_dans_pays_label":str}
        Seuls les 3 premiers (triés par score décroissant) sont affichés.
        """
        self._donnees = sorted(
            donnees, key=lambda d: d["pct_superficie_dans_pays"], reverse=True
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
            painter.setPen(QColor(150, 150, 150))
            font = QFont()
            font.setPointSize(12)
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
        zone_texte_haut = h * 0.20
        base_y = h * 0.90
        profondeur_3d = largeur_marche * 0.16  # profondeur du bloc 3D

        for i, (rang, pays) in enumerate(ordre_affichage):
            x = marge_h + i * largeur_marche + (largeur_marche - largeur_bloc) / 2

            hauteur_max = (
                (base_y - zone_texte_haut)
                * hauteur_relative[rang]
                / max(hauteur_relative.values())
            )
            hauteur_max = (h - zone_texte_haut - (h - base_y)) * hauteur_relative[rang]
            hauteur_marche = hauteur_max * self._ease_out_back(self._anim_progress)
            hauteur_marche = max(hauteur_marche, 2)

            y = base_y - hauteur_marche

            couleur_claire, couleur_sombre, couleur_lisere = self.COULEURS[rang]

            self._dessiner_ombre_portee(
                painter, x, base_y, largeur_bloc, hauteur_marche + 4
            )
            self._dessiner_marche_3d(
                painter,
                x,
                y,
                largeur_bloc,
                hauteur_marche,
                profondeur_3d,
                couleur_claire,
                couleur_sombre,
                couleur_lisere,
            )

            if self._anim_progress > 0.55:
                alpha = min(1.0, (self._anim_progress - 0.55) / 0.45)
                self._dessiner_rang(
                    painter,
                    x,
                    y,
                    largeur_bloc,
                    hauteur_marche,
                    pays["pct_superficie_dans_pays_label"],
                    alpha,
                )

            if self._anim_progress > 0.7:
                alpha = min(1.0, (self._anim_progress - 0.7) / 0.3)
                zone_texte_y = y - zone_texte_haut

                if rang == 1:
                    self._dessiner_couronne(
                        painter,
                        x + largeur_bloc / 2,
                        zone_texte_y - zone_texte_haut * 0.25,
                        zone_texte_haut * 0.22,
                        alpha,
                    )

                self._dessiner_texte_personne(
                    painter,
                    x,
                    zone_texte_y,
                    largeur_bloc,
                    zone_texte_haut,
                    pays,
                    alpha,
                )

    # ========= COMPOSANTS DE DESSIN =========

    def _dessiner_fond(self, painter, w, h):
        degrade = QLinearGradient(0, 0, 0, h)
        degrade.setColorAt(0.0, QColor(250, 250, 253))
        degrade.setColorAt(1.0, QColor(232, 234, 240))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade)
        painter.drawRoundedRect(QRectF(0, 0, w, h), 14, 14)

        # ligne de sol légèrement ombrée
        sol = QRectF(0, h * 0.90, w, h * 0.02)
        degrade_sol = QLinearGradient(sol.topLeft(), sol.bottomLeft())
        degrade_sol.setColorAt(0.0, QColor(0, 0, 0, 35))
        degrade_sol.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(degrade_sol)
        painter.drawRect(sol)

    def _dessiner_ombre_portee(self, painter, x, base_y, largeur, hauteur):
        ombre = QRectF(
            x + largeur * 0.06, base_y - hauteur * 0.06, largeur * 0.9, hauteur * 0.14
        )
        degrade = QRadialGradient(ombre.center(), largeur * 0.5)
        degrade.setColorAt(0.0, QColor(0, 0, 0, 60))
        degrade.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade)
        painter.drawEllipse(ombre)

    def _dessiner_marche_3d(
        self,
        painter,
        x,
        y,
        largeur,
        hauteur,
        profondeur,
        couleur_claire,
        couleur_sombre,
        couleur_lisere,
    ):
        """
        Dessine un vrai bloc isométrique : la profondeur part du coin
        supérieur droit vers l'arrière (haut/droite), comme un pavé vu
        légèrement de dessus. Les trois faces (avant, dessus, côté) sont
        calculées à partir des MÊMES points, donc elles s'emboîtent
        parfaitement, sans décalage ni chevauchement.
        """
        dx = profondeur
        dy = profondeur * 0.35

        # Coins de la face avant
        tl = QPointF(x, y)
        tr = QPointF(x + largeur, y)
        bl = QPointF(x, y + hauteur)
        br = QPointF(x + largeur, y + hauteur)

        # Coins "arrière" (même points décalés vers le haut-droit)
        tl_back = QPointF(tl.x() + dx, tl.y() - dy)
        tr_back = QPointF(tr.x() + dx, tr.y() - dy)
        br_back = QPointF(br.x() + dx, br.y() - dy)

        painter.setPen(Qt.PenStyle.NoPen)

        # ---- Côté droit (face la plus sombre, dans l'ombre) ----
        cote = QPolygonF([tr, tr_back, br_back, br])
        degrade_cote = QLinearGradient(tr, br_back)
        degrade_cote.setColorAt(0.0, couleur_sombre.darker(105))
        degrade_cote.setColorAt(1.0, couleur_sombre.darker(135))
        painter.setBrush(degrade_cote)
        painter.drawPolygon(cote)

        # ---- Dessus (face la plus claire, éclairée d'en haut) ----
        dessus = QPolygonF([tl, tr, tr_back, tl_back])
        degrade_dessus = QLinearGradient(tl, tr_back)
        degrade_dessus.setColorAt(0.0, couleur_claire.lighter(140))
        degrade_dessus.setColorAt(1.0, couleur_claire.lighter(112))
        painter.setBrush(degrade_dessus)
        painter.drawPolygon(dessus)

        # ---- Face avant (dégradé vertical + reflet glossy) ----
        face_avant = QRectF(tl, br)
        degrade_face = QLinearGradient(face_avant.topLeft(), face_avant.bottomLeft())
        degrade_face.setColorAt(0.0, couleur_claire)
        degrade_face.setColorAt(1.0, couleur_sombre)
        painter.setBrush(degrade_face)
        painter.drawRect(face_avant)

        # Liseré lumineux fin, juste sous l'arête dessus/avant
        liseret = QRectF(
            face_avant.x(), face_avant.y(), face_avant.width(), max(3.0, hauteur * 0.05)
        )
        painter.setBrush(couleur_lisere)
        painter.drawRect(liseret)

        # Reflet glossy diagonal sur la face avant, sur la partie gauche
        reflet = QPainterPath()
        reflet.moveTo(
            face_avant.left() + face_avant.width() * 0.06, face_avant.top() + 2
        )
        reflet.lineTo(
            face_avant.left() + face_avant.width() * 0.32, face_avant.top() + 2
        )
        reflet.lineTo(
            face_avant.left() + face_avant.width() * 0.16, face_avant.bottom() - 2
        )
        reflet.lineTo(
            face_avant.left() + face_avant.width() * 0.02, face_avant.bottom() - 2
        )
        reflet.closeSubpath()
        painter.setBrush(QColor(255, 255, 255, 50))
        painter.drawPath(reflet)

        # ---- Arêtes fines pour bien définir les 3 faces (discrètes) ----
        pen_arete = QPen(
            QColor(
                couleur_sombre.darker(140).red(),
                couleur_sombre.darker(140).green(),
                couleur_sombre.darker(140).blue(),
                90,
            )
        )
        pen_arete.setWidthF(0.8)
        painter.setPen(pen_arete)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(tl, tr)  # arête avant/dessus
        painter.drawLine(tr, br)  # arête avant/côté
        painter.drawLine(tr, tr_back)  # arête dessus/côté
        painter.setPen(Qt.PenStyle.NoPen)

    def _dessiner_rang(self, painter, x, y, largeur, hauteur, texte, alpha):
        painter.save()
        painter.setOpacity(alpha)

        font_rang = QFont("Parisienne")  # essaie une police manuscrite
        if not QFontInfo(font_rang).exactMatch():
            font_rang = QFont("Arial")  # fallback si Parisienne absente
        font_rang.setPointSize(max(10, int(hauteur * 0.15 + 5)))
        font_rang.setBold(True)
        painter.setFont(font_rang)

        largeur_texte = largeur * 0.90
        rect_ombre = QRectF(
            x + (largeur - largeur_texte) / 2,
            y + hauteur * 0.42,
            largeur_texte,
            hauteur * 0.5,
        )
        painter.setPen(QColor(0, 0, 0, 70))
        painter.drawText(
            rect_ombre.translated(1, 1), Qt.AlignmentFlag.AlignCenter, str(texte)
        )
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(rect_ombre, Qt.AlignmentFlag.AlignCenter, str(texte))
        painter.restore()

    def _dessiner_couronne(self, painter, cx, cy, taille, alpha):
        painter.save()
        painter.setOpacity(alpha)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # --- Silhouette de la couronne (5 pointes, à-plat) ---
        pts = [
            QPointF(cx - taille, cy + taille * 0.5),
            QPointF(cx - taille, cy - taille * 0.1),
            QPointF(cx - taille * 0.5, cy + taille * 0.2),
            QPointF(cx - taille * 0.25, cy - taille * 0.45),
            QPointF(cx, cy + taille * 0.1),
            QPointF(cx + taille * 0.25, cy - taille * 0.45),
            QPointF(cx + taille * 0.5, cy + taille * 0.2),
            QPointF(cx + taille, cy - taille * 0.1),
            QPointF(cx + taille, cy + taille * 0.5),
        ]

        pen_contour = QPen(QColor(180, 130, 30), max(1.0, taille * 0.025))
        pen_contour.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        painter.setPen(pen_contour)
        painter.setBrush(QColor(255, 205, 60))
        painter.drawPolygon(QPolygonF(pts))

        # --- Bandeau de base ---
        bandeau = QRectF(cx - taille, cy + taille * 0.35, taille * 2, taille * 0.3)
        painter.setPen(pen_contour)
        painter.setBrush(QColor(255, 215, 90))
        painter.drawRoundedRect(bandeau, taille * 0.05, taille * 0.05)

        # --- Petites perles le long du bandeau ---
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 240, 190))
        nb_perles = 5
        for i in range(nb_perles):
            x = cx - taille + (2 * taille) * (i + 0.5) / nb_perles
            y = cy + taille * 0.5
            painter.drawEllipse(QPointF(x, y), taille * 0.05, taille * 0.05)

        # --- Gemmes sur les pointes (à-plat, couleurs variées) ---
        sommets = [pts[1], pts[3], pts[5], pts[7]]
        couleurs_gemmes = [
            QColor(80, 140, 230),  # saphir
            QColor(210, 60, 60),  # rubis
            QColor(210, 60, 60),  # rubis
            QColor(80, 140, 230),  # saphir
        ]
        rayon_gemme = taille * 0.10

        for p, couleur in zip(sommets, couleurs_gemmes):
            painter.setBrush(couleur)
            painter.drawEllipse(p, rayon_gemme, rayon_gemme)
            # petit point de brillance, à-plat lui aussi
            painter.setBrush(QColor(255, 255, 255, 200))
            painter.drawEllipse(
                QPointF(p.x() - rayon_gemme * 0.3, p.y() - rayon_gemme * 0.3),
                rayon_gemme * 0.3,
                rayon_gemme * 0.3,
            )

        painter.restore()

    def _dessiner_texte_personne(
        self, painter, x, y_zone, largeur, hauteur_zone, pays, alpha
    ):
        painter.save()
        painter.setOpacity(alpha)

        zone_nom = QRectF(
            x - largeur * 0.15,
            y_zone + hauteur_zone * 0.32,
            largeur * 1.3,
            hauteur_zone * 0.4,
        )

        font_nom = QFont()
        font_nom.setPointSize(11)
        font_nom.setBold(True)
        painter.setFont(font_nom)
        painter.setPen(QColor(35, 35, 40))

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
