from dataclasses import dataclass
import pygame

#all colours and stufffff

@dataclass(frozen=True)
class Fonts:
    title: pygame.font.Font
    tab: pygame.font.Font
    body: pygame.font.Font
    small: pygame.font.Font
    mono: pygame.font.Font


@dataclass(frozen=True)
class Colors:
    bg: tuple[int, int, int]
    fg: tuple[int, int, int]
    dim: tuple[int, int, int]
    frame: tuple[int, int, int]


def load_theme() -> tuple[Fonts, Colors]:
    
    #Load fonts once, Call this after pygame.init().
    #Uses system fonts first cos windows dev
    #Later  can swap to a .ttf in your fonts/ folder.
    
    # System fonts SHOULD EXIST IN WINDOWS
    # If a name isn’t found, pygame fallback cos my computer is a SHITBAG!!!!
    title = pygame.font.SysFont("bahnschrift", 52, bold=True)
    tab = pygame.font.SysFont("bahnschrift", 30, bold=True)
    body = pygame.font.SysFont("bahnschrift", 28)
    small = pygame.font.SysFont("bahnschrift", 22)

    # Monospace for numbers/readouts
    mono = pygame.font.SysFont("consolas", 24)

    fonts = Fonts(title=title, tab=tab, body=body, small=small, mono=mono)

    colors = Colors(
        bg=(10, 24, 10),
        fg=(0, 255, 0),
        dim=(0, 140, 0),
        frame=(0, 110, 0),
    )

    return fonts, colors
