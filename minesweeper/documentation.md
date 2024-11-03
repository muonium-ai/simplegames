# Game Features

1. Basic Game Mechanics
   - Grid size: 30x16 cells
   - 99 mines
   - Cell size: 32x32 pixels
   - Left click to reveal cells
   - Right click to flag/unflag cells
   - Dual-click (both buttons) to reveal adjacent cells when number matches flags

2. UI Elements
   - Two-line header with game controls and information
   - Custom button system with hover effects
   - Input box for custom seeds
   - Dynamic button sizing and positioning
   - Status messages for game over and victory

3. Game Controls
   - New Game: Start fresh game with new seed
   - Restart Game: Restart with same seed
   - Quick Start: Auto-reveal 5 safe cells
   - Hint: Reveal one safe cell
   - Solve It: Auto-complete the game
   - Pause: Pause/Resume game timer

4. Visual Features
   - Custom images for mines and flags
   - Fallback to emoji symbols if images unavailable
   - Color-coded numbers (1-8)
   - Hover effects on buttons
   - Semi-transparent overlay for game over/victory
   - Cell highlighting and grid lines

5. Game Statistics
   - Time elapsed (with pause support)
   - Points system
   - Mines remaining counter
   - Hints used counter
   - Seed display/input

6. Advanced Features
   - Seed-based game generation
   - First click always safe
   - Quick start option
   - Hint system
   - Pause/Resume functionality
   - Auto-marking remaining mines
   - Victory detection
   - Dual-click chord feature

7. State Management
   - Cell states (Hidden, Revealed, Flagged)
   - Game states (Active, Paused, Victory, Game Over)
   - Timer management with pause support
   - Score tracking
   - Mine counting

8. Technical Features
   - Image loading with fallback
   - Dynamic UI scaling
   - Event handling system
   - Custom button class
   - Custom input box class
   - Error handling for resources
   - Configurable constants

9. Helper Functions
   - Reveal adjacent cells
   - Check for victory
   - Auto-mark mines
   - Handle both-click events
   - Draw message overlays
   - Calculate neighbor mines