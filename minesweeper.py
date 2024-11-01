import pygame
import random
from enum import Enum

# Constants
CELL_SIZE = 32
GRID_WIDTH = 30
GRID_HEIGHT = 16
MINE_COUNT = 99
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 50  # Extra height for timer and mine counter

# Colors
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 128, 0)
DARK_RED = (128, 0, 0)
DARK_BLUE = (0, 0, 128)
BROWN = (128, 128, 0)
BLACK = (0, 0, 0)
BUTTON_COLOR = (70, 130, 180)  # Steel Blue
BUTTON_HOVER_COLOR = (100, 149, 237)  # Cornflower Blue

# Number colors
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

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False

    def draw(self, screen, font):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

class Cell:
    def __init__(self):
        self.is_mine = False
        self.state = CellState.HIDDEN
        self.neighbor_mines = 0

class Minesweeper:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Create Quick Start button
        button_width = 150
        button_height = 30
        button_x = WINDOW_WIDTH // 2 - button_width // 2
        self.quick_start_button = Button(button_x, 10, button_width, button_height, "Quick Start")
        
        self.reset_game()

    def reset_game(self):
        self.grid = [[Cell() for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.game_over = False
        self.victory = False
        self.mines_remaining = MINE_COUNT
        self.start_time = None
        self.elapsed_time = 0
        self.first_click = True

    def quick_start(self):
        if not self.first_click:
            return
        
        # First, place mines avoiding a random starting point
        start_x = random.randint(0, GRID_WIDTH - 1)
        start_y = random.randint(0, GRID_HEIGHT - 1)
        self.place_mines(start_x, start_y)
        self.first_click = False
        self.start_time = pygame.time.get_ticks()

        # Find all safe cells
        safe_cells = []
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if not self.grid[y][x].is_mine:
                    safe_cells.append((x, y))

        # Randomly select and reveal 5 safe cells
        cells_to_reveal = random.sample(safe_cells, min(5, len(safe_cells)))
        for x, y in cells_to_reveal:
            self.reveal_cell(x, y)

    def place_mines(self, first_x, first_y):
        # Place mines randomly, avoiding the first clicked cell and its neighbors
        safe_cells = [(first_x, first_y)]
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = first_x + dx, first_y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    safe_cells.append((nx, ny))

        positions = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if (x, y) not in safe_cells]
        mine_positions = random.sample(positions, MINE_COUNT)

        for x, y in mine_positions:
            self.grid[y][x].is_mine = True

        # Calculate neighbor mines
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if not self.grid[y][x].is_mine:
                    count = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and self.grid[ny][nx].is_mine:
                                count += 1
                    self.grid[y][x].neighbor_mines = count

    def reveal_cell(self, x, y):
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return
        
        cell = self.grid[y][x]
        if cell.state != CellState.HIDDEN:
            return

        cell.state = CellState.REVEALED

        if cell.neighbor_mines == 0 and not cell.is_mine:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    self.reveal_cell(x + dx, y + dy)

    def handle_click(self, pos, right_click=False):
        if self.game_over or self.victory:
            return

        x = pos[0] // CELL_SIZE
        y = (pos[1] - 50) // CELL_SIZE  # Adjust for header height

        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return

        cell = self.grid[y][x]

        if right_click:
            if cell.state == CellState.HIDDEN:
                cell.state = CellState.FLAGGED
                self.mines_remaining -= 1
            elif cell.state == CellState.FLAGGED:
                cell.state = CellState.HIDDEN
                self.mines_remaining += 1
            return

        if cell.state == CellState.FLAGGED:
            return

        if self.first_click:
            self.start_time = pygame.time.get_ticks()
            self.place_mines(x, y)
            self.first_click = False

        if cell.is_mine:
            self.game_over = True
            self.reveal_all_mines()
        else:
            self.reveal_cell(x, y)
            self.check_victory()

    def reveal_all_mines(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x].is_mine:
                    self.grid[y][x].state = CellState.REVEALED

    def check_victory(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                if not cell.is_mine and cell.state == CellState.HIDDEN:
                    return
        self.victory = True

    def draw(self):
        self.screen.fill(GRAY)

        # Draw header
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, WINDOW_WIDTH, 50))
        
        # Draw mine counter
        mines_text = self.font.render(f"Mines: {self.mines_remaining}", True, RED)
        self.screen.blit(mines_text, (10, 10))

        # Draw timer
        if self.start_time is not None:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        timer_text = self.font.render(f"Time: {self.elapsed_time}", True, RED)
        self.screen.blit(timer_text, (WINDOW_WIDTH - 150, 10))

        # Draw Quick Start button
        if self.first_click:
            self.quick_start_button.draw(self.screen, self.font)

        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                rect = (x * CELL_SIZE, y * CELL_SIZE + 50, CELL_SIZE, CELL_SIZE)
                
                if cell.state == CellState.HIDDEN:
                    pygame.draw.rect(self.screen, DARK_GRAY, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
                elif cell.state == CellState.FLAGGED:
                    pygame.draw.rect(self.screen, DARK_GRAY, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
                    flag_text = self.font.render("🚩", True, RED)
                    self.screen.blit(flag_text, (x * CELL_SIZE + 5, y * CELL_SIZE + 45))
                else:  # REVEALED
                    pygame.draw.rect(self.screen, GRAY, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
                    
                    if cell.is_mine:
                        mine_text = self.font.render("💣", True, BLACK)
                        self.screen.blit(mine_text, (x * CELL_SIZE + 5, y * CELL_SIZE + 45))
                    elif cell.neighbor_mines > 0:
                        number_text = self.font.render(str(cell.neighbor_mines), True, NUMBER_COLORS[cell.neighbor_mines])
                        text_rect = number_text.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2,
                                                               y * CELL_SIZE + CELL_SIZE // 2 + 50))
                        self.screen.blit(number_text, text_rect)

        if self.game_over:
            self.draw_message("Game Over!")
        elif self.victory:
            self.draw_message("Victory!")

    def draw_message(self, message):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        text = self.font.render(message, True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        
        restart_text = self.font.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in (1, 3):  # Left or right click
                        # Check if Quick Start button was clicked
                        if event.button == 1 and self.first_click:
                            if self.quick_start_button.handle_event(event):
                                self.quick_start()
                            else:
                                self.handle_click(event.pos, event.button == 3)
                        else:
                            self.handle_click(event.pos, event.button == 3)
                elif event.type == pygame.MOUSEMOTION:
                    if self.first_click:
                        self.quick_start_button.handle_event(event)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Minesweeper()
    game.run()