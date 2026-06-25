################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_1/                                          #
# Onglet 1.2 – Combobox avec une couleur associée à chaque valeur              #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtWidgets import QComboBox, QListView
from PyQt6.QtGui import QPixmap, QPainter, QColor, QIcon
from PyQt6.QtCore import Qt
from _0_Utilitaires._0_1_fonctions_utiles_gen import obtenir_clef_par_valeur

# 1 -- Fonction de création de l'icône -----------------------------------------


def creer_icone_cercle(couleur: QColor, taille=24, transparent=False) -> QIcon:
    """Crée une icône circulaire avec couleur ou damier transparent."""

    pixmap = QPixmap(taille, taille)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    if transparent:
        # Damier gris clair
        carre = taille // 4
        for x in range(0, taille, carre):
            for y in range(0, taille, carre):
                painter.fillRect(
                    x,
                    y,
                    carre,
                    carre,
                    (
                        QColor(220, 220, 220)
                        if (x + y) // carre % 2 == 0
                        else QColor(255, 255, 255)
                    ),
                )

    # Cercle coloré
    painter.setBrush(couleur)
    painter.setPen(QColor(150, 150, 150))
    painter.drawEllipse(2, 2, taille - 4, taille - 4)

    painter.end()
    return QIcon(pixmap)


# 2 -- Création de la classe ---------------------------------------------------


class FondCarteCombo(QComboBox):
    """Un QComboBox spécialisé pour choisir le fond de carte."""

    def __init__(self, constantes, parent=None):
        super().__init__(parent)

        self.langue = "français"
        self.arriere_plans = constantes.dictionnaire_arriere_plans
        self.arriere_plans_trad = constantes.parametres_traduits.get(
            "arrière_plans", {}
        )

        # Vue personnalisée (liste déroulante plus flexible)
        self.setView(QListView())
        self.setIconSize(QPixmap(32, 32).size())

        # Ajouter les choix
        self.addItem(creer_icone_cercle(QColor("white")), "Blanc")
        self.addItem(creer_icone_cercle(QColor("blue")), "Bleu")

    def valeur(self) -> str:
        """Retourne le texte du choix courant."""
        return self.currentText()

    def valeur_en_francais(self):
        """Retourne le choix courant en français."""

        return obtenir_clef_par_valeur(
            dictionnaire=self.arriere_plans_trad.get(self.langue, {}),
            valeur=self.valeur(),
        )

    def set_langue(self, langue, taille: int):

        self.langue = langue

        # Mise à jour du déroulé
        self.blockSignals(True)
        self.clear()

        for clef, valeur in self.arriere_plans.items():

            self.addItem(
                creer_icone_cercle(
                    couleur=(
                        QColor(valeur) if (clef != "Transparent") else QColor("#FFFFFF")
                    ),
                    taille=taille,
                    transparent=(clef == "Transparent"),
                ),
                self.arriere_plans_trad.get(self.langue, {}).get(clef, clef),
            )

        self.blockSignals(False)
