"""Batch generation of crane challenge videos."""

import argparse
import os
import random
import math
from collections import deque
from typing import Optional


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
from ..renderer import pygame_renderer, overlays, vfx
from ..audio import sound_manager
from ..video_export import moviepy_exporter


def find_connected_tower(resting: list[pymunk.Body], spawn_y: float, space) -> list[pymunk.Body]:
    """Return all blocks forming the actual tower reaching ``spawn_y``."""
    margin = 5
    connected: set[pymunk.Body] = set()
    queue: deque[pymunk.Body] = deque()

    for body in resting:
        bb = list(body.shapes)[0].bb
        if bb.top >= spawn_y:
            connected.add(body)
            queue.append(body)

    def _adjacent(a: pymunk.Body, b: pymunk.Body) -> bool:
        abb = list(a.shapes)[0].bb
        bbb = list(b.shapes)[0].bb
        return (
            abb.left < bbb.right + margin
            and abb.right > bbb.left - margin
            and abb.bottom < bbb.top + margin
            and abb.top > bbb.bottom - margin
        )

    while queue:
        current = queue.popleft()
        for other in resting:
            if other in connected:
                continue
            if _adjacent(current, other):
                connected.add(other)
                queue.append(other)

    return list(connected)


def generate_once(
    index: int,
    assets,
    sounds=None,
    seed: Optional[int] = None,
    perfect_stack: bool | None = None,
) -> None:
    """Generate a single video with random parameters."""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    space = space_builder.init_space()
    screen = pygame.Surface((config.WIDTH, config.HEIGHT))
    frames = []
    events = []
    rng = random.Random(seed)
    sky = rng.choice(config.SKY_OPTIONS)
    crane_x = config.WIDTH // 2
    if perfect_stack is None:
        perfect_stack = config.PERFECT_STACK
    # Oscillation parameters for the crane movement
    if perfect_stack:
        amplitude = 0.0
        frequency = 0.0
        phase = 0.0
    else:
        amplitude = rng.uniform(*config.CRANE_OSC_AMPLITUDE_RANGE)
        frequency = rng.uniform(*config.CRANE_OSC_FREQUENCY_RANGE)
        phase = rng.uniform(*config.CRANE_OSC_PHASE_RANGE)
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

    impact_fx: dict[pymunk.Body, float] = {}
    confetti_particles: list[vfx.ConfettiParticle] = []
    glow_time = 0.0
    glow_blocks: list[pymunk.Body] = []

    # Camera effect state
    shake_time = 0.0
    zoom_time = 0.0
    cam_phase = rng.uniform(0, 2 * math.pi)
    cam_axis = rng.choice(["x", "y"])
    cam_amp = rng.uniform(*config.CAMERA_OSC_AMPLITUDE_RANGE)
    cam_freq = rng.uniform(*config.CAMERA_OSC_FREQUENCY_RANGE)
    cam_t = 0.0

    # Next time (in seconds) a new block should be dropped
    next_drop_time = 0.0

    IMPACT_THRESHOLD = 300

    def log_impact(arbiter, space_, data):
        """Record an impact if the collision is strong enough."""
        nonlocal shake_time
        impulse = getattr(arbiter, "total_impulse", None)
        strength = impulse.length if impulse is not None else 0

        # Avoid spamming impact sounds when bodies remain in contact
        first_contact = getattr(arbiter, "is_first_contact", False)
        if first_contact and strength >= IMPACT_THRESHOLD:
            events.append((sim_time["t"], "impact"))
            for shape in arbiter.shapes:
                body = shape.body
                if body.body_type == pymunk.Body.DYNAMIC:
                    impact_fx[body] = config.IMPACT_FLASH_DURATION
            shake_time = config.CAMERA_SHAKE_DURATION
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
    preview_variant = choose_block_variant(config.BLOCK_VARIANTS, variant_history)
    # Time until which the preview should remain hidden after a drop
    preview_hidden_until = 0.0
    unsupported: dict[pymunk.Body, float] = {}
    falling_blocks: set[pymunk.Body] = set()
    first_block: pymunk.Body | None = None

    # Render a short intro sequence before starting the simulation
    for _ in range(config.INTRO_DURATION * config.FPS):
        pygame_renderer.render_frame(screen, space, assets, crane_x, sky, preview_variant)
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
            if perfect_stack:
                drop_x = crane_x
                initial_vx = 0.0
            else:
                drop_x = crane_x + random.randint(*config.DROP_VARIATION_RANGE)
                crane_vx = amplitude * frequency * math.cos(frequency * t + phase)
                initial_vx = crane_vx * config.DROP_HORIZONTAL_SPEED_FACTOR
            new_block = block.create_block(
                space,
                drop_x,
                config.HEIGHT - config.CRANE_DROP_HEIGHT,
                preview_variant,
                initial_velocity=(initial_vx, 0.0),
            )
            if first_block is None:
                first_block = new_block
            delay = config.BLOCK_DROP_INTERVAL + random.uniform(
                -config.BLOCK_DROP_JITTER,
                config.BLOCK_DROP_JITTER,
            )
            delay = max(0.5, delay)
            next_drop_time = t + delay
            preview_hidden_until = t + config.PREVIEW_HIDE_DURATION
            preview_variant = choose_block_variant(
                config.BLOCK_VARIANTS,
                variant_history,
            )
        # Advance the simulation before checking the tower height so that newly
        # spawned blocks do not immediately trigger a win. ``sim_time`` is
        # updated with the intro offset so audio timestamps remain consistent
        # with the rendered frames.
        sim_time["t"] = config.INTRO_DURATION + (i + 1) / config.FPS
        space.step(1 / config.FPS)
        space_builder.apply_bug_forces(space)
        space_builder.apply_adhesion_forces(space)

        for body in list(impact_fx.keys()):
            impact_fx[body] -= 1 / config.FPS
            if impact_fx[body] <= 0:
                impact_fx.pop(body)

        vfx.update_confetti(confetti_particles, 1 / config.FPS)
        if glow_time > 0:
            glow_time -= 1 / config.FPS

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
            return bb.bottom <= config.FLOOR_Y + 5

        def _is_tilted(body):
            angle = abs(body.angle % math.pi)
            if angle > math.pi / 2:
                angle = math.pi - angle
            return angle > config.BLOCK_SIDE_ANGLE

        for b in resting:
            protected_first = (
                b is first_block
                and _is_on_floor(b)
                and not _has_block_on_top(b)
            )
            if (
                protected_first
                or (not _is_on_floor(b) and not _is_tilted(b))
                or _has_block_on_top(b)
            ):
                unsupported[b] = 0.0
                continue

            unsupported[b] = unsupported.get(b, 0.0) + 1 / config.FPS
            if (
                config.BLOCK_DESPAWN_ENABLED
                and unsupported[b] >= config.BLOCK_DESPAWN_DELAY
            ):
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
                    confetti_particles.extend(
                        vfx.spawn_confetti(
                            config.CONFETTI_COUNT,
                            config.HEIGHT - spawn_y,
                        )
                    )
                    glow_time = config.GLOW_DURATION
                    glow_blocks = find_connected_tower(resting, spawn_y, space)
                    zoom_time = config.VICTORY_ZOOM_DURATION
                    break
        crane_x = (
            config.WIDTH // 2
            + amplitude * math.sin(frequency * t + phase)
        )
        crane_x = max(
            config.CRANE_MOVEMENT_BOUNDS,
            min(config.WIDTH - config.CRANE_MOVEMENT_BOUNDS, crane_x),
        )
        show_preview = preview_variant if t >= preview_hidden_until else None
        effects = {
            b: (config.IMPACT_FLASH_COLOR, int(config.IMPACT_FLASH_ALPHA * (v / config.IMPACT_FLASH_DURATION)))
            for b, v in impact_fx.items()
        }
        if glow_time > 0:
            intensity = int(config.GLOW_ALPHA * glow_time / config.GLOW_DURATION)
            for b in glow_blocks:
                if b in space.bodies:
                    effects[b] = (config.GLOW_COLOR, intensity)
        pygame_renderer.render_frame(
            screen,
            space,
            assets,
            crane_x,
            sky,
            show_preview,
            block_effects=effects,
            confetti=confetti_particles,
        )
        overlays.draw_timer(screen, remaining)

        offset_x = offset_y = 0.0
        zoom = 1.0
        if config.CAMERA_EFFECTS_ENABLED:
            base = cam_amp * math.sin(cam_freq * cam_t + cam_phase)
            offset_x = base if cam_axis == "x" else 0.0
            offset_y = base if cam_axis == "y" else 0.0
            if shake_time > 0:
                strength = shake_time / config.CAMERA_SHAKE_DURATION
                offset_x += rng.uniform(-1, 1) * config.CAMERA_SHAKE_INTENSITY * strength
                offset_y += rng.uniform(-1, 1) * config.CAMERA_SHAKE_INTENSITY * strength
                shake_time -= 1 / config.FPS
            if zoom_time > 0:
                progress = 1 - zoom_time / config.VICTORY_ZOOM_DURATION
                eased = progress * progress * (3 - 2 * progress)
                zoom = 1 + config.VICTORY_ZOOM_FACTOR * eased
                zoom_time -= 1 / config.FPS
            cam_t += 1 / config.FPS

        transformed = pygame_renderer.apply_camera(screen, (offset_x, offset_y), zoom)
        arr = pygame.surfarray.array3d(transformed)
        arr = np.transpose(arr, (1, 0, 2))
        frames.append(arr)
    if state is None:
        state = "fail"
        final_remaining = 0
        events.append((sim_time["t"], "fail"))

    for _ in range(config.FPS * 2):
        sim_time["t"] += 1 / config.FPS
        space.step(1 / config.FPS)
        space_builder.apply_bug_forces(space)
        space_builder.apply_adhesion_forces(space)
        for body in list(impact_fx.keys()):
            impact_fx[body] -= 1 / config.FPS
            if impact_fx[body] <= 0:
                impact_fx.pop(body)

        vfx.update_confetti(confetti_particles, 1 / config.FPS)
        if glow_time > 0:
            glow_time -= 1 / config.FPS

        effects = {
            b: (config.IMPACT_FLASH_COLOR, int(config.IMPACT_FLASH_ALPHA * (v / config.IMPACT_FLASH_DURATION)))
            for b, v in impact_fx.items()
        }
        if glow_time > 0:
            intensity = int(config.GLOW_ALPHA * glow_time / config.GLOW_DURATION)
            for b in glow_blocks:
                if b in space.bodies:
                    effects[b] = (config.GLOW_COLOR, intensity)
        arr = pygame_renderer.render_frame(
            screen,
            space,
            assets,
            crane_x,
            sky,
            None,
            block_effects=effects,
            confetti=confetti_particles,
        )
        show_remaining = 0 if final_remaining is None else final_remaining
        overlays.draw_timer(screen, show_remaining)
        if state == "victory":
            overlays.draw_victory(screen)
        else:
            overlays.draw_fail(screen)
        offset_x = offset_y = 0.0
        zoom = 1.0
        if config.CAMERA_EFFECTS_ENABLED:
            base = cam_amp * math.sin(cam_freq * cam_t + cam_phase)
            offset_x = base if cam_axis == "x" else 0.0
            offset_y = base if cam_axis == "y" else 0.0
            if shake_time > 0:
                strength = shake_time / config.CAMERA_SHAKE_DURATION
                offset_x += rng.uniform(-1, 1) * config.CAMERA_SHAKE_INTENSITY * strength
                offset_y += rng.uniform(-1, 1) * config.CAMERA_SHAKE_INTENSITY * strength
                shake_time -= 1 / config.FPS
            if zoom_time > 0:
                progress = 1 - zoom_time / config.VICTORY_ZOOM_DURATION
                eased = progress * progress * (3 - 2 * progress)
                zoom = 1 + config.VICTORY_ZOOM_FACTOR * eased
                zoom_time -= 1 / config.FPS
            cam_t += 1 / config.FPS

        transformed = pygame_renderer.apply_camera(screen, (offset_x, offset_y), zoom)
        arr = pygame.surfarray.array3d(transformed)
        arr = np.transpose(arr, (1, 0, 2))
        frames.append(arr)

    duration = config.INTRO_DURATION + config.TIME_LIMIT + 2
    if sounds:
        audio = sound_manager.mix_tracks(duration, events, sounds)
    else:
        audio = AudioSegment.silent(duration=duration * 1000)
    output = os.path.join(config.OUTPUT_DIR, f"run_{index}.mp4")
    moviepy_exporter.export_video(frames, audio, output)


def main(
    count: int,
    with_audio: bool = True,
    seed: Optional[int] = None,
    perfect_stack: bool | None = None,
) -> None:
    assets = pygame_renderer.load_assets()
    sounds = sound_manager.load_sounds() if with_audio else None
    for i in range(count):
        run_seed = None if seed is None else seed + i
        generate_once(i, assets, sounds, seed=run_seed, perfect_stack=perfect_stack)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch generate crane videos")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument(
        "--no-audio", action="store_true", help="Disable sound track generation"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Base random seed for reproducible runs",
    )
    parser.add_argument(
        "--perfect-stack",
        action="store_true",
        help="Empile automatiquement les blocs sans mouvement de grue",
    )
    args = parser.parse_args()
    main(
        args.count,
        not args.no_audio,
        seed=args.seed,
        perfect_stack=args.perfect_stack,
    )
