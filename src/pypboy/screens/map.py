import math
import os
from pathlib import Path

import pygame
import requests

from .base import Screen
from pypboy.data import AppState
from pypboy.input.actions import Action


class MapScreen(Screen):
    """
    MAP screen DEBUGGING ONLY on my piece of shit laptop

    - Uses OpenStreetMap  tiles (https://tile.openstreetmap.org/{z}/{x}/{y}.png)
    - Caches tiles to disk so don't redownload constantly
    - pretends "player location" by panning lat/lon with navigation actions for now
    - Applies a green overlay for the Pip-Boy look ( core scanlines still apply cos done in master script isnt it)
    """

    name = "MAP"

    def __init__(self, state):
        self.state = state

        # Start somewhere sensible for dev n real thing wabt actual location
        self.lat = 53.9590
        self.lon = -1.0815

        # Map zoom level 
        # Keep modest for performance. this laptop is a shitbox
        self.zoom = 15

        # Tile config (OSM tiles are 256x256)
        self.tile_size = 256

        # Cache folder (relative to project root)
        self.cache_root = Path("cache") / "tiles"

        # In-memory cache for already-loaded pygame surfaces
        # key: (z,x,y) -> pygame.Surface
        self.surface_cache = {}

        # Fallback tile surface if fetch fails
        self.fallback_tile = pygame.Surface((self.tile_size, self.tile_size))
        self.fallback_tile.fill((5, 20, 5))
        pygame.draw.rect(self.fallback_tile, (0, 255, 0), (0, 0, self.tile_size, self.tile_size), 1)

  #INPUTS
    def on_action(self, action):
        # Pan step changes with zoom (higher zoom => smaller degrees per step)
        step = self._pan_step_deg()

        if action == Action.UP:
            self.lat = self.lat + step
            if self.lat > 85.0:
                self.lat = 85.0

        elif action == Action.DOWN:
            self.lat = self.lat - step
            if self.lat < -85.0:
                self.lat = -85.0

        elif action == Action.LEFT:
            self.lon = self.lon - step

        elif action == Action.RIGHT:
            self.lon = self.lon + step

        elif action == Action.SELECT:
            self.zoom = self.zoom + 1
            if self.zoom > 18:
                self.zoom = 18
            self.surface_cache.clear()  # flush memory cache to avoid huge RAM lol

        elif action == Action.BACK:
            self.zoom = self.zoom - 1
            if self.zoom < 2:
                self.zoom = 2
            self.surface_cache.clear()

        # Keep longitude in [-180, 180] for neatness or it goes CRAZY
        if self.lon > 180:
            self.lon = self.lon - 360
        elif self.lon < -180:
            self.lon = self.lon + 360

   #RENDER
    def draw(self, surface):
        width = surface.get_width()
        height = surface.get_height()

        # Background 
        surface.fill((10, 24, 10))

        # Determine which tile is at the center (player position)
        tile_x_float, tile_y_float = self._latlon_to_tile_float(self.lat, self.lon, self.zoom)
        center_tile_x = int(tile_x_float)
        center_tile_y = int(tile_y_float)

        # Pixel offset within the center tile (so movement is smooth)
        frac_x = tile_x_float - center_tile_x
        frac_y = tile_y_float - center_tile_y
        offset_x = int(frac_x * self.tile_size)
        offset_y = int(frac_y * self.tile_size)

        # How many tiles need to cover the screen
        tiles_needed_x = (width // self.tile_size) + 3
        tiles_needed_y = (height // self.tile_size) + 3

        # Top-left tile coordinates
        start_tile_x = center_tile_x - (tiles_needed_x // 2)
        start_tile_y = center_tile_y - (tiles_needed_y // 2)

        # Pixel location to start drawing so that player position is centered
        start_pixel_x = (width // 2) - (tiles_needed_x // 2) * self.tile_size - offset_x
        start_pixel_y = (height // 2) - (tiles_needed_y // 2) * self.tile_size - offset_y

        # Draw tiles
        number_of_tiles = 2 ** self.zoom  # number of tiles across at this zoom

        for row in range(tiles_needed_y):
            for col in range(tiles_needed_x):
                tile_x = start_tile_x + col
                tile_y = start_tile_y + row

                # Wrap x (longitude wraps around the world)
                wrapped_tile_x = tile_x % number_of_tiles

                # Clamp y (latitude does not wrap; beyond range is "no tile")
                if tile_y < 0 or tile_y >= number_of_tiles:
                    tile_surface = self.fallback_tile
                else:
                    tile_surface = self._get_tile_surface(self.zoom, wrapped_tile_x, tile_y)

                draw_x = start_pixel_x + (col * self.tile_size)
                draw_y = start_pixel_y + (row * self.tile_size)
                surface.blit(tile_surface, (draw_x, draw_y))

        # Apply a Pip-Boy green tint overlay (scanlines/flicker already in core
        tint = pygame.Surface((width, height), pygame.SRCALPHA)
        tint.fill((0, 255, 0, 60))  # adjust alpha for stronger/weaker tint
        surface.blit(tint, (0, 0))

        # Draw player marker at screen center
        pygame.draw.circle(surface, (0, 255, 0), (width // 2, height // 2), 10, 2)
        pygame.draw.line(surface, (0, 255, 0), (width // 2, height // 2 - 16), (width // 2, height // 2 - 6), 2)

        # HUD text
        title_font = pygame.font.SysFont(None, 44)
        small_font = pygame.font.SysFont(None, 24)
        mono_font = pygame.font.SysFont("consolas", 22)

        title_text = title_font.render("MAP", True, (0, 255, 0))
        help_text = small_font.render(
            "Arrows: pan   Enter: zoom in   Backspace: zoom out",
            True,
            (0, 140, 0)
        )
        coords_text = mono_font.render(
            f"Lat {self.lat:.5f}   Lon {self.lon:.5f}   Z {self.zoom}",
            True,
            (0, 140, 0)
        )

        surface.blit(title_text, (40, 110))
        surface.blit(help_text, (40, 155))
        surface.blit(coords_text, (40, 185))

  #TYLE FETCH
    def _get_tile_surface(self, z, x, y):
        key = (z, x, y)

        if key in self.surface_cache:
            return self.surface_cache[key]

        tile_path = self.cache_root / str(z) / str(x) / f"{y}.png"

        # Ensure cached on disk; if not, try downloading
        if not tile_path.exists():
            self._download_tile(z, x, y, tile_path)

        # Load from disk if present; else fallback
        if tile_path.exists():
            try:
                tile_surface = pygame.image.load(str(tile_path)).convert()
            except Exception:
                tile_surface = self.fallback_tile
        else:
            tile_surface = self.fallback_tile

        self.surface_cache[key] = tile_surface
        return tile_surface

    def _download_tile(self, z, x, y, tile_path):
        tile_path.parent.mkdir(parents=True, exist_ok=True)

        url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"

        try:
            # Keep timeout short so the UI doesn't hang if offline
            response = requests.get(
                url,
                timeout=2.5,
                headers={"User-Agent": "pipboy-ui-prototype/0.1"}
            )

            if response.status_code == 200 and response.content:
                tile_path.write_bytes(response.content)

        except Exception:
            # Offline or blocked: just skip; fallback tile will be used hopefully
            return

  #maths bullshit
    def _latlon_to_tile_float(self, lat, lon, zoom):
        """
        Convert lat/lon to fractional tile coordinates at a given zoom.
        This is standard Web Mercator tiling math.
        """
        if lat < -85.05112878:
            lat = -85.05112878
        elif lat > 85.05112878:
            lat = 85.05112878

        number_of_tiles = 2.0 ** zoom
        x = ((lon + 180.0) / 360.0) * number_of_tiles

        lat_rad = math.radians(lat)
        y = (
            1.0
            - math.log(math.tan(lat_rad) + (1.0 / math.cos(lat_rad))) / math.pi
        ) / 2.0 * number_of_tiles

        return x, y

    def _pan_step_deg(self):
        
        # These values feel decent for debugging for now idk
        if self.zoom >= 17:
            return 0.0007
        elif self.zoom >= 16:
            return 0.0015
        elif self.zoom >= 15:
            return 0.003
        elif self.zoom >= 14:
            return 0.006
        else:
            return 0.012