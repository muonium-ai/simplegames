# Snake Game Requirements

## Game Overview
Develop a Snake game using Pygame with two distinct modes:
- **Manual Mode:** The player controls the snake via keyboard.
- **Autosnake Mode:** An AI controls the snake using simple logic that avoids wall collisions.

The game score is based on both the elapsed time and the current length of the snake.

## User Interface
- **Startup Screen:**
  - Two buttons:
    - **Start Game:** Launches the manual mode.
    - **Autosnake:** Launches the AI-controlled mode.
- **In-Game HUD:**
  - Display the elapsed time ("Time: X sec").
  - Display the current snake length ("Length: Y").
  - Display the speed level ("Speed: Slow").

## Game Mechanics
- **Window Dimensions:** 800x600 pixels.
- **Snake Movement:**
  - The snake moves in blocks of 20 pixels.
  - The game runs at 5 FPS (providing a slower snake speed).
- **Food Placement:**
  - Food items are placed randomly but always away from the window edges.
- **Snake Design:**
  - The snake’s head is drawn in a different color (yellow) than the body (green).

## AI (Autosnake) Mode
- Implement AI logic that:
  - Directs the snake toward the food.
  - Avoids wall collisions by evaluating possible moves and selecting safe directions.

## Additional Considerations
- Ensure smooth transitions between the startup screen and gameplay.
- Maintain separation between game logic, AI behavior, and UI rendering.
- Aim for clear and responsive controls for the manual mode.
