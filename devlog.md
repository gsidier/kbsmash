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
