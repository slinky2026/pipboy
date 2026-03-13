import pygame
from .base import Screen
from pypboy.data import AppState


class DataScreen(Screen):
    #this is for the data tab
    #all placeholder right now
    name = "DATA"

    def __init__(self, state: AppState):
        #using shared state means screen displays live valyes without 'owning' data itslef
        self.state = state
        self.lines = [
            "System check: OK",
            "Sensors: (mock) OK", #fake for now but would like real
            "Storage: OK",
            "Last sync: never",
        ]

    def draw(self, surface: pygame.Surface) -> None:
        #rendders data contents, called once per frame
        fg = (0, 255, 0)
        dim = (0, 140, 0)
        title = pygame.font.SysFont(None, 44)
        small = pygame.font.SysFont(None, 26)

        surface.blit(title.render("DATA", True, fg), (40, 110))

        #vertical spacing
        y = 170
        for line in self.lines:
            surface.blit(small.render(line, True, dim), (40, y))
            y += 30
