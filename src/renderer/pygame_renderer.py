"""Headless Pygame renderer for the challenge."""

from typing import Dict
import math
import os

import pygame
import numpy as np
import pymunk

from .. import config

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((1, 1))


_DEF_FONT = None


def load_assets() -> Dict[str, pygame.Surface]:
    """Load image assets into a dictionary."""
    assets = {}
    assets["sky"] = {}
    for name in config.SKY_OPTIONS:
        img = pygame.image.load(os.path.join(config.ASSET_PATHS["sky"], name)).convert_alpha()
        if img.get_size() != (config.WIDTH, config.HEIGHT):
            img = pygame.transform.smoothscale(img, (config.WIDTH, config.HEIGHT))
        assets["sky"][name] = img
    assets["crane_bar"] = pygame.image.load(os.path.join(config.ASSET_PATHS["crane"], "crane_bar.png")).convert_alpha()
    assets["hook"] = pygame.image.load(os.path.join(config.ASSET_PATHS["crane"], "hook.png")).convert_alpha()

    # load block variants lazily
    assets["blocks"] = {}
    for file in os.listdir(config.ASSET_PATHS["block"]):
        if file.endswith(".png"):
            img = pygame.image.load(os.path.join(config.ASSET_PATHS["block"], file)).convert_alpha()
            if img.get_size() != config.BLOCK_SIZE:
                img = pygame.transform.smoothscale(img, config.BLOCK_SIZE)
            assets["blocks"][file] = img
    return assets


def rotate_surface(img: pygame.Surface, angle_rad: float) -> pygame.Surface:
    """Return a new surface rotated to match the given body angle."""
    angle_deg = -math.degrees(angle_rad)
    return pygame.transform.rotate(img, angle_deg)


def render_frame(surface: pygame.Surface, space, assets, crane_x: float, sky_name: str) -> np.ndarray:
    """Render a single frame and return it as a numpy array."""
    surface.blit(assets["sky"][sky_name], (0, 0))
    bar_img = assets["crane_bar"]
    if bar_img.get_width() != config.WIDTH:
        bar_img = pygame.transform.scale(bar_img, (config.WIDTH, bar_img.get_height()))
    surface.blit(bar_img, (0, config.CRANE_BAR_Y))

    hook_img = assets["hook"]
    hook_y = config.CRANE_BAR_Y + config.HOOK_Y_OFFSET
    surface.blit(hook_img, (crane_x - hook_img.get_width() // 2, hook_y))
    for body in space.bodies:
        if isinstance(body, pymunk.Body) and body.body_type != pymunk.Body.DYNAMIC:
            continue


        variant = getattr(body, "variant", None)
        if variant and variant in assets["blocks"]:
            base_img = assets["blocks"][variant]
            img = rotate_surface(base_img, body.angle)
            x, y = body.position
            # Convert from Pymunk's bottom-left origin to Pygame's top-left
            # coordinate system.
            py_y = config.HEIGHT - int(y)
            rect = img.get_rect(center=(int(x), py_y))
            surface.blit(img, rect)
    arr = pygame.surfarray.array3d(surface)
    return np.transpose(arr, (1, 0, 2))
