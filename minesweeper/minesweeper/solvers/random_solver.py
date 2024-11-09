# solvers/random_solver.py

import random
from cell import CellState

class Solver:
    def __init__(self, game, debug_mode=False):
        self.game = game
        self.debug_mode = debug_mode  # Enable debug mode for conditional printing

    def next_move(self):
        # Find all hidden cells
        hidden_cells = [
            (x, y) for y in range(len(self.game.grid))
            for x in range(len(self.game.grid[0]))
            if self.game.grid[y][x].state == CellState.HIDDEN
        ]
        
        if hidden_cells:
            x, y = random.choice(hidden_cells)
            if self.debug_mode:
                print(f"Randomly selected hidden cell at ({x}, {y}) to reveal")
            return (x, y, 'reveal')
        
        if self.debug_mode:
            print("No hidden cells left to reveal")
        return None  # No moves available
