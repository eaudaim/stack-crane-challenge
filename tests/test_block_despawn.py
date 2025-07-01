import sys
from pathlib import Path
import math
import pymunk

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.physics_sim import space_builder, block
from src import config


def simulate_step(space, steps):
    for _ in range(steps):
        space.step(1 / config.FPS)


def test_only_first_block_remains_on_floor():
    space = space_builder.init_space()
    spawn_y = config.HEIGHT - config.CRANE_DROP_HEIGHT

    first = block.create_block(space, 100, spawn_y)
    second = block.create_block(space, 400, spawn_y)

    unsupported = {}
    falling = set()
    first_block = first

    def _has_block_on_top(body, bodies):
        bb = list(body.shapes)[0].bb
        for other in bodies:
            if other is body:
                continue
            obb = list(other.shapes)[0].bb
            if (
                obb.bottom > bb.top - 5
                and obb.bottom < bb.top + config.BLOCK_SIZE[1] / 2
                and obb.right > bb.left + 10
                and obb.left < bb.right - 10
            ):
                return True
        return False

    def _is_on_floor(body):
        bb = list(body.shapes)[0].bb
        return bb.bottom <= config.FLOOR_Y + 5

    def _is_tilted(body):
        angle = abs(body.angle % math.pi)
        if angle > math.pi / 2:
            angle = math.pi - angle
        return angle > config.BLOCK_SIDE_ANGLE

    total_steps = int(config.FPS * (config.BLOCK_DESPAWN_DELAY + 4))
    for _ in range(total_steps):
        space.step(1 / config.FPS)
        dynamic = [b for b in space.bodies if b.body_type == pymunk.Body.DYNAMIC]
        resting = [b for b in dynamic if abs(b.velocity.y) < 1]
        for b in resting:
            protected_first = (
                b is first_block
                and _is_on_floor(b)
                and not _has_block_on_top(b, dynamic)
            )
            if (
                protected_first
                or (not _is_on_floor(b) and not _is_tilted(b))
                or _has_block_on_top(b, dynamic)
            ):
                unsupported[b] = 0.0
                continue

            unsupported[b] = unsupported.get(b, 0.0) + 1 / config.FPS
            if unsupported[b] >= config.BLOCK_DESPAWN_DELAY:
                for s in b.shapes:
                    s.sensor = True
                b.velocity = (0, -300)
                falling.add(b)

        for b in list(falling):
            if b.position.y < -config.BLOCK_SIZE[1]:
                space.remove(b, *b.shapes)
                falling.remove(b)
                unsupported.pop(b, None)

    remaining = [b for b in space.bodies if b.body_type == pymunk.Body.DYNAMIC]
    assert first_block in remaining
    assert second not in remaining
