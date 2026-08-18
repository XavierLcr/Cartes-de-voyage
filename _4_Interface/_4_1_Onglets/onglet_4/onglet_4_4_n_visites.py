################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.4 – Pays visités le plus grand nombre de fois                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, textwrap, math
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QFrame,
)
from PyQt6.QtCore import (
    Qt,
    QRectF,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
    QTimer,
)
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QPixmap,
    QPainterPath,
    QLinearGradient,
    QFont,
    QFontMetrics,
)

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    vider_layout,
)
from _0_Utilitaires._0_7_fonctions_voyages import (
    compter_occurences_destinations_une_granu,
)

# 1 -- Fonctions de création du classement des pays ----------------------------


## 1.1 -- Fonction de comptage par pays ----------------------------------------


def compter_voyages_par_pays(
    dictionnaire_voyages: dict, traductions: dict, langue: str
):

    return (
        compter_occurences_destinations_une_granu(
            dict_voyages=dictionnaire_voyages, granu=0
        )
        .assign(
            pays_traduction=lambda x: x["pays"].apply(
                lambda y: traductions.get(y, {}).get(langue, y)
            )
        )
        .sort_values(
            by=["N", "pays_traduction"], ascending=(False, True), inplace=False
        )
        .reset_index(drop=True, inplace=False)
    )


## 1.2 -- Fonction de limite du nombre de pays ---------------------------------


def limiter_nombre_pays(df: pd.DataFrame, n: int, type: bool, agreger: bool):

    # Récupération des paramètres
    df_temp = df.copy()
    n = max(n, 2)

    # Conservation du top pays
    if type and len(df_temp) > n:
        df_temp = df_temp[df_temp["N"] >= df_temp.iloc[n - 1]["N"]]
    else:
        df_temp = df_temp.head(n)

    if agreger and len(df_temp) > n + 1:
        min_n = df_temp["N"].min()
        df_temp = (
            pd.concat(
                [
                    # Partie agrégée de la table
                    df_temp[df_temp["N"] == min_n]
                    .groupby("N", as_index=False)
                    .agg({"pays": ", ".join, "pays_traduction": ", ".join}),
                    # Partie non agrégée
                    df_temp[df_temp["N"] > min_n],
                ],
                ignore_index=True,
            )
            # Tri des valeurs
            .sort_values(by=["N"], ascending=False)
            # Mise en forme du texte
            .assign(
                pays_traduction=lambda x: x["pays_traduction"].apply(
                    lambda y: textwrap.fill(y, width=20)
                )
            )
        )

    # Renvoi
    return df_temp


# 2 -- Classes du graphique ----------------------------------------------------


## 2.1 -- Résolution du chemin d'un drapeau ------------------------------------


def resoudre_chemin_drapeau(dossier: str, nom_pays: str) -> str:
    chemin_drapeau = os.path.join(dossier, f"{nom_pays}.png")
    if os.path.exists(chemin_drapeau):
        return chemin_drapeau
    else:
        return os.path.join(dossier, "United Nations.png")


## 2.2 -- Mât + drapeau animé --------------------------------------------------


class _MatPavillon(QWidget):
    """Un mât avec un drapeau qui "monte" jusqu'à une hauteur proportionnelle
    à sa valeur (comme une levée de drapeau de cérémonie), puis ondule
    doucement comme un vrai tissu au vent (bandes verticales décalées selon
    une sinusoïde, amplitude nulle côté mât et maximale côté libre)."""

    # Réglages de l'ondulation, modifiables si besoin
    N_BANDES = 26
    AMPLITUDE_RATIO = 0.07  # proportion de la hauteur du drapeau
    N_ONDES = 1.6  # nombre de "vagues" visibles sur la largeur
    VITESSE_ONDULATION = 2.2  # vitesse d'animation (multiplicateur de phase)

    def __init__(
        self,
        chemin_image: str | None,
        couleur_repli: str,
        ratio: float,
        hauteur_mat: float,
        largeur: float = 92,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.ratio = max(0.0, min(1.0, ratio))
        self.hauteur_mat = hauteur_mat
        self.largeur = largeur
        self.couleur_repli = QColor(couleur_repli)
        self._hauteur_actuelle = 0.0
        self._phase = 0.0

        self.pixmap = None
        self._pixmap_haute_res = None
        if chemin_image:
            pm = QPixmap(chemin_image)
            if not pm.isNull():
                self.pixmap = pm

        self.setFixedSize(int(largeur), int(hauteur_mat))
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self._timer_flottement = QTimer(self)
        self._timer_flottement.setInterval(45)
        self._timer_flottement.timeout.connect(self._avancer_flottement)

    # Géométrie interne, recalculée à chaque paint -------------------------
    def _geometrie(self):
        pole_x = 16
        pole_top = 8
        pole_bottom = self.hauteur_mat - 4
        flag_w = self.largeur - pole_x - 12
        flag_h = flag_w * 0.62
        plage_max = max((pole_bottom - pole_top) - flag_h, 1)
        return pole_x, pole_top, pole_bottom, flag_w, flag_h, plage_max

    # Animation de "hissage" -------------------------------------------------
    def get_hauteur(self):
        return self._hauteur_actuelle

    def set_hauteur(self, v):
        self._hauteur_actuelle = v
        self.update()

    hauteur = pyqtProperty(float, get_hauteur, set_hauteur)

    def lancer_animation(self, duree_ms: int = 900, delai_ms: int = 0):
        _, _, _, _, _, plage_max = self._geometrie()

        def demarrer():
            self.anim = QPropertyAnimation(self, b"hauteur")
            self.anim.setDuration(duree_ms)
            self.anim.setStartValue(0.0)
            self.anim.setEndValue(self.ratio * plage_max)
            self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.anim.start()
            self._timer_flottement.start()

        if delai_ms:
            # QTimer parenté à self : détruit automatiquement en même temps
            # que le widget, contrairement à QTimer.singleShot qui n'est
            # rattaché à rien et peut déclencher demarrer() sur un widget
            # déjà supprimé.
            self._timer_hissage = QTimer(self)
            self._timer_hissage.setSingleShot(True)
            self._timer_hissage.timeout.connect(demarrer)
            self._timer_hissage.start(delai_ms)
        else:
            demarrer()

    def _avancer_flottement(self):
        self._phase += 0.12
        self.update()

    # Dessin du drapeau, en bandes verticales ondulées -----------------------
    def _dessiner_drapeau_ondule(self, painter: QPainter, rect_drapeau: QRectF):
        x0 = rect_drapeau.left()
        y0 = rect_drapeau.top()
        w = rect_drapeau.width()
        h = rect_drapeau.height()

        n_bandes = self.N_BANDES
        largeur_bande = w / n_bandes
        amplitude_max = h * self.AMPLITUDE_RATIO

        if self.pixmap is not None:
            # On travaille sur une version un peu suréchantillonnée pour
            # limiter les artefacts de découpe en bandes fines.
            if self._pixmap_haute_res is None or self._pixmap_haute_res.width() < w * 2:
                self._pixmap_haute_res = self.pixmap.scaled(
                    max(int(w * 2), 1),
                    max(int(h * 2), 1),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            pm = self._pixmap_haute_res
            source_w = pm.width() / n_bandes

            for i in range(n_bandes):
                t = i / (n_bandes - 1)  # 0 = côté mât, 1 = côté libre
                amplitude = amplitude_max * t
                decalage = amplitude * math.sin(
                    t * 2 * math.pi * self.N_ONDES
                    - self._phase * self.VITESSE_ONDULATION
                )
                dest = QRectF(
                    x0 + i * largeur_bande,
                    y0 + decalage,
                    largeur_bande + 0.6,  # léger recouvrement anti-liseré
                    h,
                )
                src = QRectF(i * source_w, 0, source_w, pm.height())
                painter.drawPixmap(dest, pm, src)
        else:
            # Pas d'image : on ondule un aplat de couleur avec un contour
            # continu plutôt que des bandes.
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self.couleur_repli)
            chemin = QPainterPath()
            n_pts = 24
            points_haut = []
            points_bas = []
            for i in range(n_pts + 1):
                t = i / n_pts
                amplitude = amplitude_max * t
                decalage = amplitude * math.sin(
                    t * 2 * math.pi * self.N_ONDES
                    - self._phase * self.VITESSE_ONDULATION
                )
                points_haut.append((x0 + t * w, y0 + decalage))
                points_bas.append((x0 + t * w, y0 + h + decalage))
            chemin.moveTo(*points_haut[0])
            for p in points_haut[1:]:
                chemin.lineTo(*p)
            for p in reversed(points_bas):
                chemin.lineTo(*p)
            chemin.closeSubpath()
            painter.drawPath(chemin)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        pole_x, pole_top, pole_bottom, flag_w, flag_h, _ = self._geometrie()

        # Mât
        gradient_mat = QLinearGradient(pole_x - 2, 0, pole_x + 2, 0)
        gradient_mat.setColorAt(0.0, QColor("#C7C7C7"))
        gradient_mat.setColorAt(1.0, QColor("#8E8E8E"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient_mat)
        painter.drawRoundedRect(
            QRectF(pole_x - 2, pole_top, 4, pole_bottom - pole_top), 2, 2
        )

        # Pommeau
        painter.setBrush(QColor("#D8B24A"))
        painter.drawEllipse(QRectF(pole_x - 4, pole_top - 7, 8, 8))

        # Socle
        painter.setBrush(QColor("#B5B5B5"))
        painter.drawRoundedRect(QRectF(pole_x - 10, pole_bottom - 2, 20, 5), 2, 2)

        # Position (fixe désormais) du cadre du drapeau selon la hauteur hissée
        flag_bottom_y = pole_bottom - self._hauteur_actuelle
        flag_top_y = flag_bottom_y - flag_h
        rect_drapeau = QRectF(pole_x, flag_top_y, flag_w, flag_h)

        if self._hauteur_actuelle > 1:
            # Attaches mât/drapeau (sur la position de référence, non ondulée)
            painter.setPen(QColor("#8E8E8E"))
            painter.drawLine(
                int(pole_x - 1),
                int(flag_top_y + 3),
                int(pole_x + 3),
                int(flag_top_y + 3),
            )
            painter.drawLine(
                int(pole_x - 1),
                int(flag_bottom_y - 3),
                int(pole_x + 3),
                int(flag_bottom_y - 3),
            )

            # La zone de clip est élargie verticalement pour laisser passer
            # l'amplitude de l'ondulation sans rogner le haut/bas du drapeau.
            amplitude_max = flag_h * self.AMPLITUDE_RATIO
            zone_clip = QRectF(
                rect_drapeau.left() - 1,
                rect_drapeau.top() - amplitude_max - 1,
                rect_drapeau.width() + 2,
                rect_drapeau.height() + 2 * amplitude_max + 2,
            )
            chemin = QPainterPath()
            chemin.addRoundedRect(zone_clip, 2, 2)
            painter.setClipPath(chemin)

            self._dessiner_drapeau_ondule(painter, rect_drapeau)

            painter.setClipping(False)

        painter.end()


## 2.3 -- Libellés d'une carte pays (nom + valeur) ------------------------------


def _creer_label_nom(texte: str, largeur: int) -> QLabel:
    label = QLabel(texte)
    label.setStyleSheet("font-size: 11px; font-weight: 600;")
    label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
    label.setFixedWidth(largeur)
    label.setWordWrap(True)
    return label


def _creer_label_valeur(valeur: float, voyage: str, voyages: str) -> QLabel:
    label = QLabel(f"{int(valeur)} {voyage if valeur <= 1 else voyages}")
    label.setStyleSheet("font-size: 10px; color: #888;")
    label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
    return label


## 2.4 -- Widget principal : titre + rangée de mâts ----------------------------


class LeveeDrapeaux(QWidget):
    """Rangée structurée de mâts, tous de même hauteur, où le drapeau de
    chaque pays monte jusqu'à une hauteur proportionnelle au nombre de
    voyages — la cérémonie de levée de drapeaux comme classement.

    Usage :
        widget = LeveeDrapeaux(dossier_drapeaux="/chemin/vers/drapeaux", titre="Pays les plus visités")
        widget.set_donnees(labels=["France", "Italie", "Espagne"], valeurs=[12, 9, 4])
    """

    def __init__(
        self,
        dossier_drapeaux: str,
        fct_traduction,
        hauteur_mat: float = 190,
        largeur_mat: float = 92,
        palette_repli: list | None = None,
        couleur_accent: str = "#4A90A4",
        parent=None,
    ):
        super().__init__(parent=parent)
        self.fct_traduction = fct_traduction
        self.dossier_drapeaux = dossier_drapeaux
        self.hauteur_mat = hauteur_mat
        self.largeur_mat = largeur_mat
        self.couleur_accent = couleur_accent
        self.palette_repli = palette_repli or [
            "#7DC8E8",
            "#E15759",
            "#59A14F",
            "#B07AA1",
            "#EDC948",
            "#76B7B2",
        ]

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(12, 12, 12, 12)
        self.layout_principal.setSpacing(14)

        self.label_titre = None
        titre = self.fct_traduction("titre_graphique_n_voyages")
        if titre:
            conteneur_titre = QWidget()
            conteneur_titre.setContentsMargins(0, 0, 0, 0)
            layout_titre = QVBoxLayout(conteneur_titre)
            layout_titre.setContentsMargins(0, 0, 0, 0)
            layout_titre.setSpacing(2)
            layout_titre.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            texte_titre = titre.upper()

            self.label_titre = QLabel(texte_titre)
            police_titre = self.label_titre.font()
            police_titre.setPointSize(12)
            police_titre.setWeight(QFont.Weight.DemiBold)
            police_titre.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 115)
            self.label_titre.setFont(police_titre)
            self.label_titre.setStyleSheet("color: #4A5A66; margin: 0px; padding: 0px;")
            self.label_titre.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.label_titre.setContentsMargins(0, 0, 0, 0)

            # On force la hauteur du label à celle du texte réel, au lieu de
            # laisser Qt utiliser le "line height" natif de la police (souvent
            # bien plus grand que le texte affiché, d'où le grand espace visible
            # avant la barre).
            metrics_titre = QFontMetrics(police_titre)
            self.label_titre.setFixedHeight(
                metrics_titre.boundingRect(texte_titre).height()
            )

            ligne_titre = QFrame()
            ligne_titre.setFixedSize(46, 3)
            ligne_titre.setStyleSheet(
                f"background-color: {self.couleur_accent}; border-radius: 1px;"
            )

            layout_titre.addWidget(self.label_titre)
            layout_titre.addWidget(ligne_titre, alignment=Qt.AlignmentFlag.AlignHCenter)

            self.layout_principal.addWidget(
                conteneur_titre, alignment=Qt.AlignmentFlag.AlignHCenter
            )

        self.conteneur = QWidget()
        self.layout_rangee = QGridLayout(self.conteneur)
        self.layout_rangee.setHorizontalSpacing(18)
        self.layout_rangee.setVerticalSpacing(4)
        # Chaque ligne (mâts / noms / valeurs) se dimensionne indépendamment :
        # un nom sur deux lignes n'agrandit que la ligne 1, jamais la ligne 0
        # (les mâts), donc les drapeaux restent alignés entre eux.
        self.layout_rangee.setRowStretch(0, 0)
        self.layout_principal.addWidget(
            self.conteneur, alignment=Qt.AlignmentFlag.AlignHCenter
        )

    def _vider(self):
        while self.layout_rangee.count():
            item = self.layout_rangee.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

    def set_donnees(self, labels: list, valeurs: list, traductions: list):
        """labels : noms de pays tels qu'utilisés dans le dossier de
        drapeaux. valeurs déjà triées par ordre décroissant (rang 1 en
        premier)."""

        self._vider()
        if len(valeurs) == 0:
            return

        valeur_max = max(valeurs)

        for i, (label, valeur, traduction) in enumerate(
            zip(labels, valeurs, traductions)
        ):
            ratio = valeur / valeur_max if valeur_max > 0 else 0

            mat_temp = _MatPavillon(
                chemin_image=resoudre_chemin_drapeau(self.dossier_drapeaux, str(label)),
                couleur_repli=self.palette_repli[i % len(self.palette_repli)],
                ratio=ratio,
                hauteur_mat=self.hauteur_mat,
                largeur=self.largeur_mat,
            )
            label_nom = _creer_label_nom(
                str(traduction), largeur=int(self.largeur_mat + 10)
            )
            label_valeur = _creer_label_valeur(
                valeur=valeur,
                voyage=self.fct_traduction("voyage"),
                voyages=self.fct_traduction("voyages"),
            )

            self.layout_rangee.addWidget(
                mat_temp,
                0,
                i,
                alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
            )
            self.layout_rangee.addWidget(label_nom, 1, i)
            self.layout_rangee.addWidget(label_valeur, 2, i)

            mat_temp.lancer_animation(delai_ms=i * 200)


# 3 -- Classe principale -------------------------------------------------------


class PaysLesPlusVisites(QWidget):

    def __init__(self, constantes, fct_traduction, parent=None):

        super().__init__(parent=parent)

        # Variables globales
        self.langue = "français"
        self.fct_traduction = fct_traduction
        self.voyages = {}
        self.n_pays = 5
        self.n_pays_limite_type = True
        self.pays_trad = constantes.pays_differentes_langues
        self.direction_donnees_drapeaux = constantes.direction_donnees_drapeaux
        self.agreger = True

        # Style par défaut
        self.style = 1
        self.teinte = None
        self.nuances = {}

        self.layout = QVBoxLayout(self)

    def set_langue(self, langue: str):
        self.langue = langue
        self.creer_graphique()

    def set_voyages(self, voyages: dict):
        self.voyages = voyages
        self.creer_graphique()

    def set_style(self, style, teinte, nuances):
        self.style = style
        self.teinte = teinte
        self.nuances = nuances
        self.creer_graphique()

    def creer_graphique(self):
        vider_layout(layout=self.layout)

        if self.voyages:
            df_temp = compter_voyages_par_pays(
                self.voyages, traductions=self.pays_trad, langue=self.langue
            ).pipe(
                limiter_nombre_pays,
                n=self.n_pays,
                type=self.n_pays_limite_type,
                agreger=self.agreger,
            )

            widget_temp = LeveeDrapeaux(
                dossier_drapeaux=self.direction_donnees_drapeaux,
                fct_traduction=self.fct_traduction,
            )
            widget_temp.set_donnees(
                labels=df_temp["pays"].to_list(),
                valeurs=df_temp["N"].to_list(),
                traductions=df_temp["pays_traduction"].to_list(),
            )
            self.layout.addWidget(widget_temp)
