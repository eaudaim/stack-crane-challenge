"""Manage sound effects and music using pydub."""

from pathlib import Path
from typing import Dict, List, Tuple
import random

from pydub import AudioSegment

from .. import config


def load_sounds() -> Dict[str, AudioSegment]:
    """Load all WAV files from the assets directory."""
    sounds = {}
    for wav in Path(config.ASSET_PATHS["sounds"]).glob("*.wav"):
        sounds[wav.stem] = AudioSegment.from_wav(wav)
    return sounds


def mix_tracks(duration: int, events: List[Tuple[float, str]], sounds: Dict[str, AudioSegment]) -> AudioSegment:
    """Create a mixed soundtrack using the provided events."""
    base = sounds.get("bpm_loop", AudioSegment.silent(duration=duration * 1000))
    loops = int((duration * 1000) / len(base)) + 1
    backing = base * loops
    track = backing[: duration * 1000]
    impact_variants = [n for n in sounds if n.startswith("impact")]
    prev_impact: str | None = None
    for ts, name in events:
        segment = None
        if name == "impact" and impact_variants:
            options = impact_variants.copy()
            if prev_impact in options and len(options) > 1:
                options.remove(prev_impact)
            choice = random.choice(options)
            prev_impact = choice
            segment = sounds[choice]
        elif name in sounds:
            segment = sounds[name]
        if segment is not None:
            track = track.overlay(segment, position=int(ts * 1000))
    return track
