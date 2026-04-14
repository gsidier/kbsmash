import unicodedata

from kbsmash._terminal import WHITE, BLACK

# Video modes
ASCII = "ascii"
EMOJI = "emoji"

# Box-drawing characters (ASCII mode only)
BOX_TOP_LEFT = "┌"
BOX_TOP_RIGHT = "┐"
BOX_BOTTOM_LEFT = "└"
BOX_BOTTOM_RIGHT = "┘"
BOX_HORIZONTAL = "─"
BOX_VERTICAL = "│"

# Continuation marker — placed in the cell after a wide char in ASCII mode
# so draw() knows to skip it (the wide char already covers that column).
_CONT = ""


class Style:
    __slots__ = ("fg", "bg")

    def __init__(self, fg, bg=None):
        self.fg = fg
        self.bg = bg if bg is not None else BLACK


def color(fg, bg=None):
    return Style(fg, bg)


def _is_wide(ch):
    if len(ch) > 1:
        return True
    return unicodedata.east_asian_width(ch) in ("W", "F")


def text_width(string, mode=ASCII):
    """Return the width of *string* in screen cells, rounded up.

    In emoji mode narrow chars count as 0.5 cells each (packed two per cell)
    and wide chars count as 1.  In ASCII mode narrow chars are 1 cell and
    wide chars are 2.
    """
    if mode == EMOJI:
        half = 0
        for ch in string:
            half += 2 if _is_wide(ch) else 1
        return -(-half // 2)  # ceil division
    else:
        w = 0
        for ch in string:
            w += 2 if _is_wide(ch) else 1
        return w


class ScreenBuffer:
    def __init__(self, width, height, terminal, mode=ASCII):
        if mode not in (ASCII, EMOJI):
            raise ValueError(f"mode must be 'ascii' or 'emoji', got {mode!r}")
        self._width = width
        self._height = height
        self._terminal = terminal
        self._mode = mode
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

    @property
    def mode(self):
        return self._mode

    def _check_char(self, char):
        if char == " ":
            return
        wide = _is_wide(char)
        if self._mode == ASCII and wide:
            raise ValueError(
                f"emoji {char!r} not allowed in ASCII mode — use mode='emoji'"
            )
        if self._mode == EMOJI and not wide:
            raise ValueError(
                f"narrow character {char!r} not allowed in emoji mode — use mode='ascii'"
            )

    def _tx(self, x):
        return x * 2 if self._mode == EMOJI else x

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
        self._check_char(char)
        self._buf[y][x] = (char, fg, bg)

    def text(self, x, y, string, fg=WHITE, bg=BLACK, style=None):
        if style:
            fg = style.fg
            bg = style.bg
        if y < 0 or y >= self._height:
            return
        if self._mode == EMOJI:
            # Walk the string: wide chars take one cell each, narrow chars
            # are packed two per cell (so scores/labels still fit alongside
            # emoji sprites).
            i = 0
            cx = x
            while i < len(string):
                if cx >= self._width:
                    break
                ch = string[i]
                if _is_wide(ch):
                    if cx >= 0:
                        self._buf[y][cx] = (ch, fg, bg)
                    cx += 1
                    i += 1
                else:
                    pair = ch
                    if i + 1 < len(string) and not _is_wide(string[i + 1]):
                        pair += string[i + 1]
                        i += 2
                    else:
                        pair += " "
                        i += 1
                    if cx >= 0:
                        self._buf[y][cx] = (pair, fg, bg)
                    cx += 1
        else:
            # Walk the string: narrow chars take 1 cell, wide chars take 2
            # (the second cell gets a continuation marker that draw() skips).
            cx = x
            for ch in string:
                if cx >= self._width:
                    break
                if _is_wide(ch):
                    if cx >= 0:
                        self._buf[y][cx] = (ch, fg, bg)
                    if cx + 1 >= 0 and cx + 1 < self._width:
                        self._buf[y][cx + 1] = (_CONT, fg, bg)
                    cx += 2
                else:
                    if cx >= 0:
                        self._buf[y][cx] = (ch, fg, bg)
                    cx += 1

    def rect(self, x, y, w, h, char=None, fg=WHITE, bg=BLACK):
        if w < 2 or h < 2:
            return
        if self._mode == EMOJI and char is None:
            raise ValueError(
                "rect() requires a char argument in emoji mode"
            )
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

    def hline(self, x, y, length, char=None, fg=WHITE, bg=BLACK):
        if char is None:
            if self._mode == EMOJI:
                raise ValueError(
                    "hline() requires a char argument in emoji mode"
                )
            char = BOX_HORIZONTAL
        for i in range(length):
            self.put(x + i, y, char, fg, bg)

    def vline(self, x, y, length, char=None, fg=WHITE, bg=BLACK):
        if char is None:
            if self._mode == EMOJI:
                raise ValueError(
                    "vline() requires a char argument in emoji mode"
                )
            char = BOX_VERTICAL
        for i in range(length):
            self.put(x, y + i, char, fg, bg)

    def draw(self):
        self._terminal.begin_frame()
        for y in range(self._height):
            for x in range(self._width):
                cell = self._buf[y][x]
                prev = self._prev[y][x] if self._prev else None
                if prev and cell == prev:
                    continue
                char, fg, bg = cell
                if char == _CONT:
                    continue
                tx = self._tx(x)
                if self._mode == EMOJI and char == " ":
                    self._terminal.queue_char(tx, y, "  ", fg, bg)
                else:
                    self._terminal.queue_char(tx, y, char, fg, bg)
        self._terminal.end_frame()
        self._prev = [row[:] for row in self._buf]
