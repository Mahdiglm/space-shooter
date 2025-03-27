import pygame
import random
import sys
import math
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Set up the game window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")

# Asset paths
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
IMG_DIR = os.path.join(ASSET_DIR, "images")
SOUND_DIR = os.path.join(ASSET_DIR, "sounds")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Game settings
DIFFICULTY_INCREASE_RATE = 0.08  # Reduced for better balance
INITIAL_ENEMY_SPEED = 2
MAX_ENEMY_SPEED = 5
POWERUP_CHANCE = 0.15  # Increased powerup chance
BOSS_SPAWN_SCORE = 1000
SHIELD_DURATION = 5000  # 5 seconds, increased from 3 seconds

# Load images
# Try to load background image, fallback to black background if file not found
try:
    background_img = pygame.image.load(os.path.join(IMG_DIR, "background.jpg")).convert()
    background_img = pygame.transform.scale(background_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
except pygame.error:
    background_img = None
    print("Background image not found. Using black background.")

# Try to load player image, fallback to default if file not found
try:
    player_img = pygame.image.load(os.path.join(IMG_DIR, "player.png")).convert_alpha()
    player_img = pygame.transform.scale(player_img, (50, 40))
except pygame.error:
    player_img = None
    print("Player image not found. Using default.")

# Try to load enemy images, fallback to defaults if files not found
try:
    enemy_img = pygame.image.load(os.path.join(IMG_DIR, "enemy.png")).convert_alpha()
    enemy_img = pygame.transform.scale(enemy_img, (30, 30))
except pygame.error:
    enemy_img = None
    print("Enemy image not found. Using default.")

try:
    fast_enemy_img = pygame.image.load(os.path.join(IMG_DIR, "fast_enemy.png")).convert_alpha()
    fast_enemy_img = pygame.transform.scale(fast_enemy_img, (30, 30))
except pygame.error:
    fast_enemy_img = None
    print("Fast enemy image not found. Using default.")

try:
    tank_enemy_img = pygame.image.load(os.path.join(IMG_DIR, "tank_enemy.png")).convert_alpha()
    tank_enemy_img = pygame.transform.scale(tank_enemy_img, (30, 30))
except pygame.error:
    tank_enemy_img = None
    print("Tank enemy image not found. Using default.")

try:
    boss_enemy_img = pygame.image.load(os.path.join(IMG_DIR, "boss_enemy.png")).convert_alpha()
    boss_enemy_img = pygame.transform.scale(boss_enemy_img, (60, 60))
except pygame.error:
    boss_enemy_img = None
    print("Boss enemy image not found. Using default.")

try:
    bullet_img = pygame.image.load(os.path.join(IMG_DIR, "bullet.png")).convert_alpha()
    bullet_img = pygame.transform.scale(bullet_img, (5, 10))
except pygame.error:
    bullet_img = None
    print("Bullet image not found. Using default.")

# Load sounds
try:
    shoot_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "shoot.wav"))
    shoot_sound.set_volume(0.4)
except pygame.error:
    shoot_sound = None
    print("Shoot sound not found.")

try:
    explosion_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "explosion.wav"))
    explosion_sound.set_volume(0.6)
except pygame.error:
    explosion_sound = None
    print("Explosion sound not found.")

try:
    powerup_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "powerup.wav"))
    powerup_sound.set_volume(0.5)
except pygame.error:
    powerup_sound = None
    print("Power-up sound not found.")

try:
    game_over_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "game_over.wav"))
    game_over_sound.set_volume(0.7)
except pygame.error:
    game_over_sound = None
    print("Game over sound not found.")

try:
    background_music = os.path.join(SOUND_DIR, "background_music.mp3")
    pygame.mixer.music.load(background_music)
    pygame.mixer.music.set_volume(0.3)
except pygame.error:
    print("Background music not found.")

# Player spaceship
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if player_img:
            self.image = player_img
            self.original_image = player_img
        else:
            self.image = pygame.Surface((50, 40))
            self.image.fill(WHITE)
            self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.radius = 20  # Collision radius, more accurate than rectangle
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = WINDOW_HEIGHT - 10
        self.speed = 6  # Slightly increased for better movement
        self.health = 100
        self.max_health = 100
        self.power_level = 1
        self.shoot_delay = 250  # milliseconds
        self.last_shot = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = SHIELD_DURATION
        self.animation_tick = 0
        # Damage flash
        self.hit = False
        self.hit_time = 0
        self.hit_duration = 100  # Milliseconds for damage flash

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
            self.rect.x += self.speed
        
        # Update damage flash
        current_time = pygame.time.get_ticks()
        if self.hit:
            if current_time - self.hit_time > self.hit_duration:
                self.hit = False
                self.image = self.original_image.copy()
        
        # Update invulnerability
        if self.invulnerable:
            # Make the player blink when invulnerable
            self.animation_tick += 1
            if self.animation_tick % 8 == 0:  # Faster blinking
                if not self.hit:  # Don't override damage flash
                    if self.image.get_alpha() == 255 or self.image.get_alpha() is None:
                        self.image.set_alpha(128)
                    else:
                        self.image.set_alpha(255)
            
            if current_time - self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable = False
                self.image = self.original_image.copy()
                self.image.set_alpha(255)  # Restore full opacity

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            if shoot_sound:
                shoot_sound.play()
            
            if self.power_level == 1:
                return [Bullet(self.rect.centerx, self.rect.top)]
            elif self.power_level == 2:
                return [
                    Bullet(self.rect.left + 10, self.rect.top),
                    Bullet(self.rect.right - 10, self.rect.top)
                ]
            else:  # power_level == 3
                return [
                    Bullet(self.rect.centerx, self.rect.top),
                    Bullet(self.rect.left + 10, self.rect.top),
                    Bullet(self.rect.right - 10, self.rect.top)
                ]
        return []
    
    def take_damage(self, amount=1):
        if not self.invulnerable:
            self.health -= amount
            # Add damage flash
            self.hit = True
            self.hit_time = pygame.time.get_ticks()
            temp_img = self.original_image.copy()
            temp_img.fill(RED, special_flags=pygame.BLEND_RGB_ADD)
            self.image = temp_img

# Enemy base class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if enemy_img:
            self.image = enemy_img
        else:
            self.image = pygame.Surface((30, 30))
            self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.radius = 15  # Collision radius, more accurate than rectangle
        self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.speedx = 0
        self.health = 1
        self.points = 10
        self.shoot_delay = None  # Most enemies don't shoot

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # Bouncing off edges logic
        if self.rect.left < 0 and self.speedx < 0:
            self.speedx = -self.speedx
        if self.rect.right > WINDOW_WIDTH and self.speedx > 0:
            self.speedx = -self.speedx
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 4)

# Fast Enemy
class FastEnemy(Enemy):
    def __init__(self):
        super().__init__()
        if fast_enemy_img:
            self.image = fast_enemy_img
        else:
            self.image.fill(BLUE)
        self.speedy = random.randrange(4, 7)
        self.speedx = random.choice([-2, -1, 0, 1, 2])  # Some horizontal movement
        self.health = 1
        self.points = 15

# Tank Enemy
class TankEnemy(Enemy):
    def __init__(self):
        super().__init__()
        if tank_enemy_img:
            self.image = tank_enemy_img
        else:
            self.image.fill(GREEN)
        self.speedy = random.randrange(1, 3)
        self.health = 4  # Increased health for more challenge
        self.points = 25

# Boss Enemy
class BossEnemy(Enemy):
    def __init__(self):
        super().__init__()
        if boss_enemy_img:
            self.image = boss_enemy_img
        else:
            self.image = pygame.Surface((60, 60))
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.radius = 30  # Collision radius, more accurate than rectangle
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.y = -80
        self.speedy = 1
        self.speedx = 2
        self.health = 25  # Increased for more challenge
        self.points = 150  # Increased points reward
        self.movement_pattern = 0
        self.movement_timer = 0
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 2000  # 2 seconds between shots

    def update(self):
        # Boss intro movement
        if self.rect.top < 50:
            self.rect.y += 1
            return
        
        # Normal movement patterns
        self.movement_timer += 1
        if self.movement_timer > 60:
            self.movement_pattern = (self.movement_pattern + 1) % 4
            self.movement_timer = 0

        if self.movement_pattern == 0:
            self.rect.x += self.speedx
        elif self.movement_pattern == 1:
            self.rect.x -= self.speedx
        elif self.movement_pattern == 2:
            self.rect.y += 1
        else:
            self.rect.y -= 1

        if self.rect.left < 0:
            self.rect.left = 0
            self.speedx = abs(self.speedx)
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
            self.speedx = -abs(self.speedx)
        if self.rect.top < 50:
            self.rect.top = 50
        if self.rect.bottom > WINDOW_HEIGHT // 2:
            self.rect.bottom = WINDOW_HEIGHT // 2
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            return [
                EnemyBullet(self.rect.centerx - 15, self.rect.bottom),
                EnemyBullet(self.rect.centerx + 15, self.rect.bottom)
            ]
        return []

# Enemy Bullet
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.radius = 4  # Collision radius
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = 6

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

# Power-up
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        try:
            self.image = pygame.image.load(os.path.join(IMG_DIR, f"{power_type}_powerup.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (20, 20))
        except pygame.error:
            self.image = pygame.Surface((20, 20))
            if power_type == "health":
                self.image.fill(GREEN)
            elif power_type == "power":
                self.image.fill(BLUE)
            elif power_type == "shield":
                self.image.fill(YELLOW)
        
        self.rect = self.image.get_rect()
        self.radius = 10  # Collision radius
        self.rect.centerx = x
        self.rect.centery = y
        self.speedy = 2
        # Add a wobble effect
        self.wobble = 0
        self.wobble_dir = 1
        self.wobble_speed = random.randint(1, 3) * 0.1

    def update(self):
        self.rect.y += self.speedy
        # Wobble effect
        self.wobble += self.wobble_speed * self.wobble_dir
        if abs(self.wobble) > 1.5:
            self.wobble_dir *= -1
        self.rect.x += self.wobble_dir * self.wobble_speed
        
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

# Bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        if bullet_img:
            self.image = bullet_img
        else:
            self.image = pygame.Surface((5, 10))
            self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.radius = 3  # Collision radius
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# Explosion animation
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 40  # milliseconds, slightly faster animation
        
        # Try to load explosion animation frames
        self.explosion_anim = []
        try:
            for i in range(9):
                filename = f'explosion{i}.png'
                img = pygame.image.load(os.path.join(IMG_DIR, filename)).convert_alpha()
                img = pygame.transform.scale(img, (size, size))
                self.explosion_anim.append(img)
        except pygame.error:
            # If no animation frames found, use simple expanding circle animation
            for i in range(9):
                img = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(img, RED, (size//2, size//2), (i+1)*size//9)
                self.explosion_anim.append(img)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.explosion_anim):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.explosion_anim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# Star background effect
class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(1, 3)
        self.image = pygame.Surface((self.size, self.size))
        brightness = random.randint(180, 255)
        self.image.fill((brightness, brightness, brightness))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WINDOW_WIDTH)
        self.rect.y = random.randrange(WINDOW_HEIGHT)
        self.speedy = random.randrange(1, 3)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.x = random.randrange(WINDOW_WIDTH)
            self.rect.y = random.randrange(-50, -10)
            self.speedy = random.randrange(1, 3)

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
explosions = pygame.sprite.Group()
stars = pygame.sprite.Group()
player = Player()

all_sprites.add(player)

# Create background stars
if background_img is None:  # Only add stars if no background image
    for i in range(50):
        star = Star()
        stars.add(star)
        all_sprites.add(star)

# Spawn initial enemies
for i in range(6):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Game variables
score = 0
high_score = 0  # Added high score tracking
game_over = False
paused = False
clock = pygame.time.Clock()
difficulty = 1.0
boss_spawned = False
boss = None  # Reference to boss when spawned

def draw_health_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        color = GREEN
    elif pct > 0.3:
        color = YELLOW
    else:
        color = RED
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def spawn_enemy():
    enemy_type = random.random()
    if enemy_type < 0.6:
        enemy = Enemy()
    elif enemy_type < 0.8:
        enemy = FastEnemy()
    else:
        enemy = TankEnemy()
    enemy.speedy *= difficulty
    return enemy

def spawn_powerup(x, y):
    power_type = random.choice(["health", "power", "shield"])
    return PowerUp(x, y, power_type)

def show_game_over():
    game_over_text = font.render("GAME OVER! Press R to restart", True, WHITE)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
    
    screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//2 - 60))
    screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, WINDOW_HEIGHT//2))
    screen.blit(high_score_text, (WINDOW_WIDTH//2 - high_score_text.get_width()//2, WINDOW_HEIGHT//2 + 40))
    
    credit_text = small_font.render("Press ESC to quit", True, WHITE)
    screen.blit(credit_text, (WINDOW_WIDTH//2 - credit_text.get_width()//2, WINDOW_HEIGHT - 50))
    
    pygame.display.flip()

def show_pause_screen():
    pause_text = font.render("PAUSED", True, WHITE)
    resume_text = small_font.render("Press P to resume", True, WHITE)
    
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # Semi-transparent black
    screen.blit(overlay, (0, 0))
    
    screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
    screen.blit(resume_text, (WINDOW_WIDTH//2 - resume_text.get_width()//2, WINDOW_HEIGHT//2 + 10))
    
    pygame.display.flip()

# Start background music
try:
    pygame.mixer.music.play(loops=-1)  # Play the music in an infinite loop
except:
    pass

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_p:
                paused = not paused
                if paused:
                    try:
                        pygame.mixer.music.pause()
                    except:
                        pass
                else:
                    try:
                        pygame.mixer.music.unpause()
                    except:
                        pass
            elif event.key == pygame.K_SPACE and not game_over and not paused:
                new_bullets = player.shoot()
                for bullet in new_bullets:
                    all_sprites.add(bullet)
                    bullets.add(bullet)
            elif event.key == pygame.K_r and game_over:
                # Reset game
                game_over = False
                score = 0
                difficulty = 1.0
                player.health = player.max_health
                player.power_level = 1
                player.invulnerable = False
                player.rect.centerx = WINDOW_WIDTH // 2
                player.rect.bottom = WINDOW_HEIGHT - 10
                # Clear and respawn enemies
                for sprite in all_sprites:
                    if sprite != player and not isinstance(sprite, Star):
                        sprite.kill()
                for i in range(6):
                    enemy = spawn_enemy()
                    all_sprites.add(enemy)
                    enemies.add(enemy)
                boss_spawned = False
                boss = None
                # Restart background music
                try:
                    pygame.mixer.music.play(loops=-1)
                except:
                    pass

    if paused:
        show_pause_screen()
        clock.tick(5)  # Reduce CPU usage while paused
        continue

    if not game_over:
        # Update
        all_sprites.update()

        # Increase difficulty over time
        difficulty += DIFFICULTY_INCREASE_RATE * (1/60)  # 60 FPS
        difficulty = min(difficulty, 2.5)  # Cap difficulty

        # Spawn boss at certain score
        if score >= BOSS_SPAWN_SCORE and not boss_spawned:
            boss = BossEnemy()
            all_sprites.add(boss)
            enemies.add(boss)
            boss_spawned = True

        # Handle boss shooting
        if boss_spawned and boss and boss.rect.top > 0:
            enemy_shots = boss.shoot()
            for bullet in enemy_shots:
                all_sprites.add(bullet)
                enemy_bullets.add(bullet)

        # Check for bullet-enemy collisions (using better circle collision)
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True, pygame.sprite.collide_circle)
        for enemy, bullet_list in hits.items():
            enemy.health -= len(bullet_list)
            if enemy.health <= 0:
                score += enemy.points
                if score > high_score:
                    high_score = score
                if explosion_sound:
                    explosion_sound.play()
                # Create explosion
                explosion = Explosion(enemy.rect.center, max(30, enemy.rect.width))
                all_sprites.add(explosion)
                explosions.add(explosion)
                # Chance to spawn power-up
                if random.random() < POWERUP_CHANCE:
                    powerup = spawn_powerup(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(powerup)
                    powerups.add(powerup)
                
                if isinstance(enemy, BossEnemy):
                    boss_spawned = False
                    boss = None
                
                enemy.kill()
                if not boss_spawned:
                    new_enemy = spawn_enemy()
                    all_sprites.add(new_enemy)
                    enemies.add(new_enemy)

        # Check for player-enemy collisions (using better circle collision)
        if not player.invulnerable:
            hits = pygame.sprite.spritecollide(player, enemies, False, pygame.sprite.collide_circle)
            if hits:
                player.take_damage()
                if player.health <= 0:
                    if game_over_sound:
                        game_over_sound.play()
                    # Stop background music
                    pygame.mixer.music.stop()
                    game_over = True
                    # Create player explosion
                    explosion = Explosion(player.rect.center, 50)
                    all_sprites.add(explosion)
                    explosions.add(explosion)
        
        # Check for player-enemy bullet collisions
        if not player.invulnerable:
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_circle)
            if hits:
                player.take_damage(len(hits))
                if player.health <= 0:
                    if game_over_sound:
                        game_over_sound.play()
                    # Stop background music
                    pygame.mixer.music.stop()
                    game_over = True
                    # Create player explosion
                    explosion = Explosion(player.rect.center, 50)
                    all_sprites.add(explosion)
                    explosions.add(explosion)

        # Check for power-up collisions
        hits = pygame.sprite.spritecollide(player, powerups, True, pygame.sprite.collide_circle)
        for powerup in hits:
            if powerup_sound:
                powerup_sound.play()
            if powerup.power_type == "health":
                player.health = min(player.max_health, player.health + 20)
            elif powerup.power_type == "power":
                player.power_level = min(3, player.power_level + 1)
            elif powerup.power_type == "shield":
                player.invulnerable = True
                player.invulnerable_timer = pygame.time.get_ticks()

        # Draw
        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(BLACK)
            all_sprites.draw(screen)
        
        # Always draw all sprites if using stars with background
        if background_img:
            all_sprites.draw(screen)
        
        # Draw UI elements
        score_text = font.render(f"Score: {score}", True, WHITE)
        high_score_text = small_font.render(f"High Score: {high_score}", True, YELLOW)
        power_text = font.render(f"Power: {player.power_level}", True, WHITE)
        fps_text = small_font.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 40))
        draw_health_bar(screen, 10, 70, player.health)
        screen.blit(power_text, (10, 90))
        screen.blit(fps_text, (WINDOW_WIDTH - 80, 10))
        
        # Draw boss health if boss exists
        if boss_spawned and boss:
            boss_health_pct = boss.health / 25.0 * 100
            boss_text = small_font.render("BOSS", True, YELLOW)
            screen.blit(boss_text, (WINDOW_WIDTH//2 - boss_text.get_width()//2, 10))
            draw_health_bar(screen, WINDOW_WIDTH//2 - 50, 30, boss_health_pct)
        
        # Draw invulnerability indicator
        if player.invulnerable:
            shield_text = font.render("SHIELD ACTIVE!", True, YELLOW)
            # Draw remaining shield time
            remaining = max(0, (player.invulnerable_timer + player.invulnerable_duration - pygame.time.get_ticks()) / 1000)
            time_text = small_font.render(f"{remaining:.1f}s", True, YELLOW)
            screen.blit(shield_text, (WINDOW_WIDTH - 200, 10))
            screen.blit(time_text, (WINDOW_WIDTH - 200, 40))
        
        # Draw controls hint for new players
        if score < 50:
            hint_text = small_font.render("← → to move, SPACE to shoot, P to pause", True, WHITE)
            screen.blit(hint_text, (WINDOW_WIDTH//2 - hint_text.get_width()//2, WINDOW_HEIGHT - 30))
        
        pygame.display.flip()
    else:
        show_game_over()

    # Cap the framerate
    clock.tick(60)

pygame.quit()
sys.exit()
