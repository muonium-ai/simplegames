import pygame
import random
import sys
import importlib
from enum import Enum

# Constants
CELL_SIZE = 32
GRID_WIDTH = 30
GRID_HEIGHT = 16
MINE_COUNT = 99
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 100  # Extra height for header
HEADER_HEIGHT = 70  # Adjusted for header height

# Colors
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 128, 0)
DARK_BLUE = (0, 0, 128)
DARK_RED = (128, 0, 0)
BLACK = (0, 0, 0)

# Number colors for revealed cells
NUMBER_COLORS = {
    1: BLUE,
    2: DARK_GREEN,
    3: RED,
    4: DARK_BLUE,
    5: DARK_RED,
    6: (0, 128, 128),
    7: BLACK,
    8: GRAY
}

class CellState(Enum):
    HIDDEN = 0
    REVEALED = 1
    FLAGGED = 2

class Cell:
    def __init__(self):
        self.is_mine = False
        self.state = CellState.HIDDEN
        self.neighbor_mines = 0

class Minesweeper:
    def __init__(self, solver_name=None):
        pygame.init()  # Initialize Pygame
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()

        # Initialize font after pygame.init()
        self.font = pygame.font.Font(None, 36)

        # Assign grid dimensions as instance attributes
        self.GRID_WIDTH = GRID_WIDTH
        self.GRID_HEIGHT = GRID_HEIGHT

        # Load specified solver
        self.solver_name = solver_name
        self.solver = self.load_solver(solver_name)
        self.is_solver_active = self.solver is not None  # Determine if we're using a solver
        self.step_count = 0  # Track the number of steps taken by the solver
        self.reset_game()

    def load_solver(self, solver_name):
        """Dynamically load a solver from the solvers folder, if specified."""
        if solver_name is None:
            return None
        try:
            solver_module = importlib.import_module(f'solvers.{solver_name}')
            SolverClass = getattr(solver_module, 'Solver')
            print(f"Using solver: {solver_name}")  # Print solver name
            return SolverClass(self)
        except (ModuleNotFoundError, AttributeError) as e:
            print(f"Error loading solver '{solver_name}': {e}")
            return None

    def reset_game(self):
        self.grid = [[Cell() for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.game_over = False
        self.victory = False
        self.step_count = 0  # Reset step count on a new game
        self.place_mines()

    def place_mines(self):
        """Randomly place mines on the grid."""
        safe_cells = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)]
        mine_positions = random.sample(safe_cells, MINE_COUNT)
        
        for x, y in mine_positions:
            self.grid[y][x].is_mine = True
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if not self.grid[y][x].is_mine:
                    count = sum(
                        1 for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                        if 0 <= x + dx < GRID_WIDTH and 0 <= y + dy < GRID_HEIGHT
                        and self.grid[y + dy][x + dx].is_mine
                    )
                    self.grid[y][x].neighbor_mines = count

    def reveal_cell(self, x, y):
        """Reveal a cell and print debug information about clicked cells."""
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return
        cell = self.grid[y][x]
        if cell.state != CellState.HIDDEN:
            return
        cell.state = CellState.REVEALED

        # Print which cell is clicked
        print(f"Revealed cell at ({x}, {y}), mine: {cell.is_mine}, neighbors: {cell.neighbor_mines}")

        if cell.is_mine:
            self.game_over = True
            print("Game Over! Mine clicked.")
            self.reveal_all_mines()
        elif cell.neighbor_mines == 0:
            self.reveal_adjacent_cells(x, y)

        # Check for victory if no mine is clicked
        self.check_victory()

    def check_victory(self):
        """Check if all non-mine cells are revealed, indicating victory."""
        all_revealed = all(
            cell.state == CellState.REVEALED or cell.is_mine
            for row in self.grid for cell in row
        )
        if all_revealed:
            self.victory = True
            print("Victory! All non-mine cells revealed.")

    def reveal_adjacent_cells(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (dx != 0 or dy != 0) and (0 <= nx < GRID_WIDTH) and (0 <= ny < GRID_HEIGHT):
                    self.reveal_cell(nx, ny)

    def handle_click(self, pos, right_click=False):
        if self.is_solver_active:
            return  # Ignore clicks when a solver is running

        x = pos[0] // CELL_SIZE
        y = (pos[1] - HEADER_HEIGHT) // CELL_SIZE
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return
        cell = self.grid[y][x]
        if right_click:
            if cell.state == CellState.HIDDEN:
                cell.state = CellState.FLAGGED
            elif cell.state == CellState.FLAGGED:
                cell.state = CellState.HIDDEN
        else:
            self.reveal_cell(x, y)

    def reveal_all_mines(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x].is_mine:
                    self.grid[y][x].state = CellState.REVEALED

    def run(self):
        running = True
        while running:
            if self.is_solver_active and not self.game_over and not self.victory:
                self.step_count += 1
                move = self.solver.next_move()
                if move:
                    x, y, action = move
                    if action == 'reveal':
                        self.reveal_cell(x, y)
                    elif action == 'flag':
                        self.grid[y][x].state = CellState.FLAGGED

                    # Calculate hidden cells and mines remaining
                    hidden_cells = sum(1 for row in self.grid for cell in row if cell.state == CellState.HIDDEN)
                    mines_remaining = MINE_COUNT - sum(1 for row in self.grid for cell in row if cell.state == CellState.FLAGGED)

                    # Print step information
                    print(f"Step {self.step_count}: Hidden cells remaining: {hidden_cells}, Mines remaining: {mines_remaining}")

                else:
                    print("No moves available from the solver.")
                    self.game_over = True  # Stop if solver has no moves

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button == 3)

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def draw(self):
        self.screen.fill(GRAY)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                rect = (x * CELL_SIZE, y * CELL_SIZE + HEADER_HEIGHT, CELL_SIZE, CELL_SIZE)
                
                if cell.state == CellState.HIDDEN:
                    pygame.draw.rect(self.screen, DARK_GRAY, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)  # Add a border to hidden cells
                elif cell.state == CellState.REVEALED:
                    pygame.draw.rect(self.screen, GRAY, rect)
                    if cell.is_mine:
                        pygame.draw.circle(self.screen, BLACK, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + HEADER_HEIGHT + CELL_SIZE // 2), CELL_SIZE // 4)
                    elif cell.neighbor_mines > 0:
                        number_text = self.font.render(str(cell.neighbor_mines), True, NUMBER_COLORS.get(cell.neighbor_mines, BLACK))
                        text_rect = number_text.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + HEADER_HEIGHT + CELL_SIZE // 2))
                        self.screen.blit(number_text, text_rect)
                elif cell.state == CellState.FLAGGED:
                    pygame.draw.rect(self.screen, DARK_GRAY, rect)
                    pygame.draw.circle(self.screen, RED, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + HEADER_HEIGHT + CELL_SIZE // 2), CELL_SIZE // 4)

if __name__ == "__main__":
    solver_name = sys.argv[1] if len(sys.argv) > 1 else None
    game = Minesweeper(solver_name)
    game.run()
