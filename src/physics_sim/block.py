"""Creation utilities for falling blocks."""

from typing import Tuple

import pymunk
from .. import config


def create_block(space: pymunk.Space, x: float, y: float, variant: str,
                 mass: float = 5.0, size: Tuple[int, int] = (200, 100)) -> pymunk.Body:
    """Create a dynamic block body and add it to the space."""
    width, height = size
    moment = pymunk.moment_for_box(mass, (width, height))
    body = pymunk.Body(mass, moment)
    body.position = x, y
    shape = pymunk.Poly.create_box(body, (width, height))
    shape.friction = 0.7
    shape.elasticity = 0.1
    # ensure the block participates in collisions
    shape.collision_type = 1
    shape.group = 0

    # store variant to render the corresponding image
    body.variant = variant

    space.add(body, shape)
    return body
