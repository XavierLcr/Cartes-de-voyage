################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# 4.5 – Diagramme de Gantt                                                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------

from datetime import date, datetime

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QToolTip
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QMouseEvent

from _0_Utilitaires._0_10_selecteur_date import SelecteurDate
from _0_Utilitaires._0_2_fonctions_graphiques import generer_couleur_aleatoire_hex

# 1 -- Widget de dessin du Gantt -----------------------------------------------


class DiagrammeGantt(QWidget):
    """Widget PyQt6 natif qui dessine un diagramme de Gantt via QPainter."""

    MARGE_GAUCHE = 30
    MARGE_DROITE = 30
    MARGE_HAUT = 50
    MARGE_BAS = 40

    # Hauteur/espacement "confortables" utilisés tant qu'il y a peu de voyages
    HAUTEUR_BARRE_MAX = 22
    ESPACE_BARRE_MAX = 10

    # En dessous de ces valeurs, on préfère laisser le widget grandir
    # (et donc scroller) plutôt que de rendre les barres illisibles
    HAUTEUR_BARRE_MIN = 6
    ESPACE_BARRE_MIN = 2

    # Hauteur totale au-delà de laquelle on commence à affiner les barres
    HAUTEUR_GRAPHIQUE_MAX = 400

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMouseTracking(True)
        self.setMinimumHeight(200)

        self.barres = []  # liste de dicts : label, deb, fin, couleur, rect
        self.date_min = None
        self.date_max = None
        self.titre = ""
        self.barre_survolee = None

        # Dimensions effectives des barres, recalculées selon le nombre
        # de voyages à afficher (voir _calculer_dimensions_barres)
        self.hauteur_barre = self.HAUTEUR_BARRE_MAX
        self.espace_barre = self.ESPACE_BARRE_MAX

        self.couleur_grille = QColor("#e5e7eb")
        self.couleur_axe = QColor("#9ca3af")
        self.couleur_accent = QColor("#10B981")

    # -- Chargement des données --------------------------------------------

    def set_donnees(
        self,
        data,
        voyage_label: str,
        date_min_label: str,
        date_max_label: str,
        palette_couleurs: list,
        date_min: str | None = None,
        date_max: str | None = None,
        titre: str = "",
    ):

        liste_temp = []

        # Nettoyage (équivalent à la version matplotlib)
        for _, item in data.items():

            label_temp = item.get(voyage_label, "")
            deb_temp = item.get(date_min_label)
            fin_temp = item.get(date_max_label)

            if not label_temp or not deb_temp or not fin_temp:
                continue

            try:
                deb_temp = self._parse_date(deb_temp)
                fin_temp = self._parse_date(fin_temp)
            except (ValueError, TypeError):
                continue

            if date_min and fin_temp < self._parse_date(date_min):
                continue
            if date_max and deb_temp > self._parse_date(date_max):
                continue

            liste_temp.append({"label": label_temp, "deb": deb_temp, "fin": fin_temp})

        # Tri (même logique que l'original)
        liste_temp.sort(key=lambda x: (x["deb"], x["fin"], x["label"]))

        self.barres = []
        for i, item in enumerate(liste_temp):
            couleur = (
                QColor(palette_couleurs[i % len(palette_couleurs)])
                if palette_couleurs
                else QColor("#10B981")
            )
            self.barres.append(
                {
                    "label": item["label"],
                    "deb": item["deb"],
                    "fin": item["fin"],
                    "couleur": couleur,
                    "rect": None,
                }
            )

        self.date_min = (
            self._parse_date(date_min)
            if date_min
            else (min((b["deb"] for b in self.barres), default=date.today()))
        )
        self.date_max = (
            self._parse_date(date_max)
            if date_max
            else (max((b["fin"] for b in self.barres), default=date.today()))
        )
        self.titre = titre

        self._calculer_dimensions_barres()
        self.update()

    def _calculer_dimensions_barres(self):
        """Choisit la hauteur/espacement des barres pour que le graphique
        reste sous HAUTEUR_GRAPHIQUE_MAX, en affinant les barres si besoin.
        En dessous de HAUTEUR_BARRE_MIN/ESPACE_BARRE_MIN, on laisse plutôt
        le widget grandir (et donc scroller) pour rester lisible."""

        nb = max(len(self.barres), 1)
        marges = self.MARGE_HAUT + self.MARGE_BAS

        hauteur_confortable = marges + nb * (
            self.HAUTEUR_BARRE_MAX + self.ESPACE_BARRE_MAX
        )

        if hauteur_confortable <= self.HAUTEUR_GRAPHIQUE_MAX:
            self.hauteur_barre = self.HAUTEUR_BARRE_MAX
            self.espace_barre = self.ESPACE_BARRE_MAX
            hauteur_finale = hauteur_confortable
        else:
            # Espace disponible pour une "unité" barre + espace
            espace_disponible = self.HAUTEUR_GRAPHIQUE_MAX - marges
            unite_max = self.HAUTEUR_BARRE_MAX + self.ESPACE_BARRE_MAX
            unite_min = self.HAUTEUR_BARRE_MIN + self.ESPACE_BARRE_MIN
            unite = max(espace_disponible / nb, unite_min)

            # On garde le même ratio barre/espace que les valeurs "max"
            ratio_barre = self.HAUTEUR_BARRE_MAX / unite_max
            self.hauteur_barre = max(unite * ratio_barre, self.HAUTEUR_BARRE_MIN)
            self.espace_barre = max(unite - self.hauteur_barre, self.ESPACE_BARRE_MIN)

            hauteur_finale = marges + nb * (self.hauteur_barre + self.espace_barre)
            hauteur_finale = min(
                hauteur_finale, max(self.HAUTEUR_GRAPHIQUE_MAX, marges + unite_min)
            )

        self.setMinimumHeight(int(hauteur_finale))

    @staticmethod
    def _parse_date(valeur) -> date:
        if isinstance(valeur, datetime):
            return valeur.date()
        if isinstance(valeur, date):
            return valeur
        return datetime.strptime(str(valeur)[:10], "%Y-%m-%d").date()

    def _x_pour_date(self, d: date, largeur_zone: float) -> float:
        if self.date_max == self.date_min:
            return self.MARGE_GAUCHE
        total = (self.date_max - self.date_min).days
        offset = (d - self.date_min).days
        return self.MARGE_GAUCHE + (offset / total) * largeur_zone

    # -- Rendu ---------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        largeur = self.width()
        hauteur = self.height()
        largeur_zone = largeur - self.MARGE_GAUCHE - self.MARGE_DROITE

        # Titre
        if self.titre:
            font_titre = QFont()
            font_titre.setPointSize(13)
            font_titre.setBold(True)
            font_titre.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 102)
            painter.setFont(font_titre)
            painter.drawText(
                QRectF(0, 8, largeur, 25), Qt.AlignmentFlag.AlignHCenter, self.titre
            )

            # Petit trait d'accent centré sous le titre
            largeur_trait = 44
            y_trait = 34
            painter.setPen(QPen(self.couleur_accent, 2))
            painter.drawLine(
                QPointF(largeur / 2 - largeur_trait / 2, y_trait),
                QPointF(largeur / 2 + largeur_trait / 2, y_trait),
            )

        if not self.barres or self.date_min is None or self.date_max is None:
            painter.end()
            return

        # Graduation de l'axe X (mensuelle, comme AutoDateLocator)
        painter.setFont(QFont("", 8))
        for d, texte in self._graduations_mensuelles():
            x = self._x_pour_date(d, largeur_zone)
            painter.setPen(QPen(self.couleur_grille, 1))
            painter.drawLine(
                QPointF(x, self.MARGE_HAUT - 5),
                QPointF(x, hauteur - self.MARGE_BAS),
            )
            painter.setPen(self.couleur_axe)
            painter.drawText(
                QRectF(x - 30, hauteur - self.MARGE_BAS + 5, 60, 20),
                Qt.AlignmentFlag.AlignHCenter,
                texte,
            )

        # Barres
        rayon_arrondi = min(4, self.hauteur_barre / 2)
        for i, barre in enumerate(self.barres):
            y = self.MARGE_HAUT + i * (self.hauteur_barre + self.espace_barre)
            x_deb = self._x_pour_date(barre["deb"], largeur_zone)
            x_fin = self._x_pour_date(barre["fin"], largeur_zone)
            largeur_barre = max(x_fin - x_deb, 4)

            rect = QRectF(x_deb, y, largeur_barre, self.hauteur_barre)
            barre["rect"] = rect

            couleur = barre["couleur"]
            if barre is self.barre_survolee:
                couleur = couleur.lighter(115)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(couleur)
            painter.drawRoundedRect(rect, rayon_arrondi, rayon_arrondi)

        painter.end()

    def _graduations_mensuelles(self):
        graduations = []
        courant = self.date_min.replace(day=1)
        while courant <= self.date_max:
            graduations.append((courant, courant.strftime("%b %Y")))
            annee = courant.year + (courant.month // 12)
            mois = courant.month % 12 + 1
            courant = courant.replace(year=annee, month=mois, day=1)
        # Limite à ~6 graduations pour rester lisible
        if len(graduations) > 6:
            pas = len(graduations) // 6 + 1
            graduations = graduations[::pas]
        return graduations

    # -- Survol (remplace l'annotation matplotlib) ---------------------------

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()
        survol_precedent = self.barre_survolee
        self.barre_survolee = None

        for barre in self.barres:
            rect = barre.get("rect")
            if rect and rect.contains(pos):
                self.barre_survolee = barre
                texte = (
                    f"{barre['label']}\n"
                    f"{barre['deb'].strftime('%d/%m/%Y')} - "
                    f"{barre['fin'].strftime('%d/%m/%Y')}"
                )
                QToolTip.showText(event.globalPosition().toPoint(), texte, self)
                break

        if self.barre_survolee is None:
            QToolTip.hideText()

        if survol_precedent is not self.barre_survolee:
            self.update()

    def leaveEvent(self, event):
        self.barre_survolee = None
        QToolTip.hideText()
        self.update()


# 2 -- Classe PyQt6 : onglet Calendrier des voyages (mise à jour) --------------


class CalendrierVisite(QWidget):

    def __init__(self, fct_traduction, parent=None):
        super().__init__(parent=parent)

        self.langue = "français"
        self.fct_traduction = fct_traduction
        self.voyages = {}

        # Style par défaut
        self.style = 1
        self.teinte = None
        self.nuances = {}

        # Dates de départ
        aujourdhui = date.today()
        try:
            date_il_y_a_un_an = aujourdhui.replace(year=aujourdhui.year - 1)
        except ValueError:
            date_il_y_a_un_an = aujourdhui.replace(year=aujourdhui.year - 1, day=28)

        # Début du graphique
        self.debut_voyage_label = QLabel()
        self.debut_voyage = SelecteurDate(
            parent=self, date=date_il_y_a_un_an.strftime("%Y-%m-%d")
        )
        self.debut_voyage.dateChanged.connect(self.creer_graphique)

        # Fin du graphique
        self.fin_voyage_label = QLabel()
        self.fin_voyage = SelecteurDate(
            parent=self, date=date.today().strftime("%Y-%m-%d")
        )
        self.fin_voyage.dateChanged.connect(self.creer_graphique)

        # Disposition des dates
        layout_dates = QHBoxLayout()
        layout_dates.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_dates.addWidget(self.debut_voyage_label)
        layout_dates.addWidget(self.debut_voyage)
        layout_dates.addSpacing(50)
        layout_dates.addWidget(self.fin_voyage_label)
        layout_dates.addWidget(self.fin_voyage)

        # Widget du graphique (remplace le QHBoxLayout + conteneur matplotlib)
        self.diagramme = DiagrammeGantt(parent=self)

        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.addLayout(layout_dates)
        self.layout.addWidget(self.diagramme)

    def set_langue(self, langue: str):
        self.langue = langue
        self.debut_voyage_label.setText(
            self.fct_traduction("general_voyage_debut", suffixe=" :")
        )
        self.fin_voyage_label.setText(
            self.fct_traduction("general_voyage_fin", suffixe=" :")
        )
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

        if not self.voyages:
            self.diagramme.set_donnees(
                data={},
                voyage_label="nom",
                date_min_label="date_debut",
                date_max_label="date_fin",
                palette_couleurs=[],
            )
            return

        self.diagramme.set_donnees(
            data=self.voyages,
            voyage_label="nom",
            date_min_label="date_debut",
            date_max_label="date_fin",
            palette_couleurs=[
                generer_couleur_aleatoire_hex(
                    preset=self.nuances, teintes_autorisees=self.teinte
                )
                for _ in range(len(self.voyages.keys()))
            ],
            date_min=self.debut_voyage.obtenir_date_str(),
            date_max=self.fin_voyage.obtenir_date_str(),
            titre=self.fct_traduction("titre_graphique_calendrier_voyages"),
        )
