import pygame
import sys
import random

pygame.init()

# Make the window bigger/taller
WIN_WIDTH = 600
WIN_HEIGHT = 800

# Increase the top box height to show a full 4-block Tetromino
TOP_BOX_HEIGHT = 120

# Keep the grid the same size, but draw it lower on the screen
PLAY_WIDTH = 200   # 10 columns * 20 px
PLAY_HEIGHT = 400  # 20 rows * 20 px
BLOCK_SIZE = 20
GRID_COLS = 10
GRID_ROWS = 20

SIDE_OFFSET = 320

BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

SHAPES = {
    'I': [[1, 5, 9, 13]],
    'O': [[0, 1, 4, 5]],
    'T': [[1, 4, 5, 6],
           [1, 5, 6, 9],
           [4, 5, 6, 9],
           [1, 4, 5, 9]],
    'S': [[1, 2, 4, 5],
           [1, 5, 6, 10]],
    'Z': [[0, 1, 5, 6],
           [2, 5, 6, 9]],
    'J': [[1, 5, 9, 8],
           [0, 1, 2, 6],
           [1, 0, 4, 8],
           [0, 4, 5, 6]],
    'L': [[1, 5, 9, 10],
           [2, 6, 4, 5],
           [0, 1, 5, 9],
           [0, 1, 2, 4]]
}

SHAPE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': MAGENTA,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

def create_grid(locked_positions=None):
    grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    if locked_positions:
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if (r, c) in locked_positions:
                    grid[r][c] = locked_positions[(r, c)]
    return grid

class Piece:
    def __init__(self, shape_key):
        self.shape_key = shape_key
        self.color = SHAPE_COLORS[shape_key]
        self.rotation = 0
        # Starting near the top middle
        self.x = 3
        self.y = 0
        self.shape = SHAPES[shape_key]

    def current_positions(self):
        indices = self.shape[self.rotation % len(self.shape)]
        blocks = []
        for idx in indices:
            row = idx // 4
            col = idx % 4
            blocks.append((self.y + row, self.x + col))
        return blocks

def valid_space(piece, grid):
    for (r, c) in piece.current_positions():
        if r < 0 or r >= GRID_ROWS or c < 0 or c >= GRID_COLS:
            return False
        if grid[r][c] is not None:
            return False
    return True

def rotate_piece(piece, grid):
    old_rotation = piece.rotation
    piece.rotation = (piece.rotation + 1) % len(piece.shape)
    if not valid_space(piece, grid):
        piece.rotation = old_rotation

def move_piece(piece, dx, dy, grid):
    old_x, old_y = piece.x, piece.y
    piece.x += dx
    piece.y += dy
    if not valid_space(piece, grid):
        piece.x, piece.y = old_x, old_y
        return False
    return True

def lock_piece(piece, grid, locked_positions):
    for (r, c) in piece.current_positions():
        locked_positions[(r, c)] = piece.color

def clear_rows(grid, locked_positions):
    cleared = 0
    for r in range(GRID_ROWS):
        if None not in grid[r]:
            cleared += 1
            del_row = r
            for c in range(GRID_COLS):
                del locked_positions[(r, c)]
            # shift everything down
            for row_above in range(del_row - 1, -1, -1):
                for col_above in range(GRID_COLS):
                    if (row_above, col_above) in locked_positions:
                        color = locked_positions[(row_above, col_above)]
                        locked_positions[(row_above + 1, col_above)] = color
                        del locked_positions[(row_above, col_above)]
    return cleared

def get_new_piece():
    return Piece(random.choice(list(SHAPES.keys())))

def draw_grid_lines(surface):
    # Draw grid lines with vertical offset TOP_BOX_HEIGHT
    for i in range(GRID_ROWS + 1):
        pygame.draw.line(surface, GRAY,
                         (0, i * BLOCK_SIZE + TOP_BOX_HEIGHT),
                         (GRID_COLS * BLOCK_SIZE, i * BLOCK_SIZE + TOP_BOX_HEIGHT), 1)
    for j in range(GRID_COLS + 1):
        pygame.draw.line(surface, GRAY,
                         (j * BLOCK_SIZE, TOP_BOX_HEIGHT),
                         (j * BLOCK_SIZE, GRID_ROWS * BLOCK_SIZE + TOP_BOX_HEIGHT), 1)

def draw_next_piece(surface, next_piece, font):
    label = font.render("Next:", True, WHITE)
    surface.blit(label, (SIDE_OFFSET, 50))

    format_positions = next_piece.current_positions()
    offset_x, offset_y = 0, 3
    for (r, c) in format_positions:
        x = SIDE_OFFSET + (c - next_piece.x + offset_x) * BLOCK_SIZE
        y = 100 + (r - next_piece.y + offset_y) * BLOCK_SIZE
        pygame.draw.rect(surface, next_piece.color, (x, y, BLOCK_SIZE, BLOCK_SIZE))

def draw_current_piece_top(surface, current_piece):
    # Draw a bounding box above the main grid
    pygame.draw.rect(surface, WHITE, (0, 0, PLAY_WIDTH, TOP_BOX_HEIGHT), 2)

    font = pygame.font.SysFont('Arial', 18)
    info = font.render("Current Piece Movement:", True, WHITE)
    surface.blit(info, (10, 5))

    # We'll place the piece squares in this top area
    offset_y = 40  # a bit lower to fit 4-block height
    for (r, c) in current_piece.current_positions():
        draw_x = c * BLOCK_SIZE
        draw_y = offset_y  # ignoring piece.y for vertical
        # For each row, shift downward
        draw_y += (r * BLOCK_SIZE // 2)
        pygame.draw.rect(surface,
                         current_piece.color,
                         (draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE))

def draw_window(surface, grid, locked_positions, score, level, current_piece, next_piece):
    surface.fill(BLACK)
    # Draw the top area showing the current piece
    draw_current_piece_top(surface, current_piece)

    # Draw placed blocks in the main grid area, offset by TOP_BOX_HEIGHT
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if grid[r][c]:
                pygame.draw.rect(surface,
                                 grid[r][c],
                                 (c * BLOCK_SIZE,
                                  r * BLOCK_SIZE + TOP_BOX_HEIGHT,
                                  BLOCK_SIZE,
                                  BLOCK_SIZE))

    draw_grid_lines(surface)

    font = pygame.font.SysFont('Arial', 24, bold=True)
    score_label = font.render(f"Score: {score}", True, WHITE)
    level_label = font.render(f"Level: {level}", True, WHITE)
    surface.blit(score_label, (SIDE_OFFSET, 10))
    surface.blit(level_label, (SIDE_OFFSET, 30))

    # Draw the next piece
    draw_next_piece(surface, next_piece, font)

    # Draw the sidebar outline
    pygame.draw.rect(surface, WHITE, (PLAY_WIDTH, 0, WIN_WIDTH - PLAY_WIDTH, WIN_HEIGHT), 2)

    pygame.display.update()

def main():
    surface = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Tetris")

    clock = pygame.time.Clock()

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = get_new_piece()
    next_piece = get_new_piece()

    fall_time = 0
    fall_speed = 0.8
    level = 1
    lines_cleared_total = 0
    score = 0
    running = True
    paused = False
    game_over = False

    while running:
        grid = create_grid(locked_positions)
        dt = clock.tick(60) / 1000.0
        fall_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r:
                    # restart
                    locked_positions = {}
                    grid = create_grid(locked_positions)
                    current_piece = get_new_piece()
                    next_piece = get_new_piece()
                    fall_time = 0
                    fall_speed = 0.8
                    level = 1
                    lines_cleared_total = 0
                    score = 0
                    paused = False
                    game_over = False
                if not paused and not game_over:
                    if event.key == pygame.K_LEFT:
                        move_piece(current_piece, -1, 0, grid)
                    elif event.key == pygame.K_RIGHT:
                        move_piece(current_piece, 1, 0, grid)
                    elif event.key == pygame.K_DOWN:
                        # soft drop
                        moved = move_piece(current_piece, 0, 1, grid)
                        if moved:
                            score += 1
                    elif event.key == pygame.K_UP:
                        rotate_piece(current_piece, grid)
                    elif event.key == pygame.K_SPACE:
                        # hard drop
                        while move_piece(current_piece, 0, 1, grid):
                            score += 2

        if paused or game_over:
            draw_window(surface, grid, locked_positions, score, level, current_piece, next_piece)
            continue

        # Gravity
        if fall_time >= fall_speed:
            fall_time = 0
            if not move_piece(current_piece, 0, 1, grid):
                lock_piece(current_piece, grid, locked_positions)
                cleared = clear_rows(grid, locked_positions)
                if cleared == 1:
                    score += 100
                elif cleared == 2:
                    score += 300
                elif cleared == 3:
                    score += 500
                elif cleared == 4:
                    score += 800
                lines_cleared_total += cleared

                if lines_cleared_total >= level * 10:
                    level += 1
                    fall_speed = max(0.05, fall_speed * 0.9)

                current_piece = next_piece
                next_piece = get_new_piece()
                if not valid_space(current_piece, grid):
                    game_over = True

        draw_window(surface, grid, locked_positions, score, level, current_piece, next_piece)

    # Game Over screen
    font = pygame.font.SysFont('Arial', 48, bold=True)
    surface.fill(BLACK)
    go_text = font.render("GAME OVER", True, WHITE)
    surface.blit(go_text, (WIN_WIDTH // 2 - go_text.get_width() // 2,
                           WIN_HEIGHT // 2 - go_text.get_height() // 2))
    pygame.display.update()
    pygame.time.wait(3000)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()