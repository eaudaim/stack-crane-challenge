"""Headless Pygame renderer for the challenge."""

from typing import Dict
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
    assets["sky"] = {
        name: pygame.image.load(os.path.join(config.ASSET_PATHS["sky"], name)).convert_alpha()
        for name in config.SKY_OPTIONS
    }
    assets["crane_bar"] = pygame.image.load(os.path.join(config.ASSET_PATHS["crane"], "crane_bar.png")).convert_alpha()
    assets["hook"] = pygame.image.load(os.path.join(config.ASSET_PATHS["crane"], "hook.png")).convert_alpha()

    # load block variants lazily
    assets["blocks"] = {}
    for file in os.listdir(config.ASSET_PATHS["block"]):
        if file.endswith(".png"):
            assets["blocks"][file] = pygame.image.load(os.path.join(config.ASSET_PATHS["block"], file)).convert_alpha()
    return assets


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

        # NEW: draw physical hitboxes in red for debug purposes
        for shape in body.shapes:
            if isinstance(shape, pymunk.Poly):
                vertices = []
                for v in shape.get_vertices():
                    x, y = v.rotated(body.angle) + body.position
                    py_y = config.HEIGHT - int(y)
                    vertices.append((int(x), py_y))
                if len(vertices) > 2:
                    pygame.draw.polygon(surface, (255, 0, 0), vertices, 2)

        variant = getattr(body, "variant", None)
        if variant and variant in assets["blocks"]:
            img = assets["blocks"][variant]
            x, y = body.position
            # Convert from Pymunk's bottom-left origin to Pygame's top-left
            # coordinate system.
            py_y = config.HEIGHT - int(y)
            rect = img.get_rect(center=(int(x), py_y))
            surface.blit(img, rect)
    arr = pygame.surfarray.array3d(surface)
    return np.transpose(arr, (1, 0, 2))
