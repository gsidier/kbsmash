from kbsmash._terminal import Terminal, WHITE, BLACK
from kbsmash._screen import ScreenBuffer
from kbsmash._input import translate_key, KeyState
from kbsmash._timing import Timer


class Game:
    def __init__(self, width=40, height=20, fps=30, title="", mode="emoji", debounce=0, input="pynput"):
        self._width = width
        self._height = height
        self._fps = fps
        self._title = title
        self._mode = mode
        self._debounce = debounce
        self._input = input
        self._terminal = None
        self._screen = None
        self._timer = None
        self._keys = None

    def start(self):
        self._terminal = Terminal()
        self._terminal.start(title=self._title)
        self._screen = ScreenBuffer(self._width, self._height, self._terminal, mode=self._mode)
        self._timer = Timer(self._fps)
        if self._input == "pynput":
            from kbsmash._pynput_input import PynputKeyState
            self._keys = PynputKeyState(debounce=self._debounce)
        elif self._input == "curses":
            self._keys = KeyState(debounce=self._debounce)
        else:
            raise ValueError(f"input must be 'curses' or 'pynput', got {self._input!r}")

    def stop(self):
        if self._keys is not None and hasattr(self._keys, "stop"):
            self._keys.stop()
        if self._terminal:
            self._terminal.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    # --- Drawing ---

    def clear(self, char=" "):
        self._screen.clear(char)

    def put(self, x, y, char, fg=WHITE, bg=BLACK, style=None):
        self._screen.put(x, y, char, fg, bg, style)

    def text(self, x, y, string, fg=WHITE, bg=BLACK, style=None):
        self._screen.text(x, y, string, fg, bg, style)

    def rect(self, x, y, w, h, char=None, fg=WHITE, bg=BLACK):
        self._screen.rect(x, y, w, h, char, fg, bg)

    def fill(self, x, y, w, h, char=" ", fg=WHITE, bg=BLACK):
        self._screen.fill(x, y, w, h, char, fg, bg)

    def hline(self, x, y, length, char=None, fg=WHITE, bg=BLACK):
        self._screen.hline(x, y, length, char, fg, bg)

    def vline(self, x, y, length, char=None, fg=WHITE, bg=BLACK):
        self._screen.vline(x, y, length, char, fg, bg)

    def draw(self):
        self._screen.draw()
        self._timer.wait()

    # --- Input ---

    def get_key(self):
        raw = self._terminal.get_key_raw()
        return translate_key(raw)

    def update_keys(self):
        self._keys.update(self._terminal)

    def key_down(self, key):
        return self._keys.is_down(key)

    def key_pressed(self, key):
        return self._keys.just_pressed(key)

    def keys_down(self):
        return self._keys.keys_down()

    # --- Info ---

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def dt(self):
        return self._timer.dt
