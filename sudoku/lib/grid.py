# lib/grid.py

import pygame
import random  # Import random module
from .cell import Cell
from .config import BLACK, TOP_OFFSET

class Grid:
    def __init__(self, board, width, height):
        self.rows = 9
        self.cols = 9
        self.cells = [
            [
                Cell(board[i][j], i, j, width, height, board[i][j] == 0)
                for j in range(9)
            ]
            for i in range(9)
        ]
        self.width = width
        self.height = height
        self.selected = None

    def draw(self, win):
        # Draw grid lines
        gap = self.width / 9
        for i in range(self.rows + 1):
            thickness = 4 if i % 3 == 0 else 1
            pygame.draw.line(
                win,
                BLACK,
                (0, i * gap + TOP_OFFSET),
                (self.width, i * gap + TOP_OFFSET),
                thickness,
            )
            pygame.draw.line(
                win,
                BLACK,
                (i * gap, TOP_OFFSET),
                (i * gap, self.height + TOP_OFFSET),
                thickness,
            )

        # Draw cells
        for row in self.cells:
            for cell in row:
                cell.draw(win)

    def click(self, pos):
        if pos[1] < TOP_OFFSET or pos[1] > self.height + TOP_OFFSET:
            return None
        gap = self.width / 9
        x = pos[0] // gap
        y = (pos[1] - TOP_OFFSET) // gap
        if x >= 0 and y >= 0 and x < 9 and y < 9:
            return (int(y), int(x))
        else:
            return None

    def select(self, row, col):
        for r in self.cells:
            for cell in r:
                cell.selected = False
        self.cells[row][col].selected = True
        self.selected = (row, col)

    def place(self, val):
        row, col = self.selected
        cell = self.cells[row][col]
        if cell.editable:
            if self.valid(val, row, col):
                cell.value = val
                return True
            else:
                return False

    def valid(self, val, row, col):
        # Check row
        for i in range(9):
            if self.cells[row][i].value == val and i != col:
                return False
        # Check column
        for i in range(9):
            if self.cells[i][col].value == val and i != row:
                return False
        # Check square
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                cell = self.cells[start_row + i][start_col + j]
                if cell.value == val and (start_row + i, start_col + j) != (row, col):
                    return False
        return True

    def highlight(self, num):
        for row in self.cells:
            for cell in row:
                cell.highlighted = cell.value == num

    def unhighlight(self):
        for row in self.cells:
            for cell in row:
                cell.highlighted = False

    def count_filled(self):
        filled = 0
        for row in self.cells:
            for cell in row:
                if cell.value != 0:
                    filled += 1
        return filled

    def is_solved(self):
        # Check if all cells are filled
        for row in self.cells:
            for cell in row:
                if cell.value == 0:
                    return False
        # Check rows
        for i in range(9):
            nums = []
            for j in range(9):
                val = self.cells[i][j].value
                if val in nums:
                    return False
                nums.append(val)
        # Check columns
        for i in range(9):
            nums = []
            for j in range(9):
                val = self.cells[j][i].value
                if val in nums:
                    return False
                nums.append(val)
        # Check squares
        for box_x in range(3):
            for box_y in range(3):
                nums = []
                for i in range(3):
                    for j in range(3):
                        val = self.cells[box_x * 3 + i][box_y * 3 + j].value
                        if val in nums:
                            return False
                        nums.append(val)
        return True

    def hint(self, solution_board):
        # Collect all empty cells
        empty_cells = [(i, j) for i in range(9) for j in range(9) if self.cells[i][j].value == 0]
        if not empty_cells:
            return False  # No empty cells

        # Choose a random empty cell
        i, j = random.choice(empty_cells)
        cell = self.cells[i][j]
        cell.value = solution_board[i][j]
        cell.editable = False  # Make the cell non-editable after hint
        cell.hinted = True  # Mark the cell as hinted
        return True  # Hint provided

    def solve(self, solution_board):
        # Fill in all empty cells
        for i in range(9):
            for j in range(9):
                cell = self.cells[i][j]
                if cell.value == 0:
                    cell.value = solution_board[i][j]
                    cell.editable = False  # Make cells non-editable after solving
