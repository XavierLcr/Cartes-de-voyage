################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/                                                   #
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

from _0_Utilitaires._0_1_Fonctions_utiles import (
    creer_ligne_separation,
    vider_layout,
    creer_QLabel_centre,
    renvoyer_groupbox,
)


class OngletResumeDestinations(QWidget):
    def __init__(
        self,
        traduire_depuis_id,
        constantes,
        parent=None,
    ):
        super().__init__(parent)

        self.traduire_depuis_id = traduire_depuis_id
        self.emojis_pays = constantes.emojis_pays
        self.noms_pays = constantes.pays_differentes_langues
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

    def set_mise_en_forme(self, coche: bool):
        self.mise_en_forme.setChecked(coche)

    def donner_mise_en_forme(self):
        return self.mise_en_forme.isChecked()

    def set_langue(self, nouvelle_langue):
        """Permet de mettre à jour la langue."""
        self.langue_utilisee = nouvelle_langue
        self.mise_en_forme.setText(
            self.traduire_depuis_id(clef="mise_en_forme_onglet_3")
        )
        self.maj_layout_resume()

    def _creer_scroll(self, vbox):
        widget = QWidget()
        widget.setLayout(vbox)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        return scroll

    def ajouter_partie_a_layout(self, granu, pays_donnees, vbox, affichage_groupe=True):

        vider_layout(vbox)

        vbox.addWidget(
            creer_QLabel_centre(
                text=self.traduire_depuis_id(clef=granu, prefixe="<b>", suffixe="</b>")
            )
        )

        vbox.addLayout(creer_ligne_separation())
        vbox.addWidget(QLabel(""))

        if pays_donnees is not None:
            for pays, items in sorted(
                pays_donnees.items(),
                key=lambda x: self.noms_pays.get(x[0], {}).get(
                    self.langue_utilisee, x[0]
                ),
            ):

                vbox.addWidget(
                    QLabel(
                        # Pays avec emoji
                        f"<b>{self.noms_pays.get(pays, {}).get(self.langue_utilisee, pays)}</b> {self.emojis_pays.get(pays, '')}: "
                        # Items si affichage regroupé
                        f"{', '.join(items) if affichage_groupe and items else '' if items else '⏳✒️'}",
                        wordWrap=True,
                    )
                )

                # items si affichage non regroupé
                if not affichage_groupe and items:
                    [
                        vbox.addWidget(QLabel(f"   • {item}", wordWrap=True))
                        for item in items
                    ]

                vbox.addWidget(
                    QLabel(
                        "—  —  —",
                        alignment=(
                            Qt.AlignmentFlag.AlignCenter
                            if affichage_groupe
                            else Qt.AlignmentFlag.AlignLeft
                        ),
                    )
                )

        vbox.addStretch()

    def maj_layout_resume(self):

        self.ajouter_partie_a_layout(
            granu="titre_regions_visitees",
            pays_donnees=self.dicts_granu.get("region", {}),
            vbox=self.layout_resume_regions,
            affichage_groupe=self.donner_mise_en_forme(),
        )
        self.ajouter_partie_a_layout(
            granu="titre_departements_visites",
            pays_donnees=self.dicts_granu.get("dep", {}),
            vbox=self.layout_resume_departements,
            affichage_groupe=self.donner_mise_en_forme(),
        )
