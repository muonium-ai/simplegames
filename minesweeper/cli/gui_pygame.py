import pygame
from game import Minesweeper, CellState

CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 10

class PygameMinesweeper:
    def __init__(self, width, height, mines):
        pygame.init()
        self.screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.game = Minesweeper(width, height, mines)

    def draw(self):
        self.screen.fill((255, 255, 255))
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.game.grid[y][x]
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if cell.state == CellState.REVEALED:
                    pygame.draw.rect(self.screen, (200, 200, 200), rect)
                    if cell.neighbor_mines > 0:
                        text_surface = self.font.render(str(cell.neighbor_mines), True, (0, 0, 0))
                        text_rect = text_surface.get_rect(center=rect.center)
                        self.screen.blit(text_surface, text_rect)
                elif cell.state == CellState.FLAGGED:
                    pygame.draw.rect(self.screen, (255, 0, 0), rect)
                else:
                    pygame.draw.rect(self.screen, (100, 100, 100), rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos[0] // CELL_SIZE, event.pos[1] // CELL_SIZE
                    if event.button == 1:
                        self.game.reveal(x, y)
                    elif event.button == 3:
                        self.game.flag(x, y)

            self.draw()
            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    PygameMinesweeper(10,10,10).run()
