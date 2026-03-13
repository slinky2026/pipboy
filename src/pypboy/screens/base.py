from __future__ import annotations
import pygame
from pypboy.input.actions import Action

class Screen:
    name: str = "SCREEN"

    def handle_event(self, event: pygame.event.Event) -> None:
        
        pass

    def on_action(self, action: Action) -> None:
        
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        raise NotImplementedError

