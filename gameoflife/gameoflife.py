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
        self.add_button_rect = pygame.Rect(10, self.height * self.cell_size + 10, 100, 40)
        self.dropdown_rect = pygame.Rect(120, self.height * self.cell_size + 10, 100, 40)
        self.start_button_rect = pygame.Rect(230, self.height * self.cell_size + 10, 100, 40)
        # Buttons for simulation state:
        self.pause_button_rect = pygame.Rect(10, self.height * self.cell_size + 10, 100, 40)
        self.newgame_button_rect = pygame.Rect(120, self.height * self.cell_size + 10, 100, 40)

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
        # Always show "Add" and "Dropdown" buttons
        pygame.draw.rect(self.screen, (0, 200, 0), self.add_button_rect)
        add_text = font.render("Add", True, (255, 255, 255))
        self.screen.blit(add_text, (self.add_button_rect.x + 20, self.add_button_rect.y + 10))
        pygame.draw.rect(self.screen, (0, 0, 200), self.dropdown_rect)
        drop_text = font.render(f"{self.spawn_count_selected}", True, (255, 255, 255))
        self.screen.blit(drop_text, (self.dropdown_rect.x + 20, self.dropdown_rect.y + 10))
        # UI elements based on state
        if self.state == "menu":
            pygame.draw.rect(self.screen, (200, 0, 0), self.start_button_rect)
            start_text = font.render("Start", True, (255, 255, 255))
            self.screen.blit(start_text, (self.start_button_rect.x + 10, self.start_button_rect.y + 10))
        else:
            # Draw Pause and New Game buttons
            pygame.draw.rect(self.screen, (200, 200, 0), self.pause_button_rect)
            pause_text = font.render("Pause", True, (0, 0, 0))
            self.screen.blit(pause_text, (self.pause_button_rect.x + 10, self.pause_button_rect.y + 10))
            pygame.draw.rect(self.screen, (0, 0, 200), self.newgame_button_rect)
            new_text = font.render("New Game", True, (255, 255, 255))
            self.screen.blit(new_text, (self.newgame_button_rect.x + 5, self.newgame_button_rect.y + 10))
            # Move generation info to the right
            live_cells = sum(sum(row) for row in self.grid)
            info = f"Live: {live_cells}  Generation: {self.generation}"
            info_text = font.render(info, True, (0, 0, 0))
            self.screen.blit(info_text, (self.screen.get_width() - info_text.get_width() - 10, self.height * self.cell_size + 10))
        pygame.display.flip()

    def reset(self):
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.generation = 0
        self.paused = True
        self.state = "menu"

    def run(self):
        running = True
        while running:
            self.clock.tick(10)  # Ensure at least 10 FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if self.add_button_rect.collidepoint(pos):
                            # Add spawn_count_selected live cells at random positions
                            for _ in range(self.spawn_count_selected):
                                r = random.randint(0, self.height - 1)
                                c = random.randint(0, self.width - 1)
                                self.grid[r][c] = 1
                        elif self.dropdown_rect.collidepoint(pos):
                            current_index = self.dropdown_options.index(self.spawn_count_selected)
                            self.spawn_count_selected = self.dropdown_options[(current_index + 1) % len(self.dropdown_options)]
                        elif self.start_button_rect.collidepoint(pos):
                            # Only start if at least one cell is marked (live)
                            if sum(sum(row) for row in self.grid) > 0:
                                self.state = "simulation"
                                self.paused = False
                            else:
                                print("No boxes marked. Please add live cells before starting.")
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Allow manual toggling via mouse for grid cells
                        self.toggle_cell(pygame.mouse.get_pos())
                else:  # simulation state
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.paused = not self.paused
                        elif event.key == pygame.K_r:
                            self.reset()
                        elif event.key == pygame.K_q:
                            running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        # Check for Pause button click
                        if self.pause_button_rect.collidepoint(pos):
                            self.paused = not self.paused
                        # Check for New Game button click
                        elif self.newgame_button_rect.collidepoint(pos):
                            self.reset()
                        else:
                            # Allow toggling in simulation if desired
                            self.toggle_cell(pos)

            if self.state == "simulation" and not self.paused:
                self.update()
                self.generation += 1
            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    pygame.init()
    game = GameOfLife()
    game.run()
