from enum import Enum
import random

class CellState(Enum):
    HIDDEN = 0
    REVEALED = 1
    FLAGGED = 2

class Cell:
    def __init__(self, is_mine=False):
        self.is_mine = is_mine
        self.state = CellState.HIDDEN
        self.neighbor_mines = 0

class Minesweeper:
    def __init__(self, width, height, mine_count):
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.first_click = True

    def place_mines(self, safe_x, safe_y):
        positions = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) != (safe_x, safe_y)
        ]
        mine_positions = random.sample(positions, self.mine_count)
        for x, y in mine_positions:
            self.grid[y][x].is_mine = True
        self.update_neighbors()

    def update_neighbors(self):
        for y in range(self.height):
            for x in range(self.width):
                if not self.grid[y][x].is_mine:
                    self.grid[y][x].neighbor_mines = sum(
                        1 for nx, ny in self.get_neighbors(x, y)
                        if self.grid[ny][nx].is_mine
                    )

    def get_neighbors(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    yield nx, ny

    def reveal(self, x, y):
        if self.game_over or self.grid[y][x].state != CellState.HIDDEN:
            return
        if self.first_click:
            self.place_mines(x, y)
            self.first_click = False

        cell = self.grid[y][x]
        cell.state = CellState.REVEALED

        if cell.is_mine:
            self.game_over = True
            return

        if cell.neighbor_mines == 0:
            for nx, ny in self.get_neighbors(x, y):
                self.reveal(nx, ny)

    def flag(self, x, y):
        cell = self.grid[y][x]
        if cell.state == CellState.HIDDEN:
            cell.state = CellState.FLAGGED
        elif cell.state == CellState.FLAGGED:
            cell.state = CellState.HIDDEN

    def check_victory(self):
        for row in self.grid:
            for cell in row:
                if cell.state == CellState.HIDDEN and not cell.is_mine:
                    return False
        return True
