"""Batch generation of crane challenge videos."""

import argparse
import os
import random

import pygame
import pymunk
import numpy as np
from pydub import AudioSegment

from .. import config
from ..physics_sim import space_builder, block
from ..renderer import pygame_renderer, overlays
from ..audio import sound_manager
from ..video_export import moviepy_exporter


def generate_once(index: int, assets, sounds=None) -> None:
    """Generate a single video with random parameters."""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    space = space_builder.init_space()
    screen = pygame.Surface((config.WIDTH, config.HEIGHT))
    frames = []
    events = []
    block_count = random.randint(*config.BLOCK_COUNT_RANGE)
    sky = random.choice(config.SKY_OPTIONS)
    crane_x = config.WIDTH // 2
    crane_speed = random.randint(*config.GRUE_SPEED_RANGE)
    crane_dir = 1
    for i in range(config.DURATION * config.FPS):
        t = i / config.FPS
        dynamic_bodies = [b for b in space.bodies if isinstance(b, pymunk.Body) and b.body_type == pymunk.Body.DYNAMIC]
        if len(dynamic_bodies) < block_count and i % (config.FPS * config.BLOCK_DROP_INTERVAL) == 0:
            drop_x = crane_x + random.randint(*config.DROP_VARIATION_RANGE)
            block_variant = random.choice(config.BLOCK_VARIANTS)
            block.create_block(
                space,
                drop_x,
                config.HEIGHT - config.CRANE_DROP_HEIGHT,
                block_variant,
            )
            events.append((t, "impact"))
        crane_x += crane_dir * crane_speed / config.FPS
        if crane_x > config.WIDTH - config.CRANE_MOVEMENT_BOUNDS:
            crane_x = config.WIDTH - config.CRANE_MOVEMENT_BOUNDS
            crane_dir = -1
        elif crane_x < config.CRANE_MOVEMENT_BOUNDS:
            crane_x = config.CRANE_MOVEMENT_BOUNDS
            crane_dir = 1
        space.step(1 / config.FPS)
        arr = pygame_renderer.render_frame(screen, space, assets, crane_x, sky)
        if i < config.FPS * 2:
            overlays.draw_intro(screen)
            arr = pygame.surfarray.array3d(screen)
            arr = np.transpose(arr, (1, 0, 2))
        frames.append(arr)
    if sounds:
        audio = sound_manager.mix_tracks(config.DURATION, events, sounds)
    else:
        audio = AudioSegment.silent(duration=config.DURATION * 1000)
    output = os.path.join(config.OUTPUT_DIR, f"run_{index}.mp4")
    moviepy_exporter.export_video(frames, audio, output)


def main(count: int, with_audio: bool = True) -> None:
    assets = pygame_renderer.load_assets()
    sounds = sound_manager.load_sounds() if with_audio else None
    for i in range(count):
        generate_once(i, assets, sounds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch generate crane videos")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--no-audio", action="store_true", help="Disable sound track generation")
    args = parser.parse_args()
    main(args.count, not args.no_audio)
