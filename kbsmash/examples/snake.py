from kbsmash import *
from random import randint

start(30, 20, fps=8, title="Snake", mode="ascii", gamepad=True)

snake = [(15, 10)]
direction = (1, 0)
food = (randint(1, 28), randint(1, 18))
score = 0
alive = True

while alive:
    update_keys()
    if key_pressed(KEY_ESCAPE) or button_pressed(BUTTON_START): break

    # Keyboard arrows OR D-pad OR left analog stick
    sx, sy = stick(STICK_LEFT)
    if   key_pressed(KEY_UP)    or button_pressed(DPAD_UP)    or sy < -0.5: direction = (0, -1)
    elif key_pressed(KEY_DOWN)  or button_pressed(DPAD_DOWN)  or sy >  0.5: direction = (0, 1)
    elif key_pressed(KEY_LEFT)  or button_pressed(DPAD_LEFT)  or sx < -0.5: direction = (-1, 0)
    elif key_pressed(KEY_RIGHT) or button_pressed(DPAD_RIGHT) or sx >  0.5: direction = (1, 0)

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
    put(food[0], food[1], "@", fg=RED)
    for i, seg in enumerate(snake):
        put(seg[0], seg[1], "O" if i == 0 else "o", fg=GREEN)
    text(1, 0, f" Score: {score} ", fg=YELLOW)
    draw()

stop()
