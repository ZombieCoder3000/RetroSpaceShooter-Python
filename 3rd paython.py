import pygame
import random
import os

# --- 1. INITIALIZATION & SETUP ---
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galactic Defender - Ultimate Edition")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Clock
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36) # Default font, size 36

# --- 2. ASSET LOADING (The Safety Net) ---
# This block ensures the game runs even if you don't have the files yet.

def load_image(name, color, size):
    try:
        img = pygame.image.load(name).convert_alpha()
    except FileNotFoundError:
        # If file missing, create a placeholder colored block
        img = pygame.Surface(size)
        img.fill(color)
    return img

def load_sound(name):
    try:
        return pygame.mixer.Sound(name)
    except FileNotFoundError:
        # Return a dummy class if sound is missing so game doesn't crash
        class DummySound:
            def play(self): pass
        return DummySound()

# Load Graphics (Placeholders used if files not found)
player_img = load_image("spaceship.png", GREEN, (50, 40))
enemy_img = load_image("alien.png", RED, (40, 40))
bullet_img = load_image("bullet.png", YELLOW, (10, 20))
background_img = load_image("starfield.png", BLACK, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load Sounds
shoot_sound = load_sound("pew.wav")
expl_sound = load_sound("expl.wav")

# --- 3. HELPER FUNCTIONS ---

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# --- 4. CLASSES ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -8
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 8
        self.rect.x += self.speed_x
        
        # Boundaries
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play() # Play Sound

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(2, 6)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(2, 6)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# --- 5. GAME LOOP SETUP ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(8):
    e = Enemy()
    all_sprites.add(e)
    enemies.add(e)

score = 0
running = True
game_over = False

# --- 6. THE LOOP ---
while running:
    # A. Input Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # If Game Over, show screen and wait
    if game_over:
        screen.fill(BLACK)
        draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(screen, f"Final Score: {score}", 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, "Press Q to Quit or R to Restart", 22, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 / 4)
        pygame.display.flip()
        
        # Wait for input to restart or quit
        waiting = True
        while waiting:
            clock.tick(15)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                        waiting = False
                    if event.key == pygame.K_r:
                        # Reset Game
                        game_over = False
                        waiting = False
                        score = 0
                        all_sprites.empty()
                        enemies.empty()
                        bullets.empty()
                        player = Player()
                        all_sprites.add(player)
                        for i in range(8):
                            e = Enemy()
                            all_sprites.add(e)
                            enemies.add(e)
        continue # Skip the rest of the loop until restart logic is done

    # B. Update
    all_sprites.update()

    # C. Collisions
    # 1. Bullet hits Enemy
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 10
        expl_sound.play() # Play Explosion Sound
        e = Enemy() # Spawn new enemy
        all_sprites.add(e)
        enemies.add(e)

    # 2. Enemy hits Player
    hits = pygame.sprite.spritecollide(player, enemies, False)
    if hits:
        game_over = True

    # D. Draw
    screen.fill(BLACK) # Or screen.blit(background_img, (0,0))
    all_sprites.draw(screen)
    draw_text(screen, str(score), 30, SCREEN_WIDTH // 2, 10)

    # E. Flip
    pygame.display.flip()
    clock.tick(60)

pygame.quit()