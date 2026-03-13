import pygame
from .base import Screen
from pypboy.data import AppState

class RadioScreen(Screen):
    name = "RADIO"
#self explanatory and easy for now tbh
    def __init__(self, state: AppState):
        self.state = state
        self.stations = ["Diamond City Radio", "Classical Radio", "Wasteland FM"]
        self.index = 0
        self.playing = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.index = (self.index - 1) % len(self.stations)
            elif event.key == pygame.K_DOWN:
                self.index = (self.index + 1) % len(self.stations)
            elif event.key == pygame.K_RETURN:
                self.playing = not self.playing  # toggle play

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((10, 30, 10))
        font = pygame.font.SysFont(None, 44)
        small = pygame.font.SysFont(None, 26)

        surface.blit(font.render("RADIO", True, (0, 255, 0)), (40, 40))
        surface.blit(small.render("↑/↓ select  |  ENTER toggle play", True, (0, 255, 0)), (40, 90))

        y = 140
        for i, st in enumerate(self.stations):
            prefix = "♪ " if (i == self.index and self.playing) else ("▶ " if i == self.index else "  ")
            surface.blit(small.render(prefix + st, True, (0, 255, 0)), (40, y))
            y += 30
