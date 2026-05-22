from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt
import json
import os
import sys
import pygame
import random

# Window size
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 560

# Persistence
SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saved_progress.json')

# Full milestone ladder used for HUD/level panel (smaller tiles first)
ALL_MILESTONES = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]

# Milestone announcement duration (ms) - non-blocking overlay
MILESTONE_ANNOUNCE_MS = 1000

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

def load_saved_progress():
    """Load persisted personal-best milestone. Returns int (0 if missing/invalid)."""
    try:
        with open(SAVE_PATH, 'r') as f:
            data = json.load(f)
        return int(data.get('highest_milestone', 0))
    except (OSError, ValueError, TypeError):
        return 0


def save_progress(highest_milestone):
    """Persist personal-best milestone to gitignored save file."""
    try:
        with open(SAVE_PATH, 'w') as f:
            json.dump({'highest_milestone': int(highest_milestone)}, f)
    except OSError:
        pass


class Game:
    def __init__(self):
        self.grid = [[0 for _ in range(GAME_SIZE)] for _ in range(GAME_SIZE)]
        self.score = 0
        self.total_moves = 0  # Add moves counter
        self.highest_tile = 0
        self.max_tile = 2    # Add max tile tracker
        # Track all milestones (including the smaller 128/256/512/1024 tier
        # used by the Levels-reached panel) so we can show progression.
        self.milestones = {m: False for m in ALL_MILESTONES}
        # Highest milestone reached this run (0 if none yet) - powers HUD "Level".
        self.current_level = 0
        # Newly-unlocked milestone announcement (value, expires_at_ms).
        self.milestone_announce = None
        # Personal best across runs, loaded from disk.
        self.personal_best = load_saved_progress()
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
            newly_unlocked = []
            for milestone in sorted(self.milestones.keys()):
                if current_max >= milestone and not self.milestones[milestone]:
                    self.milestones[milestone] = True
                    newly_unlocked.append(milestone)
                    print(f"Achievement Unlocked: {milestone}!")
            if newly_unlocked:
                top = max(newly_unlocked)
                # Current "level" tracks the highest milestone unlocked this run.
                if top > self.current_level:
                    self.current_level = top
                # Trigger non-blocking ~1s announcement overlay.
                self.milestone_announce = (
                    top,
                    pygame.time.get_ticks() + MILESTONE_ANNOUNCE_MS,
                )
                # Persist if it beats the saved personal best.
                if top > self.personal_best:
                    self.personal_best = top
                    save_progress(self.personal_best)

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


def draw_text_left(window, text, font_size, x, y, color):
    """Render text with its left edge anchored at (x, y) (vertical center)."""
    font = pygame.font.SysFont('Arial', font_size, bold=True)
    text_surface = font.render(str(text), True, color)
    rect = text_surface.get_rect(midleft=(x, y))
    window.blit(text_surface, rect)


def draw_levels_panel(window, game, top_y):
    """Render the 'Levels reached' panel: one row of milestone chips.

    Unlocked milestones get a filled colored chip with a check glyph; locked
    ones get a dim empty chip with a dash.
    """
    panel_w = WINDOW_WIDTH - 20
    panel_h = 70
    pygame.draw.rect(window, EMPTY_CELL, (10, top_y, panel_w, panel_h), border_radius=5)
    draw_text_left(window, "Levels reached:", 16, 18, top_y + 14, TEXT_DARK)

    milestones = ALL_MILESTONES
    n = len(milestones)
    chip_w = (panel_w - 20) // n
    chip_h = 32
    chip_y = top_y + 28
    for i, m in enumerate(milestones):
        cx = 10 + 10 + i * chip_w
        unlocked = game.milestones.get(m, False)
        color = TILE_COLORS.get(m, EMPTY_CELL) if unlocked else (170, 160, 150)
        pygame.draw.rect(window, color,
                         (cx, chip_y, chip_w - 4, chip_h), border_radius=4)
        glyph = "v" if unlocked else "-"
        text_color = TEXT_DARK if (unlocked and m <= 4) else TEXT_LIGHT
        # Tile label
        label_font = pygame.font.SysFont('Arial', 12, bold=True)
        label_surf = label_font.render(str(m), True, text_color)
        window.blit(label_surf,
                    label_surf.get_rect(center=(cx + (chip_w - 4) // 2,
                                                chip_y + chip_h // 2 - 6)))
        # Status glyph
        glyph_font = pygame.font.SysFont('Arial', 12, bold=True)
        glyph_surf = glyph_font.render(glyph, True, text_color)
        window.blit(glyph_surf,
                    glyph_surf.get_rect(center=(cx + (chip_w - 4) // 2,
                                                chip_y + chip_h // 2 + 8)))

def main():
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('2048 Extended')
    clock = pygame.time.Clock()

    game = Game()
    game_won = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit(0)
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

        # Draw score and stats (two-line HUD: stats on top, level/personal best below)
        pygame.draw.rect(window, EMPTY_CELL, (10, 10, WINDOW_WIDTH - 20, 80), border_radius=5)
        draw_text(window, f"Score: {game.score} | Moves: {game.total_moves} | Max: {game.max_tile}",
                 22, WINDOW_WIDTH // 2, 30, TEXT_DARK)
        level_label = game.current_level if game.current_level else "-"
        best_label = game.personal_best if game.personal_best else "-"
        draw_text(window, f"Level: {level_label}  |  Personal best: {best_label}",
                 18, WINDOW_WIDTH // 2, 62, TEXT_DARK)

        # Draw grid with updated colors and font sizes
        for i in range(GAME_SIZE):
            for j in range(GAME_SIZE):
                x = j * (WINDOW_WIDTH // GAME_SIZE)
                y = i * (WINDOW_WIDTH // GAME_SIZE) + 110
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

        # Always visible ESC-to-quit hint (bottom-center)
        draw_text(window, "ESC to quit", 16,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT - 12, TEXT_DARK)

        # Non-blocking ~1s milestone announcement overlay (T-000056 pattern).
        if game.milestone_announce is not None:
            value, expires = game.milestone_announce
            if pygame.time.get_ticks() < expires:
                banner = pygame.Surface((WINDOW_WIDTH, 60))
                banner.fill((40, 40, 40))
                banner.set_alpha(200)
                window.blit(banner, (0, WINDOW_HEIGHT // 2 - 30))
                draw_text(window, f"Milestone Reached: {value}!",
                          28, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, TEXT_LIGHT)
            else:
                game.milestone_announce = None

        if game.is_game_over():
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(160)
            window.blit(overlay, (0, 0))
            draw_text(window, f"Game Over! Max: {game.highest_tile}",
                     48, WINDOW_WIDTH // 2, 130, TEXT_LIGHT)
            draw_text(window, f"Level: {game.current_level if game.current_level else '-'}  |  Best: {game.personal_best if game.personal_best else '-'}",
                      20, WINDOW_WIDTH // 2, 175, TEXT_LIGHT)
            draw_levels_panel(window, game, WINDOW_HEIGHT - 160)
            draw_text(window, "ESC to quit", 20,
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80, TEXT_LIGHT)
        elif game.has_won():
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((255, 223, 0))
            overlay.set_alpha(160)
            window.blit(overlay, (0, 0))
            draw_text(window, "65536 Achieved!",
                     48, WINDOW_WIDTH // 2, 130, TEXT_DARK)
            draw_text(window, f"Level: {game.current_level}  |  Best: {game.personal_best}",
                      20, WINDOW_WIDTH // 2, 175, TEXT_DARK)
            draw_levels_panel(window, game, WINDOW_HEIGHT - 160)

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()