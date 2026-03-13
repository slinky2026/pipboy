import pygame
#lotsa import
from pypboy.screens.stats import StatsScreen
from pypboy.screens.inventory import InventoryScreen
from pypboy.screens.data import DataScreen
from pypboy.screens.map import MapScreen
from pypboy.screens.radio import RadioScreen
from pypboy.data import AppState
from pypboy.input.manager import InputManager
from pypboy.input.actions import Action
from pypboy.ui.theme import load_theme




class Pypboy:
    def __init__(self, title: str, width: int, height: int, fps: int = 60):
        self.title = title
        self.width = width
        self.height = height
        self.fps = fps

        self.state = AppState()
        self.input = InputManager()

        self.running = False
        self.active_tab = 0  # 0..4
#tab titles duh
        self.tabs = ["STATS", "INV", "DATA", "MAP", "RADIO"]

        self.screens = [
            StatsScreen(self.state),
            InventoryScreen(self.state),
            DataScreen(self.state),
            MapScreen(self.state),
            RadioScreen(self.state),
        ]

        # Visual tuning we want that wasteland aesthetic
        self.bg = (10, 24, 10)           # deep green background
        self.fg = (0, 255, 0)            # pip-boy green
        self.fg_dim = (0, 140, 0)        # dim green
        self.frame = (0, 110, 0)         # border green
        self.nav_h = 68                  # top bar height

        self._flicker_phase = 0.0

    def set_tab(self, index: int) -> None:
        self.active_tab = max(0, min(len(self.screens) - 1, index))

   

    def draw_frame(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()
        # outer border
        pygame.draw.rect(surface, self.frame, pygame.Rect(12, 12, w - 24, h - 24), width=2)
        # inner border
        pygame.draw.rect(surface, self.frame, pygame.Rect(20, 20, w - 40, h - 40), width=1)

    def draw_scanlines(self, surface: pygame.Surface) -> None:
        # the horizontal lines for the fallout feel
        w, h = surface.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        # alpha is small so it’s subtle
        for y in range(0, h, 2):
            overlay.fill((0, 0, 0, 22), rect=pygame.Rect(0, y, w, 1))
        for y in range(0, h, 10):
            overlay.fill((0, 0, 0, 40), rect=pygame.Rect(0, y, w, 2))
        surface.blit(overlay, (0, 0))

    def draw_nav(self, surface: pygame.Surface) -> None:
        font = self.fonts.tab
        fg = self.colors.fg
        dim = self.colors.dim

        w, _ = surface.get_size()

        # bar background line + separator
        pygame.draw.line(surface, self.frame, (24, self.nav_h), (w - 24, self.nav_h), width=2)

        # draw tab labels evenly across noice
        left = 40
        right = w - 40
        span = right - left
        step = span // len(self.tabs)

        for i, name in enumerate(self.tabs):
            x = left + i * step
            is_active = (i == self.active_tab)

            color = self.fg if is_active else self.fg_dim
            label = font.render(name, True, color)

            # draw small active underline
            surface.blit(label, (x, 28))
            if is_active:
                underline_y = 28 + label.get_height() + 6
                pygame.draw.line(
                    surface, self.fg,
                    (x, underline_y),
                    (x + label.get_width(), underline_y),
                    width=3
                )

            # draw separators between tabs (except after last)
            if i < len(self.tabs) - 1:
                sep_x = x + step - 18
                pygame.draw.line(surface, self.frame, (sep_x, 26), (sep_x, self.nav_h - 10), width=1)

    def apply_flicker(self, surface: pygame.Surface, dt: float) -> None:
        # very subtle brightness flicker again fallout feelin
        self._flicker_phase += dt
        # every ~0.12s vary alpha a bit
        if int(self._flicker_phase * 8) % 2 == 0:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 10))
            surface.blit(overlay, (0, 0))

    #FROM HERE IS MAIN BIT

    def run(self) -> None:
        pygame.init()

        fonts, colors = load_theme()
        self.fonts = fonts
        self.colors = colors


        screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption(self.title)
        self.width, self.height = screen.get_size()

        clock = pygame.time.Clock()
        nav_font = pygame.font.SysFont(None, 32) #cool font selec
        hint_font = pygame.font.SysFont(None, 20)

        self.running = True
        while self.running:
            dt = clock.tick(self.fps) / 1000.0

            for event in pygame.event.get():
                self.input.process_pygame_event(event)

            while True:
                ev = self.input.pop()
                if ev is None:
                    break
                    
                action = ev.action
               # print("ACTION:", action)


                if action == Action.QUIT:
                    self.running = False
                    break
                #next bit is all the mapping to button stuff

                elif action == Action.TAB_1:
                     self.set_tab(0)
                elif action == Action.TAB_2:
                    self.set_tab(1)
                elif action == Action.TAB_3:
                    self.set_tab(2)
                elif action == Action.TAB_4:
                    self.set_tab(3)
                elif action == Action.TAB_5:
                    self.set_tab(4)
                
                else:
                    self.screens[self.active_tab].on_action(action)

                # Forward events to active screen
                #self.screens[self.active_tab].handle_event(event)

            self.screens[self.active_tab].update(dt)

            # Background
            screen.fill(self.bg)

            # Draw active screen into the content area (below nav)
            # We’ll “clip” so screens can’t draw over the nav bar.
            content_rect = pygame.Rect(0, self.nav_h + 10, self.width, self.height - (self.nav_h + 10))
            prev_clip = screen.get_clip()
            screen.set_clip(content_rect)
            self.screens[self.active_tab].draw(screen)
            #print("TAB", self.active_tab, "->", type(self.screens[self.active_tab]), "from", type(self.screens[self.active_tab]).__module__)

            screen.set_clip(prev_clip)

            # Overlays on top (nav, frame, scanlines, hint)
            self.draw_nav(screen)
            self.draw_frame(screen)
            self.draw_scanlines(screen)
            self.apply_flicker(screen, dt)
            #like a key or legend 
            hint = "1 Stats  2 Inv  3 Data  4 Map  5 Radio   |   ESC Quit"
            hint_surf = hint_font.render(hint, True, self.fg_dim)
            y = max(0, self.height - hint_surf.get_height() - 10)
            screen.blit(hint_surf, (24, y))

            pygame.display.flip()

        pygame.quit()
