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

    def _wrap_text(self, text: str, max_chars: int) -> list[str]:
        """Simple word wrap for the small detail panel."""
        words = text.split()
        lines = []
        line = ""

        for word in words:
            test = (line + " " + word).strip()

            if len(test) > max_chars:
                if line:
                    lines.append(line)
                line = word
            else:
                line = test

        if line:
            lines.append(line)

        return lines

    def draw(self, surface: pygame.Surface) -> None:
        fg = (0, 255, 0)
        dim = (0, 140, 0)

        # Small-screen friendly fonts
        title_font = pygame.font.SysFont(None, 30)
        label_font = pygame.font.SysFont(None, 20)
        small_font = pygame.font.SysFont(None, 17)
        tiny_font = pygame.font.SysFont(None, 15)

        # Layout for 480x320 display
        left_x = 30
        right_x = 292

        title_y = 88
        cat_y = 124
        panel_y = 150
        panel_h = 120

        list_rect = pygame.Rect(left_x, panel_y, 245, panel_h)
        detail_rect = pygame.Rect(right_x, panel_y, 155, panel_h)

        # Header
        surface.blit(title_font.render("INVENTORY", True, fg), (left_x, title_y))

        # Category strip
        cat_text = "  ".join(
            f"[{c}]" if i == self.cat_index else c
            for i, c in enumerate(self.categories)
        )
        surface.blit(label_font.render(cat_text, True, fg), (left_x, cat_y))

        # Panels
        pygame.draw.rect(surface, fg, list_rect, width=1)
        pygame.draw.rect(surface, fg, detail_rect, width=1)

        # Items in current category
        items = self._filtered()

        if not items:
            surface.blit(
                small_font.render("(empty)", True, dim),
                (list_rect.x + 10, list_rect.y + 12)
            )
            surface.blit(
                tiny_font.render("No items", True, dim),
                (detail_rect.x + 10, detail_rect.y + 12)
            )
            return

        # Clamp index safely
        self.item_index = max(0, min(self.item_index, len(items) - 1))

        # Left list
        y = list_rect.y + 14

        for i, item in enumerate(items[:4]):  # keep it short for tiny screen
            selected = i == self.item_index
            color = fg if selected else dim
            prefix = ">" if selected else " "

            text = f"{prefix} {item.name}"
            surface.blit(
                small_font.render(text, True, color),
                (list_rect.x + 10, y)
            )
            y += 24

        # Right details
        item = items[self.item_index]

        detail_x = detail_rect.x + 9
        y = detail_rect.y + 12

        # Trim long names so they don't clip too badly
        item_name = item.name
        if len(item_name) > 14:
            item_name = item_name[:13] + "."

        surface.blit(
            small_font.render(item_name, True, fg),
            (detail_x, y)
        )
        y += 26

        surface.blit(
            tiny_font.render(f"Value: {item.value}", True, dim),
            (detail_x, y)
        )
        y += 20

        surface.blit(
            tiny_font.render(f"Weight: {item.weight:.1f}", True, dim),
            (detail_x, y)
        )
        y += 22

        # Description
        desc = item.description or ""
        if desc:
            lines = self._wrap_text(desc, max_chars=17)

            for line in lines[:2]:  # only show two lines to avoid overflow
                surface.blit(
                    tiny_font.render(line, True, dim),
                    (detail_x, y)
                )
                y += 17

        # Compact controls footer
        footer = "L/R CAT  U/D ITEM  ENTER USE"
        surface.blit(
            tiny_font.render(footer, True, dim),
            (left_x, 286)
        )