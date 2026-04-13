import kbsmash
import random
import time

char_invader = "👾"
char_saucer = "🛸"
char_player = "🗼"
char_bullet = "💩"
char_zap = "⚡"
char_explosion = "💥"


screen_width = 30
screen_height = 25

game_area_left = 0
game_area_right = screen_width - 1
game_area_bottom = screen_height - 4
game_area_top = 0
status_area_y = screen_height - 2
score_x = 5
score_y = status_area_y
player_lives_x = game_area_right - 10
player_lives_y = status_area_y

wave_width = round(screen_width * .66)

WAVE_SPEED = [ .05, .1, .15, .25, .4 ]
WAVE_ZAP_PROB = [ .1, .15, .2, .3, .5 ]
WAVE_ROWS = [ 3, 3, 4, 4, 5 ]

class Invader:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = 'alive'
        self.explosion_timer = 0

    def draw(self):
        if self.state == 'alive':
            kbsmash.put(round(self.x), round(self.y), char_invader)
        elif self.state == 'hit':
           kbsmash.put(round(self.x), round(self.y), char_explosion)

    def hit(self):
        self.state = 'hit'
        self.explosion_timer = 10

    def update(self):
        if self.state == 'hit':
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.state = 'dead'
                if self in wave:
                    wave.remove(self)

    def zap(self):
        if self.alive():
            enemy_zaps.add(EnemyZap(round(self.x), round(self.y+1)))

    def alive(self):
        return self.state == 'alive'


class Player:

    START_LIVES = 3
    START_X = (game_area_left + game_area_right) // 2
    START_Y = game_area_bottom - 1

    def __init__(self):
        self.reset_position()
        self.speed = 1
        self.lives = Player.START_LIVES
        self.state = 'alive'
        self.score = 0
        self.explosion_timer = 0

    def reset_position(self):
        self.x = Player.START_X
        self.y = Player.START_Y

    def draw(self):
        if self.state == 'alive':
            kbsmash.put(round(self.x), round(self.y), char_player)
        elif self.state == 'hit':
           kbsmash.put(round(self.x), round(self.y), char_explosion)

    def hit(self):
        self.state = 'hit'
        self.explosion_timer = 10

    def update(self):
        if self.state == 'hit':
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.lives -= 1
                if self.lives > 0:
                    self.x = Player.START_X
                    self.y = Player.START_Y
                    self.state = 'alive'
                else:
                    self.state = 'dead'

    def alive(self):
        return self.state == 'alive'


class Shield:

    CHARS = [ "⬜", "🟨", "🟧", "🟫" ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hits = 0

    @property
    def char(self):
        return Shield.CHARS[self.hits]

    def draw(self):
        if self.hits < len(Shield.CHARS):
            kbsmash.put(self.x, self.y, self.char)

    def hit(self) -> bool:
        self.hits += 1
        if not self.alive():
            if self in shields:
                shields.remove(self)

    def alive(self):
        return self.hits < len(Shield.CHARS)


class Bullet:

    MAX_BULLETS = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        self.y -= 1

    def draw(self):
        kbsmash.put(self.x, self.y, char_bullet)

    def alive(self):
        return self.y >= 0


class EnemyZap:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        self.y += 1

    def draw(self):
        kbsmash.put(self.x, self.y, char_zap)

    def alive(self):
        return self.y <= game_area_bottom



def create_wave(startx, starty, wave_width, wave_height):
    wave = set()
    for row in range(wave_height):
        for col in range(wave_width):
            wave.add(Invader(startx + col + (row % 2), starty + row))
    return wave

def create_shields(shield_y, shield_width, shield_spacing):
    shields = set()
    i = 0
    for shield_x in range(game_area_left, game_area_right-shield_width, shield_spacing + shield_width):
        for j in range(shield_width):
            shields.add(Shield(x=shield_x+j, y=shield_y))
            i += 1
    return shields

def move_wave(wave, wave_speed):
    global wave_direction
    max_x = max(invader.x for invader in wave)
    min_x = min(invader.x for invader in wave)
    if (wave_direction == +1) and (round(max_x) >= game_area_right):
        change_direction = True
    elif (wave_direction == -1) and (round(min_x) <= game_area_left):
        change_direction = True
    else:
        change_direction = False

    if change_direction:
            wave_direction = -wave_direction
            for invader in wave:
                invader.y += 1

    for invader in wave:
        invader.x += wave_direction * wave_speed

def handle_collisions():
    for bullet in [*bullets]:
        for invader in [*wave]:
            if invader.alive() and (round(bullet.x), round(bullet.y)) == (round(invader.x), round(invader.y)):
                invader.hit()
                player.score += 100
                if bullet in bullets:
                    bullets.remove(bullet)

        for shield in [*shields]:
            if (round(bullet.x), round(bullet.y)) == (round(shield.x), round(shield.y)):
                shield.hit()
                if bullet in bullets:
                    bullets.remove(bullet)

    for zap in [*enemy_zaps]:
        for shield in [*shields]:
            if (round(zap.x), round(zap.y)) == (round(shield.x), round(shield.y)):
                shield.hit()
                if zap in enemy_zaps:
                    enemy_zaps.remove(zap)

        if (player.state == 'alive') and (round(zap.x), round(zap.y)) == (round(player.x), round(player.y)):
            player.hit()

kbsmash.start(
    width=screen_width,
    height=screen_height,
    fps=15,
    title="Space Invaders",
    mode="emoji")


while True:

    while True: # wait key press to start game
        kbsmash.update_keys()

        if kbsmash.key_pressed(kbsmash.KEY_ESCAPE):
            play = False
            break

        elif (kbsmash.key_pressed(kbsmash.KEY_SPACE)
              or kbsmash.button_pressed(kbsmash.BUTTON_A)
              or kbsmash.button_pressed(kbsmash.BUTTON_START)):
            play = True
            break

        kbsmash.clear()
        kbsmash.text(4, 9, "Smash space or A to start (esc exits)", fg=kbsmash.GREEN)
        kbsmash.draw()

    if not play:
        break

    player = Player()
    score = 0

    for level in range(len(WAVE_ROWS)):
        wave_direction = +1
        wave_speed = WAVE_SPEED[level]
        wave_height = WAVE_ROWS[level]
        wave_zap_probability = WAVE_ZAP_PROB[level]

        kbsmash.clear()
        txt = f"W A V E  {level+1}"
        kbsmash.text((screen_width - len(txt)) // 2, screen_height // 2, txt, fg=kbsmash.GREEN)
        kbsmash.draw()
        time.sleep(2)

        wave = create_wave(startx=1, starty=1, wave_width=wave_width, wave_height=wave_height)
        shields = create_shields(player.y - 2, shield_width=2, shield_spacing=6)
        bullets = set()
        enemy_zaps = set()

        wave_complete = False

        while True: # game loop

            # Game state
            if player.state == 'dead':
                break

            if len(wave) == 0:
                wave_complete = True
                break

            # Move and update sprites
            for bullet in [*bullets]:
                bullet.move()

            move_wave(wave, wave_speed=wave_speed)
            for invader in [*wave]:
                invader.update()

            if wave and (random.random() <= wave_zap_probability):
                invader = random.choice(list(wave))
                invader.zap()

            for zap in enemy_zaps:
                zap.move()

            player.update()

            # Handle collisions
            handle_collisions()

            # Handle input
            kbsmash.update_keys()
            sx, _ = kbsmash.stick(kbsmash.STICK_LEFT)
            if player.alive():
                move_left = (kbsmash.key_down(kbsmash.KEY_LEFT)
                             or kbsmash.button_down(kbsmash.DPAD_LEFT)
                             or sx < -0.3)
                move_right = (kbsmash.key_down(kbsmash.KEY_RIGHT)
                              or kbsmash.button_down(kbsmash.DPAD_RIGHT)
                              or sx > 0.3)
                if move_left and player.x - player.speed >= game_area_left:
                    player.x -= player.speed
                if move_right and player.x + player.speed <= game_area_right:
                    player.x += player.speed
                if (kbsmash.key_pressed(kbsmash.KEY_SPACE)
                        or kbsmash.button_pressed(kbsmash.BUTTON_A)):
                    # shoot
                    #if len(bullets) < Bullet.MAX_BULLETS:
                    bullets.add(Bullet(x=player.x, y=player.y-1))
            if (kbsmash.key_pressed(kbsmash.KEY_ESCAPE)
                    or kbsmash.button_pressed(kbsmash.BUTTON_START)):
                break

            # Draw the screen
            kbsmash.clear()
            player.draw()
            for invader in wave:
                invader.draw()
            for shield in shields:
                shield.draw()
            for bullet in bullets:
                bullet.draw()
            for zap in enemy_zaps:
                zap.draw()
            kbsmash.text(score_x, score_y, str(player.score), fg=kbsmash.GREEN)
            for i in range(player.lives - 1):
                kbsmash.put(player_lives_x + i*2, player_lives_y, char_player)
            kbsmash.draw()

        if player.state == 'dead':
            kbsmash.clear()
            txt = "G A M E  O V E R"
            kbsmash.text((screen_width - len(txt)) // 2, screen_height // 2, txt, fg=kbsmash.RED)
            kbsmash.draw()
            time.sleep(2)
            break

        if not wave_complete:
            break

    if wave_complete:
        kbsmash.clear()
        #  🎉 🎊 🎖 🎖 
        txt = "YOU COMPLETED THE GAME!"
        kbsmash.text((screen_width - len(txt)) // 2, screen_height // 2, txt, fg=kbsmash.YELLOW)
        kbsmash.draw()
        time.sleep(3)
        break
 