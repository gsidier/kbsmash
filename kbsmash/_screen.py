import unicodedata

from kbsmash._terminal import WHITE, BLACK

# Sentinel for "this cell is the right half of a wide character"
_CONTINUATION = object()

# Box-drawing characters
BOX_TOP_LEFT = "┌"
BOX_TOP_RIGHT = "┐"
BOX_BOTTOM_LEFT = "└"
BOX_BOTTOM_RIGHT = "┘"
BOX_HORIZONTAL = "─"
BOX_VERTICAL = "│"


class Style:
    __slots__ = ("fg", "bg")

    def __init__(self, fg, bg=None):
        self.fg = fg
        self.bg = bg if bg is not None else BLACK


def color(fg, bg=None):
    return Style(fg, bg)


def _char_width(ch):
    if len(ch) > 1:
        return 2
    w = unicodedata.east_asian_width(ch)
    return 2 if w in ("W", "F") else 1


class ScreenBuffer:
    def __init__(self, width, height, terminal):
        self._width = width
        self._height = height
        self._terminal = terminal
        self._buf = None
        self._prev = None
        self.clear()
        self._prev = [row[:] for row in self._buf]

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def clear(self, char=" "):
        self._buf = [
            [(char, WHITE, BLACK) for _ in range(self._width)]
            for _ in range(self._height)
        ]

    def put(self, x, y, char, fg=WHITE, bg=BLACK, style=None):
        if style:
            fg = style.fg
            bg = style.bg
        if y < 0 or y >= self._height or x < 0 or x >= self._width:
            return
        w = _char_width(char)
        # If we're overwriting the right half of a wide char, break the
        # left half so it doesn't render as a corrupt glyph
        if self._buf[y][x][0] is _CONTINUATION and x > 0:
            self._buf[y][x - 1] = (" ", WHITE, BLACK)
        self._buf[y][x] = (char, fg, bg)
        if w == 2 and x + 1 < self._width:
            self._buf[y][x + 1] = (_CONTINUATION, fg, bg)

    def text(self, x, y, string, fg=WHITE, bg=BLACK, style=None):
        if style:
            fg = style.fg
            bg = style.bg
        col = x
        for ch in string:
            if col >= self._width:
                break
            self.put(col, y, ch, fg, bg)
            col += _char_width(ch)

    def rect(self, x, y, w, h, char=None, fg=WHITE, bg=BLACK):
        if w < 2 or h < 2:
            return
        if char:
            self.hline(x, y, w, char, fg, bg)
            self.hline(x, y + h - 1, w, char, fg, bg)
            self.vline(x, y, h, char, fg, bg)
            self.vline(x + w - 1, y, h, char, fg, bg)
        else:
            self.hline(x + 1, y, w - 2, BOX_HORIZONTAL, fg, bg)
            self.hline(x + 1, y + h - 1, w - 2, BOX_HORIZONTAL, fg, bg)
            self.vline(x, y + 1, h - 2, BOX_VERTICAL, fg, bg)
            self.vline(x + w - 1, y + 1, h - 2, BOX_VERTICAL, fg, bg)
            self.put(x, y, BOX_TOP_LEFT, fg, bg)
            self.put(x + w - 1, y, BOX_TOP_RIGHT, fg, bg)
            self.put(x, y + h - 1, BOX_BOTTOM_LEFT, fg, bg)
            self.put(x + w - 1, y + h - 1, BOX_BOTTOM_RIGHT, fg, bg)

    def fill(self, x, y, w, h, char=" ", fg=WHITE, bg=BLACK):
        for row in range(y, y + h):
            for col in range(x, x + w):
                self.put(col, row, char, fg, bg)

    def hline(self, x, y, length, char=BOX_HORIZONTAL, fg=WHITE, bg=BLACK):
        for i in range(length):
            self.put(x + i, y, char, fg, bg)

    def vline(self, x, y, length, char=BOX_VERTICAL, fg=WHITE, bg=BLACK):
        for i in range(length):
            self.put(x, y + i, char, fg, bg)

    def draw(self):
        for y in range(self._height):
            for x in range(self._width):
                cell = self._buf[y][x]
                if cell[0] is _CONTINUATION:
                    continue

                prev = self._prev[y][x] if self._prev else None
                if prev and cell == prev:
                    continue

                char, fg, bg = cell

                # If the previous cell here was wide, clear its right half
                # so the terminal doesn't display a ghost half-emoji
                if prev and prev[0] is not _CONTINUATION:
                    prev_w = _char_width(prev[0])
                    cur_w = _char_width(char)
                    if prev_w == 2 and cur_w == 1 and x + 1 < self._width:
                        self._terminal.write_char(x + 1, y, " ", fg, bg)

                self._terminal.write_char(x, y, char, fg, bg)

        self._terminal.refresh()
        self._prev = [row[:] for row in self._buf]
