################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.3 – Suggestions de nouvelles destinations                           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import copy, numba
import numpy as np
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QRectF, QSize
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient, QPainterPath
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QGraphicsDropShadowEffect,
    QSizePolicy,
    QSpacerItem,
)

from _0_Utilitaires._0_1_fonctions_utiles_gen import (
    distance_haversine,
    voyages_vers_destinations,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    vider_layout,
)

from _4_Interface._4_2_Style._4_2_2_styles_complementaires import (
    style_bouton_recommandation,
)

from _4_Interface._4_1_Onglets.onglet_4.onglet_4_2.onglet_4_2_1_podium import Podium
from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)

# 1 -- Fonctions ---------------------------------------------------------------


## 1.1 -- Fonction de calcul des scores entre régions --------------------------


@numba.njit(parallel=True)
def calculer_score_region(
    lats_visite,
    lons_visite,
    vals_visite,
    na_visite,
    superficie_visite,
    lats_reste,
    lons_reste,
    vals_reste,
    na_reste,
    alpha,
):
    n_reste = lats_reste.shape[0]
    n_visite = lats_visite.shape[0]
    scores = np.zeros(n_reste)
    superficie_visitee_totale = np.sum(superficie_visite)
    poids_visite = superficie_visite * (1 - na_visite)
    for i in numba.prange(n_reste):
        s = 0.0
        na_reste_i = 1 - na_reste[i]
        for j in range(n_visite):
            s += (
                # Un bon score est un score avec une faible norme
                (1 / (1 + np.linalg.norm(vals_reste[i] - vals_visite[j])))
                # Pondération par la distance
                / (
                    (
                        1
                        + distance_haversine(
                            lats_reste[i], lons_reste[i], lats_visite[j], lons_visite[j]
                        )
                    )
                    ** alpha
                )
                # Pondération par la superficie et les NA
                * poids_visite[j]
                * na_reste_i
            )

            # Pondération par la superficie
        scores[i] = (100 * s / superficie_visitee_totale) if n_visite > 0 else 0.0
    return scores


## 1.2 -- Fonction renvoyant les régions recommandées, à l'aide des scores -----


def calculer_recommandation(
    df, dict_visite, top_n=10, alpha=1 / 3, par_pays: bool = False, n_par_pays: int = 3
):

    # Séparer les colonnes
    mask_visite = np.array(
        [
            (row[0], row[1])
            in {(p, r) for p, regions in dict_visite.items() for r in regions}
            for row in df[["name_0", "name_1"]].values
        ]
    )

    df_visite = df.iloc[mask_visite]
    df_reste = df.iloc[~mask_visite]

    # Extraire arrays NumPy
    cols_val = [
        c
        for c in df.columns
        if c
        not in [
            "name_0",
            "name_1",
            "name_2",
            "latitude",
            "longitude",
            "superficie",
            "population",
            "nombre_na",
        ]
    ]

    df_reste = (
        df_reste.assign(
            # Calcul des scores
            score_region=calculer_score_region(
                lats_visite=np.radians(df_visite["latitude"].to_numpy()),
                lons_visite=np.radians(df_visite["longitude"].to_numpy()),
                vals_visite=df_visite[cols_val].to_numpy(),
                na_visite=df_visite["nombre_na"].to_numpy(),
                superficie_visite=df_visite["superficie"].to_numpy(),
                lats_reste=np.radians(df_reste["latitude"].to_numpy()),
                lons_reste=np.radians(df_reste["longitude"].to_numpy()),
                vals_reste=df_reste[cols_val].to_numpy(),
                na_reste=df_reste["nombre_na"].to_numpy(),
                alpha=alpha,
            )
        )
        # Tri
        .sort_values("score_region", ascending=False)
    )

    # Limitation aux top pays (si souhaité)
    if par_pays:
        df_reste = (
            df_reste.groupby("name_0")
            .apply(lambda x: x.nlargest(n_par_pays, columns="score_region"))
            .reset_index(drop=False)
        )

    df_reste = (
        df_reste
        # Sélection du top des recommandations
        .nlargest(top_n, columns="score_region")
        # Sélection des colonnes
        .reset_index(drop=True)[
            ["name_0", "name_1", "latitude", "longitude", "superficie", "score_region"]
        ]
    )

    return df_reste


# 2 -- Mise en forme visuelle des recommandations -------------------------------


## 2.1 -- Layout à retour à la ligne automatique (pour les "chips" de région) --


class FlowLayout(QLayout):
    """
    Layout qui aligne ses éléments horizontalement et passe à la ligne
    automatiquement lorsque la largeur disponible est dépassée. Utilisé
    pour les "chips" de régions d'un pays, dont le nombre est variable
    et ne se prête pas à une grille de taille fixe.
    """

    def __init__(self, parent=None, marge: int = 0, espacement: int = 6):
        super().__init__(parent)
        self._items = []
        self._espacement = espacement
        if parent is not None:
            self.setContentsMargins(marge, marge, marge, marge)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._faire_layout(QRectF(0, 0, width, 0).toRect(), test_seulement=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._faire_layout(rect, test_seulement=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        taille = QSize()
        for item in self._items:
            taille = taille.expandedTo(item.minimumSize())
        marges = self.contentsMargins()
        taille += QSize(marges.left() + marges.right(), marges.top() + marges.bottom())
        return taille

    def _faire_layout(self, rect, test_seulement: bool):
        marges = self.contentsMargins()
        x = rect.x() + marges.left()
        y = rect.y() + marges.top()
        largeur_max = rect.right() - marges.right()
        hauteur_ligne = 0

        for item in self._items:
            taille_item = item.sizeHint()
            x_suivant = x + taille_item.width() + self._espacement

            if x_suivant - self._espacement > largeur_max and hauteur_ligne > 0:
                x = rect.x() + marges.left()
                y = y + hauteur_ligne + self._espacement
                x_suivant = x + taille_item.width() + self._espacement
                hauteur_ligne = 0

            if not test_seulement:
                item.setGeometry(
                    QRectF(x, y, taille_item.width(), taille_item.height()).toRect()
                )

            x = x_suivant
            hauteur_ligne = max(hauteur_ligne, taille_item.height())

        return y + hauteur_ligne - rect.y() + marges.bottom()


## 2.2 -- Thème de couleurs des cartes de recommandation -----------------------


## 2.2 -- Thème de couleurs des cartes de recommandation -----------------------


class ThemeRecommandation:
    """
    Palette de couleurs des cartes de recommandation, propre à l'onglet
    4.3. Le style clair garde une tonalité "nouvelle destination" :
    fond sauge apaisant, dégradé badge/bannière vert -> or. Le style
    sombre repose sur un fond ardoise profond et neutre, avec un
    dégradé teal -> cuivre ambré en accent, pour une ambiance chaleureuse
    sans les tons trop saturés de la version précédente. L'ombre portée
    est toujours sombre (indépendante de la couleur du texte) : une
    ombre reprenant la couleur du texte devenait blanchâtre en mode
    sombre, ce qui cassait l'effet de profondeur recherché.
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
        # Fond de carte : sauge doux en clair, ardoise profond et
        # neutre en sombre (plus élégant que le bleu-pétrole précédent).
        self.fond = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#E7F0E4",
                sombre="#8B51D6",
            )
        )
        self.texte = QColor(
            str(renvoyer_couleur_texte(style=style, couleur=self.fond.name()))
        )
        self.sous_texte = QColor(self.texte)
        self.sous_texte.setAlpha(140)

        # Dégradé badge/bannière : vert tendre -> or en clair,
        # teal profond -> cuivre ambré en sombre.
        self.badge_debut = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#8FBF8A",
                sombre="#831515",
            )
        )
        self.badge_fin = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#E8B94A",
                sombre="#70184B",
                reference=self.badge_debut.name(),
                essais=limite_essais,
            )
        )

        # Chips de région : version plus douce/claire du fond, pour
        # rester lisible sans concurrencer le dégradé du badge.
        self.fond_chip = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#D7E8CE",
                sombre="#212091",
            )
        )
        self.texte_chip = QColor(
            str(renvoyer_couleur_texte(style=style, couleur=self.fond_chip.name()))
        )

        # Ombre portée : toujours sombre, quel que soit le style —
        # contrairement à une ombre dérivée de `self.texte`, qui
        # devient claire (donc peu naturelle) en mode sombre.
        self.ombre = QColor("#000000")
        self.ombre.setAlpha(70 if style == 1 else 130)


## 2.3 -- Bannière de titre ----------------------------------------------------


def creer_entete_recommandations(texte: str, theme: ThemeRecommandation) -> QLabel:
    """Bannière arrondie en dégradé, dans le même esprit que les titres
    de section de l'onglet 4.2 (`TitreClassement`)."""
    label = QLabel(texte)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setWordWrap(True)
    label.setStyleSheet(f"""
        QLabel {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {theme.badge_debut.name()}, stop:1 {theme.badge_fin.name()}
            );
            color: #FFFFFF;
            font-weight: 600;
            font-size: 15px;
            border-radius: 14px;
            padding: 10px 16px;
        }}
        """)
    return label


## 2.4 -- Chip de région ---------------------------------------------------------


def creer_chip_region(texte: str, theme: ThemeRecommandation) -> QLabel:
    """Petite pastille arrondie pour afficher le nom d'une région."""
    label = QLabel(texte)
    label.setStyleSheet(f"""
        QLabel {{
            background-color: {theme.fond_chip.name()};
            color: {theme.texte_chip.name()};
            border-radius: 9px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 500;
        }}
        """)
    label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    return label


## 2.5 -- Carte "pays" (mode groupé) ---------------------------------------------


class CarteRecommandationPays(QWidget):
    """
    Carte pour un pays recommandé (mode groupé par pays) : nom du pays
    (avec emoji) en en-tête, suivi des régions recommandées sous forme
    de "chips" qui s'enchaînent et passent à la ligne automatiquement.
    """

    def __init__(
        self, pays_nom: str, emoji: str, regions: list[str], style, parent=None
    ):
        super().__init__(parent)
        self.theme = style

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(20)
        self._ombre_effet.setOffset(0, 5)
        self._ombre_effet.setColor(self.theme.ombre)
        self.setGraphicsEffect(self._ombre_effet)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(8)

        entete = QLabel(f"{emoji} {pays_nom} {emoji}".strip())
        entete.setStyleSheet(
            f"color: {self.theme.texte.name()}; font-weight: 600; "
            f"font-size: 14px; background: transparent;"
        )
        layout.addWidget(entete)

        conteneur_chips = QWidget()
        conteneur_chips.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        flow = FlowLayout(conteneur_chips, marge=0, espacement=6)
        for region in regions:
            flow.addWidget(creer_chip_region(region, self.theme))
        layout.addWidget(conteneur_chips)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(0, 0, self.width(), self.height()).adjusted(1, 1, -1, -1)
        rayon = min(16, min(self.width(), self.height()) * 0.1)
        chemin = QPainterPath()
        chemin.addRoundedRect(rect, rayon, rayon)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.theme.fond)
        painter.drawPath(chemin)

        super().paintEvent(event)


## 2.6 -- Carte "ligne de classement" (mode non groupé) -------------------------


class CarteRecommandationSimple(QWidget):
    """
    Carte compacte pour une ligne de recommandation (mode non groupé) :
    badge de rang en dégradé, pays (avec emoji), région recommandée.
    Reprend le vocabulaire visuel de `CarteClassementPays` (onglet 4.2).
    """

    def __init__(
        self, rang: int, pays_nom: str, emoji: str, region: str, style, parent=None
    ):
        super().__init__(parent)
        self.theme = style
        self.rang = str(rang)
        self.pays_nom = pays_nom
        self.emoji = emoji
        self.region = region

        self.setMinimumSize(90, 100)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(20)
        self._ombre_effet.setOffset(0, 5)
        self._ombre_effet.setColor(self.theme.ombre)
        self.setGraphicsEffect(self._ombre_effet)

        self.police_principale = Podium._trouver_police_disponible(
            ["CormorantGaramond", "Fredoka", "Quicksand", "Century Gothic", "Segoe UI"]
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()
        rect = QRectF(0, 0, w, h).adjusted(2, 2, -2, -2)
        rayon = min(18, min(w, h) * 0.14)
        chemin = QPainterPath()
        chemin.addRoundedRect(rect, rayon, rayon)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.theme.fond)
        painter.drawPath(chemin)
        painter.setClipPath(chemin)

        cote = min(w, h)

        # --- badge de rang ---
        rayon_badge = cote * 0.16
        centre_y = h * 0.22
        rect_badge = QRectF(
            w / 2 - rayon_badge,
            centre_y - rayon_badge,
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
        painter.drawText(rect_badge, Qt.AlignmentFlag.AlignCenter, self.rang)

        # --- pays ---
        police_pays = QFont(
            self.police_principale, max(8, int(cote * 0.085)), QFont.Weight.DemiBold
        )
        painter.setFont(police_pays)
        painter.setPen(self.theme.texte)
        rect_pays = QRectF(w * 0.05, h * 0.42, w * 0.9, h * 0.26)
        self._dessiner_texte_wrap(
            painter, rect_pays, f"{self.emoji} {self.pays_nom}".strip()
        )

        # --- région ---
        police_region = QFont(self.police_principale, max(7, int(cote * 0.07)))
        painter.setFont(police_region)
        painter.setPen(self.theme.sous_texte)
        rect_region = QRectF(w * 0.05, h * 0.7, w * 0.9, h * 0.26)
        self._dessiner_texte_wrap(painter, rect_region, self.region)

    def _dessiner_texte_wrap(self, painter, rect, texte):
        """Découpe `texte` en lignes qui tiennent dans la largeur de `rect`
        (même logique que `CarteClassementPays`, onglet 4.2)."""
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


# 3 -- Classe de calcul du tableau de recommandations --------------------------


class WorkerRecommandation(QObject):
    finished = pyqtSignal(object)  # Signal pour retourner le résultat

    def __init__(
        self,
        top_n: int,
        alpha: float,
        df,
        dict_visite,
        par_pays: bool,
        n_par_pays: int,
    ):
        super().__init__()
        self.df = df
        self.dict_visite = dict_visite

        self.top_n = top_n
        self.alpha = alpha
        self.par_pays = par_pays
        self.n_par_pays = n_par_pays

    def calculer(self):
        """Méthode exécutée dans le thread."""

        df = (
            calculer_recommandation(
                df=self.df,
                dict_visite=self.dict_visite,
                top_n=self.top_n,
                alpha=self.alpha,
                par_pays=self.par_pays,
                n_par_pays=self.n_par_pays,
            )
            if self.dict_visite != {}
            else None
        )
        self.finished.emit(df)  # Émet le résultat


# 4 -- Classe de recommandations (déclenchement des calcul et affichage) -------


class PaysAVisiter(QWidget):

    def __init__(
        self,
        constantes,
        table_superficie,
        fct_traduire,
        parent=None,
    ):
        super().__init__(parent)

        # Données
        self.df_caracteristiques = constantes.df_caracteristiques_pays
        self.table_superficie = table_superficie
        self.n_par_pays = 3
        self.recommandations_par_ligne = 3
        self.alpha = constantes.parametres_application.get("coeff_distance", 0.05)
        self.pays_traductions = constantes.pays_differentes_langues
        self.emojis_pays = constantes.emojis_pays
        self.fonction_traduire = fct_traduire

        # Paramètres utilisateur
        self.langue = "français"
        self.dict_voyages = {}
        self.recommandations_par_pays = True
        self.df = None

        # Thème par défaut (clair) — mis à jour via `set_bouton_recommandation`
        # lorsque le widget parent branche cet onglet sur le système de
        # thème clair/sombre de l'appli.
        self.style = ThemeRecommandation(
            style=1,
            teinte=[i / 360 for i in range(0, 360, 45)],
            nuances={
                "min_luminosite": 0.8,
                "max_luminosite": 0.95,
                "min_saturation": 0.2,
                "max_saturation": 0.4,
            },
        )

        layout = QVBoxLayout()
        # Bouton de lancement
        self.bouton_recommandations = QPushButton()

        layout.addWidget(self.bouton_recommandations)
        self.bouton_recommandations.clicked.connect(self.calculer_prochaine_destination)

        # Scroll area pour les recommandations
        scroll_widget = QWidget()  # widget qui contiendra le layout des recommandations
        self.corps_recommandations = QVBoxLayout()  # layout pour les cartes
        scroll_widget.setLayout(self.corps_recommandations)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(
            True
        )  # permet au scroll de s’adapter à la taille
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Nombre de recommandations
        self.recommandations_nb = QSpinBox()
        recommandations_layout = QHBoxLayout()
        self.recommandations_nb.setMinimum(5)
        self.recommandations_nb.setMaximum(100)
        self.recommandations_nb.setSingleStep(1)
        recommandations_layout.addStretch()
        recommandations_layout.addWidget(self.recommandations_nb)
        layout.addLayout(recommandations_layout)

        self.setLayout(layout)

    def calculer_prochaine_destination(self):

        vider_layout(self.corps_recommandations)

        # Liste des destinations
        destinations_temp = voyages_vers_destinations(self.dict_voyages)

        # Copie du dictionnaire pour éviter tout problème
        dict_temp = copy.deepcopy(destinations_temp.get("region"))

        for pays, groupe in self.table_superficie[
            # Ajout des régions des départements
            self.table_superficie.apply(
                lambda row: (row["name_0"], row["name_2"])
                in {
                    (p, r)
                    for p, dep in (destinations_temp.get("dep") or {}).items()
                    for r in dep
                },
                axis=1,
            )
        ].groupby("name_0"):
            regions = groupe["name_1"].tolist()
            if pays in dict_temp:
                # Ajouter les nouvelles régions sans doublons
                dict_temp[pays] = list(set(dict_temp[pays]) | set(regions))
            else:
                # Ajouter le pays s'il n'existait pas encore
                dict_temp[pays] = regions

        self.thread_temp = QThread()
        self.worker_temp = WorkerRecommandation(
            df=self.df_caracteristiques,
            alpha=self.alpha,
            top_n=self.get_recommandations_nb(),
            par_pays=self.get_recommandations_par_pays(),
            dict_visite={
                k: list(dict.fromkeys(v)) for k, v in dict_temp.items() if v is not None
            },
            n_par_pays=self.n_par_pays,
        )
        self.worker_temp.moveToThread(self.thread_temp)
        self.thread_temp.started.connect(self.worker_temp.calculer)
        self.worker_temp.finished.connect(self.on_calcul_fini)
        self.worker_temp.finished.connect(self.thread_temp.quit)
        self.worker_temp.finished.connect(self.worker_temp.deleteLater)
        self.thread_temp.finished.connect(self.thread_temp.deleteLater)
        self.thread_temp.start()

    def on_calcul_fini(self, df):
        """Méthode appelée quand le calcul est terminé."""
        self.df = df
        self.afficher_recommandation()

    def afficher_recommandation(self):

        # Affichage
        self.vider_recommandations()
        if self.df is None:
            return

        self.corps_recommandations.addWidget(
            creer_entete_recommandations(
                texte=self.fonction_traduire("titre_recommandations"),
                theme=self.style,
            )
        )
        self.corps_recommandations.addWidget(QLabel(""))

        if len(self.df) > 0:

            if not self.get_recommandations_par_pays():

                modulo = self.recommandations_par_ligne
                for i, ligne in self.df.iterrows():

                    if i % modulo == 0:
                        layout_temp = QGridLayout()
                        layout_temp.setSpacing(10)
                        for c in range(modulo):
                            layout_temp.setColumnStretch(c, 1)

                    pays_traduit = self.pays_traductions.get(ligne["name_0"], {}).get(
                        self.langue, ligne["name_0"]
                    )

                    layout_temp.addWidget(
                        CarteRecommandationSimple(
                            rang=i + 1,
                            pays_nom=pays_traduit,
                            emoji=self.emojis_pays.get(ligne["name_0"], ""),
                            region=str(ligne["name_1"]),
                            style=self.style,
                        ),
                        0,
                        i % modulo,
                    )

                    if (i + 1) % modulo == 0 or len(self.df) == (i + 1):
                        self.corps_recommandations.addLayout(layout_temp)
                        self.corps_recommandations.addWidget(QLabel(""))

                self.corps_recommandations.addStretch()

            else:

                for pays in list(self.df["name_0"].unique()):

                    pays_traduit = self.pays_traductions.get(pays, {}).get(
                        self.langue, pays
                    )
                    regions = list(self.df.loc[self.df["name_0"] == pays, "name_1"])

                    self.corps_recommandations.addWidget(
                        CarteRecommandationPays(
                            pays_nom=pays_traduit,
                            emoji=self.emojis_pays.get(pays, ""),
                            regions=regions,
                            style=self.style,
                        )
                    )
                    self.corps_recommandations.addSpacerItem(
                        QSpacerItem(
                            0, 5, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
                        )
                    )

                self.corps_recommandations.addStretch()

    def set_dicts_granu(self, dict_nv: dict):
        """Permet de mettre à jour les sélections de destinations."""
        self.dict_voyages = dict_nv
        if self.dict_voyages == {}:
            self.df = None
            self.afficher_recommandation()

    def set_langue(self, langue: str):
        self.langue = langue
        self.bouton_recommandations.setText(
            self.fonction_traduire("bouton_recommandations")
        )
        self.bouton_recommandations.setToolTip(
            self.fonction_traduire("recommandation_passeport")
        )
        self.recommandations_nb.setSuffix(
            self.fonction_traduire("recommandations_nb", prefixe=" ")
        )
        self.afficher_recommandation()

    def set_bouton_recommandation(self, style, teinte, nuances):

        # Thème des cartes de recommandation, aligné sur le style
        # clair/sombre courant de l'appli (mêmes paramètres que le
        # bouton, réutilisés pour cohérence visuelle).
        self.style = ThemeRecommandation(
            style=style, teinte=teinte, nuances=nuances, limite_essais=20
        )

        self.bouton_recommandations.setStyleSheet(
            style_bouton_recommandation(style=style, teinte=teinte, nuances=nuances)
        )

        self.afficher_recommandation()

    def get_recommandations_par_pays(self):
        return self.recommandations_par_pays

    def set_recommandations_par_pays(self, val: bool):
        self.recommandations_par_pays = val

    def vider_recommandations(self):
        vider_layout(self.corps_recommandations)
        self.corps_recommandations.update()

    def get_recommandations_nb(self):
        return self.recommandations_nb.value()

    def set_recommandations_nb(self, val: int):
        self.recommandations_nb.setValue(val)

    def initialiser_onglet(self, **kwargs):
        self.vider_recommandations()

        # Recommandations
        recommandations_nb = kwargs.get("recommandations_nb", 20)
        self.set_recommandations_nb(val=recommandations_nb)
