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
            Corps : métal gris-taupe neutre
            -------------------------------------------------------------- */

            QSpinBox {
                background-color: #74746F;
                color: #F5F0E4;

                border: 1px solid #8F8065;
                border-radius: 5px;

                padding-left: 5px;
                padding-right: 15px;

                font-size: 12px;
                font-weight: 600;

                selection-background-color: #9B8A69;
                selection-color: #FFFFFF;
            }

            /* --------------------------------------------------------------
            Survol : très léger éclaircissement
            -------------------------------------------------------------- */

            QSpinBox:hover {
                background-color: #7E7E78;
                border-color: #A18D68;
            }

            /* --------------------------------------------------------------
            Focus
            -------------------------------------------------------------- */

            QSpinBox:focus {
                background-color: #7A7A74;
                border-color: #B09A72;
            }

            /* --------------------------------------------------------------
            Boutons
            -------------------------------------------------------------- */

            QSpinBox::up-button,
            QSpinBox::down-button {
                subcontrol-origin: border;

                width: 14px;

                background-color: #656661;

                border-left: 1px solid #897A61;
            }

            QSpinBox::up-button {
                subcontrol-position: top right;

                border-top-right-radius: 4px;
                border-bottom: 1px solid #585954;
            }

            QSpinBox::down-button {
                subcontrol-position: bottom right;

                border-bottom-right-radius: 4px;
                border-top: 1px solid #85857D;
            }

            /* --------------------------------------------------------------
            Survol des commandes
            -------------------------------------------------------------- */

            QSpinBox::up-button:hover,
            QSpinBox::down-button:hover {
                background-color: #72736D;
            }

            QSpinBox::up-button:pressed,
            QSpinBox::down-button:pressed {
                background-color: #5B5C57;
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
                background-color: #777772;
                color: #B8B5AA;
                border-color: #777166;
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
