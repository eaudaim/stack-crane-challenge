"""Helpers for drawing text overlays."""

import pygame
import math

from .. import config


pygame.font.init()


def draw_intro(surface: pygame.Surface, text: str | None = None, style_name: str | None = None) -> None:
    """Draw the intro text using the style defined in :mod:`config`.

    ``style_name`` can be one of the keys defined in ``config.INTRO_STYLES`` to
    pick an alternate appearance.
    """
    if text is None:
        text = config.INTRO_TEXT
    if style_name is not None:
        style = config.INTRO_STYLES.get(style_name, config.INTRO_STYLE)
    else:
        style = config.INTRO_STYLE
    font_name = style.get("font_name")
    if font_name:
        font = pygame.font.SysFont(font_name, style.get("font_size", 72))
    else:
        font = pygame.font.Font(None, style.get("font_size", 72))
    font.set_bold(True)
    palette = config.PALETTES.get(style.get("palette", "default"), {})
    text_color = palette.get("text", (255, 255, 255))
    shadow_color = palette.get("shadow", (0, 0, 0))
    rendered = font.render(text, True, text_color)
    shadow = font.render(text, True, shadow_color)
    x = (config.WIDTH - rendered.get_width()) // 2
    y = style.get("y_pos", config.HEIGHT // 3)
    dx, dy = style.get("shadow_offset", (2, 2))
    surface.blit(shadow, (x + dx, y + dy))
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


def draw_timer(surface: pygame.Surface, remaining: float) -> None:
    """Draw the countdown timer in the top left corner."""

    secs = max(0, math.ceil(remaining))
    color = (255, 0, 0) if secs <= 10 else config.PALETTES["default"]["text"]
    font = pygame.font.Font(None, 120)
    font.set_bold(True)
    text = str(secs)
    rendered = font.render(text, True, color)
    shadow = font.render(text, True, config.PALETTES["default"]["shadow"])
    surface.blit(shadow, (12, 12))
    surface.blit(rendered, (10, 10))
