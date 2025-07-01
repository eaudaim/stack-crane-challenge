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
DURATION = INTRO_DURATION + TIME_LIMIT + 3

# Pixel dimensions of a block sprite and its corresponding physics body
BLOCK_SIZE = (300, 250)

# Time a resting block without another block placed on top
# remains before disappearing through the floor (seconds)
BLOCK_DESPAWN_DELAY = 3

# Angle (in radians) beyond which a resting block is considered to be
# "on its side" and should be removed after ``BLOCK_DESPAWN_DELAY``
# if unsupported.
BLOCK_SIDE_ANGLE = 0.4

# Vertical position of the floor segment used in the physics space
FLOOR_Y = 10


# Different textures that can be used for the falling blocks
BLOCK_VARIANTS = [
    "block.png",
    "block_variant1.png",
    "block_variant2.png",
    "block_variant3.png",
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
# ``BLOCK_DROP_JITTER`` adds a small random variation to each delay.  This
# prevents the drops from feeling too mechanical without ever producing huge
# gaps or multiple blocks at the same time.
BLOCK_DROP_INTERVAL = 2
# Maximum random variation applied to the drop interval.  The actual delay will
# be ``BLOCK_DROP_INTERVAL`` plus or minus a value drawn from this range.
BLOCK_DROP_JITTER = 0.4

# Available color palettes for overlays or effects
# "timer" is identical to the countdown timer colors. Additional palettes can be
# used for styling the intro text with various looks.
PALETTES = {
    "default": {
        "text": (255, 255, 255),
        "shadow": (0, 0, 0),
    },
    # Same white text with black shadow as the timer
    "timer": {
        "text": (255, 255, 255),
        "shadow": (0, 0, 0),
    },
    # Green on black retro computer style
    "retro": {
        "text": (0, 255, 0),
        "shadow": (0, 0, 0),
    },
    # Magenta text with cyan shadow for a neon effect
    "neon": {
        "text": (255, 0, 255),
        "shadow": (0, 255, 255),
    },
    # Yellow text with dark blue shadow reminiscent of comic books
    "comic": {
        "text": (255, 255, 0),
        "shadow": (0, 0, 128),
    },
}

# Predefined intro styles combining fonts, colors and shadow offsets
INTRO_STYLES = {
    # Matches the countdown timer appearance
    "timer": {
        "font_name": None,  # default font
        "font_size": 120,
        "y_pos": HEIGHT // 4,
        "shadow_offset": (2, 2),
        "palette": "timer",
    },
    # A green retro terminal look
    "retro": {
        "font_name": "courier",
        "font_size": 100,
        "y_pos": HEIGHT // 4,
        "shadow_offset": (4, 4),
        "palette": "retro",
    },
    # Bright neon colors with a larger shadow
    "neon": {
        "font_name": "arial",
        "font_size": 110,
        "y_pos": HEIGHT // 4,
        "shadow_offset": (6, 6),
        "palette": "neon",
    },
    # Comic style using Comic Sans and contrasting shadow
    "comic": {
        "font_name": "comicsansms",
        "font_size": 120,
        "y_pos": HEIGHT // 4,
        "shadow_offset": (5, 5),
        "palette": "comic",
    },
}

# Text shown at the beginning of the video and its styling options
INTRO_TEXT = "TERMINE CETTE TOUR EN 60s"
INTRO_STYLE = {
    "font_size": 100,
    # Vertical position of the text. A value closer to 0 means higher on screen
    "y_pos": HEIGHT // 4,
    "shadow_offset": (4, 4),
    # Palette key used for text and shadow colors
    "palette": "neon",
}

# Sky backgrounds available in assets/sky
SKY_OPTIONS = [
    "skyline_day.png",
    "skyline_night.png",
    "skyline_dusk.png",
]

ASSET_PATHS = {
    "sky": os.path.join("assets", "sky"),
    "crane": os.path.join("assets", "crane"),
    "block": os.path.join("assets", "block"),
    "sounds": os.path.join("assets", "sounds"),
}

OUTPUT_DIR = "output"
