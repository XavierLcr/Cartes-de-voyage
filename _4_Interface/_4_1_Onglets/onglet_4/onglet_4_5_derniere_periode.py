################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# 4.5 – Diagramme de Gantt                                                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from dataclasses import dataclass
from datetime import date, datetime
from operator import attrgetter

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPen
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from _0_Utilitaires._0_10_selecteur_date import SelecteurDate
from _0_Utilitaires._0_2_fonctions_graphiques import generer_couleur_aleatoire_hex

# 1 -- Données ----------------------------------------------------------------


## 1.1 -- Structure d'un voyage normalisé --------------------------------------


@dataclass(frozen=True, slots=True)
class Voyage:
    """Voyage nettoyé : le widget graphique n'a plus rien à valider."""

    id: object
    label: str
    deb: date
    fin: date


## 1.2 -- Conversion d'une valeur en date --------------------------------------


def convertir_date(valeur) -> date:
    """
    Convertit une valeur en ``datetime.date``.

    Accepte ``datetime``, ``date`` ou toute valeur dont les 10 premiers
    caractères suivent le format ``YYYY-MM-DD``.
    """

    # ``datetime`` hérite de ``date`` : il doit donc être testé en premier.
    if isinstance(valeur, datetime):
        return valeur.date()

    if isinstance(valeur, date):
        return valeur

    return date.fromisoformat(str(valeur)[:10])


## 1.3 -- Nettoyage et normalisation des voyages --------------------------------


def traiter_voyages(
    voyages: dict,
    voyage_label: str = "nom",
    date_min_label: str = "date_debut",
    date_max_label: str = "date_fin",
) -> list[Voyage]:
    """
    Normalise les voyages une seule fois, triés chronologiquement.

    Les voyages sans nom, sans date ou avec une date invalide sont ignorés.
    """

    resultat = []

    for identifiant, item in voyages.items():

        label = item.get(voyage_label)
        debut = item.get(date_min_label)
        fin = item.get(date_max_label)

        if not (label and debut and fin):
            continue

        try:
            resultat.append(
                Voyage(
                    identifiant,
                    str(label),
                    convertir_date(debut),
                    convertir_date(fin),
                )
            )
        except (ValueError, TypeError):
            continue

    resultat.sort(key=attrgetter("deb", "fin", "label"))

    return resultat


## 1.4 -- Filtrage selon la période affichée ------------------------------------


def filtrer_voyages(
    voyages: list[Voyage],
    date_min: date,
    date_max: date,
) -> list[Voyage]:
    """Conserve les voyages qui intersectent la période demandée."""

    return [v for v in voyages if v.fin >= date_min and v.deb <= date_max]


# 2 -- Widget de dessin du Gantt -----------------------------------------------


class DiagrammeGantt(QWidget):
    """Widget PyQt6 natif qui dessine un diagramme de Gantt via QPainter."""

    MARGE_GAUCHE = 30
    MARGE_DROITE = 30
    MARGE_HAUT = 50
    MARGE_BAS = 40

    # Barre + espace "confortables" quand la place ne manque pas
    HAUTEUR_BARRE_MAX = 22
    ESPACE_BARRE_MAX = 10

    # Valeurs minimales pour garder les barres lisibles
    HAUTEUR_BARRE_MIN = 6
    ESPACE_BARRE_MIN = 2

    UNITE_MAX = HAUTEUR_BARRE_MAX + ESPACE_BARRE_MAX
    UNITE_MIN = HAUTEUR_BARRE_MIN + ESPACE_BARRE_MIN

    LARGEUR_BARRE_MIN = 4
    NB_GRADUATIONS_MAX = 6

    # 2.1 -- Initialisation ----------------------------------------------------

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        self.setMouseTracking(True)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        # Données : liste de (Voyage, QColor)
        self._barres: list[tuple[Voyage, QColor]] = []
        self._graduations: list[tuple[date, str]] = []
        self._survol: int | None = None

        self.date_min = date.today()
        self.date_max = date.today()
        self._nb_jours = 1
        self.titre = ""

        # Objets de dessin créés une seule fois (et non à chaque paintEvent)
        self.couleur_accent = QColor("#10B981")

        self._pen_grille = QPen(QColor("#e5e7eb"), 1)
        self._pen_axe = QPen(QColor("#9ca3af"), 1)
        self._pen_accent = QPen(self.couleur_accent, 2)

        self._font_titre = QFont()
        self._font_titre.setPointSize(13)
        self._font_titre.setBold(True)
        self._font_titre.setLetterSpacing(
            QFont.SpacingType.PercentageSpacing,
            102,
        )

        self._font_axe = QFont()
        self._font_axe.setPointSize(8)

    # 2.2 -- Chargement des données -------------------------------------------

    def set_donnees(
        self,
        voyages: list[Voyage],
        couleurs: dict[object, QColor] | None = None,
        date_min: date | None = None,
        date_max: date | None = None,
        titre: str = "",
    ):
        """Charge des voyages déjà normalisés et leurs couleurs (QColor)."""

        couleurs = couleurs or {}

        self._barres = [(v, couleurs.get(v.id, self.couleur_accent)) for v in voyages]
        self._survol = None
        self.titre = titre

        aujourdhui = date.today()

        self.date_min = date_min or min(
            (v.deb for v in voyages),
            default=aujourdhui,
        )
        self.date_max = date_max or max(
            (v.fin for v in voyages),
            default=aujourdhui,
        )

        # Calculs qui ne dépendent que des données : faits ici, pas au rendu
        self._nb_jours = max((self.date_max - self.date_min).days, 1)
        self._graduations = self._calculer_graduations()

        self.setMinimumHeight(
            self.MARGE_HAUT
            + self.MARGE_BAS
            + max(len(self._barres), 1) * self.UNITE_MIN
        )

        self.update()

    # 2.3 -- Graduations mensuelles --------------------------------------------

    def _calculer_graduations(self) -> list[tuple[date, str]]:
        """Premiers de chaque mois compris dans la période (~6 maximum)."""

        d_min, d_max = self.date_min, self.date_max

        # Indice absolu de mois : premier mois dont le 1er est >= date_min
        premier = d_min.year * 12 + d_min.month - 1 + (d_min.day != 1)
        dernier = d_max.year * 12 + d_max.month - 1

        graduations = [
            (
                date(indice // 12, indice % 12 + 1, 1),
                date(indice // 12, indice % 12 + 1, 1).strftime("%b %Y"),
            )
            for indice in range(premier, dernier + 1)
        ]

        pas = -(-len(graduations) // self.NB_GRADUATIONS_MAX) or 1

        return graduations[::pas]

    # 2.4 -- Géométrie ---------------------------------------------------------

    def _geometrie(self) -> tuple[float, float, float]:
        """
        Renvoie ``(hauteur_barre, pas_vertical, largeur_zone)``.

        Calculé à la demande (opération arithmétique triviale) : aucun état
        à synchroniser lors des redimensionnements.
        """

        unite = (self.height() - self.MARGE_HAUT - self.MARGE_BAS) / max(
            len(self._barres),
            1,
        )
        unite = min(max(unite, self.UNITE_MIN), self.UNITE_MAX)

        hauteur = max(
            unite * self.HAUTEUR_BARRE_MAX / self.UNITE_MAX,
            self.HAUTEUR_BARRE_MIN,
        )
        espace = max(unite - hauteur, self.ESPACE_BARRE_MIN)

        largeur_zone = self.width() - self.MARGE_GAUCHE - self.MARGE_DROITE

        return hauteur, hauteur + espace, largeur_zone

    def _x_pour_date(self, d: date, largeur_zone: float) -> float:
        """Position X d'une date, bornée à la zone affichée."""

        offset = min(max((d - self.date_min).days, 0), self._nb_jours)

        return self.MARGE_GAUCHE + offset / self._nb_jours * largeur_zone

    def _rect_barre(
        self,
        i: int,
        voyage: Voyage,
        geometrie: tuple[float, float, float],
    ) -> QRectF:
        """Rectangle de la i-ème barre (source unique : rendu ET survol)."""

        hauteur, pas, largeur_zone = geometrie

        x_deb = self._x_pour_date(voyage.deb, largeur_zone)
        x_fin = self._x_pour_date(voyage.fin, largeur_zone)

        return QRectF(
            x_deb,
            self.MARGE_HAUT + i * pas,
            max(x_fin - x_deb, self.LARGEUR_BARRE_MIN),
            hauteur,
        )

    # 2.5 -- Rendu -------------------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._dessiner_titre(painter)

        if self._barres:

            geometrie = self._geometrie()

            self._dessiner_graduations(painter, geometrie[2])
            self._dessiner_barres(painter, geometrie)

        painter.end()

    def _dessiner_titre(self, painter: QPainter):

        if not self.titre:
            return

        largeur = self.width()

        painter.setFont(self._font_titre)
        painter.drawText(
            QRectF(0, 8, largeur, 25),
            Qt.AlignmentFlag.AlignHCenter,
            self.titre,
        )

        # Petit trait décoratif
        painter.setPen(self._pen_accent)
        painter.drawLine(
            QPointF(largeur / 2 - 22, 34),
            QPointF(largeur / 2 + 22, 34),
        )

    def _dessiner_graduations(self, painter: QPainter, largeur_zone: float):

        bas = self.height() - self.MARGE_BAS

        positions = [
            (self._x_pour_date(d, largeur_zone), texte)
            for d, texte in self._graduations
        ]

        # Lignes de grille, puis textes : un seul changement de stylo chacun
        painter.setPen(self._pen_grille)

        for x, _ in positions:
            painter.drawLine(
                QPointF(x, self.MARGE_HAUT - 5),
                QPointF(x, bas),
            )

        painter.setFont(self._font_axe)
        painter.setPen(self._pen_axe)

        for x, texte in positions:
            painter.drawText(
                QRectF(x - 30, bas + 5, 60, 20),
                Qt.AlignmentFlag.AlignHCenter,
                texte,
            )

    def _dessiner_barres(self, painter: QPainter, geometrie):

        rayon = min(4, geometrie[0] / 2)

        painter.setPen(Qt.PenStyle.NoPen)

        for i, (voyage, couleur) in enumerate(self._barres):

            painter.setBrush(couleur.lighter(115) if i == self._survol else couleur)
            painter.drawRoundedRect(
                self._rect_barre(i, voyage, geometrie),
                rayon,
                rayon,
            )

    # 2.6 -- Gestion du survol -------------------------------------------------

    def _barre_sous_curseur(self, pos: QPointF) -> int | None:
        """
        Indice de la barre située sous ``pos``, ou None.

        La ligne est déduite directement de Y : pas de parcours de toutes les
        barres, donc coût constant quel que soit le nombre de voyages.
        """

        geometrie = self._geometrie()

        i = int((pos.y() - self.MARGE_HAUT) // geometrie[1])

        if not 0 <= i < len(self._barres):
            return None

        rect = self._rect_barre(i, self._barres[i][0], geometrie)

        return i if rect.contains(pos) else None

    def mouseMoveEvent(self, event: QMouseEvent):

        i = self._barre_sous_curseur(event.position())

        if i is None:

            QToolTip.hideText()

        else:

            voyage = self._barres[i][0]

            QToolTip.showText(
                event.globalPosition().toPoint(),
                f"{voyage.label}\n" f"{voyage.deb:%d/%m/%Y} - {voyage.fin:%d/%m/%Y}",
                self,
            )

        if i != self._survol:

            self._survol = i
            self.update()

    def leaveEvent(self, event):

        QToolTip.hideText()

        if self._survol is not None:

            self._survol = None
            self.update()

        super().leaveEvent(event)


# 3 -- Classe PyQt6 : onglet Calendrier des voyages ---------------------------


class CalendrierVisite(QWidget):

    # 3.1 -- Initialisation ----------------------------------------------------

    def __init__(
        self,
        fct_traduction,
        parent=None,
    ):

        super().__init__(parent=parent)

        self.langue = "français"
        self.fct_traduction = fct_traduction

        # Voyages normalisés (les données brutes ne sont pas conservées)
        self.voyages_traites: list[Voyage] = []

        # identifiant du voyage -> QColor
        # Les couleurs survivent aux changements de bornes ou de langue.
        self.couleurs_voyages: dict[object, QColor] = {}

        # Style par défaut
        self.style = 1
        self.teinte = None
        self.nuances = {}

        # Sélecteurs de dates : de "il y a un an" à aujourd'hui
        aujourdhui = date.today()

        try:
            il_y_a_un_an = aujourdhui.replace(year=aujourdhui.year - 1)
        except ValueError:  # 29 février
            il_y_a_un_an = aujourdhui.replace(year=aujourdhui.year - 1, day=28)

        self.debut_voyage_label = QLabel()
        self.debut_voyage = SelecteurDate(
            parent=self,
            date=il_y_a_un_an.isoformat(),
        )

        self.fin_voyage_label = QLabel()
        self.fin_voyage = SelecteurDate(
            parent=self,
            date=aujourdhui.isoformat(),
        )

        self.debut_voyage.dateChanged.connect(self.creer_graphique)
        self.fin_voyage.dateChanged.connect(self.creer_graphique)

        # Disposition
        layout_dates = QHBoxLayout()
        layout_dates.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_dates.addWidget(self.debut_voyage_label)
        layout_dates.addWidget(self.debut_voyage)
        layout_dates.addSpacing(50)
        layout_dates.addWidget(self.fin_voyage_label)
        layout_dates.addWidget(self.fin_voyage)

        self.diagramme = DiagrammeGantt(parent=self)

        # Nommé ``layout_principal`` : ``self.layout`` masquerait la méthode
        # ``QWidget.layout()``.
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.addLayout(layout_dates)
        self.layout_principal.addWidget(self.diagramme, stretch=1)

    # 3.2 -- Mise à jour de la langue -----------------------------------------

    def set_langue(self, langue: str):

        self.langue = langue

        self.debut_voyage_label.setText(
            self.fct_traduction("general_voyage_debut", suffixe=" :")
        )
        self.fin_voyage_label.setText(
            self.fct_traduction("general_voyage_fin", suffixe=" :")
        )

        self.creer_graphique()

    # 3.3 -- Mise à jour des voyages ------------------------------------------

    def set_voyages(self, voyages: dict):

        self.voyages_traites = traiter_voyages(voyages)

        # Les voyages déjà connus gardent leur couleur
        self._mettre_a_jour_couleurs_voyages(forcer=False)

        self.creer_graphique()

    # 3.4 -- Mise à jour du style ---------------------------------------------

    def set_style(self, style, teinte, nuances):

        self.style = style
        self.teinte = teinte
        self.nuances = nuances

        # Le thème change : toutes les couleurs sont recréées
        self._mettre_a_jour_couleurs_voyages(forcer=True)

        self.creer_graphique()

    # 3.5 -- Couleurs des voyages ---------------------------------------------

    def _mettre_a_jour_couleurs_voyages(self, forcer: bool = False):
        """
        Affecte une couleur (QColor) à chaque voyage.

        Si ``forcer`` vaut False, les couleurs existantes sont conservées ;
        sinon toutes sont recréées. Les voyages disparus sont purgés.
        """

        anciennes = {} if forcer else self.couleurs_voyages

        self.couleurs_voyages = {
            v.id: (
                anciennes[v.id]
                if v.id in anciennes
                else QColor(
                    generer_couleur_aleatoire_hex(
                        preset=self.nuances,
                        teintes_autorisees=self.teinte,
                    )
                )
            )
            for v in self.voyages_traites
        }

    # 3.6 -- Création du graphique --------------------------------------------

    def creer_graphique(self):

        try:
            date_min = convertir_date(self.debut_voyage.obtenir_date_str())
            date_max = convertir_date(self.fin_voyage.obtenir_date_str())
        except (ValueError, TypeError):
            return

        self.diagramme.set_donnees(
            voyages=filtrer_voyages(self.voyages_traites, date_min, date_max),
            couleurs=self.couleurs_voyages,
            date_min=date_min,
            date_max=date_max,
            titre=self.fct_traduction("titre_graphique_calendrier_voyages"),
        )
