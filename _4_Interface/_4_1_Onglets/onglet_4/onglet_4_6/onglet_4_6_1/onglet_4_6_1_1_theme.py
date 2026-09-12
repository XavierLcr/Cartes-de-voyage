################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_1_Onglets/onglet_4/onglet_4_6/onglet_4_6_1                   #
# Onglet 4.6.1.1 – Thème du compteur de pays visités                           #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from __future__ import annotations
import math
from datetime import datetime

from PyQt6.QtGui import QColor

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import _QColor_avec_alpha
from _4_Interface._4_2_Style._4_2_1_style_principal import renvoyer_couleur_texte

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
    _NUIT_DEBUT = 0.80  # ~19h12 : nuit installée

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


# 3 -- Fonction d'interpolation de couleurs ------------------------------------


def interpoler_couleurs(
    couleurs,
    poids=None,
    retour="qcolor",
):
    """
    Interpole plusieurs couleurs en espace HSV.

    Paramètres
    ----------
    couleurs : list | tuple | dict
        Couleurs à interpoler. Les valeurs peuvent être des QColor ou des
        chaînes hexadécimales.

    poids : list | tuple | dict | None
        Poids associés aux couleurs. Si None, toutes les couleurs ont le
        même poids. Les poids sont normalisés automatiquement.

    retour : {"qcolor", "hexa", "hsv"}
        Format de sortie :
        - "qcolor" : renvoie un QColor ;
        - "hexa"   : renvoie une chaîne hexadécimale ;
        - "hsv"    : renvoie un tuple (h, s, v).

        Pour "hsv", h, s et v sont dans [0, 1].

    Retour
    ------
    QColor | str | tuple
        Couleur interpolée dans le format demandé.
    """

    # ------------------------------------------------------------------
    # Préparation des couleurs
    # ------------------------------------------------------------------

    if isinstance(couleurs, dict):
        couleurs = list(couleurs.values())

    couleurs = list(couleurs)

    if not couleurs:
        couleurs = ["#FFFFFF"]

    couleurs = [
        couleur if isinstance(couleur, QColor) else QColor(couleur)
        for couleur in couleurs
    ]

    if any(not couleur.isValid() for couleur in couleurs):
        raise ValueError("Une ou plusieurs couleurs sont invalides.")

    # ------------------------------------------------------------------
    # Préparation des poids
    # ------------------------------------------------------------------

    if poids is None:
        poids = [1.0] * len(couleurs)

    elif isinstance(poids, dict):
        poids = list(poids.values())

    else:
        poids = list(poids)

    somme_poids = sum(poids)

    if (
        len(poids) != len(couleurs)
        or any(poids_i < 0 for poids_i in poids)
        or somme_poids <= 0
    ):
        return interpoler_couleurs(couleurs=couleurs, poids=None, retour=retour)

    poids = [poids_i / somme_poids for poids_i in poids]

    # ------------------------------------------------------------------
    # Conversion HSV
    # ------------------------------------------------------------------

    hsv = []

    for couleur in couleurs:
        h, s, v, _ = couleur.getHsvF()

        # QColor renvoie -1 pour la teinte des couleurs achromatiques
        # (gris, blanc, noir...). On lui attribue ici une teinte neutre
        # pour éviter de faire tourner artificiellement la couleur.
        if h < 0:
            h = 0.0

        hsv.append((h, s, v))

    # ------------------------------------------------------------------
    # Interpolation de la teinte
    # ------------------------------------------------------------------

    # On calcule la moyenne circulaire des teintes sur le cercle HSV.
    # Cela évite par exemple que 350° + 10° donnent artificiellement 180°.

    x = 0.0
    y = 0.0

    for (h, _, _), poids_i in zip(hsv, poids):
        angle = h * math.tau
        x += math.cos(angle) * poids_i
        y += math.sin(angle) * poids_i

    if abs(x) < 1e-12 and abs(y) < 1e-12:
        h = 0.0
    else:
        h = (math.atan2(y, x) / math.tau) % 1.0

    # ------------------------------------------------------------------
    # Interpolation linéaire de saturation et luminosité
    # ------------------------------------------------------------------

    s = sum(s_i * poids_i for (_, s_i, _), poids_i in zip(hsv, poids))

    v = sum(v_i * poids_i for (_, _, v_i), poids_i in zip(hsv, poids))

    hsv_resultat = (h, s, v)

    # ------------------------------------------------------------------
    # Format de sortie
    # ------------------------------------------------------------------

    if retour == "hsv":
        return hsv_resultat

    resultat = QColor()
    resultat.setHsvF(h, s, v)

    if retour == "qcolor":
        return resultat

    if retour == "hexa":
        return resultat.name()

    return "#FFFFFF"


# 4 -- Thème du widget ---------------------------------------------------------


class CompteurTheme:
    """
    Palette de couleurs du widget de compteur de pays visités.
    """

    def __init__(self):

        self._PALETTE = {
            "nuit": {
                "centre": "#232A52",
                "bord": "#12142B",
                "rim": "#B9C4E0",
                "fond": "#1A1F3D",
                "progression_debut": "#8A78C8",
                "progression_fin": "#C7B9F2",
                "cercle_tour": "#B9C4E0",
                "sable_debut": "#A99670",
                "sable_fin": "#C8B68A",
            },
            "aube": {
                "centre": "#FDE0B0",
                "bord": "#F3A66B",
                "rim": "#F7C88A",
                "fond": "#F2DAC0",
                "progression_debut": "#D98762",
                "progression_fin": "#F5C98D",
                "cercle_tour": "#F7C88A",
                "sable_debut": "#C8A46F",
                "sable_fin": "#D8B982",
            },
            "jour": {
                "centre": "#FFFCF2",
                "bord": "#FFF3D2",
                "rim": "#F0C452",
                "fond": "#E5EFF3",
                "progression_debut": "#C9902F",
                "progression_fin": "#F3D48C",
                "cercle_tour": "#FFCB61",
                "sable_debut": "#C9A45E",
                "sable_fin": "#E2C47D",
            },
            "crepuscule": {
                "centre": "#F6B27C",
                "bord": "#D96A5C",
                "rim": "#F2914F",
                "fond": "#EFD4DE",
                "progression_debut": "#C85F5A",
                "progression_fin": "#F3A66F",
                "cercle_tour": "#F2914F",
                "sable_debut": "#B88D61",
                "sable_fin": "#C9A16A",
            },
        }

        # Calcul de la bonne couleur
        self._PALETTE = self._teintes_palette()

        # -- Ajout de la couleur du texte
        self._PALETTE["texte"] = renvoyer_couleur_texte(
            style=0, couleur=self._PALETTE["centre"].name()
        )
        # -- Ajout de la couleur de la piste
        self._PALETTE["piste"] = _QColor_avec_alpha(self._PALETTE["texte"], alpha=25)

    def _teintes_palette(self) -> dict:
        """Mélange pondéré des teintes centre/bord/rim selon les poids
        horaires actifs (transition continue, pas de bascule brutale)."""

        poids_temp = _poids_moments(phase_journee())
        return {
            cle: interpoler_couleurs(
                {moment: self._PALETTE[moment][cle] for moment in poids_temp},
                poids=poids_temp,
                retour="qcolor",
            )
            for cle in self._PALETTE.get("nuit").keys()
        }
