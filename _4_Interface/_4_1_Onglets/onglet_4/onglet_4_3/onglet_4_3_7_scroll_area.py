################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_3                                #
# Onglet 4.3.7 – Style du scroll area                                          #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QScrollArea, QFrame

# 1 -- Classe de recommandations ----------------------------------------------


class ScrollAreaGare(QScrollArea):
    """
    ScrollArea discrète, dans un style gare ancienne :
    - fond très léger et chaleureux ;
    - contour doux ;
    - scrollbar fine, élégante et peu invasive.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("scrollAreaGare")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # En général, pour ce type d'onglet, on préfère éviter l'horizontale.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.verticalScrollBar().setSingleStep(24)

        # Petit confort visuel
        self.setViewportMargins(6, 6, 6, 6)

        self.setStyleSheet("""
            /* Zone externe du scroll */
            QScrollArea#scrollAreaGare {
                background: transparent;
                border: none;
            }

            /* Le viewport réel */
            QScrollArea#scrollAreaGare > QWidget > QWidget {
                background: transparent;
            }

            /* Widget contenu si on lui donne l'objectName 'contenuRecommandations' */
            QWidget#contenuRecommandations {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(245, 240, 230, 105),
                    stop: 1 rgba(232, 224, 210, 85)
                );
                border: 1px solid rgba(115, 90, 65, 70);
                border-radius: 16px;
            }

            /* Scrollbar verticale */
            QScrollBar:vertical {
                background: rgba(70, 55, 40, 18);
                width: 14px;
                margin: 10px 2px 10px 2px;
                border-radius: 7px;
            }

            QScrollBar::handle:vertical {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(124, 98, 72, 125),
                    stop: 1 rgba(156, 126, 92, 150)
                );
                min-height: 34px;
                border-radius: 6px;
                border: 1px solid rgba(90, 68, 49, 85);
            }

            QScrollBar::handle:vertical:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(138, 109, 79, 150),
                    stop: 1 rgba(170, 137, 100, 175)
                );
                border: 1px solid rgba(90, 68, 49, 110);
            }

            QScrollBar::handle:vertical:pressed {
                background: rgba(120, 94, 70, 180);
            }

            /* On supprime les gros boutons haut/bas disgracieux */
            QScrollBar::sub-line:vertical,
            QScrollBar::add-line:vertical {
                height: 0px;
                background: transparent;
                border: none;
            }

            QScrollBar::sub-page:vertical,
            QScrollBar::add-page:vertical {
                background: transparent;
            }

            /* Scrollbar horizontale si jamais elle apparaît */
            QScrollBar:horizontal {
                background: rgba(70, 55, 40, 18);
                height: 14px;
                margin: 2px 10px 2px 10px;
                border-radius: 7px;
            }

            QScrollBar::handle:horizontal {
                background: rgba(140, 112, 84, 130);
                min-width: 34px;
                border-radius: 6px;
                border: 1px solid rgba(90, 68, 49, 85);
            }

            QScrollBar::handle:horizontal:hover {
                background: rgba(155, 124, 92, 160);
            }

            QScrollBar::sub-line:horizontal,
            QScrollBar::add-line:horizontal {
                width: 0px;
                background: transparent;
                border: none;
            }

            QScrollBar::sub-page:horizontal,
            QScrollBar::add-page:horizontal {
                background: transparent;
            }

            QScrollBar::corner {
                background: transparent;
            }
        """)
