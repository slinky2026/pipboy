import pygame
import time
import requests
from .base import Screen
from pypboy.ui.widgets import draw_meter
from pypboy.data import AppState
from pypboy.sensor_reader import SensorReader

#stuff for weather location data pulling 
YORK_LAT = 53.9590
YORK_LON = -1.0815

#WEATHER_CODES = {
  #  0: "CLEAR",
   # 1: "MAINLY CLEAR",
    #2: "PARTLY CLOUDY",
    #3: "CLOUDY",
  #  45: "FOG",
   # 48: "FOG",
    #51: "DRIZZLE",
    #53: "DRIZZLE",
    #55: "DRIZZLE",
    #61: "RAIN",
    #63: "RAIN",
    #65: "HEAVY RAIN",
    #71: "SNOW",
    #73: "SNOW",
    #75: "HEAVY SNOW",
    #80: "SHOWERS",
    #81: "SHOWERS",
    #82: "HEAVY SHOWERS",
    #95: "STORM",    
#}
class StatsScreen(Screen):
    name = "STATS"

    def __init__(self, state: AppState):
        self.state = state
        #self.weather = None
        self.temperature = None
        self.weather_error = "NO DATA"
        self.last_weather_update = 0
        self.weather_refresh_seconds = 30
        self.sensor = SensorReader(port="/dev/ttyUSB0")
        self.heart_rate = None
        self.ir_value = None

    def fetch_temperature(self):
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={YORK_LAT}&longitude={YORK_LON}"
            "&current=temperature_2m"
            "&timezone=Europe%2FLondon"
        )

        try:
            print("Fetching weather...")
            response = requests.get(url, timeout=10)
            print("Status:", response.status_code)
            print("Response:", response.text[:300])

            response.raise_for_status()
            data = response.json()

            self.temperature = data["current"]["temperature_2m"]
            self.weather_error = None

            print("Temperature:", self.temperature)

        except Exception as e:
            print("Weather failed:", repr(e))
            self.temperature = None
            self.weather_error = "NO DATA"  

    def update_sensor_if_needed(self):
        hr, ir = self.sensor.update()

        if hr is not None:
            self.heart_rate = hr

        if ir is not None:
            self.ir_value = ir

    def update_weather_if_needed(self):
        now = time.time()
        if self.temperature is None or now - self.last_weather_update > self.weather_refresh_seconds:
            self.fetch_temperature()
            self.last_weather_update = now

    def handle_event(self, event: pygame.event.Event) -> None:
        pass
     #   if event.type == pygame.KEYDOWN:
      #      if event.key in (pygame.K_EQUALS, pygame.K_PLUS):
       #         self.state.vitals.hp = min(self.state.vitals.hp_max, self.state.vitals.hp + 1)
        #    elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
         #       self.state.vitals.hp = max(0, self.state.vitals.hp - 1)

    #def fetch_weather(self) -> None:
     #   url = ("https://api.open-meteo.com/v1/forecast"
      #      f"?latitude={YORK_LAT}&longitude={YORK_LON}"
       #     "&current=temperature_2m,relative_humidity_2m,"
        #    "precipitation,weather_code,wind_speed_10m"
         #   "&timezone=Europe%2FLondon")
        #try:
         #   response = requests.get(url, timeout=5)
          #  response.raise_for_status()
           # current = response.json()["current"]

#            code = current.get("weather_code", -1)

          #  self.weather = {
           #    "temp": current.get("temperature_2m"),
            #    "humidity": current.get("relative_humidity_2m"),
             #   "rain": current.get("precipitation"),
              #  "wind": current.get("wind_speed_10m"),
               # "code": code,
                #"label": WEATHER_CODES.get(code, "UNKNOWN"), 
           # }
            #self.weather_error = None

        #except Exception as e:
         #   print("Weather fetch failed:", repr(e))
          #  self.weather = None
           # self.weather_error = "SIGNAL LOST"

    #def update_weather_if_needed(self) -> None:
     #   now = time.time()
      #  if self.weather is None or now - self.last_weather_update > self.weather_refresh_seconds:
       #     self.fetch_weather()
        #    self.last_weather_update = now

    #def draw(self, surface: pygame.Surface, x: int, y: int, w: int, h: int, fg) -> None:
     #   pygame.draw.rect(surface, fg, (x, y, w, h), 1)

      #  title_font = pygame.font.SysFont(None, 22)
       # small_font = pygame.font.SysFont(None, 18)

       # surface.blit(title_font.render("WEATHER", True, fg), (x + 8, y + 8))
        #surface.blit(small_font.render("YORK, UK", True, fg), (x + 8, y + 32))

       # if self.weather_error:
        #    surface.blit(small_font.render(self.weather_error, True, fg), (x + 8, y + 65))
         #   return

       # wt = self.weather

        #lines = [
         #   wt["label"],
          #  f"TEMP {wt['temp']} C",
           # f"HUM  {wt['humidity']}%",
            #f"WIND {wt['wind']} KM/H",
           # f"RAIN {wt['rain']} MM",
        #]

       # line_y = y + 62
        #for line in lines:
         #   surface.blit(small_font.render(line, True, fg), (x + 8, line_y))
          #  line_y += 22

    def draw_bioscan_panel(self, surface: pygame.Surface, x: int, y: int, w: int, h: int, fg) -> None:
        pygame.draw.rect(surface, fg, (x, y, w, h), 1)

        title_font = pygame.font.SysFont(None, 18)
        small_font = pygame.font.SysFont(None, 16)
        value_font = pygame.font.SysFont(None, 20)
        
        surface.blit(title_font.render("BIOSCAN", True, fg), (x + 8, y + 6))

        heart_rate = "--"
        spo2 = "--"

        surface.blit(small_font.render("HEART RATE", True, fg), (x + 8, y + 30))
        surface.blit(value_font.render(f"{heart_rate} BPM", True, fg), (x + 8, y + 48))

        surface.blit(small_font.render("O2 LEVEL", True, fg), (x + 8, y + 72))
        surface.blit(value_font.render(f"{spo2} %", True, fg), (x + 8, y + 90))
    
    
    def draw(self, surface: pygame.Surface) -> None:
        self.update_sensor_if_needed() #you know the drill blah blah
        self.update_weather_if_needed()
        #self.draw_weather_panel(surface, panel_x, panel_y, panel_w, panel_h, fg)

        fg = (0, 255, 0)
        width, height = surface.get_size()

        font = pygame.font.SysFont(None, 24)
        title_font = pygame.font.SysFont(None, 28)

        surface.blit(title_font.render("STATUS", True, fg), (30, 85))

        v = self.state.vitals
        draw_meter(surface, 30, 140, 230, 12, v.hp, v.hp_max, "HP")
        draw_meter(surface, 30, 190, 230, 12, v.rad, 100, "RAD")

            # simple weather box
        pygame.draw.rect(surface, fg, (300, 90, 150, 90), 1)
        surface.blit(font.render("WEATHER", True, fg), (310, 100))
        surface.blit(font.render("YORK", True, fg), (310, 125))

        if self.temperature is not None:
            text = f"{self.temperature} C"
        else:
            text = self.weather_error

        surface.blit(font.render(text, True, fg), (310, 150))
        
        self.draw_bioscan_panel(surface, 300, 190, 150, 115, fg)
        