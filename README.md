# kbsmash

A minimal Python engine for building terminal arcade games — designed for educational purposes.

Students write the game loop themselves; kbsmash handles the terminal, drawing, input, and timing.

## Install

```bash
uv sync                   # core engine (stdlib only)
uv sync --extra pynput    # also install pynput for precise key handling
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
- **FPS regulation** — fixed frame rate or unlimited, with `dt()` for smooth movement

## Examples

- `kbsmash/examples/bouncing_ball.py` — function API, simplest example
- `kbsmash/examples/snake.py` — function API, ASCII mode
- `kbsmash/examples/snake_emoji.py` — function API, emoji mode
- `kbsmash/examples/pong.py` — class API with pynput input

Run one:

```bash
uv run python -m kbsmash.examples.bouncing_ball
```

## Documentation

See [spec.md](spec.md) for the full API and design.
