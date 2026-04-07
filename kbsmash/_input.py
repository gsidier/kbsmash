import curses
import time

# --- Key constants ---
KEY_UP = "KEY_UP"
KEY_DOWN = "KEY_DOWN"
KEY_LEFT = "KEY_LEFT"
KEY_RIGHT = "KEY_RIGHT"
KEY_ENTER = "KEY_ENTER"
KEY_ESCAPE = "KEY_ESCAPE"
KEY_SPACE = "KEY_SPACE"
KEY_BACKSPACE = "KEY_BACKSPACE"
KEY_TAB = "KEY_TAB"

_CURSES_KEY_MAP = {
    curses.KEY_UP: KEY_UP,
    curses.KEY_DOWN: KEY_DOWN,
    curses.KEY_LEFT: KEY_LEFT,
    curses.KEY_RIGHT: KEY_RIGHT,
    curses.KEY_ENTER: KEY_ENTER,
    curses.KEY_BACKSPACE: KEY_BACKSPACE,
    10: KEY_ENTER,
    13: KEY_ENTER,
    27: KEY_ESCAPE,
    32: KEY_SPACE,
    9: KEY_TAB,
    127: KEY_BACKSPACE,
}

# Keys that cancel each other (pressing one releases the others)
_DEFAULT_CONFLICTS = [
    {KEY_UP, KEY_DOWN},
    {KEY_LEFT, KEY_RIGHT},
]


def translate_key(raw):
    if raw == -1:
        return None
    if raw in _CURSES_KEY_MAP:
        return _CURSES_KEY_MAP[raw]
    if 0 < raw < 256:
        return chr(raw)
    return None


class KeyState:
    """Tracks which keys are held down using engine-controlled repeat.

    Curses has no key-release events. Instead of relying on OS key repeat
    (which has a ~500ms initial delay), the engine generates its own
    repeats from the moment a key is first pressed.

    A key is considered held until `hold_time` seconds pass without any
    OS event for that key. The default (0.6s) is deliberately longer than
    the OS initial key-repeat delay (~500ms) so that holding a key
    produces continuous movement from the first frame — no pause.

    To keep taps precise despite the long hold window, conflicting keys
    cancel each other: pressing DOWN immediately releases UP, and vice
    versa. This means a direction change is instant, and a quick
    tap-then-tap-opposite won't accumulate phantom movement.

    Parameters:
        hold_time: seconds to keep a key "held" after last OS event (default 0.6)
        debounce:  minimum seconds between key_down() fires (default 0, every frame)
    """

    def __init__(self, hold_time=0.6, debounce=0):
        self._hold_time = hold_time
        self._debounce = debounce
        self._last_seen = {}      # key -> timestamp of last OS event
        self._press_start = {}    # key -> timestamp of initial press
        self._last_fired = {}     # key -> timestamp of last key_down() fire
        self._just_pressed = set()
        self._was_down = set()
        self._firing = set()
        self._conflicts = {}      # key -> set of keys it cancels
        for group in _DEFAULT_CONFLICTS:
            for k in group:
                self._conflicts[k] = group - {k}

    def update(self, terminal):
        """Drain all pending input. Call once per frame."""
        self._just_pressed.clear()
        new_keys = set()

        while True:
            raw = terminal.get_key_raw()
            if raw == -1:
                break
            key = translate_key(raw)
            if key is not None:
                new_keys.add(key)
                self._last_seen[key] = time.monotonic()
                if key not in self._was_down:
                    self._just_pressed.add(key)
                    self._press_start[key] = time.monotonic()

        # Cancel conflicting keys
        for key in new_keys:
            for victim in self._conflicts.get(key, ()):
                self._last_seen.pop(victim, None)
                self._press_start.pop(victim, None)
                self._last_fired.pop(victim, None)

        now = time.monotonic()

        # A key is "down" if we've seen an OS event recently enough
        self._was_down = {
            k for k, t in self._last_seen.items()
            if (now - t) < self._hold_time
        }

        # Decide which down keys "fire" this frame
        self._firing.clear()
        for key in self._was_down:
            if self._debounce <= 0:
                self._firing.add(key)
            else:
                last = self._last_fired.get(key)
                if last is None or (now - last) >= self._debounce:
                    self._firing.add(key)
                    self._last_fired[key] = now

        # Clean up released keys
        for key in list(self._last_fired):
            if key not in self._was_down:
                del self._last_fired[key]
        for key in list(self._press_start):
            if key not in self._was_down:
                del self._press_start[key]

    def is_down(self, key):
        """True if key is held and fires this frame (respects debounce)."""
        return key in self._firing

    def just_pressed(self, key):
        """True if the key was first pressed this frame (edge-triggered)."""
        return key in self._just_pressed

    def keys_down(self):
        """Return the set of keys that are firing this frame."""
        return frozenset(self._firing)
