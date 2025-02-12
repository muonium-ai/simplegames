# Hexagonal Maze Game Requirements

## Game Overview
A hexagonal grid-based maze game where players navigate through hexagonal cells from start to finish while tracking their path and distance traveled.

## Technical Requirements
- Python 3.x
- Pygame library
- Screen resolution: 800x850 pixels (800x800 maze + 50px control panel)
- Hex Grid: 15x15 hexagons

## Core Features

### Maze Generation
- Random maze generation using modified depth-first search for hexagonal grid
- Guaranteed path from start to finish
- Six possible directions for each cell
- Black walls and white paths
- Fixed start (top, green) and end points (bottom, red)

### Hexagonal Grid
- Offset coordinate system for hex grid
- Regular hexagon cells
- Proper hex-to-pixel coordinate conversion
- Smooth cell-to-cell navigation

### Player Movement
- Six directional movement (Q,W,E,A,S,D keys)
- Continuous movement when keys are held down
- Movement acceleration for smoother gameplay
- Collision detection with maze walls
- Yellow trail showing player's path
- Blue marker showing current position

### Game Features
1. Distance Tracking
   - Real-time display of distance traveled
   - Counter shown in bottom panel
   - Hex-appropriate distance calculations

2. Solve Feature
   - Auto-solve button in bottom panel
   - A* pathfinding adapted for hexagonal grid
   - Light blue highlight showing solution path
   - Automated movement along solution path

3. Game States
   - Active gameplay
   - Pause modal
   - Victory screen
   - Solution animation

### UI Elements
1. Main Game Screen
   - Hexagonal maze grid (15x15)
   - Bottom control panel
   - Solve button
   - Distance counter

2. Modal Windows
   - Game Won notification
   - Pause menu
   - Buttons:
     * Restart (140x40 pixels)
     * New Game (140x40 pixels)

### Color Scheme
- Walls: Black
- Paths: White
- Player: Blue
- Start: Green
- End: Red
- Player Trail: Yellow
- Solution Path: Light Blue
- Buttons: White with black text
- Modal Background: Semi-transparent black

### Controls
- Q,W,E,A,S,D Keys: Move in six directions
- Space: Trigger solve
- Mouse: Button interactions
- Click 'Solve': Start automatic pathfinding
- Click 'Restart': Reset current maze
- Click 'New Game': Generate new maze

### Game Flow
1. Start with random hexagonal maze
2. Player navigates using six-directional movement
3. Track movement and display hex-based distance
4. Show victory screen upon reaching goal
5. Option to restart same maze or generate new one

## Technical Considerations
1. Hex Grid Implementation
   - Axial coordinate system
   - Proper neighbor calculations
   - Accurate distance measurements
   - Correct rendering of hexagonal cells

2. Pathfinding Adaptations
   - Modified A* algorithm for hex grid
   - Six-directional movement costs
   - Proper heuristic function for hexagonal distance

3. Visual Rendering
   - Proper hexagon drawing
   - Correct cell overlap handling
   - Smooth transitions between cells