################################################################################
# Projet de cartes de voyage                                                   #
# _0_Utilitaires                                                               #
# 0.15 – Fonction en lien avec la date et le temps                             #
################################################################################


# 0 -- Introduction ------------------------------------------------------------


import time, math
from datetime import date, datetime

# 1 -- Fonction de formatage de l'heure et de la date actuelles ----------------


def formater_temps_actuel(n: int = 0) -> str:
    formats = {
        0: "%d-%m-%Y %Hh%M",
        1: "%Y-%m-%d %H:%M",
        2: "%Y-%m-%d",
    }
    return time.strftime(formats.get(n, formats[0]), time.localtime())


# 2 -- Fonction faisant n pauses par minute ------------------------------------


def sleep_n_fois(n: float, time_ref: float | None):

    # Si pas de temps de référence, on prend l'instant actuel
    if time_ref is None:
        time_ref = time.time()

    # Attente
    time.sleep(
        max(
            0,
            60 / n - (time.time() - time_ref),
        )
    )


# 3 -- Fonction de mise en forme selon les événements --------------------------


## 3.1 -- Thème lié à des événements type saison, nouvent an, Noël, ... --------


def periode_particuliere(periodes: dict) -> dict:

    aujourdhui = date.today()
    mois_actuel = aujourdhui.month
    jour_actuel = aujourdhui.day

    # Parcourir les périodes pour trouver la bonne
    for nom, details in periodes.items():
        if "dates" in details:
            for plage in details["dates"]:
                debut_jour = plage.get("debut", {}).get("jour", 1)
                debut_mois = plage.get("debut", {}).get("mois", 1)
                fin_jour = plage.get("fin", {}).get("jour", 31)
                fin_mois = plage.get("fin", {}).get("mois", 12)

                if (
                    # Vérification que la date est supérieure à celle de début
                    mois_actuel > debut_mois
                    or (mois_actuel == debut_mois and jour_actuel >= debut_jour)
                ) and (
                    # Vérification que la date est inférieure à celle de fin
                    mois_actuel < fin_mois
                    or (mois_actuel == fin_mois and jour_actuel <= fin_jour)
                ):

                    return details["config"]

    # Retourner la configuration par défaut
    return periodes.get("Défaut", {}).get(
        "config",
        {
            "titre_police": "Vivaldi",
            "titre_police_coeff": 1,
            "emoji": "",
        },
    )


## 3.2 -- Vérifie si un jour est lié à l'armée ---------------------------------


def est_jour_militaire(date_jour: date | None = None) -> bool:
    """
    Indique si la date correspond à une journée militaire ou commémorative
    importante en France.

    Si aucune date n'est fournie, utilise la date du jour.
    """

    if date_jour is None:
        date_jour = date.today()

    jours_militaires = {
        (5, 8),  # 8 mai
        (6, 18),  # 18 juin
        (7, 14),  # 14 juillet
        (11, 11),  # 11 novembre
    }

    return (date_jour.month, date_jour.day) in jours_militaires


# 4 -- Phase de la journée -----------------------------------------------------


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


# 5 -- Répartition de l'éclairage de la phase ----------------------------------


## 5.1 -- Calcul des phases selon la date et les coordonnées -------------------


def _moments_journee(
    date_jour: date,
    latitude: float,
    longitude: float,
) -> dict:
    """
    Calcule les quatre moments de la journée solaire pour une date et
    une position données.

    Retourne les phases (0-1) correspondant à :
        - nuit_fin     : début du crépuscule civil (-6°)
        - jour_debut   : lever du Soleil (-0.833°)
        - jour_fin     : coucher du Soleil (-0.833°)
        - nuit_debut   : fin du crépuscule civil (-6°)

    La phase 0 correspond à minuit local et la phase 1 à minuit suivant.
    """

    # -------------------------------------------------------------------------
    # Jour de l'année
    # -------------------------------------------------------------------------

    jour_annee = date_jour.timetuple().tm_yday

    gamma = 2 * math.pi / 365 * (jour_annee - 1)

    # -------------------------------------------------------------------------
    # Équation du temps
    # -------------------------------------------------------------------------

    equation_temps = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )

    # -------------------------------------------------------------------------
    # Déclinaison solaire
    # -------------------------------------------------------------------------

    declinaison = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.001480 * math.sin(3 * gamma)
    )

    latitude_rad = math.radians(latitude)

    # -------------------------------------------------------------------------
    # Décalage horaire local
    # -------------------------------------------------------------------------

    # On prend le décalage du fuseau de l'ordinateur pour cette date.
    # Cela gère automatiquement l'heure d'été / heure d'hiver.
    datetime_local = datetime(
        date_jour.year,
        date_jour.month,
        date_jour.day,
        12,
    ).astimezone()

    decalage_utc = datetime_local.utcoffset().total_seconds() / 3600

    # -------------------------------------------------------------------------
    # Angle horaire pour une hauteur solaire donnée
    # -------------------------------------------------------------------------

    def angle_horaire(hauteur: float) -> float | None:
        """
        Retourne l'angle horaire en degrés pour une hauteur solaire donnée.
        """

        hauteur_rad = math.radians(hauteur)

        cos_angle = (
            math.sin(hauteur_rad) - math.sin(latitude_rad) * math.sin(declinaison)
        ) / (math.cos(latitude_rad) * math.cos(declinaison))

        if not -1 <= cos_angle <= 1:
            return None

        return math.degrees(math.acos(cos_angle))

    # -------------------------------------------------------------------------
    # Conversion d'un événement solaire en heure locale
    # -------------------------------------------------------------------------

    def heures_evenement(
        hauteur: float,
    ) -> tuple[float | None, float | None]:
        """
        Retourne (heure_lever, heure_coucher) en heures locales.
        """

        angle = angle_horaire(hauteur)

        if angle is None:
            return None, None

        # Heure du midi solaire local.
        midi_solaire = 720 - 4 * longitude - equation_temps + 60 * decalage_utc

        minutes_lever = midi_solaire - 4 * angle
        minutes_coucher = midi_solaire + 4 * angle

        return (
            (minutes_lever / 60) % 24,
            (minutes_coucher / 60) % 24,
        )

    # -------------------------------------------------------------------------
    # Lever / coucher
    # -------------------------------------------------------------------------

    heure_aube, heure_crepuscule = heures_evenement(-6.0)

    heure_lever, heure_coucher = heures_evenement(-0.833)

    # -------------------------------------------------------------------------
    # Heure → phase
    # -------------------------------------------------------------------------

    def phase(heure: float | None) -> float | None:
        if heure is None:
            return None

        return heure / 24

    return {
        "nuit_fin": phase(heure_aube),
        "jour_debut": phase(heure_lever),
        "jour_fin": phase(heure_coucher),
        "nuit_debut": phase(heure_crepuscule),
    }


## 5.2 -- Répartition de la phase ----------------------------------------------


def _poids_moments(
    phase: float, latitude: float = 50.63, longitude: float = 5.57
) -> dict:
    """
    Renvoie les poids (0-1, somme = 1) de chaque moment pour la phase
    donnée, avec transitions douces (aube / crépuscule) plutôt que des
    bascules brutales. Clés : 'nuit', 'aube', 'jour', 'crepuscule'.
    """

    moments = _moments_journee(
        date_jour=datetime.now().date(),
        latitude=latitude,
        longitude=longitude,
    )

    _NUIT_FIN = moments["nuit_fin"]
    _JOUR_DEBUT = moments["jour_debut"]
    _JOUR_FIN = moments["jour_fin"]
    _NUIT_DEBUT = moments["nuit_debut"]

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
