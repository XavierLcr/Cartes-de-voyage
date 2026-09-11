################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6                                #
# Onglet 4.6.1.1 – Thème du compteur de pays visités                           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math
import random
from datetime import datetime
from typing import List, Optional, Tuple

from PyQt6.QtCore import (
    Qt,
    QRectF,
    QPointF,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
    QTimer,
)
from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QBrush,
    QPen,
    QColor,
    QFont,
    QFontMetrics,
    QRadialGradient,
    QConicalGradient,
    QLinearGradient,
)
from PyQt6.QtWidgets import QWidget, QSizePolicy, QGraphicsDropShadowEffect

from _4_Interface._4_2_Style._4_2_1_style_principal import (
    renvoyer_couleur_widget,
    renvoyer_couleur_texte,
    renvoyer_couleur_widget_differente,
)
from _4_Interface._4_3_Icones._4_3_32_etoile_de_mer import _dessiner_etoile_mer
from _4_Interface._4_3_Icones._4_3_33_coquillage import _dessiner_coquillage
from _4_Interface._4_3_Icones._4_3_34_poissons import (
    _dessiner_poisson,
    _generer_poissons,
)

# 1 -- Phase de la journée -----------------------------------------------------


def phase_journee(instant: datetime | None = None) -> float:
    """
    Position dans le cycle jour/nuit, en continu :
    0.0 / 1.0 = minuit
    0.25      = lever du soleil (~6h)
    0.5       = midi
    0.75      = coucher du soleil (~18h)
    Ajuste les bornes ci-dessous si tu veux un cycle plus réaliste
    selon la saison plutôt que fixe.
    """
    if instant is None:
        instant = datetime.now()
    secondes = instant.hour * 3600 + instant.minute * 60 + instant.second
    return secondes / 86400.0


# 2 -- Répartition de l'éclairage de la phase ----------------------------------


def _poids_moments(phase: float) -> dict:
    """
    Renvoie les poids (0-1, somme = 1) de chaque moment pour la phase
    donnée, avec transitions douces (aube / crépuscule) plutôt que des
    bascules brutales. Clés : 'nuit', 'aube', 'jour', 'crepuscule'.
    """

    # Bornes des moments-clés (en phase 0-1), ajustables
    _NUIT_FIN = 0.22  # ~5h17 : fin de nuit, début de l'aube
    _JOUR_DEBUT = 0.30  # ~7h12 : soleil bien levé
    _JOUR_FIN = 0.70  # ~16h48 : plein jour jusque-là
    _NUIT_DEBUT = 0.78  # ~18h43 : nuit installée

    def lisser(a, b, x):
        if b <= a:
            return 1.0
        t = max(0.0, min(1.0, (x - a) / (b - a)))
        return t * t * (3 - 2 * t)  # smoothstep

    if phase <= _NUIT_FIN:
        return {"nuit": 1.0, "aube": 0.0, "jour": 0.0, "crepuscule": 0.0}
    if phase <= _JOUR_DEBUT:
        t = lisser(_NUIT_FIN, _JOUR_DEBUT, phase)
        return {"nuit": 1 - t, "aube": t, "jour": 0.0, "crepuscule": 0.0}
    if phase <= _JOUR_FIN:
        return {"nuit": 0.0, "aube": 0.0, "jour": 1.0, "crepuscule": 0.0}
    if phase <= _NUIT_DEBUT:
        t = lisser(_JOUR_FIN, _NUIT_DEBUT, phase)
        return {"nuit": 0.0, "aube": 0.0, "jour": 1 - t, "crepuscule": t}
    return {"nuit": 1.0, "aube": 0.0, "jour": 0.0, "crepuscule": 0.0}


# 3 --
