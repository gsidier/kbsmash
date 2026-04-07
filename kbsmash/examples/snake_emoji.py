from kbsmash import *
from random import randint
import time 

width = 20
height = 20

start(width, height, fps=8, title="Snake", mode="emoji")


while True: # loop forever

    while True: # wait key press to start game
        update_keys()

        if key_pressed(KEY_ESCAPE):
            play = False
            break

        elif len(keys_down()) > 0:
            play = True
            break

        clear()
        text(2, 9, "Smash a key to start (esc exits)", fg=GREEN)
        draw()

    if not play:
        break

    alive = True
    snake = [(7, 10)]
    direction = (1, 0)
    food = (randint(1, 13), randint(1, 18))
    score = 0

    while alive: # game loop
        
        update_keys()
        if key_down(KEY_UP) and (direction != (0, 1)):      direction = (0, -1)
        elif key_down(KEY_DOWN) and (direction != (0, -1)):  direction = (0, 1)
        elif key_down(KEY_LEFT) and (direction != (1, 0)):  direction = (-1, 0)
        elif key_down(KEY_RIGHT) and (direction != (-1, 0)): direction = (1, 0)
        elif key_down(KEY_ESCAPE): break

        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        if (head[0] < 0 or head[0] >= width or
            head[1] < 0 or head[1] >= height or
            head in snake):
            alive = False
            continue

        snake.insert(0, head)
        if head == food:
            score += 1
            food = (randint(1, 13), randint(1, 18))
        else:
            snake.pop()

        clear()
        rect(0, 0, width, height, char="🟫")
        put(food[0], food[1], "🍎")
        for i, seg in enumerate(snake):
            put(seg[0], seg[1], "😺" if i == 0 else "🍏")
        text(1, 0, f" Score: {score} ", fg=YELLOW)
        draw()

clear()
text(2, 9, "Bye !", fg=RED)
draw()
time.sleep(1)
stop()
