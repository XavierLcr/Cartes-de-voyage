################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4 – Création de l'onglet complet                                      #
################################################################################


from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
)

from _4_Interface._4_1_Onglets.onglet_4 import onglet_4_1_hemicycle, onglet_4_2_classement


class OngletTopPays(QWidget):
    def __init__(
        self,
        constantes,
        fct_traduction,
        table_superficie,
        parent,
    ):
        super().__init__(parent)

        self.mise_en_page = constantes.parametres_application["onglet_4_mise_en_page"]
        self.fonction_traduction = fct_traduction

        # === Création des pages

        ## === Onglet Hémicycle ===
        self.hemicycle = onglet_4_1_hemicycle.HemicycleWidget(
            constantes=constantes,
        )
        page_hemicycle = QWidget()
        layout_hemicycle = QVBoxLayout(page_hemicycle)
        layout_hemicycle.addWidget(self.hemicycle)

        ## === Onglet Classement ===
        self.classement_widget = onglet_4_2_classement.ClassementPays(
            constantes=constantes,
            table_superficie=table_superficie,
            fct_traduction=self.fonction_traduction,
        )

        # === Mise en page ===
        layout = QVBoxLayout(self)

        if self.mise_en_page == 0:

            ## === Stack (remplace QTabWidget) ===
            self.pages = QStackedWidget()
            self.pages.addWidget(page_hemicycle)  # index 0
            self.pages.addWidget(self.classement_widget)  # index 1

            # === Barre de boutons (navigation) ===
            btn_layout = QHBoxLayout()
            self.btn_hemicycle = QPushButton("Hémicycle")
            self.btn_top_pays = QPushButton("Top Pays")
            btn_layout.addWidget(self.btn_hemicycle)
            btn_layout.addWidget(self.btn_top_pays)

            # Connexions
            self.btn_hemicycle.clicked.connect(lambda: self.pages.setCurrentIndex(0))
            self.btn_top_pays.clicked.connect(lambda: self.pages.setCurrentIndex(1))

            # Layout principal
            layout.addLayout(btn_layout)
            layout.addWidget(self.pages)

        elif self.mise_en_page == 1:

            ## === Création du QTabWidget ===
            self.sous_onglets = QTabWidget()
            self.sous_onglets.addTab(page_hemicycle, "Hémicycle")
            self.sous_onglets.addTab(self.classement_widget, "Top Pays")

            ## === Layout principal ===
            layout.addWidget(self.sous_onglets)

    def set_dicts_granu(self, dict_nv):
        self.hemicycle.set_pays_visites(pays_visites=dict_nv)
        self.classement_widget.set_dicts_granu(dict_nv)

    def set_langue(self, nouvelle_langue):
        self.hemicycle.set_langue(langue=nouvelle_langue)
        self.classement_widget.set_langue(nouvelle_langue)

        texte_onglet_1 = self.fonction_traduction(
            "titre_sous_onglet_4_1",
            suffixe=(" 🗺️"),
        )
        texte_onglet_2 = self.fonction_traduction(
            "titre_sous_onglet_4_2",
            suffixe=(" 🏆"),
        )

        if self.mise_en_page == 0:
            self.btn_hemicycle.setText(texte_onglet_1)
            self.btn_top_pays.setText(texte_onglet_2)
        elif self.mise_en_page == 1:
            self.sous_onglets.setTabText(
                self.sous_onglets.indexOf(self.hemicycle.parentWidget()), texte_onglet_1
            )
            self.sous_onglets.setTabText(
                self.sous_onglets.indexOf(self.classement_widget), texte_onglet_2
            )
