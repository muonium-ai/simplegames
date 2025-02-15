# Snake Game Requirements

## Game Overview
Develop a Snake game using Pygame with two distinct modes: manual play and AI-controlled ("autosnake"). The game's score is based on both the time survived and the current length of the snake.

## User Interface
- **Startup Screen:**
  - Two buttons:
    - **Start Game:** Begin a standard human-controlled game.
    - **Autosnake:** Start the game in AI mode where the snake is controlled by an algorithm.
    
## Game Mechanics
- **Scoring:**
  - Display two scores during gameplay:
    - **Time Score:** The total time the snake has been playing.
    - **Length Score:** The current length of the snake.
    
- **Gameplay:**
  - Use Pygame for rendering and event handling.
  - The snake moves continuously and grows longer when it eats food.
  - Ensure smooth animations and responsive controls for manual mode.
  
## AI (Autosnake) Mode
- Implement an algorithm to control the snake automatically.
- The AI should focus on maximizing the score by:
  - Collecting food quickly while avoiding collisions.
  - Balancing the snake's length and travel time.
  
## Additional Considerations
- Maintain a clear separation between game logic and UI rendering.
- Ensure the game can switch between modes from the startup screen.
