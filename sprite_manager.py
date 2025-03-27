import pygame
import math
from collections import defaultdict
from game_logger import log_performance, log_debug, log_info

class SpatialHash:
    """
    A spatial hash system to optimize collision detection.
    Divides the screen into a grid and only checks collisions between objects in the same grid cells.
    """
    def __init__(self, cell_size=64):
        self.cell_size = cell_size
        self.grid = defaultdict(list)
    
    def clear(self):
        """Clear the spatial hash grid."""
        self.grid.clear()
    
    def hash_point(self, x, y):
        """Convert a point to a grid cell."""
        return int(x / self.cell_size), int(y / self.cell_size)
    
    def insert_object(self, obj):
        """Insert an object into the grid."""
        # Calculate the grid cells this object overlaps
        left = obj.rect.left
        right = obj.rect.right
        top = obj.rect.top
        bottom = obj.rect.bottom
        
        # Get all cells the object overlaps
        min_x, min_y = self.hash_point(left, top)
        max_x, max_y = self.hash_point(right, bottom)
        
        # Insert object into each cell it overlaps
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                self.grid[(x, y)].append(obj)
        
        # Store which cells the object is in
        obj.grid_cells = [(x, y) for x in range(min_x, max_x + 1) for y in range(min_y, max_y + 1)]
    
    def get_nearby_objects(self, obj):
        """Get all objects in the same cells as the given object."""
        nearby = set()
        
        for cell in getattr(obj, 'grid_cells', []):
            nearby.update(self.grid[cell])
        
        # Remove the object itself from the results
        if obj in nearby:
            nearby.remove(obj)
            
        return nearby

class SpriteManager:
    """
    Manages game sprites with optimized updates and collision detection.
    """
    def __init__(self, screen_width, screen_height):
        # Screen dimensions
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Sprite groups for each sprite type
        self.all_sprites = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.background_sprites = pygame.sprite.Group()
        
        # Spatial hash for collision detection
        self.spatial_hash = SpatialHash()
        
        # Visible sprites (within screen boundaries)
        self.visible_sprites = set()
        
        # Performance metrics
        self.sprites_processed = 0
        self.collisions_checked = 0
        self.collisions_detected = 0
        
    def add_sprite(self, sprite, sprite_type):
        """Add a sprite to appropriate groups."""
        self.all_sprites.add(sprite)
        
        if sprite_type == 'player':
            self.player_group.add(sprite)
        elif sprite_type == 'enemy':
            self.enemies.add(sprite)
        elif sprite_type == 'bullet':
            self.bullets.add(sprite)
        elif sprite_type == 'enemy_bullet':
            self.enemy_bullets.add(sprite)
        elif sprite_type == 'powerup':
            self.powerups.add(sprite)
        elif sprite_type == 'explosion':
            self.explosions.add(sprite)
        elif sprite_type == 'background':
            self.background_sprites.add(sprite)
    
    def remove_sprite(self, sprite):
        """Remove a sprite from all groups."""
        sprite.kill()
    
    def update_sprites(self):
        """Update all sprites and rebuild spatial hash."""
        # Reset counters
        self.sprites_processed = 0
        self.visible_sprites.clear()
        
        # Clear spatial hash
        self.spatial_hash.clear()
        
        # Update all sprites and add to spatial hash if visible
        for sprite in self.all_sprites:
            sprite.update()
            self.sprites_processed += 1
            
            # Check if sprite is visible on screen
            if self._is_sprite_visible(sprite):
                self.visible_sprites.add(sprite)
                self.spatial_hash.insert_object(sprite)
    
    def _is_sprite_visible(self, sprite):
        """Check if a sprite is visible on screen."""
        if not hasattr(sprite, 'rect'):
            return False
            
        rect = sprite.rect
        return (rect.right > 0 and rect.left < self.screen_width and 
                rect.bottom > 0 and rect.top < self.screen_height)
    
    def get_all_groups(self):
        """Get all sprite groups for rendering."""
        return [self.background_sprites, self.bullets, self.enemy_bullets, 
                self.enemies, self.player_group, self.powerups, self.explosions]
    
    def get_visible_sprites(self):
        """Get all sprites that are currently visible."""
        return self.visible_sprites
    
    def get_all_sprites(self):
        """Get all sprites from all groups as a list."""
        return self.all_sprites.sprites()
    
    def check_collisions(self):
        """
        Check collisions between sprites using the spatial hash.
        Returns a dictionary of collision pairs.
        """
        # Reset collision counters
        self.collisions_checked = 0
        self.collisions_detected = 0
        
        # Dictionary to store collision results
        collisions = {
            'bullet_enemy': [],
            'player_enemy': [],
            'player_powerup': [],
            'player_enemy_bullet': []
        }
        
        # Get player sprite
        player = self.player_group.sprite
        if player:
            # Check player collisions with enemies
            nearby_enemies = self.spatial_hash.get_nearby_objects(player)
            for enemy in nearby_enemies:
                if enemy in self.enemies:
                    self.collisions_checked += 1
                    if self._check_circle_collision(player, enemy):
                        collisions['player_enemy'].append(enemy)
                        self.collisions_detected += 1
            
            # Check player collisions with enemy bullets
            for bullet in self.enemy_bullets:
                self.collisions_checked += 1
                if self._check_circle_collision(player, bullet):
                    collisions['player_enemy_bullet'].append(bullet)
                    self.collisions_detected += 1
            
            # Check player collisions with powerups
            for powerup in self.powerups:
                self.collisions_checked += 1
                if self._check_circle_collision(player, powerup):
                    collisions['player_powerup'].append(powerup)
                    self.collisions_detected += 1
        
        # Check bullet-enemy collisions
        for bullet in self.bullets:
            nearby_enemies = self.spatial_hash.get_nearby_objects(bullet)
            for enemy in nearby_enemies:
                if enemy in self.enemies:
                    self.collisions_checked += 1
                    if self._check_circle_collision(bullet, enemy):
                        if enemy not in collisions['bullet_enemy']:
                            collisions['bullet_enemy'].append((enemy, bullet))
                            self.collisions_detected += 1
        
        return collisions
    
    def _check_circle_collision(self, sprite1, sprite2):
        """
        Check collision between two sprites using circle collision.
        More accurate than rectangle collision especially for round objects.
        """
        # Check if sprites have the required attributes
        if not (hasattr(sprite1, 'rect') and hasattr(sprite2, 'rect')):
            return False
        
        # Use radius attribute if available, otherwise use half the width
        radius1 = getattr(sprite1, 'radius', sprite1.rect.width // 2)
        radius2 = getattr(sprite2, 'radius', sprite2.rect.width // 2)
        
        # Calculate center points
        center1 = sprite1.rect.center
        center2 = sprite2.rect.center
        
        # Calculate distance between centers
        dx = center1[0] - center2[0]
        dy = center1[1] - center2[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        # Check if distance is less than sum of radii
        return distance < radius1 + radius2
    
    def get_performance_metrics(self):
        """Get performance metrics for the sprite manager."""
        return {
            'total_sprites': len(self.all_sprites),
            'visible_sprites': len(self.visible_sprites),
            'sprites_processed': self.sprites_processed,
            'collisions_checked': self.collisions_checked,
            'collisions_detected': self.collisions_detected
        }
    
    def clear_all_except_player(self):
        """
        Remove all sprites except the player.
        Used when resetting the game.
        """
        player = None
        if self.player_group.sprite:
            player = self.player_group.sprite
        
        # Clear all sprite groups
        self.all_sprites.empty()
        self.enemies.empty()
        self.bullets.empty()
        self.enemy_bullets.empty()
        self.powerups.empty()
        self.explosions.empty()
        
        # Keep background sprites if any
        # Clear and re-add background sprites
        background_sprites = pygame.sprite.Group()
        for sprite in self.background_sprites:
            background_sprites.add(sprite)
        self.background_sprites.empty()
        
        # Reset spatial hash
        self.spatial_hash.clear()
        self.visible_sprites.clear()
        
        # Add back the player and background sprites
        if player:
            self.all_sprites.add(player)
            self.player_group.add(player)
        
        for sprite in background_sprites:
            self.all_sprites.add(sprite)
            self.background_sprites.add(sprite)
        
        # Log the reset
        log_info(f"Sprite manager cleared. Remaining sprites: {len(self.all_sprites)}")
        
        # Reset performance metrics
        self.sprites_processed = 0
        self.collisions_checked = 0
        self.collisions_detected = 0 