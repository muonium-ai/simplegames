from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' 
import pygame
from game import Minesweeper, CellState
import sys



class PygameMinesweeper:
    CELL_SIZE = 30
    GRID_WIDTH = 10
    GRID_HEIGHT = 10
    MENU_HEIGHT = 30

    def __init__(self, width=10, height=10, mine_count=10):
        pygame.init()
        pygame.display.set_caption("Minesweeper")
        self.CELL_SIZE = 30
        self.GRID_WIDTH = width
        self.GRID_HEIGHT = height

        self.screen = pygame.display.set_mode((self.GRID_WIDTH * self.CELL_SIZE, self.GRID_HEIGHT * self.CELL_SIZE + self.MENU_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.game = Minesweeper(width=width, height=height, mine_count=mine_count)

    def draw(self):
        self.screen.fill((255, 255, 255))
        probabilities = self.game.get_mine_probabilities()
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                cell = self.game.grid[y][x]
                rect = pygame.Rect(x * self.CELL_SIZE, y * self.CELL_SIZE + self.MENU_HEIGHT, self.CELL_SIZE, self.CELL_SIZE)
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
                    prob_text = probabilities[y][x]
                    if prob_text.strip():
                        text_surface = self.small_font.render(prob_text, True, (255, 255, 255))
                        text_rect = text_surface.get_rect(center=rect.center)
                        self.screen.blit(text_surface, text_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

        self.draw_menu()

    def draw_menu(self):
        status = self.game.get_status()
        menu_rect = pygame.Rect(0, 0, self.GRID_WIDTH * self.CELL_SIZE, self.MENU_HEIGHT)
        pygame.draw.rect(self.screen, (220, 220, 220), menu_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), menu_rect, 2)

        status_text = self.small_font.render(
            f"Steps: {status['steps']}  Reveals: {status['reveals']}  Flags: {status['flags']}  Remaining: {status['hidden_remaining']}",
            True, (0, 0, 0)
        )

        self.screen.blit(status_text, (10, 5))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos[0] // self.CELL_SIZE, (event.pos[1] - self.MENU_HEIGHT) // self.CELL_SIZE
                    if 0 <= x < self.GRID_WIDTH and 0 <= y < self.GRID_HEIGHT:
                        if event.button == 1:
                            self.game.reveal(x, y)
                        elif event.button == 3:
                            self.game.flag(x, y)

            self.draw()
            pygame.display.flip()
            self.clock.tick(30)

            if self.game.game_over:
                if self.game.victory:
                    print("Congratulations! You won the game.")
                else:
                    print("Mine clicked. Game over.")
                    self.game.print_solution()
                running = False

if __name__ == "__main__":
    if len(sys.argv) == 4:
        width, height, mine_count = map(int, sys.argv[1:])
    else:
        width, height, mine_count = 10, 10, 10

    print(f"Starting Minesweeper game with width={width}, height={height}, mine_count={mine_count}")

    PygameMinesweeper(width, height, mine_count).run()
