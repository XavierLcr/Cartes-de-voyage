################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_3                                #
# Onglet 4.3.6 – SpinBox des recommandations                                   #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSpinBox

# 1 -- Classe du sélecteur -----------------------------------------------------


class SpinBoxGare(QSpinBox):
    """
    SpinBox compact inspiré d'un petit compteur de pupitre ferroviaire.

    Le widget reste volontairement discret :
        - fond émaillé sombre ;
        - fine bordure en laiton vieilli ;
        - chiffres crème ;
        - boutons intégrés à droite.
    """

    def __init__(
        self,
        minimum: int = 5,
        maximum: int = 100,
        valeur: int = 20,
        pas: int = 1,
        parent=None,
    ):
        super().__init__(parent)

        self.setRange(
            minimum,
            maximum,
        )

        self.setSingleStep(pas)

        self.setValue(valeur)

        # Widget volontairement compact
        self.setFixedHeight(30)
        # self.setMinimumWidth(68)
        # # self.setMaximumWidth(82)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)

        self.setAccelerated(True)

        self.setStyleSheet("""
            /* --------------------------------------------------------------
            Corps : métal clair semi-transparent
            -------------------------------------------------------------- */

            QSpinBox {
                background-color: rgba(205, 204, 198, 205);
                color: #343632;

                border: 1px solid rgba(132, 122, 103, 175);
                border-radius: 5px;

                padding-left: 5px;
                padding-right: 15px;

                font-size: 12px;
                font-weight: 600;

                selection-background-color: rgba(150, 137, 108, 190);
                selection-color: #FFFFFF;
            }

            /* --------------------------------------------------------------
            Survol
            -------------------------------------------------------------- */

            QSpinBox:hover {
                background-color: rgba(218, 216, 207, 220);
                border-color: rgba(151, 133, 99, 190);
            }

            /* --------------------------------------------------------------
            Focus
            -------------------------------------------------------------- */

            QSpinBox:focus {
                background-color: rgba(214, 212, 203, 225);
                border-color: rgba(164, 142, 101, 205);
            }

            /* --------------------------------------------------------------
            Boutons
            -------------------------------------------------------------- */

            QSpinBox::up-button,
            QSpinBox::down-button {
                subcontrol-origin: border;

                width: 14px;

                background-color: rgba(165, 165, 158, 145);
                border-left: 1px solid rgba(120, 113, 99, 135);
            }

            QSpinBox::up-button {
                subcontrol-position: top right;

                border-top-right-radius: 4px;
                border-bottom: 1px solid rgba(100, 100, 94, 90);
            }

            QSpinBox::down-button {
                subcontrol-position: bottom right;

                border-bottom-right-radius: 4px;
                border-top: 1px solid rgba(235, 233, 223, 90);
            }

            /* --------------------------------------------------------------
            Survol des commandes
            -------------------------------------------------------------- */

            QSpinBox::up-button:hover,
            QSpinBox::down-button:hover {
                background-color: rgba(180, 178, 169, 180);
            }

            QSpinBox::up-button:pressed,
            QSpinBox::down-button:pressed {
                background-color: rgba(145, 145, 139, 180);
            }

            /* --------------------------------------------------------------
            Flèches
            -------------------------------------------------------------- */

            QSpinBox::up-arrow,
            QSpinBox::down-arrow {
                width: 7px;
                height: 7px;
            }

            /* --------------------------------------------------------------
            Désactivé
            -------------------------------------------------------------- */

            QSpinBox:disabled {
                background-color: rgba(190, 190, 184, 130);
                color: rgba(70, 70, 66, 140);
                border-color: rgba(120, 115, 105, 100);
            }
        """)

    # --------------------------------------------------------------------------
    # Molette
    # --------------------------------------------------------------------------

    def wheelEvent(self, event):
        """
        Évite de modifier accidentellement la valeur pendant le défilement
        général de l'onglet : la molette agit uniquement si le widget a
        explicitement le focus.
        """

        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()
