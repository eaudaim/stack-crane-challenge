"""Global configuration constants for Stack Crane Challenge."""

import os

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 60  # seconds

# Pixel dimensions of a block sprite and its corresponding physics body
BLOCK_SIZE = (200, 100)

# Number of blocks that may be dropped in a single video
BLOCK_COUNT_RANGE = (10, 20)

# Speed of the moving crane in pixels per second
GRUE_SPEED_RANGE = (50, 120)

# Height from the bottom of the screen where blocks are spawned
CRANE_DROP_HEIGHT = 150

# Horizontal margin used for crane movement limits
CRANE_MOVEMENT_BOUNDS = 200

# Random variation applied to the drop X position
DROP_VARIATION_RANGE = (-30, 30)

# Offset for the hook relative to the top of the crane bar
# The crane_bar asset contains a large transparent margin above the
# visible bar. To keep the hook 80px below the visible bar despite
# this margin, we compensate here (394px transparent head).
HOOK_Y_OFFSET = 474

# Vertical position of the crane bar itself. We shift it upward so the
# visible bar sits only a few pixels from the top of the window.
CRANE_BAR_Y = -389

# Delay between consecutive block drops in seconds
BLOCK_DROP_INTERVAL = 2

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
