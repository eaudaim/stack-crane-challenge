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


def _draw_centered(surface: pygame.Surface, text: str, color, size: int = 96) -> None:
    """Helper to draw centered bold text with a drop shadow."""
    font = pygame.font.Font(None, size)
    font.set_bold(True)
    rendered = font.render(text, True, color)
    shadow = font.render(text, True, config.PALETTES["default"]["shadow"])
    x = (config.WIDTH - rendered.get_width()) // 2
    y = (config.HEIGHT - rendered.get_height()) // 2
    surface.blit(shadow, (x + 2, y + 2))
    surface.blit(rendered, (x, y))


def draw_victory(surface: pygame.Surface) -> None:
    """Display the victory message."""
    _draw_centered(surface, "Victoire", (255, 255, 0))


def draw_fail(surface: pygame.Surface) -> None:
    """Display the failure message."""
    _draw_centered(surface, "Perdu", (255, 0, 0))
