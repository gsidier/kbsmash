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
        if self._mode == EMOJI:
            # In emoji mode each cell is 2 terminal columns wide, so we pack
            # two ASCII chars per cell. This lets text() still be used for
            # scores, labels, etc. in emoji games.
            for ch in string:
                if _is_wide(ch):
                    raise ValueError(
                        f"text() in emoji mode expects narrow (ASCII) "
                        f"characters — got wide char {ch!r}"
                    )
            if len(string) % 2 == 1:
                string = string + " "
            for i in range(0, len(string), 2):
                cx = x + i // 2
                if cx < 0 or cx >= self._width or y < 0 or y >= self._height:
                    continue
                self._buf[y][cx] = (string[i:i + 2], fg, bg)
        else:
            for i, ch in enumerate(string):
                self.put(x + i, y, ch, fg, bg)

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
                tx = self._tx(x)
                if self._mode == EMOJI and char == " ":
                    self._terminal.queue_char(tx, y, "  ", fg, bg)
                else:
                    self._terminal.queue_char(tx, y, char, fg, bg)
        self._terminal.end_frame()
        self._prev = [row[:] for row in self._buf]
