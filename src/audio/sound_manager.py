"""Manage sound effects and music using pydub."""

from pathlib import Path
from typing import Dict, List, Tuple

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
    for ts, name in events:
        if name in sounds:
            track = track.overlay(sounds[name], position=int(ts * 1000))
    return track
