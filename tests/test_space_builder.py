import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.physics_sim import space_builder


def test_space_has_gravity():
    space = space_builder.init_space()
    assert space.gravity == (0, -900)


def test_apply_adhesion_forces():
    import src.config as config
    original = config.BLOCK_ADHESION_FORCE
    config.BLOCK_ADHESION_FORCE = 100.0
    try:
        space = space_builder.init_space()
        from src.physics_sim import block
        y_offset = config.BLOCK_SIZE[1]
        b1 = block.create_block(space, 100, 100)
        b2 = block.create_block(space, 100, 100 + y_offset)
        b1.force = (0, 0)
        b2.force = (0, 0)
        space_builder.apply_adhesion_forces(space)
        assert b1.force.y > 0
        assert b2.force.y < 0
    finally:
        config.BLOCK_ADHESION_FORCE = original
