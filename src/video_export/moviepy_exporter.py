"""Video assembly utilities using MoviePy."""

import os
from tempfile import NamedTemporaryFile
from typing import List

import numpy as np
try:
    # MoviePy <2.x provides the ``editor`` module. In later versions the
    # classes are exposed at the package root, so we fall back gracefully.
    from moviepy.editor import ImageSequenceClip, AudioFileClip
except ModuleNotFoundError:  # pragma: no cover - legacy compatibility
    import moviepy
    ImageSequenceClip = moviepy.ImageSequenceClip
    AudioFileClip = moviepy.AudioFileClip

from .. import config


def export_video(frames: List[np.ndarray], audio, output_path: str, fps: int = config.FPS) -> None:
    """Export the given frames and audio segment to an MP4 file."""
    clip = ImageSequenceClip(frames, fps=fps)
    with NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        audio.export(temp_wav.name, format="wav")
        audio_clip = AudioFileClip(temp_wav.name)
        try:
            try:
                clip = clip.set_audio(audio_clip)
            except AttributeError:  # MoviePy >=2.1 uses ``with_audio``
                clip = clip.with_audio(audio_clip)  # pragma: no cover
            clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        finally:
            # Explicitly free MoviePy resources before returning
            audio_clip.close()
            clip.close()
    os.unlink(temp_wav.name)
