################################################################################
# Projet de cartes de voyage                                                   #
# application/onglets                                                          #
# Onglet 3 – Résumé des pays visités                                           #
################################################################################


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QCheckBox,
)

from _0_Utilitaires._0_1_Fonctions_utiles import creer_ligne_separation


class OngletResumeDestinations(QWidget):
    def __init__(
        self,
        traduire_depuis_id,
        emojis_pays,
        parent=None,
    ):
        super().__init__(parent)

        self.traduire_depuis_id = traduire_depuis_id
        self.emojis_pays = emojis_pays
        self.dicts_granu = {"region": {}, "dep": {}}
        self.langue_utilisee = "français"

        self.layout_onglet_3 = QVBoxLayout()
        self.layout_resume_pays = QHBoxLayout()

        # Layout régions
        self.layout_resume_regions = QVBoxLayout()
        self.scroll_regions = self._creer_scroll(self.layout_resume_regions)

        # Layout départements
        self.layout_resume_departements = QVBoxLayout()
        self.scroll_departements = self._creer_scroll(self.layout_resume_departements)

        # Bouton de mise en forme
        self.mise_en_forme = QCheckBox()
        self.mise_en_forme.stateChanged.connect(self.maj_layout_resume)

        # Assembler les widgets
        self.layout_resume_pays.addWidget(self.scroll_regions)
        self.layout_resume_pays.addWidget(self.scroll_departements)

        self.layout_onglet_3.addLayout(self.layout_resume_pays)
        self.layout_onglet_3.addWidget(self.mise_en_forme)

        self.setLayout(self.layout_onglet_3)

    def set_dicts_granu(self, dict_nv: dict):
        """Permet de mettre à jour les sélections de destinations."""
        self.dicts_granu = dict_nv
        self.maj_layout_resume()

    def set_langue(self, nouvelle_langue):
        """Permet de mettre à jour la langue."""
        self.langue_utilisee = nouvelle_langue
        self.mise_en_forme.setText(self.traduire_depuis_id(clef="mise_en_forme_onglet_3"))
        self.maj_layout_resume()

    def _creer_scroll(self, vbox):
        widget = QWidget()
        widget.setLayout(vbox)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        return scroll

    def ajouter_partie_a_layout(self, granu, pays_donnees, vbox, affichage_groupe=True):
        label_titre = QLabel(
            self.traduire_depuis_id(clef=granu, prefixe="<b>", suffixe="</b>")
        )
        label_titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(label_titre)

        vbox.addLayout(creer_ligne_separation())
        vbox.addWidget(QLabel(""))

        for pays, items in pays_donnees.items():
            emoji_i = f"{self.emojis_pays.get(pays, '')} "

            if affichage_groupe:
                texte_items = ", ".join(items) if items else "Aucun élément"
                texte = f"<b>{pays}</b> {emoji_i}: {texte_items}"
                label = QLabel(texte)
                label.setWordWrap(True)
                vbox.addWidget(label)
            else:
                vbox.addWidget(QLabel(f"<b>{pays}</b> {emoji_i}:"))
                if items:
                    for item in items:
                        label = QLabel(f"   • {item}")
                        label.setWordWrap(True)
                        vbox.addWidget(label)

            label_sep = QLabel("– " * 3)
            label_sep.setAlignment(
                Qt.AlignmentFlag.AlignCenter
                if affichage_groupe
                else Qt.AlignmentFlag.AlignLeft
            )
            vbox.addWidget(label_sep)

        vbox.addStretch()

    def vider_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def maj_layout_resume(self):

        self.vider_layout(self.layout_resume_regions)
        self.vider_layout(self.layout_resume_departements)

        self.ajouter_partie_a_layout(
            "titre_regions_visitees",
            self.dicts_granu.get("region", {}),
            self.layout_resume_regions,
            affichage_groupe=self.mise_en_forme.isChecked(),
        )
        self.ajouter_partie_a_layout(
            "titre_departements_visites",
            self.dicts_granu.get("dep", {}),
            self.layout_resume_departements,
            affichage_groupe=self.mise_en_forme.isChecked(),
        )
