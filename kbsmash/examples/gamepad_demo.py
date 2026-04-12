"""Minimal gamepad demo.

Run:  uv sync --extra gamepad
      uv run python -m kbsmash.examples.gamepad_demo
"""

from kbsmash import (
    start, stop, clear, put, text, rect, draw,
    update_keys, key_pressed, button_down, button_pressed, stick, trigger,
    KEY_ESCAPE, BUTTON_A, BUTTON_B, BUTTON_X, BUTTON_Y,
    DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT,
    WHITE, RED, GREEN, YELLOW, BRIGHT_CYAN,
)

start(60, 20, fps=30, mode="ascii", title="Gamepad Demo",
      input="pynput", gamepad=True)

x, y = 30.0, 10.0

while True:
    update_keys()
    if key_pressed(KEY_ESCAPE):
        break

    # Analog movement
    sx, sy = stick("left")
    x += sx * 0.5
    y += sy * 0.5

    # D-pad also moves the cursor
    if button_down(DPAD_LEFT):  x -= 0.5
    if button_down(DPAD_RIGHT): x += 0.5
    if button_down(DPAD_UP):    y -= 0.5
    if button_down(DPAD_DOWN):  y += 0.5

    x = max(1, min(58, x))
    y = max(1, min(18, y))

    clear()
    rect(0, 0, 60, 20)
    text(2, 0, " Gamepad Demo ", fg=BRIGHT_CYAN)
    text(2, 2, "left stick:  move", fg=WHITE)
    text(2, 3, "A/B/X/Y:     press to paint", fg=WHITE)
    text(2, 4, "triggers:    bars below", fg=WHITE)
    text(2, 5, "escape:      quit", fg=WHITE)

    # Trigger bars
    lt = int(trigger("left") * 20)
    rt = int(trigger("right") * 20)
    text(2, 17, f"L2 [{'#' * lt:<20}]", fg=YELLOW)
    text(2, 18, f"R2 [{'#' * rt:<20}]", fg=YELLOW)

    # Face buttons paint the cursor different colors
    color = WHITE
    if button_down(BUTTON_A): color = GREEN
    if button_down(BUTTON_B): color = RED
    if button_down(BUTTON_X): color = BRIGHT_CYAN
    if button_down(BUTTON_Y): color = YELLOW

    put(int(x), int(y), "@", fg=color)
    draw()

stop()
