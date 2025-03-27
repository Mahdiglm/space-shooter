import pygame
import os

# Initialize pygame to use its drawing functions
pygame.init()

# Create the assets directories if they don't exist
os.makedirs('assets/images', exist_ok=True)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Create player ship
player_surface = pygame.Surface((50, 40), pygame.SRCALPHA)
# Draw a triangular spaceship
pygame.draw.polygon(player_surface, WHITE, [(25, 0), (0, 40), (50, 40)])
# Add some details
pygame.draw.rect(player_surface, BLUE, (10, 30, 30, 5))
pygame.image.save(player_surface, 'assets/images/player.png')

# Create regular enemy
enemy_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
# Draw a simple enemy
pygame.draw.circle(enemy_surface, RED, (15, 15), 15)
pygame.draw.rect(enemy_surface, WHITE, (5, 5, 20, 5))
pygame.image.save(enemy_surface, 'assets/images/enemy.png')

# Create fast enemy
fast_enemy_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
# Draw a simple enemy
pygame.draw.circle(fast_enemy_surface, BLUE, (15, 15), 15)
pygame.draw.polygon(fast_enemy_surface, WHITE, [(5, 15), (15, 5), (25, 15), (15, 25)])
pygame.image.save(fast_enemy_surface, 'assets/images/fast_enemy.png')

# Create tank enemy
tank_enemy_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
# Draw a simple enemy
pygame.draw.circle(tank_enemy_surface, GREEN, (15, 15), 15)
pygame.draw.rect(tank_enemy_surface, WHITE, (5, 10, 20, 10))
pygame.image.save(tank_enemy_surface, 'assets/images/tank_enemy.png')

# Create boss enemy
boss_enemy_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
# Draw a boss
pygame.draw.circle(boss_enemy_surface, YELLOW, (30, 30), 30)
pygame.draw.polygon(boss_enemy_surface, RED, [(20, 20), (40, 20), (30, 40)])
pygame.draw.rect(boss_enemy_surface, WHITE, (15, 45, 30, 5))
pygame.image.save(boss_enemy_surface, 'assets/images/boss_enemy.png')

# Create bullet
bullet_surface = pygame.Surface((5, 10), pygame.SRCALPHA)
# Draw a bullet
pygame.draw.rect(bullet_surface, WHITE, (0, 0, 5, 10))
pygame.image.save(bullet_surface, 'assets/images/bullet.png')

# Create health power-up
health_powerup_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
# Draw a power-up
pygame.draw.circle(health_powerup_surface, GREEN, (10, 10), 10)
pygame.draw.rect(health_powerup_surface, WHITE, (5, 8, 10, 4))
pygame.draw.rect(health_powerup_surface, WHITE, (8, 5, 4, 10))
pygame.image.save(health_powerup_surface, 'assets/images/health_powerup.png')

# Create power power-up
power_powerup_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
# Draw a power-up
pygame.draw.circle(power_powerup_surface, BLUE, (10, 10), 10)
pygame.draw.polygon(power_powerup_surface, WHITE, [(10, 3), (15, 10), (10, 17), (5, 10)])
pygame.image.save(power_powerup_surface, 'assets/images/power_powerup.png')

# Create shield power-up
shield_powerup_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
# Draw a power-up
pygame.draw.circle(shield_powerup_surface, YELLOW, (10, 10), 10)
pygame.draw.circle(shield_powerup_surface, WHITE, (10, 10), 5, 2)
pygame.image.save(shield_powerup_surface, 'assets/images/shield_powerup.png')

# Create explosion frames
for i in range(9):
    size = 30
    explosion_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    radius = int((i + 1) * size / 18)
    pygame.draw.circle(explosion_surface, RED, (size//2, size//2), radius)
    pygame.draw.circle(explosion_surface, YELLOW, (size//2, size//2), radius - 2)
    pygame.image.save(explosion_surface, f'assets/images/explosion{i}.png')

print("All placeholder images have been created!") 