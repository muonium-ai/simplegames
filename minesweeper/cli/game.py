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
        self.solved = False # dont increase hint count if cell is solved


import string
import random

class MinesweeperFormat:
    BASE62_CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase

    @staticmethod
    def place_mines_random(rows, columns, mines):
        """Place mines randomly on the board."""
        board = [[0 for _ in range(columns)] for _ in range(rows)]
        mine_positions = random.sample([(x, y) for x in range(columns) for y in range(rows)], mines)
        for x, y in mine_positions:
            board[y][x] = 1
        return board

    @staticmethod
    def to_base62(num):
        """Convert an integer to a Base62 string."""
        if num == 0:
            return MinesweeperFormat.BASE62_CHARS[0]
        base62 = []
        while num > 0:
            num, rem = divmod(num, 62)
            base62.append(MinesweeperFormat.BASE62_CHARS[rem])
        return ''.join(reversed(base62))

    @staticmethod
    def from_base62(base62_str):
        """Convert a Base62 string to an integer."""
        num = 0
        for char in base62_str:
            num = num * 62 + MinesweeperFormat.BASE62_CHARS.index(char)
        return num

    @staticmethod
    def encode_board(board):
        def to_base62(num):
            chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            base = len(chars)
            result = []
            while num > 0:
                result.append(chars[num % base])
                num //= base
            return ''.join(reversed(result)) or '0'

        # Flatten the board and convert to a binary string
        binary_string = ''.join('1' if cell else '0' for row in board for cell in row)

        # Split the binary string into chunks of 6 bits
        chunks = [binary_string[i:i+6] for i in range(0, len(binary_string), 6)]

        # Convert each chunk to an integer and then to base62
        base62_encoded = ''.join(to_base62(int(chunk, 2)) for chunk in chunks)

        return base62_encoded

    @staticmethod
    def decode_board(encoded, rows=16, columns=30):
        """Decode a Base62 string back to the original binary board."""
        # Convert Base62 string back to binary string
        binary_string = ''.join(f"{MinesweeperFormat.from_base62(char):06b}" for char in encoded)

        # Convert binary string back to 2D board
        board = [[int(binary_string[i * columns + j]) for j in range(columns)] for i in range(rows)]

        return board

    @staticmethod
    def encode_game(rows, columns, mines,complexity, board):
        """Encode the game configuration as a compact string."""
        encoded = MinesweeperFormat.encode_board(board)
        encoded_game = f"{rows}/{columns}/{mines}/{complexity}/{encoded}"
        return encoded_game

    @staticmethod
    def decode_game(encoded_game):
        """Decode the compact game configuration string back to its components."""
        rows, columns, mines, encoded = encoded_game.split("/")
        board = MinesweeperFormat.decode_board(encoded, int(rows), int(columns))
        return int(rows), int(columns), int(mines), board



class Minesweeper:
    def __init__(self, width, height, mine_count, quickstart=False):
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.victory = False
        self.first_click = not quickstart  # If quickstart is True, we won't wait for first click to place mines
        self.reveals = 0
        self.flags = 0
        self.hidden_remaining = width * height
        self.steps = 0
        self.hints = 0  # Initialize hints count
        self.initial_probability = mine_count / (width * height)
        self.mine_positions = []
        self.complexity = 0
        self.game_id = ''

        for y in range(height):
            for x in range(width):
                self.grid[y][x].x = x
                self.grid[y][x].y = y

        # If quickstart is True, place mines now
        if quickstart:
            self.place_mines_random()
            self.complexity = self.complexity_score()  # Compute complexity immediately

    def place_mines_random(self):
        all_positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        self.mine_positions = random.sample(all_positions, self.mine_count)

        for x, y in self.mine_positions:
            self.grid[y][x].is_mine = True

        # Update neighbor counts
        for x, y in self.mine_positions:
            for nx, ny in self.get_neighbors(x, y):
                self.grid[ny][nx].neighbor_mines += 1

    def place_mines(self, safe_x, safe_y):
        safe_cells = {(safe_x, safe_y)}
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = safe_x + dx, safe_y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    safe_cells.add((nx, ny))

        all_positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        possible_mine_positions = [pos for pos in all_positions if pos not in safe_cells]
        self.mine_positions = random.sample(possible_mine_positions, self.mine_count)

        for x, y in self.mine_positions:
            self.grid[y][x].is_mine = True

        for x, y in self.mine_positions:
            for nx, ny in self.get_neighbors(x, y):
                self.grid[ny][nx].neighbor_mines += 1

        # After placing mines, compute complexity
        self.complexity =self.complexity_score()


    def factorial(self,n):
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers.")
        if n == 0 or n == 1:
            return 1
        return n * self.factorial(n - 1)

    def complexity_score(self):
        """
        Calculate and print a complexity score based on the distribution of neighbor_mines counts.
        Currently all multipliers are set to 1.
        """
        counts = {i: 0 for i in range(9)}  # counts for 0 through 8
        for row in self.grid:
            for cell in row:
                if not cell.is_mine:
                    if 0 <= cell.neighbor_mines <= 8:
                        counts[cell.neighbor_mines] += 1

        # Currently multiplier is 1 for all
        score = sum(counts[i] * self.factorial(i) for i in range(9))

        # Print counts for debugging
        print("Complexity Counts:", counts)
        print("Complexity Score:", score)
        self.complexity = score
        # game_id computation

        # Convert the grid to a list of lists for encoding
        board_list = [[cell.is_mine for cell in row] for row in self.grid]
        
        self.game_id = MinesweeperFormat.encode_game(self.width, self.height, self.mine_count,self.complexity, board_list)
        print("Game ID:", self.game_id)

        return score

    def get_neighbors(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    yield nx, ny

    def reveal(self, x, y):
        # If not quickstart, place mines on first click ensuring safe cell
        if self.first_click:
            self.place_mines(x, y)
            self.first_click = False

        cell = self.grid[y][x]
        if cell.state == CellState.HIDDEN:
            cell.state = CellState.REVEALED
            cell.solved = True
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
                cell.solved = True
                self.flags += 1
                self.steps += 1
                self.hidden_remaining -= 1
                self.update_probabilities()
        elif cell.state == CellState.FLAGGED:
            cell.state = CellState.HIDDEN
            cell.solved = False
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
            'hints': self.hints,  # Include hints count
            'complexity_score': self.complexity #  # Include complexity score
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
            neighbor = self.grid[nny][nnx]
            if neighbor.state == CellState.HIDDEN:
                unopened_neighbors += 1

        if unopened_neighbors == 0:
            return 0

        remaining_mines = self.mine_count - self.flags
        probability = remaining_mines / unopened_neighbors

        # Ensure probability is not negative
        probability = max(0, probability)
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

                remaining_mines = max(0, remaining_mines)
                hidden_neighbors = max(1, hidden_neighbors)  # Avoid division by zero

                probability = remaining_mines / hidden_neighbors
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
    
    def solve(self, x, y):
        
        cell = self.grid[y][x]
        if cell.solved:
            return x, y
        #print(f"Solving cell ({x}, {y})")
        if cell.is_mine:
            self.flag(x, y)
            print(f"Flagged cell ({x}, {y})")
        else:
            #print(f"Cell state before reveal: {cell.state}")
            self.reveal(x, y)
            print(f"Revealed cell ({x}, {y})")
            #print(f"Cell state after reveal: {cell.state}")
        cell.solved = True
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
        self.print_solution()  # Do not remove, for debugging
        print("not implemented yet")

    def get_hidden_neighbors(self, x, y):
        return [
            (nx, ny) for nx, ny in self.get_neighbors(x, y)
            if self.grid[ny][nx].state == CellState.HIDDEN
        ]

    def solve_game(self):
        print("Starting game solver...")
        self.print_solution()  # Do not remove, for debugging
        """
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].state == CellState.HIDDEN:
                    self.solve(x, y)
        """
        # iterate self.mine_positions and reveal all mines
        print("Revealing all mines...")
        print(self.mine_positions)
        for x, y in self.mine_positions:
            self.flag(x, y)
