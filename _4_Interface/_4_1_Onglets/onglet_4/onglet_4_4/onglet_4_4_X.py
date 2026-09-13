################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_4                                #
# Onglet 4.4.X – Pays visités le plus grand nombre de fois                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import (
    Qt,
    QRectF,
    QTimer,
)

from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QPainter,
)

from PyQt6.QtWidgets import (
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# A adapter selon l'emplacement choisi pour le premier script
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_4.onglet_4_4_01_drapeau import Drapeau
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_4.onglet_4_4_02_calculs import (
    compter_voyages_par_pays,
    limiter_nombre_pays,
    resoudre_chemin_drapeau,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_4.onglet_4_4_03_theme import (
    ThemeLeveeDrapeaux,
)
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_4.onglet_4_4_04_ciel import Ciel
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_4.onglet_4_4_05_sol import Sol
from _4_Interface._4_1_Onglets.onglet_4.onglet_4_4.onglet_4_4_06_montagnes import (
    Montagnes,
)

# 1 -- Widget graphique --------------------------------------------------------


class LeveeDrapeaux(QWidget):
    """
    Représentation du classement sous forme de drapeaux hissés à une hauteur
    proportionnelle au nombre de voyages.

    L'ensemble de la scène est dessiné dans le paintEvent du widget. Les
    drapeaux sont de simples objets graphiques et ne sont pas des QWidget.
    """

    INTERVALLE_ANIMATION_MS = 30

    def __init__(
        self,
        dossier_drapeaux: str,
        fct_traduction,
        palette_repli: list | None = None,
        couleur_accent: str = "#4A90A4",
        parent=None,
    ):

        super().__init__(parent=parent)

        # Données générales
        self.fct_traduction = fct_traduction
        self.dossier_drapeaux = dossier_drapeaux
        self.couleur_accent = QColor(couleur_accent)
        self.theme = ThemeLeveeDrapeaux()
        self.ciel = Ciel()
        self.sol = Sol(proportion_hauteur=0.4)
        self.montagnes = Montagnes(proportion_hauteur=0.32, n_couches=3)

        self.palette_repli = palette_repli or [
            "#7DC8E8",
            "#E15759",
            "#59A14F",
            "#B07AA1",
            "#EDC948",
            "#76B7B2",
        ]

        # Données du graphique
        self.labels = []
        self.valeurs = []
        self.traductions = []
        self.drapeaux = []

        # Animation globale
        self._temps_animation_ms = 0.0

        self._timer_animation = QTimer(self)
        self._timer_animation.setInterval(self.INTERVALLE_ANIMATION_MS)
        self._timer_animation.timeout.connect(self._animer)

        # Dimensionnement
        self.setMinimumHeight(300)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    # 2.1 -- Données -----------------------------------------------------------

    def set_donnees(
        self,
        labels: list,
        valeurs: list,
        traductions: list,
    ) -> None:
        """Crée les drapeaux correspondant aux données du classement."""

        self.labels = list(labels)
        self.valeurs = list(valeurs)
        self.traductions = list(traductions)

        self.drapeaux.clear()

        if len(self.valeurs) == 0:
            self._timer_animation.stop()
            self.update()
            return

        valeur_max = max(self.valeurs)

        for i, (label, valeur) in enumerate(
            zip(
                self.labels,
                self.valeurs,
            )
        ):

            ratio = valeur / valeur_max if valeur_max > 0 else 0.0

            drapeau = Drapeau(
                chemin_image=resoudre_chemin_drapeau(self.dossier_drapeaux, str(label)),
                couleur_repli=self.palette_repli[i % len(self.palette_repli)],
                ratio=ratio,
            )

            drapeau.demarrer_animation(duree_ms=900, delai_ms=i * 200)

            self.drapeaux.append(drapeau)

        self._temps_animation_ms = 0.0

        if not self._timer_animation.isActive():
            self._timer_animation.start()

        self.update()

    # 2.2 -- Animation ---------------------------------------------------------

    def _animer(self) -> None:
        """Fait avancer simultanément toutes les animations."""

        delta_ms = self.INTERVALLE_ANIMATION_MS
        delta_s = delta_ms / 1000

        self._temps_animation_ms += delta_ms

        for drapeau in self.drapeaux:

            drapeau.animer(temps_ecoule_ms=self._temps_animation_ms, delta_s=delta_s)

        self.update()

    # 2.3 -- Géométrie ---------------------------------------------------------

    def _rect_scene(self) -> QRectF:
        """Rectangle utile du graphique."""

        marge = 18

        return QRectF(
            marge,
            marge,
            max(0, self.width() - 2 * marge),
            max(0, self.height() - 2 * marge),
        )

    def _geometrie_scene(
        self,
        rect_scene: QRectF,
    ) -> dict:
        """Calcule les différentes zones de la scène."""

        hauteur_titre = 48
        hauteur_libelles = 55
        marge_titre_graphique = 10

        rect_titre = QRectF(
            rect_scene.left(),
            rect_scene.top(),
            rect_scene.width(),
            hauteur_titre,
        )

        rect_drapeaux = QRectF(
            rect_scene.left(),
            rect_titre.bottom() + marge_titre_graphique,
            rect_scene.width(),
            max(
                0,
                rect_scene.height()
                - hauteur_titre
                - hauteur_libelles
                - marge_titre_graphique,
            ),
        )

        rect_libelles = QRectF(
            rect_scene.left(),
            rect_drapeaux.bottom(),
            rect_scene.width(),
            hauteur_libelles,
        )

        return {
            "titre": rect_titre,
            "drapeaux": rect_drapeaux,
            "libelles": rect_libelles,
        }

    def _rectangles_drapeaux(
        self,
        rect_zone: QRectF,
    ) -> list[QRectF]:
        """Répartit horizontalement les drapeaux dans la zone disponible."""

        n = len(self.drapeaux)

        if n == 0:
            return []

        # Chaque drapeau reçoit un emplacement horizontal identique.
        largeur_case = rect_zone.width() / n

        # On conserve des drapeaux raisonnablement fins même sur grand écran.
        largeur_drapeau = min(
            115.0,
            largeur_case * 0.82,
        )

        hauteur_drapeau = min(
            rect_zone.height(),
            230.0,
        )

        y = rect_zone.bottom() - hauteur_drapeau

        rectangles = []

        for i in range(n):

            centre_x = rect_zone.left() + largeur_case * (i + 0.5)

            rectangles.append(
                QRectF(
                    centre_x - largeur_drapeau / 2,
                    y,
                    largeur_drapeau,
                    hauteur_drapeau,
                )
            )

        return rectangles

    # 2.4 -- Dessin du titre ---------------------------------------------------

    def _dessiner_titre(
        self,
        painter: QPainter,
        rect: QRectF,
    ) -> None:

        titre = self.fct_traduction("titre_graphique_n_voyages")

        if not titre:
            return

        texte = titre.upper()

        police = QFont(painter.font())

        police.setPointSize(12)
        police.setWeight(QFont.Weight.DemiBold)
        police.setLetterSpacing(
            QFont.SpacingType.PercentageSpacing,
            115,
        )

        painter.setFont(police)
        painter.setPen(QColor("#4A5A66"))

        metrics = QFontMetrics(police)

        hauteur_texte = metrics.height()

        rect_texte = QRectF(
            rect.left(),
            rect.top(),
            rect.width(),
            hauteur_texte + 4,
        )

        painter.drawText(
            rect_texte,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            texte,
        )

        # Petit trait décoratif sous le titre
        largeur_ligne = 46
        hauteur_ligne = 3

        x = rect.center().x() - largeur_ligne / 2
        y = rect_texte.bottom() + 5

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.couleur_accent)

        painter.drawRoundedRect(
            QRectF(
                x,
                y,
                largeur_ligne,
                hauteur_ligne,
            ),
            1.5,
            1.5,
        )

    # 2.5 -- Dessin des libellés ----------------------------------------------

    def _dessiner_libelles(
        self,
        painter: QPainter,
        rect_zone: QRectF,
    ) -> None:

        n = len(self.drapeaux)

        if n == 0:
            return

        largeur_case = rect_zone.width() / n

        for i, (traduction, valeur) in enumerate(
            zip(
                self.traductions,
                self.valeurs,
            )
        ):

            rect_case = QRectF(
                rect_zone.left() + i * largeur_case,
                rect_zone.top(),
                largeur_case,
                rect_zone.height(),
            )

            # Nom du pays
            police_nom = QFont(painter.font())

            police_nom.setPointSize(10)
            police_nom.setWeight(QFont.Weight.DemiBold)

            painter.setFont(police_nom)

            painter.setPen(QColor("#4A4A4A"))

            rect_nom = QRectF(
                rect_case.left() + 3,
                rect_case.top() + 3,
                rect_case.width() - 6,
                25,
            )

            painter.drawText(
                rect_nom,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                str(traduction),
            )

            # Nombre de voyages
            texte_valeur = (
                f"{int(valeur)} "
                f"{self.fct_traduction('voyage') if valeur <= 1 else self.fct_traduction('voyages')}"
            )

            police_valeur = QFont(painter.font())

            police_valeur.setPointSize(9)

            painter.setFont(police_valeur)

            painter.setPen(QColor("#888888"))

            rect_valeur = QRectF(
                rect_case.left() + 3,
                rect_case.top() + 28,
                rect_case.width() - 6,
                20,
            )

            painter.drawText(
                rect_valeur,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                texte_valeur,
            )

    # 2.6 -- Dessin ------------------------------------------------------------

    def paintEvent(self, event) -> None:

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect_scene = self._rect_scene()

        geometrie = self._geometrie_scene(rect_scene)

        # Ciel
        self.ciel.dessiner(
            painter=painter,
            rect=rect_scene,
            theme=self.theme,
        )

        # Montagnes
        self.montagnes.dessiner(
            painter=painter,
            rect_scene=rect_scene,
            theme=self.theme,
            proportion_sol=0.40,
        )

        # Sol
        self.sol.dessiner(
            painter=painter,
            rect_scene=rect_scene,
            theme=self.theme,
        )

        # Titre
        self._dessiner_titre(
            painter=painter,
            rect=geometrie["titre"],
        )

        # Drapeaux
        rectangles = self._rectangles_drapeaux(geometrie["drapeaux"])

        for drapeau, rect_drapeau in zip(
            self.drapeaux,
            rectangles,
        ):

            drapeau.dessiner(
                painter=painter,
                rect=rect_drapeau,
            )

        # Libellés temporaires
        self._dessiner_libelles(
            painter=painter,
            rect_zone=geometrie["libelles"],
        )

        painter.end()


# 2 -- Classe principale -------------------------------------------------------


class PaysLesPlusVisites(QWidget):

    def __init__(
        self,
        constantes,
        fct_traduction,
        parent=None,
    ):

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

        # Widget graphique, créé une seule fois
        self.graphique = LeveeDrapeaux(
            dossier_drapeaux=self.direction_donnees_drapeaux,
            fct_traduction=self.fct_traduction,
        )

        # Layout principal
        self.layout = QVBoxLayout(self)

        self.layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.layout.addWidget(self.graphique)

    # 2.1 -- Paramètres ---------------------------------------------------------

    def set_langue(
        self,
        langue: str,
    ) -> None:

        self.langue = langue
        self.creer_graphique()

    def set_voyages(
        self,
        voyages: dict,
    ) -> None:

        self.voyages = voyages
        self.creer_graphique()

    def set_style(
        self,
        style,
        teinte,
        nuances,
    ) -> None:

        self.style = style
        self.teinte = teinte
        self.nuances = nuances

        # Pour l'instant, le style n'est pas utilisé directement par
        # LeveeDrapeaux. Un simple repaint suffit donc.
        self.graphique.update()

    # 2.2 -- Mise à jour du graphique ------------------------------------------

    def creer_graphique(self) -> None:

        # Si aucun voyage n'est disponible, on vide simplement le graphique.
        if not self.voyages:

            self.graphique.set_donnees(
                labels=[],
                valeurs=[],
                traductions=[],
            )

            return

        # Calcul du classement des pays
        df_temp = compter_voyages_par_pays(
            dictionnaire_voyages=self.voyages,
            traductions=self.pays_trad,
            langue=self.langue,
        ).pipe(
            limiter_nombre_pays,
            n=self.n_pays,
            type=self.n_pays_limite_type,
            agreger=self.agreger,
        )

        # Mise à jour du widget existant
        self.graphique.set_donnees(
            labels=df_temp["pays"].to_list(),
            valeurs=df_temp["N"].to_list(),
            traductions=df_temp["pays_traduction"].to_list(),
        )
