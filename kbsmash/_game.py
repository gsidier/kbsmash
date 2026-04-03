from kbsmash._terminal import Terminal, WHITE, BLACK
from kbsmash._screen import ScreenBuffer
from kbsmash._input import translate_key
from kbsmash._timing import Timer


class Game:
    def __init__(self, width=40, height=20, fps=30, title="", mode="ascii"):
        self._width = width
        self._height = height
        self._fps = fps
        self._title = title
        self._mode = mode
        self._terminal = None
        self._screen = None
        self._timer = None

    def start(self):
        self._terminal = Terminal()
        self._terminal.start(title=self._title)
        self._screen = ScreenBuffer(self._width, self._height, self._terminal, mode=self._mode)
        self._timer = Timer(self._fps)

    def stop(self):
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

    # --- Info ---

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def dt(self):
        return self._timer.dt
