"""Utilities to build a Pymunk space for the simulation."""

import pymunk
from .. import config


def init_space() -> pymunk.Space:
    """Initialise the physics space with gravity and a static floor."""
    space = pymunk.Space()
    space.gravity = (0, 900)

    floor = pymunk.Segment(space.static_body, (0, config.HEIGHT - 10), (config.WIDTH, config.HEIGHT - 10), 5)
    floor.friction = 1.0
    space.add(floor)
    return space
