
## **Tetris Game Requirements (Python + Pygame)**

### **1. General Overview**
Tetris is a tile-matching puzzle game where different shaped blocks (Tetrominoes) fall from the top of the screen. The player must rotate and move the blocks to create complete horizontal lines. When a full line is formed, it disappears, and the player earns points.

---

### **2. Functional Requirements**

#### **2.1 Game Window**
- The game window should have a fixed resolution (e.g., **400x600** pixels).
- The playing area consists of a **grid** (e.g., **10 columns × 20 rows**).
- A sidebar should display:
  - **Current Score**
  - **Next Tetromino**
  - **Level**

#### **2.2 Game Objects**
- **Tetrominoes:**
  - Seven types of Tetrominoes (I, O, T, S, Z, J, L).
  - Each piece moves down automatically at a fixed speed.
  - The player can move and rotate Tetrominoes before they lock into place.

- **Game Grid:**
  - A **10x20 grid** where Tetrominoes stack up.
  - When a **full row** is completed, the row disappears and all rows above shift down.
  - The game ends when **Tetrominoes stack up to the top** of the screen.

#### **2.3 Controls**
- **Move Left:** Left Arrow (`←`)
- **Move Right:** Right Arrow (`→`)
- **Move Down Faster:** Down Arrow (`↓`)
- **Rotate Tetromino:** Up Arrow (`↑`)
- **Drop Instantly:** Spacebar (`SPACE`)
- **Pause/Resume:** `P`
- **Restart:** `R`

#### **2.4 Scoring System**
- **Line Clears:**
  - 1 line cleared: **100 points**
  - 2 lines cleared: **300 points**
  - 3 lines cleared: **500 points**
  - 4 lines cleared (**Tetris**): **800 points**
- **Soft Drop Bonus:** Small points for manually moving Tetrominoes down faster.
- **Hard Drop Bonus:** More points for instantly dropping a Tetromino.

#### **2.5 Game Speed & Levels**
- The game starts at **Level 1**.
- The drop speed increases after every **10 cleared lines**.
- The level and speed should be displayed on the sidebar.

#### **2.6 Game Over and Restart**
- The game **ends** when Tetrominoes reach the top.
- A **"Game Over"** message should be displayed.
- Pressing `R` should restart the game.

#### **2.7 Sound Effects**
- A sound should play when a Tetromino **locks into place**.
- A sound should play when a **line clears**.
- A different sound should play for **hard drop**.
- Optional: Background music.

---

### **3. Technical Requirements**
- The game must be implemented using **Python (version 3.x)**.
- The **Pygame** library should be used for:
  - **Rendering** (Tetrominoes, grid, UI)
  - **Handling input events** (movement, rotation)
  - **Managing game loop and timing** (fall speed, updates)
- The game logic should be structured using **functions and/or object-oriented programming (OOP)**.
- The game should handle **collisions** properly (prevent pieces from overlapping).

---

### **4. Optional Enhancements**
- **Hold Piece:** Allow a player to store one Tetromino for later use.
- **Ghost Piece:** Show where the Tetromino will land before dropping.
- **Multiplayer Mode:** Compete with a second player or AI.
- **Special Effects:** Add animations for clearing lines.
- **Leaderboard:** Save high scores.

---
