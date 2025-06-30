import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import src.config as config

def test_basic_constants():
    assert config.WIDTH > 0
    assert config.HEIGHT > 0
    assert isinstance(config.SKY_OPTIONS, list)
