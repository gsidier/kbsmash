from kbsmash import *

start(40, 20, fps=30, title="Bouncing Ball")

x, y = 20, 10
dx, dy = 1, 1
running = True

while running:
    key = get_key()
    if key == KEY_ESCAPE:
        running = False

    x += dx
    y += dy
    if x <= 0 or x >= screen_width() - 1:
        dx = -dx
    if y <= 0 or y >= screen_height() - 1:
        dy = -dy

    clear()
    rect(0, 0, screen_width(), screen_height())
    put(x, y, "O", fg=RED)
    draw()

stop()
