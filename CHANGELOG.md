# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-03-27

### Added
- Multiple enemy types:
  - Regular enemies (red)
  - Fast enemies (blue) - faster but fragile
  - Tank enemies (green) - slower but tougher
  - Boss enemy (yellow) - appears at 1000 points
- Power-up system with three types:
  - Health power-up (green) - restores 20 health
  - Power power-up (blue) - increases weapon power
  - Shield power-up (yellow) - temporary invulnerability
- Progressive difficulty system
- Weapon power levels (1-3):
  - Level 1: Single shot
  - Level 2: Double shot
  - Level 3: Triple shot
- Shooting cooldown system
- Different point values for different enemies
- Boss enemy with unique movement patterns
- Visual indicators for power-ups and shield status

### Changed
- Completely revamped enemy spawning system
- Improved collision detection
- Enhanced game balance
- More challenging gameplay mechanics
- Better visual feedback for game state

### Fixed
- Memory management for sprites
- Collision detection accuracy
- Game state management
- Power-up spawning logic

### Removed
- Basic enemy-only system
- Simple scoring system
- Single-shot weapon system

## [0.1.1] - 2025-03-27

### Added
- Scoring system
- Player health system
- Game over screen with restart option
- On-screen display for score and health
- Press R to restart after game over

### Changed
- Improved game mechanics
- Enhanced enemy behavior
- Better collision detection

### Fixed
- Game now properly ends when player loses all health
- Added proper game state management
- Fixed potential memory leaks with sprite cleanup

## [0.1.0] - 2025-03-27

### Added
- Initial release
- Basic game mechanics
  - Player spaceship with movement controls
  - Enemy ships with random movement patterns
  - Bullet shooting system
  - Collision detection
- Game window setup (800x600)
- Basic graphics using Pygame surfaces

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None