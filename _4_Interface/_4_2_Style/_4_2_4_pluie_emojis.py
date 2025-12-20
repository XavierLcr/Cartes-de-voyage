import sys
import random
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsTextItem
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor


class EmojiTombant(QGraphicsTextItem):
    """Classe représentant un emoji tombant avec effet de vent."""

    def __init__(self, emoji, force_vent_globale=1.0):
        super().__init__(emoji)
        self.setFont(QFont("Arial", 16))
        self.vitesse_chute = random.uniform(1, 3)  # Vitesse de chute verticale
        # Vitesse horizontale (vent) : légèrement aléatoire autour de la force globale
        self.vitesse_vent = (
            random.uniform(-0.6, 0.6) + force_vent_globale
        ) * random.choice([-1, 1])

    def avancer(self):
        """Met à jour la position de l'emoji (chute + vent)."""
        self.setY(self.y() + self.vitesse_chute)  # Chute verticale
        self.setX(self.x() + self.vitesse_vent)  # Déplacement horizontal (vent)


class VuePluieEmojis(QGraphicsView):
    """Vue transparente et non bloquante pour afficher une pluie d'emojis."""

    def __init__(
        self,
        constantes,
        duree_ms,
        intervalle_timer_ms,
        force_vent_globale=1.0,
        parent=None,
    ):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.constantes = constantes
        self.liste_emojis = self.constantes.dict_themes_temporaires.get(
            "pluie_emojis", []
        )
        self.emojis_tombants = []
        self.duree_ms = duree_ms
        self.force_vent_globale = force_vent_globale
        self.parent = parent
        self.intervalle_timer = intervalle_timer_ms  # millisecondes

        # Configuration pour la transparence et la non-interaction
        self.scene.setBackgroundBrush(QBrush(QColor(0, 0, 0, 0)))  # Fond transparent
        self.setStyleSheet("background: transparent; border: none;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )  # Permet aux clics de traverser
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Initialise la taille
        self.mettre_a_jour_taille()

        # Timers
        self.timer_creation = QTimer(self)
        self.timer_creation.timeout.connect(self.creer_emoji)
        self.timer_creation.start(100)

        self.timer_animation = QTimer(self)
        self.timer_animation.timeout.connect(self.mettre_a_jour_emojis)
        self.timer_animation.start(self.intervalle_timer)

        QTimer.singleShot(self.duree_ms, self.arreter_creation)

    def mettre_a_jour_taille(self):
        """Met à jour la taille de la scène."""
        if self.parent:
            self.setSceneRect(0, 0, self.parent.width(), self.parent.height())
            self.setGeometry(0, 0, self.parent.width(), self.parent.height())

    def creer_emoji(self):
        """Crée un nouvel emoji."""
        x = random.uniform(0, self.scene.width())
        y = -20
        emoji = random.choice(self.liste_emojis)
        emoji_tombant = EmojiTombant(emoji, self.force_vent_globale)
        emoji_tombant.setPos(x, y)
        self.scene.addItem(emoji_tombant)
        self.emojis_tombants.append(emoji_tombant)

    def mettre_a_jour_emojis(self):
        """Met à jour les emojis."""
        for emoji in self.emojis_tombants[:]:
            emoji.avancer()
            if emoji.y() > self.scene.height():
                self.scene.removeItem(emoji)
                self.emojis_tombants.remove(emoji)
        if not self.emojis_tombants and not self.timer_creation.isActive():
            self.timer_animation.stop()

    def arreter_creation(self):
        """Arrête la création de nouveaux emojis."""
        self.timer_creation.stop()

    def demarrer(self):
        """Démarre l'animation."""
        self.timer_creation.start(500)
        self.timer_animation.start(self.intervalle_timer)

    def arreter(self):
        """Arrête l'animation."""
        self.timer_creation.stop()
        self.timer_animation.stop()
        for emoji in self.emojis_tombants:
            self.scene.removeItem(emoji)
        self.emojis_tombants.clear()

    def resizeEvent(self, event):
        """Met à jour la taille si la fenêtre est redimensionnée."""
        self.mettre_a_jour_taille()
        super().resizeEvent(event)
