import atexit
import curses
import locale
import sys

# Must be called before curses.initscr() so curses uses the system UTF-8
# encoding when rendering multi-byte characters (emoji, etc.)
locale.setlocale(locale.LC_ALL, "")

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


def _fg_code(color):
    # normal 0-7 -> 30-37, bright 8-15 -> 90-97
    if color >= 8:
        return 90 + (color - 8)
    return 30 + color


def _bg_code(color):
    if color >= 8:
        return 100 + (color - 8)
    return 40 + color


class Terminal:
    def __init__(self):
        self._scr = None
        self._started = False

    @property
    def started(self):
        return self._started

    def start(self, title=""):
        if self._started:
            return
        # Use curses only for terminal setup (alt screen, raw mode) and input.
        # All character output is done via direct ANSI escape sequences to
        # bypass ncurses' outdated wcwidth tables which mis-measure many
        # emoji on macOS and break cursor tracking.
        self._scr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self._scr.keypad(True)
        self._scr.nodelay(True)
        # Tell curses not to track the physical cursor — we position it
        # ourselves with ANSI escapes.
        self._scr.leaveok(True)
        self._started = True
        atexit.register(self.stop)
        # Clear the alt screen we just entered.
        sys.stdout.write("\x1b[2J")
        if title:
            sys.stdout.write(f"\x1b]0;{title}\x07")
        sys.stdout.flush()

    def stop(self):
        if not self._started:
            return
        self._started = False
        # Reset any lingering SGR attributes before leaving alt screen.
        sys.stdout.write("\x1b[0m")
        sys.stdout.flush()
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        self._scr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def write_char(self, x, y, char, fg=WHITE, bg=BLACK):
        if not self._started:
            return
        # ANSI cursor position is 1-indexed: ESC[row;colH
        sys.stdout.write(
            f"\x1b[{y + 1};{x + 1}H"
            f"\x1b[{_fg_code(fg)};{_bg_code(bg)}m"
            f"{char}"
            f"\x1b[0m"
        )

    def refresh(self):
        if self._started:
            sys.stdout.flush()

    def get_key_raw(self):
        if not self._started:
            return -1
        try:
            return self._scr.getch()
        except curses.error:
            return -1
