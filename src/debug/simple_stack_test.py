"""Simple diagnostic video generator for block stacking."""

import os

import pygame
from pydub import AudioSegment

from .. import config
from ..physics_sim import block, space_builder
from ..renderer import pygame_renderer
from ..video_export import moviepy_exporter


def run(output: str = os.path.join(config.OUTPUT_DIR, "stack_test.mp4"), seconds: int = 10) -> None:
    """Generate a short video dropping two blocks at the same position."""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    assets = pygame_renderer.load_assets()
    space = space_builder.init_space()
    screen = pygame.Surface((config.WIDTH, config.HEIGHT))

    crane_x = config.WIDTH // 2
    drop_y = config.HEIGHT - config.CRANE_DROP_HEIGHT
    block_variant = next(iter(assets["blocks"]))
    drop_frames = [config.FPS, config.FPS * 3]
    total_frames = seconds * config.FPS

    frames = []
    for i in range(total_frames):
        if i in drop_frames:
            block.create_block(space, crane_x, drop_y, block_variant)
            print(f"Bloc créé à ({crane_x}, {drop_y})")
            print(f"Nombre de bodies: {len(space.bodies)}")
            print(f"Nombre de shapes: {len(space.shapes)}")
        space.step(1 / config.FPS)
        arr = pygame_renderer.render_frame(screen, space, assets, crane_x, "skyline_day.png")
        frames.append(arr)

    audio = AudioSegment.silent(duration=seconds * 1000)
    moviepy_exporter.export_video(frames, audio, output)


if __name__ == "__main__":
    run()
