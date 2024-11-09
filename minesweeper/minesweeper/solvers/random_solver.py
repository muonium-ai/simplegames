# solvers/random_solver.py

import random
from cell import CellState

class Solver:
    def __init__(self, game):
        self.game = game

    def next_move(self):
        # Find all hidden cells
        hidden_cells = [
            (x, y) for y in range(len(self.game.grid))
            for x in range(len(self.game.grid[0]))
            if self.game.grid[y][x].state == CellState.HIDDEN
        ]
        
        if hidden_cells:
            x, y = random.choice(hidden_cells)
            return (x, y, 'reveal')
        return None  # No moves available
