# kbsmash

A minimal Python engine for building terminal arcade games — designed for educational purposes  .

Students write the game loop themselves; kbsmash handles the terminal, drawing, input, and timing.

## Install

```bash
uv init .
uv add 'git+https://github.com/gsidier/kbsmash.git'
```

## Quick example

```python
from kbsmash import *

start(40, 20, fps=30, title="Bouncing Ball")

x, y = 20, 10
dx, dy = 1, 1

while True:
    if get_key() == KEY_ESCAPE:
        break

    x += dx
    y += dy
    if x <= 0 or x >= screen_width() - 1: dx = -dx
    if y <= 0 or y >= screen_height() - 1: dy = -dy

    clear()
    rect(0, 0, screen_width(), screen_height())
    put(x, y, "O", fg=RED)
    draw()

stop()
```

## Features

- **Two API flavors** — function-based (global state, for beginners) and class-based (`Game` subclass, for intermediates)
- **Two video modes** — ASCII (single-width chars) or emoji (double-width, 2 terminal columns per cell)
- **Drawing primitives** — `put`, `text`, `rect`, `fill`, `hline`, `vline`
- **Colors** — 16 named colors with fg/bg, reusable `color()` styles
- **Input** — simple `get_key()` or held-key tracking with `update_keys()` + `key_down()` + `key_pressed()`
- **Input backends** — pynput for arcade-feel key handling (no OS repeat delay), or curses for portability
- **Gamepad support** — enabled by default, works with Xbox/PlayStation controllers via pygame
- **FPS regulation** — fixed frame rate or unlimited, with `dt()` for smooth movement
- **Flicker-free rendering** — frames are batched into a single write and wrapped in DEC mode 2026 (Synchronized Output) so supporting terminals apply each frame atomically

## Examples

- `kbsmash/examples/bouncing_ball.py` — function API, simplest example
- `kbsmash/examples/snake.py` — function API, ASCII mode
- `kbsmash/examples/snake_emoji.py` — function API, emoji mode
- `kbsmash/examples/pong.py` — class API with pynput input
- `kbsmash/examples/gamepad_demo.py` — gamepad input (buttons, sticks, triggers)

Run one:

```bash
uv run python -m kbsmash.examples.bouncing_ball
```

## Tutorial

This tutorial walks through building up a game from scratch. By the end you'll
have written a bouncing ball, a dodge game, and a mini snake.

### 1. Your first screen

Every kbsmash program follows the same shape: `start()`, a loop that draws
frames, then `stop()`.

```python
from kbsmash import *

start(40, 10, fps=30, title="Hello")

while True:
    if get_key() == KEY_ESCAPE:
        break
    clear()
    text(5, 4, "Hello, world!")
    draw()

stop()
```

- `start(width, height, ...)` opens the terminal and sets the grid size.
- `clear()` wipes the buffer to spaces.
- `text(x, y, "...")` writes a string starting at column `x`, row `y`.
  `(0, 0)` is the top-left; `x` grows right, `y` grows down.
- `draw()` pushes the buffer to the terminal and waits until the next frame
  (at 30 fps, ~33 ms).
- `get_key()` returns the last key pressed, or `None` if no key is waiting.
  `KEY_ESCAPE` lets the player quit.

Press Esc to exit.

### 2. Moving a character

Keep track of a position in variables, update them each frame, and redraw.

```python
from kbsmash import *

start(40, 10, fps=30)

x, y = 20, 5

while True:
    key = get_key()
    if key == KEY_ESCAPE:
        break
    if key == "l": x += 1
    if key == "h": x -= 1
    if key == "j": y += 1
    if key == "k": y -= 1

    clear()
    put(x, y, "@")
    draw()

stop()
```

- `put(x, y, char)` draws a single character at `(x, y)`.
- Letter keys come back as their lowercase string: `"a"`, `"h"`, etc.
- Out-of-bounds `put()` calls are silently clipped, so you don't have to
  worry about crashing if `x` goes negative.

### 3. Held keys and smooth movement

`get_key()` only reports keys that arrived in the terminal buffer — it misses
held-down keys and has a ~500 ms OS delay before repeats kick in. For
arcade-style controls, use the `update_keys()` + `key_down()` API instead.

```python
from kbsmash import *

start(40, 10, fps=30, input="pynput")

x, y = 20, 5

while True:
    update_keys()
    if key_pressed(KEY_ESCAPE):
        break
    if key_down(KEY_LEFT):  x -= 1
    if key_down(KEY_RIGHT): x += 1
    if key_down(KEY_UP):    y -= 1
    if key_down(KEY_DOWN):  y += 1

    clear()
    put(x, y, "@", fg=YELLOW)
    draw()

stop()
```

- `update_keys()` drains all input events once per frame — call it at the top
  of your loop.
- `key_down(k)` is true every frame that key is held.
- `key_pressed(k)` is true only on the **first** frame the key was pressed
  (good for menu selections, jumps, firing a shot).
- `input="pynput"` uses OS-level key hooks, which is the nicest feel. The
  default `input="curses"` works everywhere but has the 500 ms repeat delay.

If the paddle moves too fast when held, add a `debounce`:

```python
start(40, 10, fps=30, input="pynput", debounce=0.05)
```

This limits `key_down()` to fire at most every 50 ms.

### 4. A bouncing ball

Putting movement, bounds-checking, and colors together:

```python
from kbsmash import *

start(40, 20, fps=30, title="Bouncing Ball")

x, y = 20, 10
dx, dy = 1, 1

while True:
    if get_key() == KEY_ESCAPE:
        break

    x += dx
    y += dy
    if x <= 0 or x >= screen_width() - 1:  dx = -dx
    if y <= 0 or y >= screen_height() - 1: dy = -dy

    clear()
    rect(0, 0, screen_width(), screen_height())
    put(x, y, "O", fg=RED)
    draw()

stop()
```

- `rect(x, y, w, h)` draws a box using the default box-drawing characters.
- `screen_width()` / `screen_height()` return the grid size you passed to
  `start()`.

### 5. Colors and styles

kbsmash has 16 named color constants: `BLACK`, `RED`, `GREEN`, `YELLOW`,
`BLUE`, `MAGENTA`, `CYAN`, `WHITE`, and their `BRIGHT_*` variants.

```python
put(5, 5, "@", fg=RED, bg=BLACK)
text(0, 0, "Score: 0", fg=BRIGHT_YELLOW)
```

For repeated styles, use `color()` to make a reusable handle:

```python
warning = color(BRIGHT_RED, BLACK)
hud     = color(BRIGHT_YELLOW)

text(10, 0, "GAME OVER", style=warning)
text(0, 0, "Score: 42", style=hud)
```

### 6. Drawing primitives

| Function | What it does |
|---|---|
| `put(x, y, ch)` | one character |
| `text(x, y, "...")` | a string |
| `rect(x, y, w, h)` | box outline (ASCII uses `┌─┐│└┘`) |
| `rect(x, y, w, h, char="#")` | box drawn with custom char |
| `fill(x, y, w, h, char)` | solid rectangle |
| `hline(x, y, len)` / `vline(x, y, len)` | horizontal/vertical line |

### 7. A mini dodge game

```python
import random
from kbsmash import *

start(40, 15, fps=20, debounce=0.05)

player_x = 20
obstacles = []  # list of [x, y]
score = 0
alive = True

while alive:
    update_keys()
    if key_pressed(KEY_ESCAPE) or button_pressed(BUTTON_START):
        break

    # Keyboard or gamepad
    if key_down(KEY_LEFT) or button_down(DPAD_LEFT):
        if player_x > 1: player_x -= 1
    if key_down(KEY_RIGHT) or button_down(DPAD_RIGHT):
        if player_x < 38: player_x += 1

    # Analog stick
    sx, _ = stick(STICK_LEFT)
    if sx < -0.3 and player_x > 1:  player_x -= 1
    if sx >  0.3 and player_x < 38: player_x += 1

    # move existing obstacles down, drop ones that fell off
    for o in obstacles:
        o[1] += 1
    obstacles = [o for o in obstacles if o[1] < 15]

    # spawn new obstacles
    if random.random() < 0.3:
        obstacles.append([random.randint(1, 38), 0])

    # collision
    for ox, oy in obstacles:
        if ox == player_x and oy == 14:
            alive = False

    score += 1

    clear()
    rect(0, 0, 40, 15)
    for ox, oy in obstacles:
        put(ox, oy, "*", fg=RED)
    put(player_x, 14, "A", fg=BRIGHT_YELLOW)
    text(1, 0, f" score {score} ", fg=BRIGHT_YELLOW)
    draw()

stop()
print(f"Game over! Score: {score}")
```

### 8. Emoji mode

Set `mode="emoji"` to use emoji as game tiles. Each cell is **2 terminal
columns wide** to make room for emoji.

```python
from kbsmash import *

start(15, 10, mode="emoji", input="pynput")

x, y = 7, 5
while True:
    update_keys()
    if key_pressed(KEY_ESCAPE): break
    if key_down(KEY_LEFT)  and x > 0:  x -= 1
    if key_down(KEY_RIGHT) and x < 14: x += 1
    if key_down(KEY_UP)    and y > 0:  y -= 1
    if key_down(KEY_DOWN)  and y < 9:  y += 1

    clear()
    rect(0, 0, 15, 10, char="⬜")
    put(x, y, "🍎")
    text(1, 0, f"pos {x:2d},{y:2d}", fg=BRIGHT_YELLOW)
    draw()

stop()
```

In emoji mode:

- Only wide characters (emoji, CJK) are allowed in `put()`.
- `rect()`, `hline()`, `vline()` require an explicit `char=` argument (no
  box-drawing default).
- `text()` still works — it packs **two ASCII chars per emoji cell**, so
  `"score"` uses 3 cells (`"sc"`, `"or"`, `"e "`).
- Putting an ASCII char in emoji mode (or an emoji in ASCII mode) raises
  `ValueError`.

### 9. Class-based API

For bigger games, subclass `Game` and keep all your state on `self`:

```python
from kbsmash import Game, KEY_UP, KEY_DOWN, KEY_ESCAPE, WHITE, YELLOW

class Pong(Game):
    def __init__(self):
        super().__init__(60, 24, fps=30, title="Pong", input="pynput")
        self.paddle_y = 10
        self.ball_x, self.ball_y = 30, 12
        self.ball_dx, self.ball_dy = 1, 1
        self.score = 0

pong = Pong()

with pong:
    while True:
        pong.update_keys()
        if pong.key_pressed(KEY_ESCAPE): break
        if pong.key_down(KEY_UP)   and pong.paddle_y > 0:                 pong.paddle_y -= 1
        if pong.key_down(KEY_DOWN) and pong.paddle_y < pong.height - 5:   pong.paddle_y += 1

        pong.ball_x += pong.ball_dx
        pong.ball_y += pong.ball_dy
        if pong.ball_y <= 0 or pong.ball_y >= pong.height - 1: pong.ball_dy *= -1
        if pong.ball_x >= pong.width - 2: pong.ball_dx *= -1
        if pong.ball_x == 1 and pong.paddle_y <= pong.ball_y <= pong.paddle_y + 4:
            pong.ball_dx *= -1
            pong.score += 1
        if pong.ball_x <= 0: break

        pong.clear()
        pong.rect(0, 0, pong.width, pong.height)
        for i in range(5):
            pong.put(1, pong.paddle_y + i, "█", fg=WHITE)
        pong.put(pong.ball_x, pong.ball_y, "o", fg=YELLOW)
        pong.text(pong.width // 2 - 4, 0, f" {pong.score} ", fg=YELLOW)
        pong.draw()
```

The `with pong:` context manager calls `start()` on entry and `stop()` on
exit, even if the game crashes.

### 10. Structure tip: start screens and game-over

Reset your game state **inside** the outer loop, before the inner game loop:

```python
while True:  # outer: loop forever
    # wait for a key to start
    while get_key() is None:
        clear()
        text(5, 5, "Press any key to start", fg=GREEN)
        draw()

    # reset for a new game
    x, y = 20, 10
    alive = True
    score = 0

    while alive:  # inner: one game
        ...
```

A common bug is forgetting to reset `alive = True`, which makes the inner
loop fall through instantly — the start screen then looks "stuck" but is
actually cycling through zero-length games.

### 11. Gamepad support

Gamepad support is enabled by default — Xbox and PlayStation controllers just
work. If no controller is connected, all gamepad calls return safe defaults so
your code doesn't need `if` guards.

`pygame` is installed automatically with kbsmash and provides the controller
backend.

Gamepad input uses the same `update_keys()` call you already have. Buttons
work like keys — `button_down()` for held, `button_pressed()` for edge:

```python
from kbsmash import *

start(40, 15, fps=20, input="pynput")

x, y = 20, 7

while True:
    update_keys()
    if key_pressed(KEY_ESCAPE) or button_pressed(BUTTON_START):
        break

    # D-pad (digital)
    if button_down(DPAD_LEFT):  x -= 1
    if button_down(DPAD_RIGHT): x += 1
    if button_down(DPAD_UP):    y -= 1
    if button_down(DPAD_DOWN):  y += 1

    # Left stick (analog) — (x, y) floats in [-1, 1]
    sx, sy = stick(STICK_LEFT)
    if sx < -0.3: x -= 1
    if sx >  0.3: x += 1

    # Face buttons
    if button_pressed(BUTTON_A):
        pass  # fire, jump, confirm...

    # Triggers — float in [0, 1]
    boost = trigger(TRIGGER_RIGHT)

    clear()
    put(x, y, "@", fg=YELLOW)
    draw()

stop()
```

**Button constants:**

| Constant | What |
|---|---|
| `BUTTON_A`, `B`, `X`, `Y` | Face buttons (A = south) |
| `BUTTON_L1`, `R1` | Shoulder bumpers |
| `BUTTON_L3`, `R3` | Stick clicks |
| `BUTTON_START`, `SELECT`, `HOME` | Menu buttons |
| `DPAD_UP`, `DOWN`, `LEFT`, `RIGHT` | D-pad |
| `STICK_LEFT`, `STICK_RIGHT` | For `stick()` |
| `TRIGGER_LEFT`, `TRIGGER_RIGHT` | For `trigger()` |

To disable gamepad (e.g. to avoid the pygame import), pass `gamepad=False`:

```python
start(40, 20, gamepad=False)
```

### Reference

See [spec.md](spec.md) for the full API and design.
