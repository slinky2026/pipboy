import pygame


def draw_meter(surface: pygame.Surface, x: int, y: int, w: int, h: int,
               value: int, max_value: int, label: str,
               fg=(0, 255, 0), dim=(0, 80, 0)) -> None:
    # outline
    pygame.draw.rect(surface, fg, (x, y, w, h), width=1)
    # fill
    frac = 0 if max_value <= 0 else max(0.0, min(1.0, value / max_value))
    inner_w = int((w - 2) * frac)
    pygame.draw.rect(surface, fg, (x + 1, y + 1, inner_w, h - 2), width=0)

    font = pygame.font.SysFont(None, 22)
    txt = font.render(f"{label} {value}/{max_value}", True, fg)
    surface.blit(txt, (x, y - 22))


def draw_listbox(surface: pygame.Surface, rect: pygame.Rect, items: list[str], index: int,
                 fg=(0, 255, 0), dim=(0, 140, 0)) -> None:
    pygame.draw.rect(surface, fg, rect, width=1)

    font = pygame.font.SysFont(None, 26)
    line_h = 30
    padding = 10

    # scrolling window
    visible = max(1, (rect.height - 2 * padding) // line_h)
    start = max(0, index - visible // 2)
    end = min(len(items), start + visible)
    start = max(0, end - visible)

    y = rect.y + padding
    for i in range(start, end):
        is_sel = (i == index)
        prefix = "▶ " if is_sel else "  "
        color = fg if is_sel else dim
        txt = font.render(prefix + items[i], True, color)
        surface.blit(txt, (rect.x + padding, y))
        y += line_h
