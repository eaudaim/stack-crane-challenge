import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.physics_sim import space_builder


def test_space_has_gravity():
    space = space_builder.init_space()
    assert space.gravity == (0, 900)
