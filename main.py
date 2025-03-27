import pygame
import random
import sys
import math
import os
import time
from collections import defaultdict
from game_renderer import GameRenderer
from performance_monitor import PerformanceMonitor
from sprite_manager import SpriteManager
from collision_system import CollisionSystem
from game_logger import logger, log_error, log_info, log_warning, log_game_event, log_performance, log_debug
from game_exceptions import *
from game_config import *
from version import VERSION, VERSION_NAME

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
    """
    Player spaceship class with health, weapon power levels, and power-up effects.
    Uses circle-based collision detection for more accurate hit detection.
    """
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
        # The radius attribute is used for circular collision detection
        # This provides more accurate and efficient collision checking
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
        """
        Apply damage to the player and trigger visual feedback.
        
        Args:
            amount (int): Amount of damage to apply
            
        Returns:
            bool: True if the player is still alive, False if dead
        """
        if not self.invulnerable:
            self.health -= amount
            self.hit = True
            self.hit_time = pygame.time.get_ticks()
            temp_img = self.original_image.copy()
            temp_img.fill(RED, special_flags=pygame.BLEND_RGB_ADD)
            self.image = temp_img
            log_game_event("Damage", f"Player took {amount} damage. Health: {self.health}")
            return self.health > 0
        return True

# Enemy base class
class Enemy(pygame.sprite.Sprite):
    """
    Base enemy class that other enemy types inherit from.
    Uses circle-based collision detection and adapts to difficulty level.
    """
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
        """
        Update enemy position and check screen boundaries.
        Enemies move from top to bottom with type-specific behaviors.
        """
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
        """
        Reset enemy to a new random position at the top of the screen.
        Used for reusing enemy objects rather than creating new ones.
        """
        self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        if self.enemy_type == 'fast':
            self.speedx = random.choice([-2, -1, 0, 1, 2])

    def update_boss_movement(self):
        """
        Special movement pattern for boss enemies.
        Bosses use a sine wave pattern for horizontal movement.
        """
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
        """
        Handle enemy taking damage and return if the enemy was destroyed.
        
        Args:
            amount (int): Amount of damage to apply
            
        Returns:
            bool: True if the enemy was destroyed, False otherwise
        """
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
    """
    Power-up item that can be collected by the player.
    Uses oscillating movement and provides various effects.
    """
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
        """
        Update power-up position and wobble animation.
        Power-ups move downward and have a slight horizontal oscillation.
        """
        self.rect.y += self.speedy
        # Wobble effect
        self.wobble += self.wobble_speed * self.wobble_dir
        if abs(self.wobble) > 1.5:
            self.wobble_dir *= -1
        self.rect.x += self.wobble_dir * self.wobble_speed
        
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

    def apply_effect(self, player):
        """
        Apply power-up effect to the player based on type.
        
        Args:
            player (Player): The player sprite to apply the effect to
        """
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
        """
        Check if the power-up is still active or should be removed.
        
        Returns:
            bool: True if the power-up is still active, False otherwise
        """
        if not self.active or self.duration == 0:
            return False
        return pygame.time.get_ticks() - self.start_time < self.duration

# Bullet
class Bullet(pygame.sprite.Sprite):
    """
    Player bullet sprite.
    Travels upward from the player's position.
    """
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
        """
        Update bullet position and check if it's off-screen.
        """
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# Explosion animation
class Explosion(pygame.sprite.Sprite):
    """
    Explosion animation sprite.
    Creates a temporary animated explosion effect.
    """
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
        """
        Update explosion animation frame.
        Removes the explosion when animation is complete.
        """
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
    """
    Background star sprite for when no background image is available.
    Stars have different sizes and speeds for parallax effect.
    """
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
        """
        Update star position and handle wrapping when reaching screen bottom.
        """
        self.rect.y += self.speedy
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.x = random.randrange(WINDOW_WIDTH)
            self.rect.y = random.randrange(-50, -10)
            self.speedy = random.randrange(1, 3)

# Start background music
#try:
#    pygame.mixer.music.play(loops=-1)  # Play the music in an infinite loop
#except:
#    pass

class Game:
    """
    Main game class that handles the game loop, rendering, and input.
    Implements performance optimization through the GameRenderer,
    SpriteManager, and PerformanceMonitor.
    """
    def __init__(self):
        try:
            pygame.init()
            pygame.mixer.init()
            
            # Initialize performance monitoring first
            self.perf_monitor = PerformanceMonitor(sample_size=120)
            self.perf_monitor.terminal_reporting_enabled = True  # Enable terminal FPS reporting
            
            # Game state initialization
            self.running = True
            self.paused = False
            self.game_over = False
            self.score = 0
            self.high_score = 0
            self.difficulty = 1.0
            self.last_enemy_spawn = 0
            self.last_boss_spawn = 0
            self.show_fps = True  # Show FPS by default
            self.boss_spawned = False
            
            # Screen dimensions
            self.screen_width = WINDOW_WIDTH
            self.screen_height = WINDOW_HEIGHT
            
            # Initialize game systems with optimizations
            self.renderer = GameRenderer(WINDOW_WIDTH, WINDOW_HEIGHT, BLACK, self.perf_monitor)
            self.collision_system = CollisionSystem(WINDOW_WIDTH, WINDOW_HEIGHT, 75, self.perf_monitor)
            self.sprite_manager = SpriteManager(WINDOW_WIDTH, WINDOW_HEIGHT)
            self.clock = pygame.time.Clock()
            self.screen = self.renderer.get_screen()
            
            # Initialize player
            self.player = Player()
            
            # Add player to sprite manager
            self.sprite_manager.add_sprite(self.player, 'player')
            
            # Register player as a special entity (always checked for collisions)
            self.collision_system.register_static_object(self.player)
            
            # Load game assets
            self.load_assets()
            
            # Create background stars if no background image
            if background_img is None:
                for i in range(50):
                    star = Star()
                    self.sprite_manager.add_sprite(star, 'background')
            
            # Spawn initial enemies
            for i in range(6):
                enemy = self.spawn_enemy()
                self.sprite_manager.add_sprite(enemy, 'enemy')
                
            log_info("Game initialized successfully")
        except pygame.error as e:
            log_error(e, "Failed to initialize pygame")
            raise GameError("Failed to initialize game") from e
        except Exception as e:
            log_error(e, "Unexpected error during game initialization")
            raise

    def load_assets(self):
        """
        Load all game assets (images, sounds).
        Handles fallbacks for missing assets.
        """
        try:
            self.perf_monitor.start_section("loading")
            start_time = time.time()
            
            log_info("Loading game assets...")
            
            # Load background image
            if background_img:
                # Set background directly using background_img since it's already loaded
                self.renderer.set_background_image(background_img)
            else:
                # Just set a background color if no image
                log_warning("Background image not found. Using black background.")
            
            # Cache commonly used game images
            if player_img:
                self.renderer.add_to_cache("player", player_img)
            if enemy_img:
                self.renderer.add_to_cache("enemy", enemy_img)
            if bullet_img:
                self.renderer.add_to_cache("bullet", bullet_img)
            
            load_time = time.time() - start_time
            log_performance("Asset Loading", load_time)
            self.perf_monitor.end_section("loading")
            log_info("All assets loaded successfully")
        except Exception as e:
            log_error(e, "Failed to load game assets")
            raise AssetLoadError("Failed to load game assets") from e

    def load_image(self, filename):
        """
        Load an image asset with error handling.
        
        Args:
            filename (str): Image filename
            
        Returns:
            Surface: Loaded image or None if failed
        """
        try:
            filepath = os.path.join(IMG_DIR, filename)
            return pygame.image.load(filepath).convert_alpha()
        except pygame.error as e:
            log_warning(f"Could not load image: {filename}")
            return None
        except FileNotFoundError as e:
            log_warning(f"Image file not found: {filename}")
            return None

    def load_sound(self, filename):
        """
        Load a sound asset with error handling.
        
        Args:
            filename (str): Sound filename
            
        Returns:
            Sound: Loaded sound or None if failed
        """
        try:
            filepath = os.path.join(SOUND_DIR, filename)
            return pygame.mixer.Sound(filepath)
        except pygame.error:
            log_warning(f"Could not load sound: {filename}")
            return None
        except FileNotFoundError:
            log_warning(f"Sound file not found: {filename}")
            return None

    def handle_input(self):
        """
        Process user input events.
        Handles key presses and game state changes.
        """
        try:
            # Start timing input handling
            self.perf_monitor.start_section("input")
            
            for event in pygame.event.get():
                # Quit event
                if event.type == pygame.QUIT:
                    self.running = False
                    log_info("Game quit by user")
                
                # Key down events
                elif event.type == pygame.KEYDOWN:
                    # Pause toggle (P key)
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                        log_game_event("Game State", "Paused" if self.paused else "Unpaused")
                    
                    # Performance monitor toggle (M key)
                    elif event.key == pygame.K_m:
                        self.perf_monitor.toggle_display()
                        self.renderer.force_full_redraw()
                        log_game_event("Display", "Performance monitor toggled")

                    # Toggle FPS display (F key)
                    elif event.key == pygame.K_f:
                        self.show_fps = not self.show_fps
                        log_game_event("Display", f"FPS display {'enabled' if self.show_fps else 'disabled'}")
                        
                    # Toggle terminal FPS reporting (T key)
                    elif event.key == pygame.K_t:
                        enabled = self.perf_monitor.toggle_terminal_reporting()
                        log_game_event("Display", f"Terminal FPS reporting {'enabled' if enabled else 'disabled'}")
                    
                    # Toggle debug visualization (D key)
                    elif event.key == pygame.K_d:
                        if not hasattr(self, 'debug_mode'):
                            self.debug_mode = True
                        else:
                            self.debug_mode = not self.debug_mode
                        self.collision_system.toggle_debug()
                        log_game_event("Display", f"Debug visualization {'enabled' if self.debug_mode else 'disabled'}")
                        
                    # Toggle dirty rectangles visualization (R key)
                    elif event.key == pygame.K_r and not self.game_over:
                        self.renderer.toggle_dirty_rects_display()
                        log_game_event("Display", "Dirty rectangles visualization toggled")
                    
                    # Force full redraw of screen (C key)
                    elif event.key == pygame.K_c:
                        self.renderer.force_full_redraw()
                        log_game_event("Renderer", "Forced full redraw")
                    
                    # Exit game (ESC key)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        log_info("Game quit using ESC key")
                    
                    # Restart game if game over (R key)
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                        log_game_event("Game State", "Game restarted")
            
            # End timing input handling
            self.perf_monitor.end_section("input")
        except Exception as e:
            log_error(e, "Error handling input")
            raise InputError("Failed to process user input") from e
            
    def reset_game(self):
        """
        Reset the game state for a new game.
        """
        log_info("Resetting game state")
        # Reset game state
        self.score = 0
        self.game_over = False
        self.difficulty = 1.0
        self.boss_spawned = False
        
        # Clear collision system
        self.collision_system.clear()
        self.collision_system.cached_cells.clear()
        
        # Clear all sprites except player
        self.sprite_manager.clear_all_except_player()
        
        # Reset player
        self.player.rect.centerx = WINDOW_WIDTH // 2
        self.player.rect.bottom = WINDOW_HEIGHT - 10
        self.player.health = self.player.max_health
        self.player.power_level = 1
        self.player.invulnerable = False
        
        # Register player again
        self.collision_system.register_static_object(self.player)
        
        # Create initial enemies
        for i in range(6):
            enemy = self.spawn_enemy()
            self.sprite_manager.add_sprite(enemy, 'enemy')
        
        # Force full redraw
        self.renderer.force_full_redraw()

    def update(self):
        """
        Update game state, including sprites and collisions.
        Implements performance monitoring for optimization.
        """
        try:
            if not self.paused:
                self.perf_monitor.start_section("update")
                start_time = time.time()
                
                # Update game difficulty
                self.difficulty = min(
                    GAME_BALANCE['max_difficulty'],
                    1.0 + (self.score / 1000) * GAME_BALANCE['difficulty_increase_rate']
                )
                
                # Clear the collision system for new frame
                self.collision_system.clear()
                
                # Update all sprites
                all_sprites = self.sprite_manager.get_all_sprites()
                for sprite in all_sprites:
                    sprite.update()
                
                # Update collision system with current sprite positions
                for sprite in self.sprite_manager.bullets:
                    self.collision_system.add_object(sprite, 'bullet')
                
                for sprite in self.sprite_manager.enemies:
                    self.collision_system.add_object(sprite, 'enemy')
                
                for sprite in self.sprite_manager.powerups:
                    self.collision_system.add_object(sprite, 'powerup')
                    
                for sprite in self.sprite_manager.enemy_bullets:
                    self.collision_system.add_object(sprite, 'enemy_bullet')
                
                # Always add player
                self.collision_system.add_object(self.player, 'player')
                
                # Run collision detection using optimized system
                self.check_collisions()
                
                # Periodic cleanup of collision system cache
                self.collision_system.cleanup_cached_data()
                
                # Every 1000 frames, try to optimize collision grid
                if self.perf_monitor.frame_count % 1000 == 0:
                    self.collision_system.optimize_partitioning()
                
                update_time = time.time() - start_time
                log_performance("Game Update", update_time)
                self.perf_monitor.end_section("update")
        except Exception as e:
            log_error(e, "Error updating game state")
            raise GameStateError("Failed to update game state") from e

    def check_collisions(self):
        """
        Check for collisions between game objects.
        Uses the optimized collision system for better performance.
        """
        try:
            self.perf_monitor.start_section("collision")
            
            # Process bullet-enemy collisions (high priority)
            def bullet_enemy_callback(bullet, enemy):
                # Apply damage to enemy
                if enemy.take_damage(1):
                    # Enemy was destroyed
                    score_value = ENEMY_TYPES[enemy.enemy_type]['points']
                    # Apply score multiplier if active
                    if self.player.points_multiplier > 1:
                        score_value *= self.player.points_multiplier
                    self.score += score_value
                    
                    # Update high score if needed
                    if self.score > self.high_score:
                        self.high_score = self.score
                    
                    # Chance to spawn power-up at enemy position
                    if random.random() < POWERUP_CHANCE:
                        powerup = self.spawn_powerup(enemy.rect.centerx, enemy.rect.centery)
                        self.sprite_manager.add_sprite(powerup, 'powerup')
                        
                    # Create explosion at enemy position
                    self.create_explosion(enemy.rect.center, size="lg")
                    
                    # Remove destroyed enemy
                    self.sprite_manager.remove_sprite(enemy)
                
                # Always remove bullet that hit enemy
                self.sprite_manager.remove_sprite(bullet)
            
            # Check bullet-enemy collisions
            self.collision_system.check_collisions(
                self.sprite_manager.bullets, 
                'enemy', 
                bullet_enemy_callback,
                use_distance=True,
                priority="high"
            )
            
            # Process player-enemy collisions (high priority)
            def player_enemy_callback(player, enemy):
                if not player.invulnerable:
                    # Player takes damage
                    if not player.take_damage():
                        # Player was destroyed
                        self.game_over = True
                        # Update high score if needed
                        if self.score > self.high_score:
                            self.high_score = self.score
                        self.create_explosion(player.rect.center, size="xl")
                        if game_over_sound:
                            game_over_sound.play()
                    else:
                        # Player was damaged but survived
                        if explosion_sound:
                            explosion_sound.play()
                
                # Enemy is destroyed on collision
                self.sprite_manager.remove_sprite(enemy)
                self.create_explosion(enemy.rect.center, size="lg")
            
            # Check player-enemy collisions
            self.collision_system.check_collisions(
                [self.player], 
                'enemy', 
                player_enemy_callback,
                use_distance=True,
                priority="high"
            )
            
            # Process player-powerup collisions (medium priority)
            def player_powerup_callback(player, powerup):
                powerup.apply_effect(player)
                self.sprite_manager.remove_sprite(powerup)
                if powerup_sound:
                    powerup_sound.play()
            
            # Check player-powerup collisions
            self.collision_system.check_collisions(
                [self.player], 
                'powerup', 
                player_powerup_callback,
                use_distance=True,
                priority="medium"
            )
            
            # Process player-enemy bullet collisions (high priority)
            def player_enemy_bullet_callback(player, bullet):
                if not player.invulnerable:
                    # Player takes damage
                    if not player.take_damage():
                        # Player was destroyed
                        self.game_over = True
                        # Update high score if needed
                        if self.score > self.high_score:
                            self.high_score = self.score
                        self.create_explosion(player.rect.center, size="xl")
                        if game_over_sound:
                            game_over_sound.play()
                    else:
                        # Player was damaged but survived
                        if explosion_sound:
                            explosion_sound.play()
                
                # Always remove the enemy bullet
                self.sprite_manager.remove_sprite(bullet)
            
            # Check player-enemy bullet collisions
            self.collision_system.check_collisions(
                [self.player], 
                'enemy_bullet', 
                player_enemy_bullet_callback,
                use_distance=True,
                priority="high"
            )
            
            self.perf_monitor.end_section("collision")
        except Exception as e:
            log_error(e, "Error checking collisions")
            raise CollisionError("Failed to check collisions") from e

    def render(self):
        """
        Render the game using the optimized GameRenderer.
        Implements dirty rectangle rendering for optimized performance.
        """
        try:
            # Start timing for performance measurement
            start_time = time.time()
            
            # Get all sprites to render - this includes all sprites, not just visible ones
            all_sprites = []
            for group in self.sprite_manager.get_all_groups():
                all_sprites.extend(group.sprites())
            
            # Use the optimized renderer to draw sprites with dirty rectangle optimization
            visible_sprites = self.renderer.draw_sprites(all_sprites)
            
            # Draw UI elements (will be included in dirty rects by renderer)
            self.draw_ui()
            
            # Draw performance monitor if enabled
            if self.perf_monitor.display_enabled:
                self.perf_monitor.draw(self.screen)
            
            # Draw debugging visualizations if enabled
            if hasattr(self, 'debug_mode') and self.debug_mode:
                self.collision_system.draw_debug(self.screen)
            
            render_time = time.time() - start_time
            log_performance("Game Render", render_time)
        except Exception as e:
            log_error(e, "Error rendering game state")
            raise RenderError("Failed to render game state") from e
    
    def draw_ui(self):
        """
        Draw all UI elements like score, health bar, and game state overlays.
        """
        # Create a semi-transparent UI background for better readability
        ui_bg = pygame.Surface((self.screen_width, 120), pygame.SRCALPHA)
        ui_bg.fill((0, 0, 0, 100))  # Semi-transparent black
        self.screen.blit(ui_bg, (0, 0))
        # Make sure UI area is marked as dirty
        ui_rect = pygame.Rect(0, 0, self.screen_width, 120)
        self.renderer.dirty_rects.append(ui_rect)
        
        # Score - more prominent
        self.renderer.draw_text(f"Score: {self.score}", 10, 10, (255, 255, 255), font)
        
        # High score
        self.renderer.draw_text(f"High Score: {self.high_score}", 10, 50, (255, 255, 255), small_font)
        
        # Draw health bar - larger and more visible
        self.draw_health_bar(self.renderer.screen, 10, 80, self.player.health / self.player.max_health)
        
        # Shield timer if active
        if self.player.invulnerable:
            shield_pct = (pygame.time.get_ticks() - self.player.invulnerable_timer) / self.player.invulnerable_duration
            self.renderer.draw_text(f"Shield: {(1-shield_pct)*100:.0f}%", self.screen_width - 150, 10, (255, 255, 0), small_font)
        
        # FPS counter if enabled
        if self.show_fps:
            fps = self.perf_monitor.get_fps()
            self.renderer.draw_text(f"FPS: {fps:.1f}", self.screen_width - 100, 50, (0, 255, 0), small_font)
            
        # Version info - always show in bottom right
        version_text = f"v{VERSION}"
        self.renderer.draw_text(version_text, self.screen_width - 60, self.screen_height - 20, (150, 150, 150), small_font)
        
        # Game state screens
        if self.game_over:
            self.show_game_over()
            # Force full screen update for game over screen
            self.renderer.force_full_redraw()
        elif self.paused:
            self.show_pause_screen()
            # Force full screen update for pause screen
            self.renderer.force_full_redraw()

    def draw_health_bar(self, surf, x, y, pct):
        """
        Draw a health bar on the screen.
        
        Args:
            surf (Surface): Surface to draw on
            x (int): X position
            y (int): Y position
            pct (float): Percentage of health (0.0 to 1.0)
        """
        if pct < 0:
            pct = 0
        BAR_LENGTH = 200  # Increased from 100
        BAR_HEIGHT = 20   # Increased from 10
        fill = pct * BAR_LENGTH
        
        # Draw background/border for the health bar
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        pygame.draw.rect(surf, (50, 50, 50), outline_rect)  # Dark gray background
        
        # Draw the filled portion
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        
        # Color based on health percentage
        if pct > 0.6:
            color = (0, 255, 0)  # Green
        elif pct > 0.3:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red
            
        pygame.draw.rect(surf, color, fill_rect)
        pygame.draw.rect(surf, (255, 255, 255), outline_rect, 2)  # White border
        
        # Add health text
        health_text = small_font.render(f"Health: {int(pct * 100)}%", True, (255, 255, 255))
        text_pos = (x + 5, y + (BAR_HEIGHT - health_text.get_height()) // 2)
        surf.blit(health_text, text_pos)
        
        # Add this area to dirty rects to ensure it updates
        # Add a bit of padding to the health bar area to ensure complete rendering
        padded_rect = outline_rect.inflate(8, 8)
        self.renderer.dirty_rects.append(padded_rect)

    def run(self):
        """
        Main game loop.
        Handles timing, input, updates, and rendering with performance monitoring.
        """
        try:
            log_info("Starting game loop")
            
            # Play background music if available
            try:
                pygame.mixer.music.play(loops=-1)
            except:
                log_warning("Could not play background music")
            
            # Force an initial full redraw
            self.renderer.force_full_redraw()
            
            # Main game loop
            while self.running:
                # Start timing the frame
                self.perf_monitor.start_frame()
                
                # Handle input
                self.handle_input()
                
                # Skip updates if paused or game over
                if not self.paused and not self.game_over:
                    # Update game state
                    self.update()
                    
                    # Handle player shooting
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        new_bullets = self.player.shoot()
                        for bullet in new_bullets:
                            self.sprite_manager.add_sprite(bullet, 'bullet')
                    
                    # Spawn enemies based on time
                    current_time = pygame.time.get_ticks()
                    if current_time - self.last_enemy_spawn > 1000: # Spawn every 1 second
                        self.last_enemy_spawn = current_time
                        enemy = self.spawn_enemy()
                        self.sprite_manager.add_sprite(enemy, 'enemy')
                    
                    # Handle boss spawning
                    if not self.boss_spawned and self.score >= BOSS_SPAWN_SCORE:
                        boss = BossEnemy()
                        self.sprite_manager.add_sprite(boss, 'enemy')
                        self.boss_spawned = True
                        log_game_event("Boss", "Boss enemy spawned")
                
                # Render the game
                self.render()
                
                # End timing the frame
                self.perf_monitor.end_frame()
                
                # Limit the frame rate - but don't use clock.tick which blocks
                # Instead, just sleep for a tiny amount if we're ahead of schedule
                frame_time = time.time() - self.perf_monitor.frame_start_time
                if frame_time < 1/60:  # If we're running faster than 60 FPS
                    time.sleep(max(0, (1/60) - frame_time))
            
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
        """
        Handle game errors and exceptions.
        
        Args:
            error: The exception that was raised
        """
        try:
            # Display error message to user
            self.show_error_screen(str(error))
            # Wait for user acknowledgment
            self.wait_for_key()
        except Exception as e:
            log_error(e, "Error handling game error")

    def cleanup(self):
        """
        Clean up resources before exiting.
        """
        try:
            pygame.quit()
            log_info("Game cleaned up successfully")
        except Exception as e:
            log_error(e, "Error during cleanup")

    def show_error_screen(self, message):
        """
        Display error message on screen.
        
        Args:
            message (str): Error message to display
        """
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
        """
        Wait for any key press.
        
        Returns:
            bool: True if a key was pressed, False if the user quit
        """
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYUP:
                    waiting = False

    def create_explosion(self, center, size="lg"):
        """
        Create an explosion animation at the specified position.
        
        Args:
            center (tuple): Center position for the explosion (x, y)
            size (str): Size of the explosion ("sm", "lg", or "xl")
        """
        try:
            # Determine explosion size in pixels
            if size == "sm":
                explosion_size = 20
            elif size == "lg":
                explosion_size = 40
            elif size == "xl":
                explosion_size = 60
            else:
                explosion_size = 30
            
            # Create explosion sprite and add to sprite manager
            explosion = Explosion(center, explosion_size)
            self.sprite_manager.add_sprite(explosion, 'explosion')
            
            # Play explosion sound if available
            if explosion_sound:
                explosion_sound.play()
            
            log_game_event("Explosion", f"Created {size} explosion at {center}")
        except Exception as e:
            log_error(e, "Error creating explosion")

    def spawn_enemy(self):
        """
        Spawn a new enemy based on probability and return it.
        Handles enemy type selection based on ENEMY_TYPES configuration.
        
        Returns:
            Enemy: A new enemy sprite
        """
        enemy_type = random.random()
        if enemy_type < 0.6:
            enemy = Enemy()
        elif enemy_type < 0.8:
            enemy = FastEnemy()
        else:
            enemy = TankEnemy()
        enemy.speedy *= self.difficulty
        return enemy
    
    def spawn_powerup(self, x, y):
        """
        Spawn a random power-up at the given position.
        
        Args:
            x (int): X position
            y (int): Y position
            
        Returns:
            PowerUp: A new power-up sprite
        """
        power_type = random.choice(["health", "power", "shield"])
        return PowerUp(x, y, power_type)

    def show_game_over(self):
        """
        Display the game over screen with final score.
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # More opaque
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = font.render("GAME OVER! Press R to restart", True, (255, 255, 255))
        score_text = font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        high_score_text = font.render(f"High Score: {self.high_score}", True, (255, 255, 0))
        
        self.screen.blit(game_over_text, (self.screen_width//2 - game_over_text.get_width()//2, self.screen_height//2 - 60))
        self.screen.blit(score_text, (self.screen_width//2 - score_text.get_width()//2, self.screen_height//2))
        self.screen.blit(high_score_text, (self.screen_width//2 - high_score_text.get_width()//2, self.screen_height//2 + 40))
        
        credit_text = small_font.render("Press ESC to quit", True, (255, 255, 255))
        self.screen.blit(credit_text, (self.screen_width//2 - credit_text.get_width()//2, self.screen_height - 50))

    def show_pause_screen(self):
        """
        Display pause screen overlay.
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        pause_text = font.render("PAUSED", True, (255, 255, 255))
        resume_text = small_font.render("Press P to resume", True, (255, 255, 255))
        version_text = small_font.render(f"Space Shooter {VERSION} - {VERSION_NAME}", True, (200, 200, 200))
        
        self.screen.blit(pause_text, (self.screen_width//2 - pause_text.get_width()//2, self.screen_height//2 - 50))
        self.screen.blit(resume_text, (self.screen_width//2 - resume_text.get_width()//2, self.screen_height//2 + 10))
        self.screen.blit(version_text, (self.screen_width//2 - version_text.get_width()//2, self.screen_height//2 + 50))

# Replace the global game initialization code with a main function
def main():
    """
    Main function that initializes and runs the game.
    """
    try:
        # Initialize the game
        log_info("Initializing Space Shooter game...")
        game = Game()
        
        # Run the game
        game.run()
        
        # Clean exit
        log_info("Game exited cleanly")
        return 0
    except Exception as e:
        log_error(e, "Unhandled exception in main")
        pygame.quit()
        return 1

# Run the game if this script is executed directly
if __name__ == "__main__":
    sys.exit(main())
