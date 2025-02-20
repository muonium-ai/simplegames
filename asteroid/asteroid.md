
# Asteroid Game Requirements

## Game Initialization
```python
# Hide pygame support prompt
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
```

## Display Requirements
1. Resolution Options:
   - Standard: 800x600
   - HD: 1920x1080
2. Frame Rate: 60 FPS
3. Black background with white objects
4. Score display in top-left corner
5. Lives display in top-right corner

## Game Elements

### Player Ship
1. Controls:
   - Left/Right arrows for rotation
   - Up arrow for thrust
   - Space bar for shooting
2. Physics:
   - Momentum-based movement
   - Screen wrapping
   - Gradual speed decay
3. Properties:
   - 3 lives at start
   - Brief invulnerability after respawn
   - White triangle shape
   - Visible thrust effect

### Asteroids
1. Types:
   - Large (score: 20)
   - Medium (score: 50)
   - Small (score: 100)
2. Behavior:
   - Random initial direction
   - Constant speed based on size
   - Split into smaller pieces when hit
   - Screen wrapping
3. Generation:
   - Start with 4 large asteroids
   - New wave after clearing screen
   - Increasing number per wave

### Projectiles
1. Properties:
   - Limited lifetime (2 seconds)
   - Fixed speed
   - Maximum 4 active at once
2. Collision:
   - Single-hit destruction
   - Disappear on asteroid hit

### UFOs (Bonus Feature)
1. Types:
   - Large UFO (random shots)
   - Small UFO (aimed shots)
2. Behavior:
   - Appear randomly after wave 2
   - Cross screen horizontally
   - Shoot at player
3. Scoring:
   - Large UFO: 200 points
   - Small UFO: 1000 points

## Game Mechanics

### Scoring System
1. Point values:
   - Large Asteroid: 20
   - Medium Asteroid: 50
   - Small Asteroid: 100
   - Large UFO: 200
   - Small UFO: 1000
2. Extra life every 10,000 points

### Wave System
1. Wave progression:
   - Start with 4 asteroids
   - Each wave adds 2 asteroids
   - UFOs appear from wave 2
2. Difficulty increase:
   - Faster asteroids
   - More frequent UFOs
   - Better UFO aim

### Sound Effects
1. Required sounds:
   - Thrust
   - Shooting
   - Explosion (3 sizes)
   - UFO presence
   - UFO shooting
   - Extra life

### Menu System
1. Main Menu:
   - Start Game
   - High Scores
   - Controls
   - Quit
2. Pause Menu:
   - Resume
   - Restart
   - Main Menu
   - Quit

### High Score System
1. Features:
   - Top 10 scores
   - Name entry for high scores
   - Persistent storage
2. Display:
   - Score
   - Wave reached
   - Date achieved

## Technical Requirements
1. Python 3.x
2. Pygame library
3. Object-oriented design
4. Separate modules for:
   - Game engine
   - Entity management
   - Collision detection
   - Sound management
   - Score tracking

## Code Organization
1. Main Classes:
   - Game
   - Player
   - Asteroid
   - Projectile
   - UFO
   - ScoreManager
2. Helper Classes:
   - Vector2D
   - CollisionManager
   - SoundManager
   - MenuManager

## Development Guidelines
1. Clean code principles
2. Comprehensive comments
3. Type hints
4. Error handling
5. Frame rate independence
6. Configurable constants
