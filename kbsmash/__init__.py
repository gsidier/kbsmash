# Function-based API
from kbsmash._functions import (
    start, stop, clear, put, text, rect, fill, hline, vline,
    draw, get_key, update_keys, key_down, key_pressed, keys_down,
    screen_width, screen_height, dt,
)

# Class-based API
from kbsmash._game import Game

# Key constants
from kbsmash._input import (
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT,
    KEY_ENTER, KEY_ESCAPE, KEY_SPACE, KEY_BACKSPACE, KEY_TAB,
)

# Color constants
from kbsmash._terminal import (
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE,
    BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW,
    BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE,
)

# Video modes
from kbsmash._screen import ASCII, EMOJI

# Color style helper
from kbsmash._screen import color
