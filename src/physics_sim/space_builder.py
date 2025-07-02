"""Utilities to build a Pymunk space for the simulation."""

import pymunk
import random
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


def apply_bug_forces(space: pymunk.Space) -> None:
    """Inject random forces to create a deliberately unstable simulation."""
    if config.BUG_SIDE_IMPULSE <= 0 and config.BUG_SPIN_VELOCITY <= 0:
        return
    for body in space.bodies:
        if body.body_type != pymunk.Body.DYNAMIC:
            continue
        if config.BUG_SIDE_IMPULSE > 0:
            impulse = random.uniform(-config.BUG_SIDE_IMPULSE, config.BUG_SIDE_IMPULSE)
            body.apply_impulse_at_local_point((impulse, 0))
        if config.BUG_SPIN_VELOCITY > 0:
            body.angular_velocity += random.uniform(-config.BUG_SPIN_VELOCITY, config.BUG_SPIN_VELOCITY)


def apply_adhesion_forces(space: pymunk.Space) -> None:
    """Attract vertically aligned blocks to reinforce stacking stability."""
    force = config.BLOCK_ADHESION_FORCE
    if force <= 0:
        return

    dynamic = [b for b in space.bodies if b.body_type == pymunk.Body.DYNAMIC]
    width, height = config.BLOCK_SIZE
    x_thresh = width * 0.5
    y_thresh = height * 1.5

    for i, b1 in enumerate(dynamic):
        for b2 in dynamic[i + 1:]:
            dx = b2.position.x - b1.position.x
            dy = b2.position.y - b1.position.y
            if abs(dx) > x_thresh:
                continue
            if 0 < dy <= y_thresh:
                b1.apply_force_at_local_point((0, force))
                b2.apply_force_at_local_point((0, -force))
            elif -y_thresh <= dy < 0:
                b1.apply_force_at_local_point((0, -force))
                b2.apply_force_at_local_point((0, force))
