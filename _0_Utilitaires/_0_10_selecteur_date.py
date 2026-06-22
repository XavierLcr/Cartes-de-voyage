################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# 0.10 – Classe d'outil de sélection d'une date                                #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


from PyQt6.QtWidgets import QDateEdit
from PyQt6.QtCore import QDate

# 1 -- Classe de sélection du mois et de l'année -------------------------------


class SelecteurDate(QDateEdit):

    def __init__(self, parent=None, date=None):
        super().__init__(parent)

        # ✔ affichage au jour près
        self.setDisplayFormat("dd/MM/yyyy")

        # Calendrier popup (recommandé pour sélection jour)
        self.setCalendarPopup(True)

        self.calendarWidget().setStyleSheet("""
            QCalendarWidget {
                color: black;
                background-color: white;
            }

            QCalendarWidget QToolButton {
                color: black;
                background-color: #f0f0f0;
            }

            QCalendarWidget QMenu {
                color: black;
                background-color: white;
            }
        """)

        # date par défaut
        if date is not None:
            year, month, day = map(int, date.split("-"))
            qdate = QDate(year, month, day)
        else:
            qdate = QDate.currentDate()

        self.setDate(qdate)

    def obtenir_date(self):
        """Retourne la date sélectionnée (QDate)."""
        return self.date()

    def obtenir_date_str(self, format_sortie="yyyy-MM-dd"):
        """Retourne la date sélectionnée en string."""
        return self.date().toString(format_sortie)
