# 🐍 Snake Adventure - The Ultimate Slither Experience

A modern, feature-rich reimagining of the classic Snake game built with Python and Pygame. This isn't your ordinary Snake game - it's packed with visual enhancements, progressive difficulty, power-ups, and engaging gameplay mechanics that will keep you coming back for more!

## ✨ Features

### 🎮 Enhanced Gameplay
- **Mouse Control**: Smooth, intuitive mouse-based movement - click anywhere to guide your snake
- **Progressive Speed System**: Snake gradually gets faster as you consume more food, adding strategic depth
- **Multiple Lives**: Start with 3 lives and temporary invulnerability after taking damage
- **Level Progression**: Clear all food to advance to the next level with new challenges

### 🍎 Diverse Food Types
- **🔴 Regular Food**: Basic growth and points (10 points, +1 segment)
- **🟡 Super Food**: Bonus points and extra growth (50 points, +3 segments)  
- **🟣 Power Food**: Temporary speed boost power-up (50 points, +3 segments, 2x speed)

### 🎨 Visual Excellence
- **Enhanced Snake Design**: Realistic segmented body with gradient coloring, animated scales, and detailed head with eyes and forked tongue
- **3D Food Effects**: Pulsing food with glow effects, sparkles for special items, and realistic textures
- **Dynamic Backgrounds**: Animated grass patterns and gradient environments
- **Obstacle Graphics**: 3D textured rocks with realistic shadows and highlights
- **Particle Effects**: Visual feedback for various game events

### 📊 Advanced Features
- **Statistics Tracking**: Score, level, lives, food eaten, snake length
- **High Score System**: Persistent high score storage with JSON file saving
- **Speed Meter**: Real-time visual speed indicator
- **Multiple Game States**: Menu, playing, paused, and game over screens
- **Collision Detection**: Comprehensive collision system for walls, obstacles, self, and food

### 🎯 Game Mechanics
- **Smart Obstacle Generation**: Procedurally generated levels with increasing difficulty
- **Invulnerability Frames**: Brief protection period after taking damage or advancing levels
- **Dynamic Difficulty**: More obstacles and food as you progress through levels
- **Wiggle Animation**: Realistic snake movement with body segments that follow naturally

## 🚀 Getting Started

### Prerequisites
```bash
pip install pygame
```

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/snake-adventure.git
cd snake-adventure
```

2. Run the game:
```bash
python snake_game.py
```

## 🎮 How to Play

1. **Start**: Click anywhere on the menu screen to begin
2. **Movement**: Move your mouse to guide the snake's head
3. **Objective**: Eat all food items to advance to the next level
4. **Survival**: Avoid walls, obstacles, and your own body
5. **Power-ups**: Collect purple food for temporary speed boosts
6. **Progression**: Each level adds more obstacles and food

### 🎯 Controls
- **Mouse**: Guide snake movement
- **P**: Pause/unpause game
- **ESC**: Return to menu or pause
- **R**: Restart after game over

## 📈 Scoring System

| Item | Points | Growth | Special Effect |
|------|--------|--------|----------------|
| Regular Food | 10 | +1 segment | - |
| Super Food | 50 | +3 segments | - |
| Power Food | 50 | +3 segments | 2x speed boost |

## 🏆 Game Features Breakdown

### Progressive Speed System
The snake starts slow and gradually increases speed based on food consumption:
- **Base Speed**: 15% (very manageable)
- **Speed Increment**: +2% per food item
- **Maximum Speed**: 80% (challenging but playable)
- **Visual Feedback**: Real-time speed meter

### Advanced Graphics
- **Segment Rendering**: Each body segment has proper thickness, color gradients, and positioning
- **Head Details**: Animated eyes, forked tongue, and directional awareness  
- **Food Animation**: Pulsing effects, glow auras, and sparkle animations
- **Environment**: Dynamic grass patterns and atmospheric backgrounds

### Collision System
- **Wall Collision**: Boundary detection with visual margins
- **Self Collision**: Prevents snake from eating itself (with grace period for small snakes)
- **Obstacle Collision**: 3D rendered rock obstacles with precise hit detection
- **Food Collection**: Optimized collision detection for smooth gameplay

## 🔧 Technical Details

- **Language**: Python 3.x
- **Framework**: Pygame
- **Resolution**: 1000x700 (configurable)
- **Frame Rate**: 60 FPS
- **Data Persistence**: JSON-based high score storage

## 🎨 Customization

The game is designed to be easily customizable:
- Modify colors in the drawing functions
- Adjust speed parameters in `GameStats` class
- Change food spawn rates and types
- Customize obstacle generation patterns
- Modify visual effects and animations

## 🤝 Contributing

Contributions are welcome! Areas for potential improvement:
- Sound effects and background music
- Additional power-up types
- New obstacle varieties
- Enhanced particle effects
- Mobile-friendly controls
- Multiplayer functionality

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Inspired by the classic Nokia Snake game
- Built with the amazing Pygame library
- Thanks to the Python gaming community for inspiration and resources

---

**Enjoy slithering! 🐍✨**

*Star this repository if you enjoyed the game and want to support its development!*
