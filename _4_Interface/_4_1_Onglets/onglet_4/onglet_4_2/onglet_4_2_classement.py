################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4.2 – Partie classement des pays visités                              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import pandas as pd
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
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    vider_layout,
    creer_scroll,
    _trouver_police_disponible,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_2.onglet_4_2_2_podium import Podium
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_2.onglet_4_2_1_style_visuel import (
    ThemeCarteClassement,
)

# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de création du classement des pays les plus visités ---------


def creer_classement_pays(
    gdf_visite,
    table_superficie,
    pays_traductions: dict,
    langue: str,
    granularite: int = 1,
    top_n: int | None = None,
    ndigits: int | None = None,
):

    df_temp = (
        # Ajout des superficies
        gdf_visite.copy()
        .merge(
            table_superficie,
            how="left",
            left_on=["pays", "subdivision"],
            right_on=["name_0", f"name_{granularite}"],
        )
        # Somme par pays des superficies visitées
        .groupby("pays")[["pct_superficie_pays", "superficie"]]
        .sum()
        .reset_index()
        # Tri des valeurs par ordre décroissant
        .sort_values(by=["pct_superficie_pays", "superficie"], ascending=[False, False])
        # Arrondi de la valeur
        .assign(
            pct_superficie_pays=lambda x: x["pct_superficie_pays"].apply(
                lambda x: round(100 * (x or 0), ndigits=ndigits)
            )
        )
        .assign(
            # Mise en forme du pourcentage
            pct_superficie_pays_label=lambda x: x["pct_superficie_pays"].apply(
                lambda x: f"{x} %".replace(".", ",")
            ),
            # Récupération du nom du pays dans la langue utilisée
            nom_pays=lambda x: x["pays"]
            .map({k: v.get(langue, k) for k, v in pays_traductions.items()})
            .fillna(x["pays"]),
        )
        .reset_index()
    )

    # Ajout du classement
    df_temp["classement"] = df_temp.index.to_series().apply(
        lambda i: ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
    )

    # Sélection du top pays si souhaité
    if top_n is not None:
        df_temp = df_temp.head(top_n)

    # Pays avec un pourcentage arrondi non nul ou dans les trois premières lignes
    df_temp = df_temp[(df_temp["pct_superficie_pays"] > 0) | (df_temp.index < 3)]

    return df_temp


## 1.2 -- Fonction d'agrégation des lignes à 100 % -----------------------------


def agreger_top_pays(df: pd.DataFrame, top_n_lignes_min: int | None):

    df_temp = df.copy()

    top_n_lignes = (df_temp["pct_superficie_pays"] == 100).sum()

    # Agrégation des pays à 100 % (si souhaité)
    if top_n_lignes_min is not None and top_n_lignes >= top_n_lignes_min:

        df_temp = pd.concat(
            [  # Agrégation des premières lignes
                pd.DataFrame(
                    {
                        "classement": [df_temp["classement"].iloc[0]],
                        "nom_pays": [", ".join(df_temp.head(top_n_lignes)["nom_pays"])],
                        "pct_superficie_pays_label": [
                            df_temp["pct_superficie_pays_label"].iloc[0]
                        ],
                        "pct_superficie_pays": [df_temp["pct_superficie_pays"].iloc[0]],
                    }
                ),
                # reste de la table
                df_temp.iloc[top_n_lignes:][
                    [
                        "classement",
                        "nom_pays",
                        "pct_superficie_pays",
                        "pct_superficie_pays_label",
                    ]
                ],
            ],
            axis=0,
        ).assign(agreg=True)

    else:

        df_temp["agreg"] = False

    # Renvoi
    return df_temp


## 1.3 -- Fonction de création d'une carte pour une ligne du classement --------


def creer_label_pays(
    ligne,
    style,
):
    """
    Renvoie une carte (CarteClassementPays) pour une ligne du classement
    située au-delà du podium (rang 4 et plus), dans le même style que
    les widgets du tableau de bord et le podium.
    """
    classement_brut = str(ligne["classement"])

    return CarteClassementPays(
        classement=classement_brut,
        nom_pays=str(ligne["nom_pays"]),
        pct_label=str(ligne["pct_superficie_pays_label"]),
        style=style,
    )


# 2 -- Carte d'une ligne de classement (style "tableau de bord") ---------------


class CarteClassementPays(QWidget):
    """
    Carte compacte pour une ligne du classement (rang 4 et plus) :
    badge de rang, nom du pays, pourcentage de superficie visitée.

    Reprend le vocabulaire visuel des widgets du tableau de bord et du
    podium voisin (onglet 4.2.1) : carte à coins arrondis, ombre douce,
    même police "joyeuse" que le podium (avec repli automatique), et un
    thème de couleurs (`ThemeCarteClassement`) construit sur les mêmes
    appels de style que le reste du tableau de bord.

    Améliorations visuelles par rapport à la version précédente :
    - léger liseré (bordure) autour de la carte pour la détacher du fond
    - reflet "glacé" en haut de la carte pour un effet plus premium
    - badge de rang avec ombre portée propre et anneau de contour
    - mini barre de progression sous le pourcentage, pour visualiser
      la superficie visitée d'un coup d'œil
    - séparateur discret entre le nom du pays et le pourcentage
    """

    def __init__(
        self,
        classement: str,
        nom_pays: str,
        pct_label: str,
        style,
        parent=None,
    ) -> None:

        super().__init__(parent)

        self.classement = classement
        self.nom_pays = nom_pays
        self.pct_label = pct_label

        # Valeur numérique du pourcentage, utilisée pour la mini barre de
        # progression. On tente de la déduire de `pct_label` (ex: "42 %"),
        # et on retombe sur 0 si l'extraction échoue.
        self._pct_valeur = self._extraire_pourcentage(pct_label)

        # Thème par défaut (clair) — mis à jour via `set_style` si le
        # widget parent (ClassementPays / OngletTopPays) est un jour
        # branché sur le système de thème clair/sombre de l'appli.
        self.theme = style

        # Même police que le podium (méthode réutilisée depuis Podium
        # pour ne pas dupliquer la liste de polices candidates).
        self.police_principale = _trouver_police_disponible(
            [
                "CormorantGaramond",
                "Fredoka",
                "Quicksand",
                "Century Gothic",
                "Segoe UI",
            ]
        )

        self.setMinimumSize(80, 90)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(28)
        self._ombre_effet.setOffset(0, 8)
        self._ombre_effet.setColor(self.theme.ombre)
        self.setGraphicsEffect(self._ombre_effet)

    @staticmethod
    def _extraire_pourcentage(pct_label: str) -> float:
        """Extrait la valeur numérique d'un label du type '42 %' ou '3.5%'."""
        chiffres = ""
        for c in pct_label:
            if c.isdigit() or c == ".":
                chiffres += c
            elif chiffres:
                break
        try:
            return max(0.0, min(100.0, float(chiffres)))
        except ValueError:
            return 0.0

    def set_style(self, style, nuances, teintes):
        """Met à jour le thème de couleurs (même signature que les autres
        widgets du tableau de bord : `set_style(style, nuances, teintes)`)."""
        self.theme = ThemeCarteClassement(
            style=style, nuances=nuances, teinte=teintes, limite_essais=20
        )
        self._ombre_effet.setColor(self.theme.ombre)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()

        # --- carte à coins arrondis ---
        rect_carte = QRectF(0, 0, w, h).adjusted(2, 2, -2, -2)
        rayon = min(20, min(w, h) * 0.14)
        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(rect_carte, rayon, rayon)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.theme.fond)
        painter.drawPath(chemin_carte)

        # léger liseré pour détacher la carte du fond
        pen_contour = QPen(self.theme.badge_debut)
        pen_contour.setWidthF(1.1)
        pen_contour.setColor(self._avec_alpha(self.theme.badge_debut, 60))
        painter.setPen(pen_contour)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(chemin_carte)

        painter.setClipPath(chemin_carte)

        # reflet "glacé" discret en haut de la carte
        degrade_reflet = QLinearGradient(0, 0, 0, h * 0.5)
        degrade_reflet.setColorAt(0.0, self._avec_alpha(QColor("#FFFFFF"), 40))
        degrade_reflet.setColorAt(1.0, self._avec_alpha(QColor("#FFFFFF"), 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade_reflet)
        painter.drawRect(QRectF(0, 0, w, h * 0.5))

        cote = min(w, h)

        # --- badge de rang ---
        rayon_badge = cote * 0.17
        centre_badge_y = h * 0.24
        rect_badge = QRectF(
            w / 2 - rayon_badge,
            centre_badge_y - rayon_badge,
            rayon_badge * 2,
            rayon_badge * 2,
        )

        # petite ombre propre au badge, pour le détacher du fond de carte
        rect_ombre_badge = rect_badge.translated(0, rayon_badge * 0.12)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._avec_alpha(QColor("#000000"), 35))
        painter.drawEllipse(rect_ombre_badge)

        degrade = QLinearGradient(rect_badge.topLeft(), rect_badge.bottomRight())
        degrade.setColorAt(0.0, self.theme.badge_debut)
        degrade.setColorAt(1.0, self.theme.badge_fin)
        painter.setBrush(degrade)
        painter.drawEllipse(rect_badge)

        # fin anneau clair sur le pourtour du badge, effet "médaille"
        pen_anneau = QPen(self._avec_alpha(QColor("#FFFFFF"), 90))
        pen_anneau.setWidthF(max(1.0, rayon_badge * 0.06))
        painter.setPen(pen_anneau)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect_badge.adjusted(1, 1, -1, -1))

        police_badge = QFont(
            self.police_principale, max(7, int(rayon_badge * 0.62)), QFont.Weight.Bold
        )
        painter.setFont(police_badge)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(rect_badge, Qt.AlignmentFlag.AlignCenter, self.classement)

        # --- nom du pays ---
        police_nom = QFont(
            self.police_principale, max(8, int(cote * 0.09)), QFont.Weight.DemiBold
        )
        painter.setFont(police_nom)
        painter.setPen(self.theme.texte)
        rect_nom = QRectF(w * 0.06, h * 0.46, w * 0.88, h * 0.26)
        self._dessiner_texte_wrap(painter, rect_nom, self.nom_pays)

        # --- pourcentage ---
        police_pct = QFont(self.police_principale, max(7, int(cote * 0.075)))
        painter.setFont(police_pct)
        painter.setPen(self.theme.sous_texte)
        rect_pct = QRectF(w * 0.06, h * 0.77, w * 0.88, h * 0.13)
        painter.drawText(rect_pct, Qt.AlignmentFlag.AlignCenter, self.pct_label)

        # --- mini barre de progression ---
        largeur_barre = w * 0.7
        hauteur_barre = max(3.0, h * 0.028)
        x_barre = (w - largeur_barre) / 2
        y_barre = h * 0.92

        rect_barre_fond = QRectF(x_barre, y_barre, largeur_barre, hauteur_barre)
        chemin_fond = QPainterPath()
        chemin_fond.addRoundedRect(
            rect_barre_fond, hauteur_barre / 2, hauteur_barre / 2
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._avec_alpha(self.theme.sous_texte, 45))
        painter.drawPath(chemin_fond)

        largeur_remplie = largeur_barre * (self._pct_valeur / 100.0)
        if largeur_remplie > 0:
            rect_barre_remplie = QRectF(
                x_barre, y_barre, largeur_remplie, hauteur_barre
            )
            chemin_remplie = QPainterPath()
            chemin_remplie.addRoundedRect(
                rect_barre_remplie, hauteur_barre / 2, hauteur_barre / 2
            )
            degrade_barre = QLinearGradient(
                rect_barre_remplie.topLeft(), rect_barre_remplie.topRight()
            )
            degrade_barre.setColorAt(0.0, self.theme.badge_debut)
            degrade_barre.setColorAt(1.0, self.theme.badge_fin)
            painter.setBrush(degrade_barre)
            painter.drawPath(chemin_remplie)

    @staticmethod
    def _avec_alpha(couleur: QColor, alpha: int) -> QColor:
        """Retourne une copie de `couleur` avec un canal alpha donné (0-255)."""
        c = QColor(couleur)
        c.setAlpha(alpha)
        return c

    def _dessiner_texte_wrap(self, painter, rect, texte):
        """Découpe `texte` en lignes qui tiennent dans la largeur de `rect`
        (même logique que le podium voisin)."""
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

        y_depart = rect.y() + max(0.0, (rect.height() - hauteur_totale) / 2)
        for i, ligne in enumerate(lignes):
            rect_ligne = QRectF(
                rect.x(), y_depart + i * hauteur_ligne, rect.width(), hauteur_ligne
            )
            painter.drawText(rect_ligne, Qt.AlignmentFlag.AlignCenter, ligne)


# 3 -- Classe du widget de titre -----------------------------------------------


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
    def _teinte_douce(couleur: QColor, alpha: int) -> QColor:
        """Copie une QColor du thème avec une opacité réduite, pour ne
        jamais muter les couleurs originales du thème."""
        c = QColor(couleur)
        c.setAlpha(alpha)
        return c

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
        degrade.setColorAt(0, self._teinte_douce(self.theme.badge_debut, 150))
        degrade.setColorAt(1, self._teinte_douce(self.theme.badge_fin, 150))
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
        teinte_fin = self._teinte_douce(self.theme.badge_fin, 235)
        teinte_debut = self._teinte_douce(self.theme.badge_debut, 235)
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
        painter.setBrush(self._teinte_douce(self.theme.badge_fin, 150))
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
        degrade_nord.setColorAt(0.0, self._teinte_douce(self.theme.badge_fin, 255))
        degrade_nord.setColorAt(1.0, self._teinte_douce(self.theme.badge_fin, 195))
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
        degrade_sud.setColorAt(0.0, self._teinte_douce(self.theme.badge_debut, 245))
        degrade_sud.setColorAt(1.0, self._teinte_douce(self.theme.badge_debut, 150))
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
        degrade_pivot.setColorAt(0.4, self._teinte_douce(self.theme.badge_fin, 255))
        degrade_pivot.setColorAt(1.0, self._teinte_douce(self.theme.badge_fin, 220))
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


# 4 -- Classe affichant les pays les plus visités ------------------------------


class ClassementPays(QWidget):
    def __init__(
        self,
        constantes,
        fct_traduction,
        table_superficie,
        parent=None,
        min_changement_mise_en_forme: int = 4,
        adapter_mise_en_forme: bool = True,
    ):
        super().__init__(parent)

        # === Variables globales === #
        self.pays_traductions = constantes.pays_differentes_langues
        self.table_superficie = table_superficie
        self.top_n = constantes.parametres_application["top_n_pays"]
        self.ndigits = constantes.parametres_application["pct_ndigits"]
        self.ndigits = None if self.ndigits == 0 else self.ndigits
        self.fonction_traduction = fct_traduction
        self.dicts_granu = {"region": {}, "dep": {}}
        self.langue_utilisee = "français"
        self.min_changement_mise_en_forme = min_changement_mise_en_forme
        self.adapter_mise_en_forme = adapter_mise_en_forme
        self.n_colonnes = 3

        # === Layout principal === #
        self.layout = QHBoxLayout(self)

        # Style par défaut
        self.set_style(
            style=1,
            teintes=[i / 360 for i in range(0, 360, 45)],
            nuances={
                "min_luminosite": 0.8,
                "max_luminosite": 0.95,
                "min_saturation": 0.2,
                "max_saturation": 0.4,
            },
        )

    def creer_layout_classement(self, df: pd.DataFrame, vbox: QVBoxLayout):
        """
        Affiche le classement des pays dans un QGridLayout (vbox).
        - df : DataFrame contenant 'Pays' et 'pct_superficie_pays'
        - vbox : QVBoxLayout où ajouter les QLabel
        """

        if df is None or df.empty:
            return

        df_temp = df.copy()

        # === Ajout de la première ligne === #

        layout_temp = QHBoxLayout()
        n_lignes = 3 if df_temp["agreg"].sum() == 0 else 1

        podium_temp = Podium()
        podium_temp.set_style(style_parent=self.style)
        podium_temp.set_donnees(df_temp.head(n=n_lignes).to_dict(orient="records"))

        layout_temp.addWidget(podium_temp)

        # Ajout au layout
        vbox.addLayout(layout_temp)

        # Suppression de la première ligne
        df_temp = df_temp.iloc[n_lignes:]

        # === Ajout des autres lignes === #

        layout_temp = QGridLayout()
        n_col_temp = self.n_colonnes
        layout_necessaire = False

        # Complétion du reste des cases
        for i, (_, ligne) in enumerate(df_temp.iterrows()):

            layout_necessaire = True

            # Ajout du label
            layout_temp.addWidget(
                creer_label_pays(
                    ligne=ligne,
                    style=self.style,
                ),
                i // n_col_temp,
                i % n_col_temp,
            )

            # Largueur de la colonne
            layout_temp.setColumnStretch(i % n_col_temp, 1)

        # Ajout au layout
        if layout_necessaire:
            vbox.addLayout(layout_temp)

    def lancer_classement_pays(self, granularite: int, dict_territoire: dict):

        layout_final = QVBoxLayout()
        titre = self.fonction_traduction(
            f"classement_selon_{'regions' if granularite==1 else 'departements'}"
        )

        layout_final.addWidget(TitreClassement(titre=titre, style=self.style))

        try:

            # Création de la table des lieux visités
            df_temp = pd.DataFrame(
                [(k, v) for k, lst in (dict_territoire.items()) for v in (lst or [])],
                columns=["pays", "subdivision"],
            )

            # Classement des pays
            df_temp = creer_classement_pays(
                # Transformation du dictionnaire en Data.frame
                gdf_visite=df_temp,
                table_superficie=self.table_superficie,
                pays_traductions=self.pays_traductions,
                langue=self.langue_utilisee,
                granularite=granularite,
                top_n=self.top_n,
                ndigits=self.ndigits,
            )
            # Agrégation du top pays (si souhaité et nécessaire)
            df_temp = agreger_top_pays(
                df=df_temp,
                top_n_lignes_min=(
                    None
                    if not self.adapter_mise_en_forme
                    else self.min_changement_mise_en_forme
                ),
            )

            self.creer_layout_classement(
                df=df_temp,
                vbox=layout_final,
            )

        except Exception as e:
            return None

        layout_final.addStretch()

        # Mise en scroll et renvoi
        return creer_scroll(layout=layout_final)

    def lancer_classement_par_region_departement(self):

        # Nettoyage du layout
        vider_layout(self.layout)

        # Création des dictionnaires
        dict_regions = self.dicts_granu.get("region") or {}
        dict_departements = self.dicts_granu.get("dep") or {}

        for pays, deps in dict_departements.items():
            mask = (self.table_superficie["name_0"] == pays) & (
                self.table_superficie["name_2"].isin(deps)
            )
            dict_regions[pays] = (
                self.table_superficie.loc[mask, "name_1"].unique().tolist()
            )

        # Choix de self.n_colonnes
        if (dict_regions == {}) or (dict_departements == {}):
            self.n_colonnes = 6
        else:
            self.n_colonnes = 3

        for granu, dict_temp in {1: dict_regions, 2: dict_departements}.items():

            if dict_temp:

                # Création du layout
                res_temp = self.lancer_classement_pays(
                    granularite=granu, dict_territoire=dict_temp
                )

                # Ajout
                if res_temp is not None:
                    self.layout.addWidget(res_temp)

    def set_dicts_granu(self, dict_nv):
        self.dicts_granu = dict_nv

    def set_langue(self, nouvelle_langue):
        self.langue_utilisee = nouvelle_langue
        self.lancer_classement_par_region_departement()

    def set_style(self, style, nuances, teintes):
        self.style = ThemeCarteClassement(
            style=style, teinte=teintes, nuances=nuances, limite_essais=20
        )
        self.lancer_classement_par_region_departement()
