import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Set up the game window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Font
font = pygame.font.Font(None, 36)

# Game settings
DIFFICULTY_INCREASE_RATE = 0.1
INITIAL_ENEMY_SPEED = 2
MAX_ENEMY_SPEED = 5
POWERUP_CHANCE = 0.1
BOSS_SPAWN_SCORE = 1000

# Player spaceship
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = WINDOW_HEIGHT - 10
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.power_level = 1
        self.shoot_delay = 250  # milliseconds
        self.last_shot = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 3000  # 3 seconds

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
            self.rect.x += self.speed
        
        # Update invulnerability
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable = False

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
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

# Enemy base class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.health = 1
        self.points = 10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)

# Fast Enemy
class FastEnemy(Enemy):
    def __init__(self):
        super().__init__()
        self.image.fill(BLUE)
        self.speedy = random.randrange(4, 7)
        self.health = 1
        self.points = 15

# Tank Enemy
class TankEnemy(Enemy):
    def __init__(self):
        super().__init__()
        self.image.fill(GREEN)
        self.speedy = random.randrange(1, 2)
        self.health = 3
        self.points = 25

# Boss Enemy
class BossEnemy(Enemy):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 60))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.y = -60
        self.speedy = 1
        self.health = 20
        self.points = 100
        self.movement_pattern = 0
        self.movement_timer = 0

    def update(self):
        self.movement_timer += 1
        if self.movement_timer > 60:
            self.movement_pattern = (self.movement_pattern + 1) % 4
            self.movement_timer = 0

        if self.movement_pattern == 0:
            self.rect.x += 2
        elif self.movement_pattern == 1:
            self.rect.x -= 2
        elif self.movement_pattern == 2:
            self.rect.y += 1
        else:
            self.rect.y -= 1

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH

# Power-up
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.power_type = power_type
        if power_type == "health":
            self.image.fill(GREEN)
        elif power_type == "power":
            self.image.fill(BLUE)
        elif power_type == "shield":
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

# Bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player = Player()

all_sprites.add(player)

# Spawn initial enemies
for i in range(6):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Game variables
score = 0
game_over = False
clock = pygame.time.Clock()
difficulty = 1.0
boss_spawned = False

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
    screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
    screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, WINDOW_HEIGHT//2 + 10))
    pygame.display.flip()

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
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
                    if sprite != player:
                        sprite.kill()
                for i in range(6):
                    enemy = spawn_enemy()
                    all_sprites.add(enemy)
                    enemies.add(enemy)
                boss_spawned = False

    if not game_over:
        # Update
        all_sprites.update()

        # Increase difficulty over time
        difficulty += DIFFICULTY_INCREASE_RATE * (1/60)  # 60 FPS

        # Spawn boss at certain score
        if score >= BOSS_SPAWN_SCORE and not boss_spawned:
            boss = BossEnemy()
            all_sprites.add(boss)
            enemies.add(boss)
            boss_spawned = True

        # Check for bullet-enemy collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, bullet_list in hits.items():
            enemy.health -= len(bullet_list)
            if enemy.health <= 0:
                score += enemy.points
                # Chance to spawn power-up
                if random.random() < POWERUP_CHANCE:
                    powerup = spawn_powerup(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(powerup)
                    powerups.add(powerup)
                enemy.kill()
                if not boss_spawned:
                    new_enemy = spawn_enemy()
                    all_sprites.add(new_enemy)
                    enemies.add(new_enemy)

        # Check for player-enemy collisions
        if not player.invulnerable:
            hits = pygame.sprite.spritecollide(player, enemies, False)
            if hits:
                player.health -= 1
                if player.health <= 0:
                    game_over = True

        # Check for power-up collisions
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in hits:
            if powerup.power_type == "health":
                player.health = min(player.max_health, player.health + 20)
            elif powerup.power_type == "power":
                player.power_level = min(3, player.power_level + 1)
            elif powerup.power_type == "shield":
                player.invulnerable = True
                player.invulnerable_timer = pygame.time.get_ticks()

        # Draw
        screen.fill(BLACK)
        all_sprites.draw(screen)
        
        # Draw score, health, and power level
        score_text = font.render(f"Score: {score}", True, WHITE)
        health_text = font.render(f"Health: {player.health}", True, WHITE)
        power_text = font.render(f"Power: {player.power_level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(health_text, (10, 40))
        screen.blit(power_text, (10, 70))
        
        # Draw invulnerability indicator
        if player.invulnerable:
            shield_text = font.render("SHIELD ACTIVE!", True, YELLOW)
            screen.blit(shield_text, (WINDOW_WIDTH - 200, 10))
        
        pygame.display.flip()
    else:
        show_game_over()

    # Cap the framerate
    clock.tick(60)

pygame.quit()
sys.exit()
