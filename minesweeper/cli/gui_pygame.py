import pygame
from game import Minesweeper, CellState

class PygameMinesweeper:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.game = Minesweeper(10, 10, 10)

    def draw(self):
        self.screen.fill((200, 200, 200))
        for y, row in enumerate(self.game.grid):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * 30, y * 30, 30, 30)
                if cell.state == CellState.HIDDEN:
                    pygame.draw.rect(self.screen, (150, 150, 150), rect)
                elif cell.state == CellState.FLAGGED:
                    pygame.draw.rect(self.screen, (255, 0, 0), rect)
                elif cell.is_mine:
                    pygame.draw.rect(self.screen, (0, 0, 0), rect)
                else:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect)
                    if cell.neighbor_mines > 0:
                        font = pygame.font.Font(None, 24)
                        text = font.render(str(cell.neighbor_mines), True, (0, 0, 0))
                        self.screen.blit(text, rect.topleft)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos[0] // 30, event.pos[1] // 30
                    if event.button == 1:
                        self.game.reveal(x, y)
                    elif event.button == 3:
                        self.game.flag(x, y)

            self.draw()
            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    PygameMinesweeper().run()
