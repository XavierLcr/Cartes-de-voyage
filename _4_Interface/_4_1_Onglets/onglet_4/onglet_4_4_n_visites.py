################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.4 – Pays visités le plus grand nombre de fois                       #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, textwrap, math, unicodedata
import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import (
    Qt,
    QRectF,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
    QTimer,
)
from PyQt6.QtGui import QPainter, QColor, QPixmap, QPainterPath, QLinearGradient

from _0_Utilitaires._0_2_fonctions_graphiques import (
    hex_to_rgb,
    rgb_to_hex,
    generer_couleur_aleatoire_hex,
)
from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    vider_layout,
    conteneur_graphique_simple,
)
from _0_Utilitaires._0_7_fonctions_voyages import (
    compter_occurences_destinations_une_granu,
)
from _0_Utilitaires._0_8_plot_diagramme_barres import plot_diagramme_barre

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
    à sa valeur (comme une levée de drapeau de cérémonie), puis se met à
    flotter doucement (léger balancement vertical continu)."""

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
            self.anim.finished.connect(self._timer_flottement.start)
            self.anim.start()

        if delai_ms:
            QTimer.singleShot(delai_ms, demarrer)
        else:
            demarrer()

    def _avancer_flottement(self):
        self._phase += 0.12
        self.update()

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

        # Position du drapeau (léger flottement vertical une fois hissé)
        bob = math.sin(self._phase) * 2.2 if self._timer_flottement.isActive() else 0.0
        flag_bottom_y = pole_bottom - self._hauteur_actuelle + bob
        flag_top_y = flag_bottom_y - flag_h
        rect_drapeau = QRectF(pole_x, flag_top_y, flag_w, flag_h)

        if self._hauteur_actuelle > 1:
            # Attaches mât/drapeau
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

            chemin = QPainterPath()
            chemin.addRoundedRect(rect_drapeau, 2, 2)
            painter.setClipPath(chemin)

            if self.pixmap is not None:
                pm = self.pixmap.scaled(
                    int(flag_w),
                    int(flag_h),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
                painter.drawPixmap(
                    int(rect_drapeau.left() + (flag_w - pm.width()) / 2),
                    int(rect_drapeau.top() + (flag_h - pm.height()) / 2),
                    pm,
                )
            else:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(self.couleur_repli)
                painter.drawRect(rect_drapeau)

            painter.setClipping(False)

        painter.end()


## 2.3 -- Carte : mât + libellés -----------------------------------------------


class _CartePavillon(QWidget):
    def __init__(self, label: str, valeur: float, mat: _MatPavillon, parent=None):
        super().__init__(parent=parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
        )

        layout.addWidget(mat, alignment=Qt.AlignmentFlag.AlignHCenter)

        label_nom = QLabel(label)
        label_nom.setStyleSheet("font-size: 11px; font-weight: 600;")
        label_nom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_nom.setFixedWidth(mat.largeur + 10)
        label_nom.setWordWrap(True)

        label_valeur = QLabel(f"{int(valeur)} voyage{'s' if valeur > 1 else ''}")
        label_valeur.setStyleSheet("font-size: 10px; color: #888;")
        label_valeur.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label_nom)
        layout.addWidget(label_valeur)


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
        titre: str = "",
        hauteur_mat: float = 190,
        largeur_mat: float = 92,
        palette_repli: list | None = None,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.dossier_drapeaux = dossier_drapeaux
        self.hauteur_mat = hauteur_mat
        self.largeur_mat = largeur_mat
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
        self.layout_principal.setSpacing(10)

        self.label_titre = None
        if titre:
            self.label_titre = QLabel(titre)
            self.label_titre.setStyleSheet("font-weight: 600; font-size: 14px;")
            self.layout_principal.addWidget(self.label_titre)

        self.conteneur = QWidget()
        self.layout_rangee = QHBoxLayout(self.conteneur)
        self.layout_rangee.setSpacing(18)
        self.layout_rangee.setAlignment(
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft
        )
        self.layout_principal.addWidget(self.conteneur)

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

            mat = _MatPavillon(
                chemin_image=resoudre_chemin_drapeau(self.dossier_drapeaux, str(label)),
                couleur_repli=self.palette_repli[i % len(self.palette_repli)],
                ratio=ratio,
                hauteur_mat=self.hauteur_mat,
                largeur=self.largeur_mat,
            )
            carte = _CartePavillon(label=str(traduction), valeur=valeur, mat=mat)
            self.layout_rangee.addWidget(carte)

            mat.lancer_animation(delai_ms=i * 0)
            # mat.lancer_animation(delai_ms=i * 150)


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
        self.couleur = "#ADCEDB"

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

            widget = LeveeDrapeaux(
                dossier_drapeaux=self.direction_donnees_drapeaux,
                titre=self.fct_traduction("titre_graphique_n_voyages"),
            )
            widget.set_donnees(
                labels=df_temp["pays"].to_list(),
                valeurs=df_temp["N"].to_list(),
                traductions=df_temp["pays_traduction"].to_list(),
            )
            self.layout.addWidget(widget)
