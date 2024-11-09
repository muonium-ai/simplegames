# solvers/simple_solver.py

import random
from cell import CellState
from config import GRID_WIDTH, GRID_HEIGHT

class Solver:
    def __init__(self, game, debug_mode=False):
        self.game = game
        self.debug_mode = debug_mode  # Enable debug mode for conditional printing
        self.initial_move_made = False

    def next_move(self):
        # First move is random to start the game
        if not self.initial_move_made:
            self.initial_move_made = True
            x, y = self.random_hidden_cell()
            if self.debug_mode:
                print(f"Initial random move at ({x}, {y}) to start the game.")
            return x, y, 'reveal'

        # Analyze the board for moves
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.game.grid[y][x]
                
                if cell.state == CellState.REVEALED and cell.neighbor_mines > 0:
                    hidden_neighbors, flagged_neighbors = self.get_neighbors(x, y)
                    
                    # Reveal all safe cells
                    if len(flagged_neighbors) == cell.neighbor_mines:
                        for hx, hy in hidden_neighbors:
                            if self.debug_mode:
                                print(f"Safe cell found at ({hx}, {hy}), revealing it.")
                            return hx, hy, 'reveal'
                    
                    # Flag cells that must be mines
                    if len(hidden_neighbors) == cell.neighbor_mines:
                        for hx, hy in hidden_neighbors:
                            if self.debug_mode:
                                print(f"Cell at ({hx}, {hy}) must be a mine, flagging it.")
                            return hx, hy, 'flag'

        # If no logical move is available, make a random move
        x, y = self.random_hidden_cell()
        if self.debug_mode:
            print(f"No logical move found, choosing random hidden cell at ({x}, {y}) to reveal.")
        return x, y, 'reveal'

    def get_neighbors(self, x, y):
        """Return lists of hidden and flagged neighbors around a given cell."""
        hidden_neighbors = []
        flagged_neighbors = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                neighbor = self.game.grid[ny][nx]
                if neighbor.state == CellState.HIDDEN:
                    hidden_neighbors.append((nx, ny))
                elif neighbor.state == CellState.FLAGGED:
                    flagged_neighbors.append((nx, ny))
                    
        if self.debug_mode:
            print(f"Cell at ({x}, {y}) has {len(hidden_neighbors)} hidden and {len(flagged_neighbors)} flagged neighbors.")
        
        return hidden_neighbors, flagged_neighbors

    def random_hidden_cell(self):
        """Return a random hidden cell to reveal."""
        hidden_cells = [
            (x, y) for y in range(GRID_HEIGHT)
            for x in range(GRID_WIDTH)
            if self.game.grid[y][x].state == CellState.HIDDEN
        ]
        
        if hidden_cells:
            return random.choice(hidden_cells)
        
        if self.debug_mode:
            print("No hidden cells left to reveal.")
        return None  # No hidden cells left
