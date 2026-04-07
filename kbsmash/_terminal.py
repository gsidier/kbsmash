import atexit
import curses
import locale
import sys
import traceback

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


def _enable_windows_vt():
    """Enable ANSI escape sequence processing on the Windows console.

    By default, the Windows console writes ANSI bytes literally. We need
    ENABLE_VIRTUAL_TERMINAL_PROCESSING on stdout and ENABLE_VIRTUAL_TERMINAL_INPUT
    on stdin for our direct-ANSI rendering to work. No-op on other platforms.
    """
    if sys.platform != "win32":
        return
    import ctypes

    kernel32 = ctypes.windll.kernel32
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    STD_OUTPUT_HANDLE = -11

    h_out = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    mode = ctypes.c_ulong()
    if kernel32.GetConsoleMode(h_out, ctypes.byref(mode)):
        kernel32.SetConsoleMode(
            h_out, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        )


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
        # On Windows, curses/windows-curses may leave the console without
        # VT processing enabled, so our ANSI escapes would be written
        # literally (or buffered and only flushed on exit). Enable it now,
        # after curses has finished setting up the console.
        _enable_windows_vt()
        self._started = True
        atexit.register(self.stop)
        # Install an excepthook that restores the terminal before printing
        # the traceback. Without this, the traceback renders into the alt
        # screen (invisible) or into a still-raw console (garbled).
        self._prev_excepthook = sys.excepthook
        sys.excepthook = self._excepthook
        # Enter the alt screen and clear it. curses does not reliably
        # switch to the alt screen on Windows, so we do it explicitly.
        sys.stdout.write("\x1b[?1049h\x1b[2J\x1b[H")
        if title:
            sys.stdout.write(f"\x1b]0;{title}\x07")
        sys.stdout.flush()

    def _excepthook(self, exc_type, exc_value, exc_tb):
        self.stop()
        traceback.print_exception(exc_type, exc_value, exc_tb)

    def stop(self):
        if not self._started:
            return
        self._started = False
        # Restore the previous excepthook.
        if hasattr(self, "_prev_excepthook"):
            sys.excepthook = self._prev_excepthook
        # Reset SGR attributes and leave the alt screen we entered in start().
        sys.stdout.write("\x1b[0m\x1b[?1049l")
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
