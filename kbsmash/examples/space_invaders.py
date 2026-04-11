import kbsmash

char_invader = "👾"
char_saucer = "🛸"
char_player = "🗼"
char_bullet = "💩"
char_zap = "⚡"
char_explosion = "💥"


class Invader:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = 'alive'
        self.explosion_timer = 10

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
            wave.remove(self)
    


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
            shields.remove(self)

    def alive(self):
        return self.hits < len(Shield.CHARS)


class Bullet:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        self.y -= 1

    def draw(self):
        kbsmash.put(self.x, self.y, char_bullet)
    
    def alive(self):
        return self.y >= 0


width = 50
height = 40

wave_width = 40
wave_height = 4

game_area_left = 0
game_area_right = width - 1
game_area_bottom = height - 1
game_area_top = 0


wave_speed = .1
wave_direction = +1

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

def move_wave(wave):
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
            if (round(bullet.x), round(bullet.y)) == (round(invader.x), round(invader.y)):
                invader.hit()
                bullets.remove(bullet)
        
        for shield in [*shields]:
            if (round(bullet.x), round(bullet.y)) == (round(shield.x), round(shield.y)):
                shield.hit()
                bullets.remove(bullet)

kbsmash.start(
    width=width, 
    height=height, 
    fps=15, 
    title="Space Invaders", 
    mode="emoji")


while True:

    while True: # wait key press to start game
        kbsmash.update_keys()

        if kbsmash.key_pressed(kbsmash.KEY_ESCAPE):
            play = False
            break

        elif kbsmash.key_pressed(kbsmash.KEY_SPACE):
            play = True
            break

        kbsmash.clear()
        kbsmash.text(10, 9, "Smash space to start (esc exits)", fg=kbsmash.GREEN)
        kbsmash.draw()

    if not play:
        break

    alive = True
    player_x = width // 2
    player_y = game_area_bottom - 1
    player_speed = 1
    score = 0

    wave = create_wave(startx=1, starty=1, wave_width=wave_width, wave_height=wave_height)
    shields = create_shields(player_y - 2, shield_width=2, shield_spacing=6)
    bullets = set()

    while alive: # game loop

        # Move 

        for bullet in [*bullets]:
            bullet.move()
        
        # Move invaders
        move_wave(wave)
        for invader in [*wave]:
            invader.update()

        handle_collisions()
        
        
        kbsmash.update_keys()
        if kbsmash.key_down(kbsmash.KEY_LEFT):
            if player_x - player_speed >= game_area_left:
                player_x -= player_speed
        if kbsmash.key_down(kbsmash.KEY_RIGHT):
            if player_x + player_speed <= game_area_right:
                player_x += player_speed

        if kbsmash.key_pressed(kbsmash.KEY_SPACE):
            # shoot
            bullets.add(Bullet(x=player_x, y=player_y-1))
        if kbsmash.key_pressed(kbsmash.KEY_ESCAPE):
            break

        #
        kbsmash.clear()
        #kbsmash.fill(0, 0, width, height, "🌌")
        kbsmash.put(x=player_x, y=player_y, char=char_player)
        for invader in wave:
            invader.draw()
        for shield in shields:
            shield.draw()
        for bullet in bullets:
            bullet.draw()
        kbsmash.draw()
