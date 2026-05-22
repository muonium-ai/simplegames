import pygame
import random
import sys
import os
import json
import argparse

pygame.init()

# Level select / progression
LEVEL_CAP = 9  # classic Tetris convention; in-game level may climb beyond
SAVED_PROGRESS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_progress.json")


def load_highest_level():
    try:
        with open(SAVED_PROGRESS_PATH, "r") as fh:
            data = json.load(fh)
        val = int(data.get("highest_level", 1))
        return max(1, min(LEVEL_CAP, val))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 1


def save_highest_level(level):
    try:
        capped = max(1, min(LEVEL_CAP, int(level)))
        with open(SAVED_PROGRESS_PATH, "w") as fh:
            json.dump({"highest_level": capped}, fh)
    except (OSError, ValueError, TypeError):
        pass


def parse_argv_level():
    for i, arg in enumerate(sys.argv[1:], start=1):
        if arg == "--level" and i + 1 <= len(sys.argv) - 1:
            try:
                return max(1, min(LEVEL_CAP, int(sys.argv[i + 1])))
            except ValueError:
                return None
        if arg.startswith("--level="):
            try:
                return max(1, min(LEVEL_CAP, int(arg.split("=", 1)[1])))
            except ValueError:
                return None
    return None


def parse_cli_args():
    """Parse command-line arguments. Returns argparse.Namespace.

    Honors --level (also via parse_argv_level for back-compat) and --autoplay.
    """
    parser = argparse.ArgumentParser(description="Tetris", add_help=True)
    parser.add_argument("--level", type=int, default=None,
                        help="Starting level (1-%d)" % LEVEL_CAP)
    parser.add_argument("--autoplay", action="store_true", default=False,
                        help="Run a greedy autoplay bot (skips start screen)")
    try:
        args, _unknown = parser.parse_known_args()
    except SystemExit:
        # Fall back to defaults if argparse decided to exit
        args = argparse.Namespace(level=None, autoplay=False)
    return args


def initial_fall_speed_for_level(level):
    # Mirror in-game ramp: fall_speed *= 0.9 per level, floor 0.05
    speed = 0.8
    for _ in range(max(0, level - 1)):
        speed = max(0.05, speed * 0.9)
    return speed


def show_start_screen(surface, clock, highest_unlocked):
    """Level select. Returns chosen level (>=1), or exits on QUIT/ESC."""
    title_font = pygame.font.SysFont('Arial', 40, bold=True)
    sub_font = pygame.font.SysFont('Arial', 20)
    btn_font = pygame.font.SysFont('Arial', 28, bold=True)

    # 3x3 grid of level buttons
    cols, rows = 3, 3
    btn_w, btn_h = 80, 60
    gap = 20
    grid_w = cols * btn_w + (cols - 1) * gap
    grid_h = rows * btn_h + (rows - 1) * gap
    grid_x = (WIN_WIDTH - grid_w) // 2
    grid_y = 260

    buttons = []
    for n in range(1, LEVEL_CAP + 1):
        idx = n - 1
        col = idx % cols
        row = idx // cols
        rect = pygame.Rect(
            grid_x + col * (btn_w + gap),
            grid_y + row * (btn_h + gap),
            btn_w, btn_h
        )
        buttons.append((n, rect))

    selected = 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return selected
                if event.key == pygame.K_LEFT and selected > 1:
                    if selected - 1 <= highest_unlocked:
                        selected -= 1
                if event.key == pygame.K_RIGHT and selected < LEVEL_CAP:
                    if selected + 1 <= highest_unlocked:
                        selected += 1
                if event.key == pygame.K_UP and selected - 3 >= 1:
                    if selected - 3 <= highest_unlocked:
                        selected -= 3
                if event.key == pygame.K_DOWN and selected + 3 <= LEVEL_CAP:
                    if selected + 3 <= highest_unlocked:
                        selected += 3
                # number keys 1-9
                if pygame.K_1 <= event.key <= pygame.K_9:
                    n = event.key - pygame.K_0
                    if n <= highest_unlocked:
                        selected = n
                        return selected
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for n, rect in buttons:
                    if rect.collidepoint(mx, my) and n <= highest_unlocked:
                        return n

        surface.fill(BLACK)
        title = title_font.render("TETRIS", True, WHITE)
        surface.blit(title, (WIN_WIDTH // 2 - title.get_width() // 2, 80))
        sub = sub_font.render("Select starting level", True, WHITE)
        surface.blit(sub, (WIN_WIDTH // 2 - sub.get_width() // 2, 150))
        hint = sub_font.render("Arrows/Click to choose - Enter to start - ESC to quit", True, GRAY)
        surface.blit(hint, (WIN_WIDTH // 2 - hint.get_width() // 2, 190))

        for n, rect in buttons:
            unlocked = n <= highest_unlocked
            if not unlocked:
                color = (40, 40, 40)
                text_color = (90, 90, 90)
            elif n == selected:
                color = (80, 140, 200)
                text_color = WHITE
            else:
                color = (60, 60, 60)
                text_color = WHITE
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, WHITE, rect, 2)
            label = btn_font.render(str(n), True, text_color)
            surface.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

        unlocked_hint = sub_font.render(f"Highest unlocked: {highest_unlocked}", True, WHITE)
        surface.blit(unlocked_hint, (WIN_WIDTH // 2 - unlocked_hint.get_width() // 2, grid_y + grid_h + 30))

        pygame.display.update()
        clock.tick(30)

# Make the window bigger/taller
BLOCK_SIZE = 30
GRID_COLS = 10
GRID_ROWS = 20

PLAY_WIDTH = GRID_COLS * BLOCK_SIZE   # 300
PLAY_HEIGHT = GRID_ROWS * BLOCK_SIZE  # 600

# Redundant "Current Piece Movement" top panel removed; the piece is
# already visible inside the play area.
TOP_BOX_HEIGHT = 0

SIDEBAR_WIDTH = 180
WIN_WIDTH = PLAY_WIDTH + SIDEBAR_WIDTH   # 480
WIN_HEIGHT = PLAY_HEIGHT + 60            # 660 (room for ESC hint)

SIDE_OFFSET = PLAY_WIDTH + 20            # 320

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
        for (r, c), color in locked_positions.items():
            if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                grid[r][c] = color
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
        if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
            locked_positions[(r, c)] = piece.color

def clear_rows(grid, locked_positions):
    filled_counts = [0] * GRID_ROWS
    for (r, c) in locked_positions:
        if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
            filled_counts[r] += 1

    rows_to_clear = [r for r, count in enumerate(filled_counts) if count == GRID_COLS]
    if not rows_to_clear:
        return 0

    clear_set = set(rows_to_clear)

    # Remove all blocks in completed rows.
    for r in rows_to_clear:
        for c in range(GRID_COLS):
            locked_positions.pop((r, c), None)

    # Shift remaining blocks downward by the number of cleared rows below them.
    updated_positions = {}
    for (r, c), color in locked_positions.items():
        rows_below_cleared = sum(1 for cleared_row in clear_set if cleared_row > r)
        updated_positions[(r + rows_below_cleared, c)] = color

    locked_positions.clear()
    locked_positions.update(updated_positions)
    return len(rows_to_clear)

def get_new_piece():
    return Piece(random.choice(list(SHAPES.keys())))


# ---------------------------------------------------------------------------
# Greedy Autoplay Bot
# ---------------------------------------------------------------------------

def _grid_from_locked(locked_positions):
    """Return a fresh 2D grid (color-or-None) from locked_positions."""
    return create_grid(locked_positions)


def _piece_cells(shape_key, rotation, x, y):
    """Cells occupied by a piece given shape, rotation index, and offsets."""
    rotations = SHAPES[shape_key]
    indices = rotations[rotation % len(rotations)]
    cells = []
    for idx in indices:
        row = idx // 4
        col = idx % 4
        cells.append((y + row, x + col))
    return cells


def _fits(cells, board):
    """Check that all cells are inside the play area and not overlapping board."""
    for (r, c) in cells:
        if r < 0 or r >= GRID_ROWS or c < 0 or c >= GRID_COLS:
            return False
        if board[r][c] is not None:
            return False
    return True


def _drop_cells(shape_key, rotation, x, board):
    """Drop the piece in the given rotation at x as far down as possible.

    Returns the resting cells (list of (r, c)) or None if it cannot rest legally.
    """
    # Find the highest y that places piece off-board (above 0 if needed)
    # Start above the board and increment y until next y is illegal.
    y = -3
    # ensure starting position is at least not below board
    last_valid = None
    while True:
        cells = _piece_cells(shape_key, rotation, x, y)
        # Allow rows < 0 while dropping; we only check column bounds and overlap
        any_out_bottom = any(r >= GRID_ROWS for (r, c) in cells)
        any_out_side = any(c < 0 or c >= GRID_COLS for (r, c) in cells)
        if any_out_side:
            return None
        if any_out_bottom:
            break
        # Check overlap only for rows within board
        overlap = any(r >= 0 and board[r][c] is not None for (r, c) in cells)
        if overlap:
            break
        last_valid = cells
        y += 1
    return last_valid


def _simulate_lock(board, cells, color=1):
    """Return a new board with the piece cells filled."""
    new_board = [row[:] for row in board]
    for (r, c) in cells:
        if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
            new_board[r][c] = color
    return new_board


def _clear_full_rows(board):
    """Clear full rows from a 2D board; returns (new_board, lines_cleared)."""
    kept = [row for row in board if any(cell is None for cell in row)]
    cleared = GRID_ROWS - len(kept)
    while len(kept) < GRID_ROWS:
        kept.insert(0, [None] * GRID_COLS)
    return kept, cleared


def _column_heights(board):
    """For each column, height = GRID_ROWS - first filled row (0 if empty)."""
    heights = [0] * GRID_COLS
    for c in range(GRID_COLS):
        for r in range(GRID_ROWS):
            if board[r][c] is not None:
                heights[c] = GRID_ROWS - r
                break
    return heights


def _count_holes(board):
    """An empty cell with a filled cell anywhere above it (same column)."""
    holes = 0
    for c in range(GRID_COLS):
        seen_block = False
        for r in range(GRID_ROWS):
            if board[r][c] is not None:
                seen_block = True
            elif seen_block:
                holes += 1
    return holes


def _bumpiness(heights):
    return sum(abs(heights[i] - heights[i + 1]) for i in range(len(heights) - 1))


def _score_placement(board_after, lines_cleared):
    heights = _column_heights(board_after)
    aggregate = sum(heights)
    holes = _count_holes(board_after)
    bumps = _bumpiness(heights)
    return (
        1.0 * lines_cleared
        - 0.5 * aggregate
        - 0.7 * holes
        - 0.2 * bumps
    )


def plan_best_placement(piece, locked_positions):
    """Enumerate every (rotation, column) for piece and return best plan.

    Returns dict with keys: rotation, x, score. Returns None if no legal move.
    """
    board = _grid_from_locked(locked_positions)
    rotations = SHAPES[piece.shape_key]
    best = None
    for rot in range(len(rotations)):
        for x in range(-3, GRID_COLS + 1):
            cells = _drop_cells(piece.shape_key, rot, x, board)
            if cells is None:
                continue
            # Ensure piece is fully inside columns (already enforced) and within rows
            if any(r < 0 for (r, c) in cells):
                continue
            simulated = _simulate_lock(board, cells, color=1)
            cleared_board, cleared = _clear_full_rows(simulated)
            s = _score_placement(cleared_board, cleared)
            if best is None or s > best["score"]:
                best = {"rotation": rot, "x": x, "score": s, "cells": cells}
    return best


def bot_step(piece, plan, grid):
    """Advance the piece one step toward the planned (rotation, x).

    Mutates piece via rotate_piece / move_piece. Returns True if some action
    occurred this tick (rotation or horizontal move); False if already aligned.
    """
    if plan is None:
        return False
    # First match rotation
    if piece.rotation != plan["rotation"]:
        rotate_piece(piece, grid)
        return True
    # Then move horizontally toward target column
    if piece.x < plan["x"]:
        return move_piece(piece, 1, 0, grid)
    if piece.x > plan["x"]:
        return move_piece(piece, -1, 0, grid)
    return False

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

def draw_window(surface, grid, locked_positions, score, level, current_piece, next_piece, autoplay=False):
    surface.fill(BLACK)

    # Draw placed (locked) blocks
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if grid[r][c]:
                pygame.draw.rect(surface,
                                 grid[r][c],
                                 (c * BLOCK_SIZE,
                                  r * BLOCK_SIZE + TOP_BOX_HEIGHT,
                                  BLOCK_SIZE,
                                  BLOCK_SIZE))

    # Draw the active falling piece so the player can see what's in motion.
    for (r, c) in current_piece.current_positions():
        if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
            pygame.draw.rect(surface,
                             current_piece.color,
                             (c * BLOCK_SIZE,
                              r * BLOCK_SIZE + TOP_BOX_HEIGHT,
                              BLOCK_SIZE,
                              BLOCK_SIZE))

    draw_grid_lines(surface)

    font = pygame.font.SysFont('Arial', 24, bold=True)
    score_label = font.render(f"Score: {score}", True, WHITE)
    level_text = f"Level: {level}" + ("  [AI]" if autoplay else "")
    level_label = font.render(level_text, True, WHITE)
    surface.blit(score_label, (SIDE_OFFSET, 10))
    surface.blit(level_label, (SIDE_OFFSET, 30))

    # Draw the next piece
    draw_next_piece(surface, next_piece, font)

    # Draw "ESC to quit" hint in the HUD area
    hint_font = pygame.font.SysFont('Arial', 16)
    hint_label = hint_font.render("ESC to quit", True, WHITE)
    surface.blit(hint_label, (SIDE_OFFSET, WIN_HEIGHT - 30))

    # Draw the sidebar outline
    pygame.draw.rect(surface, WHITE, (PLAY_WIDTH, 0, WIN_WIDTH - PLAY_WIDTH, WIN_HEIGHT), 2)

    pygame.display.update()

def _draw_level_overlay(surface, font, level):
    text = font.render(f"Level {level}", True, WHITE)
    bg = pygame.Surface((text.get_width() + 40, text.get_height() + 20), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 180))
    bg_rect = bg.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2))
    surface.blit(bg, bg_rect)
    surface.blit(text, text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2)))


def main():
    surface = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Tetris")

    clock = pygame.time.Clock()

    cli_args = parse_cli_args()
    autoplay = bool(cli_args.autoplay)

    highest_unlocked = load_highest_level()

    # Determine starting level. --level (argparse) takes precedence; fall back
    # to legacy parse_argv_level for back-compat with T-000097.
    argv_level = cli_args.level if cli_args.level is not None else parse_argv_level()

    if autoplay:
        # Skip the start screen entirely; default to level 1, honor --level if given.
        starting_level = argv_level if argv_level is not None else 1
        starting_level = max(1, min(LEVEL_CAP, starting_level))
    elif argv_level is not None:
        starting_level = min(argv_level, max(highest_unlocked, 1))
    else:
        starting_level = show_start_screen(surface, clock, highest_unlocked)

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = get_new_piece()
    next_piece = get_new_piece()

    fall_time = 0
    level = starting_level
    # Halve the fall interval in autoplay mode (uniform autoplay speedup).
    fall_speed = initial_fall_speed_for_level(level) * (0.5 if autoplay else 1.0)
    lines_cleared_total = (level - 1) * 10
    score = 0
    running = True
    paused = False
    game_over = False
    level_up_deadline = 0
    overlay_font = pygame.font.SysFont('Arial', 56, bold=True)

    # Autoplay bot state: one planned placement per active piece.
    bot_plan = None
    bot_plan_piece_id = None
    # Throttle bot ticks so the play remains watchable. The interval is halved
    # below when --autoplay is on, so the bot moves at ~2x normal pace.
    bot_step_interval = 0.03 if autoplay else 0.06  # seconds between bot actions
    bot_step_accum = 0.0

    while running:
        grid = create_grid(locked_positions)
        dt = clock.tick(60) / 1000.0
        fall_time += dt
        if autoplay:
            bot_step_accum += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                save_highest_level(max(highest_unlocked, min(LEVEL_CAP, level)))
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r:
                    # restart at the chosen starting level
                    locked_positions = {}
                    grid = create_grid(locked_positions)
                    current_piece = get_new_piece()
                    next_piece = get_new_piece()
                    fall_time = 0
                    level = starting_level
                    fall_speed = initial_fall_speed_for_level(level) * (0.5 if autoplay else 1.0)
                    lines_cleared_total = (level - 1) * 10
                    score = 0
                    paused = False
                    game_over = False
                    level_up_deadline = 0
                    bot_plan = None
                    bot_plan_piece_id = None
                    bot_step_accum = 0.0
                if not paused and not game_over and not autoplay:
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

        # Autoplay: plan once per active piece, then advance one step per tick
        if autoplay and not paused and not game_over:
            if bot_plan_piece_id != id(current_piece):
                bot_plan = plan_best_placement(current_piece, locked_positions)
                bot_plan_piece_id = id(current_piece)
            if bot_step_accum >= bot_step_interval:
                bot_step_accum = 0.0
                bot_step(current_piece, bot_plan, grid)

        if paused or game_over:
            draw_window(surface, grid, locked_positions, score, level, current_piece, next_piece, autoplay=autoplay)
            if pygame.time.get_ticks() < level_up_deadline:
                _draw_level_overlay(surface, overlay_font, level)
                pygame.display.update()
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
                    level_up_deadline = pygame.time.get_ticks() + 1000
                    if level > highest_unlocked:
                        highest_unlocked = min(LEVEL_CAP, level)

                current_piece = next_piece
                next_piece = get_new_piece()
                if not valid_space(current_piece, grid):
                    if not game_over:
                        save_highest_level(max(highest_unlocked, min(LEVEL_CAP, level)))
                    game_over = True

        draw_window(surface, grid, locked_positions, score, level, current_piece, next_piece, autoplay=autoplay)
        if pygame.time.get_ticks() < level_up_deadline:
            _draw_level_overlay(surface, overlay_font, level)
            pygame.display.update()

    # Game Over screen
    font = pygame.font.SysFont('Arial', 48, bold=True)
    surface.fill(BLACK)
    go_text = font.render("GAME OVER", True, WHITE)
    surface.blit(go_text, (WIN_WIDTH // 2 - go_text.get_width() // 2,
                           WIN_HEIGHT // 2 - go_text.get_height() // 2))
    hint_font = pygame.font.SysFont('Arial', 20)
    hint_text = hint_font.render("ESC to quit", True, WHITE)
    surface.blit(hint_text, (WIN_WIDTH // 2 - hint_text.get_width() // 2,
                             WIN_HEIGHT // 2 + go_text.get_height()))
    pygame.display.update()
    # Non-blocking wait so the close button still works on the GAME OVER screen
    _go_deadline = pygame.time.get_ticks() + 3000
    while pygame.time.get_ticks() < _go_deadline:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit(0)
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()