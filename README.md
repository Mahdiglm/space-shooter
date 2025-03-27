# 🚀 Space Shooter v0.3.9

<div align="center">

![Space Shooter Banner](https://via.placeholder.com/800x200/0a0a2a/ffffff?text=Space+Shooter+v0.3.9)

<h3>An optimized 2D space shooter game with advanced performance techniques</h3>

[![Release Version](https://img.shields.io/badge/release-v0.3.9-blue.svg)](RELEASE_NOTES.md)
[![Performance Optimized](https://img.shields.io/badge/performance-optimized-green.svg)](ARCHITECTURE.md)
[![MIT License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Pygame](https://img.shields.io/badge/pygame-2.0+-red.svg)](https://www.pygame.org/)
[![Python](https://img.shields.io/badge/python-3.7+-blueviolet.svg)](https://www.python.org/)
[![FPS](https://img.shields.io/badge/FPS-60+-orange.svg)](PERFORMANCE.md)

<p>
Blast through space with optimized rendering, intelligent collision detection, and smooth 60+ FPS gameplay!
</p>

</div>

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📋 **README.md**](README.md) | General overview, features, and installation instructions |
| [📝 **RELEASE_NOTES.md**](RELEASE_NOTES.md) | Detailed information about the latest release |
| [🏗️ **ARCHITECTURE.md**](ARCHITECTURE.md) | Technical architecture, performance systems, and extension guides |
| [❓ **FAQ.md**](FAQ.md) | Frequently asked questions for both players and developers |
| [🤝 **CONTRIBUTING.md**](CONTRIBUTING.md) | Guidelines for contributing to the project |
| [📜 **CHANGELOG.md**](CHANGELOG.md) | Detailed history of changes and improvements |
| [⚖️ **CODE_OF_CONDUCT.md**](CODE_OF_CONDUCT.md) | Community standards and expectations |

## 🌟 Features

<div align="center">
<table>
  <tr>
    <td width="50%">
      <h3 align="center">🎮 Gameplay</h3>
      <ul>
        <li>Multiple enemy types with unique behaviors</li>
        <li>Powerful boss battles</li>
        <li>Power-up system with various buffs</li>
        <li>Increasing difficulty over time</li>
      </ul>
    </td>
    <td width="50%">
      <h3 align="center">⚡ Performance</h3>
      <ul>
        <li>Dirty rectangle rendering optimization</li>
        <li>Spatial partitioning for collision detection</li>
        <li>Asset caching and sprite culling</li>
        <li>Performance monitoring system</li>
      </ul>
    </td>
  </tr>
</table>
</div>

## 🚀 Quick Start

### Requirements
- Python 3.7 or higher
- Pygame 2.0.0 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/Mahdiglm/space-shooter.git

# Navigate to the game directory
cd space-shooter

# Install dependencies
pip install pygame

# Run the game
python main.py
```

## 🎮 Game Controls

<div align="center">
<table>
  <tr>
    <th>Main Controls</th>
    <th>Debug Controls</th>
  </tr>
  <tr>
    <td>
      <ul align="left">
        <li><strong>Arrow Keys</strong>: Move ship</li>
        <li><strong>Space</strong>: Shoot</li>
        <li><strong>P</strong>: Pause game</li>
        <li><strong>R</strong>: Restart (when game over)</li>
        <li><strong>ESC</strong>: Quit game</li>
      </ul>
    </td>
    <td>
      <ul align="left">
        <li><strong>F</strong>: Toggle FPS display</li>
        <li><strong>T</strong>: Toggle terminal reporting</li>
        <li><strong>D</strong>: Toggle debug visualization</li>
        <li><strong>M</strong>: Toggle performance monitor</li>
        <li><strong>C</strong>: Force full screen redraw</li>
      </ul>
    </td>
  </tr>
</table>
</div>

## 🔋 Power-ups

- **💚 Health**: Restores player health
- **🔵 Power**: Increases weapon power level
- **🔶 Shield**: Temporary invulnerability
- **🟣 Rapid Fire**: Temporarily increases firing rate
- **🟠 Double Points**: Doubles score for a limited time

## ⚙️ Performance Optimizations

<div align="center">
<img src="https://via.placeholder.com/800x200/333/ffffff?text=Performance+Visualization" alt="Performance Visualization" width="80%"/>
</div>

The game implements several advanced performance techniques:

1. **🖥️ Dirty Rectangle Rendering**
   - Only updates portions of the screen that changed
   - Significantly reduces GPU workload and improves FPS

2. **🔲 Spatial Partitioning**
   - Divides game space into a grid for efficient collision detection
   - Reduces collision checks from O(n²) to nearly O(n)

3. **💾 Asset Caching**
   - Pre-loads and caches frequently used images and text surfaces
   - Dramatically reduces loading times and memory usage

4. **✂️ Sprite Culling**
   - Off-screen sprites are bypassed during rendering
   - Reduces unnecessary processing

5. **⭕ Optimized Collision Detection**
   - Uses circle-based collision for better accuracy and performance
   - Implements collision pair caching to prevent redundant checks

## 📈 Latest Updates (v0.3.9)

- Fixed screen blinking during periodic redraws with intelligent redraw scheduling
- Enhanced text rendering system with better caching and surface management
- Improved sprite trail cleanup with better padding and background restoration
- Added semi-transparent UI background for better readability
- Increased health bar size and visibility
- Optimized full screen redraw intervals to reduce visual artifacts
- Created comprehensive RELEASE_NOTES.md with detailed changelog

## 🤝 Contributing

We welcome contributions from the community! Check out [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

<div align="center">
<table>
  <tr>
    <td align="center">
      <strong>Reporting Bugs</strong><br>
      <a href="https://github.com/Mahdiglm/space-shooter/issues">Issue Tracker</a>
    </td>
    <td align="center">
      <strong>Suggesting Features</strong><br>
      <a href="https://github.com/Mahdiglm/space-shooter/issues">Feature Requests</a>
    </td>
    <td align="center">
      <strong>Code Contributions</strong><br>
      <a href="CONTRIBUTING.md">Contribution Guide</a>
    </td>
  </tr>
</table>
</div>

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Sound effects from [SoundJay](https://www.soundjay.com/)
- Inspired by classic space shooter games

<div align="center">
<p>
<strong>Space Shooter</strong> - Blast through space at 60+ FPS! 🚀
</p>
</div> 