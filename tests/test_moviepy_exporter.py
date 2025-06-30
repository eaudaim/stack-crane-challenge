import sys
from pathlib import Path
import numpy as np
from pydub import AudioSegment

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.video_export import moviepy_exporter


def test_export_video(tmp_path):
    frames = [np.zeros((1920, 1080, 3), dtype=np.uint8) for _ in range(2)]
    audio = AudioSegment.silent(duration=100)
    output = tmp_path / "out.mp4"
    moviepy_exporter.export_video(frames, audio, str(output))
    assert output.exists()
