from kbsmash._terminal import Terminal, WHITE, BLACK
from kbsmash._screen import ScreenBuffer, color, ASCII
from kbsmash._input import translate_key, KeyState
from kbsmash._timing import Timer

_terminal = None
_screen = None
_timer = None
_keys = None


def _require_started():
    if _terminal is None or not _terminal.started:
        raise RuntimeError("Call start() before using kbsmash functions")


def start(width=40, height=20, fps=30, title="", mode="ascii", debounce=0):
    global _terminal, _screen, _timer, _keys
    _terminal = Terminal()
    _terminal.start(title=title)
    _screen = ScreenBuffer(width, height, _terminal, mode=mode)
    _timer = Timer(fps)
    _keys = KeyState(debounce=debounce)


def stop():
    global _terminal, _screen, _timer, _keys
    if _terminal:
        _terminal.stop()
    _terminal = None
    _screen = None
    _timer = None
    _keys = None


def clear(char=" "):
    _require_started()
    _screen.clear(char)


def put(x, y, char, fg=WHITE, bg=BLACK, style=None):
    _require_started()
    _screen.put(x, y, char, fg, bg, style)


def text(x, y, string, fg=WHITE, bg=BLACK, style=None):
    _require_started()
    _screen.text(x, y, string, fg, bg, style)


def rect(x, y, w, h, char=None, fg=WHITE, bg=BLACK):
    _require_started()
    _screen.rect(x, y, w, h, char, fg, bg)


def fill(x, y, w, h, char=" ", fg=WHITE, bg=BLACK):
    _require_started()
    _screen.fill(x, y, w, h, char, fg, bg)


def hline(x, y, length, char=None, fg=WHITE, bg=BLACK):
    _require_started()
    _screen.hline(x, y, length, char, fg, bg)


def vline(x, y, length, char=None, fg=WHITE, bg=BLACK):
    _require_started()
    _screen.vline(x, y, length, char, fg, bg)


def draw():
    _require_started()
    _screen.draw()
    _timer.wait()


def get_key():
    _require_started()
    raw = _terminal.get_key_raw()
    return translate_key(raw)


def update_keys():
    _require_started()
    _keys.update(_terminal)


def key_down(key):
    _require_started()
    return _keys.is_down(key)


def key_pressed(key):
    _require_started()
    return _keys.just_pressed(key)


def screen_width():
    _require_started()
    return _screen.width


def screen_height():
    _require_started()
    return _screen.height


def dt():
    _require_started()
    return _timer.dt
