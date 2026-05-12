import pygame
from .base import Screen
from pypboy.data import AppState, Item
from pypboy.input.actions import Action
from pypboy.ui.widgets import draw_listbox


class InventoryScreen(Screen):
    name = "INVENTORY"

    def __init__(self, state: AppState):
        self.state = state

        # Fallout 4-ish categories
        self.categories = ["WEAPONS", "APPAREL", "AID", "MISC"]
        self.cat_index = 0
        self.item_index = 0

    def _filtered(self) -> list[Item]:
        cat = self.categories[self.cat_index]
        return [i for i in self.state.inventory if i.category == cat]

    def on_action(self, action: Action) -> None:
        # Category switching
        if action == Action.LEFT:
            self.cat_index = (self.cat_index - 1) % len(self.categories)
            self.item_index = 0

        elif action == Action.RIGHT:
            self.cat_index = (self.cat_index + 1) % len(self.categories)
            self.item_index = 0

        # List navigation
        elif action == Action.UP:
            items = self._filtered()
            if items:
                self.item_index = (self.item_index - 1) % len(items)

        elif action == Action.DOWN:
            items = self._filtered()
            if items:
                self.item_index = (self.item_index + 1) % len(items)

        
        elif action == Action.SELECT:
            # could equip/use item later
            pass

        elif action == Action.BACK:
           
            pass

    def draw(self, surface: pygame.Surface):
    #draws same thing as data tab -> None:
        fg = (0, 255, 0)
        dim = (0, 140, 0)

        title_font = pygame.font.SysFont(None, 30)
        label_font = pygame.font.SysFont(None, 20)
        small_font = pygame.font.SysFont(None, 18)

        title_y = 88
        cat_y = 125
        panel_y = 155
        panel_h = 115

        left_x = 30
        left_w = 245

        right_x = 295
        right_w = 150

        # Header
        surface.blit(title_font.render("INVENTORY", True, fg), (left_x, title_y))
        surface.blit(label_font.render("[WEAPONS] APPAREL AID MISC", True, fg), (left_x, cat_y))

        # Category strip (Fallout-ish)
        cat_text = "  ".join(
            f"[{c}]" if i == self.cat_index else c
            for i, c in enumerate(self.categories)
        )
        surface.blit(small.render(cat_text, True, fg), (40, 155))

        # Panels
        list_rect = pygame.Rect(40, 190, 320, 420)
        detail_rect = pygame.Rect(380, 190, 300, 420)
        pygame.draw.rect(surface, fg, list_rect, width=1)
        pygame.draw.rect(surface, fg, detail_rect, width=1)

        # Items in current category
        items = self._filtered()
        if not items:
            surface.blit(small.render("(empty)", True, dim), (list_rect.x + 12, list_rect.y + 12))
            surface.blit(small.render("No items in this category.", True, dim), (detail_rect.x + 12, detail_rect.y + 12))
            return

        # Clamp index safely
        self.item_index = max(0, min(self.item_index, len(items) - 1))

        # Left list
        names = [i.name for i in items]
        draw_listbox(surface, list_rect, names, self.item_index, fg=fg, dim=dim)

        # Right details
        item = items[self.item_index]

        surface.blit(small.render(item.name, True, fg), (detail_rect.x + 12, detail_rect.y + 12))
        surface.blit(small.render(f"Value: {item.value}", True, dim), (detail_rect.x + 12, detail_rect.y + 50))
        surface.blit(small.render(f"Weight: {item.weight:.1f}", True, dim), (detail_rect.x + 12, detail_rect.y + 78))

        # Description for each silly item
        desc = item.description or ""
        if desc:
            words = desc.split()
            line = ""
            y = detail_rect.y + 120
            for w in words:
                test = (line + " " + w).strip()
                # crude char-based wrap (good enough for now)
                if len(test) > 28:
                    surface.blit(small.render(line, True, dim), (detail_rect.x + 12, y))
                    y += 26
                    line = w
                else:
                    line = test
            if line:
                surface.blit(small.render(line, True, dim), (detail_rect.x + 12, y))

        # Controls 
        surface.blit(
            small.render("←/→ category   ↑/↓ select   Enter=Select   Backspace=Back", True, dim),
            (40, 630),
        )
