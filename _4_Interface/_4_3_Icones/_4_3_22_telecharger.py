################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_3_Icones                                                     #
# 4.3.22 – Script de création de l'icône d'export / import                     #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


from PyQt6.QtCore import QPointF, Qt, QRectF
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath

from _0_Utilitaires._0_3_fonctions_utiles_pyqt6 import _dessiner_badge_validation

# 1 -- Fonction de création de l'icône ------------------------------------------


def _dessiner_icone_telechargement(
    painter: QPainter,
    centre: QPointF,
    taille: float,
    validee: bool,
    couleur_fleche_debut: str = "#ffb85c",
    couleur_fleche_fin: str = "#ff8c42",
    couleur_doc_debut: str = "#5eead4",
    couleur_doc_fin: str = "#14b8a6",
    vers_la_droite: bool = True,
) -> None:
    """Icône "document + flèche horizontale" : un feuillet à coin corné,
    avec quelques lignes de texte stylisées (dégradé orangé), sur lequel
    mord une flèche pleine horizontale (dégradé turquoise).

    Le document occupe toujours la même position, quelle que soit la valeur
    de `vers_la_droite` : seule la flèche est concernée par ce paramètre.
    La flèche occupe elle aussi toujours le même espace (même empreinte) ;
    `vers_la_droite=True` -> export (pointe à droite), `vers_la_droite=False`
    -> import (pointe à gauche) est obtenu en pivotant la flèche de 180°
    autour de son propre centre, sans déplacer son emprise. Pas d'ombre
    portée ni de reflet glossy."""

    couleur_fleche_debut = QColor(couleur_fleche_debut)
    couleur_fleche_fin = QColor(couleur_fleche_fin)
    couleur_doc_debut = QColor(couleur_doc_debut)
    couleur_doc_fin = QColor(couleur_doc_fin)

    cx, cy = centre.x(), centre.y()

    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # Marge globale de l'icône (faible, pour occuper un maximum de place)
    marge = taille * 0.04

    # ============================================================
    # DOCUMENT -- position et taille FIXES, indépendantes du sens
    # ============================================================
    largeur_doc = taille * 0.68
    hauteur_doc = taille - 2 * marge
    rayon_coin = taille * 0.07
    coin_pli = taille * 0.18

    x_doc_gauche = cx - taille / 2 + marge
    x_doc_droite = x_doc_gauche + largeur_doc
    y_doc_haut = cy - hauteur_doc / 2
    y_doc_bas = y_doc_haut + hauteur_doc

    rect_doc = QRectF(x_doc_gauche, y_doc_haut, largeur_doc, hauteur_doc)

    chemin_doc = QPainterPath()
    chemin_doc.addRoundedRect(rect_doc, rayon_coin, rayon_coin)

    # Coin corné, toujours en haut à droite du document (fixe)
    chemin_pli = QPainterPath()
    chemin_pli.moveTo(x_doc_droite - coin_pli, y_doc_haut)
    chemin_pli.lineTo(x_doc_droite, y_doc_haut)
    chemin_pli.lineTo(x_doc_droite, y_doc_haut + coin_pli)
    chemin_pli.closeSubpath()

    chemin_doc = chemin_doc.subtracted(chemin_pli)

    # Lignes de texte stylisées (3 barres arrondies), toujours au même endroit
    largeur_ligne = largeur_doc * 0.55
    epaisseur_ligne = taille * 0.06
    x_ligne_gauche = x_doc_gauche + largeur_doc * 0.18

    chemin_lignes = QPainterPath()
    for fraction_y in (0.28, 0.5, 0.72):
        y_ligne = y_doc_haut + hauteur_doc * fraction_y - epaisseur_ligne / 2
        rect_ligne = QRectF(x_ligne_gauche, y_ligne, largeur_ligne, epaisseur_ligne)
        chemin_lignes.addRoundedRect(
            rect_ligne, epaisseur_ligne / 2, epaisseur_ligne / 2
        )

    chemin_doc = chemin_doc.united(chemin_lignes)

    degrade_doc = QLinearGradient(QPointF(x_doc_gauche, cy), QPointF(x_doc_droite, cy))
    degrade_doc.setColorAt(0.0, couleur_doc_debut)
    degrade_doc.setColorAt(1.0, couleur_doc_fin)

    # ============================================================
    # FLÈCHE PLEINE HORIZONTALE -- emprise FIXE, mord sur le document
    # ============================================================
    # L'emprise (de x_fleche_gauche à x_fleche_droite) ne dépend jamais de
    # `vers_la_droite` : elle démarre à l'intérieur du document (chevauchement
    # volontaire) et va jusqu'au bord de l'icône. Seule l'extrémité qui porte
    # la pointe change, ce qui équivaut à une rotation de 180° de la flèche
    # autour de son propre centre.
    chevauchement = taille * 0.12
    x_fleche_gauche = x_doc_droite - chevauchement
    x_fleche_droite = cx + taille / 2 - marge

    hauteur_tige = taille * 0.16
    largeur_pointe = taille * 0.42

    longueur_totale = x_fleche_droite - x_fleche_gauche
    longueur_pointe = longueur_totale * 0.55
    longueur_tige = longueur_totale - longueur_pointe

    if vers_la_droite:
        x_queue = x_fleche_gauche
        x_fin_tige = x_fleche_gauche + longueur_tige
        x_pointe = x_fleche_droite
    else:
        x_queue = x_fleche_droite
        x_fin_tige = x_fleche_droite - longueur_tige
        x_pointe = x_fleche_gauche

    chemin_fleche = QPainterPath()
    chemin_fleche.moveTo(x_queue, cy - hauteur_tige / 2)
    chemin_fleche.lineTo(x_fin_tige, cy - hauteur_tige / 2)
    chemin_fleche.lineTo(x_fin_tige, cy - largeur_pointe / 2)
    chemin_fleche.lineTo(x_pointe, cy)
    chemin_fleche.lineTo(x_fin_tige, cy + largeur_pointe / 2)
    chemin_fleche.lineTo(x_fin_tige, cy + hauteur_tige / 2)
    chemin_fleche.lineTo(x_queue, cy + hauteur_tige / 2)
    chemin_fleche.closeSubpath()

    degrade_fleche = QLinearGradient(QPointF(x_queue, cy), QPointF(x_pointe, cy))
    degrade_fleche.setColorAt(0.0, couleur_fleche_debut)
    degrade_fleche.setColorAt(1.0, couleur_fleche_fin)

    # ============================================================
    # DESSIN (deux passes, une par couleur ; la flèche est dessinée
    # après le document afin de visiblement "mordre" dessus)
    # ============================================================
    painter.setPen(Qt.PenStyle.NoPen)

    painter.setBrush(QBrush(degrade_doc))
    painter.drawPath(chemin_doc)

    painter.setBrush(QBrush(degrade_fleche))
    painter.drawPath(chemin_fleche)

    # Badge de validation (optionnel)
    if validee:
        _dessiner_badge_validation(painter=painter, centre=centre, taille=taille)
