# Dev Log

## 2026-04-03 — Initial implementation

Implemented core engine (Phase 1-3 from spec):
- `_terminal.py` — curses init/teardown, color pair management, raw I/O
- `_screen.py` — grid buffer with diffing, all drawing primitives (put, text, rect, fill, hline, vline), emoji width detection, color/style helper
- `_input.py` — non-blocking key reading, key constants (arrows, escape, enter, space, etc.)
- `_timing.py` — FPS regulation via sleep, delta-time tracking
- `_functions.py` — function-based API (module-level state, all primitives)
- `_game.py` — Game class with context manager, same primitives as methods
- `__init__.py` — clean exports of both APIs, all constants

Examples: bouncing_ball.py (function API), snake.py (function API), pong.py (class API).

## 2026-04-11 — Gamepad support

- New `_gamepad.py` module exposing `GamepadState`, backed by the `inputs`
  library (optional extra: `uv sync --extra gamepad`).
- Public API mirrors the keyboard: `button_down()`, `button_pressed()`,
  `buttons_down()` for digital buttons, plus `stick(which)` returning
  `(x, y)` in `[-1, 1]` and `trigger(which)` returning `[0, 1]`. Dead-zone
  default 0.15.
- Button constants: `BUTTON_A/B/X/Y`, `BUTTON_L1/R1/L3/R3`,
  `BUTTON_START/SELECT/HOME`, `DPAD_UP/DOWN/LEFT/RIGHT`, plus
  `STICK_LEFT/RIGHT` and `TRIGGER_LEFT/RIGHT` aliases.
- Internally maps evdev-style codes (`BTN_SOUTH`, `BTN_TL`, `ABS_X`, `ABS_Z`,
  `ABS_HAT0X`, etc.) to the public constants. D-pad is supported both as a
  hat axis and as discrete buttons (different controllers report it
  differently).
- Polling happens in a daemon thread; `update_keys()` on `Game` also calls
  `GamepadState.update()` to snapshot edge-triggered presses per frame.
- Hot-plug supported: the poll loop retries after `get_gamepad()` raises
  so a controller connected mid-game just starts working.
- Opt-in via `gamepad=True` on `start()` / `Game.__init__()`. When off (the
  default), all gamepad queries return safe defaults so games can call them
  unconditionally without crashing.
- 18 new unit tests covering button edge/held, dpad as hat-axis and as
  discrete buttons, stick normalization + dead-zone, triggers, and unknown
  codes. Tests bypass `__init__` so the `inputs` library is not required
  to run them.
- New example: `kbsmash/examples/gamepad_demo.py`.

## 2026-04-11 — Flicker-free rendering

- `Terminal` now exposes a 3-phase frame API: `begin_frame()` / `queue_char()` /
  `end_frame()`. `ScreenBuffer.draw()` uses it to batch the entire frame into
  one stdout write.
- Each frame is wrapped in DEC private mode 2026 (Synchronized Output) escapes
  so supporting terminals (iTerm2, kitty, WezTerm, Windows Terminal, modern
  xterm and VS Code/JetBrains terminals) apply the update atomically — no more
  visible row-by-row paint sweep on large diffs.
- Within a frame, the emitter tracks `(last_fg, last_bg)` and `(last_x, last_y)`
  and skips redundant `SGR` color escapes and `CUP` cursor positioning escapes.
  A full-screen solid fill now emits one color switch instead of one per cell.
- New optional `vsync=True` parameter on `start()` / `Game.__init__()` — escape
  hatch for unusual terminals. Defaults to on.
- `write_char()` kept as a thin wrapper for single-char writes so exception
  paths and tests still work.
- Tests: new `FakeTerminal` tracks `frames_begun`/`frames_ended`; added one
  test asserting `draw()` makes exactly one frame begin/end.

## 2026-04-07 — keys_down() and pressed-set API

- Added `keys_down()` to both `KeyState` and `PynputKeyState`, returning a
  `frozenset` of currently-firing keys. Exposed through `Game.keys_down()` and
  the function API. Makes diagonal movement and multi-key checks one call
  instead of a chain of `key_down()` tests.

## 2026-04-06 — Windows support fixes

- Enable Windows console VT processing via `SetConsoleMode` +
  `ENABLE_VIRTUAL_TERMINAL_PROCESSING` when curses is up, so our direct ANSI
  escapes are interpreted instead of written literally or buffered until exit.
- Explicitly enter/leave the alt screen with `\x1b[?1049h` / `\x1b[?1049l` —
  `windows-curses` doesn't reliably switch it for us.
- Install a custom `sys.excepthook` in `Terminal.start()` that tears down the
  terminal before printing the traceback. Previously, tracebacks from unhandled
  exceptions in the function-API path rendered into the still-active alt screen
  (invisible) or into a still-raw console (garbled).
- Added `windows-curses` as a `sys_platform == 'win32'` conditional dependency.

## 2026-04-05 — Test suite, refactor, README tutorial

- Added pytest suite: 70 tests covering screen primitives, input state machine,
  timing, terminal color codes, and a package API smoke test. `FakeTerminal`
  test double in `tests/conftest.py`. pytest is a dev-group dependency only.
- Refactored `_functions.py` to delegate to a single module-level `Game`
  instance instead of duplicating Terminal/Screen/Timer/KeyState wiring.
- README: added a 10-section tutorial progressing from "hello world" through
  held-key input, colors, a dodge game, emoji mode, class-based API, and a
  start-screen/game-over structure tip.
- `text()` now works in emoji mode by packing two ASCII chars per emoji cell
  (so scores and labels render alongside emoji sprites).

## 2026-04-04 — ANSI rendering, direct stdout writes

- Replaced curses-based character output with direct ANSI escape sequences.
  Root cause: macOS ncurses 6.0 (2015) has outdated wcwidth tables that
  mis-measure many emoji (🟢🟡⚽⚾⬜✅❎🟠), breaking cursor tracking so that
  subsequent writes land in the wrong columns. curses is now only used for
  terminal setup (alt screen, raw mode, keypad) and input (`getch`, `nodelay`).
- `Terminal.write_char()` now emits
  `\x1b[Y;XH\x1b[FG;BGm{char}\x1b[0m` directly to stdout.
- Dropped `curses.init_pair` color pair management (~30 lines).
- Added `leaveok(True)` so curses stops fighting our cursor positioning.

## 2026-04-04 — Video modes, held-key input, pynput backend

- Added ASCII/emoji video modes (`mode="ascii"` | `"emoji"`). Each has uniform
  cell width; mixing widths is an error. Emoji mode maps each game cell to 2
  terminal columns. Removed continuation-cell complexity.
- Added held-key tracking: `update_keys()` + `key_down()` + `key_pressed()`
  alongside the simple `get_key()`. Configurable `debounce` for rate-limiting.
- Added conflicting-key cancellation (UP/DOWN, LEFT/RIGHT cancel each other)
  to keep direction changes instant despite long hold windows.
- Added optional pynput backend (`input="pynput"`) using OS-level key event
  hooks. Gives real key-down/key-up events, no OS repeat delay, no phantom
  taps. Requires `uv sync --extra pynput`. Default remains curses (stdlib only).
- Added pyproject.toml (hatchling build backend, pynput as optional extra).
