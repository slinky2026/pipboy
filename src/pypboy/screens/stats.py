import pygame
from .base import Screen
from pypboy.ui.widgets import draw_meter
from pypboy.data import AppState


class StatsScreen(Screen):
    name = "STATS"

    def __init__(self, state: AppState):
        self.state = state

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                self.state.vitals.hp = min(self.state.vitals.hp_max, self.state.vitals.hp + 1)
            elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                self.state.vitals.hp = max(0, self.state.vitals.hp - 1)

    def draw(self, surface: pygame.Surface) -> None:
        # core draws background;  just draw content
        font = pygame.font.SysFont(None, 44)
        fg = (0, 255, 0)

        surface.blit(font.render("STATUS", True, fg), (40, 110))
#all fake fro now- heart rate key will want that in
        v = self.state.vitals
        draw_meter(surface, 40, 180, 280, 18, v.hp, v.hp_max, "HP")
        draw_meter(surface, 40, 240, 280, 18, v.ap, v.ap_max, "AP")
        draw_meter(surface, 40, 300, 280, 18, v.rad, 100, "RAD")
