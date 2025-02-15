from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt

import pygame
import sys
import copy
import random

class GameOfLife:
    def __init__(self, width=50, height=50, cell_size=15):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.paused = True
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        # Increase window height for UI area below grid
        self.screen = pygame.display.set_mode((self.width * self.cell_size, self.height * self.cell_size + 60))
        pygame.display.set_caption("Game of Life")
        self.clock = pygame.time.Clock()
        # New UI and simulation state properties
        self.state = "menu"  # "menu" for setup, "simulation" for active game
        self.generation = 0
        self.spawn_count_selected = 10
        self.dropdown_options = [i for i in range(10, 101, 10)]
        # New buttons for menu:
        bottom_y = self.height * self.cell_size + 10
        # Fixed positions for UI controls (do not overlap)
        self.add_button_rect = pygame.Rect(10, bottom_y, 100, 40)
        self.dropdown_rect = pygame.Rect(120, bottom_y, 100, 40)
        self.start_button_rect = pygame.Rect(230, bottom_y, 100, 40)
        self.pause_button_rect = pygame.Rect(340, bottom_y, 100, 40)
        self.newgame_button_rect = pygame.Rect(450, bottom_y, 100, 40)
        self.prev_live_counts = []
        self.prev_grids = []
        
        # Add pattern buttons (after other button definitions)
        button_y = self.height * self.cell_size + 10
        self.pattern_buttons = {
            'Blinker': pygame.Rect(560, button_y, 80, 40),
            'Block': pygame.Rect(650, button_y, 80, 40),
            'Glider': pygame.Rect(740, button_y, 80, 40),
            'Gosper': pygame.Rect(830, button_y, 80, 40)
        }
        
        # Increase window width to accommodate pattern buttons
        self.screen = pygame.display.set_mode((920, self.height * self.cell_size + 60))

    # Common Game of Life Patterns
    PATTERNS = {
        'Blinker': [(0, 1), (1, 1), (2, 1)],
        'Block': [(0, 0), (0, 1), (1, 0), (1, 1)],
        'Glider': [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
        'Gosper': [
            (0, 2), (0, 3), (1, 2), (1, 3),  # Left block
            (10, 2), (10, 3), (10, 4),  # Right block
            (11, 1), (11, 5),
            (12, 0), (12, 6),
            (13, 0), (13, 6),
            (14, 3),
            (15, 1), (15, 5),
            (16, 2), (16, 3), (16, 4),
            (17, 3)
        ]
    }

    def toggle_cell(self, pos):
        x, y = pos
        if y >= self.height * self.cell_size:  # Ignore clicks on UI
            return
        col = x // self.cell_size
        row = y // self.cell_size
        if 0 <= row < self.height and 0 <= col < self.width:
            self.grid[row][col] = 0 if self.grid[row][col] else 1

    def update(self):
        new_grid = copy.deepcopy(self.grid)
        for i in range(self.height):
            for j in range(self.width):
                live_neighbors = self.count_live_neighbors(i, j)
                if self.grid[i][j]:
                    if live_neighbors < 2 or live_neighbors > 3:
                        new_grid[i][j] = 0
                else:
                    if live_neighbors == 3:
                        new_grid[i][j] = 1
        self.grid = new_grid

    def count_live_neighbors(self, row, col):
        count = 0
        for i in range(max(0, row-1), min(self.height, row+2)):
            for j in range(max(0, col-1), min(self.width, col+2)):
                if i == row and j == col:
                    continue
                count += self.grid[i][j]
        return count

    def draw_menu(self):
        font = pygame.font.SysFont(None, 24)
        # Draw "Add" button (to add live cells randomly)
        pygame.draw.rect(self.screen, (0, 200, 0), self.add_button_rect)
        add_text = font.render("Add", True, (255, 255, 255))
        self.screen.blit(add_text, (self.add_button_rect.x + 20, self.add_button_rect.y + 10))
        # Draw Dropdown for spawn count
        pygame.draw.rect(self.screen, (0, 0, 200), self.dropdown_rect)
        drop_text = font.render(f"{self.spawn_count_selected}", True, (255, 255, 255))
        self.screen.blit(drop_text, (self.dropdown_rect.x + 20, self.dropdown_rect.y + 10))
        # Draw "Start" button
        pygame.draw.rect(self.screen, (200, 0, 0), self.start_button_rect)
        start_text = font.render("Start", True, (255, 255, 255))
        self.screen.blit(start_text, (self.start_button_rect.x + 10, self.start_button_rect.y + 10))

    def draw(self):
        self.screen.fill((255, 255, 255))
        # Draw grid
        for i in range(self.height):
            for j in range(self.width):
                color = (0, 0, 0) if self.grid[i][j] else (255, 255, 255)
                rect = pygame.Rect(j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)
        # Draw UI area below grid based on state
        font = pygame.font.SysFont(None, 24)
        # Always draw "Add" and "Dropdown" at fixed locations
        pygame.draw.rect(self.screen, (0, 200, 0), self.add_button_rect)
        add_text = font.render("Add", True, (255, 255, 255))
        self.screen.blit(add_text, (self.add_button_rect.x + 20, self.add_button_rect.y + 10))
        pygame.draw.rect(self.screen, (0, 0, 200), self.dropdown_rect)
        drop_text = font.render(f"{self.spawn_count_selected}", True, (255, 255, 255))
        self.screen.blit(drop_text, (self.dropdown_rect.x + 20, self.dropdown_rect.y + 10))
        if self.state == "menu":
            # Fixed "Start" button in menu
            pygame.draw.rect(self.screen, (200, 0, 0), self.start_button_rect)
            start_text = font.render("Start", True, (255, 255, 255))
            self.screen.blit(start_text, (self.start_button_rect.x + 10, self.start_button_rect.y + 10))
        else:
            # In simulation, fixed "Pause" and "New Game" buttons
            pygame.draw.rect(self.screen, (200, 200, 0), self.pause_button_rect)
            pause_text = font.render("Pause", True, (0, 0, 0))
            self.screen.blit(pause_text, (self.pause_button_rect.x + 10, self.pause_button_rect.y + 10))
            pygame.draw.rect(self.screen, (0, 0, 200), self.newgame_button_rect)
            new_text = font.render("New Game", True, (255, 255, 255))
            self.screen.blit(new_text, (self.newgame_button_rect.x + 5, self.newgame_button_rect.y + 10))
            # Draw generation info (unchanged)
            live_cells = sum(sum(row) for row in self.grid)
            info = f"Live: {live_cells}  Generation: {self.generation}"
            info_text = font.render(info, True, (0, 0, 0))
            self.screen.blit(info_text, (self.screen.get_width() - info_text.get_width() - 10, self.height * self.cell_size + 10))
        
        # Draw pattern buttons
        font = pygame.font.SysFont(None, 20)
        for name, rect in self.pattern_buttons.items():
            pygame.draw.rect(self.screen, (100, 100, 200), rect)
            text = font.render(name, True, (255, 255, 255))
            self.screen.blit(text, (rect.x + 5, rect.y + 10))
        
        pygame.display.flip()

    def reset(self):
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.generation = 0
        self.paused = True
        self.state = "menu"

    def place_pattern(self, pattern_name, start_row, start_col):
        if pattern_name in self.PATTERNS:
            # Clear a space for the pattern
            for i in range(max(0, start_row-1), min(self.height, start_row+10)):
                for j in range(max(0, start_col-1), min(self.width, start_col+10)):
                    self.grid[i][j] = 0
            # Place the pattern
            for row_offset, col_offset in self.PATTERNS[pattern_name]:
                new_row = start_row + row_offset
                new_col = start_col + col_offset
                if 0 <= new_row < self.height and 0 <= new_col < self.width:
                    self.grid[new_row][new_col] = 1

    def run(self):
        running = True
        while running:
            self.clock.tick(10)  # Ensure at least 10 FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    # Always process "Add" and "Dropdown" button clicks first
                    if self.add_button_rect.collidepoint(pos):
                        for _ in range(self.spawn_count_selected):
                            r = random.randint(0, self.height - 1)
                            c = random.randint(0, self.width - 1)
                            self.grid[r][c] = 1
                    elif self.dropdown_rect.collidepoint(pos):
                        current_index = self.dropdown_options.index(self.spawn_count_selected)
                        self.spawn_count_selected = self.dropdown_options[(current_index + 1) % len(self.dropdown_options)]
                    # Process state-specific buttons
                    if self.state == "menu":
                        if self.start_button_rect.collidepoint(pos):
                            if sum(sum(row) for row in self.grid) > 0:
                                self.state = "simulation"
                                self.paused = False
                            else:
                                print("No boxes marked. Please add live cells before starting.")
                        else:
                            # Allow toggling cells outside UI area
                            self.toggle_cell(pos)
                    else:
                        if self.pause_button_rect.collidepoint(pos):
                            self.paused = not self.paused
                        elif self.newgame_button_rect.collidepoint(pos):
                            self.reset()
                        else:
                            self.toggle_cell(pos)
                    
                    # Add pattern button handling
                    for pattern_name, rect in self.pattern_buttons.items():
                        if rect.collidepoint(pos):
                            # Place pattern near the center of the grid
                            center_row = self.height // 2 - 2
                            center_col = self.width // 2 - 2
                            self.place_pattern(pattern_name, center_row, center_col)
                            break

                if self.state == "simulation":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.paused = not self.paused
                        elif event.key == pygame.K_r:
                            self.reset()
                        elif event.key == pygame.K_q:
                            running = False

            if self.state == "simulation" and not self.paused:
                self.update()
                self.generation += 1
                # Record current live count and grid state (deepcopy)
                current_live = sum(sum(row) for row in self.grid)
                self.prev_live_counts.append(current_live)
                self.prev_grids.append(copy.deepcopy(self.grid))
                # Keep history limited (we only need last 5 or so)
                if len(self.prev_live_counts) > 5:
                    self.prev_live_counts.pop(0)
                if len(self.prev_grids) > 3:
                    self.prev_grids.pop(0)
                # Check condition: last five live counts equal
                if len(self.prev_live_counts) == 5 and len(set(self.prev_live_counts)) == 1:
                    print("Static live count detected over 5 generations. Pausing game.")
                    self.paused = True
                # Check condition: same grid as two generations ago
                if len(self.prev_grids) == 3:
                    if self.prev_grids[0] == self.prev_grids[2]:
                        print("Static grid detected compared to two generations ago. Pausing game.")
                        self.paused = True

            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    pygame.init()
    game = GameOfLife()
    game.run()
