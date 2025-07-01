import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import src.config as config

def test_basic_constants():
    assert config.WIDTH > 0
    assert config.HEIGHT > 0
    assert isinstance(config.SKY_OPTIONS, list)
    assert config.BLOCK_DROP_INTERVAL > 0
    assert 0 <= config.BLOCK_DROP_JITTER < config.BLOCK_DROP_INTERVAL
    assert config.BLOCK_DESPAWN_DELAY > 0
    assert config.BLOCK_SIDE_ANGLE > 0
