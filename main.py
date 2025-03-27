import pygame
import random
import sys
import math
import os
import time
from game_logger import logger, log_error, log_info, log_game_event, log_performance
from game_exceptions import *

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
        self.radius = 20
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = WINDOW_HEIGHT - 10
        
        # Base stats from config
        self.speed = GAME_BALANCE['player']['base_speed']
        self.health = GAME_BALANCE['player']['base_health']
        self.max_health = GAME_BALANCE['player']['base_health']
        self.power_level = 1
        self.shoot_delay = GAME_BALANCE['player']['base_shoot_delay']
        self.last_shot = 0
        
        # Power-up effects
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = POWERUP_TYPES['shield']['duration']
        self.rapid_fire_end = 0
        self.points_multiplier = 1
        self.double_points_end = 0
        
        # Visual effects
        self.animation_tick = 0
        self.hit = False
        self.hit_time = 0
        self.hit_duration = VISUAL_SETTINGS['damage_flash_duration']

    def update(self):
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
            self.rect.x += self.speed
        
        current_time = pygame.time.get_ticks()
        
        # Update power-up effects
        if self.rapid_fire_end and current_time > self.rapid_fire_end:
            self.shoot_delay = GAME_BALANCE['player']['base_shoot_delay']
            self.rapid_fire_end = 0
            log_game_event("PowerUp", "Rapid fire ended")
            
        if self.double_points_end and current_time > self.double_points_end:
            self.points_multiplier = 1
            self.double_points_end = 0
            log_game_event("PowerUp", "Double points ended")
        
        # Update damage flash
        if self.hit:
            if current_time - self.hit_time > self.hit_duration:
                self.hit = False
                self.image = self.original_image.copy()
        
        # Update invulnerability
        if self.invulnerable:
            self.animation_tick += 1
            if self.animation_tick % VISUAL_SETTINGS['shield_blink_rate'] == 0:
                if not self.hit:
                    if self.image.get_alpha() == 255 or self.image.get_alpha() is None:
                        self.image.set_alpha(128)
                    else:
                        self.image.set_alpha(255)
            
            if current_time - self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable = False
                self.image = self.original_image.copy()
                self.image.set_alpha(255)
                log_game_event("PowerUp", "Shield deactivated")

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            if shoot_sound:
                shoot_sound.play()
            
            bullets = []
            if self.power_level == 1:
                bullets.append(Bullet(self.rect.centerx, self.rect.top))
            elif self.power_level == 2:
                bullets.extend([
                    Bullet(self.rect.left + 10, self.rect.top),
                    Bullet(self.rect.right - 10, self.rect.top)
                ])
            else:  # power_level == 3
                bullets.extend([
                    Bullet(self.rect.centerx, self.rect.top),
                    Bullet(self.rect.left + 10, self.rect.top),
                    Bullet(self.rect.right - 10, self.rect.top)
                ])
            
            log_game_event("Shooting", f"Fired {len(bullets)} bullets")
            return bullets
        return []
    
    def take_damage(self, amount=1):
        if not self.invulnerable:
            self.health -= amount
            self.hit = True
            self.hit_time = pygame.time.get_ticks()
            temp_img = self.original_image.copy()
            temp_img.fill(RED, special_flags=pygame.BLEND_RGB_ADD)
            self.image = temp_img
            log_game_event("Damage", f"Player took {amount} damage. Health: {self.health}")

# Enemy base class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type='regular', difficulty=1.0):
        super().__init__()
        self.enemy_type = enemy_type
        self.config = ENEMY_TYPES[enemy_type]
        
        # Load appropriate image
        if enemy_type == 'regular' and enemy_img:
            self.image = enemy_img
        elif enemy_type == 'fast' and fast_enemy_img:
            self.image = fast_enemy_img
        elif enemy_type == 'tank' and tank_enemy_img:
            self.image = tank_enemy_img
        elif enemy_type == 'boss' and boss_enemy_img:
            self.image = boss_enemy_img
        else:
            self.image = pygame.Surface((30, 30))
            self.image.fill(self.config['color'])
        
        self.rect = self.image.get_rect()
        self.radius = 15
        
        # Apply difficulty scaling
        self.health = int(self.config['health'] * (1 + (difficulty - 1) * DIFFICULTY_SCALING['enemy_health']['increase_rate']))
        self.max_health = self.health
        self.speedy = self.config['speed'] * (1 + (difficulty - 1) * DIFFICULTY_SCALING['enemy_speed']['increase_rate'])
        self.speedx = 0
        self.points = self.config['points']
        
        # Position
        self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        
        # Boss-specific attributes
        if enemy_type == 'boss':
            self.rect.centerx = WINDOW_WIDTH // 2
            self.rect.y = -80
            self.speedx = 2
            self.movement_pattern = 0
            self.movement_timer = 0
            self.last_shot = pygame.time.get_ticks()
            self.shoot_delay = 2000
            log_game_event("Enemy", "Boss spawned")

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        # Bouncing off edges logic
        if self.rect.left < 0 and self.speedx < 0:
            self.speedx = -self.speedx
        if self.rect.right > WINDOW_WIDTH and self.speedx > 0:
            self.speedx = -self.speedx
            
        # Reset position when off screen
        if self.rect.top > WINDOW_HEIGHT:
            self.reset_position()
            
        # Boss-specific movement
        if self.enemy_type == 'boss':
            self.update_boss_movement()

    def reset_position(self):
        """Reset enemy position when it goes off screen."""
        self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        if self.enemy_type == 'fast':
            self.speedx = random.choice([-2, -1, 0, 1, 2])

    def update_boss_movement(self):
        """Update boss-specific movement patterns."""
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

        # Keep boss within bounds
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

    def take_damage(self, amount):
        """Handle enemy taking damage."""
        self.health -= amount
        if self.health <= 0:
            log_game_event("Enemy", f"{self.enemy_type} enemy destroyed")
            return True
        return False

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
        self.config = POWERUP_TYPES[power_type]
        
        try:
            self.image = pygame.image.load(os.path.join(IMG_DIR, f"{power_type}_powerup.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (20, 20))
        except pygame.error:
            self.image = pygame.Surface((20, 20))
            self.image.fill(self.config['color'])
        
        self.rect = self.image.get_rect()
        self.radius = 10  # Collision radius
        self.rect.centerx = x
        self.rect.centery = y
        self.speedy = 2
        
        # Wobble effect
        self.wobble = 0
        self.wobble_dir = 1
        self.wobble_speed = random.randint(1, 3) * VISUAL_SETTINGS['powerup_wobble_speed']
        
        # Duration for temporary power-ups
        self.duration = self.config['duration']
        self.active = False
        self.start_time = 0

    def update(self):
        self.rect.y += self.speedy
        # Wobble effect
        self.wobble += self.wobble_speed * self.wobble_dir
        if abs(self.wobble) > 1.5:
            self.wobble_dir *= -1
        self.rect.x += self.wobble_dir * self.wobble_speed
        
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

    def apply_effect(self, player):
        """Apply the power-up effect to the player."""
        if self.power_type == 'health':
            player.health = min(player.max_health, player.health + self.config['heal_amount'])
            log_game_event("PowerUp", f"Health restored: {self.config['heal_amount']}")
            
        elif self.power_type == 'power':
            player.power_level = min(GAME_BALANCE['player']['max_power_level'], 
                                  player.power_level + self.config['power_increase'])
            log_game_event("PowerUp", f"Power level increased to: {player.power_level}")
            
        elif self.power_type == 'shield':
            player.invulnerable = True
            player.invulnerable_timer = pygame.time.get_ticks()
            player.invulnerable_duration = self.config['duration']
            log_game_event("PowerUp", "Shield activated")
            
        elif self.power_type == 'rapid_fire':
            player.shoot_delay = GAME_BALANCE['player']['base_shoot_delay'] / self.config['fire_rate_multiplier']
            player.rapid_fire_end = pygame.time.get_ticks() + self.config['duration']
            log_game_event("PowerUp", "Rapid fire activated")
            
        elif self.power_type == 'double_points':
            player.points_multiplier = self.config['points_multiplier']
            player.double_points_end = pygame.time.get_ticks() + self.config['duration']
            log_game_event("PowerUp", "Double points activated")

    def is_active(self):
        """Check if the power-up is still active."""
        if not self.active or self.duration == 0:
            return False
        return pygame.time.get_ticks() - self.start_time < self.duration

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

class Game:
    def __init__(self):
        try:
            pygame.init()
            pygame.mixer.init()
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Space Shooter")
            self.clock = pygame.time.Clock()
            self.running = True
            self.paused = False
            self.load_assets()
            log_info("Game initialized successfully")
        except pygame.error as e:
            log_error(e, "Failed to initialize pygame")
            raise GameError("Failed to initialize game") from e
        except Exception as e:
            log_error(e, "Unexpected error during game initialization")
            raise

    def load_assets(self):
        """Load game assets with error handling."""
        try:
            start_time = time.time()
            # Load images
            self.background = self.load_image('assets/images/background.png')
            self.player_img = self.load_image('assets/images/player.png')
            self.bullet_img = self.load_image('assets/images/bullet.png')
            self.enemy_img = self.load_image('assets/images/enemy.png')
            
            # Load sounds
            self.shoot_sound = self.load_sound('assets/sounds/shoot.wav')
            self.explosion_sound = self.load_sound('assets/sounds/explosion.wav')
            
            load_time = time.time() - start_time
            log_performance("Asset Loading", load_time)
            log_info("All assets loaded successfully")
        except AssetLoadError as e:
            log_error(e, "Failed to load game assets")
            raise
        except Exception as e:
            log_error(e, "Unexpected error loading assets")
            raise

    def load_image(self, path):
        """Load an image with error handling."""
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            raise AssetLoadError(f"Failed to load image: {path}") from e
        except FileNotFoundError as e:
            raise AssetLoadError(f"Image file not found: {path}") from e

    def load_sound(self, path):
        """Load a sound with error handling."""
        try:
            return pygame.mixer.Sound(path)
        except pygame.error as e:
            raise AudioError(f"Failed to load sound: {path}") from e
        except FileNotFoundError as e:
            raise AudioError(f"Sound file not found: {path}") from e

    def handle_input(self):
        """Handle user input with error handling."""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    log_info("Game quit by user")
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                        log_game_event("Game State", "Paused" if self.paused else "Unpaused")
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        log_info("Game quit using ESC key")
        except Exception as e:
            log_error(e, "Error handling input")
            raise InputError("Failed to process user input") from e

    def update(self):
        """Update game state with error handling."""
        try:
            if not self.paused:
                start_time = time.time()
                
                # Update game objects
                self.player.update()
                self.enemies.update()
                self.bullets.update()
                self.powerups.update()
                
                # Check collisions
                self.check_collisions()
                
                update_time = time.time() - start_time
                log_performance("Game Update", update_time)
        except Exception as e:
            log_error(e, "Error updating game state")
            raise GameStateError("Failed to update game state") from e

    def check_collisions(self):
        """Check collisions with error handling."""
        try:
            # Bullet-enemy collisions
            for bullet in self.bullets:
                hits = pygame.sprite.spritecollide(bullet, self.enemies, True, pygame.sprite.collide_circle)
                for hit in hits:
                    self.score += 10
                    self.explosion_sound.play()
                    log_game_event("Collision", f"Enemy destroyed at position {hit.rect.center}")

            # Player-enemy collisions
            hits = pygame.sprite.spritecollide(self.player, self.enemies, True, pygame.sprite.collide_circle)
            for hit in hits:
                self.player.health -= 10
                self.explosion_sound.play()
                log_game_event("Collision", f"Player hit by enemy. Health: {self.player.health}")
                
        except Exception as e:
            log_error(e, "Error checking collisions")
            raise CollisionError("Failed to check collisions") from e

    def render(self):
        """Render game state with error handling."""
        try:
            start_time = time.time()
            
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.background, (0, 0))
            
            self.all_sprites.draw(self.screen)
            self.draw_ui()
            
            pygame.display.flip()
            
            render_time = time.time() - start_time
            log_performance("Game Render", render_time)
        except Exception as e:
            log_error(e, "Error rendering game state")
            raise RenderError("Failed to render game state") from e

    def run(self):
        """Main game loop with error handling."""
        try:
            log_info("Starting game loop")
            while self.running:
                self.clock.tick(60)
                self.handle_input()
                self.update()
                self.render()
            
            log_info("Game loop ended normally")
        except GameError as e:
            log_error(e, "Game error occurred")
            self.handle_game_error(e)
        except Exception as e:
            log_error(e, "Unexpected error in game loop")
            self.handle_game_error(e)
        finally:
            self.cleanup()

    def handle_game_error(self, error):
        """Handle game errors gracefully."""
        try:
            # Display error message to user
            self.show_error_screen(str(error))
            # Wait for user acknowledgment
            self.wait_for_key()
        except Exception as e:
            log_error(e, "Error handling game error")

    def cleanup(self):
        """Clean up resources."""
        try:
            pygame.quit()
            log_info("Game cleaned up successfully")
        except Exception as e:
            log_error(e, "Error during cleanup")

    def show_error_screen(self, message):
        """Display error message to user."""
        try:
            self.screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 36)
            text = font.render(f"An error occurred: {message}", True, (255, 0, 0))
            text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            self.screen.blit(text, text_rect)
            pygame.display.flip()
        except Exception as e:
            log_error(e, "Error displaying error screen")

    def wait_for_key(self):
        """Wait for user to press a key."""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYUP:
                    waiting = False

game = Game()
game.run()
