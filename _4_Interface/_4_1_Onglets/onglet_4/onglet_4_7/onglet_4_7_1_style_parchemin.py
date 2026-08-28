################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_7                                #
# Onglet 4.7.1 – Style du parchemin                                            #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import math
import random

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import QLabel

# 1 -- Classe de création du parchemin -----------------------------------------


class QLabelParchemin(QLabel):
    """
    QLabel dont le fond est peint à la main pour simuler un morceau de
    parchemin / vieux papier, avec un rendu différent à chaque instance
    (sauf si un seed fixe est fourni).
    """

    def __init__(
        self,
        *args,
        couleur_papier="#E8D9B5",
        couleur_bord="#6B5637",
        couleur_encre="#3B2A1A",
        intensite_taches=0.5,
        amplitude_bord=3.5,
        seed=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.couleur_papier = QColor(couleur_papier)
        self.couleur_bord = QColor(couleur_bord)
        self.couleur_encre = QColor(couleur_encre)
        self.intensite_taches = intensite_taches
        self.amplitude_bord = amplitude_bord

        self._seed = seed if seed is not None else random.randint(0, 999_999)

        # caches de la texture générée (dépendent de la taille du widget)
        self._taille_cache = None
        self._chemin_bord = None
        self._points_bruit = []
        self._taches = []

        # le fond est peint à la main -> on désactive le fond par défaut de QLabel
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

    # ------------------------------------------------------------------ #
    # Génération de la texture (appelée au resize / premier affichage)
    # ------------------------------------------------------------------ #
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._generer_texture()

    def _generer_texture(self):
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        self._taille_cache = (w, h)
        rng = random.Random(self._seed)  # reset pour un rendu stable au resize

        self._chemin_bord = self._construire_bord_irregulier(w, h, rng)

        # grain fin sur toute la surface
        nb_points = max(80, int(w * h / 22))
        self._points_bruit = []
        for _ in range(nb_points):
            x = rng.uniform(0, w)
            y = rng.uniform(0, h)
            alpha = rng.randint(4, 16)
            plus_clair = rng.random() < 0.5
            self._points_bruit.append((x, y, alpha, plus_clair))

        # taches d'humidité / vieillissement
        nb_taches = max(2, int(6 * self.intensite_taches))
        self._taches = []
        for _ in range(nb_taches):
            cx = rng.uniform(0, w)
            cy = rng.uniform(0, h)
            rayon = rng.uniform(min(w, h) * 0.10, min(w, h) * 0.26)
            alpha = rng.randint(8, 24)
            self._taches.append((cx, cy, rayon, alpha))

    def _construire_bord_irregulier(self, w, h, rng, pas=13):
        """
        Construit un contour rectangulaire dont les bords sont légèrement
        "cassés" par du bruit, pour éviter l'effet carré parfait.
        """
        marge = self.amplitude_bord + 1
        coins = [
            (marge, marge),
            (w - marge, marge),
            (w - marge, h - marge),
            (marge, h - marge),
            (marge, marge),
        ]

        points_bruts = []  # (x, y, cote) ; cote: 0=haut,1=droite,2=bas,3=gauche
        cotes = [0, 1, 2, 3]
        for i in range(4):
            x0, y0 = coins[i]
            x1, y1 = coins[i + 1]
            longueur = math.hypot(x1 - x0, y1 - y0)
            nb = max(3, int(longueur / pas))
            for k in range(nb + 1):
                t = k / nb
                x = x0 + (x1 - x0) * t
                y = y0 + (y1 - y0) * t
                points_bruts.append([x, y, cotes[i]])

        # décalage perpendiculaire au segment, aléatoire mais lissé
        decalage_precedent = 0.0
        pts_finaux = []
        for x, y, cote in points_bruts:
            bruit = rng.uniform(-self.amplitude_bord, self.amplitude_bord)
            # lissage simple : moyenne avec le décalage précédent
            bruit = (bruit + decalage_precedent) / 2
            decalage_precedent = bruit

            if cote == 0:  # haut -> décale en y
                y -= bruit
            elif cote == 2:  # bas
                y += bruit
            elif cote == 3:  # gauche
                x -= bruit
            else:  # droite
                x += bruit
            pts_finaux.append(QPointF(x, y))

        chemin = QPainterPath()
        chemin.moveTo(pts_finaux[0])
        for p in pts_finaux[1:]:
            chemin.lineTo(p)
        chemin.closeSubpath()
        return chemin

    # ------------------------------------------------------------------ #
    # Peinture
    # ------------------------------------------------------------------ #
    def paintEvent(self, event):
        w, h = self.width(), self.height()
        if self._taille_cache != (w, h) or self._chemin_bord is None:
            self._generer_texture()

        if self._chemin_bord is not None:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            painter.save()
            painter.setClipPath(self._chemin_bord)

            # 1. fond avec vignettage (plus clair au centre, plus sombre aux bords)
            degrade = QRadialGradient(w / 2, h / 2, max(w, h) * 0.75)
            degrade.setColorAt(0.0, self.couleur_papier.lighter(108))
            degrade.setColorAt(0.7, self.couleur_papier)
            degrade.setColorAt(1.0, self.couleur_papier.darker(124))
            painter.fillPath(self._chemin_bord, QBrush(degrade))

            # 2. taches d'humidité
            painter.setPen(Qt.PenStyle.NoPen)
            for cx, cy, rayon, alpha in self._taches:
                base = self.couleur_bord.darker(105)
                centre = QColor(base)
                centre.setAlpha(0)
                bord_tache = QColor(base)
                bord_tache.setAlpha(alpha)
                transparent = QColor(base)
                transparent.setAlpha(0)

                degrade_tache = QRadialGradient(cx, cy, rayon)
                degrade_tache.setColorAt(0.0, centre)
                degrade_tache.setColorAt(0.75, bord_tache)
                degrade_tache.setColorAt(1.0, transparent)
                painter.setBrush(QBrush(degrade_tache))
                painter.drawEllipse(QPointF(cx, cy), rayon, rayon)

            # 3. grain fin
            for x, y, alpha, plus_clair in self._points_bruit:
                couleur = (
                    self.couleur_papier.lighter(130)
                    if plus_clair
                    else self.couleur_bord.darker(115)
                )
                couleur.setAlpha(alpha)
                painter.setPen(QPen(couleur, 0.9))
                painter.drawPoint(QPointF(x, y))

            painter.restore()

            # 4. liseré de contour (irrégulier lui aussi, cohérent avec le fond)
            stylo = QPen(self.couleur_bord, 1.3)
            stylo.setCosmetic(True)
            painter.setPen(stylo)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self._chemin_bord)

            painter.end()

        # le texte est géré par QLabel lui-même (wordWrap, alignement, police
        # définis via setStyleSheet / setAlignment / setWordWrap)
        super().paintEvent(event)


# 3 -- Fonction finale ---------------------------------------------------------


def creer_QLabel_parchemin(
    text="",
    wordWrap=True,
    alignement=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
    police_script="Georgia",
    taille_police=19,
    couleur_encre="#3B2A1A",
    couleur_papier="#E8D9B5",
    couleur_bord_papier="#6B5637",
    intensite_taches=0.5,
    seed=None,
):
    """
    Crée un QLabel façon parchemin ancien, texturé (grain, taches, bord
    irrégulier), avec un texte aligné/word-wrappé comme demandé.

    Paramètres
    ----------
    text : str
        Le texte à afficher.
    wordWrap : bool
        Active le retour à la ligne automatique.
    alignement : Qt.AlignmentFlag
        Alignement du texte dans le label.
    police_script, taille_police, couleur_encre :
        Apparence du texte.
    couleur_papier, couleur_bord_papier :
        Apparence du "papier" (fond et liseré).
    intensite_taches : float
        0 = presque propre, 1 = très taché/vieilli.
    seed : int | None
        Fixe le rendu aléatoire (même seed = même texture à chaque lancement).
        Laisser à None pour un rendu différent à chaque création.
    """
    label = QLabelParchemin(
        text,
        couleur_papier=couleur_papier,
        couleur_bord=couleur_bord_papier,
        couleur_encre=couleur_encre,
        intensite_taches=intensite_taches,
        seed=seed,
    )
    label.setWordWrap(wordWrap)
    label.setAlignment(alignement)
    label.setStyleSheet(f"""
        QLabel {{
            font-family: {police_script};
            font-size: {taille_police}px;
            font-weight: 400;
            color: {couleur_encre};
            background: transparent;
            border: none;
            padding: 30px 36px;
        }}
        """)
    return label
