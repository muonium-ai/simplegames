# solvers/solver_constraint.py

class Solver:
    def __init__(self, grid):
        self.grid = grid

    def next_move(self):
        # Implement constraint propagation logic here
        # Return True if a move was made, False otherwise
        move_made = False
        for i in range(9):
            for j in range(9):
                cell = self.grid.cells[i][j]
                if cell.value == 0:
                    possible_values = self.get_possible_values(i, j)
                    if len(possible_values) == 1:
                        cell.value = possible_values.pop()
                        move_made = True
                        return True  # Move made
        return move_made

    def get_possible_values(self, row, col):
        values = set(range(1, 10))
        # Remove values from the same row
        values -= {self.grid.cells[row][i].value for i in range(9)}
        # Remove values from the same column
        values -= {self.grid.cells[i][col].value for i in range(9)}
        # Remove values from the same 3x3 square
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        values -= {
            self.grid.cells[r][c].value
            for r in range(start_row, start_row + 3)
            for c in range(start_col, start_col + 3)
        }
        return values
