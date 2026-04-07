from kbsmash import *
from random import randint

start(30, 20, fps=8, title="Snake", mode="ascii")

snake = [(15, 10)]
direction = (1, 0)
food = (randint(1, 28), randint(1, 18))
score = 0
alive = True

while alive:
    key = get_key()
    if key == KEY_UP:      direction = (0, -1)
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
    put(food[0], food[1], "@", fg=RED)
    for i, seg in enumerate(snake):
        put(seg[0], seg[1], "O" if i == 0 else "o", fg=GREEN)
    text(1, 0, f" Score: {score} ", fg=YELLOW)
    draw()

stop()
