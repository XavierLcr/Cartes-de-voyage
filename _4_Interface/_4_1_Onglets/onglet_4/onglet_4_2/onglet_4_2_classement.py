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
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_2.onglet_4_2_1_podium import Podium

from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
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


# 2 -- Thème de couleurs de la carte de classement ------------------------------


class ThemeCarteClassement:
    """
    Palette de couleurs de la carte de classement (rang 4 et plus).

    Reprend la même structure que `ThemeJoursVoyages` (onglet 4.6.4) et
    les autres thèmes du tableau de bord — même fond de carte, même
    convention d'ombre, mêmes appels de style (`renvoyer_couleur_widget`,
    `renvoyer_couleur_texte`, `renvoyer_couleur_widget_differente`) —
    avec son propre accent bleu-violet pour le badge de rang, distinct
    des médailles or/argent/bronze du podium voisin.
    """

    def __init__(
        self,
        style,
        teinte=[i / 360 for i in range(0, 360, 45)],
        nuances={
            "min_luminosite": 0.8,
            "max_luminosite": 0.95,
            "min_saturation": 0.2,
            "max_saturation": 0.4,
        },
        limite_essais=20,
    ):
        # Fond de carte : identique aux autres widgets du tableau de bord.
        self.fond = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#eaf6f7",
                sombre="#4658a1",
            )
        )
        self.texte = QColor(
            str(renvoyer_couleur_texte(style=style, couleur=self.fond.name()))
        )
        # Sous-texte
        self.sous_texte = QColor(self.texte)
        self.sous_texte.setAlpha(140)

        # Dégradé du badge de rang : bleu-violet, neutre par rapport aux
        # médailles or/argent/bronze du podium.
        self.badge_debut = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#B6EEE9",
                sombre="#24A5A5",
            )
        )
        self.badge_fin = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#55E4DD",
                sombre="#1F971F",
                reference=self.badge_debut.name(),
                essais=limite_essais,
            )
        )

        # Ombre portée : même convention que les widgets voisins.
        self.ombre = QColor(self.texte)
        self.ombre.setAlpha(60 if style == 1 else 120)


# 3 -- Carte d'une ligne de classement (style "tableau de bord") ---------------


class CarteClassementPays(QWidget):
    """
    Carte compacte pour une ligne du classement (rang 4 et plus) :
    badge de rang, nom du pays, pourcentage de superficie visitée.

    Reprend le vocabulaire visuel des widgets du tableau de bord et du
    podium voisin (onglet 4.2.1) : carte à coins arrondis, ombre douce,
    même police "joyeuse" que le podium (avec repli automatique), et un
    thème de couleurs (`ThemeCarteClassement`) construit sur les mêmes
    appels de style que le reste du tableau de bord.
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

        # Thème par défaut (clair) — mis à jour via `set_style` si le
        # widget parent (ClassementPays / OngletTopPays) est un jour
        # branché sur le système de thème clair/sombre de l'appli.
        self.theme = style

        # Même police que le podium (méthode réutilisée depuis Podium
        # pour ne pas dupliquer la liste de polices candidates).
        self.police_principale = Podium._trouver_police_disponible(
            [
                "CormorantGaramond",
                "Fredoka",
                "Quicksand",
                "Century Gothic",
                "Segoe UI",
            ]
        )

        self.setMinimumSize(80, 80)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(24)
        self._ombre_effet.setOffset(0, 6)
        self._ombre_effet.setColor(self.theme.ombre)
        self.setGraphicsEffect(self._ombre_effet)

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

        # --- carte à coins arrondis : même formule que les autres cartes ---
        rect_carte = QRectF(0, 0, w, h).adjusted(2, 2, -2, -2)
        rayon = min(20, min(w, h) * 0.14)
        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(rect_carte, rayon, rayon)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.theme.fond)
        painter.drawPath(chemin_carte)
        painter.setClipPath(chemin_carte)

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
        degrade = QLinearGradient(rect_badge.topLeft(), rect_badge.bottomRight())
        degrade.setColorAt(0.0, self.theme.badge_debut)
        degrade.setColorAt(1.0, self.theme.badge_fin)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(degrade)
        painter.drawEllipse(rect_badge)

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
        rect_nom = QRectF(w * 0.06, h * 0.46, w * 0.88, h * 0.32)
        self._dessiner_texte_wrap(painter, rect_nom, self.nom_pays)

        # --- pourcentage ---
        police_pct = QFont(self.police_principale, max(7, int(cote * 0.075)))
        painter.setFont(police_pct)
        painter.setPen(self.theme.sous_texte)
        rect_pct = QRectF(w * 0.06, h * 0.82, w * 0.88, h * 0.14)
        painter.drawText(rect_pct, Qt.AlignmentFlag.AlignCenter, self.pct_label)

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


class TitreClassement(QWidget):
    """
    Carte titre pour les sections de classement du tableau de bord.

    Le fond de la carte est entièrement occupé par une petite carte
    stylisée : un semis de points génère un pavage bas-poly façon
    "régions" (cellules de type Voronoi, remplies de teintes très
    discrètes dérivées du thème, séparées par des frontières
    irrégulières). Pour `granularite=2`, un second semis, plus dense,
    ajoute des frontières supplémentaires plus fines par-dessus,
    évoquant un découpage plus fin (départements). Le titre et le
    sous-titre sont affichés dans un panneau arrondi centré, avec le
    dégradé bleu-violet du thème, qui se détache de la carte en fond.
    """

    def __init__(
        self, titre, sous_titre="", granularite: int = 1, style=None, parent=None
    ):
        super().__init__(parent)

        self.titre = titre
        self.sous_titre = sous_titre
        self.granularite = granularite
        self.theme = style

        # Même police que le podium / les cartes de classement.
        self.police_principale = Podium._trouver_police_disponible(
            [
                "Fredoka",
                "CormorantGaramond",
                "Quicksand",
                "Century Gothic",
                "Segoe UI",
            ]
        )

        self.setMinimumHeight(92)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.ombre = QGraphicsDropShadowEffect(self)
        self.ombre.setBlurRadius(26)
        self.ombre.setOffset(0, 7)
        self.ombre.setColor(self.theme.ombre)
        self.setGraphicsEffect(self.ombre)

        # --- Grilles de la fausse carte (fixées à l'initialisation) ---

        # Semis "régions" : peu de points, répartis régulièrement (grille
        # jitterée) pour obtenir des zones larges et bien réparties,
        # plutôt qu'un nuage aléatoire pouvant se regrouper localement.
        self._semis_regions = self._generer_semis(
            graine=101, n_lignes=3, n_colonnes=4, jitter=0.32
        )
        # Grille de cellules utilisée pour peindre/tracer les "régions".
        self._grille_regions = (14, 6)  # (colonnes, lignes)

        # Semis "départements" : uniquement si granularite == 2, plus
        # dense, pour ajouter des frontières plus fines par-dessus.
        if granularite == 2:
            self._semis_departements = self._generer_semis(
                graine=202, n_lignes=6, n_colonnes=9, jitter=0.4
            )
            self._grille_departements = (34, 14)
        else:
            self._semis_departements = None
            self._grille_departements = None

    # -- Génération du semis de points (grille régulière jitterée) -----

    @staticmethod
    def _generer_semis(graine, n_lignes, n_colonnes, jitter):
        """
        Renvoie une liste de points (x, y) fractionnaires dans [0, 1] x
        [0, 1], un par case d'une grille `n_lignes` x `n_colonnes`,
        légèrement décalés aléatoirement (`jitter`, en fraction de la
        case) pour éviter un aspect trop régulier tout en gardant une
        répartition homogène façon "régions" d'un pays.
        """
        import random

        rng = random.Random(graine)
        points = []
        for j in range(n_lignes):
            for i in range(n_colonnes):
                cx = (i + 0.5) / n_colonnes
                cy = (j + 0.5) / n_lignes
                cx += (rng.random() - 0.5) * jitter / n_colonnes
                cy += (rng.random() - 0.5) * jitter / n_lignes
                points.append((min(max(cx, 0.0), 1.0), min(max(cy, 0.0), 1.0)))
        return points

    @staticmethod
    def _plus_proche(fx, fy, semis):
        """Indice du point du `semis` le plus proche de (fx, fy)
        (distance euclidienne au carré, en coordonnées fractionnaires)."""
        meilleur_i, meilleure_dist = 0, None
        for i, (sx, sy) in enumerate(semis):
            dist = (fx - sx) ** 2 + (fy - sy) ** 2
            if meilleure_dist is None or dist < meilleure_dist:
                meilleur_i, meilleure_dist = i, dist
        return meilleur_i

    def _assignation_cellules(self, semis, colonnes, lignes):
        """Renvoie une grille [lignes][colonnes] contenant, pour chaque
        cellule, l'indice du point du `semis` le plus proche de son
        centre (pavage façon Voronoi discrétisé)."""
        return [
            [
                self._plus_proche((i + 0.5) / colonnes, (j + 0.5) / lignes, semis)
                for i in range(colonnes)
            ]
            for j in range(lignes)
        ]

    def _dessiner_fausse_carte(self, painter, rect: QRectF):
        """Peint la fausse carte (remplissage + frontières) dans `rect`,
        en superposant la couche "régions" puis, si disponible, la
        couche "départements" (frontières fines uniquement)."""

        largeur, hauteur = rect.width(), rect.height()

        # --- Couche "régions" : remplissage + frontières ---
        colonnes, lignes = self._grille_regions
        assignation = self._assignation_cellules(self._semis_regions, colonnes, lignes)

        # Petite palette de teintes très proches du fond, dérivées du
        # thème, pour un effet chloropléthe discret.
        palette = [
            self.theme.fond,
            self.theme.fond.lighter(106),
            self.theme.fond.darker(104),
        ]

        largeur_cellule = largeur / colonnes
        hauteur_cellule = hauteur / lignes

        painter.setPen(Qt.PenStyle.NoPen)
        for j in range(lignes):
            for i in range(colonnes):
                couleur = palette[assignation[j][i] % len(palette)]
                painter.setBrush(couleur)
                painter.drawRect(
                    QRectF(
                        rect.x() + i * largeur_cellule,
                        rect.y() + j * hauteur_cellule,
                        largeur_cellule + 0.5,
                        hauteur_cellule + 0.5,
                    )
                )

        couleur_frontiere_region = QColor(self.theme.sous_texte)
        couleur_frontiere_region.setAlpha(120)
        painter.setPen(
            QPen(
                couleur_frontiere_region,
                max(1.0, min(largeur, hauteur) * 0.006),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        for j in range(lignes):
            for i in range(colonnes):
                # Frontière verticale (avec la cellule à droite)
                if i + 1 < colonnes and assignation[j][i] != assignation[j][i + 1]:
                    x = rect.x() + (i + 1) * largeur_cellule
                    painter.drawLine(
                        QPointF(x, rect.y() + j * hauteur_cellule),
                        QPointF(x, rect.y() + (j + 1) * hauteur_cellule),
                    )
                # Frontière horizontale (avec la cellule du dessous)
                if j + 1 < lignes and assignation[j][i] != assignation[j + 1][i]:
                    y = rect.y() + (j + 1) * hauteur_cellule
                    painter.drawLine(
                        QPointF(rect.x() + i * largeur_cellule, y),
                        QPointF(rect.x() + (i + 1) * largeur_cellule, y),
                    )

        # --- Couche "départements" (frontières fines uniquement) ---
        if self._semis_departements and self._grille_departements:
            colonnes2, lignes2 = self._grille_departements
            assignation2 = self._assignation_cellules(
                self._semis_departements, colonnes2, lignes2
            )
            largeur_cellule2 = largeur / colonnes2
            hauteur_cellule2 = hauteur / lignes2

            couleur_frontiere_dep = QColor(self.theme.sous_texte)
            couleur_frontiere_dep.setAlpha(65)
            painter.setPen(
                QPen(
                    couleur_frontiere_dep,
                    max(0.6, min(largeur, hauteur) * 0.0025),
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                )
            )
            for j in range(lignes2):
                for i in range(colonnes2):
                    if (
                        i + 1 < colonnes2
                        and assignation2[j][i] != assignation2[j][i + 1]
                    ):
                        x = rect.x() + (i + 1) * largeur_cellule2
                        painter.drawLine(
                            QPointF(x, rect.y() + j * hauteur_cellule2),
                            QPointF(x, rect.y() + (j + 1) * hauteur_cellule2),
                        )
                    if j + 1 < lignes2 and assignation2[j][i] != assignation2[j + 1][i]:
                        y = rect.y() + (j + 1) * hauteur_cellule2
                        painter.drawLine(
                            QPointF(rect.x() + i * largeur_cellule2, y),
                            QPointF(rect.x() + (i + 1) * largeur_cellule2, y),
                        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()
        rect = QRectF(2, 2, w - 4, h - 4)
        rayon_carte = min(22, h * 0.26)

        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(rect, rayon_carte, rayon_carte)

        # --- fond de carte + fausse carte, contenus dans les coins arrondis ---
        painter.save()
        painter.setClipPath(chemin_carte)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.theme.fond)
        painter.drawRect(rect)

        self._dessiner_fausse_carte(painter, rect)

        painter.restore()

        # --- panneau central (titre / sous-titre), au-dessus de la carte ---
        police_titre = QFont(
            self.police_principale, max(10, int(h * 0.14)), QFont.Weight.DemiBold
        )
        police_sous_titre = QFont(self.police_principale, max(7, int(h * 0.1)))

        painter.setFont(police_titre)
        metrics_titre = painter.fontMetrics()
        largeur_max_texte = w * 0.8
        titre_affiche = metrics_titre.elidedText(
            self.titre, Qt.TextElideMode.ElideRight, int(largeur_max_texte)
        )
        largeur_titre = metrics_titre.horizontalAdvance(titre_affiche)
        hauteur_titre = metrics_titre.height()

        largeur_sous_titre = 0
        hauteur_sous_titre = 0
        sous_titre_affiche = ""
        if self.sous_titre:
            painter.setFont(police_sous_titre)
            metrics_sous_titre = painter.fontMetrics()
            sous_titre_affiche = metrics_sous_titre.elidedText(
                self.sous_titre, Qt.TextElideMode.ElideRight, int(largeur_max_texte)
            )
            largeur_sous_titre = metrics_sous_titre.horizontalAdvance(
                sous_titre_affiche
            )
            hauteur_sous_titre = metrics_sous_titre.height()

        pad_h, pad_v, espace = 22, 12, 2
        largeur_panneau = min(
            w * 0.86, max(largeur_titre, largeur_sous_titre) + pad_h * 2
        )
        hauteur_panneau = (
            hauteur_titre
            + hauteur_sous_titre
            + (espace if self.sous_titre else 0)
            + pad_v * 2
        )

        rect_panneau = QRectF(
            w / 2 - largeur_panneau / 2,
            h / 2 - hauteur_panneau / 2,
            largeur_panneau,
            hauteur_panneau,
        )
        rayon_panneau = min(16, hauteur_panneau * 0.3)

        degrade_panneau = QLinearGradient(
            rect_panneau.topLeft(), rect_panneau.bottomRight()
        )
        degrade_panneau.setColorAt(0, self.theme.badge_debut)
        degrade_panneau.setColorAt(1, self.theme.badge_fin)

        chemin_panneau = QPainterPath()
        chemin_panneau.addRoundedRect(rect_panneau, rayon_panneau, rayon_panneau)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(degrade_panneau))
        painter.drawPath(chemin_panneau)

        contour = QColor(255, 255, 255, 90)
        painter.setPen(QPen(contour, 1.2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(chemin_panneau)

        y_depart = rect_panneau.y() + pad_v
        painter.setFont(police_titre)
        painter.setPen(QColor(255, 255, 255, 255))
        painter.drawText(
            QRectF(rect_panneau.x(), y_depart, rect_panneau.width(), hauteur_titre),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            titre_affiche,
        )

        if self.sous_titre:
            painter.setFont(police_sous_titre)
            painter.setPen(QColor(255, 255, 255, 210))
            painter.drawText(
                QRectF(
                    rect_panneau.x(),
                    y_depart + hauteur_titre + espace,
                    rect_panneau.width(),
                    hauteur_sous_titre,
                ),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
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

        layout_final.addWidget(
            TitreClassement(
                titre=titre,
                sous_titre="",
                style=self.style,
                granularite=granularite,
            )
        )

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
