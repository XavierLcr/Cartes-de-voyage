################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4                                           #
# Onglet 4.6 – Onglet de résumé de profil                                      #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from textwrap import dedent

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox
from PyQt6.QtCore import Qt

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import (
    vider_layout,
    creer_QLabel_centre,
    creer_scroll,
)
from _0_Utilitaires._0_13_LLM import LLMClient

# 1 -- Classe PyQt6 ------------------------------------------------------------


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


class ProfilVoyageur(QWidget):

    langue = "français"
    modele = "qwen2.5:7b"
    contexte = 32768
    voyages = {}

    def __init__(self, fct_traduction, parent=None):
        super().__init__(parent=parent)

        self.fonction_traduction = fct_traduction

        self.groupbox_description_profil = QGroupBox()
        self.layout_description_profil = QVBoxLayout(self.groupbox_description_profil)

        layout = QVBoxLayout()
        layout.addWidget(self.groupbox_description_profil)
        self.setLayout(layout)

    def set_langue(self, langue):
        self.langue = langue

        self.groupbox_description_profil.setTitle(
            self.fonction_traduction("groupbox_description_profil")
        )

    def set_voyages(self, voyages: dict):

        self.voyages = compacter_voyages(voyages)

    def creer_descriptif(self):

        vider_layout(layout=self.layout_description_profil)

        try:

            profil_LLM = LLMClient(
                model=self.modele,
                url="http://localhost:11434/api/generate",
                timeout=300,
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
                    Analyse la fréquence et la régularité de ses voyages, les périodes où il voyage le plus, la répartition entre courts séjours et voyages plus longs, les types d'occasions qui déclenchent ses déplacements (vacances, événements familiaux, études, travail, amis, excursions), ainsi que ses éventuelles habitudes récurrentes. Ne déduis pas une habitude à partir d'un seul voyage isolé.

                    - Ses destinations favorites :
                    Identifie les pays, régions ou zones géographiques qui reviennent le plus souvent dans son historique. Distingue les destinations réellement fréquentes des simples destinations ponctuelles. Mets en avant les tendances géographiques observables (par exemple une forte présence en Europe, des voyages réguliers dans une zone donnée ou une diversité internationale importante), sans transformer une visite unique en préférence.

                    - Son style de voyage :
                    Analyse les caractéristiques observables de sa manière de voyager : type de destinations choisies, diversité culturelle et géographique, voyages en groupe ou avec des proches lorsque cela est explicitement indiqué, préférence éventuelle pour les séjours urbains, nature, road trips, itinérance, événements ou expériences particulières. Ne déduis pas ses motivations personnelles si elles ne sont pas présentes dans les données.

                    - Ses évolutions dans le temps :
                    Analyse les changements visibles au fil des années : évolution de la fréquence des voyages, élargissement ou changement des zones visitées, apparition de nouveaux types de voyages, évolution entre voyages familiaux, scolaires, amicaux, professionnels ou personnels lorsque cela ressort clairement des données. Appuie-toi uniquement sur une comparaison chronologique des voyages enregistrés.
                                                                    
                    Règle d'interprétation :
                    Une tendance doit être appuyée par plusieurs éléments de l'historique. Une seule occurrence ne suffit pas pour conclure à une préférence, une habitude ou un trait de personnalité. Lorsque les données ne permettent pas de conclure, utilise des formulations prudentes comme "vous semblez avoir...", "votre historique montre..." ou "les données disponibles indiquent...".
                                  
                                                
                    Style :
                    - le texte s'adresse directement au voyageur (utilise "vous") ;
                    - adopte un ton chaleureux, positif et naturel ;
                    - rédige un texte fluide de 3 à 4 phrases ;
                    - mets en avant les tendances marquantes sans exagérer ;
                    - évite les listes à puces ;
                    - reste factuel et nuancé : lorsque les données sont insuffisantes, indique-le plutôt que de tirer une conclusion.

                                                
                    Ne fabrique aucune information. Tu dois être sûr et certain de tout ce que tu écris. Ne parle que des voyages effectués.
                    """))
            profil_LLM.creer_prompt_profil()

            resultat_temp = profil_LLM.generate()
            layout_temp = QVBoxLayout()
            label_temp = creer_QLabel_centre(
                text=resultat_temp,
                wordWrap=True,
                alignement=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
            )
            label_temp.setStyleSheet("""
                QLabel {
                    font-family: "Segoe UI";
                    font-size: 14px;
                    font-weight: 400;
                    color: #333333;
                    padding: 10px;
                }
                """)
            layout_temp.addWidget(label_temp)
            self.layout_description_profil.addWidget(creer_scroll(layout_temp))

        except Exception as e:
            print(e)
            pass
