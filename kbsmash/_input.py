import curses

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


def translate_key(raw):
    if raw == -1:
        return None
    if raw in _CURSES_KEY_MAP:
        return _CURSES_KEY_MAP[raw]
    if 0 < raw < 256:
        return chr(raw)
    return None
