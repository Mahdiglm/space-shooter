# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.2] - 2025-03-27

### Added
- Added comprehensive LICENSE file with MIT License
- Added proper asset licensing and attribution information
- Added licensing section to README.md

### Changed
- Updated asset attribution to correctly reflect OpenGameArt.org sources
- Improved documentation of third-party asset usage
- Fixed incorrect asset ownership claims
- Updated copyright notice in LICENSE file
- Improved documentation of asset ownership and licensing

## [0.3.1] - 2025-03-27

### Added
- Pause functionality (Press P to pause/unpause)
- High score tracking
- FPS counter
- Star background when no background image is available
- Enemy bullets for boss fights
- Player damage visual feedback
- Wobble effect for powerups
- Remaining shield time display
- Game controls hint for new players
- Color-coded health bar
- Boss health bar display
- Quit option with ESC key

### Changed
- Improved collision detection with circular hitboxes
- Enhanced player movement speed for better responsiveness
- Better difficulty scaling with a maximum cap
- Increased shield duration from 3 to 5 seconds
- More dynamic boss behavior with shooting ability
- Rebalanced gameplay for better challenge:
  - Increased powerup drop chance
  - Improved enemy movement patterns
  - Enhanced boss rewards
- More efficient screen updates
- Reduced CPU usage while paused

### Fixed
- Player shield visual effect now uses transparency instead of color swapping
- Fixed potential memory leak with sprite management
- Fixed enemy spawning at screen edges
- More accurate collision detection for all game objects
- Fixed potential crash when loading missing assets
- Performance optimizations for smoother gameplay
- Better enemy spawning logic

## [0.3.0] - 2025-03-27

### Added
- Complete audiovisual overhaul:
  - Sprite graphics for player, enemies, and power-ups
  - Background image for enhanced visual appeal
  - Explosion animations when enemies and player are destroyed
  - Sound effects for:
    - Shooting
    - Explosions
    - Power-up collection
    - Game over
  - Background music for immersive gameplay
- Visual health bar instead of text
- Player shield visualization with blinking effect
- Improved game menu and HUD (Heads Up Display)
- Automatic resource loading with fallbacks for missing assets

### Changed
- Improved player feedback with visual and audio cues
- Enhanced explosion animations
- Better visual representation of power-ups
- More responsive controls and gameplay
- Restructured game assets to support better organization

### Fixed
- Asset loading with proper error handling
- Visual bug with powerup collection
- Animation timing and frame rate issues
- Rendering optimizations for smoother gameplay

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