# minesweeper.py

import pygame
import random
from config import *
from cell import Cell, CellState


class Minesweeper:
    def __init__(self, solver=None):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()
        self.solver = solver(self) if solver else None  # Initialize solver if provided

    def reset_game(self):
        self.grid = [[Cell() for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.game_over = False
        self.first_click = True
        print("Game reset with hidden cells.")

    def place_mines(self, first_x, first_y):
        safe_cells = [(first_x, first_y)]
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = first_x + dx, first_y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    safe_cells.append((nx, ny))

        mine_positions = [
            (x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
            if (x, y) not in safe_cells
        ]
        selected_positions = random.sample(mine_positions, MINE_COUNT)

        for x, y in selected_positions:
            self.grid[y][x].is_mine = True

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if not self.grid[y][x].is_mine:
                    self.grid[y][x].neighbor_mines = sum(
                        1 for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                        if 0 <= x + dx < GRID_WIDTH and 0 <= y + dy < GRID_HEIGHT
                        and self.grid[y + dy][x + dx].is_mine
                    )

    def reveal_cell(self, x, y):
        """Reveal a cell and handle cascade reveal if the cell has no neighboring mines."""
        if self.first_click:
            self.place_mines(x, y)
            self.first_click = False

        cell = self.grid[y][x]
        if cell.state != CellState.HIDDEN:
            return

        cell.state = CellState.REVEALED
        print(f"Revealed cell at ({x}, {y}) - Neighbor mines: {cell.neighbor_mines}")

        if cell.is_mine:
            self.game_over = True
            print("Game Over! Mine clicked.")
            self.reveal_all_mines()
        elif cell.neighbor_mines == 0:
            self.cascade_reveal(x, y)

    def cascade_reveal(self, x, y):
        """Recursively reveal adjacent cells if they have no neighboring mines."""
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                neighbor = self.grid[ny][nx]
                if neighbor.state == CellState.HIDDEN and not neighbor.is_mine:
                    neighbor.state = CellState.REVEALED
                    print(f"Cascade reveal cell at ({nx}, {ny}) - Neighbor mines: {neighbor.neighbor_mines}")
                    if neighbor.neighbor_mines == 0:
                        self.cascade_reveal(nx, ny)

    def reveal_all_mines(self):
        """Reveal all mines when the game is over."""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                if cell.is_mine:
                    cell.state = CellState.REVEALED
        print("All mines revealed.")

    def handle_click(self, pos, right_click=False):
        if self.game_over:
            return
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

    def draw(self):
        self.screen.fill(GRAY)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                rect = (x * CELL_SIZE, y * CELL_SIZE + HEADER_HEIGHT, CELL_SIZE, CELL_SIZE)
                if cell.state == CellState.HIDDEN:
                    pygame.draw.rect(self.screen, DARK_GRAY, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
                elif cell.state == CellState.REVEALED:
                    pygame.draw.rect(self.screen, GRAY, rect)
                    if cell.is_mine:
                        pygame.draw.circle(self.screen, BLACK, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + HEADER_HEIGHT + CELL_SIZE // 2), CELL_SIZE // 4)
                    elif cell.neighbor_mines > 0:
                        number_text = self.font.render(str(cell.neighbor_mines), True, NUMBER_COLORS[cell.neighbor_mines])
                        text_rect = number_text.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + HEADER_HEIGHT + CELL_SIZE // 2))
                        self.screen.blit(number_text, text_rect)
                elif cell.state == CellState.FLAGGED:
                    pygame.draw.rect(self.screen, DARK_GRAY, rect)
                    pygame.draw.circle(self.screen, RED, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + HEADER_HEIGHT + CELL_SIZE // 2), CELL_SIZE // 4)

    def run(self):
        running = True
        while running:
            if self.solver and not self.game_over:
                move = self.solver.next_move()
                if move:
                    x, y, action = move
                    if action == 'reveal':
                        self.reveal_cell(x, y)
                    elif action == 'flag':
                        self.grid[y][x].state = CellState.FLAGGED
                        print(f"Flagged cell at ({x}, {y}) as a mine")
                else:
                    print("No moves available from the solver.")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button == 3)
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
