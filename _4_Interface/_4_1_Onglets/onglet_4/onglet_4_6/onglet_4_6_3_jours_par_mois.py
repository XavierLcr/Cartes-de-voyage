################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6                                #
# Onglet 4.6.3 – Jours voyagés par mois                                        #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Optional, Sequence, Tuple

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    Qt,
    QPointF,
    pyqtProperty,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
)
from PyQt6.QtWidgets import QSizePolicy, QWidget, QToolTip

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    ombre_onglet_4_6,
    _QColor_avec_alpha,
)
from _0_Utilitaires._0_2_fonctions_graphiques import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
)
from _4_Interface._4_3_Icones._4_3_01_soleil_souriant import _dessiner_icone_soleil
from _4_Interface._4_3_Icones._4_3_02_flocon_neige import _dessiner_icone_flocon
from _4_Interface._4_3_Icones._4_3_03_feuille_automne import _dessiner_icone_feuille
from _4_Interface._4_3_Icones._4_3_04_jeune_pousse import _dessiner_icone_pousse

# Initiales des mois, dans l'ordre calendaire (index 0 = janvier)
NOMS_MOIS_INITIALES = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]


# 1 -- Jours voyagés par mois ---------------------------------------------------


def jours_voyages_par_mois(
    data,
    n_mois: int = 12,
) -> Tuple[List[int], List[int], int]:
    """
    Calcule le nombre de jours voyagés par mois sur les `n_mois` derniers
    mois (mois calendaire courant inclus), à partir de `date_debut` et
    `date_fin`.

    - Un voyage dont `date_debut` OU `date_fin` vaut None (ou est mal
      formatée) est ignoré.
    - Un voyage à cheval sur plusieurs mois voit ses jours répartis sur
      chacun des mois concernés.
    - Un jour couvert par plusieurs voyages qui se chevauchent n'est
      compté qu'une seule fois.

    Renvoie (valeurs, mois_numeros, total) :
    - valeurs       : liste de n_mois entiers, du plus ancien au plus
                      récent.
    - mois_numeros  : numéro du mois (1 = janvier ... 12 = décembre).
    - total         : somme des jours voyagés sur la période.
    """

    aujourd_hui = datetime.now()

    # 1. Bornes calendaires des n_mois derniers mois
    bornes_mois: List[Tuple[datetime, datetime]] = []
    mois_numeros: List[int] = []

    for i in range(n_mois - 1, -1, -1):
        mois_index = aujourd_hui.month - 1 - i
        annee = aujourd_hui.year + mois_index // 12
        mois = mois_index % 12 + 1

        debut_mois = datetime(annee, mois, 1)

        if mois == 12:
            fin_mois = datetime(annee + 1, 1, 1) - timedelta(days=1)
        else:
            fin_mois = datetime(annee, mois + 1, 1) - timedelta(days=1)

        bornes_mois.append((debut_mois, fin_mois))
        mois_numeros.append(mois)

    # 2. Collecter les intervalles valides
    intervalles: List[Tuple[datetime, datetime]] = []

    for voyage in data.values():
        date_deb_str = voyage.get("date_debut")
        date_fin_str = voyage.get("date_fin")

        if date_deb_str is None or date_fin_str is None:
            continue

        try:
            date_deb = datetime.strptime(date_deb_str, "%Y-%m-%d")
            date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d")
        except ValueError:
            continue

        if date_fin < date_deb:
            date_deb, date_fin = date_fin, date_deb

        intervalles.append((date_deb, date_fin))

    # 3. Compter les jours couverts
    valeurs = [0] * n_mois

    for i, (debut_mois, fin_mois) in enumerate(bornes_mois):
        nb_jours_mois = (fin_mois - debut_mois).days + 1

        for j in range(nb_jours_mois):
            jour = debut_mois + timedelta(days=j)

            if any(deb <= jour <= fin for deb, fin in intervalles):
                valeurs[i] += 1

    total = sum(valeurs)

    return valeurs, mois_numeros, total


# 2 -- Classe de création du thème ---------------------------------------------


class ThemeJoursVoyages:
    """
    Thème graphique complet de la carte "Jours voyagés".

    Toutes les couleurs du widget sont centralisées ici :
    - fond et textes ;
    - badge ;
    - éléments décoratifs du calendrier ;
    - couleurs saisonnières ;
    - couleurs des barres mensuelles.

    Le widget lui-même ne contient donc aucun choix de couleur.
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
        # ------------------------------------------------------------------
        # Couleurs générales
        # ------------------------------------------------------------------

        self.fond = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#ffffff",
                sombre="#12141c",
            )
        )

        self.texte = QColor(
            str(
                renvoyer_couleur_texte(
                    style=style,
                    couleur=self.fond.name(),
                )
            )
            if style != 1
            else "#1c1f2b"
        )

        self.sous_texte = _QColor_avec_alpha(
            self.texte,
            alpha=140,
        )

        self.barre = _QColor_avec_alpha(
            couleur=self.texte,
            alpha=30 if style == 1 else 25,
        )

        # ------------------------------------------------------------------
        # Éléments décoratifs du calendrier
        # ------------------------------------------------------------------

        self.calendrier_vernis_debut = QColor(255, 255, 255, 70)
        self.calendrier_vernis_milieu = QColor(255, 255, 255, 15)
        self.calendrier_vernis_fin = QColor(255, 255, 255, 0)

        self.calendrier_anneaux = QColor(255, 255, 255, 235)
        self.calendrier_bandeau = QColor(255, 255, 255, 60)
        self.calendrier_colline = QColor(255, 255, 255, 80)

        # ------------------------------------------------------------------
        # Paramètres saisonniers
        # ------------------------------------------------------------------

        self.saisons = {
            "hiver": {
                "mois": (12, 1, 2),
                "teinte_badge_debut": 205,
                "teinte_badge_fin": 225,
                "teinte_barre": 215,
            },
            "printemps": {
                "mois": (3, 4, 5),
                "teinte_badge_debut": 150,
                "teinte_badge_fin": 115,
                "teinte_barre": 130,
            },
            "ete": {
                "mois": (6, 7, 8),
                "teinte_badge_debut": 45,
                "teinte_badge_fin": 25,
                "teinte_barre": 35,
            },
            "automne": {
                "mois": (9, 10, 11),
                "teinte_badge_debut": 20,
                "teinte_badge_fin": 355,
                "teinte_barre": 15,
            },
        }

        # ------------------------------------------------------------------
        # Couleurs de référence du badge
        # ------------------------------------------------------------------

        self.badge_debut = QColor("#AFB5F1")
        self.badge_fin = QColor("#C6B7F3")

    # ----------------------------------------------------------------------
    # Gestion du mois
    # ----------------------------------------------------------------------

    def _saison_du_mois(self, mois: int) -> dict:
        """Renvoie les paramètres saisonniers associés au mois."""

        for parametres in self.saisons.values():
            if mois in parametres["mois"]:
                return parametres

        return self.saisons["hiver"]

    def couleurs_mois(
        self,
        mois: int,
        mois_actuel: bool = False,
    ) -> dict:
        """
        Renvoie toutes les couleurs dépendant du mois.

        Les couleurs retournées sont notamment :
        - badge_debut ;
        - badge_fin ;
        - barre.

        `mois_actuel` permet de renforcer visuellement la barre du mois
        courant.
        """

        parametres = self._saison_du_mois(mois)

        # --------------------------------------------------------------
        # Badge
        # --------------------------------------------------------------

        _, saturation_debut, valeur_debut, alpha_debut = self.badge_debut.getHsv()

        _, saturation_fin, valeur_fin, alpha_fin = self.badge_fin.getHsv()

        saturation_debut = max(saturation_debut, 140)
        saturation_fin = max(saturation_fin, 140)

        couleur_debut = QColor.fromHsv(
            parametres["teinte_badge_debut"],
            saturation_debut,
            valeur_debut,
            alpha_debut,
        )

        couleur_fin = QColor.fromHsv(
            parametres["teinte_badge_fin"],
            saturation_fin,
            valeur_fin,
            alpha_fin,
        )

        # --------------------------------------------------------------
        # Barre mensuelle
        # --------------------------------------------------------------

        if mois_actuel:
            saturation_barre = 160
            valeur_barre = 200
            alpha_barre = 160
        else:
            saturation_barre = 130
            valeur_barre = 235
            alpha_barre = 75

        barre = QColor.fromHsv(
            parametres["teinte_barre"],
            saturation_barre,
            valeur_barre,
        )
        barre.setAlpha(alpha_barre)

        return {
            "badge_debut": couleur_debut,
            "badge_fin": couleur_fin,
            "barre": barre,
        }


# 3 -- Classe du widget ----------------------------------------------------------


class JoursVoyagesParMoisWidget(QWidget):
    """
    Carte "Jours voyagés" : nombre total de jours passés en voyage sur les
    12 derniers mois, avec un mini graphique montrant la répartition
    mois par mois.
    """

    def __init__(
        self,
        fonction_traduction,
        jours: Optional[Sequence[int]] = None,
        mois_numeros: Optional[Sequence[int]] = None,
        n_mois: int = 12,
        parent: Optional[QWidget] = None,
        duree_animation: int = 1000,
    ) -> None:
        super().__init__(parent)

        self.setMouseTracking(True)
        self.points_hover = []

        self.voyages = {}
        self.fonction_traduction = fonction_traduction
        self.n_mois = n_mois

        self._total = 0.0
        self.total_cible = 0

        self.texte_etiquette_principal = ""
        self.texte_etiquette_secondaire = ""

        self.historique_jours: List[int] = list(jours) if jours else [0] * n_mois

        self.mois_numeros: List[int] = (
            list(mois_numeros) if mois_numeros else self._mois_par_defaut()
        )

        self._progression_barres = 0.0
        self.duree_animation = duree_animation

        self.theme = ThemeJoursVoyages(style=1)

        self.setMinimumSize(320, 180)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._animation_total = QPropertyAnimation(
            self,
            b"valeurAnimee",
            self,
        )
        self._animation_total.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._animation_barres = QPropertyAnimation(
            self,
            b"progressionBarres",
            self,
        )
        self._animation_barres.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation_barres.setStartValue(0.0)
        self._animation_barres.setEndValue(1.0)

        self.definir_historique(
            self.historique_jours,
            self.mois_numeros,
            animer=False,
        )

        self.definir_valeur(
            sum(self.historique_jours),
            animer=True,
        )

        self.set_langue()

    @staticmethod
    def _mois_par_defaut() -> List[int]:
        """Numéros des 12 derniers mois."""

        aujourd_hui = datetime.now()

        return [((aujourd_hui.month - 1 - i) % 12) + 1 for i in range(11, -1, -1)]

    # ----------------------------------------------------------------------
    # Propriétés animables Qt
    # ----------------------------------------------------------------------

    def _obtenir_valeur_animee(self) -> float:
        return self._total

    def _definir_valeur_animee(self, v: float) -> None:
        self._total = v
        self.update()

    valeurAnimee = pyqtProperty(
        float,
        _obtenir_valeur_animee,
        _definir_valeur_animee,
    )

    def _obtenir_progression_barres(self) -> float:
        return self._progression_barres

    def _definir_progression_barres(self, v: float) -> None:
        self._progression_barres = v
        self.update()

    progressionBarres = pyqtProperty(
        float,
        _obtenir_progression_barres,
        _definir_progression_barres,
    )

    # ----------------------------------------------------------------------
    # API publique
    # ----------------------------------------------------------------------

    def definir_valeur(
        self,
        total: int,
        animer: bool = True,
    ) -> None:
        """Met à jour le nombre total de jours affiché."""

        total = max(0, total)
        self.total_cible = total

        self._animation_total.stop()
        self._animation_total.setDuration(self.duree_animation if animer else 0)
        self._animation_total.setStartValue(self._total)
        self._animation_total.setEndValue(float(total))
        self._animation_total.start()

    def definir_historique(
        self,
        historique: Sequence[int],
        mois_numeros: Optional[Sequence[int]] = None,
        animer: bool = True,
    ) -> None:
        """Remplace les valeurs du graphique mensuel."""

        self.historique_jours = list(historique)

        if mois_numeros is not None:
            self.mois_numeros = list(mois_numeros)

        self._animation_barres.stop()
        self._animation_barres.setDuration(self.duree_animation if animer else 0)

        if animer:
            self._progression_barres = 0.0
        else:
            self._progression_barres = 1.0

        self._animation_barres.start()

    def set_langue(self):
        """Mise à jour de la langue."""

        self.texte_etiquette_principal = self.fonction_traduction("4_6_4_jours_voyages")

        self.texte_etiquette_secondaire = self.fonction_traduction(
            "4_6_4_annee_glissante"
        )

        self.update()

    def set_style(
        self,
        style,
        nuances,
        teintes,
    ):
        """Applique un nouveau style au widget."""

        self.theme = ThemeJoursVoyages(
            style=style,
            nuances=nuances,
            teinte=teintes,
            limite_essais=20,
        )

        self.setGraphicsEffect(
            ombre_onglet_4_6(
                style=style,
                parent=self,
            )
        )

        self.update()

    def set_voyages(self, voyages):
        """Met à jour les voyages utilisés pour calculer les statistiques."""

        self.voyages = voyages.copy()
        self.set_valeurs()
        self.update()

    def set_valeurs(self):
        """Recalcule les statistiques mensuelles."""

        valeurs, mois_numeros, total = jours_voyages_par_mois(
            data=self.voyages,
            n_mois=self.n_mois,
        )

        self.definir_historique(
            valeurs,
            mois_numeros,
        )

        self.definir_valeur(total)

    # ----------------------------------------------------------------------
    # Rendu principal
    # ----------------------------------------------------------------------

    def paintEvent(self, event) -> None:
        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()

        # ------------------------------------------------------------------
        # Carte
        # ------------------------------------------------------------------

        rect_carte = QRectF(
            0,
            0,
            w,
            h,
        ).adjusted(
            2,
            2,
            -2,
            -2,
        )

        rayon = min(
            24,
            min(w, h) * 0.14,
        )

        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(
            rect_carte,
            rayon,
            rayon,
        )

        painter.fillPath(
            chemin_carte,
            QBrush(self.theme.fond),
        )

        painter.setClipPath(chemin_carte)

        marge = w * 0.055
        taille_badge = h * 0.24

        # ------------------------------------------------------------------
        # Badge
        # ------------------------------------------------------------------

        rect_badge = QRectF(
            marge,
            h * 0.08,
            taille_badge,
            taille_badge,
        )

        self._dessiner_badge_calendrier(
            painter,
            rect_badge,
        )

        # ------------------------------------------------------------------
        # Texte principal
        # ------------------------------------------------------------------

        x_texte = rect_badge.right() + marge * 0.8
        largeur_texte = w - x_texte - marge

        police_valeur = QFont(
            "Segoe UI",
            max(11, int(h * 0.15)),
            QFont.Weight.Bold,
        )

        painter.setFont(police_valeur)
        painter.setPen(self.theme.texte)

        rect_valeur = QRectF(
            x_texte,
            h * 0.05,
            largeur_texte,
            h * 0.20,
        )

        painter.drawText(
            rect_valeur,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"{int(round(self._total))}",
        )

        # ------------------------------------------------------------------
        # Étiquettes
        # ------------------------------------------------------------------

        painter.setPen(self.theme.sous_texte)

        police_etiquette_1 = QFont(
            "Segoe UI",
            max(7, int(h * 0.075)),
        )

        rect_ligne_1 = QRectF(
            x_texte,
            h * 0.26,
            largeur_texte,
            h * 0.13,
        )

        painter.setFont(police_etiquette_1)

        painter.drawText(
            rect_ligne_1,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.texte_etiquette_principal,
        )

        police_etiquette_2 = QFont(
            "Segoe UI",
            max(6, int(h * 0.06)),
        )

        rect_ligne_2 = QRectF(
            x_texte,
            h * 0.37,
            largeur_texte,
            h * 0.09,
        )

        painter.setFont(police_etiquette_2)

        painter.drawText(
            rect_ligne_2,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.texte_etiquette_secondaire,
        )

        # ------------------------------------------------------------------
        # Graphique mensuel
        # ------------------------------------------------------------------

        rect_barres = QRectF(
            marge,
            h * 0.52,
            w - 2 * marge,
            h * 0.30,
        )

        rect_etiquettes = QRectF(
            marge,
            h * 0.83,
            w - 2 * marge,
            h * 0.13,
        )

        self._dessiner_graphique_mensuel(
            painter,
            rect_barres,
            rect_etiquettes,
        )

    # ----------------------------------------------------------------------
    # Badge calendrier
    # ----------------------------------------------------------------------

    def _dessiner_badge_calendrier(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:
        """Dessine le badge calendrier saisonnier."""

        rayon_badge = rect.width() * 0.3
        mois = datetime.now().month

        couleurs = self.theme.couleurs_mois(mois)

        # ------------------------------------------------------------------
        # Corps du badge
        # ------------------------------------------------------------------

        degrade = QLinearGradient(
            rect.topLeft(),
            rect.bottomRight(),
        )

        degrade.setColorAt(
            0.0,
            couleurs["badge_debut"],
        )

        degrade.setColorAt(
            1.0,
            couleurs["badge_fin"],
        )

        chemin_corps = QPainterPath()
        chemin_corps.addRoundedRect(
            rect,
            rayon_badge,
            rayon_badge,
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(degrade))
        painter.drawPath(chemin_corps)

        painter.setClipPath(chemin_corps)

        # ------------------------------------------------------------------
        # Vernis
        # ------------------------------------------------------------------

        vernis = QLinearGradient(
            rect.topLeft(),
            QPointF(
                rect.left(),
                rect.bottom(),
            ),
        )

        vernis.setColorAt(
            0.0,
            self.theme.calendrier_vernis_debut,
        )
        vernis.setColorAt(
            0.5,
            self.theme.calendrier_vernis_milieu,
        )
        vernis.setColorAt(
            1.0,
            self.theme.calendrier_vernis_fin,
        )

        painter.setBrush(QBrush(vernis))
        painter.drawRect(rect)

        s = rect.width()

        # ------------------------------------------------------------------
        # Anneaux de reliure
        # ------------------------------------------------------------------

        largeur_anneau = s * 0.07
        hauteur_anneau = s * 0.16

        painter.setBrush(QBrush(self.theme.calendrier_anneaux))

        for fraction_x in (0.28, 0.72):
            rect_anneau = QRectF(
                rect.left() + s * fraction_x - largeur_anneau / 2,
                rect.top() - hauteur_anneau * 0.35,
                largeur_anneau,
                hauteur_anneau,
            )

            chemin_anneau = QPainterPath()

            chemin_anneau.addRoundedRect(
                rect_anneau,
                largeur_anneau / 2,
                largeur_anneau / 2,
            )

            painter.drawPath(chemin_anneau)

        # ------------------------------------------------------------------
        # Bandeau d'en-tête
        # ------------------------------------------------------------------

        rect_entete = QRectF(
            rect.left(),
            rect.top() + s * 0.18,
            s,
            s * 0.16,
        )

        painter.setBrush(QBrush(self.theme.calendrier_bandeau))

        painter.drawRect(rect_entete)

        # ------------------------------------------------------------------
        # Scène saisonnière
        # ------------------------------------------------------------------

        rect_scene = QRectF(
            rect.left(),
            rect_entete.bottom(),
            s,
            rect.bottom() - rect_entete.bottom(),
        )

        self._dessiner_scene_saison(
            painter,
            rect_scene,
            mois,
        )

        painter.setClipping(False)

    # ----------------------------------------------------------------------
    # Scène saisonnière
    # ----------------------------------------------------------------------

    def _dessiner_scene_saison(
        self,
        painter: QPainter,
        rect_scene: QRectF,
        mois: int,
    ) -> None:
        """Dessine la petite scène saisonnière du calendrier."""

        # ------------------------------------------------------------------
        # Colline
        # ------------------------------------------------------------------

        colline = QPainterPath()

        colline.moveTo(
            rect_scene.left(),
            rect_scene.bottom(),
        )

        colline.quadTo(
            QPointF(
                rect_scene.center().x(),
                rect_scene.top() + rect_scene.height() * 0.32,
            ),
            QPointF(
                rect_scene.right(),
                rect_scene.bottom(),
            ),
        )

        colline.lineTo(
            rect_scene.right(),
            rect_scene.bottom(),
        )

        colline.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QBrush(self.theme.calendrier_colline))

        painter.drawPath(colline)

        # ------------------------------------------------------------------
        # Icône
        # ------------------------------------------------------------------

        centre_icone = QPointF(
            rect_scene.center().x(),
            rect_scene.top() + rect_scene.height() * 0.24,
        )

        taille_icone = rect_scene.height() * 0.9

        if mois in (12, 1, 2):
            _dessiner_icone_flocon(
                painter,
                centre_icone,
                taille_icone,
            )

        elif mois in (3, 4, 5):
            _dessiner_icone_pousse(
                painter,
                centre_icone,
                taille_icone,
            )

        elif mois in (6, 7, 8):
            _dessiner_icone_soleil(
                painter,
                centre_icone,
                taille_icone,
            )

        else:
            _dessiner_icone_feuille(
                painter,
                centre_icone,
                taille_icone,
            )

    # ----------------------------------------------------------------------
    # Graphique mensuel
    # ----------------------------------------------------------------------

    def _dessiner_graphique_mensuel(
        self,
        painter: QPainter,
        rect_barres: QRectF,
        rect_etiquettes: QRectF,
    ) -> None:

        valeurs = self.historique_jours
        n = len(valeurs)

        self.points_hover = []

        if n == 0:
            return

        maximum = max(valeurs) or 1

        espace = rect_barres.width() * 0.18 / max(1, n - 1) if n > 1 else 0

        largeur_barre = (rect_barres.width() - espace * (n - 1)) / n

        police_mois = QFont(
            "Segoe UI",
            max(
                6,
                int(rect_etiquettes.height() * 0.6),
            ),
        )

        painter.setFont(police_mois)
        painter.setPen(Qt.PenStyle.NoPen)

        mois_actuel = datetime.now().month

        for i, v in enumerate(valeurs):

            x = rect_barres.left() + i * (largeur_barre + espace)

            hauteur_pleine = rect_barres.height() * (v / maximum) if maximum else 0.0

            hauteur_pleine = max(
                hauteur_pleine,
                rect_barres.height() * 0.06,
            )

            hauteur_barre = hauteur_pleine * self._progression_barres

            y = rect_barres.bottom() - hauteur_barre

            # ----------------------------------------------------------
            # Couleur de la barre
            # ----------------------------------------------------------

            if i < len(self.mois_numeros):
                numero_mois = self.mois_numeros[i]

                couleur = self.theme.couleurs_mois(
                    numero_mois,
                    mois_actuel=(numero_mois == mois_actuel),
                )["barre"]

            else:
                couleur = self.theme.barre

            painter.setBrush(QBrush(couleur))

            # ----------------------------------------------------------
            # Barre
            # ----------------------------------------------------------

            rect_barre = QRectF(
                x,
                y,
                largeur_barre,
                hauteur_barre,
            )

            chemin = QPainterPath()

            chemin.addRoundedRect(
                rect_barre,
                largeur_barre * 0.35,
                largeur_barre * 0.35,
            )

            self.points_hover.append(
                {
                    "rect": rect_barre,
                    "valeur": v,
                }
            )

            painter.drawPath(chemin)

            # ----------------------------------------------------------
            # Étiquette du mois
            # ----------------------------------------------------------

            if i < len(self.mois_numeros):

                numero_mois = self.mois_numeros[i]

                texte_mois = NOMS_MOIS_INITIALES[(numero_mois - 1) % 12]

                couleur_texte = QColor(couleur)
                couleur_texte.setAlpha(255)

                if i == n - 1:
                    painter.setPen(couleur_texte)
                else:
                    painter.setPen(self.theme.sous_texte)

                rect_mois = QRectF(
                    x,
                    rect_etiquettes.top(),
                    largeur_barre,
                    rect_etiquettes.height(),
                )

                painter.drawText(
                    rect_mois,
                    Qt.AlignmentFlag.AlignCenter,
                    texte_mois,
                )

                painter.setPen(Qt.PenStyle.NoPen)

    # ----------------------------------------------------------------------
    # Interaction
    # ----------------------------------------------------------------------

    def mouseMoveEvent(self, event):
        """Affiche la valeur d'une barre au survol."""

        pos = event.position()

        for point in self.points_hover:
            if point["rect"].contains(pos):
                QToolTip.showText(
                    event.globalPosition().toPoint(),
                    f"{point['valeur']}",
                    self,
                )
                return

        QToolTip.hideText()

    # ----------------------------------------------------------------------
    # Animation
    # ----------------------------------------------------------------------

    def relancer_animation(self) -> None:
        """Relance les animations sans modifier les données."""

        duree = self.duree_animation

        # ------------------------------------------------------------------
        # Animation du nombre total
        # ------------------------------------------------------------------

        self._animation_total.stop()
        self._animation_total.setDuration(duree)
        self._animation_total.setStartValue(0.0)
        self._animation_total.setEndValue(float(self.total_cible))
        self._animation_total.start()

        # ------------------------------------------------------------------
        # Animation des barres
        # ------------------------------------------------------------------

        self._animation_barres.stop()
        self._animation_barres.setDuration(duree)
        self._animation_barres.setStartValue(0.0)
        self._animation_barres.setEndValue(1.0)

        self._progression_barres = 0.0

        self._animation_barres.start()
