from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' 
import pygame
from game import Minesweeper, CellState
import sys

class PygameMinesweeper:
    CELL_SIZE = 30
    GRID_WIDTH = 10
    GRID_HEIGHT = 10
    MENU_HEIGHT = 90  # Increased from 60 to 90 to provide more space

    def __init__(self, width=10, height=10, mine_count=10):
        pygame.init()
        pygame.display.set_caption("Minesweeper")
        self.GRID_WIDTH = width
        self.GRID_HEIGHT = height

        # Adjusted window height to include new MENU_HEIGHT
        self.screen = pygame.display.set_mode((self.GRID_WIDTH * self.CELL_SIZE, self.GRID_HEIGHT * self.CELL_SIZE + self.MENU_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.game = Minesweeper(width=width, height=height, mine_count=mine_count)
        self.game_message = ''  # Message to display when game is over

        # Create buttons
        self.new_button = pygame.Rect(10, 10, 80, 30)
        self.hint_button = pygame.Rect(100, 10, 80, 30)
        self.quickstart_button = pygame.Rect(190, 10, 120, 30)
        self.pattern_button = pygame.Rect(320, 10, 160, 30)  # New Pattern Recognition button

    def draw(self):
        self.screen.fill((255, 255, 255))
        probabilities = self.game.get_mine_probabilities()
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                cell = self.game.grid[y][x]
                # Corrected y-coordinate to start drawing grid below the menu
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
                    prob = probabilities[y][x]
                    if prob:
                        if prob == 1 or prob >= 90:
                            self.game.flag(x, y)

                        # Ensure probability is used as integer without converting to float
                        text_surface = self.small_font.render(f"{prob}", True, (255, 255, 255))
                        text_rect = text_surface.get_rect(center=rect.center)
                        self.screen.blit(text_surface, text_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

        self.draw_menu()

    def draw_menu(self):
        status = self.game.get_status()
        menu_rect = pygame.Rect(0, 0, self.GRID_WIDTH * self.CELL_SIZE, self.MENU_HEIGHT)
        pygame.draw.rect(self.screen, (220, 220, 220), menu_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), menu_rect, 2)

        # Draw buttons
        buttons = [
            (self.new_button, "New"),
            (self.hint_button, "Hint"),
            (self.quickstart_button, "Quickstart"),
            (self.pattern_button, "Pattern Recognition")
        ]
        for button_rect, text in buttons:
            pygame.draw.rect(self.screen, (200, 200, 200), button_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)
            button_text = self.small_font.render(text, True, (0, 0, 0))
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)

        # Combine all status into one line
        status_text = self.small_font.render(
            f"Steps: {status['steps']}  Reveals: {status['reveals']}  "
            f"Flags: {status['flags']}  Hints: {status['hints']}  Mines: {status['remaining_mines']}/{status['total_mines']}",
            True, (0, 0, 0)
        )
        status_text_rect = status_text.get_rect()
        status_text_rect.topleft = (10, 50)
        self.screen.blit(status_text, status_text_rect)

        # Draw game message if any
        if self.game_message:
            message_text = self.small_font.render(
                self.game_message, True, (0, 0, 255)
            )
            message_text_rect = message_text.get_rect()
            message_text_rect.topleft = (10, 70)
            self.screen.blit(message_text, message_text_rect)

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.new_button.collidepoint(event.pos):
                        self.game = Minesweeper(
                            width=self.GRID_WIDTH, height=self.GRID_HEIGHT, mine_count=self.game.mine_count
                        )
                        self.game_message = ''  # Clear game message
                    elif self.hint_button.collidepoint(event.pos):
                        if not self.game.game_over:
                            self.game.hint()
                    elif self.quickstart_button.collidepoint(event.pos):
                        self.game = Minesweeper(
                            width=self.GRID_WIDTH, height=self.GRID_HEIGHT, mine_count=self.game.mine_count
                        )
                        self.game_message = ''  # Clear game message
                        for _ in range(5):
                            self.game.hint()
                    elif self.pattern_button.collidepoint(event.pos):
                        if not self.game.game_over:
                            self.game.pattern_recognition()
                    else:
                        if not self.game.game_over:
                            x, y = event.pos[0] // self.CELL_SIZE, (event.pos[1] - self.MENU_HEIGHT) // self.CELL_SIZE
                            if 0 <= x < self.GRID_WIDTH and 0 <= y < self.GRID_HEIGHT:
                                cell = self.game.grid[y][x]
                                if event.button == 1:
                                    if cell.state == CellState.REVEALED and cell.neighbor_mines > 0:
                                        self.game.automark(x, y)
                                    else:
                                        self.game.reveal(x, y)
                                elif event.button == 3:
                                    self.game.flag(x, y)

            if self.game.game_over and not self.game_message:
                if self.game.victory:
                    self.game_message = "Congratulations! You won the game."
                else:
                    self.game_message = "Mine clicked. Game over."
                    self.game.print_solution()

            self.draw()
            pygame.display.flip()
            self.clock.tick(30)
            

if __name__ == "__main__":
    if len(sys.argv) == 4:
        width, height, mine_count = map(int, sys.argv[1:])
    else:
        width, height, mine_count = 30, 16, 99

    if len(sys.argv) == 2 and sys.argv[1] in ('-h', '--help', 'help'):
        print("Usage: python -m gui_pygame.py [width] [height] [mine_count]")
        print("Example: python -m gui_pygame.py simple/ medium / hard")
        print("alernatively you can give only one argument to display this help message.")
        print("Press Ctrl+C to exit the game.")
        print
        sys.exit(0)
    elif len(sys.argv) == 2:
        case = sys.argv[1].lower()
        if case == 'simple' or case == 'easy' or case == 'beginner' or case =='basic' or case == 'b' or case == 's':
            width, height, mine_count = 10, 10, 10
        elif case == 'medium' or case == 'intermediate' or case == 'i' or case == 'm':
            width, height, mine_count = 16, 16, 40
        elif case == 'hard' or case == 'expert' or case == 'e' or case == 'h':
            width, height, mine_count = 30, 16, 99
        else:
            print("Invalid arguments. Run 'python -m gui_pygame.py -h' for help.")
            sys.exit(1)

    print(f"Starting Minesweeper game with width={width}, height={height}, mine_count={mine_count}")
    try:
        PygameMinesweeper(width, height, mine_count).run()
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
        pygame.quit()
        sys.exit(0)
    
