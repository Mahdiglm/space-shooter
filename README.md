# Space Shooter Game

A visually stunning and highly immersive 2D space shooter game built with Python and Pygame. Control your spaceship, shoot enemies, collect power-ups, and try to survive as long as possible!

*Last updated: March 27, 2025*
*Current version: 0.3.1*

![Space Shooter Game](assets/images/background.jpg)

## Features

- Smooth spaceship controls with responsive gameplay
- Rich audiovisual experience with custom graphics and sound effects
- Multiple enemy types with unique behaviors and visuals
- Power-up system with three types of upgrades and visual effects
- Progressive difficulty system that keeps the challenge fresh
- Boss battles with unique attack patterns and projectiles
- Weapon power levels with visual feedback
- Health and shield system with animations
- Scoring system with high score tracking
- 60 FPS gameplay with optimized rendering
- Game over screen with restart option
- Immersive background music and sound effects
- Dynamic explosion animations
- Visual health bar and power indicators
- Pause functionality
- Star background effect when playing without background image
- Player damage visual feedback
- Detailed game UI with FPS counter and shield timer

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Mahdiglm/space-shooter.git
cd space-shooter
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

1. Run the game:
```bash
python main.py
```

2. Controls:
- LEFT ARROW: Move spaceship left
- RIGHT ARROW: Move spaceship right
- SPACEBAR: Shoot bullets
- P: Pause/unpause the game
- R: Restart game after game over
- ESC: Quit the game

3. Enemy Types:
- Regular Enemies (Red): Standard enemies
- Fast Enemies (Blue): Faster but more fragile, with horizontal movement
- Tank Enemies (Green): Slower but tougher, with more health
- Boss Enemy (Yellow): Appears at 1000 points, shoots projectiles, has complex movement patterns

4. Power-ups:
- Health (Green): Restores 20 health points
- Power (Blue): Increases weapon power level
- Shield (Yellow): Temporary invulnerability for 5 seconds

5. Weapon Power Levels:
- Level 1: Single shot
- Level 2: Double shot
- Level 3: Triple shot

6. Objective:
- Shoot enemies to score points
- Collect power-ups to enhance your abilities
- Avoid collisions with enemies and boss projectiles
- Try to survive as long as possible
- Defeat the boss enemy for bonus points
- Beat your high score

7. Scoring:
- Regular Enemy: 10 points
- Fast Enemy: 15 points
- Tank Enemy: 25 points
- Boss Enemy: 150 points

8. Difficulty:
- Game becomes progressively harder over time
- Enemy speed increases with difficulty
- Boss appears at 1000 points
- Try to achieve the highest score possible!

## Game Assets

- All graphics are custom-designed for this game
- Sound effects:
  - Shooting sounds when firing bullets
  - Explosion sounds when enemies are destroyed
  - Power-up collection sounds
  - Game over sound
- Background music plays during gameplay

## Latest Updates (v0.3.1)

- Added pause functionality (Press P to pause/unpause)
- Added high score tracking
- Improved collision detection with circular hitboxes
- Enhanced player movement for better responsiveness 
- Added boss projectiles for more challenging boss fights
- Added visual damage feedback when player is hit
- Enhanced power-up effects with wobble animation
- Added remaining shield time display
- Added color-coded health bar
- Added star background effect when no background image is available
- Improved game balance and difficulty progression

## Development

This project is open source and welcomes contributions! Please check out our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Asset Licensing
All game assets (images, sounds, and fonts) are original works created for this project and are licensed under the MIT License. No third-party assets are used in this game.

## Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Sound effects from [SoundJay](https://www.soundjay.com/)
- Inspired by classic space shooter games 