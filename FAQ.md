# Space Shooter - Frequently Asked Questions

## Player Questions

### General Questions

#### Q: What are the system requirements to run Space Shooter?
A: Space Shooter has minimal requirements:
- Python 3.6 or higher
- Pygame 2.0.0 or higher
- 512MB RAM
- Any graphics card that supports hardware acceleration
- Works on Windows, macOS, and Linux

#### Q: How do I install the game?
A: Follow these steps:
1. Clone the repository: `git clone https://github.com/Mahdiglm/space-shooter.git`
2. Navigate to the game directory: `cd space-shooter`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the game: `python main.py`

#### Q: The game is running slowly on my computer. What can I do?
A: Try these solutions:
- Press 'M' to view performance metrics and identify bottlenecks
- Close other applications that might be using system resources
- Decrease your monitor's resolution before running the game
- Edit `game_config.py` and reduce `MAX_PARTICLES` or `MAX_ENEMIES`

### Gameplay Questions

#### Q: How do I improve my score?
A: Here are some tips:
- Focus on destroying tank enemies and bosses for more points
- Collect the orange Double Points power-up to double your score temporarily
- Try to keep your weapon power level at maximum for more firepower
- Prioritize survival over aggressive play - staying alive longer means more points

#### Q: How do I defeat the boss enemies?
A: Boss enemies have several attack patterns:
1. They move in a sine wave pattern horizontally
2. They shoot projectiles at the player
3. They have significantly more health than regular enemies

To defeat them:
- Focus on dodging their projectiles
- Attack when they're at the bottom of their movement pattern
- Keep your power level high for maximum damage output
- Use shield power-ups strategically when they're about to hit you

#### Q: What do the different power-ups do?
A: The game features several power-ups:
- Health (Green): Restores 20 health points
- Power (Blue): Increases weapon power level
- Shield (Yellow): Temporary invulnerability for 5 seconds
- Rapid Fire (Purple): Increases firing rate for 8 seconds
- Double Points (Orange): Doubles all points earned for 10 seconds

#### Q: Why does my weapon power-up reset when I die?
A: This is part of the game design. When your ship is destroyed, you restart with the base weapon power level (single shot). This adds challenge and encourages careful play.

## Developer Questions

#### Q: How does the optimized rendering system work?
A: The game uses a technique called "dirty rectangle" rendering:
1. Only areas of the screen that changed are redrawn (dirty rectangles)
2. The `GameRenderer` class tracks sprite positions from frame to frame
3. When a sprite moves, its old position is marked as dirty and needs to be redrawn
4. This minimizes GPU operations and improves performance

See `ARCHITECTURE.md` for technical details.

#### Q: How is collision detection optimized?
A: The game uses a spatial hash grid system:
1. The game world is divided into a grid of cells
2. Objects are stored in the cells they overlap
3. Collision checks only happen between objects in the same or adjacent cells
4. This reduces collision checks from O(n²) to nearly O(n)

See the `SpatialHash` class in `sprite_manager.py` for implementation details.

#### Q: How do I add a new enemy type?
A: To add a new enemy type:
1. Add the enemy type configuration to the `ENEMY_TYPES` dictionary in `game_config.py`
2. Create a new enemy class that inherits from the base `Enemy` class
3. Implement custom behavior in the `update()` method
4. Add appropriate sprites for the new enemy
5. Update the enemy spawning logic in the `spawn_enemy()` function

See `ARCHITECTURE.md` for a code example.

#### Q: How do I contribute to the project?
A: Please follow these steps:
1. Fork the repository on GitHub
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add appropriate tests
4. Ensure your code follows the project's style guidelines
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

See `CONTRIBUTING.md` for detailed guidelines.

#### Q: What's the recommended way to debug the game?
A: The game includes several debugging tools:
- Press 'M' to toggle performance metrics display
- Check the log files in the `logs` directory
- Use `log_debug()` and `log_game_event()` functions from `game_logger.py`
- Add `print()` statements during development (but remove before submitting pull requests)
- For complex issues, use Python's built-in debugging tools such as `pdb`

#### Q: Can I use the game's assets in my own project?
A: All game assets (images, sounds, and fonts) are licensed under the MIT License. You can use them in your own projects, but attribution is appreciated.

## Technical Troubleshooting

#### Q: I get "ModuleNotFoundError: No module named 'pygame'" when running the game
A: You need to install the Pygame library:
```
pip install pygame
```

#### Q: The game crashes with "pygame.error: No available video device"
A: This usually happens when:
- You're running on a headless server without a display
- Your graphics drivers need updating
- You're using a remote desktop connection that doesn't support graphics

Solution: Install proper graphics drivers or use a system with a display.

#### Q: The game performance decreases over time
A: This might be due to:
- Memory leaks (unlikely but possible)
- System thermal throttling
- Background processes starting

Solutions:
- Restart the game after extended play sessions
- Check system temperatures
- Close unnecessary background applications

#### Q: I'm getting "PermissionError" when running the game
A: This can happen if:
- The game's log files are open in another application
- You don't have write permissions in the game directory

Solutions:
- Close any applications that might be accessing the game's files
- Run the game with appropriate permissions
- Ensure the game directory is writable 