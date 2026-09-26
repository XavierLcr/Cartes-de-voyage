################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# 4.5 – Diagramme de Gantt                                                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from datetime import date, datetime

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QToolTip,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QMouseEvent

from _0_Utilitaires._0_10_selecteur_date import SelecteurDate
from _0_Utilitaires._0_2_fonctions_graphiques import generer_couleur_aleatoire_hex
from _0_Utilitaires._0_15_dates import est_jour_militaire
from _4_Interface._4_3_Icones._4_3_48_avion._4_3_48_X_avion import Avion

# 1 -- Fonctions de traitement des données -------------------------------------


## 1.1 -- Conversion d'une valeur en date --------------------------------------


def convertir_date(valeur) -> date:
    """
    Convertit une valeur de date en objet ``datetime.date``.

    Accepte notamment :
        - datetime.datetime ;
        - datetime.date ;
        - chaîne au format YYYY-MM-DD ;
        - valeur dont les 10 premiers caractères suivent ce format.
    """

    if isinstance(
        valeur,
        datetime,
    ):
        return valeur.date()

    if isinstance(
        valeur,
        date,
    ):
        return valeur

    return datetime.strptime(
        str(valeur)[:10],
        "%Y-%m-%d",
    ).date()


## 1.2 -- Nettoyage et normalisation des voyages --------------------------------


def traiter_voyages(
    voyages: dict,
    voyage_label: str = "nom",
    date_min_label: str = "date_debut",
    date_max_label: str = "date_fin",
) -> list[dict]:
    """
    Nettoie et normalise les voyages une seule fois.

    Les voyages sans nom, sans date de début, sans date de fin ou possédant
    une date invalide sont ignorés.

    La structure renvoyée est volontairement indépendante de la structure
    d'origine afin que le widget graphique n'ait plus à effectuer de
    nettoyage ou de conversion.

    Retour :
        [
            {
                "id": ...,
                "label": ...,
                "deb": date(...),
                "fin": date(...),
            },
            ...
        ]
    """

    voyages_traites = []

    for identifiant, item in voyages.items():

        label = item.get(
            voyage_label,
            "",
        )

        date_debut = item.get(
            date_min_label,
        )

        date_fin = item.get(
            date_max_label,
        )

        # ----------------------------------------------------------------------
        # Informations indispensables
        # ----------------------------------------------------------------------

        if not label or not date_debut or not date_fin:
            continue

        # ----------------------------------------------------------------------
        # Conversion des dates
        # ----------------------------------------------------------------------

        try:

            date_debut = convertir_date(
                date_debut,
            )

            date_fin = convertir_date(
                date_fin,
            )

        except (ValueError, TypeError):

            continue

        # ----------------------------------------------------------------------
        # Ajout
        # ----------------------------------------------------------------------

        voyages_traites.append(
            {
                "id": identifiant,
                "label": str(label),
                "deb": date_debut,
                "fin": date_fin,
            }
        )

    # --------------------------------------------------------------------------
    # Tri chronologique effectué une seule fois
    # --------------------------------------------------------------------------

    voyages_traites.sort(
        key=lambda x: (
            x["deb"],
            x["fin"],
            x["label"],
        )
    )

    return voyages_traites


## 1.3 -- Filtrage des voyages selon la période affichée -----------------------


def filtrer_voyages(
    voyages: list[dict],
    date_min: date,
    date_max: date,
) -> list[dict]:
    """
    Conserve les voyages qui intersectent la période demandée.

    Les dates des voyages sont déjà normalisées : aucune conversion ni
    validation supplémentaire n'est donc nécessaire ici.
    """

    return [
        voyage
        for voyage in voyages
        if voyage["fin"] >= date_min and voyage["deb"] <= date_max
    ]


# 2 -- Widget de dessin du Gantt -----------------------------------------------


class DiagrammeGantt(QWidget):
    """Widget PyQt6 natif qui dessine un diagramme de Gantt via QPainter."""

    MARGE_GAUCHE = 30
    MARGE_DROITE = 30
    MARGE_HAUT = 50
    MARGE_BAS = 40

    # Hauteur/espacement "confortables" utilisés quand la place ne manque pas
    HAUTEUR_BARRE_MAX = 22
    ESPACE_BARRE_MAX = 10

    # Valeurs minimales conservées pour garder les barres lisibles
    HAUTEUR_BARRE_MIN = 6
    ESPACE_BARRE_MIN = 2

    INTERVALLE_ANIMATION_MS = 25

    # 2.1 -- Initialisation ----------------------------------------------------

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent=parent,
        )

        self.setMouseTracking(
            True,
        )

        self.setMinimumHeight(
            200,
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        # ----------------------------------------------------------------------
        # Données
        # ----------------------------------------------------------------------

        self.barres = []

        self.date_min = None
        self.date_max = None

        self.titre = ""

        self.barre_survolee = None

        # ----------------------------------------------------------------------
        # Avion
        # ----------------------------------------------------------------------

        self.init_avion()

        self._timer_avion = QTimer(
            self,
        )

        self._timer_avion.setInterval(
            self.INTERVALLE_ANIMATION_MS,
        )

        self._timer_avion.timeout.connect(
            self._animer_avion,
        )

        self._timer_avion.start()

        # ----------------------------------------------------------------------
        # Dimensions des barres
        # ----------------------------------------------------------------------

        self.hauteur_barre = self.HAUTEUR_BARRE_MAX
        self.espace_barre = self.ESPACE_BARRE_MAX

        # ----------------------------------------------------------------------
        # Couleurs
        # ----------------------------------------------------------------------

        self.couleur_grille = QColor(
            "#e5e7eb",
        )

        self.couleur_axe = QColor(
            "#9ca3af",
        )

        self.couleur_accent = QColor(
            "#10B981",
        )

    # 2.2 -- Chargement des données -------------------------------------------

    def set_donnees(
        self,
        data: list[dict],
        couleurs_voyages: dict | None = None,
        date_min: date | None = None,
        date_max: date | None = None,
        titre: str = "",
    ):
        """
        Charge des données déjà nettoyées et normalisées.

        Le widget graphique ne connaît donc plus :
            - les noms des colonnes d'origine ;
            - la structure du dictionnaire source ;
            - les règles de validation ;
            - la manière de convertir les dates.
        """

        self.init_avion()

        self.barre_survolee = None

        if couleurs_voyages is None:
            couleurs_voyages = {}

        # ----------------------------------------------------------------------
        # Création des barres
        # ----------------------------------------------------------------------

        self.barres = []

        for item in data:

            couleur = QColor(
                couleurs_voyages.get(
                    item["id"],
                    "#10B981",
                )
            )

            self.barres.append(
                {
                    "id": item["id"],
                    "label": item["label"],
                    "deb": item["deb"],
                    "fin": item["fin"],
                    "couleur": couleur,
                    "rect": None,
                }
            )

        # ----------------------------------------------------------------------
        # Bornes du graphique
        # ----------------------------------------------------------------------

        self.date_min = (
            date_min
            if date_min is not None
            else min(
                (barre["deb"] for barre in self.barres),
                default=date.today(),
            )
        )

        self.date_max = (
            date_max
            if date_max is not None
            else max(
                (barre["fin"] for barre in self.barres),
                default=date.today(),
            )
        )

        self.titre = titre

        # ----------------------------------------------------------------------
        # Mise à jour
        # ----------------------------------------------------------------------

        self._calculer_dimensions_barres()

        self.update()

    # 2.3 -- Animation de l'avion ---------------------------------------------

    def _animer_avion(
        self,
    ) -> None:
        """Fait avancer l'avion sur sa trajectoire."""

        if not self.barres:
            return

        delta_s = self._timer_avion.interval() / 1000

        self.avion.animer(
            delta_s=delta_s,
        )

        self.update()

    # 2.4 -- Calcul des dimensions des barres ----------------------------------

    def _calculer_dimensions_barres(
        self,
    ):

        nb = max(
            len(self.barres),
            1,
        )

        marges = self.MARGE_HAUT + self.MARGE_BAS

        unite_min = self.HAUTEUR_BARRE_MIN + self.ESPACE_BARRE_MIN

        hauteur_plancher = marges + nb * unite_min

        self.setMinimumHeight(int(hauteur_plancher))

        self._mettre_a_jour_taille_barres()

    # 2.5 -- Mise à jour de la taille des barres -------------------------------

    def _mettre_a_jour_taille_barres(
        self,
    ):

        nb = max(
            len(self.barres),
            1,
        )

        marges = self.MARGE_HAUT + self.MARGE_BAS

        hauteur_disponible = max(
            self.height() - marges,
            0,
        )

        unite_max = self.HAUTEUR_BARRE_MAX + self.ESPACE_BARRE_MAX

        unite_min = self.HAUTEUR_BARRE_MIN + self.ESPACE_BARRE_MIN

        unite = hauteur_disponible / nb if nb else unite_max

        unite = max(
            min(
                unite,
                unite_max,
            ),
            unite_min,
        )

        ratio_barre = self.HAUTEUR_BARRE_MAX / unite_max

        self.hauteur_barre = max(
            unite * ratio_barre,
            self.HAUTEUR_BARRE_MIN,
        )

        self.espace_barre = max(
            unite - self.hauteur_barre,
            self.ESPACE_BARRE_MIN,
        )

    # 2.6 -- Redimensionnement -------------------------------------------------

    def resizeEvent(
        self,
        event,
    ):

        self._mettre_a_jour_taille_barres()

        super().resizeEvent(
            event,
        )

    # 2.7 -- Conversion d'une date en position X -------------------------------

    def _x_pour_date(
        self,
        d: date,
        largeur_zone: float,
    ) -> float:

        if self.date_max == self.date_min:
            return self.MARGE_GAUCHE

        total = (self.date_max - self.date_min).days

        offset = (d - self.date_min).days

        return self.MARGE_GAUCHE + (offset / total) * largeur_zone

    # 2.8 -- Initialisation de l'avion -----------------------------------------

    def init_avion(
        self,
    ):

        avion_temp = (
            "rafale"
            if est_jour_militaire(
                date_jour=None,
            )
            else "ligne"
        )

        self.avion = Avion(
            avion=avion_temp,
            taille=50,
            vitesse=60,
            tension=1.0,
            marge_sortie=50,
        )

    # 2.9 -- Rendu -------------------------------------------------------------

    def paintEvent(
        self,
        event,
    ):

        painter = QPainter(
            self,
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
        )

        largeur = self.width()
        hauteur = self.height()

        largeur_zone = largeur - self.MARGE_GAUCHE - self.MARGE_DROITE

        # ----------------------------------------------------------------------
        # Titre
        # ----------------------------------------------------------------------

        if self.titre:

            font_titre = QFont()

            font_titre.setPointSize(
                13,
            )

            font_titre.setBold(
                True,
            )

            font_titre.setLetterSpacing(
                QFont.SpacingType.PercentageSpacing,
                102,
            )

            painter.setFont(
                font_titre,
            )

            painter.drawText(
                QRectF(
                    0,
                    8,
                    largeur,
                    25,
                ),
                Qt.AlignmentFlag.AlignHCenter,
                self.titre,
            )

            # ------------------------------------------------------------------
            # Petit trait décoratif
            # ------------------------------------------------------------------

            largeur_trait = 44
            y_trait = 34

            painter.setPen(
                QPen(
                    self.couleur_accent,
                    2,
                )
            )

            painter.drawLine(
                QPointF(
                    largeur / 2 - largeur_trait / 2,
                    y_trait,
                ),
                QPointF(
                    largeur / 2 + largeur_trait / 2,
                    y_trait,
                ),
            )

        # ----------------------------------------------------------------------
        # Pas de données
        # ----------------------------------------------------------------------

        if not self.barres or self.date_min is None or self.date_max is None:

            painter.end()

            return

        # ----------------------------------------------------------------------
        # Graduation de l'axe X
        # ----------------------------------------------------------------------

        painter.setFont(
            QFont(
                "",
                8,
            )
        )

        for d, texte in self._graduations_mensuelles():

            x = self._x_pour_date(
                d,
                largeur_zone,
            )

            painter.setPen(
                QPen(
                    self.couleur_grille,
                    1,
                )
            )

            painter.drawLine(
                QPointF(
                    x,
                    self.MARGE_HAUT - 5,
                ),
                QPointF(
                    x,
                    hauteur - self.MARGE_BAS,
                ),
            )

            painter.setPen(
                self.couleur_axe,
            )

            painter.drawText(
                QRectF(
                    x - 30,
                    hauteur - self.MARGE_BAS + 5,
                    60,
                    20,
                ),
                Qt.AlignmentFlag.AlignHCenter,
                texte,
            )

        # ----------------------------------------------------------------------
        # Barres + points traversés par l'avion
        # ----------------------------------------------------------------------

        rayon_arrondi = min(
            4,
            self.hauteur_barre / 2,
        )

        points_avion = []

        for i, barre in enumerate(self.barres):

            y = self.MARGE_HAUT + i * (self.hauteur_barre + self.espace_barre)

            x_deb = self._x_pour_date(
                barre["deb"],
                largeur_zone,
            )

            x_fin = self._x_pour_date(
                barre["fin"],
                largeur_zone,
            )

            largeur_barre = max(
                x_fin - x_deb,
                4,
            )

            rect = QRectF(
                x_deb,
                y,
                largeur_barre,
                self.hauteur_barre,
            )

            barre["rect"] = rect

            # ------------------------------------------------------------------
            # Points visités par l'avion :
            # début du voyage puis fin du voyage
            # ------------------------------------------------------------------

            points_avion.append(
                QPointF(
                    x_deb,
                    rect.center().y(),
                )
            )

            if x_deb < x_fin:

                points_avion.append(
                    QPointF(
                        x_fin,
                        rect.center().y(),
                    )
                )

            # ------------------------------------------------------------------
            # Barre
            # ------------------------------------------------------------------

            couleur = barre["couleur"]

            if barre is self.barre_survolee:

                couleur = couleur.lighter(
                    115,
                )

            painter.setPen(
                Qt.PenStyle.NoPen,
            )

            painter.setBrush(
                couleur,
            )

            painter.drawRoundedRect(
                rect,
                rayon_arrondi,
                rayon_arrondi,
            )

        # ----------------------------------------------------------------------
        # Avion
        # ----------------------------------------------------------------------

        # Zone dans laquelle sont tirées les hauteurs aléatoires
        # des points d'entrée et de sortie.

        rect_zone_avion = QRectF(
            0,
            self.MARGE_HAUT,
            largeur,
            max(
                0,
                hauteur - self.MARGE_HAUT - self.MARGE_BAS,
            ),
        )

        self.avion.dessiner(
            painter=painter,
            points_passage=points_avion,
            rect_zone=rect_zone_avion,
        )

        painter.end()

    # 2.10 -- Création des graduations mensuelles ------------------------------

    def _graduations_mensuelles(
        self,
    ):

        graduations = []

        courant = self.date_min.replace(
            day=1,
        )

        while courant <= self.date_max:

            graduations.append(
                (
                    courant,
                    courant.strftime("%b %Y"),
                )
            )

            annee = courant.year + courant.month // 12

            mois = courant.month % 12 + 1

            courant = courant.replace(
                year=annee,
                month=mois,
                day=1,
            )

        # ----------------------------------------------------------------------
        # Limite à environ 6 graduations
        # ----------------------------------------------------------------------

        if len(graduations) > 6:

            pas = len(graduations) // 6 + 1

            graduations = graduations[::pas]

        return graduations

    # 2.11 -- Gestion du survol ------------------------------------------------

    def mouseMoveEvent(
        self,
        event: QMouseEvent,
    ):

        pos = event.position()

        survol_precedent = self.barre_survolee

        self.barre_survolee = None

        for barre in self.barres:

            rect = barre.get(
                "rect",
            )

            if rect and rect.contains(pos):

                self.barre_survolee = barre

                texte = (
                    f"{barre['label']}\n"
                    f"{barre['deb'].strftime('%d/%m/%Y')} - "
                    f"{barre['fin'].strftime('%d/%m/%Y')}"
                )

                QToolTip.showText(
                    event.globalPosition().toPoint(),
                    texte,
                    self,
                )

                break

        if self.barre_survolee is None:

            QToolTip.hideText()

        if survol_precedent is not self.barre_survolee:

            self.update()

    # 2.12 -- Sortie de la souris ---------------------------------------------

    def leaveEvent(
        self,
        event,
    ):

        self.barre_survolee = None

        QToolTip.hideText()

        self.update()


# 3 -- Classe PyQt6 : onglet Calendrier des voyages ---------------------------


class CalendrierVisite(QWidget):

    # 3.1 -- Initialisation ----------------------------------------------------

    def __init__(
        self,
        fct_traduction,
        parent=None,
    ):

        super().__init__(
            parent=parent,
        )

        self.langue = "français"

        self.fct_traduction = fct_traduction

        # ----------------------------------------------------------------------
        # Voyages
        # ----------------------------------------------------------------------

        # Les données brutes ne sont pas conservées :
        # seule leur version propre et normalisée est utile à l'onglet.

        self.voyages_traites = []

        # Association :
        # identifiant du voyage -> couleur hexadécimale
        #
        # Cela évite que les couleurs changent lorsque l'utilisateur ne fait
        # que déplacer les bornes temporelles ou changer la langue.

        self.couleurs_voyages = {}

        # ----------------------------------------------------------------------
        # Style par défaut
        # ----------------------------------------------------------------------

        self.style = 1
        self.teinte = None
        self.nuances = {}

        # ----------------------------------------------------------------------
        # Dates de départ
        # ----------------------------------------------------------------------

        aujourdhui = date.today()

        try:

            date_il_y_a_un_an = aujourdhui.replace(
                year=aujourdhui.year - 1,
            )

        except ValueError:

            # Cas particulier du 29 février
            date_il_y_a_un_an = aujourdhui.replace(
                year=aujourdhui.year - 1,
                day=28,
            )

        # ----------------------------------------------------------------------
        # Début du graphique
        # ----------------------------------------------------------------------

        self.debut_voyage_label = QLabel()

        self.debut_voyage = SelecteurDate(
            parent=self,
            date=date_il_y_a_un_an.strftime("%Y-%m-%d"),
        )

        self.debut_voyage.dateChanged.connect(
            self.creer_graphique,
        )

        # ----------------------------------------------------------------------
        # Fin du graphique
        # ----------------------------------------------------------------------

        self.fin_voyage_label = QLabel()

        self.fin_voyage = SelecteurDate(
            parent=self,
            date=aujourdhui.strftime("%Y-%m-%d"),
        )

        self.fin_voyage.dateChanged.connect(
            self.creer_graphique,
        )

        # ----------------------------------------------------------------------
        # Disposition des dates
        # ----------------------------------------------------------------------

        layout_dates = QHBoxLayout()

        layout_dates.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )

        layout_dates.addWidget(
            self.debut_voyage_label,
        )

        layout_dates.addWidget(
            self.debut_voyage,
        )

        layout_dates.addSpacing(
            50,
        )

        layout_dates.addWidget(
            self.fin_voyage_label,
        )

        layout_dates.addWidget(
            self.fin_voyage,
        )

        # ----------------------------------------------------------------------
        # Diagramme
        # ----------------------------------------------------------------------

        self.diagramme = DiagrammeGantt(
            parent=self,
        )

        # ----------------------------------------------------------------------
        # Layout principal
        # ----------------------------------------------------------------------

        self.layout = QVBoxLayout(
            self,
        )

        self.layout.addLayout(
            layout_dates,
        )

        self.layout.addWidget(
            self.diagramme,
            stretch=1,
        )

    # 3.2 -- Mise à jour de la langue -----------------------------------------

    def set_langue(
        self,
        langue: str,
    ):

        self.langue = langue

        self.debut_voyage_label.setText(
            self.fct_traduction(
                "general_voyage_debut",
                suffixe=" :",
            )
        )

        self.fin_voyage_label.setText(
            self.fct_traduction(
                "general_voyage_fin",
                suffixe=" :",
            )
        )

        # Aucun retraitement des données
        # et aucune régénération des couleurs.

        self.creer_graphique()

    # 3.3 -- Mise à jour des voyages ------------------------------------------

    def set_voyages(
        self,
        voyages: dict,
    ):

        # ----------------------------------------------------------------------
        # Nettoyage effectué UNE SEULE FOIS
        # ----------------------------------------------------------------------

        self.voyages_traites = traiter_voyages(
            voyages=voyages,
            voyage_label="nom",
            date_min_label="date_debut",
            date_max_label="date_fin",
        )

        # ----------------------------------------------------------------------
        # Couleurs
        # ----------------------------------------------------------------------

        # Les couleurs déjà attribuées aux voyages existants sont conservées.
        # Seuls les nouveaux voyages reçoivent une nouvelle couleur.

        self._mettre_a_jour_couleurs_voyages(
            forcer=False,
        )

        # ----------------------------------------------------------------------
        # Graphique
        # ----------------------------------------------------------------------

        self.creer_graphique()

    # 3.4 -- Mise à jour du style ---------------------------------------------

    def set_style(
        self,
        style,
        teinte,
        nuances,
    ):

        self.style = style
        self.teinte = teinte
        self.nuances = nuances

        # Le thème change :
        # il est donc logique de recréer toutes les couleurs.

        self._mettre_a_jour_couleurs_voyages(
            forcer=True,
        )

        self.creer_graphique()

    # 3.5 -- Mise à jour des couleurs des voyages ------------------------------

    def _mettre_a_jour_couleurs_voyages(
        self,
        forcer: bool = False,
    ):
        """
        Affecte une couleur à chaque voyage.

        Si ``forcer`` vaut False, les couleurs existantes sont conservées.
        Si ``forcer`` vaut True, toutes les couleurs sont recréées.
        """

        if forcer:
            couleurs_precedentes = {}
        else:
            couleurs_precedentes = self.couleurs_voyages

        nouvelles_couleurs = {}

        for voyage in self.voyages_traites:

            identifiant = voyage["id"]

            if identifiant in couleurs_precedentes:

                couleur = couleurs_precedentes[identifiant]

            else:

                couleur = generer_couleur_aleatoire_hex(
                    preset=self.nuances,
                    teintes_autorisees=self.teinte,
                )

            nouvelles_couleurs[identifiant] = couleur

        self.couleurs_voyages = nouvelles_couleurs

    # 3.6 -- Création du graphique --------------------------------------------

    def creer_graphique(
        self,
    ):

        # ----------------------------------------------------------------------
        # Bornes temporelles
        # ----------------------------------------------------------------------

        # Seulement DEUX conversions de chaînes vers date à chaque mise à jour :
        # les dates sélectionnées par l'utilisateur.

        try:

            date_min = convertir_date(self.debut_voyage.obtenir_date_str())

            date_max = convertir_date(self.fin_voyage.obtenir_date_str())

        except (ValueError, TypeError):

            return

        # ----------------------------------------------------------------------
        # Filtrage
        # ----------------------------------------------------------------------

        # Ici, aucune donnée brute n'est reconstruite ou revalidée.
        # Les dates de tous les voyages sont déjà des datetime.date.

        voyages_affiches = filtrer_voyages(
            voyages=self.voyages_traites,
            date_min=date_min,
            date_max=date_max,
        )

        # ----------------------------------------------------------------------
        # Mise à jour du diagramme
        # ----------------------------------------------------------------------

        self.diagramme.set_donnees(
            data=voyages_affiches,
            couleurs_voyages=self.couleurs_voyages,
            date_min=date_min,
            date_max=date_max,
            titre=self.fct_traduction("titre_graphique_calendrier_voyages"),
        )
