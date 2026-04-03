import atexit
import curses
import sys

# --- Color constants ---
BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7
BRIGHT_BLACK = 8
BRIGHT_RED = 9
BRIGHT_GREEN = 10
BRIGHT_YELLOW = 11
BRIGHT_BLUE = 12
BRIGHT_MAGENTA = 13
BRIGHT_CYAN = 14
BRIGHT_WHITE = 15

_CURSES_COLORS = {
    BLACK: curses.COLOR_BLACK,
    RED: curses.COLOR_RED,
    GREEN: curses.COLOR_GREEN,
    YELLOW: curses.COLOR_YELLOW,
    BLUE: curses.COLOR_BLUE,
    MAGENTA: curses.COLOR_MAGENTA,
    CYAN: curses.COLOR_CYAN,
    WHITE: curses.COLOR_WHITE,
}


class Terminal:
    def __init__(self):
        self._scr = None
        self._color_pairs = {}
        self._next_pair = 1
        self._started = False

    @property
    def started(self):
        return self._started

    def start(self, title=""):
        if self._started:
            return
        self._scr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self._scr.keypad(True)
        self._scr.nodelay(True)
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
        self._started = True
        atexit.register(self.stop)
        if title:
            sys.stdout.write(f"\033]0;{title}\007")
            sys.stdout.flush()

    def stop(self):
        if not self._started:
            return
        self._started = False
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        self._scr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def get_color_pair(self, fg, bg):
        key = (fg, bg)
        if key in self._color_pairs:
            return self._color_pairs[key]

        curses_fg = _CURSES_COLORS.get(fg % 8, curses.COLOR_WHITE)
        curses_bg = _CURSES_COLORS.get(bg % 8, curses.COLOR_BLACK)

        pair_num = self._next_pair
        self._next_pair += 1
        try:
            curses.init_pair(pair_num, curses_fg, curses_bg)
        except curses.error:
            pair_num = 0

        attr = curses.color_pair(pair_num)
        if fg >= 8:
            attr |= curses.A_BOLD
        self._color_pairs[key] = attr
        return attr

    def write_char(self, x, y, char, fg=WHITE, bg=BLACK):
        if not self._started:
            return
        attr = self.get_color_pair(fg, bg)
        try:
            self._scr.addstr(y, x, char, attr)
        except curses.error:
            pass

    def refresh(self):
        if self._started:
            self._scr.refresh()

    def get_key_raw(self):
        if not self._started:
            return -1
        try:
            return self._scr.getch()
        except curses.error:
            return -1
