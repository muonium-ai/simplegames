import pygame
import random
from enum import Enum

# Constants
CELL_SIZE = 32
GRID_WIDTH = 30
GRID_HEIGHT = 16
MINE_COUNT = 99
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 100  # Extra height for two-line header
HEADER_HEIGHT = 70  # Adjusted for two-line header
PADDING = 10  # Padding for spacing between buttons and elements

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

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BLACK
        self.text = text
        self.txt_surface = pygame.font.Font(None, 32).render(text, True, WHITE)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = pygame.font.Font(None, 32).render(self.text, True, WHITE)
        return None

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

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
        
        # Button layout
        button_width = 130
        button_height = 30
        button_y = 10

        self.new_game_button = Button(PADDING, button_y, button_width, button_height, "New Game")
        self.restart_button = Button(PADDING + button_width + PADDING, button_y, button_width, button_height, "Restart Game")
        self.quick_start_button = Button(PADDING + 2 * (button_width + PADDING), button_y, button_width, button_height, "Quick Start")
        self.hint_button = Button(PADDING + 3 * (button_width + PADDING), button_y, button_width, button_height, "Hint")

        # Input box for seed and display for time, points, hints
        self.seed_input_box = InputBox(PADDING, HEADER_HEIGHT - 35, 100, 30)
        self.seed = None
        self.hints_used = 0
        self.reset_game()

    def reset_game(self, seed=None):
        self.grid = [[Cell() for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.game_over = False
        self.victory = False
        self.mines_remaining = MINE_COUNT
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.first_click = True
        self.points = 0
        self.used_hint_or_quickplay = False
        self.hints_used = 0  # Reset hint counter on new game
        if seed is None:
            self.seed = random.randint(0, 9999)
        else:
            self.seed = int(seed)
        random.seed(self.seed)
        self.seed_input_box.text = str(self.seed)
        self.seed_input_box.txt_surface = self.font.render(str(self.seed), True, WHITE)

    def quick_start(self):
        if not self.first_click:
            return
        
        self.used_hint_or_quickplay = True
        # Place mines but keep the existing seed
        self.first_click = False
        start_x = random.randint(0, GRID_WIDTH - 1)
        start_y = random.randint(0, GRID_HEIGHT - 1)
        self.place_mines(start_x, start_y)
        
        # Find all safe cells and reveal 5 random ones
        safe_cells = [(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) if not self.grid[y][x].is_mine]
        cells_to_reveal = random.sample(safe_cells, min(5, len(safe_cells)))
        for x, y in cells_to_reveal:
            self.reveal_cell(x, y)

    def hint(self):
        safe_hidden_cells = [(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH)
                             if not self.grid[y][x].is_mine and self.grid[y][x].state == CellState.HIDDEN]
        
        if safe_hidden_cells:
            x, y = random.choice(safe_hidden_cells)
            self.grid[y][x].state = CellState.REVEALED
            self.used_hint_or_quickplay = True
            self.hints_used += 1
            if self.grid[y][x].neighbor_mines == 0:
                self.reveal_adjacent_cells(x, y)
            # Check for victory after revealing a cell
            self.check_victory()

    def place_mines(self, first_x, first_y):
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
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if not self.grid[y][x].is_mine:
                    count = sum(1 for dx in [-1, 0, 1] for dy in [-1, 0, 1] 
                                if 0 <= x + dx < GRID_WIDTH and 0 <= y + dy < GRID_HEIGHT and self.grid[y + dy][x + dx].is_mine)
                    self.grid[y][x].neighbor_mines = count

    def reveal_cell(self, x, y):
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return
        cell = self.grid[y][x]
        if cell.state != CellState.HIDDEN:
            return
        cell.state = CellState.REVEALED
        if not self.used_hint_or_quickplay:
            self.points += cell.neighbor_mines if cell.neighbor_mines else 1
        if cell.neighbor_mines == 0 and not cell.is_mine:
            self.reveal_adjacent_cells(x, y)

    def reveal_adjacent_cells(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (dx != 0 or dy != 0) and (0 <= nx < GRID_WIDTH) and (0 <= ny < GRID_HEIGHT):
                    self.reveal_cell(nx, ny)

    def handle_click(self, pos, right_click=False):
        if self.game_over or self.victory:
            return
        x = pos[0] // CELL_SIZE
        y = (pos[1] - HEADER_HEIGHT) // CELL_SIZE  # Adjusted for header height
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
        if all(cell.state == CellState.REVEALED or (cell.is_mine and cell.state == CellState.FLAGGED)
               for row in self.grid for cell in row):
            self.victory = True
            self.game_over = True  # Stop the game if victory is achieved

    def draw(self):
        self.screen.fill(GRAY)
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, WINDOW_WIDTH, HEADER_HEIGHT))
        
        # Draw buttons on the first line
        self.new_game_button.draw(self.screen, self.font)
        self.restart_button.draw(self.screen, self.font)
        self.quick_start_button.draw(self.screen, self.font)
        self.hint_button.draw(self.screen, self.font)

        # Draw second line of header with seed, time, points, hints
        self.seed_input_box.draw(self.screen)

        timer_text = self.font.render(f"Time: {self.elapsed_time}", True, RED)
        self.screen.blit(timer_text, (120 + PADDING, HEADER_HEIGHT - 35))
        
        points_text = self.font.render(f"Points: {self.points}", True, RED)
        self.screen.blit(points_text, (250 + 2 * PADDING, HEADER_HEIGHT - 35))

        hints_text = self.font.render(f"Hints Used: {self.hints_used}", True, RED)
        self.screen.blit(hints_text, (400 + 3 * PADDING, HEADER_HEIGHT - 35))
        
        mines_text = self.font.render(f"Mines: {self.mines_remaining}", True, RED)
        self.screen.blit(mines_text, (600 + 4 * PADDING, HEADER_HEIGHT - 35))

        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                rect = (x * CELL_SIZE, y * CELL_SIZE + HEADER_HEIGHT, CELL_SIZE, CELL_SIZE)
                if cell.state == CellState.HIDDEN:
                    pygame.draw.rect(self.screen, DARK_GRAY, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
                elif cell.state == CellState.FLAGGED:
                    pygame.draw.rect(self.screen, DARK_GRAY, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
                    flag_text = self.font.render("🚩", True, RED)
                    self.screen.blit(flag_text, (x * CELL_SIZE + 5, y * CELL_SIZE + HEADER_HEIGHT + 5))
                else:
                    pygame.draw.rect(self.screen, GRAY, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
                    if cell.is_mine:
                        mine_text = self.font.render("💣", True, BLACK)
                        self.screen.blit(mine_text, (x * CELL_SIZE + 5, y * CELL_SIZE + HEADER_HEIGHT + 5))
                    elif cell.neighbor_mines > 0:
                        number_text = self.font.render(str(cell.neighbor_mines), True, NUMBER_COLORS[cell.neighbor_mines])
                        text_rect = number_text.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2 + HEADER_HEIGHT))
                        self.screen.blit(number_text, text_rect)

        if self.game_over:
            if self.victory:
                self.draw_message("Victory!")
            else:
                self.draw_message("Game Over!")

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
                    if event.button == 1:
                        if self.new_game_button.handle_event(event):
                            self.reset_game()
                        elif self.restart_button.handle_event(event):
                            self.reset_game(self.seed)
                        elif self.quick_start_button.handle_event(event):
                            self.quick_start()
                        elif self.hint_button.handle_event(event):
                            self.hint()
                        elif event.pos[1] > HEADER_HEIGHT:  # Only process clicks on grid below header
                            self.handle_click(event.pos, event.button == 3)
                    elif event.button == 3:
                        self.handle_click(event.pos, right_click=True)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    else:
                        seed_input = self.seed_input_box.handle_event(event)
                        if seed_input is not None:
                            self.reset_game(seed_input)

            # Update timer only if the game is active
            if not self.game_over:
                self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Minesweeper()
    game.run()
