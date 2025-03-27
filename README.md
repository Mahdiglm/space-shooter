# Space Shooter Game

A challenging 2D space shooter game built with Python and Pygame. Control your spaceship, shoot enemies, collect power-ups, and try to survive as long as possible!

*Last updated: March 27, 2025*

## Features

- Smooth spaceship controls
- Multiple enemy types with unique behaviors
- Power-up system with three types of upgrades
- Progressive difficulty system
- Boss battles
- Weapon power levels
- Health and shield system
- Scoring system with different point values
- 60 FPS gameplay
- Game over screen with restart option
- On-screen display for score, health, and power level

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
- R: Restart game after game over

3. Enemy Types:
- Regular Enemies (Red): Standard enemies
- Fast Enemies (Blue): Faster but more fragile
- Tank Enemies (Green): Slower but tougher
- Boss Enemy (Yellow): Appears at 1000 points

4. Power-ups:
- Health (Green): Restores 20 health points
- Power (Blue): Increases weapon power level
- Shield (Yellow): Temporary invulnerability

5. Weapon Power Levels:
- Level 1: Single shot
- Level 2: Double shot
- Level 3: Triple shot

6. Objective:
- Shoot enemies to score points
- Collect power-ups to enhance your abilities
- Avoid collisions with enemies
- Try to survive as long as possible
- Defeat the boss enemy for bonus points

7. Scoring:
- Regular Enemy: 10 points
- Fast Enemy: 15 points
- Tank Enemy: 25 points
- Boss Enemy: 100 points

8. Difficulty:
- Game becomes progressively harder over time
- Enemy speed increases with difficulty
- Boss appears at 1000 points
- Try to achieve the highest score possible!

## Development

This project is open source and welcomes contributions! Please check out our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Inspired by classic space shooter games 