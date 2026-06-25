################################################################################
# Projet de cartes de voyage                                                   #
# _4_Interface/_4_2_Style                                                      #
# 4.2.3 – Script permettant de mettre de la musique                            #
################################################################################


# 0 -- Initialisation ----------------------------------------------------------


import os, time, threading

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame


class MusicPlayer:
    def __init__(
        self,
        path: str,
        volume: float = 0.5,
        start_ms: int = 0,
        max_duration_ms: int = 10000,
        fade_out_ms: int = 2000,
    ):
        pygame.mixer.init()
        self.path = path
        self.volume = max(0.0, min(volume, 1.0))
        self.start_ms = max(0, start_ms)
        self.max_duration_ms = max_duration_ms
        self.fade_out_ms = fade_out_ms
        self.fade_interval_ms = 50
        self.is_playing = False
        self._stop_requested = False
        self.thread = None

    def play(self):
        if self.is_playing:
            return
        self.is_playing = True
        self._stop_requested = False
        pygame.mixer.music.load(self.path)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(start=self.start_ms / 1000.0)
        self.thread = threading.Thread(target=self._manage_playback)
        self.thread.start()

    def _manage_playback(self):
        if self.max_duration_ms > 0:
            time.sleep(self.max_duration_ms / 1000.0)
            if self.is_playing and not self._stop_requested:
                self.start_fade_out()

    def start_fade_out(self):
        if not self.is_playing or self._stop_requested:
            return
        current_volume = pygame.mixer.music.get_volume()
        steps = max(1, self.fade_out_ms // self.fade_interval_ms)
        for i in range(steps):
            if self._stop_requested:
                break
            time.sleep(self.fade_interval_ms / 1000.0)
            ratio = 1 - (i / steps)
            new_volume = current_volume * ratio
            pygame.mixer.music.set_volume(new_volume)
        self.stop()

    def stop(self):
        self._stop_requested = True
        pygame.mixer.music.stop()
        self.is_playing = False
        if self.thread and self.thread.is_alive():
            self.thread.join(
                timeout=0.1
            )  # Attend max 0.1s pour que le thread se termine

    def __del__(self):
        self.stop()
        pygame.mixer.quit()
