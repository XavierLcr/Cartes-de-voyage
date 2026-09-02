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
    vers_la_droite: bool = True,
) -> None:
    """Icône "document + flèche horizontale" : un feuillet à coin corné,
    avec quelques lignes de texte stylisées (dégradé orangé), d'où part une
    flèche pleine horizontale (dégradé turquoise). `vers_la_droite=True` ->
    export (flèche vers la droite) ; `vers_la_droite=False` -> import
    (flèche vers la gauche, tout est simplement mis en miroir). Pas d'ombre
    portée ni de reflet glossy."""

    COULEUR_FLECHE_DEBUT = QColor("#ffb85c")
    COULEUR_FLECHE_FIN = QColor("#ff8c42")
    COULEUR_DOC_DEBUT = QColor("#5eead4")
    COULEUR_DOC_FIN = QColor("#14b8a6")

    cx, cy = centre.x(), centre.y()
    sens = 1 if vers_la_droite else -1

    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # -- Fonction de décalage / miroir ---------------------------------------
    def dx(valeur: float) -> float:
        return cx + sens * valeur

    # -- Dimensions de base : document ---------------------------------------
    largeur_doc = taille * 0.52
    hauteur_doc = taille * 0.75
    rayon_coin = taille * 0.06
    coin_pli = taille * 0.14

    offset_doc_gauche = -taille * 0.42
    offset_doc_droite = offset_doc_gauche + largeur_doc

    y_doc_haut = cy - hauteur_doc / 2
    y_doc_bas = y_doc_haut + hauteur_doc

    # -- Dimensions de base : flèche -----------------------------------------
    hauteur_tige = taille * 0.14
    largeur_pointe = taille * 0.32
    longueur_tige = taille * 0.22
    longueur_pointe = taille * 0.16

    offset_fleche_debut = offset_doc_droite
    offset_fin_tige = offset_fleche_debut + longueur_tige
    offset_pointe = offset_fin_tige + longueur_pointe

    # ============================================================
    # DOCUMENT (rectangle arrondi, coin corné, lignes de texte)
    # ============================================================
    x_doc_gauche, x_doc_droite = dx(offset_doc_gauche), dx(offset_doc_droite)
    rect_doc = QRectF(
        min(x_doc_gauche, x_doc_droite),
        y_doc_haut,
        abs(x_doc_droite - x_doc_gauche),
        hauteur_doc,
    )

    chemin_doc = QPainterPath()
    chemin_doc.addRoundedRect(rect_doc, rayon_coin, rayon_coin)

    # Coin corné, du côté d'où part la flèche
    chemin_pli = QPainterPath()
    chemin_pli.moveTo(dx(offset_doc_droite - coin_pli), y_doc_haut)
    chemin_pli.lineTo(dx(offset_doc_droite), y_doc_haut)
    chemin_pli.lineTo(dx(offset_doc_droite), y_doc_haut + coin_pli)
    chemin_pli.closeSubpath()

    chemin_doc = chemin_doc.subtracted(chemin_pli)

    # Lignes de texte stylisées (3 barres arrondies)
    largeur_ligne = largeur_doc * 0.6
    epaisseur_ligne = taille * 0.055
    x_ligne_gauche = dx(offset_doc_gauche + largeur_doc * 0.2)
    x_ligne_droite = dx(offset_doc_gauche + largeur_doc * 0.2 + sens * largeur_ligne)
    rect_ligne_largeur = abs(x_ligne_droite - x_ligne_gauche)
    x_ligne_min = min(x_ligne_gauche, x_ligne_droite)

    chemin_lignes = QPainterPath()
    for fraction_y in (0.28, 0.5, 0.72):
        y_ligne = y_doc_haut + hauteur_doc * fraction_y - epaisseur_ligne / 2
        rect_ligne = QRectF(x_ligne_min, y_ligne, rect_ligne_largeur, epaisseur_ligne)
        chemin_lignes.addRoundedRect(
            rect_ligne, epaisseur_ligne / 2, epaisseur_ligne / 2
        )

    chemin_doc = chemin_doc.united(chemin_lignes)

    degrade_doc = QLinearGradient(
        QPointF(dx(offset_doc_gauche), cy), QPointF(dx(offset_doc_droite), cy)
    )
    degrade_doc.setColorAt(0.0, COULEUR_DOC_DEBUT)
    degrade_doc.setColorAt(1.0, COULEUR_DOC_FIN)

    # ============================================================
    # FLÈCHE PLEINE HORIZONTALE
    # ============================================================
    chemin_fleche = QPainterPath()
    chemin_fleche.moveTo(dx(offset_fleche_debut), cy - hauteur_tige / 2)
    chemin_fleche.lineTo(dx(offset_fin_tige), cy - hauteur_tige / 2)
    chemin_fleche.lineTo(dx(offset_fin_tige), cy - largeur_pointe / 2)
    chemin_fleche.lineTo(dx(offset_pointe), cy)
    chemin_fleche.lineTo(dx(offset_fin_tige), cy + largeur_pointe / 2)
    chemin_fleche.lineTo(dx(offset_fin_tige), cy + hauteur_tige / 2)
    chemin_fleche.lineTo(dx(offset_fleche_debut), cy + hauteur_tige / 2)
    chemin_fleche.closeSubpath()

    degrade_fleche = QLinearGradient(
        QPointF(dx(offset_fleche_debut), cy), QPointF(dx(offset_pointe), cy)
    )
    degrade_fleche.setColorAt(0.0, COULEUR_FLECHE_DEBUT)
    degrade_fleche.setColorAt(1.0, COULEUR_FLECHE_FIN)

    # ============================================================
    # DESSIN (deux passes, une par couleur)
    # ============================================================
    painter.setPen(Qt.PenStyle.NoPen)

    painter.setBrush(QBrush(degrade_doc))
    painter.drawPath(chemin_doc)

    painter.setBrush(QBrush(degrade_fleche))
    painter.drawPath(chemin_fleche)

    # Badge de validation (optionnel)
    if validee:
        _dessiner_badge_validation(painter=painter, centre=centre, taille=taille)
