# Space Shooter v0.3.9

An optimized 2D space shooter game built with Pygame, featuring performance enhancements using dirty rectangle rendering and spatial partitioning for collision detection.

[![Release Version](https://img.shields.io/badge/release-v0.3.9-blue.svg)](RELEASE_NOTES.md)
[![Performance Optimized](https://img.shields.io/badge/performance-optimized-green.svg)](ARCHITECTURE.md)
[![GPL License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## Documentation

| Document | Description |
|----------|-------------|
| [📋 **README.md**](README.md) | General overview, features, and installation instructions |
| [📝 **RELEASE_NOTES.md**](RELEASE_NOTES.md) | Detailed information about the latest release |
| [🏗️ **ARCHITECTURE.md**](ARCHITECTURE.md) | Technical architecture, performance systems, and extension guides |
| [❓ **FAQ.md**](FAQ.md) | Frequently asked questions for both players and developers |
| [🤝 **CONTRIBUTING.md**](CONTRIBUTING.md) | Guidelines for contributing to the project |
| [📜 **CHANGELOG.md**](CHANGELOG.md) | Detailed history of changes and improvements |

## Features

- Smooth 60+ FPS gameplay with optimized rendering
- Diverse enemy types with different behaviors
- Power-up system with various buffs
- Performance monitoring and visualization tools
- Optimized collision detection using spatial partitioning
- Visual effects and animations

## Installation

### Requirements
- Python 3.7 or higher
- Pygame 2.0.0 or higher

### Setup
1. Clone this repository
2. Install the required packages:
```
pip install pygame
```
3. Run the game:
```
python main.py
```

## Gameplay

### Controls
- **Arrow Keys**: Move the player ship
- **Space**: Shoot
- **P**: Pause the game
- **ESC**: Quit
- **R**: Restart (after game over)

### Debug Controls
- **F**: Toggle FPS display
- **T**: Toggle terminal FPS reporting
- **D**: Toggle debug visualization
- **R**: Toggle dirty rectangles visualization (when not in game over state)
- **C**: Force a full screen redraw
- **M**: Toggle performance monitor display

### Power-ups
- **Health**: Restores player health
- **Power**: Increases weapon power level
- **Shield**: Temporary invulnerability

## Performance Optimizations

This game implements several performance optimizations:

1. **Dirty Rectangle Rendering**: Only update portions of the screen that have changed, significantly reducing GPU workload.
2. **Spatial Partitioning**: Divides the game space into a grid for efficient collision detection, reducing the number of checks required.
3. **Asset Caching**: Frequently used images and text are cached to reduce loading times.
4. **Sprite Culling**: Off-screen sprites are skipped during rendering.
5. **Optimized Collision Detection**: Uses circle-based collision for better accuracy and performance.

## Debugging and Development

Use the performance monitor (toggle with M key) to track:
- FPS
- Frame times
- Update times
- Render times
- Collision detection times

## Version History

### v0.3.9 - "Performance Optimized" (Current)
- Implemented dirty rectangle rendering for optimized performance
- Added spatial partitioning for collision detection
- Integrated comprehensive performance monitoring system
- Enhanced UI elements with semi-transparent backgrounds
- Fixed sprite trail artifacts and screen blinking
- Improved text rendering with advanced caching
- Increased health bar visibility and UI clarity

### v0.3.0
- Initial game implementation

## License

This project is open-source. Feel free to use, modify, and distribute the code.

## Game Assets

- Graphics and UI elements are sourced from OpenGameArt.org (CC0 Public Domain)
- Sound effects and background music are sourced from OpenGameArt.org (CC0 Public Domain)
- All assets are properly licensed and attributed to their respective sources

## Latest Updates (v0.3.9)

- Fixed screen blinking during periodic redraws with intelligent redraw scheduling
- Enhanced text rendering system with better caching and surface management
- Improved sprite trail cleanup with better padding and background restoration
- Added semi-transparent UI background for better readability
- Increased health bar size and visibility
- Optimized full screen redraw intervals to reduce visual artifacts
- Created comprehensive RELEASE_NOTES.md with detailed changelog

## Development

This project is open source and welcomes contributions! We have several ways you can help:

### Reporting Issues
- Use our [Issue Tracker](https://github.com/Mahdiglm/space-shooter/issues) to report bugs
- Follow the bug report template for detailed information
- Include system information and steps to reproduce

### Suggesting Features
- Submit feature requests through our [Issue Tracker](https://github.com/Mahdiglm/space-shooter/issues)
- Use the feature request template to describe your idea
- Explain why the feature would be beneficial

### Contributing Code
- Fork the repository
- Create a new branch for your feature
- Follow our coding standards
- Submit a pull request

### Documentation
- Help improve documentation
- Add comments to complex code
- Create tutorials or guides

For detailed guidelines, please check out our [Contributing Guidelines](CONTRIBUTING.md).

## Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Sound effects from [SoundJay](https://www.soundjay.com/)
- Inspired by classic space shooter games 