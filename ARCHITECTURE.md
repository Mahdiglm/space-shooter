# Space Shooter - Technical Architecture

This document provides an overview of the technical architecture of the Space Shooter game, explaining key systems and how they interact.

## Core Architecture

The Space Shooter game is built with a modular architecture focused on performance optimization and maintainability. The core components are:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     main.py     │────▶│  GameRenderer   │────▶│  SpriteManager  │
└────────┬────────┘     └─────────────────┘     └─────────────────┘
         │                                                │
         ▼                                                ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│PerformanceMonitor│    │   game_config   │    │  SpatialHash    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   game_logger   │────▶│     Sprites     │────▶│ game_exceptions │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Performance Optimization Systems

The game implements several advanced performance optimization techniques:

### 1. GameRenderer - Optimized Rendering System

The `GameRenderer` class implements dirty rectangle rendering to minimize GPU operations:

```python
class GameRenderer:
    def __init__(self, screen, background_color=(0, 0, 0)):
        self.screen = screen
        self.dirty_rects = []
        self.previous_sprite_rects = {}
        self.full_redraw_needed = True
```

**Key Features:**
- Tracks "dirty rectangles" (areas of the screen that changed)
- Only redraws parts of the screen that need updating
- Maintains a cache of the background for efficient partial redraws
- Toggleable performance metrics display 

**Advantages:**
- Significantly reduces GPU usage
- Improves performance on lower-end hardware
- Allows for more sprites on screen simultaneously

### 2. SpatialHash - Advanced Collision Detection

The `SpatialHash` class divides the game world into a grid for efficient collision detection:

```python
class SpatialHash:
    def __init__(self, cell_size=64):
        self.cell_size = cell_size
        self.grid = defaultdict(list)
        
    def insert_object(self, obj):
        # Calculate grid cells this object overlaps
        # Insert into appropriate cells
```

**How It Works:**
1. Divides the screen into a grid of cells (default 64x64 pixels)
2. Places game objects into grid cells they overlap
3. When checking collisions, only checks objects in the same or adjacent cells
4. Reduces collision checks from O(n²) to nearly O(n)

**Implementation Example:**
```python
# Without spatial partitioning (O(n²)):
for sprite1 in all_sprites:
    for sprite2 in all_sprites:
        if sprite1 != sprite2:
            check_collision(sprite1, sprite2)
            
# With spatial partitioning (nearly O(n)):
for sprite in all_sprites:
    nearby_sprites = spatial_hash.get_nearby_objects(sprite)
    for nearby_sprite in nearby_sprites:
        check_collision(sprite, nearby_sprite)
```

### 3. SpriteManager - Optimized Sprite Processing

The `SpriteManager` class handles efficient sprite updates and rendering:

```python
class SpriteManager:
    def __init__(self, screen_width, screen_height):
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.spatial_hash = SpatialHash()
        self.visible_sprites = set()
```

**Key Features:**
- Visibility tracking (only processes sprites visible on screen)
- Interfaces with the spatial hash system
- Efficient collision group management
- Performance metrics tracking

### 4. PerformanceMonitor - Real-time Performance Analysis

The `PerformanceMonitor` class provides real-time performance statistics:

```python
class PerformanceMonitor:
    def __init__(self, sample_size=60):
        self.metrics = {
            "frame": deque(maxlen=sample_size),
            "update": deque(maxlen=sample_size),
            "render": deque(maxlen=sample_size),
            "collision": deque(maxlen=sample_size),
            # Additional metrics...
        }
```

**Key Features:**
- Detailed timing for game operations (update, render, collision, etc.)
- FPS tracking and display
- Performance warnings when operations take too long
- In-game visualization toggle (M key)

## Sprite System

The game uses Pygame's sprite system with custom enhancements:

```python
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Player attributes
        self.radius = 20  # Used for circular collision detection
```

**Collision Detection:**
- Uses circle-based collision detection for more accurate and efficient hit detection:
```python
def _check_circle_collision(self, sprite1, sprite2):
    """Check collision between two sprites using circular hitboxes."""
    dx = sprite1.rect.centerx - sprite2.rect.centerx
    dy = sprite1.rect.centery - sprite2.rect.centery
    distance = math.sqrt(dx * dx + dy * dy)
    return distance < (getattr(sprite1, 'radius', 25) + getattr(sprite2, 'radius', 25))
```

## Configuration System

The game uses a dedicated configuration system (`game_config.py`) for game balance:

```python
# Difficulty settings example:
DIFFICULTY_SCALING = {
    'enemy_speed': {
        'base': 2.0,
        'increase_rate': 0.05,
        'max': 5.0
    },
    # Additional settings...
}

# Power-up settings example:
POWERUP_TYPES = {
    'health': {
        'chance': 0.4,
        'heal_amount': 20,
        'duration': 0,
        'color': (0, 255, 0)
    },
    # Additional power-ups...
}
```

## Logging and Error Handling

The game implements robust logging and error handling:

```python
# Logging example:
log_performance("Rendering", avg_render_time)
log_game_event("PowerUp", "Shield activated")

# Error handling:
try:
    # Game operation
except GameException as e:
    handle_game_error(e)
```

## Extending the Game

### Adding a New Enemy Type:

```python
class NewEnemy(Enemy):
    def __init__(self):
        super().__init__(enemy_type='new')
        self.health = ENEMY_TYPES['new']['health']
        self.speed = ENEMY_TYPES['new']['speed']
        
    def update(self):
        # Custom movement pattern
        self.rect.y += self.speed
        self.rect.x += math.sin(pygame.time.get_ticks() * 0.01) * 3
```

### Adding a New Power-up Type:

1. Add to `POWERUP_TYPES` in `game_config.py`:
```python
'mega_shield': {
    'chance': 0.05,
    'duration': 10000,
    'color': (255, 215, 0)
}
```

2. Implement the effect in the `PowerUp.apply_effect` method:
```python
def apply_effect(self, player):
    if self.power_type == 'mega_shield':
        player.invulnerable = True
        player.invulnerable_timer = pygame.time.get_ticks()
        player.invulnerable_duration = POWERUP_TYPES['mega_shield']['duration']
```

## Future Architecture Improvements

- Entity Component System (ECS) for better organization
- Asset Manager for centralized resource handling
- Game State Machine for cleaner state transitions
- Thread-based asset loading for smoother gameplay 