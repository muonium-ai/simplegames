# Multi-Snake Game Requirements

## Game Overview
- Built using Pygame library
- Multiple AI-controlled snakes competing simultaneously
- Real-time gameplay with timer display
- Automated winner tracking system

## Technical Requirements

### Display
1. Window size: 800x600 pixels
2. Game grid: 40x30 cells
3. Timer display in top-right corner
4. Snake colors:
   - Each snake assigned unique color from preset palette
   - Minimum 4 different colors available

### Game Mechanics
1. Snake Movement
   - Grid-based movement
   - Constant speed for all snakes
   - Collision detection with walls and other snakes
   - Growth mechanics when consuming food

2. Food System
   - Random food placement
   - Single food item at a time
   - Food regenerates after consumption

### AI Requirements
1. Multiple AI Algorithms
   - Basic pathfinding algorithm
   - Advanced algorithm with obstacle avoidance
   - Survival-focused algorithm
   
2. AI Behavior
   - Food tracking
   - Collision avoidance
   - Territory control

### Scoring System
1. Winner List Display
   - Snake color
   - Final length
   - Survival time
   - Ranking based on length and survival time

### Game Flow
1. Start screen with AI algorithm selection
2. Main game loop with timer
3. Game over screen showing winner list
4. Option to restart with different AI combinations

## Technical Implementation
1. Python 3.x
2. Pygame library
3. Object-oriented design for snake and AI classes
4. Separate modules for:
   - Game engine
   - AI algorithms
   - Display handling
   - Score tracking
