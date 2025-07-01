"""Utilities to build a Pymunk space for the simulation."""

import pymunk
from .. import config


def init_space() -> pymunk.Space:
    """Initialise the physics space with gravity and a static floor."""
    space = pymunk.Space()
    # In Pymunk the Y axis points upward, so a negative value means gravity
    # towards the bottom of the screen.  The original code used a positive value
    # which made the blocks "fall" upwards.  We flip the sign so that the
    # simulation matches the visual representation used by Pygame.
    space.gravity = (0, -900)

    # The floor should be located near the bottom of the space.  Previously it
    # was placed at ``HEIGHT - 10`` which corresponds to the top edge when using
    # Pymunk's coordinate system.  Moving it near ``y=10`` allows the blocks to
    # properly land and stack on screen.
    floor_y = config.FLOOR_Y
    floor = pymunk.Segment(
        space.static_body, (0, floor_y), (config.WIDTH, floor_y), 5
    )
    floor.friction = 1.0
    space.add(floor)
    return space
