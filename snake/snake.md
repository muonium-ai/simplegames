# Snake Game Requirements

## Game Overview
Develop a Snake game using Pygame with two distinct modes:
- **Manual Mode:** The player controls the snake via keyboard.
- **Autosnake Mode:** An AI controls the snake using simple logic to choose safe moves and avoid collisions.

The game score is based on both elapsed time and the current snake length.

## User Interface
- **Startup Screen:**
  - Two buttons:
    - **Start Game:** Launches manual mode.
    - **Autosnake:** Launches AI-controlled mode.
- **In-Game HUD:**
  - Displays elapsed time ("Time: X sec").
  - Displays snake length ("Length: Y").
  - Displays current speed ("Speed: Z FPS").
  - Two arrow buttons are provided to increase or decrease the snake speed (minimum 1 FPS, maximum 20 FPS).

## Game Mechanics
- **Window Dimensions:** 800x600 pixels.
- **Movement:**
  - The snake moves in blocks of 20 pixels.
  - Default speed is 5 FPS, adjustable via the arrow buttons during gameplay.
- **Food Placement:**
  - Food is spawned randomly away from window edges and never on top of any snake segment.
- **Snake Design:**
  - The snake’s head is rendered in yellow while the body is rendered in green.
- **Collision Detection:**
  - The snake collides with walls or its body (excluding the tail segment that is about to be removed) to trigger game over.
- **AI (Autosnake) Mode:**
  - The AI analyzes possible moves, evaluates safety (to avoid walls and self-collision), and selects the move that minimizes the distance to food.

## Additional Considerations
- Ensure smooth transitions between initial screens and gameplay.
- Maintain clear separation of game logic, AI behavior, and UI rendering.
- Responsive controls for manual mode and reliable feedback for speed adjustments.
