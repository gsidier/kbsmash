from kbsmash._terminal import WHITE, BLACK
from kbsmash._game import Game

_game = None


def _require_started():
    if _game is None:
        raise RuntimeError("Call start() before using kbsmash functions")


def start(width=40, height=20, fps=30, title="", mode="emoji", debounce=0, input="pynput", vsync=True, gamepad=False):
    global _game
    _game = Game(width, height, fps, title, mode, debounce, input, vsync, gamepad)
    _game.start()


def stop():
    global _game
    if _game is not None:
        _game.stop()
    _game = None


def clear(char=" "):
    _require_started()
    _game.clear(char)


def put(x, y, char, fg=WHITE, bg=BLACK, style=None):
    _require_started()
    _game.put(x, y, char, fg, bg, style)


def text(x, y, string, fg=WHITE, bg=BLACK, style=None):
    _require_started()
    _game.text(x, y, string, fg, bg, style)


def rect(x, y, w, h, char=None, fg=WHITE, bg=BLACK):
    _require_started()
    _game.rect(x, y, w, h, char, fg, bg)


def fill(x, y, w, h, char=" ", fg=WHITE, bg=BLACK):
    _require_started()
    _game.fill(x, y, w, h, char, fg, bg)


def hline(x, y, length, char=None, fg=WHITE, bg=BLACK):
    _require_started()
    _game.hline(x, y, length, char, fg, bg)


def vline(x, y, length, char=None, fg=WHITE, bg=BLACK):
    _require_started()
    _game.vline(x, y, length, char, fg, bg)


def draw():
    _require_started()
    _game.draw()


def get_key():
    _require_started()
    return _game.get_key()


def update_keys():
    _require_started()
    _game.update_keys()


def key_down(key):
    _require_started()
    return _game.key_down(key)


def key_pressed(key):
    _require_started()
    return _game.key_pressed(key)


def keys_down():
    _require_started()
    return _game.keys_down()


def button_down(button):
    _require_started()
    return _game.button_down(button)


def button_pressed(button):
    _require_started()
    return _game.button_pressed(button)


def buttons_down():
    _require_started()
    return _game.buttons_down()


def stick(which):
    _require_started()
    return _game.stick(which)


def trigger(which):
    _require_started()
    return _game.trigger(which)


def screen_width():
    _require_started()
    return _game.width


def screen_height():
    _require_started()
    return _game.height


def dt():
    _require_started()
    return _game.dt()
