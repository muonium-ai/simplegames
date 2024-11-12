# solvers/advanced_solver.py

import random
from cell import CellState
from config import GRID_WIDTH, GRID_HEIGHT

class Solver:
    def __init__(self, game, debug_mode=False):
        self.game = game
        self.debug_mode = debug_mode
        self.initial_move_made = False

        # Flags to track cells that have been acted upon
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.game.grid[y][x]
                cell.is_flagged_in_game = False
                cell.is_revealed_in_game = False

    def next_move(self):
        # First move is random to start the game
        if not self.initial_move_made:
            self.initial_move_made = True
            move = self.random_hidden_cell()
            if move:
                x, y = move
                if self.debug_mode:
                    print(f"Initial random reveal at ({x}, {y})")
                return x, y, 'reveal'

        changes_made = True
        while changes_made:
            changes_made = False

            # Apply basic logical inference
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    cell = self.game.grid[y][x]
                    if cell.state == CellState.REVEALED and cell.neighbor_mines > 0:
                        hidden_neighbors, flagged_neighbors = self.get_neighbors(x, y)
                        remaining_mines = cell.neighbor_mines - len(flagged_neighbors)

                        # If remaining mines equal hidden neighbors, flag them
                        if remaining_mines == len(hidden_neighbors) and remaining_mines > 0:
                            for hx, hy in hidden_neighbors:
                                neighbor_cell = self.game.grid[hy][hx]
                                if not neighbor_cell.is_flagged_in_game:
                                    neighbor_cell.state = CellState.FLAGGED
                                    neighbor_cell.is_flagged_in_game = True
                                    self.game.mines_remaining -= 1
                                    changes_made = True
                                    if self.debug_mode:
                                        print(f"Flagged cell at ({hx}, {hy}) as Mine")
                        
                        # If remaining mines are zero, reveal hidden neighbors
                        if remaining_mines == 0 and hidden_neighbors:
                            for hx, hy in hidden_neighbors:
                                neighbor_cell = self.game.grid[hy][hx]
                                if not neighbor_cell.is_revealed_in_game:
                                    changes_made = True
                                    neighbor_cell.is_revealed_in_game = True
                                    if self.debug_mode:
                                        print(f"Revealed cell at ({hx}, {hy}) as Safe")
                                    return hx, hy, 'reveal'

            # Apply overlapping constraints
            if self.apply_overlapping_constraints():
                changes_made = True

        # After applying inference rules, make moves based on the deductions
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.game.grid[y][x]
                if cell.state == CellState.FLAGGED and not cell.is_flagged_in_game:
                    self.game.mines_remaining -= 1
                    cell.is_flagged_in_game = True
                    if self.debug_mode:
                        print(f"Flagged cell at ({x}, {y}) as Mine")
                    return x, y, 'flag'
                elif cell.state == CellState.REVEALED and not cell.is_revealed_in_game:
                    cell.is_revealed_in_game = True
                    if self.debug_mode:
                        print(f"Revealed cell at ({x}, {y})")
                    return x, y, 'reveal'

        # If no certain moves are available, use CSP solver
        if self.csp_solver():
            return self.next_move()

        # If no moves from CSP solver, proceed to probabilistic guessing
        return self.probabilistic_guess()

    def get_neighbors(self, x, y):
        """Return lists of hidden and flagged neighbors around a given cell."""
        hidden_neighbors = []
        flagged_neighbors = []
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),         (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]

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
        probability_map = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        counts = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        # Populate the probability map based on neighboring mines
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.game.grid[y][x]
                if cell.state == CellState.REVEALED and cell.neighbor_mines > 0:
                    hidden_neighbors, flagged_neighbors = self.get_neighbors(x, y)
                    remaining_mines = cell.neighbor_mines - len(flagged_neighbors)

                    if hidden_neighbors:
                        probability = remaining_mines / len(hidden_neighbors)
                        for hx, hy in hidden_neighbors:
                            probability_map[hy][hx] += probability
                            counts[hy][hx] += 1

        # Calculate average probabilities
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if counts[y][x] > 0:
                    probability_map[y][x] /= counts[y][x]
                else:
                    probability_map[y][x] = 1  # Assume worst if no info

        # Find the cell with the lowest mine probability
        min_probability = float('inf')
        best_cell = None

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.game.grid[y][x].state == CellState.HIDDEN:
                    prob = probability_map[y][x]
                    if prob < min_probability:
                        min_probability = prob
                        best_cell = (x, y)

        # If a cell with low probability is found, reveal it; otherwise, choose randomly
        if best_cell:
            if self.debug_mode:
                print(f"Probabilistic guess at {best_cell} with mine probability: {min_probability}")
            return best_cell[0], best_cell[1], 'reveal'
        else:
            # Fall back to random choice if no probabilistic move is found
            hidden_cell = self.random_hidden_cell()
            if hidden_cell is None:
                return None  # No moves left
            x, y = hidden_cell
            if self.debug_mode:
                print(f"No probabilistic move found, falling back to random cell at ({x}, {y})")
            return x, y, 'reveal'

    def apply_overlapping_constraints(self):
        """Apply advanced logical inference using overlapping constraints."""
        changes_made = False
        opened_cells = [
            (x, y) for y in range(GRID_HEIGHT)
            for x in range(GRID_WIDTH)
            if self.game.grid[y][x].state == CellState.REVEALED and self.game.grid[y][x].neighbor_mines >= 0
        ]

        for idx, (x1, y1) in enumerate(opened_cells):
            cell1 = self.game.grid[y1][x1]
            hidden_neighbors1, flagged_neighbors1 = self.get_neighbors(x1, y1)
            remaining_mines1 = cell1.neighbor_mines - len(flagged_neighbors1)

            for x2, y2 in opened_cells[idx+1:]:
                cell2 = self.game.grid[y2][x2]
                hidden_neighbors2, flagged_neighbors2 = self.get_neighbors(x2, y2)
                remaining_mines2 = cell2.neighbor_mines - len(flagged_neighbors2)

                # Find common and unique hidden neighbors
                common_hidden = set(hidden_neighbors1) & set(hidden_neighbors2)
                unique1 = set(hidden_neighbors1) - common_hidden
                unique2 = set(hidden_neighbors2) - common_hidden

                # If unique1's remaining mines are the same as unique2's, flag them
                if remaining_mines1 > remaining_mines2 and unique1:
                    difference = remaining_mines1 - remaining_mines2
                    if difference == len(unique1):
                        for hx, hy in unique1:
                            neighbor_cell = self.game.grid[hy][hx]
                            if neighbor_cell.state == CellState.HIDDEN and not neighbor_cell.is_flagged_in_game:
                                neighbor_cell.state = CellState.FLAGGED
                                neighbor_cell.is_flagged_in_game = True
                                self.game.mines_remaining -= 1
                                changes_made = True
                                if self.debug_mode:
                                    print(f"Flagged (overlap) cell at ({hx}, {hy}) as Mine")
                elif remaining_mines2 > remaining_mines1 and unique2:
                    difference = remaining_mines2 - remaining_mines1
                    if difference == len(unique2):
                        for hx, hy in unique2:
                            neighbor_cell = self.game.grid[hy][hx]
                            if neighbor_cell.state == CellState.HIDDEN and not neighbor_cell.is_flagged_in_game:
                                neighbor_cell.state = CellState.FLAGGED
                                neighbor_cell.is_flagged_in_game = True
                                self.game.mines_remaining -= 1
                                changes_made = True
                                if self.debug_mode:
                                    print(f"Flagged (overlap) cell at ({hx}, {hy}) as Mine")

        return changes_made

    def csp_solver(self):
        """Attempt to solve using a basic CSP solver."""
        # Collect variables (hidden cells adjacent to numbers)
        variables = set()
        constraints = []
        variable_indices = {}
        index = 0

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.game.grid[y][x]
                if cell.state == CellState.REVEALED and cell.neighbor_mines > 0:
                    hidden_neighbors, flagged_neighbors = self.get_neighbors(x, y)
                    remaining_mines = cell.neighbor_mines - len(flagged_neighbors)
                    if hidden_neighbors:
                        constraints.append({
                            'cells': hidden_neighbors,
                            'total_mines': remaining_mines
                        })
                        for var in hidden_neighbors:
                            variables.add(var)

        variables = list(variables)
        if not variables:
            return False  # No variables to assign

        # Assign variables to a consistent state using backtracking
        assignment = {}
        result = self.backtrack(variables, constraints, assignment)
        if result:
            # Use the assignment to make moves
            for (x, y), value in assignment.items():
                cell = self.game.grid[y][x]
                if value == 'Mine' and not cell.is_flagged_in_game:
                    cell.state = CellState.FLAGGED
                    cell.is_flagged_in_game = True
                    self.game.mines_remaining -= 1
                    if self.debug_mode:
                        print(f"Flagged cell at ({x}, {y}) as Mine via CSP")
                    return True
                elif value == 'Safe' and not cell.is_revealed_in_game:
                    cell.is_revealed_in_game = True
                    if self.debug_mode:
                        print(f"Revealed cell at ({x}, {y}) as Safe via CSP")
                    return True
            return False
        return False  # No assignment found

    def backtrack(self, variables, constraints, assignment):
        if len(assignment) == len(variables):
            if self.check_constraints(constraints, assignment):
                return assignment
            else:
                return None

        var = variables[len(assignment)]
        for value in ['Safe', 'Mine']:
            assignment[var] = value
            if self.check_constraints(constraints, assignment):
                result = self.backtrack(variables, constraints, assignment)
                if result:
                    return result
            del assignment[var]
        return None

    def check_constraints(self, constraints, assignment):
        for constraint in constraints:
            cells = constraint['cells']
            total_mines = constraint['total_mines']
            mine_count = 0
            unknown_cells = 0
            for cell in cells:
                if cell in assignment:
                    if assignment[cell] == 'Mine':
                        mine_count += 1
                else:
                    unknown_cells += 1
            # If mine_count exceeds total_mines, constraint is violated
            if mine_count > total_mines:
                return False
            # If remaining mines cannot be placed in unknown cells, constraint is violated
            if mine_count + unknown_cells < total_mines:
                return False
        return True
