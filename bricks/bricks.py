from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt

import pygame
import sys
import random
import math
import os
import json
import time
import argparse

# --- Constants ---
WINDOW_WIDTH = 1000  # increased width
WINDOW_HEIGHT = 700  # increased height
FPS = 60

PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 6
FAST_PADDLE_SPEED = 12  # increased paddle speed for fast autoplay

BALL_SIZE = 12
BALL_SPEED = 5

BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_WIDTH = 80
BRICK_HEIGHT = 25
BRICK_GAP = 2

STARTING_LIVES = 3
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (200, 0, 0)
BLUE = (0, 100, 200)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (180, 60, 200)
CYAN = (0, 200, 220)

# Script-relative paths (T-000055)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(SCRIPT_DIR, "saved_progress.json")

# --- Level definitions ---
# Each level: rows of brick specs.
# A row is a list of (hit, color) tuples or None for empty cells.
# color: 1=blue,2=red,3=green,4=yellow,5=orange,6=purple,7=cyan
COLOR_MAP = {
    1: BLUE, 2: RED, 3: GREEN, 4: YELLOW,
    5: ORANGE, 6: PURPLE, 7: CYAN,
}

def _row(hits, color, cols=BRICK_COLS):
    return [(hits, color)] * cols

def _gap_row(cols=BRICK_COLS):
    return [None] * cols

LEVELS = [
    {
        "name": "Warm Up",
        "brick_width": 110,
        "brick_height": 25,
        "gap": 4,
        "rows": [
            _row(1, 1),
            _row(1, 1),
            _row(1, 2),
        ],
    },
    {
        "name": "Step Up",
        "brick_width": 110,
        "brick_height": 25,
        "gap": 4,
        "rows": [
            _row(1, 4),
            _row(2, 2),
            _row(2, 2),
            _row(1, 1),
        ],
    },
    {
        "name": "Checkerboard",
        "brick_width": 110,
        "brick_height": 25,
        "gap": 4,
        "rows": [
            [(2, 3) if i % 2 == 0 else None for i in range(BRICK_COLS)],
            [None if i % 2 == 0 else (2, 4) for i in range(BRICK_COLS)],
            [(2, 3) if i % 2 == 0 else None for i in range(BRICK_COLS)],
            [None if i % 2 == 0 else (2, 4) for i in range(BRICK_COLS)],
            _row(1, 1),
        ],
    },
    {
        "name": "Tight Wall",
        "brick_width": 110,
        "brick_height": 22,
        "gap": 2,
        "rows": [
            _row(3, 5),
            _row(2, 2),
            _row(2, 2),
            _row(2, 7),
            _row(1, 1),
            _row(1, 1),
        ],
    },
    {
        "name": "Pyramid",
        "brick_width": 110,
        "brick_height": 22,
        "gap": 2,
        "rows": [
            [None, None, (3, 6), (3, 6), (3, 6), (3, 6), None, None],
            [None, (2, 5), (2, 5), (2, 5), (2, 5), (2, 5), (2, 5), None],
            [(2, 4), (2, 4), (2, 4), (2, 4), (2, 4), (2, 4), (2, 4), (2, 4)],
            _row(1, 3),
            _row(1, 1),
        ],
    },
    {
        "name": "Gauntlet",
        "brick_width": 110,
        "brick_height": 20,
        "gap": 2,
        "rows": [
            _row(3, 6),
            _row(3, 6),
            _row(2, 5),
            _row(2, 4),
            _row(2, 3),
            _row(2, 2),
            _row(1, 1),
        ],
    },
]
TOTAL_LEVELS = len(LEVELS)

def calculate_intercept_position(ball_x, ball_y, ball_dx, ball_dy, target_x, target_y, paddle_y, try_alternative=False):
    """Calculate where to position paddle to hit ball toward target"""
    if ball_dy > 0:  # Ball is falling
        # Calculate exact landing position accounting for current velocity
        time_to_paddle = (paddle_y - ball_y) / ball_dy
        landing_x = ball_x + (ball_dx * time_to_paddle)
        
        # Add safety margin - aim slightly toward ball's center
        if ball_dx > 0:
            landing_x -= PADDLE_WIDTH * 0.2  # Shift left a bit if ball moving right
        else:
            landing_x += PADDLE_WIDTH * 0.2  # Shift right a bit if ball moving left
            
        # Keep paddle within screen bounds
        landing_x = max(PADDLE_WIDTH/2, min(WINDOW_WIDTH - PADDLE_WIDTH/2, landing_x))
        return landing_x

    # For upward-moving balls
    time_to_paddle = (paddle_y - ball_y) / ball_dy if ball_dy != 0 else 0
    intersection_x = ball_x + (ball_dx * time_to_paddle)
    dx_to_target = target_x - intersection_x
    
    # Adjust angle factor based on height difference
    dy_to_target = target_y - ball_y
    angle_factor = 0.5
    if dy_to_target < -WINDOW_HEIGHT/3:  # If target is significantly higher
        angle_factor = 0.8  # Use more aggressive angles
    
    offset = dx_to_target * angle_factor
    max_offset = PADDLE_WIDTH * 0.9  # Allow more extreme positions
    offset = max(-max_offset, min(max_offset, offset))
    return intersection_x + offset

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = (WINDOW_WIDTH - self.width) // 2
        self.y = WINDOW_HEIGHT - 50
        self.speed = PADDLE_SPEED

    def move_left(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = 0

    def move_right(self):
        self.x += self.speed
        if self.x + self.width > WINDOW_WIDTH:
            self.x = WINDOW_WIDTH - self.width

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self):
        self.reset()
        self.last_distance_to_target = None  # Add tracking for target distance
        self.hits_getting_closer = True      # Track if we're making progress

    def reset(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - 60
        self.dx = 0
        self.dy = 0  # Set 0 so ball is "held" until space pressed
        self.hit_paddle = False  # Initialize paddle hit flag
        self.last_distance_to_target = None
        self.hits_getting_closer = True

    def launch(self):
        # Launch with a random horizontal direction
        self.dx = random.choice([-BALL_SPEED, BALL_SPEED])
        self.dy = -BALL_SPEED

    def update(self, paddle, bricks):
        prev_x = self.x
        prev_y = self.y
        self.x += self.dx
        self.y += self.dy

        # Collide with walls
        if self.x < 0:
            self.x = 0
            self.dx = -self.dx
        elif self.x + BALL_SIZE > WINDOW_WIDTH:
            self.x = WINDOW_WIDTH - BALL_SIZE
            self.dx = -self.dx
        if self.y < 0:
            self.y = 0
            self.dy = -self.dy

        # Collide with paddle
        if (self.y + BALL_SIZE >= paddle.y and
            self.x + BALL_SIZE >= paddle.x and
            self.x <= paddle.x + paddle.width and
            self.dy > 0):
            self.y = paddle.y - BALL_SIZE
            # Alter bounce angle based on where it hits the paddle while preserving speed
            speed = math.hypot(self.dx, self.dy)
            if speed == 0:
                speed = BALL_SPEED
            half_paddle = paddle.width / 2
            hit_pos = (self.x + BALL_SIZE/2) - (paddle.x + half_paddle)
            normalized = max(-1.0, min(1.0, hit_pos / half_paddle))
            max_angle = math.radians(60)
            angle = normalized * max_angle
            self.dx = speed * math.sin(angle)
            self.dy = -speed * math.cos(angle)
            self.hit_paddle = True

        # Collide with bricks (handle all overlapping bricks this frame)
        total_points = 0
        flipped_x = False
        flipped_y = False
        for brick in bricks:
            if brick.hit > 0:
                if (self.x + BALL_SIZE > brick.x and
                    self.x < brick.x + brick.width and
                    self.y + BALL_SIZE > brick.y and
                    self.y < brick.y + brick.height):
                    brick.hit -= 1
                    total_points += brick.points
                    # Determine entry side using previous-frame position vs brick rect
                    was_outside_x = (prev_x + BALL_SIZE <= brick.x) or (prev_x >= brick.x + brick.width)
                    was_outside_y = (prev_y + BALL_SIZE <= brick.y) or (prev_y >= brick.y + brick.height)
                    if was_outside_x and not was_outside_y:
                        if not flipped_x:
                            self.dx = -self.dx
                            flipped_x = True
                    elif was_outside_y and not was_outside_x:
                        if not flipped_y:
                            self.dy = -self.dy
                            flipped_y = True
                    else:
                        # Corner hit or fully-inside: use overlap-depth comparison
                        overlap_x = min(self.x + BALL_SIZE - brick.x, brick.x + brick.width - self.x)
                        overlap_y = min(self.y + BALL_SIZE - brick.y, brick.y + brick.height - self.y)
                        if overlap_x < overlap_y:
                            if not flipped_x:
                                self.dx = -self.dx
                                flipped_x = True
                        else:
                            if not flipped_y:
                                self.dy = -self.dy
                                flipped_y = True
        if total_points > 0:
            if self.hit_paddle:
                if self.last_distance_to_target is not None:
                    current_distance = self.distance_to_target(self.x, self.y)
                    self.hits_getting_closer = current_distance < self.last_distance_to_target
                self.last_distance_to_target = None
            return total_points
        if self.hit_paddle:
            # After paddle hit, if we have a last_distance, check if we're getting closer
            if self.last_distance_to_target is not None:
                current_distance = self.distance_to_target(self.x, self.y)
                self.hits_getting_closer = current_distance < self.last_distance_to_target
            self.last_distance_to_target = None  # Reset for next measurement
        return 0

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x + BALL_SIZE/2), int(self.y + BALL_SIZE/2)), BALL_SIZE//2)

    def distance_to_target(self, target_x, target_y):
        return ((self.x - target_x) ** 2 + (self.y - target_y) ** 2) ** 0.5

class Brick:
    def __init__(self, x, y, hit=1, width=BRICK_WIDTH, height=BRICK_HEIGHT, color=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hit = hit  # Durability
        self.initial = hit  # Save initial hit count for miss calculation
        self.points = 10 * hit
        self.hover = False  # Add hover state
        # Color overrides default hit-based palette when provided.
        self.color = color

    def draw(self, surface):
        if self.hit > 0:
            if self.color is not None:
                # Darken slightly as durability drops below the initial value.
                base = self.color
                if self.initial > 1 and self.hit < self.initial:
                    shade = 0.55 + 0.45 * (self.hit / max(1, self.initial))
                    color = (int(base[0] * shade), int(base[1] * shade), int(base[2] * shade))
                else:
                    color = base
            else:
                color = BLUE if self.hit == 1 else RED
            pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
            # Draw hover effect
            if self.hover:
                pygame.draw.rect(surface, (255, 255, 255),
                               (self.x, self.y, self.width, self.height), 2)

def create_bricks(level=1):
    """Build the brick layout for a 1-indexed level using LEVELS."""
    idx = max(1, min(TOTAL_LEVELS, level)) - 1
    spec = LEVELS[idx]
    bw = spec.get("brick_width", BRICK_WIDTH)
    bh = spec.get("brick_height", BRICK_HEIGHT)
    gap = spec.get("gap", BRICK_GAP)
    rows = spec["rows"]
    cols = BRICK_COLS
    # Center the grid horizontally
    grid_width = cols * bw + (cols - 1) * gap
    x_offset = max(0, (WINDOW_WIDTH - grid_width) // 2)
    y_offset = 80  # below HUD
    bricks = []
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            if cell is None:
                continue
            hits, color_key = cell
            color = COLOR_MAP.get(color_key, WHITE)
            x = x_offset + c * (bw + gap)
            y = y_offset + r * (bh + gap)
            bricks.append(Brick(x, y, hit=hits, width=bw, height=bh, color=color))
    return bricks

def load_progress():
    """Read saved highest level reached. Returns int >= 1."""
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        return max(1, min(TOTAL_LEVELS, int(data.get("highest_level", 1))))
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return 1

def save_progress(highest_level):
    """Persist highest level reached. Best-effort, never raises."""
    try:
        capped = max(1, min(TOTAL_LEVELS, int(highest_level)))
        with open(SAVE_FILE, "w") as f:
            json.dump({"highest_level": capped}, f)
    except OSError:
        pass

def show_level_overlay(screen, font, clock, level_index, duration_ms=1000):
    """Show a 'Level N - Name' overlay for ~duration_ms, non-blocking so ESC works."""
    name = LEVELS[level_index - 1]["name"]
    big_font = pygame.font.SysFont(None, 72)
    msg = big_font.render(f"Level {level_index}", True, WHITE)
    sub = font.render(name, True, WHITE)
    deadline = pygame.time.get_ticks() + duration_ms
    while pygame.time.get_ticks() < deadline:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit(0)
        screen.fill(BLACK)
        screen.blit(msg, (WINDOW_WIDTH // 2 - msg.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
        screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, WINDOW_HEIGHT // 2 + 10))
        pygame.display.flip()
        clock.tick(FPS)

def show_level_select(screen, font, highest_unlocked):
    """Render a level select grid, return the chosen level (1..TOTAL_LEVELS)."""
    title_font = pygame.font.SysFont(None, 48)
    cell_size = 80
    margin = 20
    grid_cols = min(TOTAL_LEVELS, 6)
    grid_rows = (TOTAL_LEVELS + grid_cols - 1) // grid_cols
    total_w = grid_cols * cell_size + (grid_cols - 1) * margin
    start_x = (WINDOW_WIDTH - total_w) // 2
    start_y = 260

    def cell_rect(i):
        r = i // grid_cols
        c = i % grid_cols
        return pygame.Rect(start_x + c * (cell_size + margin),
                           start_y + r * (cell_size + margin),
                           cell_size, cell_size)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return 1
                if pygame.K_1 <= event.key <= pygame.K_9:
                    n = event.key - pygame.K_0
                    if 1 <= n <= TOTAL_LEVELS:
                        return n
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(TOTAL_LEVELS):
                    if cell_rect(i).collidepoint(event.pos):
                        return i + 1

        screen.fill(BLACK)
        title = title_font.render("Select Level", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 140))
        hint = font.render(f"Highest reached: {highest_unlocked}   (1-{TOTAL_LEVELS} keys / click / Enter=Level 1)", True, WHITE)
        screen.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 200))
        esc_hint = font.render("ESC to quit", True, WHITE)
        screen.blit(esc_hint, (WINDOW_WIDTH // 2 - esc_hint.get_width()//2, 230))

        for i in range(TOTAL_LEVELS):
            rect = cell_rect(i)
            unlocked = (i + 1) <= highest_unlocked
            hovered = rect.collidepoint(mouse_pos)
            bg = (60, 60, 60) if not unlocked else ((90, 130, 200) if hovered else GRAY)
            pygame.draw.rect(screen, bg, rect)
            border = WHITE if unlocked else (90, 90, 90)
            pygame.draw.rect(screen, border, rect, 2)
            label = title_font.render(str(i + 1), True, WHITE if unlocked else (140, 140, 140))
            screen.blit(label, label.get_rect(center=rect.center))

        pygame.display.flip()

def parse_level_arg(argv, default=1):
    """Parse --level <n> or --level=<n> from argv. Returns clamped int."""
    n = default
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--level" and i + 1 < len(argv):
            try:
                n = int(argv[i + 1])
            except ValueError:
                pass
            i += 2
            continue
        if a.startswith("--level="):
            try:
                n = int(a.split("=", 1)[1])
            except ValueError:
                pass
        i += 1
    return max(1, min(TOTAL_LEVELS, n))

def parse_cli_args(argv):
    """Parse command-line flags via argparse.

    Returns an argparse.Namespace with:
      - level: int or None (1..TOTAL_LEVELS) when --level was supplied
      - autoplay: bool (True when --autoplay was supplied)

    Unknown args are tolerated to avoid breaking when launched by harnesses.
    """
    parser = argparse.ArgumentParser(
        prog="bricks",
        description="Brick Breaker game.",
        add_help=False,
    )
    parser.add_argument("--level", type=int, default=None,
                        help=f"Starting level 1..{TOTAL_LEVELS}.")
    parser.add_argument("--autoplay", action="store_true", default=False,
                        help="Start directly in fast autoplay mode (skip modal).")
    ns, _unknown = parser.parse_known_args(argv)
    if ns.level is not None:
        ns.level = max(1, min(TOTAL_LEVELS, ns.level))
    return ns

def show_modal(screen, font, prev_stats=None):
    """Display modal with three buttons and previous game stats if available"""
    modal_rect = pygame.Rect(100, 200, 800, 200)  # Made taller for stats
    # Define three buttons horizontally arranged
    start_button = pygame.Rect(modal_rect.x + 50, modal_rect.y + 125, 200, 50)
    auto_button = pygame.Rect(modal_rect.x + 300, modal_rect.y + 125, 200, 50)
    fast_button = pygame.Rect(modal_rect.x + 550, modal_rect.y + 125, 200, 50)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return "manual"
                if auto_button.collidepoint(event.pos):
                    return "autoplay"
                if fast_button.collidepoint(event.pos):
                    return "fast_autoplay"

        screen.fill(BLACK)
        # Draw title
        title = font.render("BRICK BREAKER", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        # ESC to quit hint
        esc_hint = font.render("ESC to quit", True, WHITE)
        screen.blit(esc_hint, (WINDOW_WIDTH//2 - esc_hint.get_width()//2, 130))
        
        # Draw previous game stats if available
        if prev_stats:
            score_text = font.render(f"Previous Score: {prev_stats['score']}", True, WHITE)
            time_text = font.render(f"Time: {prev_stats['time']} sec", True, WHITE)
            hits_text = font.render(f"Hits: {prev_stats['hits']}", True, WHITE)
            misses_text = font.render(f"Misses: {prev_stats['misses']}", True, WHITE)
            
            # Layout stats in two rows above the buttons
            screen.blit(score_text, (WINDOW_WIDTH//2 - 300, 150))
            screen.blit(time_text, (WINDOW_WIDTH//2 + 50, 150))
            screen.blit(hits_text, (WINDOW_WIDTH//2 - 300, 180))
            screen.blit(misses_text, (WINDOW_WIDTH//2 + 50, 180))
        
        # Draw buttons
        pygame.draw.rect(screen, GRAY, modal_rect)
        pygame.draw.rect(screen, WHITE, start_button)
        pygame.draw.rect(screen, WHITE, auto_button)
        pygame.draw.rect(screen, WHITE, fast_button)
        
        start_text = font.render("Start Game", True, BLACK)
        auto_text = font.render("Autoplay", True, BLACK)
        fast_text = font.render("Fast Autoplay", True, BLACK)
        screen.blit(start_text, start_text.get_rect(center=start_button.center))
        screen.blit(auto_text, auto_text.get_rect(center=auto_button.center))
        screen.blit(fast_text, fast_text.get_rect(center=fast_button.center))
        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Brick Breaker")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    prev_stats = None  # Initialize previous game stats

    # Parse CLI flags (argparse-based). Also keep manual parser fallback for level
    # to preserve historical semantics.
    cli_args = parse_cli_args(sys.argv[1:])
    cli_level = parse_level_arg(sys.argv[1:], default=0)
    # parse_level_arg clamps to >=1, but we use 0 to signal "no override"
    raw_argv = sys.argv[1:]
    has_level_arg = any(a == "--level" or a.startswith("--level=") for a in raw_argv)
    has_autoplay_arg = bool(cli_args.autoplay)

    highest_unlocked = load_progress()

    while True:  # Outer loop to allow restarting the game
        autoplay_first_run = has_autoplay_arg
        if has_autoplay_arg:
            mode = "fast_autoplay"
            has_autoplay_arg = False  # only honor on first run; restarts use modal
        else:
            mode = show_modal(screen, font, prev_stats)

        # Pick starting level
        if has_level_arg:
            starting_level = cli_level
            has_level_arg = False  # only honor on first run; subsequent restarts use selector
        elif autoplay_first_run:
            # --autoplay alone: skip level selector, start at level 1
            starting_level = 1
        else:
            starting_level = show_level_select(screen, font, highest_unlocked)

        # Initialize game variables
        paddle = Paddle()
        if mode == "fast_autoplay":
            paddle.speed = FAST_PADDLE_SPEED  # Increase paddle speed for fast autoplay
        ball = Ball()
        current_level = starting_level
        bricks = create_bricks(current_level)
        total_initial_hits = sum(b.initial for b in bricks)  # total brick hits needed to win this level
        score = 0
        lives = STARTING_LIVES
        paddle_hits = 0  # Count of paddle hits
        start_time = pygame.time.get_ticks()

        # Initialize highlighted brick container for fast mode
        chosen_brick = None

        # Intro overlay for the starting level
        show_level_overlay(screen, font, clock, current_level, duration_ms=1000)
        # T-000114: record monotonic start time for terminal "level completed" prints
        level_start_time = time.monotonic()

        running = True
        victory = False
        while running:
            # Speed up the game loop when an autoplay mode is active.
            clock.tick(FPS * 2 if mode in ("autoplay", "fast_autoplay") else FPS)

            # Get mouse position for hover effect
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.MOUSEBUTTONDOWN and mode == "fast_autoplay":
                    # Check if clicked on a brick
                    for brick in bricks:
                        if (brick.hit > 0 and 
                            brick.x <= mouse_pos[0] <= brick.x + BRICK_WIDTH and
                            brick.y <= mouse_pos[1] <= brick.y + BRICK_HEIGHT):
                            chosen_brick = brick
                            ball.last_distance_to_target = None  # Reset tracking for new target
                            break
                elif mode == "manual" and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and ball.dx == 0 and ball.dy == 0:
                        ball.launch()
            
            # Update brick hover states
            for brick in bricks:
                brick.hover = (brick.hit > 0 and mode == "fast_autoplay" and
                             brick.x <= mouse_pos[0] <= brick.x + BRICK_WIDTH and
                             brick.y <= mouse_pos[1] <= brick.y + BRICK_HEIGHT)
            
            if mode == "autoplay":
                # Autopilot: move paddle toward ball
                paddle_center = paddle.x + paddle.width / 2
                ball_center = ball.x + BALL_SIZE / 2
                if abs(paddle_center - ball_center) > 5:
                    if paddle_center < ball_center:
                        paddle.move_right()
                    elif paddle_center > ball_center:
                        paddle.move_left()
                if ball.dx == 0 and ball.dy == 0:
                    ball.launch()
            elif mode == "fast_autoplay":
                # Fast autopilot: keep a persistent target brick until it is broken
                active_bricks = [brick for brick in bricks if brick.hit > 0]
                if active_bricks:
                    if chosen_brick is None or chosen_brick.hit <= 0 or chosen_brick not in active_bricks:
                        chosen_brick = random.choice(active_bricks)
                        ball.last_distance_to_target = None
                    target_x = chosen_brick.x + (BRICK_WIDTH / 2)
                    target_y = chosen_brick.y + (BRICK_HEIGHT / 2)
                else:
                    target_x = ball.x + BALL_SIZE/2
                    target_y = 0
                    chosen_brick = None
                
                # Calculate paddle position
                desired_x = calculate_intercept_position(
                    ball.x + BALL_SIZE/2, ball.y + BALL_SIZE/2,
                    ball.dx, ball.dy,
                    target_x, target_y,
                    paddle.y,
                    try_alternative=not ball.hits_getting_closer
                )
                
                # Move paddle more aggressively for falling balls
                paddle_center = paddle.x + paddle.width/2
                if ball.dy > 0:  # Ball is falling
                    # Double speed and use direct positioning for falling balls
                    move_speed = paddle.speed * 2
                    if abs(paddle_center - desired_x) > 2:
                        if paddle_center < desired_x:
                            paddle.x = min(paddle.x + move_speed, WINDOW_WIDTH - paddle.width)
                        else:
                            paddle.x = max(paddle.x - move_speed, 0)
                else:
                    # Normal movement for rising balls
                    if abs(paddle_center - desired_x) > 5:
                        if paddle_center < desired_x:
                            paddle.move_right()
                        else:
                            paddle.move_left()

                # Launch ball if stationary
                if ball.dx == 0 and ball.dy == 0:
                    ball.launch()
                    ball.dx *= 1.5
                    ball.dy *= 1.5
            else:
                # Manual mode: use keyboard for paddle movement
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    paddle.move_left()
                if keys[pygame.K_RIGHT]:
                    paddle.move_right()

            # Update ball when in motion
            gained_points = ball.update(paddle, bricks)
            score += gained_points
            # Check for paddle hit event and record count.
            if ball.hit_paddle:
                paddle_hits += 1
                ball.hit_paddle = False

            # Check if ball fell below
            if ball.y > WINDOW_HEIGHT:
                lives -= 1
                ball.reset()
                if lives <= 0:
                    running = False

            # Check if all *breakable* bricks destroyed -> level clear / advance.
            if all(brick.hit <= 0 for brick in bricks):
                # T-000114: terminal progress print on level clear
                _cleared_level = current_level
                _cleared_name = LEVELS[_cleared_level - 1]["name"]
                _cleared_elapsed = time.monotonic() - level_start_time
                print(f"[bricks] Level {_cleared_level} ({_cleared_name}) completed in {_cleared_elapsed:.2f}s", flush=True)
                # Persist progress (next level unlocked, or final level cleared).
                next_level = current_level + 1
                if next_level <= TOTAL_LEVELS:
                    highest_unlocked = max(highest_unlocked, next_level)
                    save_progress(highest_unlocked)
                    current_level = next_level
                    show_level_overlay(screen, font, clock, current_level, duration_ms=1000)
                    bricks = create_bricks(current_level)
                    total_initial_hits += sum(b.initial for b in bricks)
                    # Reset ball; preserve paddle position, lives, score
                    ball.reset()
                    chosen_brick = None
                    # Reset per-level timer for the next level's print
                    level_start_time = time.monotonic()
                else:
                    # Final level cleared
                    highest_unlocked = TOTAL_LEVELS
                    save_progress(highest_unlocked)
                    victory = True
                    running = False

            # Drawing game and HUD; compute pending hits as sum of remaining (current) brick hits.
            pending_hits = sum(brick.hit for brick in bricks if brick.hit > 0)
            # Compute misses = paddle_hits - (total hits achieved), where total achieved = total_initial_hits - pending_hits.
            # So, misses = paddle_hits + pending_hits - total_initial_hits.
            misses = max(0, paddle_hits + pending_hits - total_initial_hits)

            # Drawing game
            screen.fill(BLACK)
            paddle.draw(screen)
            ball.draw(screen)
            for brick in bricks:
                brick.draw(screen)
                # Highlight the chosen and hovered bricks
                if mode == "fast_autoplay":
                    if chosen_brick is not None and brick is chosen_brick:
                        pygame.draw.rect(screen, (255, 255, 0), 
                                       (brick.x, brick.y, brick.width, brick.height), 3)
            
            # Draw scores in two lines with better spacing
            # First line: Score, Lives, Time, Level
            score_label = f"Score: {score}" + ("  [AI]" if mode in ("autoplay", "fast_autoplay") else "")
            score_text = font.render(score_label, True, WHITE)
            lives_text = font.render(f"Lives: {lives}", True, WHITE)
            elapsed_sec = (pygame.time.get_ticks() - start_time) // 1000
            time_text = font.render(f"Time: {elapsed_sec} sec", True, WHITE)
            level_text = font.render(f"Level: {current_level}/{TOTAL_LEVELS}", True, WHITE)

            # Second line: Paddle hits, Misses, Remaining bricks
            hits_text = font.render(f"Paddle Hits: {paddle_hits}", True, WHITE)
            misses_text = font.render(f"Misses: {misses}", True, WHITE)
            remaining_text = font.render(f"Remaining Bricks: {pending_hits}", True, WHITE)

            # First line positioning
            screen.blit(score_text, (20, 10))
            screen.blit(lives_text, (220, 10))
            screen.blit(time_text, (400, 10))
            screen.blit(level_text, (640, 10))

            # Second line positioning
            screen.blit(hits_text, (20, 40))
            screen.blit(misses_text, (250, 40))
            screen.blit(remaining_text, (480, 40))
            
            pygame.display.flip()
        
        # Update prev_stats before showing end screen
        prev_stats = {
            'score': score,
            'time': elapsed_sec,
            'hits': paddle_hits,
            'misses': misses
        }
        
        # Enhanced end screen with detailed stats
        screen.fill(BLACK)
        if victory:
            title_text = font.render("VICTORY! All levels cleared!", True, WHITE)
        elif lives > 0:
            title_text = font.render("You Win!", True, WHITE)
        else:
            title_text = font.render("Game Over!", True, WHITE)
        
        # Show detailed stats
        final_score_text = font.render(f"Final Score: {score}", True, WHITE)
        final_time = font.render(f"Time: {elapsed_sec} sec", True, WHITE)
        final_hits = font.render(f"Total Hits: {paddle_hits}", True, WHITE)
        final_misses = font.render(f"Total Misses: {misses}", True, WHITE)
        restart_text = font.render("Press any button to restart", True, WHITE)
        esc_hint_text = font.render("ESC to quit", True, WHITE)

        # Position all end screen elements
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
        screen.blit(final_score_text, (WINDOW_WIDTH//2 - final_score_text.get_width()//2, WINDOW_HEIGHT//2 - 40))
        screen.blit(final_time, (WINDOW_WIDTH//2 - final_time.get_width()//2, WINDOW_HEIGHT//2))
        screen.blit(final_hits, (WINDOW_WIDTH//2 - final_hits.get_width()//2, WINDOW_HEIGHT//2 + 40))
        screen.blit(final_misses, (WINDOW_WIDTH//2 - final_misses.get_width()//2, WINDOW_HEIGHT//2 + 80))
        screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 140))
        screen.blit(esc_hint_text, (WINDOW_WIDTH//2 - esc_hint_text.get_width()//2, WINDOW_HEIGHT//2 + 170))

        pygame.display.flip()
        # Non-blocking wait so QUIT events are still handled during the end screen
        _end_deadline = pygame.time.get_ticks() + 3000
        while pygame.time.get_ticks() < _end_deadline:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit(0)
            clock.tick(30)

if __name__ == "__main__":
    main()