"""Video assembly utilities using MoviePy."""

import os
from tempfile import NamedTemporaryFile
from typing import List

import numpy as np
from moviepy.editor import ImageSequenceClip, AudioFileClip

from .. import config


def export_video(frames: List[np.ndarray], audio, output_path: str, fps: int = config.FPS) -> None:
    """Export the given frames and audio segment to an MP4 file."""
    clip = ImageSequenceClip(frames, fps=fps)
    with NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        audio.export(temp_wav.name, format="wav")
        clip = clip.set_audio(AudioFileClip(temp_wav.name))
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    os.unlink(temp_wav.name)
