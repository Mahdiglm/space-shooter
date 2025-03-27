# Game Configuration Settings

# Difficulty Settings
DIFFICULTY_SCALING = {
    'enemy_speed': {
        'base': 2.0,
        'increase_rate': 0.05,
        'max': 5.0
    },
    'enemy_spawn_rate': {
        'base': 1.0,
        'increase_rate': 0.02,
        'max': 2.5
    },
    'enemy_health': {
        'base': 1.0,
        'increase_rate': 0.03,
        'max': 2.0
    },
    'boss_health': {
        'base': 25.0,
        'increase_rate': 0.1,
        'max': 50.0
    }
}

# Power-up Settings
POWERUP_TYPES = {
    'health': {
        'chance': 0.4,
        'heal_amount': 20,
        'duration': 0,
        'color': (0, 255, 0)
    },
    'power': {
        'chance': 0.3,
        'power_increase': 1,
        'duration': 0,
        'color': (0, 0, 255)
    },
    'shield': {
        'chance': 0.2,
        'duration': 5000,  # 5 seconds
        'color': (255, 255, 0)
    },
    'rapid_fire': {
        'chance': 0.1,
        'duration': 8000,  # 8 seconds
        'fire_rate_multiplier': 2.0,
        'color': (255, 0, 255)
    },
    'double_points': {
        'chance': 0.1,
        'duration': 10000,  # 10 seconds
        'points_multiplier': 2.0,
        'color': (255, 165, 0)
    }
}

# Enemy Types and Their Properties
ENEMY_TYPES = {
    'regular': {
        'health': 1,
        'speed': 2,
        'points': 10,
        'spawn_chance': 0.6
    },
    'fast': {
        'health': 1,
        'speed': 4,
        'points': 15,
        'spawn_chance': 0.2
    },
    'tank': {
        'health': 4,
        'speed': 1,
        'points': 25,
        'spawn_chance': 0.15
    },
    'boss': {
        'health': 25,
        'speed': 1,
        'points': 150,
        'spawn_chance': 0.05
    }
}

# Boss Spawn Settings
BOSS_SPAWN = {
    'initial_score': 1000,
    'score_increase': 500,  # Boss appears every 500 points after initial spawn
    'min_interval': 30000  # Minimum time between boss spawns (30 seconds)
}

# Game Balance Settings
GAME_BALANCE = {
    'player': {
        'base_health': 100,
        'base_speed': 6,
        'base_shoot_delay': 250,
        'max_power_level': 3
    },
    'difficulty_increase_rate': 0.08,
    'max_difficulty': 2.5,
    'powerup_chance': 0.15
}

# Visual Settings
VISUAL_SETTINGS = {
    'damage_flash_duration': 100,
    'shield_blink_rate': 8,
    'powerup_wobble_speed': 0.1,
    'explosion_frame_rate': 40
} 