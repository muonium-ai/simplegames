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
        self.x = 0
        self.y = 0
        self.simple_probability = 0
        self.adjacent_probability = 0

class Minesweeper:
    def __init__(self, width, height, mine_count):
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.victory = False
        self.first_click = True
        self.reveals = 0
        self.flags = 0
        self.hidden_remaining = width * height
        self.steps = 0
        self.initial_probability = mine_count / (width * height)

        for y in range(height):
            for x in range(width):
                self.grid[y][x].x = x
                self.grid[y][x].y = y

    def place_mines(self, safe_x, safe_y):
        safe_cells = {(safe_x, safe_y)}
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = safe_x + dx, safe_y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    safe_cells.add((nx, ny))

        all_positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        possible_mine_positions = [pos for pos in all_positions if pos not in safe_cells]
        mine_positions = random.sample(possible_mine_positions, self.mine_count)

        for x, y in mine_positions:
            self.grid[y][x].is_mine = True

        for x, y in mine_positions:
            for nx, ny in self.get_neighbors(x, y):
                self.grid[ny][nx].neighbor_mines += 1

    def get_neighbors(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    yield nx, ny

    def reveal(self, x, y):
        if self.first_click:
            self.place_mines(x, y)
            self.first_click = False

        cell = self.grid[y][x]
        if cell.state == CellState.HIDDEN:
            cell.state = CellState.REVEALED
            self.reveals += 1
            self.hidden_remaining -= 1
            self.steps += 1
            if cell.is_mine:
                self.game_over = True
                self.victory = False
            else:
                if cell.neighbor_mines == 0:
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                self.reveal(nx, ny)
                self.check_victory()
            self.update_probabilities()

    def flag(self, x, y):
        cell = self.grid[y][x]
        if cell.state == CellState.HIDDEN:
            cell.state = CellState.FLAGGED
            self.flags += 1
            self.steps += 1
        elif cell.state == CellState.FLAGGED:
            cell.state = CellState.HIDDEN
            self.flags -= 1
            self.steps += 1
        self.update_probabilities()

    def update_probabilities(self):
        for row in self.grid:
            for cell in row:
                if cell.state == CellState.HIDDEN:
                    cell.simple_probability = self.calculate_simple_probability(cell)
                    cell.adjacent_probability = self.calculate_adjacent_probability(cell)

    def check_victory(self):
        for row in self.grid:
            for cell in row:
                if cell.state == CellState.HIDDEN and not cell.is_mine:
                    return
        self.game_over = True
        self.victory = True
    
    def print_solution(self):
        for row in self.grid:
            line = []
            for cell in row:
                if cell.is_mine:
                    line.append('*')
                else:
                    line.append(str(cell.neighbor_mines))
            print(' '.join(line))

    def get_status(self):
        return {
            'reveals': self.reveals,
            'flags': self.flags,
            'hidden_remaining': self.hidden_remaining,
            'steps': self.steps,
            'game_over': self.game_over,
            'victory': self.victory
        }

    def get_current_board_status(self):
        board_status = []
        for row in self.grid:
            line = []
            for cell in row:
                if cell.state == CellState.HIDDEN:
                    line.append('.')
                elif cell.state == CellState.FLAGGED:
                    line.append('F')
                elif cell.is_mine:
                    line.append('*')
                else:
                    line.append(str(cell.neighbor_mines))
            board_status.append(line)
        return board_status

    def get_mine_probabilities(self):
        probabilities = []
        for row in self.grid:
            line = []
            for cell in row:
                if cell.state == CellState.HIDDEN:
                    prob = cell.adjacent_probability if cell.adjacent_probability > 0 else cell.simple_probability
                    line.append(int(prob))
                else:
                    line.append(' ')
            probabilities.append(line)
        return probabilities

    def calculate_simple_probability(self, cell):
        if cell.state != CellState.HIDDEN:
            return 0

        unopened_neighbors = 0
        marked_neighbors = 0
        for nx, ny in self.get_neighbors(cell.x, cell.y):
            neighbor = self.grid[ny][nx]
            if neighbor.state == CellState.HIDDEN:
                unopened_neighbors += 1
            elif neighbor.state == CellState.FLAGGED:
                marked_neighbors += 1

        if unopened_neighbors == 0:
            return 0

        remaining_mines = self.mine_count - self.flags
        probability = (remaining_mines - marked_neighbors) / unopened_neighbors

        # Convert to percentage and ensure it is between 1% and 99%
        probability_percentage = int(probability)  #max(1, min(99, int(probability * 100)))

        return probability_percentage

    def calculate_adjacent_probability(self, cell):
        if cell.state != CellState.HIDDEN:
            return 0

        adjacent_probability = 0
        for nx, ny in self.get_neighbors(cell.x, cell.y):
            neighbor = self.grid[ny][nx]
            if neighbor.state == CellState.REVEALED and neighbor.neighbor_mines > 0:
                unopened_neighbors = 0
                marked_neighbors = 0
                for nnx, nny in self.get_neighbors(neighbor.x, neighbor.y):
                    n_neighbor = self.grid[nny][nnx]
                    if n_neighbor.state == CellState.HIDDEN:
                        unopened_neighbors += 1
                    elif n_neighbor.state == CellState.FLAGGED:
                        marked_neighbors += 1

                if unopened_neighbors > 0:
                    remaining_mines = neighbor.neighbor_mines - marked_neighbors
                    probability = remaining_mines / unopened_neighbors
                    adjacent_probability = max(adjacent_probability, probability)

        # Convert to percentage and ensure it is between 1% and 99%
        probability_percentage = int(adjacent_probability) #max(1, min(99, int(adjacent_probability * 100)))

        return probability_percentage