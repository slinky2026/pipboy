import pygame
import time
import requests
from .base import Screen
from pypboy.ui.widgets import draw_meter
from pypboy.data import AppState

#stuff for weather location data pulling 
YORK_LAT = 53.9590
YORK_LON = -1.0815

WEATHER_CODES = {
    0: "CLEAR",
    1: "MAINLY CLEAR",
    2: "PARTLY CLOUDY",
    3: "CLOUDY",
    45: "FOG",
    48: "FOG",
    51: "DRIZZLE",
    53: "DRIZZLE",
    55: "DRIZZLE",
    61: "RAIN",
    63: "RAIN",
    65: "HEAVY RAIN",
    71: "SNOW",
    73: "SNOW",
    75: "HEAVY SNOW",
    80: "SHOWERS",
    81: "SHOWERS",
    82: "HEAVY SHOWERS",
    95: "STORM",    
}
class StatsScreen(Screen):
    name = "STATS"

    def __init__(self, state: AppState):
        self.state = state
        self.weather = None
        self.weather_error = "NO DATA"
        self.last_weather_update = 0
        self.weather_refresh_seconds = 600 #10 mins to min computation


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                self.state.vitals.hp = min(self.state.vitals.hp_max, self.state.vitals.hp + 1)
            elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                self.state.vitals.hp = max(0, self.state.vitals.hp - 1)

    def fetch_weather(self) -> None:
        url = ("https://api.open-meteo.com/v1/forecast"
            f"?latitude={YORK_LAT}&longitude={YORK_LON}"
            "&current=temperature_2m,relative_humidity_2m,"
            "precipitation,weather_code,wind_speed_10m"
            "&timezone=Europe%2FLondon")
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            current = response.json()["current"]

            code = current.get("weather_code", -1)

            self.weather = {
               "temp": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "rain": current.get("precipitation"),
                "wind": current.get("wind_speed_10m"),
                "code": code,
                "label": WEATHER_CODES.get(code, "UNKNOWN"), 
            }
            self.weather_error = None

        except Exception:
            self.weather = None
            self.weather_error = "SIGNAL LOST"

    def update_weather_if_needed(self) -> None:
        now = time.time()
        if self.weather is None or now - self.last_weather_update > self.weather_refresh_seconds:
            self.fetch_weather()
            self.last_weather_update = now

    def draw_weather_panel(self, surface: pygame.Surface, x: int, y: int, w: int, h: int, fg) -> None:
        pygame.draw.rect(surface, fg, (x, y, w, h), 1)

        title_font = pygame.font.SysFont(None, 22)
        small_font = pygame.font.SysFont(None, 18)

        surface.blit(title_font.render("WEATHER", True, fg), (x + 8, y + 8))
        surface.blit(small_font.render("YORK, UK", True, fg), (x + 8, y + 32))

        if self.weather_error:
            surface.blit(small_font.render(self.weather_error, True, fg), (x + 8, y + 65))
            return

        wt = self.weather

        lines = [
            wt["label"],
            f"TEMP {wt['temp']} C",
            f"HUM  {wt['humidity']}%",
            f"WIND {wt['wind']} KM/H",
            f"RAIN {wt['rain']} MM",
        ]

        line_y = y + 62
        for line in lines:
            surface.blit(small_font.render(line, True, fg), (x + 8, line_y))
            line_y += 22


    def draw(self, surface: pygame.Surface) -> None:
        self.update_weather_if_needed
        # core draws background;  just draw content
        font = pygame.font.SysFont(None, 44)
        fg = (0, 255, 0)
        width, height = surface.get_size()

        sx = width/480
        sy = height/320

        title_font = pygame.font.SysFont(None, int(34 * sy))


        surface.blit(font.render("STATS", True, fg), (40, 110))
#all fake fro now- heart rate key will want that in
        v = self.state.vitals

        meter_x = int(28*sx)
        meter_w = int(250*sx)
        meter_h = max(10, int(16*sy))

        draw_meter(surface, meter_x, int(135 * sy), meter_w, meter_h, v.hp, v.hp_max, "HP")
        draw_meter(surface, meter_x, int(195 * sy), meter_w, meter_h, v.rad, 100, "RAD")

        panel_x = int(305 * sx)
        panel_y = int(70 * sy)
        panel_w = int(160 * sx)
        panel_h = int(205 * sy)

        self.draw_weather_panel(surface, panel_x, panel_y, panel_w, panel_h, fg)
