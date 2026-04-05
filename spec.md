# kbsmash — Terminal Arcade Engine for Kids

A minimal Python engine for building terminal-based arcade games, designed to teach programming.

---

## Design Principles

1. **Minimal boilerplate** — a working game in under 20 lines
2. **No hidden magic** — the student writes the game loop, controls the flow
3. **Two API flavors** — function-based (beginners) → class-based (intermediate)
4. **Modern terminals** — color, emoji "sprites", box-drawing characters
5. **Zero dependencies** — stdlib only (`curses`, `sys`, `os`, `time`, `enum`)

---

## Architecture Overview

```
┌─────────────────────────────────────┐
│           Student's Code            │
│  (game loop, logic, draw calls)     │
├──────────┬──────────┬───────────────┤
│  Input   │ Drawing  │  Timing       │
│  Module  │ Module   │  Module       │
├──────────┴──────────┴───────────────┤
│        Terminal Backend             │
│  (curses wrapper, color, Unicode)   │
└─────────────────────────────────────┘
```

**Four internal modules, one package:**

| Module | Responsibility |
|--------|---------------|
| `terminal` | curses init/teardown, raw character output, color pair management |
| `screen` | the grid buffer, coordinate system, drawing primitives |
| `input` | non-blocking key reading, key constants |
| `timing` | FPS regulation, delta-time tracking |

The student never imports these directly. They use either the function API or the class API, both of which are thin wrappers.

---

## Video Modes

Two mutually exclusive modes — no mixing of character widths:

### ASCII Mode (`mode="ascii"`, default)

- Each game cell = 1 terminal column
- Only single-width characters allowed (letters, digits, box-drawing, etc.)
- Emoji raises `ValueError`
- `rect()`, `hline()`, `vline()` default to box-drawing characters

```python
start(40, 20, mode="ascii")
put(5, 3, "@")       # ok
put(5, 3, "🍎")     # ValueError
```

### Emoji Mode (`mode="emoji"`)

- Each game cell = 2 terminal columns (grouped in pairs)
- Only double-width characters allowed (emoji, CJK, etc.)
- Single-width ASCII raises `ValueError`
- `rect()`, `hline()`, `vline()` require a `char` argument (no box-drawing default)
- Coordinates address the double-wide cells, so a width of 15 uses 30 terminal columns

```python
start(15, 20, mode="emoji")
put(5, 3, "🍎")     # ok
put(5, 3, "@")       # ValueError
rect(0, 0, 15, 20, char="⬜")  # ok
rect(0, 0, 15, 20)              # ValueError (no default in emoji mode)
```

Spaces are the one exception — allowed in both modes for `clear()` and `fill()`.

`text()` is also allowed in emoji mode as a special case: it packs two ASCII
chars per emoji cell, so scores and labels still work. Odd-length strings are
padded with a trailing space. Passing a wide char to `text()` in emoji mode
raises `ValueError`.

---

## Coordinate System

- Origin `(0, 0)` is **top-left**
- `x` increases rightward, `y` increases downward
- All coordinates are integers
- Out-of-bounds writes are silently clipped (no crash, no wrap)
- In emoji mode, each coordinate unit spans 2 terminal columns

---

## Color System

### Named Colors (16 standard terminal colors)

```python
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW,
BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE
```

These are importable constants. Colors are specified as foreground/background pairs:

```python
put(5, 3, "@", fg=RED, bg=BLACK)
```

- `fg` defaults to `WHITE`
- `bg` defaults to `BLACK`

### Color Convenience

A `color(fg, bg=None)` function returns a reusable style handle to avoid repeating colors:

```python
danger = color(RED, BRIGHT_WHITE)
put(5, 3, "!", style=danger)
```

---

## Input System

Two input styles are available:

### Simple: `get_key()`

```python
key = get_key()  # returns a key constant, or None if no key is pressed
```

- **Non-blocking** — returns `None` immediately if nothing is pressed
- Returns key constants for special keys, single characters for printable keys
- Reads one key per call — fine for turn-based or direction-setting games (snake, sokoban)

### Held keys: `update_keys()` + `key_down()` / `key_pressed()`

For games where the player holds a key for continuous movement (pong, platformers):

```python
update_keys()              # drain input buffer, update key state — call once per frame
key_down(KEY_UP)           # True if the key is held AND fires this frame
key_pressed(KEY_ESCAPE)    # True only on the first frame the key is seen (edge-triggered)
```

Terminals don't report key-release events. Two input backends are available:

**curses** (default, stdlib only):
Approximates "held" by considering a key down for `hold_time` seconds (default 0.6s)
after last OS event. Long enough to bridge the OS initial key-repeat delay (~500ms)
so held keys respond immediately. Conflicting keys (UP/DOWN, LEFT/RIGHT) cancel
each other on press, which keeps taps precise. Trade-off: a genuinely held-then-released
key can still produce some residual movement after release (up to hold_time).

**pynput** (optional, real key state):
Uses OS-level key event hooks — real key-down and key-up events. No repeat delay,
no phantom taps, accurate release detection.
- Install: `uv sync --extra pynput` (or `pip install pynput`)
- macOS: grant Accessibility permission on first run
- Captures keys globally (listens system-wide, not just the terminal)
- Select with `input="pynput"` on `start()` / `Game.__init__()`

```python
start(60, 24, fps=30, input="pynput", debounce=0.03)
```

#### Debounce

The `debounce` parameter (seconds) controls how often `key_down()` fires while
a key is held. Set it on `start()` or `Game.__init__()`:

```python
start(60, 24, fps=30, debounce=0.05)  # key_down fires at most once per 50ms
```

- `debounce=0` (default) — fires every frame (no rate limiting)
- `debounce=0.05` — fires immediately on press, then once every 50ms while held
- The initial delay equals the repeat interval (no extra wait before first repeat)

**Don't mix** `get_key()` and `update_keys()` in the same loop — both drain the input
buffer, so one will steal events from the other.

### Key Constants

```python
KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
KEY_ENTER, KEY_ESCAPE, KEY_SPACE, KEY_BACKSPACE, KEY_TAB
KEY_A through KEY_Z  # uppercase constants, match both 'a' and 'A'
```

Printable characters are returned as single-character strings (`"a"`, `"1"`, `" "`), so students can also compare directly:

```python
key = get_key()
if key == KEY_UP:
    player_y -= 1
elif key == "q":
    running = False
```

---

## Drawing Primitives

All drawing writes to an off-screen buffer. Nothing appears until `draw()` is called.

### Core

| Function | Description |
|----------|-------------|
| `clear()` | Fill the buffer with spaces (or a given character) |
| `put(x, y, char, fg=WHITE, bg=BLACK, style=None)` | Place a single character or emoji at (x, y) |
| `draw()` | Flush the buffer to the terminal |

### Text

| Function | Description |
|----------|-------------|
| `text(x, y, string, fg=WHITE, bg=BLACK, style=None)` | Write a horizontal string starting at (x, y) |

### Shapes

| Function | Description |
|----------|-------------|
| `rect(x, y, w, h, char=None, fg=WHITE, bg=BLACK)` | Draw a rectangle outline using box-drawing chars. If `char` is given, use that character instead. |
| `fill(x, y, w, h, char=" ", fg=WHITE, bg=BLACK)` | Fill a rectangular area with a character |
| `hline(x, y, length, char="─", fg=WHITE, bg=BLACK)` | Horizontal line |
| `vline(x, y, length, char="│", fg=WHITE, bg=BLACK)` | Vertical line |

### Information

| Function | Description |
|----------|-------------|
| `screen_width()` | Returns the configured width |
| `screen_height()` | Returns the configured height |

---

## Timing

FPS control is handled by the engine. The student specifies desired FPS at init time:

```python
start(40, 20, fps=30)    # 30 frames per second
start(40, 20, fps=None)  # unlimited — run as fast as possible
start(40, 20)             # default: 30 fps
```

The engine sleeps as needed after `draw()` to maintain the target frame rate. This keeps the game loop simple — students don't manage `time.sleep()` themselves.

An optional helper:

```python
dt()  # seconds since last draw() call, as a float — useful for smooth movement
```

---

## API Flavor 1: Function-Based

For beginners who haven't learned classes yet. All state is global/module-level.

### Lifecycle

```python
start(width, height, fps=30, title="")  # initialize terminal, set screen size
stop()                                    # restore terminal, cleanup
```

`start()` enters alternate screen mode, hides cursor, enables raw input.
`stop()` reverses all of that. Also installed as an `atexit` handler so a crash doesn't brick the terminal.

### Full Example — Bouncing Ball

```python
from kbsmash import *

start(40, 20, fps=30, title="Bouncing Ball")

x, y = 20, 10
dx, dy = 1, 1
running = True

while running:
    # input
    key = get_key()
    if key == KEY_ESCAPE:
        running = False

    # update
    x += dx
    y += dy
    if x <= 0 or x >= screen_width() - 1:
        dx = -dx
    if y <= 0 or y >= screen_height() - 1:
        dy = -dy

    # draw
    clear()
    rect(0, 0, screen_width(), screen_height())
    put(x, y, "🔴")
    draw()

stop()
```

### Full Example — Snake (function-based)

```python
from kbsmash import *
from random import randint

start(30, 20, fps=8, title="Snake")

snake = [(15, 10)]
direction = (1, 0)
food = (randint(1, 28), randint(1, 18))
score = 0
alive = True

while alive:
    key = get_key()
    if key == KEY_UP:    direction = (0, -1)
    elif key == KEY_DOWN:  direction = (0, 1)
    elif key == KEY_LEFT:  direction = (-1, 0)
    elif key == KEY_RIGHT: direction = (1, 0)
    elif key == KEY_ESCAPE: break

    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    if (head[0] < 0 or head[0] >= 30 or
        head[1] < 0 or head[1] >= 20 or
        head in snake):
        alive = False
        continue

    snake.insert(0, head)
    if head == food:
        score += 1
        food = (randint(1, 28), randint(1, 18))
    else:
        snake.pop()

    clear()
    rect(0, 0, 30, 20)
    put(food[0], food[1], "🍎")
    for i, seg in enumerate(snake):
        put(seg[0], seg[1], "🟢" if i == 0 else "🟩")
    text(1, 0, f" Score: {score} ")
    draw()

stop()
```

---

## API Flavor 2: Class-Based

For students ready to organize code into methods. The class provides structure but the student still writes the game loop explicitly.

### Base Class

```python
class Game:
    def __init__(self, width=40, height=20, fps=30, title=""):
        """Store config. Does NOT start the terminal yet."""

    def start(self):
        """Enter terminal mode. Call at the beginning."""

    def stop(self):
        """Exit terminal mode. Call at the end."""

    # --- Drawing (same as function API, but as methods) ---
    def clear(self): ...
    def put(self, x, y, char, fg=WHITE, bg=BLACK, style=None): ...
    def text(self, x, y, string, fg=WHITE, bg=BLACK, style=None): ...
    def rect(self, x, y, w, h, char=None, fg=WHITE, bg=BLACK): ...
    def fill(self, x, y, w, h, char=" ", fg=WHITE, bg=BLACK): ...
    def hline(self, x, y, length, char="─", fg=WHITE, bg=BLACK): ...
    def vline(self, x, y, length, char="│", fg=WHITE, bg=BLACK): ...
    def draw(self): ...

    # --- Input ---
    def get_key(self): ...

    # --- Info ---
    @property
    def width(self): ...
    @property
    def height(self): ...
    def dt(self): ...
```

### Context Manager Support

```python
game = Game(40, 20, fps=30)
with game:
    # game loop here ...
```

`__enter__` calls `start()`, `__exit__` calls `stop()`. This is the recommended pattern — it guarantees cleanup even on exceptions.

### Full Example — Pong (class-based)

```python
from kbsmash import Game, KEY_UP, KEY_DOWN, KEY_ESCAPE, WHITE, YELLOW

class Pong(Game):
    def __init__(self):
        super().__init__(60, 24, fps=30, title="Pong")
        self.paddle_y = 10
        self.ball_x, self.ball_y = 30, 12
        self.ball_dx, self.ball_dy = 1, 1
        self.score = 0

pong = Pong()

with pong:
    while True:
        key = pong.get_key()
        if key == KEY_ESCAPE:
            break
        if key == KEY_UP and pong.paddle_y > 0:
            pong.paddle_y -= 1
        if key == KEY_DOWN and pong.paddle_y < pong.height - 5:
            pong.paddle_y += 1

        pong.ball_x += pong.ball_dx
        pong.ball_y += pong.ball_dy
        if pong.ball_y <= 0 or pong.ball_y >= pong.height - 1:
            pong.ball_dy *= -1
        if pong.ball_x >= pong.width - 2:
            pong.ball_dx *= -1
        if (pong.ball_x == 1 and
            pong.paddle_y <= pong.ball_y <= pong.paddle_y + 4):
            pong.ball_dx *= -1
            pong.score += 1
        if pong.ball_x <= 0:
            break  # game over

        pong.clear()
        pong.rect(0, 0, pong.width, pong.height)
        for i in range(5):
            pong.put(1, pong.paddle_y + i, "█", fg=WHITE)
        pong.put(pong.ball_x, pong.ball_y, "⚾")
        pong.text(pong.width // 2 - 4, 0, f" {pong.score} ", fg=YELLOW)
        pong.draw()
```

---

## Terminal Backend Details

### Initialization (`start()`)

1. Enter curses mode (`curses.wrapper` pattern or manual `initscr`)
2. Switch to alternate screen buffer
3. Hide cursor
4. Enable keypad mode (arrow keys as single reads)
5. Set `nodelay` (non-blocking input)
6. Initialize color pairs
7. Register `atexit` cleanup

### Screen Buffer

- Internal 2D array of `(char, fg, bg)` tuples
- `clear()` resets every cell to `(" ", WHITE, BLACK)`
- `draw()` diffs the buffer against the previous frame and only writes changed cells (for performance)
- In ASCII mode, each buffer cell maps 1:1 to a terminal column
- In emoji mode, each buffer cell maps to 2 terminal columns — `draw()` multiplies x by 2, and cleared cells write two spaces

### Cleanup (`stop()`)

1. Restore cursor
2. Leave alternate screen buffer
3. End curses mode
4. Print any pending error messages to stderr

---

## Package Structure

```
kbsmash/
├── __init__.py          # public API — exports both flavors
├── _terminal.py         # curses wrapper, color pairs, raw I/O
├── _screen.py           # grid buffer, drawing primitives
├── _input.py            # key reading, key constants
├── _timing.py           # FPS regulator, delta time
├── _game.py             # Game base class (class-based API)
├── _functions.py         # function-based API (module-level state)
└── examples/
    ├── bouncing_ball.py
    ├── snake.py
    ├── pong.py
    └── sokoban.py
```

`__init__.py` exports everything:

```python
# function API
from kbsmash._functions import start, stop, clear, put, text, rect, fill, hline, vline, draw, get_key, screen_width, screen_height, dt

# class API
from kbsmash._game import Game

# constants
from kbsmash._input import (KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT,
                             KEY_ENTER, KEY_ESCAPE, KEY_SPACE, ...)
from kbsmash._screen import color
from kbsmash._terminal import (BLACK, RED, GREEN, YELLOW, BLUE,
                                MAGENTA, CYAN, WHITE, ...)
```

---

## Scope Boundaries — What This Engine Does NOT Do

- **No sprites/images** — characters and emoji only
- **No sound** — terminal has no audio API
- **No mouse input** — keyboard only (keeps input handling simple)
- **No networking** — single-player, single-machine
- **No scene management** — one screen, managed by the student
- **No physics** — students write their own collision/movement logic
- **No entity/component system** — students manage their own data structures

These are intentional constraints. The engine handles the terminal so the student can focus on game logic.

---

## Implementation Order

### Phase 1: Core (minimum viable engine)
1. `_terminal.py` — curses init/teardown, alternate screen, color pairs
2. `_screen.py` — grid buffer, `clear()`, `put()`, `draw()` with diffing
3. `_input.py` — `get_key()`, key constants
4. `_timing.py` — FPS sleep, `dt()`
5. `_functions.py` — wire up function-based API
6. `__init__.py` — exports

**Milestone:** bouncing ball example works.

### Phase 2: Drawing Primitives
7. `text()`, `rect()`, `fill()`, `hline()`, `vline()`
8. `color()` style handles
9. Emoji double-width handling

**Milestone:** snake example works.

### Phase 3: Class API
10. `_game.py` — `Game` class with context manager
11. Port examples to both API flavors

**Milestone:** pong example works with class API.

### Phase 4: Polish
12. Robust cleanup (atexit, signal handlers)
13. Helpful error messages (e.g., "did you forget to call start()?")
14. Edge cases: terminal resize, very small terminals
15. Examples: sokoban, simple roguelike

---

## Testing Strategy

- **Manual play-testing** — run each example, verify rendering and input
- **Unit tests** — test the screen buffer logic without curses (mock terminal)
  - `put()` writes to correct buffer positions
  - `clear()` resets buffer
  - Out-of-bounds writes are clipped
  - Emoji double-width reservation
  - Color pair management
- **Integration tests** — capture curses output in a virtual terminal (if feasible; optional)
