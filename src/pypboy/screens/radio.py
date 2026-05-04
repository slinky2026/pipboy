import pygame
import os
import random
from .base import Screen
from pypboy.data import AppState


class RadioScreen(Screen):
    name = "RADIO"

    def __init__(self, state: AppState):
        self.state = state

        self.audio_path = "assets/audio"
        self.tracks = [
            f for f in os.listdir(self.audio_path)
            if f.endswith(".ogg") or f.endswith(".wav")
        ]

        self.playing = False
        self.current_track = None

        pygame.mixer.init()

    def play_random(self):
        if not self.tracks:
            print("No audio files found")
            return

        self.current_track = random.choice(self.tracks)
        full_path = os.path.join(self.audio_path, self.current_track)

        print("Playing:", full_path)

        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play()

        self.playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.playing:
                self.stop()
            else:
                self.play_random()

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((10, 30, 10))

        font = pygame.font.SysFont(None, 44)
        small = pygame.font.SysFont(None, 26)

        surface.blit(font.render("RADIO", True, (0, 255, 0)), (40, 40))

        if self.playing:
            text = f"PLAYING: {self.current_track}"
        else:
            text = "TAP TO PLAY"

        surface.blit(small.render(text, True, (0, 255, 0)), (40, 120))