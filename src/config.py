"""Global configuration constants for Stack Crane Challenge."""

import os

WIDTH = 1080
HEIGHT = 1920
FPS = 30
# Duration of the initial intro screen shown before the simulation starts
INTRO_DURATION = 3  # seconds
# Number of seconds before the challenge ends. If the tower has not
# reached the required height after this duration, the run is a failure.
TIME_LIMIT = 30
# Total clip duration used when exporting the final video
DURATION = INTRO_DURATION + TIME_LIMIT + 2

# Pixel dimensions of a block sprite and its corresponding physics body
BLOCK_SIZE = (350, 150)


# Different textures that can be used for the falling blocks
BLOCK_VARIANTS = [
    "block.png",
    "block_variant1.png",
    "block_variant2.png",
]

# Number of blocks that may be dropped in a single video
BLOCK_COUNT_RANGE = (10, 20)

# Speed of the moving crane in pixels per second
GRUE_SPEED_RANGE = (80, 120)

# Height from the bottom of the screen where blocks are spawned
CRANE_DROP_HEIGHT = 580

# Horizontal margin used for crane movement limits
CRANE_MOVEMENT_BOUNDS = 340

# Random variation applied to the drop X position
DROP_VARIATION_RANGE = (-10, 10)

# Offset for the hook relative to the top of the crane bar
# The crane_bar asset contains a large transparent margin above the
# visible bar. To keep the hook 80px below the visible bar despite
# this margin, we compensate here (394px transparent head).
HOOK_Y_OFFSET = 400

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

# Text shown at the beginning of the video and its styling options
INTRO_TEXT = "PEUT-IL FINIR CETTE TOUR EN 60s ?"
INTRO_STYLE = {
    "font_size": 120,
    # Vertical position of the text. A value closer to 0 means higher on screen
    "y_pos": HEIGHT // 4,
    "shadow_offset": (4, 4),
    # Palette key used for text and shadow colors
    "palette": "default",
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
