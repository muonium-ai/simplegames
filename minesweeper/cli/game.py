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
        self.hints = 0  # Initialize hints count
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
                if dx == 0 and dy == 0:
                    continue
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
                    for nx, ny in self.get_neighbors(x, y):
                        self.reveal(nx, ny)
                self.check_victory()
            self.update_probabilities()

    def flag(self, x, y):
        cell = self.grid[y][x]
        if cell.state == CellState.HIDDEN:
            if self.flags < self.mine_count:
                cell.state = CellState.FLAGGED
                self.flags += 1
                self.steps += 1
                self.hidden_remaining -= 1
                self.update_probabilities()
        elif cell.state == CellState.FLAGGED:
            cell.state = CellState.HIDDEN
            self.flags -= 1
            self.steps += 1
            self.hidden_remaining += 1
            self.update_probabilities()

    def update_probabilities(self):
        remaining_mines = self.mine_count - self.flags
        total_hidden_cells = sum(cell.state == CellState.HIDDEN for row in self.grid for cell in row)

        if total_hidden_cells == 0:
            base_probability = 0
        else:
            base_probability = remaining_mines / total_hidden_cells

        for row in self.grid:
            for cell in row:
                if cell.state == CellState.HIDDEN:
                    cell.simple_probability = max(0, min(99, int(base_probability * 100)))
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
            'victory': self.victory,
            'total_mines': self.mine_count,
            'remaining_mines': self.mine_count - self.flags,
            'hints': self.hints  # Include hints count
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
                    prob = max(0, cell.adjacent_probability if cell.adjacent_probability > 0 else cell.simple_probability)
                    line.append(int(prob))
                else:
                    line.append(' ')
            probabilities.append(line)
        return probabilities

    def calculate_simple_probability(self, cell):
        if cell.state != CellState.HIDDEN:
            return 0

        unopened_neighbors = 0
        for nx, ny in self.get_neighbors(cell.x, cell.y):
            neighbor = self.grid[ny][nx]
            if neighbor.state == CellState.HIDDEN:
                unopened_neighbors += 1

        if unopened_neighbors == 0:
            return 0

        remaining_mines = self.mine_count - self.flags
        probability = remaining_mines / unopened_neighbors

        # Ensure probability is not negative
        probability = max(0, probability)

        # Convert to percentage and ensure it is between 0% and 99%
        probability_percentage = max(0, min(99, int(probability * 100)))

        return probability_percentage

    def calculate_adjacent_probability(self, cell):
        if cell.state != CellState.HIDDEN:
            return 0

        max_probability = 0
        for nx, ny in self.get_neighbors(cell.x, cell.y):
            neighbor = self.grid[ny][nx]
            if neighbor.state == CellState.REVEALED and neighbor.neighbor_mines > 0:
                flagged_neighbors = 0
                hidden_neighbors = 0
                for nnx, nny in self.get_neighbors(neighbor.x, neighbor.y):
                    n_cell = self.grid[nny][nnx]
                    if n_cell.state == CellState.FLAGGED:
                        flagged_neighbors += 1
                    elif n_cell.state == CellState.HIDDEN:
                        hidden_neighbors += 1
                remaining_mines = neighbor.neighbor_mines - flagged_neighbors

                # Ensure remaining mines and hidden neighbors are not negative
                remaining_mines = max(0, remaining_mines)
                hidden_neighbors = max(1, hidden_neighbors)  # Avoid division by zero

                probability = remaining_mines / hidden_neighbors

                # Ensure probability is not negative
                probability = max(0, probability)

                probability_percentage = max(0, min(99, int(probability * 100)))
                max_probability = max(max_probability, probability_percentage)
        return max_probability
    
    def hint(self):
        unmarked_non_mine_cells = [(x, y) for y in range(self.height) for x in range(self.width)
                                   if self.grid[y][x].state == CellState.HIDDEN and not self.grid[y][x].is_mine]
        if unmarked_non_mine_cells:
            x, y = random.choice(unmarked_non_mine_cells)
            self.reveal(x, y)
            self.hints += 1
        self.check_victory()
        return x, y

    def automark(self, x, y):
        cell = self.grid[y][x]
        if cell.state == CellState.REVEALED and cell.neighbor_mines > 0:
            flagged_neighbors = 0
            unmarked_neighbors = []
            for nx, ny in self.get_neighbors(x, y):
                neighbor = self.grid[ny][nx]
                if neighbor.state == CellState.FLAGGED:
                    flagged_neighbors += 1
                elif neighbor.state == CellState.HIDDEN:
                    unmarked_neighbors.append((nx, ny))
            if flagged_neighbors == cell.neighbor_mines:
                for nx, ny in unmarked_neighbors:
                    self.reveal(nx, ny)

    def pattern_recognition(self):
        print("Starting pattern recognition...")
        pattern_found = False
        self.print_solution()  # Do not remove, for debugging

        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]

                # Check vertical "1-2-1" pattern
                if 0 < y < self.height - 1:
                    top_cell = self.grid[y - 1][x]
                    middle_cell = cell
                    bottom_cell = self.grid[y + 1][x]

                    if (top_cell.state == CellState.REVEALED and top_cell.neighbor_mines == 1 and
                        middle_cell.state == CellState.REVEALED and middle_cell.neighbor_mines == 2 and
                        bottom_cell.state == CellState.REVEALED and bottom_cell.neighbor_mines == 1):

                        top_hidden = set(self.get_hidden_neighbors(x, y - 1))
                        middle_hidden = set(self.get_hidden_neighbors(x, y))
                        bottom_hidden = set(self.get_hidden_neighbors(x, y + 1))

                        # Mines are hidden cells common between middle and side cells
                        mines_to_flag = (top_hidden & middle_hidden) | (bottom_hidden & middle_hidden)
                        safe_cells = middle_hidden - (top_hidden | bottom_hidden)

                        if mines_to_flag or safe_cells:
                            pattern_found = True
                            print(f"121 pattern found vertically at ({x}, {y})")
                            print(f"Top hidden: {top_hidden}")
                            print(f"Middle hidden: {middle_hidden}")
                            print(f"Bottom hidden: {bottom_hidden}")
                            print(f"Mines to flag: {mines_to_flag}")
                            print(f"Safe cells to reveal: {safe_cells}")

                            # Flag mines
                            if mines_to_flag:
                                for mx, my in mines_to_flag:
                                    self.flag(mx, my)
                                    print(f"Flagging cell at ({mx}, {my})")

                            # Reveal safe cells
                            if safe_cells:
                                for sx, sy in safe_cells:
                                    self.reveal(sx, sy)
                                    print(f"Revealing cell at ({sx}, {sy})")

                # Check horizontal "1-2-1" pattern
                if 0 < x < self.width - 1:
                    left_cell = self.grid[y][x - 1]
                    middle_cell = cell
                    right_cell = self.grid[y][x + 1]

                    if (left_cell.state == CellState.REVEALED and left_cell.neighbor_mines == 1 and
                        middle_cell.state == CellState.REVEALED and middle_cell.neighbor_mines == 2 and
                        right_cell.state == CellState.REVEALED and right_cell.neighbor_mines == 1):

                        left_hidden = set(self.get_hidden_neighbors(x - 1, y))
                        middle_hidden = set(self.get_hidden_neighbors(x, y))
                        right_hidden = set(self.get_hidden_neighbors(x + 1, y))

                        # Mines are hidden cells common between middle and side cells
                        mines_to_flag = (left_hidden & middle_hidden) | (right_hidden & middle_hidden)
                        safe_cells = middle_hidden - (left_hidden | right_hidden)

                        if mines_to_flag or safe_cells:
                            pattern_found = True
                            print(f"121 pattern found horizontally at ({x}, {y})")
                            print(f"Left hidden: {left_hidden}")
                            print(f"Middle hidden: {middle_hidden}")
                            print(f"Right hidden: {right_hidden}")
                            print(f"Mines to flag: {mines_to_flag}")
                            print(f"Safe cells to reveal: {safe_cells}")

                            # Flag mines
                            if mines_to_flag:
                                for mx, my in mines_to_flag:
                                    self.flag(mx, my)
                                    print(f"Flagging cell at ({mx}, {my})")

                            # Reveal safe cells
                            if safe_cells:
                                for sx, sy in safe_cells:
                                    self.reveal(sx, sy)
                                    print(f"Revealing cell at ({sx}, {sy})")

        if not pattern_found:
            print("No 121 patterns found.")

    def get_hidden_neighbors(self, x, y):
        return [
            (nx, ny) for nx, ny in self.get_neighbors(x, y)
            if self.grid[ny][nx].state == CellState.HIDDEN
        ]
