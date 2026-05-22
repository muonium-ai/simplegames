from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt
import pygame
import random
import sys
import time
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

        # Game-Lost modal buttons (manual mode only; solver runs auto-restart
        # via the T-000117 path). Fixed-position rects so click hit-testing
        # works on the same frame the modal first draws.
        modal_button_y = WINDOW_HEIGHT // 2 + 30
        self.lost_new_game_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 210, modal_button_y, 200, 40,
        )
        self.lost_exit_rect = pygame.Rect(
            WINDOW_WIDTH // 2 + 30, modal_button_y, 160, 40,
        )

        self.reset_game()

    # Explicit allowlist of solver module names under solvers/.
    # Validating against this list before importlib.import_module prevents
    # arbitrary module loading via crafted CLI input.
    ALLOWED_SOLVERS = {"random_solver", "basic_solver", "subset_solver", "csp_solver"}

    def load_solver(self, solver_name):
        """Dynamically load a solver from the solvers folder, if specified."""
        if solver_name is None:
            return None
        if solver_name not in self.ALLOWED_SOLVERS:
            print(
                f"Solver '{solver_name}' is not allowed. "
                f"Valid solvers: {', '.join(sorted(self.ALLOWED_SOLVERS))}"
            )
            sys.exit(1)
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
        # Defer mine placement until the first click so it can be made safe.
        self.mines_placed = False

    def place_mines(self, safe_cells=None):
        """Randomly place mines on the grid, avoiding any cells in safe_cells."""
        safe_cells = set(safe_cells) if safe_cells else set()
        candidate_cells = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in safe_cells
        ]
        mine_count = min(MINE_COUNT, len(candidate_cells))
        mine_positions = random.sample(candidate_cells, mine_count)

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

    def _ensure_mines_placed(self, click_x, click_y):
        """Place mines on first click, excluding the clicked cell and its 8 neighbors."""
        if self.mines_placed:
            return
        safe_cells = {
            (click_x + dx, click_y + dy)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if 0 <= click_x + dx < GRID_WIDTH and 0 <= click_y + dy < GRID_HEIGHT
        }
        self.place_mines(safe_cells=safe_cells)
        self.mines_placed = True

    def reveal_cell(self, x, y):
        """Reveal a cell and print debug information about clicked cells."""
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return
        # Guarantee the first revealed cell is safe by placing mines now.
        self._ensure_mines_placed(x, y)
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
        # Reveal unflagged mines only; preserve FLAGGED state so the solver's
        # correct flags survive the post-mortem (and remain countable).
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                if cell.is_mine and cell.state != CellState.FLAGGED:
                    cell.state = CellState.REVEALED

    def run(self):
        running = True
        # T-000117: record monotonic start of this round for outcome timing
        self._round_start_time = time.monotonic()
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
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # When the Game-Lost modal is up (manual loss), only its
                    # two buttons accept clicks — grid clicks are ignored
                    # until the player chooses New Game or Exit.
                    if (event.button == 1
                            and self.game_over and not self.victory
                            and not self.is_solver_active):
                        if self.lost_new_game_rect.collidepoint(event.pos):
                            self.reset_game()
                            self._round_start_time = time.monotonic()
                            continue
                        if self.lost_exit_rect.collidepoint(event.pos):
                            pygame.quit()
                            sys.exit(0)
                        continue
                    self.handle_click(event.pos, event.button == 3)

            self.draw()
            pygame.display.flip()
            # Double the FPS cap when a solver is driving the game, matching the
            # uniform autoplay/solver speedup convention.
            self.clock.tick(120 if self.is_solver_active else 60)

            # T-000117: in solver/autoplay mode, on game end print outcome,
            # hold ~1s, then start a new round.
            if self.is_solver_active and (self.game_over or self.victory):
                outcome = "WIN" if self.victory else "LOSS"
                elapsed = time.monotonic() - self._round_start_time
                # Progress made before the game ended. reveal_all_mines now
                # preserves FLAGGED state, so the count reflects real flags.
                opened = sum(
                    1 for row in self.grid for c in row
                    if c.state == CellState.REVEALED and not c.is_mine
                )
                flagged = sum(
                    1 for row in self.grid for c in row
                    if c.state == CellState.FLAGGED
                )
                safe_total = GRID_WIDTH * GRID_HEIGHT - MINE_COUNT
                print(
                    f"[minesweeper-solver] {outcome} in {elapsed:.2f}s "
                    f"— flagged {flagged}/{MINE_COUNT}, opened {opened}/{safe_total}",
                    flush=True,
                )
                restart_deadline = pygame.time.get_ticks() + 1000
                while pygame.time.get_ticks() < restart_deadline:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                            pygame.quit()
                            sys.exit(0)
                    self.clock.tick(60)
                self.reset_game()
                self._round_start_time = time.monotonic()

        pygame.quit()

    def draw(self):
        self.screen.fill(GRAY)

        # ESC to quit hint
        esc_font = pygame.font.Font(None, 20)
        esc_hint = esc_font.render("ESC to quit", True, BLACK)
        self.screen.blit(esc_hint, (WINDOW_WIDTH - esc_hint.get_width() - 10, 5))

        # SOLVER badge in the header when a solver is driving the game.
        if self.is_solver_active:
            badge_font = pygame.font.Font(None, 28)
            badge = badge_font.render("SOLVER", True, RED)
            self.screen.blit(badge, (10, 5))

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

        # Manual-mode Game-Lost modal. Solver mode skips this because the
        # T-000117 auto-restart loop reshuffles the board within ~1s.
        if self.game_over and not self.victory and not self.is_solver_active:
            self.draw_game_lost_modal()

    def draw_game_lost_modal(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("Game Lost!", True, RED)
        self.screen.blit(
            title,
            title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80)),
        )
        subtitle = self.font.render("You clicked a mine.", True, WHITE)
        self.screen.blit(
            subtitle,
            subtitle.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20)),
        )
        mouse_pos = pygame.mouse.get_pos()
        for rect, label in (
            (self.lost_new_game_rect, "Play New Game"),
            (self.lost_exit_rect, "Exit Game"),
        ):
            color = (100, 149, 237) if rect.collidepoint(mouse_pos) else (70, 130, 180)
            pygame.draw.rect(self.screen, color, rect)
            text = self.font.render(label, True, WHITE)
            self.screen.blit(text, text.get_rect(center=rect.center))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Minesweeper with optional solver")
    parser.add_argument(
        "--solver",
        type=str,
        default=None,
        help="Name of the solver module to load from solvers/ (e.g. 'random_solver').",
    )
    # Accept a positional name for backward-compatibility with the previous
    # `python minesweeper_with_solver.py <solver_name>` invocation pattern.
    parser.add_argument(
        "solver_positional",
        nargs="?",
        default=None,
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()

    solver_name = args.solver if args.solver is not None else args.solver_positional
    game = Minesweeper(solver_name)
    game.run()
