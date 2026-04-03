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
