from __future__ import annotations

import random
from dataclasses import dataclass
import pygame

from .. import config


@dataclass
class ConfettiParticle:
    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    life: float


def spawn_confetti(count: int, y_pos: float) -> list[ConfettiParticle]:
    particles = []
    for _ in range(count):
        vx = random.uniform(-150, 150)
        vy = random.uniform(-250, -50)
        p = ConfettiParticle(
            random.uniform(0, config.WIDTH),
            y_pos,
            vx,
            vy,
            random.choice(config.CONFETTI_COLORS),
            config.CONFETTI_LIFETIME,
        )
        particles.append(p)
    return particles


def update_confetti(particles: list[ConfettiParticle], dt: float) -> None:
    for p in particles[:]:
        p.vy += config.CONFETTI_GRAVITY * dt
        p.x += p.vx * dt
        p.y += p.vy * dt
        p.life -= dt
        if p.life <= 0 or p.y > config.HEIGHT + 20:
            particles.remove(p)


def draw_confetti(surface: pygame.Surface, particles: list[ConfettiParticle]) -> None:
    for p in particles:
        rect = pygame.Rect(int(p.x), int(p.y), 4, 4)
        pygame.draw.rect(surface, p.color, rect)
