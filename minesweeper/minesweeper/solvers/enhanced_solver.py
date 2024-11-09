# solvers/enhanced_solver.py

import random
from cell import CellState
from config import GRID_WIDTH, GRID_HEIGHT

class Solver:
    def __init__(self, game, debug_mode=False):
        self.game = game
        self.debug_mode = debug_mode  # Set debug mode for conditional printing
        self.initial_move_made = False

    def next_move(self):
        # First move is random to start the game
        if not self.initial_move_made:
            self.initial_move_made = True
            x, y = self.random_hidden_cell()
            return x, y, 'reveal'

        # Iterate over the grid and apply logic for certain moves
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.game.grid[y][x]
                if cell.state == CellState.REVEALED and cell.neighbor_mines > 0:
                    hidden_neighbors, flagged_neighbors = self.get_neighbors(x, y)
                    
                    # Flagging move: If all hidden neighbors must be mines
                    if len(hidden_neighbors) == cell.neighbor_mines - len(flagged_neighbors):
                        for hx, hy in hidden_neighbors:
                            return hx, hy, 'flag'
                    
                    # Safe move: If all remaining neighbors are safe
                    if len(flagged_neighbors) == cell.neighbor_mines:
                        for hx, hy in hidden_neighbors:
                            return hx, hy, 'reveal'

        # If no certain move is available, use probabilistic guessing
        return self.probabilistic_guess()

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
        return None  # No hidden cells left

    def probabilistic_guess(self):
        """Guess a cell with the lowest probability of containing a mine."""
        probability_map = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Populate the probability map based on neighboring mines
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.game.grid[y][x]
                if cell.state == CellState.REVEALED and cell.neighbor_mines > 0:
                    hidden_neighbors, flagged_neighbors = self.get_neighbors(x, y)
                    remaining_mines = cell.neighbor_mines - len(flagged_neighbors)
                    
                    # Set probability for each hidden neighbor based on the remaining mine count
                    if hidden_neighbors:
                        probability = remaining_mines / len(hidden_neighbors)
                        for hx, hy in hidden_neighbors:
                            if probability_map[hy][hx] is None or probability_map[hy][hx] < probability:
                                probability_map[hy][hx] = probability

        # Find the cell with the lowest mine probability
        min_probability = float('inf')
        best_cell = None

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if probability_map[y][x] is not None and probability_map[y][x] < min_probability:
                    min_probability = probability_map[y][x]
                    best_cell = (x, y)

        # If a cell with low probability is found, reveal it; otherwise, choose randomly
        if best_cell:
            if self.debug_mode:
                print(f"Probabilistic guess at {best_cell} with mine probability: {min_probability}")
            return best_cell[0], best_cell[1], 'reveal'
        else:
            # Fall back to random choice if no probabilistic move is found
            x, y = self.random_hidden_cell()
            if self.debug_mode:
                print(f"No probabilistic move found, falling back to random cell at ({x}, {y})")
            return x, y, 'reveal'
