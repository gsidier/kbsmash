from kbsmash import *
from random import randint
import time

width = 20
height = 20

start(width, height, fps=8, title="Snake", mode="emoji")


def any_input():
    """Either a key or a gamepad button was just pressed."""
    return len(keys_down()) > 0 or len(buttons_down()) > 0


while True: # loop forever

    while True: # wait key press to start game
        update_keys()

        if key_pressed(KEY_ESCAPE):
            play = False
            break

        elif any_input():
            play = True
            break

        clear()
        text(2, 9, "Smash a key or button to start (esc exits)", fg=GREEN)
        draw()

    if not play:
        break

    alive = True
    snake = [(7, 10)]
    direction = (1, 0)
    food = (randint(1, 13), randint(1, 18))
    score = 0

    while alive: # game loop

        update_keys()
        # Keyboard + D-pad + left analog stick
        sx, sy = stick(STICK_LEFT)
        up    = key_down(KEY_UP)    or button_down(DPAD_UP)    or sy < -0.5
        down  = key_down(KEY_DOWN)  or button_down(DPAD_DOWN)  or sy >  0.5
        left  = key_down(KEY_LEFT)  or button_down(DPAD_LEFT)  or sx < -0.5
        right = key_down(KEY_RIGHT) or button_down(DPAD_RIGHT) or sx >  0.5
        if   up    and direction != (0,  1): direction = (0, -1)
        elif down  and direction != (0, -1): direction = (0,  1)
        elif left  and direction != (1,  0): direction = (-1, 0)
        elif right and direction != (-1, 0): direction = (1,  0)
        if key_down(KEY_ESCAPE) or button_pressed(BUTTON_START): break

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
