import sys
from pathlib import Path
import pymunk

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.physics_sim import space_builder, block
from src import config


def test_victory_not_triggered_on_spawn():
    space = space_builder.init_space()
    spawn_y = config.HEIGHT - config.CRANE_DROP_HEIGHT
    block.create_block(space, 100, spawn_y)
    space.step(1 / config.FPS)
    dynamic_bodies = [
        b
        for b in space.bodies
        if isinstance(b, pymunk.Body) and b.body_type == pymunk.Body.DYNAMIC
    ]
    resting = [b for b in dynamic_bodies if abs(b.velocity.y) < 1]
    triggered = False
    if resting:
        top = max(b.position.y + config.BLOCK_SIZE[1] / 2 for b in resting)
        triggered = top >= spawn_y
    assert not triggered
