################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_2                                           #
# Onglet 2 – Sélection des destinations                                        #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


from PyQt6.QtWidgets import QDateEdit, QCalendarWidget
from PyQt6.QtCore import QDate


# 1 -- Classe de sélection du mois et de l'année -------------------------------


class SelecteurMoisAnnee(QDateEdit):

    def __init__(self, parent=None, date=None):
        super().__init__(parent)

        # Configurer la locale en français
        # QLocale.setDefault(QLocale(QLocale.Language.French, QLocale.Country.France))
        # self.setLocale(QLocale(QLocale.Language.French, QLocale.Country.France))

        # Définir le format d'affichage (mois/année)
        self.setDisplayFormat("MM/yyyy")

        # Créer un calendrier personnalisé
        calendrier = QCalendarWidget()
        # calendrier.setLocale(QLocale(QLocale.Language.French, QLocale.Country.France))
        calendrier.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )
        calendrier.setHorizontalHeaderFormat(
            QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames
        )

        # Associer le calendrier au QDateEdit
        self.setCalendarPopup(False)

        # Définir la date actuelle par défaut
        if date is not None:
            year, month, day = map(int, date.split("-"))
            qdate = QDate(year, month, day)
        else:
            qdate = QDate.currentDate()

        # Exemple d'utilisation dans une méthode PyQt6
        self.setDate(qdate)

    def obtenir_mois_annee(self):
        """Retourne un tuple (mois, année) sélectionné."""
        date = self.date()
        return date.month(), date.year()

    def obtenir_premier_jour_mois(self, format_sortie="yyyy-MM-dd"):
        """
        Retourne une chaîne représentant le premier jour du mois sélectionné,
        au format spécifié (par défaut : "yyyy-MM-dd").
        """
        mois, annee = self.obtenir_mois_annee()
        date_premier_jour = QDate(annee, mois, 1)
        return date_premier_jour.toString(format_sortie)
