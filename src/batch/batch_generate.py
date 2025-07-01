"""Batch generation of crane challenge videos."""

import argparse
import os
import random
import math
from collections import deque


def choose_block_variant(variants, history: deque) -> str:
    """Return a variant avoiding long consecutive repeats."""
    if len(variants) <= 1:
        choice = variants[0]
    else:
        # Exclude variant if it already appears twice consecutively
        banned = None
        if len(history) >= 2 and history[-1] == history[-2]:
            banned = history[-1]
        available = [v for v in variants if v != banned] if banned else variants
        choice = random.choice(available)
    history.append(choice)
    if len(history) > 2:
        history.popleft()
    return choice

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
    sky = random.choice(config.SKY_OPTIONS)
    crane_x = config.WIDTH // 2
    crane_speed = random.randint(*config.GRUE_SPEED_RANGE)
    crane_dir = 1
    spawn_y = config.HEIGHT - config.CRANE_DROP_HEIGHT
    state = None  # "victory" or "fail"
    # Track the current simulation time so collision callbacks can timestamp
    # impact events accurately. The value will be updated each frame before
    # stepping the space.
    # ``sim_time`` tracks the absolute time in the final clip. This starts at
    # ``INTRO_DURATION`` so that all logged audio events line up with the video
    # frames once the intro sequence has played.
    sim_time = {"t": float(config.INTRO_DURATION)}
    prev_second = config.TIME_LIMIT + 1
    final_remaining = None

    # Next time (in seconds) a new block should be dropped
    next_drop_time = 0.0

    IMPACT_THRESHOLD = 300

    def log_impact(arbiter, space_, data):
        """Record an impact if the collision is strong enough."""
        impulse = getattr(arbiter, "total_impulse", None)
        strength = impulse.length if impulse is not None else 0

        # Avoid spamming impact sounds when bodies remain in contact
        first_contact = getattr(arbiter, "is_first_contact", False)
        if first_contact and strength >= IMPACT_THRESHOLD:
            events.append((sim_time["t"], "impact"))
        return True

    if hasattr(space, "on_collision"):
        # Pymunk >= 7 uses the on_collision API instead of
        # add_default_collision_handler. Passing ``None`` for both
        # collision types registers a global handler.
        space.on_collision(post_solve=log_impact)
    else:  # pragma: no cover - legacy pymunk
        handler = space.add_default_collision_handler()
        handler.post_solve = log_impact

    variant_history: deque = deque(maxlen=2)
    unsupported: dict[pymunk.Body, float] = {}
    falling_blocks: set[pymunk.Body] = set()
    first_block: pymunk.Body | None = None

    # Render a short intro sequence before starting the simulation
    for _ in range(config.INTRO_DURATION * config.FPS):
        pygame_renderer.render_frame(screen, space, assets, crane_x, sky)
        overlays.draw_intro(screen)
        arr = pygame.surfarray.array3d(screen)
        arr = np.transpose(arr, (1, 0, 2))
        frames.append(arr)

    for i in range(config.TIME_LIMIT * config.FPS):
        t = i / config.FPS
        remaining = config.TIME_LIMIT - t
        secs = int(math.ceil(remaining))
        if secs < prev_second:
            if 0 < secs <= 5:
                # Offset the timer event by the intro duration so it matches
                # the absolute timestamp used for audio mixing.
                events.append((config.INTRO_DURATION + t, "timer"))
            prev_second = secs
        if state is None and t >= next_drop_time:
            drop_x = crane_x + random.randint(*config.DROP_VARIATION_RANGE)
            block_variant = choose_block_variant(
                config.BLOCK_VARIANTS, variant_history
            )
            new_block = block.create_block(
                space,
                drop_x,
                config.HEIGHT - config.CRANE_DROP_HEIGHT,
                block_variant,
            )
            if first_block is None:
                first_block = new_block
            delay = config.BLOCK_DROP_INTERVAL + random.uniform(
                -config.BLOCK_DROP_JITTER,
                config.BLOCK_DROP_JITTER,
            )
            delay = max(0.5, delay)
            next_drop_time = t + delay
        # Advance the simulation before checking the tower height so that newly
        # spawned blocks do not immediately trigger a win. ``sim_time`` is
        # updated with the intro offset so audio timestamps remain consistent
        # with the rendered frames.
        sim_time["t"] = config.INTRO_DURATION + (i + 1) / config.FPS
        space.step(1 / config.FPS)

        dynamic_bodies = [
            b
            for b in space.bodies
            if isinstance(b, pymunk.Body) and b.body_type == pymunk.Body.DYNAMIC
        ]
        resting = [b for b in dynamic_bodies if abs(b.velocity.y) < 1]

        def _has_block_on_top(body):
            bb = list(body.shapes)[0].bb
            for other in dynamic_bodies:
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
            return bb.bottom <= config.FLOOR_Y + 1

        def _is_tilted(body):
            angle = abs(body.angle % math.pi)
            if angle > math.pi / 2:
                angle = math.pi - angle
            return angle > config.BLOCK_SIDE_ANGLE

        for b in resting:
            if (
                b is first_block
                or (not _is_on_floor(b) and not _is_tilted(b))
                or _has_block_on_top(b)
            ):
                unsupported[b] = 0.0
                continue

            unsupported[b] = unsupported.get(b, 0.0) + 1 / config.FPS
            if unsupported[b] >= config.BLOCK_DESPAWN_DELAY:
                for s in b.shapes:
                    s.sensor = True
                b.velocity = (0, -300)
                falling_blocks.add(b)

        for b in list(falling_blocks):
            if b.position.y < -config.BLOCK_SIZE[1]:
                space.remove(b, *b.shapes)
                falling_blocks.remove(b)
                unsupported.pop(b, None)

        if state is None:
            if resting:
                top = max(b.position.y + config.BLOCK_SIZE[1] / 2 for b in resting)
                if top >= spawn_y:
                    state = "victory"
                    events.append((sim_time["t"], "victory"))
                    remaining_challenge = sim_time["t"] - config.INTRO_DURATION
                    final_remaining = max(0.0, config.TIME_LIMIT - remaining_challenge)
                    break
        crane_x += crane_dir * crane_speed / config.FPS
        if crane_x > config.WIDTH - config.CRANE_MOVEMENT_BOUNDS:
            crane_x = config.WIDTH - config.CRANE_MOVEMENT_BOUNDS
            crane_dir = -1
        elif crane_x < config.CRANE_MOVEMENT_BOUNDS:
            crane_x = config.CRANE_MOVEMENT_BOUNDS
            crane_dir = 1
        pygame_renderer.render_frame(screen, space, assets, crane_x, sky)
        overlays.draw_timer(screen, remaining)
        arr = pygame.surfarray.array3d(screen)
        arr = np.transpose(arr, (1, 0, 2))
        frames.append(arr)
    if state is None:
        state = "fail"
        final_remaining = 0
        events.append((sim_time["t"], "fail"))

    for _ in range(config.FPS * 2):
        sim_time["t"] += 1 / config.FPS
        space.step(1 / config.FPS)
        arr = pygame_renderer.render_frame(screen, space, assets, crane_x, sky)
        show_remaining = 0 if final_remaining is None else final_remaining
        overlays.draw_timer(screen, show_remaining)
        if state == "victory":
            overlays.draw_victory(screen)
        else:
            overlays.draw_fail(screen)
        arr = pygame.surfarray.array3d(screen)
        arr = np.transpose(arr, (1, 0, 2))
        frames.append(arr)

    duration = config.INTRO_DURATION + config.TIME_LIMIT + 2
    if sounds:
        audio = sound_manager.mix_tracks(duration, events, sounds)
    else:
        audio = AudioSegment.silent(duration=duration * 1000)
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
    parser.add_argument(
        "--no-audio", action="store_true", help="Disable sound track generation"
    )
    args = parser.parse_args()
    main(args.count, not args.no_audio)
