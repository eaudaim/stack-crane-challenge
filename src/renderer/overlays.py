"""Helpers for drawing text overlays."""

import pygame

from .. import config


pygame.font.init()

def draw_intro(surface: pygame.Surface, text: str = "PEUT-IL FINIR CETTE TOUR EN 60s ?") -> None:
    """Draw an intro overlay text on the given surface."""
    font = pygame.font.Font(None, 72)
    rendered = font.render(text, True, config.PALETTES["default"]["text"])
    shadow = font.render(text, True, config.PALETTES["default"]["shadow"])
    x = (config.WIDTH - rendered.get_width()) // 2
    y = config.HEIGHT // 3
    surface.blit(shadow, (x + 2, y + 2))
    surface.blit(rendered, (x, y))
