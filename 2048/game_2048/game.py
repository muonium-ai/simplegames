import random
from typing import List, Tuple, Dict
from game_2048.constants import GAME_SIZE

class Game2048:
    def __init__(self):
        self.grid = [[0 for _ in range(GAME_SIZE)] for _ in range(GAME_SIZE)]
        self.score = 0
        self.total_moves = 0
        self.highest_tile = 0
        self.max_tile = 2
        self.milestones = {2048: False, 4096: False, 8192: False, 
                          16384: False, 32768: False, 65536: False}
        self.add_new_tile()
        self.add_new_tile()

    def get_state(self) -> Dict:
        return {
            'grid': self.grid,
            'score': self.score,
            'moves': self.total_moves,
            'max_tile': self.max_tile,
            'highest_tile': self.highest_tile,
            'game_over': self.is_game_over(),
            'won': self.has_won()
        }

    def add_new_tile(self) -> None:
        empty_cells = [(i, j) for i in range(GAME_SIZE) 
                      for j in range(GAME_SIZE) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4
            self.update_highest_tile()

    def update_highest_tile(self) -> None:
        current_max = max(max(row) for row in self.grid)
        if current_max > self.highest_tile:
            self.highest_tile = current_max
            self.max_tile = current_max
            for milestone in sorted(self.milestones.keys()):
                if current_max >= milestone and not self.milestones[milestone]:
                    self.milestones[milestone] = True

    def move(self, direction: str) -> bool:
        original_grid = [row[:] for row in self.grid]
        
        if direction in ['UP', 'DOWN']:
            self.transpose()
        if direction in ['RIGHT', 'DOWN']:
            self.reverse()

        moved = False
        score_added = 0
        
        # Compress and merge
        self.compress()
        score_added = self.merge()
        self.compress()

        if direction in ['RIGHT', 'DOWN']:
            self.reverse()
        if direction in ['UP', 'DOWN']:
            self.transpose()

        # Check if grid changed
        if original_grid != self.grid:
            moved = True
            self.score += score_added
            self.total_moves += 1
            self.add_new_tile()

        return moved

    def compress(self) -> None:
        new_grid = [[0 for _ in range(GAME_SIZE)] for _ in range(GAME_SIZE)]
        for i in range(GAME_SIZE):
            pos = 0
            for j in range(GAME_SIZE):
                if self.grid[i][j] != 0:
                    new_grid[i][pos] = self.grid[i][j]
                    pos += 1
        self.grid = new_grid

    def merge(self) -> int:
        score = 0
        for i in range(GAME_SIZE):
            for j in range(GAME_SIZE-1):
                if self.grid[i][j] == self.grid[i][j+1] and self.grid[i][j] != 0:
                    self.grid[i][j] *= 2
                    self.grid[i][j+1] = 0
                    score += self.grid[i][j]
        return score

    def reverse(self) -> None:
        self.grid = [row[::-1] for row in self.grid]

    def transpose(self) -> None:
        self.grid = [[self.grid[j][i] for j in range(GAME_SIZE)] 
                    for i in range(GAME_SIZE)]

    def is_game_over(self) -> bool:
        # Check for empty cells
        if any(0 in row for row in self.grid):
            return False

        # Check for possible merges
        for i in range(GAME_SIZE):
            for j in range(GAME_SIZE-1):
                if self.grid[i][j] == self.grid[i][j+1]:
                    return False
                if self.grid[j][i] == self.grid[j+1][i]:
                    return False
        return True

    def has_won(self) -> bool:
        return self.highest_tile >= 65536
