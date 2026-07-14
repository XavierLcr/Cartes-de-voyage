################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/                                          #
# Onglet 4.7 – Groupbox de création d'un portrait IA du profil                 #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import re
from textwrap import dedent

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QPushButton,
    QComboBox,
    QWidget,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    vider_layout,
    creer_QLabel_centre,
    creer_scroll,
    creer_ligne_verticale,
)
from _0_Utilitaires._0_13_LLM import LLMClient, tester_ollama
from clefs_et_mots_de_passe import modeles_compatibles_ollama

# 1 -- Fonction de simplification des voyages ----------------------------------


def compacter_voyages(voyages: dict) -> str:
    """
    Transforme les voyages en texte compact pour un LLM.
    """

    lignes = []

    for nom, infos in voyages.items():
        elements = [infos.get("nom", nom)]

        # Gestion des dates
        debut = infos.get("date_debut")
        fin = infos.get("date_fin")

        if debut and fin:
            if debut == fin:
                elements.append(f"({debut})")
            else:
                elements.append(f"({debut}→{fin})")
        elif debut:
            elements.append(f"({debut})")
        elif fin:
            elements.append(f"(→{fin})")

        # Gestion des destinations
        destinations = []

        for pays, villes in infos.get("dep", {}).items():
            if villes:
                destinations.append(f"{pays}/{','.join(villes)}")
            else:
                destinations.append(pays)
        for pays, villes in infos.get("region", {}).items():
            if villes:
                destinations.append(f"{pays}/{','.join(villes)}")
            else:
                destinations.append(pays)

        if destinations:
            elements.append(": " + ";".join(destinations))

        lignes.append(" ".join(elements))

    return "\n".join(lignes)


# 2 -- Classe d'un Worker pour un Thread ---------------------------------------


class ProfilLLMWorker(QThread):
    resultat = pyqtSignal(str)
    erreur = pyqtSignal(str)

    def __init__(self, modele, contexte, langue, voyages, timeout, url):
        super().__init__()

        self.modele = modele
        self.contexte = contexte
        self.langue = langue
        self.voyages = voyages
        self.timout = timeout
        self.url = url

    def run(self):
        try:
            profil_LLM = LLMClient(
                model=self.modele,
                url=self.url,
                timeout=self.timout,
                contexte=self.contexte,
                temperature=0.5,
            )

            profil_LLM.set_langue(langue=self.langue)
            profil_LLM.set_data(data=self.voyages)

            profil_LLM.set_prompt(prompt=dedent("""
                Tu es un spécialiste des voyages.

                À partir de l'historique fourni,
                écris un portrait du voyageur.

                Analyse le profil du voyageur selon les axes suivants :

                - Ses habitudes :
                Analyse la fréquence et la régularité de ses voyages,
                les périodes où il voyage le plus, la répartition entre
                courts séjours et voyages plus longs, les types d'occasions
                qui déclenchent ses déplacements.

                - Ses destinations favorites :
                Identifie les pays, régions ou zones géographiques qui
                reviennent le plus souvent dans son historique.
                Distingue les destinations fréquentes des visites ponctuelles.

                - Son style de voyage :
                Analyse les caractéristiques observables :
                types de destinations, diversité géographique, voyages avec
                des proches lorsque cela est explicitement indiqué,
                séjours urbains, nature, road trips ou expériences particulières.

                - Ses évolutions dans le temps :
                Analyse les changements visibles au fil des années :
                évolution de la fréquence, nouvelles zones visitées,
                apparition de nouveaux types de voyages.

                Règle d'interprétation :
                Une tendance doit être appuyée par plusieurs éléments.
                Une seule occurrence ne suffit pas pour conclure à une
                préférence ou une habitude.

                Style :
                - Adresse-toi directement au voyageur avec "vous".
                - Ton chaleureux, positif et naturel.
                - Texte fluide de 3 à 4 phrases.
                - Pas de listes à puces.
                - Reste factuel et nuancé.

                Ne fabrique aucune information.
                Ne parle que des voyages effectués.
            """))

            profil_LLM.creer_prompt_profil()

            resultat_temp = profil_LLM.generate()

            self.resultat.emit(resultat_temp)

        except Exception as e:
            self.erreur.emit(str(e))


# 3 -- Classe du GroupBox PyQt6 ------------------------------------------------


class ProfilVoyageurIA(QGroupBox):

    langue = "français"
    contexte = 32768
    voyages = {}
    url = "http://localhost:11434/api/generate"
    clef_probleme = "probleme_label_4_7_ollama"

    # Palette « papier ancien » pour l'affichage du portrait sous forme de lettre
    couleur_fond_pupitre = "#EFE3C8"  # Fond derrière la feuille (léger contraste)
    couleur_papier = "#F5ECD7"  # Couleur de la feuille elle-même
    couleur_bord_papier = "#D8C6A1"  # Bordure sépia de la feuille
    couleur_encre = "#3B2B20"  # Couleur du texte, façon encre brune
    police_script = (
        '"Segoe Script", "Lucida Handwriting", "Segoe Print", '
        '"Brush Script MT", "Bradley Hand", "Comic Sans MS", cursive'
    )

    def __init__(self, fct_traduction, parent=None):
        super().__init__(parent=parent)

        self.fonction_traduction = fct_traduction
        test_ollama = tester_ollama(url=re.match(r"^([^\d]*\d*)", self.url).group(1))

        self.widget_lancement = QWidget()
        layout_lancement = QHBoxLayout(self.widget_lancement)
        self.creer_description_profil_btn = QPushButton("Créer votre profil")
        self.creer_description_profil_btn.clicked.connect(self.creer_descriptif)
        self.modele = QComboBox()
        layout_lancement.addWidget(self.creer_description_profil_btn, stretch=4)
        layout_lancement.addWidget(creer_ligne_verticale())
        layout_lancement.addWidget(self.modele, stretch=1)

        layout_temp = QVBoxLayout()
        self.layout_description_profil = QVBoxLayout()
        self.initialiser_onglet()
        self.attente_label = creer_QLabel_centre(wordWrap=True)
        self.attente_label.hide()
        self.probleme_label = creer_QLabel_centre(
            wordWrap=True,
            alignement=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )

        if test_ollama.get("disponible", False) == False:

            self.clef_probleme = "probleme_label_4_7_ollama"
            layout_temp.addWidget(self.probleme_label)

        elif (
            self.lister_modeles(liste_modeles_dispo=test_ollama.get("modeles", []))
            == False
        ):

            self.clef_probleme = "probleme_label_4_7_modele"
            layout_temp.addWidget(self.probleme_label)
            layout_temp.addStretch()

        else:
            layout_temp.addWidget(self.widget_lancement)
            layout_temp.addWidget(self.attente_label)
            layout_temp.addLayout(self.layout_description_profil)

        self.setLayout(layout_temp)

    def lister_modeles(self, liste_modeles_dispo):
        """
        Sélectionne automatiquement le meilleur modèle disponible.
        """

        modele_temp = []
        modeles_dispo = set(liste_modeles_dispo)
        ok_temp = False

        for liste_modeles in modeles_compatibles_ollama.values():
            for modele in liste_modeles:
                if modele in modeles_dispo:
                    modele_temp.append(modele)
                    ok_temp = True

        self.modele.addItems(modele_temp)
        return ok_temp

    def set_langue(self, langue):
        self.langue = langue

        self.setTitle(self.fonction_traduction("groupbox_description_profil"))
        self.creer_description_profil_btn.setText(
            self.fonction_traduction("creer_description_profil_btn")
        )
        self.attente_label.setText(
            self.fonction_traduction("attente_label_4_7", prefixe="🔮 ", suffixe="...")
        )

        texte_temp = ""

        for categorie, modeles in modeles_compatibles_ollama.items():
            texte_temp += (
                f"\n  • {self.fonction_traduction(categorie, depuis_id=False)}\n"
            )
            texte_temp += "\n".join(f"      - {modele}" for modele in modeles)
            texte_temp += "\n"
        self.probleme_label.setText(
            self.fonction_traduction(
                clef=self.clef_probleme,
                prefixe="⚠️ ",
                suffixe=texte_temp,
            )
        )

        self.modele.setToolTip(
            self.fonction_traduction("modele_4_7_tooltip", suffixe=f" :{texte_temp}")
        )

    def set_voyages(self, voyages: dict):

        self.voyages = compacter_voyages(voyages)

    def creer_descriptif(self):

        self.widget_lancement.hide()
        self.attente_label.show()

        self.thread_profil = ProfilLLMWorker(
            modele=self.modele.currentText(),
            contexte=self.contexte,
            langue=self.langue,
            voyages=self.voyages,
            timeout=None,
            url=self.url,
        )

        self.thread_profil.resultat.connect(self.maj_interface_descriptif)
        self.thread_profil.erreur.connect(self.maj_interface_descriptif)

        self.thread_profil.start()

    def maj_interface_descriptif(self, descriptif):

        vider_layout(layout=self.layout_description_profil)

        # -- La "feuille de lettre" : le texte du portrait, en encre sur papier --
        label_temp = creer_QLabel_centre(
            text=descriptif,
            wordWrap=True,
            alignement=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )
        label_temp.setStyleSheet(f"""
            QLabel {{
                font-family: {self.police_script};
                font-size: 19px;
                font-weight: 400;
                color: {self.couleur_encre};
                background-color: {self.couleur_papier};
                border: 1px solid {self.couleur_bord_papier};
                border-radius: 2px;
                padding: 30px 36px;
            }}
        """)

        # Ombre légère et diffuse, pour donner l'impression d'une feuille
        # posée sur le pupitre plutôt qu'un simple bloc de couleur
        ombre = QGraphicsDropShadowEffect(label_temp)
        ombre.setBlurRadius(20)
        ombre.setOffset(0, 3)
        ombre.setColor(QColor(0, 0, 0, 55))
        label_temp.setGraphicsEffect(ombre)

        layout_temp = QVBoxLayout()
        layout_temp.setContentsMargins(18, 18, 18, 18)
        layout_temp.addWidget(label_temp)

        # -- Le "pupitre" : fond derrière la feuille, y compris hors du texte --
        scroll_temp = creer_scroll(layout_temp)
        scroll_temp.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.couleur_fond_pupitre};
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {self.couleur_fond_pupitre};
            }}
        """)

        self.layout_description_profil.addWidget(scroll_temp)

        self.widget_lancement.show()
        self.attente_label.hide()

    def initialiser_onglet(self):

        vider_layout(layout=self.layout_description_profil)
        self.layout_description_profil.addStretch()
