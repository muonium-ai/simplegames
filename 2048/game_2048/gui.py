import pygame
from game_2048.game import Game2048
from game_2048.constants import *

class TextRenderer:
    @staticmethod
    def draw_text(window, text, font_size, x, y, color):
        if len(str(text)) > 4:
            font_size = int(font_size * 0.8)
        if len(str(text)) > 5:
            font_size = int(font_size * 0.7)
        
        font = pygame.font.SysFont('Arial', font_size, bold=True)
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        window.blit(text_surface, text_rect)

class GameGUI:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('2048 Extended')
        self.clock = pygame.time.Clock()
        self.game = Game2048()
        
        # Calculate grid measurements
        self.grid_padding = 10
        self.grid_top = 100
        self.tile_size = (WINDOW_WIDTH - (self.grid_padding * 5)) // GAME_SIZE
        self.grid_size = self.tile_size * GAME_SIZE + self.grid_padding * (GAME_SIZE + 1)

    def handle_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN and not self.game.is_game_over():
                moved = False
                if event.key == pygame.K_UP:
                    moved = self.game.move('UP')
                elif event.key == pygame.K_DOWN:
                    moved = self.game.move('DOWN')
                elif event.key == pygame.K_LEFT:
                    moved = self.game.move('LEFT')
                elif event.key == pygame.K_RIGHT:
                    moved = self.game.move('RIGHT')

                if moved:
                    pygame.display.set_caption(f'2048 Extended - Max Tile: {self.game.max_tile}')
        return True

    def draw(self):
        self.window.fill(BACKGROUND)
        self._draw_score()
        self._draw_grid()
        self._draw_game_state()
        pygame.display.update()

    def _draw_score(self):
        pygame.draw.rect(self.window, EMPTY_CELL, (10, 10, WINDOW_WIDTH - 20, 60), border_radius=5)
        TextRenderer.draw_text(
            self.window,
            f"Score: {self.game.score} | Moves: {self.game.total_moves} | Max: {self.game.max_tile}",
            24, WINDOW_WIDTH // 2, 40, TEXT_DARK
        )

    def _draw_grid(self):
        for i in range(GAME_SIZE):
            for j in range(GAME_SIZE):
                x = j * (self.tile_size + self.grid_padding) + self.grid_padding
                y = i * (self.tile_size + self.grid_padding) + self.grid_top

                # Draw tile background
                pygame.draw.rect(
                    self.window,
                    EMPTY_CELL,
                    (x, y, self.tile_size, self.tile_size),
                    border_radius=5
                )

                # Draw tile value
                value = self.game.grid[i][j]
                if value != 0:
                    pygame.draw.rect(
                        self.window,
                        TILE_COLORS.get(value, TILE_COLORS[2048]),
                        (x, y, self.tile_size, self.tile_size),
                        border_radius=5
                    )

                    # Determine font size based on number of digits
                    if value >= 1000:
                        font_size = 36
                    else:
                        font_size = 48

                    TextRenderer.draw_text(
                        self.window,
                        str(value),
                        font_size,
                        x + self.tile_size // 2,
                        y + self.tile_size // 2,
                        TEXT_DARK if value <= 4 else TEXT_LIGHT
                    )

    def _draw_game_state(self):
        if self.game.is_game_over() or self.game.has_won():
            # Create semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0) if self.game.is_game_over() else (255, 223, 0))
            overlay.set_alpha(128)
            self.window.blit(overlay, (0, 0))

            if self.game.is_game_over():
                message = f"Game Over! Max: {self.game.max_tile}"
                color = TEXT_LIGHT
            else:
                message = "65536 Achieved!"
                color = TEXT_DARK

            TextRenderer.draw_text(
                self.window,
                message,
                64,
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2,
                color
            )

            # Display final stats
            stats = f"Final Score: {self.game.score} | Moves: {self.game.total_moves}"
            TextRenderer.draw_text(
                self.window,
                stats,
                32,
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2 + 80,
                color
            )

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
