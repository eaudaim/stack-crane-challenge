"""Helpers for drawing text overlays."""

import pygame
import math
import numpy as np

from .. import config


pygame.font.init()


def render_flat_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    text_color,
    shadow_color,
    x: int,
    y: int,
    dx: int,
    dy: int,
) -> None:
    """Render clean text with a short drop shadow."""

    rendered = font.render(text, True, text_color)
    shadow = font.render(text, True, shadow_color)
    surface.blit(shadow, (x + dx, y + dy))
    surface.blit(rendered, (x, y))


def render_neon_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    text_color,
    shadow_color,
    x: int,
    y: int,
    dx: int,
    dy: int,
) -> None:
    """Render bright neon text with an additive glow."""

    rendered = font.render(text, True, text_color)
    center = (x + rendered.get_width() // 2, y + rendered.get_height() // 2)

    for i, scale in enumerate((1.2, 1.4, 1.6)):
        glow = font.render(text, True, text_color)
        glow = pygame.transform.smoothscale(
            glow,
            (
                int(glow.get_width() * scale),
                int(glow.get_height() * scale),
            ),
        )
        glow.set_alpha(100 // (i + 1))
        rect = glow.get_rect(center=center)
        surface.blit(glow, rect.topleft, special_flags=pygame.BLEND_RGBA_ADD)

    shadow = font.render(text, True, shadow_color)
    surface.blit(shadow, (x + dx, y + dy))
    surface.blit(rendered, (x, y))


def render_vintage_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    text_color,
    shadow_color,
    x: int,
    y: int,
    dx: int,
    dy: int,
) -> None:
    """Render text with a warm retro look."""

    rendered = font.render(text, True, text_color)
    shadow = font.render(text, True, shadow_color)

    soft = pygame.transform.smoothscale(
        shadow,
        (int(shadow.get_width() * 1.1), int(shadow.get_height() * 1.1)),
    )
    soft.set_alpha(120)
    surface.blit(soft, (x + dx * 3, y + dy * 3))
    surface.blit(shadow, (x + dx, y + dy))

    width, height = rendered.get_size()

    dark_grad = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(height):
        alpha = int(60 * i / height)
        pygame.draw.line(dark_grad, (0, 0, 0, alpha), (0, i), (width, i))
    rendered.blit(dark_grad, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    light_grad = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(height):
        alpha = int(30 * (1 - i / height))
        pygame.draw.line(light_grad, (255, 255, 255, alpha), (0, i), (width, i))
    rendered.blit(light_grad, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    noise = pygame.Surface((width, height), pygame.SRCALPHA)
    arr = np.random.randint(0, 30, (height, width)).astype(np.uint8)
    pygame.surfarray.pixels_alpha(noise)[:, :] = arr
    rendered.blit(noise, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    surface.blit(rendered, (x, y))

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
    width, height = font.size(text)
    x = (config.WIDTH - width) // 2
    y = style.get("y_pos", config.HEIGHT // 3)
    dx, dy = style.get("shadow_offset", (2, 2))
    effect = style.get("effect", "flat")
    if effect == "neon":
        render_neon_text(surface, text, font, text_color, shadow_color, x, y, dx, dy)
    elif effect == "vintage":
        render_vintage_text(surface, text, font, text_color, shadow_color, x, y, dx, dy)
    else:
        render_flat_text(surface, text, font, text_color, shadow_color, x, y, dx, dy)


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
