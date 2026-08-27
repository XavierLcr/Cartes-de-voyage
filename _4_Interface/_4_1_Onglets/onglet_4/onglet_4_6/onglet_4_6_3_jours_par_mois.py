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
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QSizePolicy, QWidget, QToolTip

from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)
from _4_Interface._4_3_Icones._4_3_1_soleil_souriant import _dessiner_icone_soleil
from _4_Interface._4_3_Icones._4_3_2_flocon_neige import _dessiner_icone_flocon
from _4_Interface._4_3_Icones._4_3_3_feuille_automne import _dessiner_icone_feuille
from _4_Interface._4_3_Icones._4_3_4_jeune_pousse import _dessiner_icone_pousse

# Initiales des mois, dans l'ordre calendaire (index 0 = janvier)
NOMS_MOIS_INITIALES = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]


# 1 -- Jours voyagés par mois ---------------------------------------------------


def jours_voyages_par_mois(data, n_mois: int = 12) -> Tuple[List[int], List[int], int]:
    """
    Calcule le nombre de jours voyagés par mois sur les `n_mois` derniers
    mois (mois calendaire courant inclus), à partir de `date_debut` et
    `date_fin`.

    - Un voyage dont `date_debut` OU `date_fin` vaut None (ou est mal
      formatée) est ignoré.
    - Un voyage à cheval sur plusieurs mois voit ses jours répartis sur
      chacun des mois concernés (pas tout attribué au mois de départ).

    Renvoie (valeurs, mois_numeros, total) :
    - valeurs       : liste de n_mois entiers, du plus ancien au plus
                      récent (le dernier élément = mois en cours).
    - mois_numeros  : numéro du mois (1 = janvier ... 12 = décembre)
                      correspondant à chaque élément de `valeurs`.
    - total         : somme des jours voyagés sur la période.
    """
    aujourd_hui = datetime.now()

    # 1. Bornes calendaires des n_mois derniers mois (du plus ancien au
    #    plus récent), sous la forme (premier_jour, dernier_jour).
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

    valeurs = [0] * n_mois

    # 2. Parcourir les voyages valides et répartir leurs jours sur les mois
    #    qu'ils traversent.
    for voyage in data.values():
        date_deb_str = voyage.get("date_debut")
        date_fin_str = voyage.get("date_fin")
        if date_deb_str is None or date_fin_str is None:
            continue
        try:
            date_deb = datetime.strptime(date_deb_str, "%Y-%m-%d")
            date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d")
        except ValueError:
            # Date mal formatée : on ignore ce voyage plutôt que de planter
            continue
        if date_fin < date_deb:
            date_deb, date_fin = date_fin, date_deb

        for i, (debut_mois, fin_mois) in enumerate(bornes_mois):
            chevauchement_debut = max(date_deb, debut_mois)
            chevauchement_fin = min(date_fin, fin_mois)
            if chevauchement_fin >= chevauchement_debut:
                valeurs[i] += (chevauchement_fin - chevauchement_debut).days + 1

    total = sum(valeurs)
    return valeurs, mois_numeros, total


# 2 -- Classe de création des couleurs -----------------------------------------


class ThemeJoursVoyages:
    """
    Palette de couleurs de la carte "Jours voyagés".

    Reprend la même structure que `ThemeCarte` (onglet 4.6.3) et
    `CompteurTheme` (onglet 4.6.2) — même fond de carte, même convention
    d'ombre, mêmes appels de style — avec son propre accent indigo ->
    violet, pour que le tableau de bord affiche trois teintes distinctes
    mais construites de façon identique.
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
        # Fond de carte : identique aux deux autres widgets.
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
            str(renvoyer_couleur_texte(style=style, couleur=self.fond.name()))
            if style != 1
            else "#1c1f2b"
        )
        # Sous-texte
        self.sous_texte = QColor(self.texte)
        self.sous_texte.setAlpha(140)

        # Barres "normales" du graphique mensuel : dérivées du texte, très
        # diluées, même alpha que les widgets voisins.
        self.barre = QColor(self.texte)
        self.barre.setAlpha(30 if style == 1 else 25)

        # Dégradé du badge (icône calendrier) : indigo -> violet.
        self.badge_debut = QColor(
            renvoyer_couleur_widget(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#6366F1",
                sombre="#818CF8",
            )
        )
        self.badge_fin = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#8B5CF6",
                sombre="#A78BFA",
                reference=self.badge_debut.name(),
                essais=limite_essais,
            )
        )

        # Barre du mois en cours, mise en avant : même famille que le
        # badge mais dans l'autre sens (comme `barre_surbrillance` dans
        # ThemeCarte), pour un léger contraste avec le reste du graphique.
        self.barre_surbrillance = QColor(
            renvoyer_couleur_widget_differente(
                style=style,
                teinte=teinte,
                nuances=nuances,
                clair="#8B5CF6",
                sombre="#6366F1",
                reference=self.badge_fin.name(),
                essais=limite_essais,
            )
        )

        # Ombre portée : même convention que les widgets voisins.
        self.ombre = QColor(self.texte)
        self.ombre.setAlpha(60 if style == 1 else 120)


# 3 -- Classe du widget ----------------------------------------------------------


class JoursVoyagesParMoisWidget(QWidget):
    """
    Carte "Jours voyagés" : nombre total de jours passés en voyage sur les
    12 derniers mois (gros chiffre animé + badge), avec un mini graphique
    en barres montrant la répartition mois par mois.

    Reprend le vocabulaire visuel des deux autres widgets du tableau de
    bord (carte à coins arrondis, même ombre, même typographie) avec son
    propre accent indigo -> violet, pour compléter la palette turquoise
    du compteur de pays et orange/rose du nombre de voyages.
    """

    def __init__(
        self,
        fonction_traduction,
        jours: Optional[Sequence[int]] = None,
        mois_numeros: Optional[Sequence[int]] = None,
        n_mois: int = 12,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        jours          : historique de jours voyagés par mois (n_mois
                         valeurs, du plus ancien au plus récent). Si None,
                         démarre à zéro partout (à remplir via
                         `set_voyages`).
        mois_numeros   : numéro de mois (1-12) associé à chaque valeur de
                         `jours`, pour l'étiquette sous chaque barre.
        n_mois         : profondeur du graphique mensuel (12 par défaut).
        """
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

        self.theme = ThemeJoursVoyages(style=1)

        self.setMinimumSize(320, 180)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._ombre_effet = QGraphicsDropShadowEffect(self)
        self._ombre_effet.setBlurRadius(30)
        self._ombre_effet.setOffset(0, 8)
        self._ombre_effet.setColor(self.theme.ombre)
        self.setGraphicsEffect(self._ombre_effet)

        self._animation_total = QPropertyAnimation(self, b"valeurAnimee", self)
        self._animation_total.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._animation_barres = QPropertyAnimation(self, b"progressionBarres", self)
        self._animation_barres.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation_barres.setStartValue(0.0)
        self._animation_barres.setEndValue(1.0)

        self.definir_historique(self.historique_jours, self.mois_numeros, animer=False)
        self.definir_valeur(sum(self.historique_jours), animer=True)
        self.set_langue()

    @staticmethod
    def _mois_par_defaut() -> List[int]:
        """Numéros de mois (1-12) des 12 derniers mois, par défaut."""
        aujourd_hui = datetime.now()
        return [((aujourd_hui.month - 1 - i) % 12) + 1 for i in range(11, -1, -1)]

    # ---------------------------------------------------------------
    # Propriétés animables Qt
    # ---------------------------------------------------------------
    def _obtenir_valeur_animee(self) -> float:
        return self._total

    def _definir_valeur_animee(self, v: float) -> None:
        self._total = v
        self.update()

    valeurAnimee = pyqtProperty(float, _obtenir_valeur_animee, _definir_valeur_animee)

    def _obtenir_progression_barres(self) -> float:
        return self._progression_barres

    def _definir_progression_barres(self, v: float) -> None:
        self._progression_barres = v
        self.update()

    progressionBarres = pyqtProperty(
        float, _obtenir_progression_barres, _definir_progression_barres
    )

    # ---------------------------------------------------------------
    # API publique
    # ---------------------------------------------------------------
    def definir_valeur(
        self, total: int, animer: bool = True, duree: int = 1000
    ) -> None:
        """Met à jour le nombre total de jours affiché (avec ou sans animation)."""
        total = max(0, total)
        self.total_cible = total

        self._animation_total.stop()
        self._animation_total.setDuration(duree if animer else 0)
        self._animation_total.setStartValue(self._total)
        self._animation_total.setEndValue(float(total))
        self._animation_total.start()

    def definir_historique(
        self,
        historique: Sequence[int],
        mois_numeros: Optional[Sequence[int]] = None,
        animer: bool = True,
        duree: int = 900,
    ) -> None:
        """Remplace les valeurs du graphique mensuel (et les rejoue en entrée)."""
        self.historique_jours = list(historique)
        if mois_numeros is not None:
            self.mois_numeros = list(mois_numeros)

        self._animation_barres.stop()
        self._animation_barres.setDuration(duree if animer else 0)
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

    def set_style(self, style, nuances, teintes):
        self.theme = ThemeJoursVoyages(
            style=style, nuances=nuances, teinte=teintes, limite_essais=20
        )
        self._ombre_effet.setColor(self.theme.ombre)
        self.update()

    def set_voyages(self, voyages):
        self.voyages = voyages.copy()
        self.set_valeurs()
        self.update()

    def set_valeurs(self):
        valeurs, mois_numeros, total = jours_voyages_par_mois(
            data=self.voyages, n_mois=self.n_mois
        )
        self.definir_historique(valeurs, mois_numeros)
        self.definir_valeur(total)

    # ---------------------------------------------------------------
    # Rendu
    # ---------------------------------------------------------------
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()

        # --- carte à coins arrondis : même formule que les widgets voisins ---
        rect_carte = QRectF(0, 0, w, h).adjusted(2, 2, -2, -2)
        rayon = min(24, min(w, h) * 0.14)
        chemin_carte = QPainterPath()
        chemin_carte.addRoundedRect(rect_carte, rayon, rayon)
        painter.fillPath(chemin_carte, QBrush(self.theme.fond))
        painter.setClipPath(chemin_carte)

        marge = w * 0.055
        taille_badge = h * 0.24

        # --- badge (icône calendrier) ---
        rect_badge = QRectF(marge, h * 0.08, taille_badge, taille_badge)
        self._dessiner_badge_calendrier(painter, rect_badge)

        # --- zone texte à droite du badge ---
        x_texte = rect_badge.right() + marge * 0.8
        largeur_texte = w - x_texte - marge

        police_valeur = QFont("Segoe UI", max(11, int(h * 0.15)), QFont.Weight.Bold)
        painter.setFont(police_valeur)
        painter.setPen(self.theme.texte)
        rect_valeur = QRectF(x_texte, h * 0.05, largeur_texte, h * 0.20)
        painter.drawText(
            rect_valeur,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            f"{int(round(self._total))}",
        )

        # --- étiquette : deux lignes, deuxième plus petite ---
        painter.setPen(self.theme.sous_texte)

        police_etiquette_1 = QFont("Segoe UI", max(7, int(h * 0.075)))
        rect_ligne_1 = QRectF(x_texte, h * 0.26, largeur_texte, h * 0.13)
        painter.setFont(police_etiquette_1)
        painter.drawText(
            rect_ligne_1,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.texte_etiquette_principal,
        )

        police_etiquette_2 = QFont("Segoe UI", max(6, int(h * 0.06)))
        rect_ligne_2 = QRectF(x_texte, h * 0.37, largeur_texte, h * 0.09)
        painter.setFont(police_etiquette_2)
        painter.drawText(
            rect_ligne_2,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.texte_etiquette_secondaire,
        )

        # --- graphique en barres mensuel + étiquettes des mois ---
        rect_barres = QRectF(marge, h * 0.52, w - 2 * marge, h * 0.30)
        rect_etiquettes = QRectF(marge, h * 0.83, w - 2 * marge, h * 0.13)
        self._dessiner_graphique_mensuel(painter, rect_barres, rect_etiquettes)

    def _dessiner_badge_calendrier(self, painter: QPainter, rect: QRectF) -> None:
        """Badge calendrier dont la couleur de fond ET l'illustration sur la
        page changent selon la saison en cours (flocon sur colline enneigée
        en hiver, pousse sur colline verte au printemps, soleil sur colline
        en été, feuille tombante en automne)."""
        rayon_badge = rect.width() * 0.3
        mois = datetime.now().month
        couleur_debut, couleur_fin = self._couleurs_saison(mois)

        degrade = QLinearGradient(rect.topLeft(), rect.bottomRight())
        degrade.setColorAt(0.0, couleur_debut)
        degrade.setColorAt(1.0, couleur_fin)
        chemin_corps = QPainterPath()
        chemin_corps.addRoundedRect(rect, rayon_badge, rayon_badge)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(degrade))
        painter.drawPath(chemin_corps)

        painter.setClipPath(chemin_corps)

        # léger vernis en haut du badge, pour donner du relief
        vernis = QLinearGradient(rect.topLeft(), QPointF(rect.left(), rect.bottom()))
        vernis.setColorAt(0.0, QColor(255, 255, 255, 70))
        vernis.setColorAt(0.5, QColor(255, 255, 255, 15))
        vernis.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(vernis))
        painter.drawRect(rect)

        s = rect.width()

        # petits anneaux de reliure, en haut du calendrier
        largeur_anneau = s * 0.07
        hauteur_anneau = s * 0.16
        painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
        for fraction_x in (0.28, 0.72):
            rect_anneau = QRectF(
                rect.left() + s * fraction_x - largeur_anneau / 2,
                rect.top() - hauteur_anneau * 0.35,
                largeur_anneau,
                hauteur_anneau,
            )
            chemin_anneau = QPainterPath()
            chemin_anneau.addRoundedRect(
                rect_anneau, largeur_anneau / 2, largeur_anneau / 2
            )
            painter.drawPath(chemin_anneau)

        # bandeau d'en-tête (léger voile blanc translucide)
        rect_entete = QRectF(rect.left(), rect.top() + s * 0.18, s, s * 0.16)
        painter.setBrush(QBrush(QColor(255, 255, 255, 60)))
        painter.drawRect(rect_entete)

        # --- scène saisonnière, sur le reste de la page du calendrier ---
        rect_scene = QRectF(
            rect.left(),
            rect_entete.bottom(),
            s,
            rect.bottom() - rect_entete.bottom(),
        )
        self._dessiner_scene_saison(painter, rect_scene, mois)

        painter.setClipping(False)

    def _couleurs_saison(self, mois: int) -> tuple[QColor, QColor]:
        """Renvoie le couple (début, fin) de dégradé du badge pour le mois
        donné : la teinte tourne selon la saison, tandis que saturation /
        luminosité restent pilotées par le thème (cohérence clair/sombre)."""
        if mois in (12, 1, 2):
            teinte_debut, teinte_fin = 205, 225  # bleu glacé -> bleu-violet froid
        elif mois in (3, 4, 5):
            teinte_debut, teinte_fin = 150, 115  # vert tendre -> vert printemps
        elif mois in (6, 7, 8):
            teinte_debut, teinte_fin = 45, 25  # jaune soleil -> orangé chaud
        else:
            teinte_debut, teinte_fin = 20, 355  # roux automnal -> rouge feuille

        _, saturation_debut, valeur_debut, alpha_debut = self.theme.badge_debut.getHsv()
        _, saturation_fin, valeur_fin, alpha_fin = self.theme.badge_fin.getHsv()

        # on garantit une saturation minimale pour que les couleurs
        # saisonnières restent franches même si la palette du thème est pastel
        saturation_debut = max(saturation_debut, 140)
        saturation_fin = max(saturation_fin, 140)

        couleur_debut = QColor.fromHsv(
            teinte_debut, saturation_debut, valeur_debut, alpha_debut
        )
        couleur_fin = QColor.fromHsv(teinte_fin, saturation_fin, valeur_fin, alpha_fin)
        return couleur_debut, couleur_fin

    # -- Teinte de base par saison, réutilisée pour les barres du graphique
    #    mensuel (une seule teinte représentative par saison, contrairement
    #    au dégradé à deux teintes du badge).
    _TEINTE_SAISON_HIVER = 215
    _TEINTE_SAISON_PRINTEMPS = 130
    _TEINTE_SAISON_ETE = 35
    _TEINTE_SAISON_AUTOMNE = 15

    def _teinte_saison(self, mois: int) -> int:
        """Renvoie la teinte (0-359) associée au mois donné, en réutilisant
        le découpage saisonnier de `_couleurs_saison`."""
        if mois in (12, 1, 2):
            return self._TEINTE_SAISON_HIVER
        elif mois in (3, 4, 5):
            return self._TEINTE_SAISON_PRINTEMPS
        elif mois in (6, 7, 8):
            return self._TEINTE_SAISON_ETE
        else:
            return self._TEINTE_SAISON_AUTOMNE

    def _couleur_barre_saison(self, mois: int) -> QColor:
        """Couleur (pâle) d'une barre du graphique mensuel, teintée selon la
        saison de `mois`. Reste nettement moins saturée/visible que
        `barre_surbrillance` (réservée au mois en cours), pour que ce
        dernier continue à ressortir clairement."""
        teinte = self._teinte_saison(mois)

        # on ancre la luminosité sur le fond de la carte, pour rester
        # cohérent avec le thème clair/sombre actuel
        mois_actuel = datetime.now().month == mois
        valeur = 200 if mois_actuel else 235
        saturation = saturation = 160 if mois_actuel else 130

        couleur = QColor.fromHsv(teinte, saturation, valeur)
        couleur.setAlpha(130 if mois_actuel else 55)
        return couleur

    def _dessiner_scene_saison(
        self, painter: QPainter, rect_scene: QRectF, mois: int
    ) -> None:
        """Dessine, dans la zone `rect_scene` (la page du calendrier), une
        petite colline avec un élément saisonnier au-dessus."""
        # colline (silhouette commune à toutes les saisons)
        colline = QPainterPath()
        colline.moveTo(rect_scene.left(), rect_scene.bottom())
        colline.quadTo(
            QPointF(
                rect_scene.center().x(),
                rect_scene.top() + rect_scene.height() * 0.32,
            ),
            QPointF(rect_scene.right(), rect_scene.bottom()),
        )
        colline.lineTo(rect_scene.right(), rect_scene.bottom())
        colline.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 80)))
        painter.drawPath(colline)

        centre_icone = QPointF(
            rect_scene.center().x(), rect_scene.top() + rect_scene.height() * 0.24
        )
        taille_icone = rect_scene.height() * 0.9

        if mois in (12, 1, 2):
            _dessiner_icone_flocon(painter, centre_icone, taille_icone)
        elif mois in (3, 4, 5):
            _dessiner_icone_pousse(painter, centre_icone, taille_icone)
        elif mois in (6, 7, 8):
            _dessiner_icone_soleil(painter, centre_icone, taille_icone)
        else:
            _dessiner_icone_feuille(painter, centre_icone, taille_icone)

    def _dessiner_graphique_mensuel(
        self, painter: QPainter, rect_barres: QRectF, rect_etiquettes: QRectF
    ) -> None:

        valeurs = self.historique_jours
        n = len(valeurs)

        self.points_hover = []

        if n == 0:
            return

        maximum = max(valeurs) or 1
        espace = rect_barres.width() * 0.18 / max(1, n - 1) if n > 1 else 0
        largeur_barre = (rect_barres.width() - espace * (n - 1)) / n

        police_mois = QFont("Segoe UI", max(6, int(rect_etiquettes.height() * 0.6)))
        painter.setFont(police_mois)

        painter.setPen(Qt.PenStyle.NoPen)
        for i, v in enumerate(valeurs):
            x = rect_barres.left() + i * (largeur_barre + espace)

            hauteur_pleine = rect_barres.height() * (v / maximum) if maximum else 0.0
            hauteur_pleine = max(hauteur_pleine, rect_barres.height() * 0.06)
            hauteur_barre = hauteur_pleine * self._progression_barres
            y = rect_barres.bottom() - hauteur_barre

            if i < len(self.mois_numeros):
                couleur = self._couleur_barre_saison(self.mois_numeros[i])
            else:
                couleur = self.theme.barre
            painter.setBrush(QBrush(couleur))
            rect_barre = QRectF(x, y, largeur_barre, hauteur_barre)
            chemin = QPainterPath()
            chemin.addRoundedRect(
                rect_barre, largeur_barre * 0.35, largeur_barre * 0.35
            )

            self.points_hover.append(
                {
                    "rect": rect_barre,
                    "valeur": v,
                }
            )

            painter.drawPath(chemin)

            # étiquette du mois, centrée sous la barre
            couleur.setAlpha(255)
            if i < len(self.mois_numeros):
                numero_mois = self.mois_numeros[i]
                texte_mois = NOMS_MOIS_INITIALES[(numero_mois - 1) % 12]
                painter.setPen(self.theme.sous_texte if not (i == n - 1) else couleur)
                rect_mois = QRectF(
                    x, rect_etiquettes.top(), largeur_barre, rect_etiquettes.height()
                )
                painter.drawText(rect_mois, Qt.AlignmentFlag.AlignCenter, texte_mois)
                painter.setPen(Qt.PenStyle.NoPen)

    def mouseMoveEvent(self, event):

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
