################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones/_4_3_49_TGV                                         #
# 4.3.49.3 – Classe de création d'un TGV complet                               #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainter

from _4_Interface._4_3_Icones._4_3_49_TGV._4_3_49_1_motrice import MotriceTGV
from _4_Interface._4_3_Icones._4_3_49_TGV._4_3_49_2_voiture import VoitureTGV

# 1 -- Classe de création d'un TGV ---------------------------------------------


class TGV:
    """
    Dessine une rame TGV complète composée de :

        - une motrice avant ;
        - n voitures voyageurs ;
        - une motrice arrière.

    Les pays sont répartis entre les voitures aussi équitablement que possible.

    Exemple
    -------
    17 pays sur 4 voitures :

        [5, 4, 4, 4]

    Une répartition personnalisée peut être fournie avec :

        repartition=[3, 4, 5, 5]

    Chaque voiture gère ensuite elle-même :
        - ses fenêtres simples / doubles ;
        - le mode classique / Duplex ;
        - l'état visité / non visité des pays ;
        - sa largeur recommandée.
    """

    def __init__(
        self,
        nb_pays: int,
        couleur_fenetres: QColor | str,
        nb_wagons: int | None = None,
        duplex: bool = False,
        repartition: list[int] | None = None,
        pays_allumes: list[bool] | None = None,
        couleur_caisse: QColor | str = "#E7E9E8",
        couleur_secondaire: QColor | str = "#59646A",
        couleur_vitres_motrice: QColor | str = "#314954",
        couleur_toit: QColor | str | None = None,
        couleur_cadre_fenetres: QColor | str = "#3C454A",
        portes: bool = True,
        halo_fenetres: bool = True,
        reflets_fenetres: bool = True,
        pantographes: bool = True,
        feux: bool = True,
        capacite_cible_wagon: int | None = None,
    ):

        self.nb_pays = max(
            int(nb_pays),
            0,
        )

        self.duplex = bool(duplex)

        self.couleur_fenetres = QColor(couleur_fenetres)

        self.couleur_caisse = QColor(couleur_caisse)

        self.couleur_secondaire = QColor(couleur_secondaire)

        self.couleur_vitres_motrice = QColor(couleur_vitres_motrice)

        self.couleur_toit = QColor(couleur_toit) if couleur_toit is not None else None

        self.couleur_cadre_fenetres = QColor(couleur_cadre_fenetres)

        self.portes = bool(portes)
        self.halo_fenetres = bool(halo_fenetres)
        self.reflets_fenetres = bool(reflets_fenetres)

        self.pantographes = bool(pantographes)
        self.feux = bool(feux)

        # ----------------------------------------------------------------------
        # État des pays
        # ----------------------------------------------------------------------

        if pays_allumes is None:

            self.pays_allumes = [True for _ in range(self.nb_pays)]

        else:

            if len(pays_allumes) != self.nb_pays:
                raise ValueError(
                    "pays_allumes doit contenir exactement " f"{self.nb_pays} éléments."
                )

            self.pays_allumes = list(pays_allumes)

        # ----------------------------------------------------------------------
        # Nombre de wagons
        # ----------------------------------------------------------------------

        if repartition is not None:

            self.repartition = self._valider_repartition(repartition)

            self.nb_wagons = len(self.repartition)

            if nb_wagons is not None and nb_wagons != self.nb_wagons:
                raise ValueError(
                    "nb_wagons ne correspond pas à la longueur de repartition."
                )

        else:

            if nb_wagons is None:

                # Capacité uniquement destinée à déterminer automatiquement
                # un nombre raisonnable de voitures.
                if capacite_cible_wagon is None:
                    capacite_cible_wagon = 16 if self.duplex else 10

                capacite_cible_wagon = max(
                    int(capacite_cible_wagon),
                    1,
                )

                nb_wagons = max(
                    1,
                    (self.nb_pays + capacite_cible_wagon - 1) // capacite_cible_wagon,
                )

            self.nb_wagons = max(
                int(nb_wagons),
                1,
            )

            if self.nb_pays > 0 and self.nb_wagons > self.nb_pays:
                raise ValueError(
                    "Le nombre de wagons ne peut pas dépasser " "le nombre de pays."
                )

            self.repartition = self._calculer_repartition()

        # ----------------------------------------------------------------------
        # Zones interactives
        # ----------------------------------------------------------------------

        # zones_pays[i] correspond au pays d'indice i.
        self.zones_pays = [QRectF() for _ in range(self.nb_pays)]

        # Conservé après le dernier dessin, pratique pour debugger.
        self.rects_voitures = []
        self.rect_motrice_gauche = QRectF()
        self.rect_motrice_droite = QRectF()

    # --------------------------------------------------------------------------
    # Répartition
    # --------------------------------------------------------------------------

    def _calculer_repartition(
        self,
    ) -> list[int]:
        """
        Répartit aussi uniformément que possible les pays entre les voitures.

        Exemples
        --------
        17 / 4 -> [5, 4, 4, 4]
        18 / 4 -> [5, 5, 4, 4]
        20 / 4 -> [5, 5, 5, 5]
        """

        quotient, reste = divmod(
            self.nb_pays,
            self.nb_wagons,
        )

        return [quotient + (1 if i < reste else 0) for i in range(self.nb_wagons)]

    def _valider_repartition(
        self,
        repartition: list[int],
    ) -> list[int]:

        if not repartition:
            raise ValueError("repartition ne peut pas être vide.")

        resultat = [int(n) for n in repartition]

        if any(n < 0 for n in resultat):
            raise ValueError("La répartition ne peut pas contenir de valeur négative.")

        if sum(resultat) != self.nb_pays:
            raise ValueError(
                "La somme de repartition doit être égale à nb_pays : "
                f"{sum(resultat)} != {self.nb_pays}."
            )

        return resultat

    # --------------------------------------------------------------------------
    # Répartition des indices de pays
    # --------------------------------------------------------------------------

    def indices_par_wagon(
        self,
    ) -> list[list[int]]:
        """
        Renvoie les indices globaux des pays contenus dans chaque voiture.

        Exemple avec [5, 4, 4] :

            [
                [0, 1, 2, 3, 4],
                [5, 6, 7, 8],
                [9, 10, 11, 12],
            ]
        """

        resultat = []

        debut = 0

        for nb_pays_wagon in self.repartition:

            fin = debut + nb_pays_wagon

            resultat.append(
                list(
                    range(
                        debut,
                        fin,
                    )
                )
            )

            debut = fin

        return resultat

    # --------------------------------------------------------------------------
    # Création d'une voiture
    # --------------------------------------------------------------------------

    def _creer_voiture(
        self,
        indices_pays: list[int],
    ) -> VoitureTGV:

        return VoitureTGV(
            nb_pays=len(indices_pays),
            duplex=self.duplex,
            couleur_fenetres=self.couleur_fenetres,
            pays_allumes=[self.pays_allumes[i] for i in indices_pays],
            couleur_caisse=self.couleur_caisse,
            couleur_secondaire=self.couleur_secondaire,
            couleur_toit=self.couleur_toit,
            couleur_cadre_fenetres=self.couleur_cadre_fenetres,
            portes=self.portes,
            halo_fenetres=self.halo_fenetres,
            reflets_fenetres=self.reflets_fenetres,
        )

    # --------------------------------------------------------------------------
    # Création des motrices
    # --------------------------------------------------------------------------

    def _creer_motrice(
        self,
    ) -> MotriceTGV:

        return MotriceTGV(
            couleur_caisse=self.couleur_caisse,
            couleur_secondaire=self.couleur_secondaire,
            couleur_vitres=self.couleur_vitres_motrice,
            couleur_toit=self.couleur_toit,
            duplex=self.duplex,
            pantographe=self.pantographes,
            feux=self.feux,
        )

    # --------------------------------------------------------------------------
    # Largeur des motrices
    # --------------------------------------------------------------------------

    @staticmethod
    def largeur_motrice_recommandee(
        hauteur: float,
    ) -> float:
        """
        Rapport volontairement assez allongé pour conserver un nez de TGV
        visuellement convaincant.
        """

        return hauteur * 2.55

    # --------------------------------------------------------------------------
    # Recouvrement entre éléments
    # --------------------------------------------------------------------------

    @staticmethod
    def recouvrement_recommande(
        hauteur: float,
    ) -> float:
        """
        Léger chevauchement entre deux éléments afin que les articulations
        ne donnent pas l'impression de wagons flottant les uns à côté des autres.
        """

        return hauteur * 0.028

    # --------------------------------------------------------------------------
    # Largeur totale recommandée
    # --------------------------------------------------------------------------

    def largeur_recommandee(
        self,
        hauteur: float,
    ) -> float:

        if hauteur <= 0:
            return 0.0

        indices_wagons = self.indices_par_wagon()

        largeur_motrice = self.largeur_motrice_recommandee(hauteur)

        largeurs_voitures = []

        for indices in indices_wagons:

            voiture = self._creer_voiture(indices)

            largeurs_voitures.append(voiture.largeur_recommandee(hauteur=hauteur))

        # Deux motrices + toutes les voitures
        largeur = 2 * largeur_motrice + sum(largeurs_voitures)

        # Nombre de jonctions :
        # motrice / wagon / wagon / ... / motrice
        nb_jonctions = self.nb_wagons + 1

        largeur -= nb_jonctions * self.recouvrement_recommande(hauteur)

        return largeur

    # --------------------------------------------------------------------------
    # Hauteur maximale permettant de rentrer dans un rectangle
    # --------------------------------------------------------------------------

    def hauteur_adaptee(
        self,
        rect: QRectF,
    ) -> float:
        """
        Renvoie la plus grande hauteur permettant au train de tenir dans rect.

        Comme toutes les dimensions internes sont proportionnelles à la hauteur,
        le calcul est direct.
        """

        if rect.width() <= 0 or rect.height() <= 0:
            return 0.0

        largeur_unitaire = self.largeur_recommandee(hauteur=1.0)

        if largeur_unitaire <= 0:
            return 0.0

        hauteur_par_largeur = rect.width() / largeur_unitaire

        return min(
            rect.height(),
            hauteur_par_largeur,
        )

    # --------------------------------------------------------------------------
    # Dessin principal
    # --------------------------------------------------------------------------

    def peindre(
        self,
        painter: QPainter,
        rect: QRectF,
        perspective: float = 0.07,
        adapter: bool = True,
        alignement_vertical: str = "centre",
        ombre: bool = True,
    ) -> None:
        """
        Dessine le TGV complet dans `rect`.

        adapter
        -------
        True :
            calcule automatiquement la plus grande hauteur possible sans
            dépasser la largeur disponible.

        False :
            utilise directement rect.height() comme hauteur de rame.
        """

        if rect.width() <= 0 or rect.height() <= 0:
            return

        # ----------------------------------------------------------------------
        # Hauteur utilisée
        # ----------------------------------------------------------------------

        if adapter:

            hauteur = self.hauteur_adaptee(rect)

        else:

            hauteur = rect.height()

        if hauteur <= 0:
            return

        largeur_totale = self.largeur_recommandee(hauteur)

        # ----------------------------------------------------------------------
        # Position générale
        # ----------------------------------------------------------------------

        x = rect.left() + (rect.width() - largeur_totale) / 2

        if alignement_vertical == "haut":

            y = rect.top()

        elif alignement_vertical == "bas":

            y = rect.bottom() - hauteur

        else:

            y = rect.top() + (rect.height() - hauteur) / 2

        recouvrement = self.recouvrement_recommande(hauteur)

        largeur_motrice = self.largeur_motrice_recommandee(hauteur)

        # Réinitialisation des zones
        self.zones_pays = [QRectF() for _ in range(self.nb_pays)]

        self.rects_voitures = []

        # ----------------------------------------------------------------------
        # Motrice gauche
        # ----------------------------------------------------------------------

        self.rect_motrice_gauche = QRectF(
            x,
            y,
            largeur_motrice,
            hauteur,
        )

        motrice_gauche = self._creer_motrice()

        motrice_gauche.peindre(
            painter=painter,
            rect=self.rect_motrice_gauche,
            sens=-1,
            perspective=perspective,
            ombre=ombre,
        )

        x += largeur_motrice - recouvrement

        # ----------------------------------------------------------------------
        # Voitures
        # ----------------------------------------------------------------------

        indices_wagons = self.indices_par_wagon()

        for numero_wagon, indices in enumerate(indices_wagons):

            voiture = self._creer_voiture(indices)

            largeur_voiture = voiture.largeur_recommandee(hauteur=hauteur)

            rect_voiture = QRectF(
                x,
                y,
                largeur_voiture,
                hauteur,
            )

            self.rects_voitures.append(QRectF(rect_voiture))

            # --------------------------------------------------------------
            # Bogies articulés
            # --------------------------------------------------------------
            #
            # Le premier wagon dessine son bogie gauche.
            #
            # Ensuite chaque wagon dessine son bogie droit.
            #
            # Ainsi une articulation entre deux voitures ne possède qu'un
            # seul bogie visuel au lieu de deux bogies superposés.
            # --------------------------------------------------------------

            voiture.peindre(
                painter=painter,
                rect=rect_voiture,
                perspective=perspective,
                ombre=ombre,
                bogie_gauche=(numero_wagon == 0),
                bogie_droit=True,
            )

            # --------------------------------------------------------------
            # Récupération des zones des pays
            # --------------------------------------------------------------

            for indice_local, indice_global in enumerate(indices):

                self.zones_pays[indice_global] = QRectF(
                    voiture.zones_pays[indice_local]
                )

            x += largeur_voiture - recouvrement

        # ----------------------------------------------------------------------
        # Motrice droite
        # ----------------------------------------------------------------------

        self.rect_motrice_droite = QRectF(
            x,
            y,
            largeur_motrice,
            hauteur,
        )

        motrice_droite = self._creer_motrice()

        motrice_droite.peindre(
            painter=painter,
            rect=self.rect_motrice_droite,
            sens=1,
            perspective=perspective,
            ombre=ombre,
        )

    # --------------------------------------------------------------------------
    # Pays survolé
    # --------------------------------------------------------------------------

    def pays_survole(
        self,
        position: QPointF,
    ) -> int | None:
        """
        Renvoie l'indice global du pays correspondant à la vitre survolée.
        """

        for indice, zone in enumerate(self.zones_pays):

            if zone.contains(position):
                return indice

        return None
