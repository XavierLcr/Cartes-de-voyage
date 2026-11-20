################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1.8 – Widget contenant la barre de progression ou l'animation légère  #                                 #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtWidgets import QWidget, QVBoxLayout

from _4_Interface._4_1_Onglets.onglet_1.onglet_1_6_animation_legere import (
    AnimationCreationLegere,
)
from _4_Interface._4_1_Onglets.onglet_1.onglet_1_7_barre_progression import (
    BarreProgressionVoyage,
)

# 1 -- Classe de sélection -----------------------------------------------------


class ProgressionCreationLocale(QWidget):
    """
    Conteneur permettant de choisir entre deux représentations de la progression.

    Modes disponibles :
        - "classique" : barre de progression traditionnelle.
        - "animation" : animation avec avion.

    API commune :
        set_texte_haut(texte)
        set_texte_bas(texte)
        set_maximum(maximum)
        set_valeur(valeur)
        set_theme(theme)
        demarrer()
        arreter()
    """

    MODES = ("classique", "animation")

    def __init__(
        self,
        mode="classique",
        parent=None,
        theme=1,
    ):

        super().__init__(parent)

        if mode not in self.MODES:
            raise ValueError(
                f"Mode inconnu : {mode}. " f"Modes disponibles : {self.MODES}"
            )

        self.mode = mode
        self.theme = theme

        self._creer_widget()
        self._creer_interface()

    # 1.1 -- Création du widget -----------------------------------------------

    def _creer_widget(self):

        if self.mode == "classique":
            self.widget = BarreProgressionVoyage(theme=self.theme)
        else:
            self.widget = AnimationCreationLegere()

    # 1.2 -- Interface ---------------------------------------------------------

    def _creer_interface(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.widget)

    # 1.3 -- API commune : textes ---------------------------------------------

    def set_texte_haut(self, texte):

        self.widget.set_texte_haut(texte)

    # -------------------------------------------------------------------------

    def set_texte_bas(self, texte):

        self.widget.set_texte_bas(texte)

    # 1.4 -- API commune : progression ----------------------------------------

    def set_maximum(self, maximum):

        self.widget.set_maximum(maximum)

    # -------------------------------------------------------------------------

    def set_valeur(self, valeur):

        self.widget.set_valeur(valeur)

    # 1.5 -- Contrôle de l'animation ------------------------------------------

    def demarrer(self):

        if hasattr(self.widget, "demarrer"):
            self.widget.demarrer()

    # -------------------------------------------------------------------------

    def arreter(self):

        if hasattr(self.widget, "arreter"):
            self.widget.arreter()

    # 1.6 -- Contrôle du thème -------------------------------------------------

    def set_style(self, style):

        if hasattr(self.widget, "set_style"):
            self.widget.set_style(style="clair" if style == 1 else "sombre")
