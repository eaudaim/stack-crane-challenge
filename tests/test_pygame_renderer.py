import sys
from pathlib import Path
import numpy as np
import pygame

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.renderer import pygame_renderer
from src.physics_sim import space_builder
from src.physics_sim import block


def test_render_frame_shape(tmp_path):
    assets = {
        "sky": {"skyline_day.png": pygame.Surface((1080, 1920))},
        "crane_bar": pygame.Surface((1080, 50)),
        "hook": pygame.Surface((50, 50)),
        "blocks": {"block.png": pygame.Surface((100, 100))},
    }
    space = space_builder.init_space()
    block.create_block(space, 540, 100, "block.png")
    surface = pygame.Surface((1080, 1920))
    arr = pygame_renderer.render_frame(surface, space, assets, 540, "skyline_day.png")
    assert arr.shape[0] == 1920 and arr.shape[1] == 1080
