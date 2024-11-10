# solvers/solver_example.py

class Solver:
    def __init__(self, grid):
        self.grid = grid

    def next_move(self):
        # Implement the solver logic here
        # Return True if a move was made, False otherwise
        empty_cell = self.find_empty()
        if not empty_cell:
            return False  # Puzzle is solved or no moves left
        else:
            row, col = empty_cell

        for num in range(1, 10):
            if self.grid.valid(num, row, col):
                self.grid.cells[row][col].value = num
                return True  # Move made

        return False  # No valid moves

    def find_empty(self):
        for i in range(9):
            for j in range(9):
                if self.grid.cells[i][j].value == 0:
                    return (i, j)
        return None
