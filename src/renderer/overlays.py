"""Helpers for drawing text overlays."""

import pygame
import math
import random

from .. import config


pygame.font.init()


def render_flat_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    text_color: tuple[int, int, int],
    shadow_color: tuple[int, int, int],
    pos: tuple[int, int],
    offset: tuple[int, int],
) -> None:
    """Render text with a simple drop shadow."""

    x, y = pos
    dx, dy = offset
    rendered = font.render(text, True, text_color)
    shadow = font.render(text, True, shadow_color)
    surface.blit(shadow, (x + dx, y + dy))
    surface.blit(rendered, (x, y))


def render_neon_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    text_color: tuple[int, int, int],
    shadow_color: tuple[int, int, int],
    pos: tuple[int, int],
    offset: tuple[int, int],
) -> None:
    """Render text with a neon glow effect."""

    x, y = pos
    dx, dy = offset
    base = font.render(text, True, text_color)
    shadow = font.render(text, True, shadow_color)

    # Draw colored shadow first
    surface.blit(shadow, (x + dx, y + dy))

    # Additive glow passes around the text
    for i in range(3):
        scale = 1 + 0.15 * (i + 1)
        glow = pygame.transform.smoothscale(
            base, (int(base.get_width() * scale), int(base.get_height() * scale))
        )
        glow = pygame.transform.smoothscale(glow, base.get_size())
        glow.set_alpha(80 - i * 20)
        gx = x - (glow.get_width() - base.get_width()) // 2
        gy = y - (glow.get_height() - base.get_height()) // 2
        surface.blit(glow, (gx, gy), special_flags=pygame.BLEND_RGBA_ADD)

    surface.blit(base, (x, y))


def render_vintage_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    text_color: tuple[int, int, int],
    shadow_color: tuple[int, int, int],
    pos: tuple[int, int],
    offset: tuple[int, int],
) -> None:
    """Render text with a vintage look (soft shadow and slight grain)."""

    x, y = pos
    dx, dy = offset

    base = font.render(text, True, text_color)

    # Apply a subtle vertical gradient (lighter at the top)
    w, h = base.get_size()
    gradient = pygame.Surface((w, h), pygame.SRCALPHA)
    for row in range(h):
        factor = 1 - 0.2 * (row / max(1, h - 1))
        val = int(255 * factor)
        pygame.draw.line(gradient, (val, val, val, 255), (0, row), (w, row))
    base.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Long soft shadow made from multiple blurred passes
    shadow = font.render(text, True, shadow_color)
    for i in range(2):
        scale = 1 + 0.1 * (i + 1)
        blurred = pygame.transform.smoothscale(
            shadow,
            (int(shadow.get_width() * scale), int(shadow.get_height() * scale)),
        )
        blurred = pygame.transform.smoothscale(blurred, shadow.get_size())
        blurred.set_alpha(90 - i * 30)
        bx = x + dx - (blurred.get_width() - base.get_width()) // 2
        by = y + dy - (blurred.get_height() - base.get_height()) // 2
        surface.blit(blurred, (bx, by))

    # Add optional light grain
    noise = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(w * h // 50):
        nx = random.randint(0, w - 1)
        ny = random.randint(0, h - 1)
        alpha = random.randint(10, 30)
        noise.set_at((nx, ny), (0, 0, 0, alpha))
    base.blit(noise, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    surface.blit(base, (x, y))


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
    size = font.size(text)
    x = (config.WIDTH - size[0]) // 2
    y = style.get("y_pos", config.HEIGHT // 3)
    dx, dy = style.get("shadow_offset", (2, 2))

    effect = style.get("effect", "flat")
    if effect == "neon":
        render_neon_text(surface, text, font, text_color, shadow_color, (x, y), (dx, dy))
    elif effect == "vintage":
        render_vintage_text(surface, text, font, text_color, shadow_color, (x, y), (dx, dy))
    else:
        render_flat_text(surface, text, font, text_color, shadow_color, (x, y), (dx, dy))


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

