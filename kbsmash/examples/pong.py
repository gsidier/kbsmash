from kbsmash import Game, KEY_UP, KEY_DOWN, KEY_ESCAPE, WHITE, YELLOW


class Pong(Game):
    def __init__(self):
        super().__init__(60, 24, fps=30, title="Pong", debounce=0.03, input="pynput")
        self.paddle_y = 10
        self.ball_x, self.ball_y = 30, 12
        self.ball_dx, self.ball_dy = 1, 1
        self.score = 0


pong = Pong()

with pong:
    while True:
        pong.update_keys()
        if pong.key_pressed(KEY_ESCAPE):
            break
        if pong.key_down(KEY_UP) and pong.paddle_y > 0:
            pong.paddle_y -= 1
        if pong.key_down(KEY_DOWN) and pong.paddle_y < pong.height - 5:
            pong.paddle_y += 1

        pong.ball_x += pong.ball_dx
        pong.ball_y += pong.ball_dy
        if pong.ball_y <= 0 or pong.ball_y >= pong.height - 1:
            pong.ball_dy *= -1
        if pong.ball_x >= pong.width - 2:
            pong.ball_dx *= -1
        if (pong.ball_x == 1 and
                pong.paddle_y <= pong.ball_y <= pong.paddle_y + 4):
            pong.ball_dx *= -1
            pong.score += 1
        if pong.ball_x <= 0:
            break

        pong.clear()
        pong.rect(0, 0, pong.width, pong.height)
        for i in range(5):
            pong.put(1, pong.paddle_y + i, "█", fg=WHITE)
        pong.put(pong.ball_x, pong.ball_y, "o", fg=YELLOW)
        pong.text(pong.width // 2 - 4, 0, f" {pong.score} ", fg=YELLOW)
        pong.draw()
