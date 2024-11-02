import pygame
import random

# Window size
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500

# Game size
GAME_SIZE = 4

# Colors
BACKGROUND = (187, 173, 160)
EMPTY_CELL = (205, 193, 180)
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (237, 190, 30),
    8192: (237, 185, 20),
    16384: (236, 180, 15),
    32768: (236, 175, 10),
    65536: (236, 170, 5)
}
TEXT_DARK = (119, 110, 101)
TEXT_LIGHT = (249, 246, 242)

class Game:
    def __init__(self):
        self.grid = [[0 for _ in range(GAME_SIZE)] for _ in range(GAME_SIZE)]
        self.score = 0
        self.total_moves = 0  # Add moves counter
        self.highest_tile = 0
        self.max_tile = 2    # Add max tile tracker
        self.milestones = {2048: False, 4096: False, 8192: False, 
                          16384: False, 32768: False, 65536: False}
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(GAME_SIZE) for j in range(GAME_SIZE) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4

    def update_highest_tile(self):
        current_max = max(max(row) for row in self.grid)
        if current_max > self.highest_tile:
            self.highest_tile = current_max
            # Check milestones
            for milestone in sorted(self.milestones.keys()):
                if current_max >= milestone and not self.milestones[milestone]:
                    self.milestones[milestone] = True
                    print(f"Achievement Unlocked: {milestone}!")

    def move(self, direction):
        original_grid = [row[:] for row in self.grid]
        moved = False

        if direction in ['UP', 'DOWN']:
            self.transpose()
        if direction in ['RIGHT', 'DOWN']:
            self.reverse()

        self.compress()
        score_added = self.merge()
        self.compress()

        if direction in ['RIGHT', 'DOWN']:
            self.reverse()
        if direction in ['UP', 'DOWN']:
            self.transpose()

        # Check if the grid changed
        if original_grid != self.grid:
            moved = True
            self.score += score_added
            self.total_moves += 1  # Increment moves counter
            self.add_new_tile()
            self.update_highest_tile()
            self.max_tile = max(max(row) for row in self.grid)  # Update max tile

        return moved

    def compress(self):
        new_grid = [[0 for _ in range(GAME_SIZE)] for _ in range(GAME_SIZE)]
        for i in range(GAME_SIZE):
            pos = 0
            for j in range(GAME_SIZE):
                if self.grid[i][j] != 0:
                    new_grid[i][pos] = self.grid[i][j]
                    pos += 1
        self.grid = new_grid

    def merge(self):
        score_added = 0
        for i in range(GAME_SIZE):
            for j in range(GAME_SIZE - 1):
                if self.grid[i][j] != 0 and self.grid[i][j] == self.grid[i][j + 1]:
                    self.grid[i][j] *= 2
                    score_added += self.grid[i][j]
                    self.grid[i][j + 1] = 0
        return score_added

    def reverse(self):
        self.grid = [row[::-1] for row in self.grid]

    def transpose(self):
        self.grid = [[self.grid[j][i] for j in range(GAME_SIZE)] for i in range(GAME_SIZE)]

    def is_game_over(self):
        # Check for empty cells
        if any(0 in row for row in self.grid):
            return False

        # Check for possible merges
        for i in range(GAME_SIZE):
            for j in range(GAME_SIZE):
                current = self.grid[i][j]
                # Check right
                if j < GAME_SIZE - 1 and current == self.grid[i][j + 1]:
                    return False
                # Check down
                if i < GAME_SIZE - 1 and current == self.grid[i + 1][j]:
                    return False
        return True

    def has_won(self):
        return self.highest_tile >= 65536

def draw_text(window, text, font_size, x, y, color):
    # Adjust font size based on number of digits
    if len(str(text)) > 4:
        font_size = int(font_size * 0.8)
    if len(str(text)) > 5:
        font_size = int(font_size * 0.7)
    
    font = pygame.font.SysFont('Arial', font_size, bold=True)
    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    window.blit(text_surface, text_rect)

def main():
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('2048 Extended')
    clock = pygame.time.Clock()

    game = Game()
    game_won = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN and not game.is_game_over():
                moved = False
                if event.key == pygame.K_UP:
                    moved = game.move('UP')
                elif event.key == pygame.K_DOWN:
                    moved = game.move('DOWN')
                elif event.key == pygame.K_LEFT:
                    moved = game.move('LEFT')
                elif event.key == pygame.K_RIGHT:
                    moved = game.move('RIGHT')

                if moved:
                    pygame.display.set_caption(f'2048 Extended - Max Tile: {game.max_tile}')

        # Draw background
        window.fill(BACKGROUND)

        # Draw score and stats
        pygame.draw.rect(window, EMPTY_CELL, (10, 10, WINDOW_WIDTH - 20, 60), border_radius=5)
        draw_text(window, f"Score: {game.score} | Moves: {game.total_moves} | Max: {game.max_tile}", 
                 24, WINDOW_WIDTH // 2, 40, TEXT_DARK)

        # Draw grid with updated colors and font sizes
        for i in range(GAME_SIZE):
            for j in range(GAME_SIZE):
                x = j * (WINDOW_WIDTH // GAME_SIZE)
                y = i * (WINDOW_WIDTH // GAME_SIZE) + 100
                value = game.grid[i][j]
                
                pygame.draw.rect(window, 
                               TILE_COLORS.get(value, EMPTY_CELL),
                               (x + 5, y + 5, WINDOW_WIDTH // GAME_SIZE - 10, WINDOW_WIDTH // GAME_SIZE - 10),
                               border_radius=5)

                if value != 0:
                    # Dynamic font sizing based on number length
                    if value <= 4:
                        font_size = 48
                    elif value <= 512:
                        font_size = 36
                    elif value <= 16384:
                        font_size = 24
                    else:
                        font_size = 20
                    
                    text_color = TEXT_DARK if value <= 4 else TEXT_LIGHT
                    draw_text(window, value, font_size,
                            x + WINDOW_WIDTH // GAME_SIZE // 2,
                            y + WINDOW_WIDTH // GAME_SIZE // 2,
                            text_color)

        if game.is_game_over():
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            window.blit(overlay, (0, 0))
            draw_text(window, f"Game Over! Max: {game.highest_tile}", 
                     64, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, TEXT_LIGHT)
        elif game.has_won():
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((255, 223, 0))
            overlay.set_alpha(128)
            window.blit(overlay, (0, 0))
            draw_text(window, "65536 Achieved!", 
                     64, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, TEXT_DARK)

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()