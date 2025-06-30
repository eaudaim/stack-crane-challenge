"""Global configuration constants for Stack Crane Challenge."""

import os

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 60  # seconds

BLOCK_COUNT_RANGE = (10, 20)  # number of floors per video
GRUE_SPEED_RANGE = (150, 300)  # pixels per second

# Available color palettes for overlays or effects
PALETTES = {
    "default": {
        "text": (255, 255, 255),
        "shadow": (0, 0, 0),
    }
}

# Sky backgrounds available in assets/sky
SKY_OPTIONS = [
    "skyline_day.png",
    "skyline_night.png",
]

ASSET_PATHS = {
    "sky": os.path.join("assets", "sky"),
    "crane": os.path.join("assets", "crane"),
    "block": os.path.join("assets", "block"),
    "sounds": os.path.join("assets", "sounds"),
}

OUTPUT_DIR = "output"
