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
    victory_ts = next((ts for ts, name in events if name == "victory"), None)

    track = AudioSegment.silent(duration=duration * 1000)

    base = sounds.get("bpm_loop", AudioSegment.silent(duration=duration * 1000))
    if config.SOUND_ENABLED.get("bpm_loop", True):
        loops = int((duration * 1000) / len(base)) + 1
        backing = base * loops
        end = duration * 1000 if victory_ts is None else int(victory_ts * 1000)
        track = track.overlay(backing[:end], position=0)

    impact_variants = [n for n in sounds if n.startswith("impact")]
    prev_impact: str | None = None
    for ts, name in events:
        to_play: List[str] = []
        if name == "impact" and impact_variants:
            options = impact_variants.copy()
            if prev_impact in options and len(options) > 1:
                options.remove(prev_impact)
            choice = random.choice(options)
            prev_impact = choice
            to_play.append(choice)
        elif name == "victory":
            to_play.extend(["victory", "win_music", "applause"])
        elif name in sounds:
            to_play.append(name)

        for sound_name in to_play:
            if sound_name in sounds and config.SOUND_ENABLED.get(sound_name, True):
                segment = sounds[sound_name]
                track = track.overlay(segment, position=int(ts * 1000))
    return track
