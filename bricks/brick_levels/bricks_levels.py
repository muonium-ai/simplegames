from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt

import pygame
import sys
import random
import math
import json
import os
from bricks import *  # Import all from original bricks.py
from brick_colors import get_brick_color  # Add this import

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
            # Alter dx based on where it hits the paddle
            hit_pos = (self.x + BALL_SIZE/2) - (paddle.x + paddle.width/2)
            self.dx = hit_pos * 0.05
            self.dy = -self.dy
            self.hit_paddle = True

        # Collide with bricks
        for brick in bricks:
            if brick.hit > 0:
                if (self.x + BALL_SIZE > brick.x and
                    self.x < brick.x + brick.width and
                    self.y + BALL_SIZE > brick.y and
                    self.y < brick.y + brick.height):
                    brick.hit -= 1
                    if abs((self.x + BALL_SIZE) - brick.x) < 5 or abs(self.x - (brick.x + brick.width)) < 5:
                        self.dx = -self.dx
                    else:
                        self.dy = -self.dy
                    return brick.points  # Return the points from the collision
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
    def __init__(self, x, y, hit=1):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.hit = hit  # Durability
        self.initial = hit  # Save initial hit count for miss calculation
        self.points = 10 * hit
        self.hover = False  # Add hover state

    def draw(self, surface):
        if self.hit > 0:
            color = BLUE if self.hit == 1 else RED
            pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
            # Draw hover effect
            if self.hover:
                pygame.draw.rect(surface, (255, 255, 255), 
                               (self.x, self.y, self.width, self.height), 2)

class LevelManager:
    def __init__(self, levels_dir="levels"):
        self.levels_dir = levels_dir
        self.current_level = 1
        self.max_level = self._count_levels()
        
        # Create levels directory if it doesn't exist
        os.makedirs(levels_dir, exist_ok=True)

    def _count_levels(self):
        """Count how many level files exist"""
        count = 0
        while os.path.exists(self.get_level_path(count + 1)):
            count += 1
        return count

    def get_level_path(self, level_number):
        return os.path.join(self.levels_dir, f"level{level_number}.json")

    def load_level(self, level_number=None):
        """Load a specific level or current level if none specified"""
        if level_number is None:
            level_number = self.current_level
            
        try:
            with open(self.get_level_path(level_number), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.generate_default_level()

    def generate_default_level(self):
        """Generate a default level if no level file exists"""
        return {
            "level_name": f"Level {self.current_level}",
            "background_color": [0, 0, 0],
            "bricks": [
                {
                    "x": col * (BRICK_WIDTH + BRICK_GAP),
                    "y": row * (BRICK_HEIGHT + BRICK_GAP) + 50,
                    "hits": min(row + 1, 5),
                    "color": min(row + 1, 5)
                }
                for row in range(BRICK_ROWS)
                for col in range(BRICK_COLS)
            ]
        }

    def create_bricks(self):
        """Create brick objects from current level data"""
        level_data = self.load_level()
        bricks = []
        
        for brick_data in level_data["bricks"]:
            brick = Brick(
                x=brick_data["x"],
                y=brick_data["y"],
                hit=brick_data["hits"]
            )
            if brick.hit == -1:  # Unbreakable brick
                brick.points = 0
            brick.color = get_brick_color(brick_data["color"])
            bricks.append(brick)
            
        return bricks

    def next_level(self):
        """Advance to next level if available"""
        if self.current_level < self.max_level:
            self.current_level += 1
            return True
        return False

    def save_level(self, bricks, level_number=None):
        """Save current brick configuration as a level"""
        if level_number is None:
            level_number = self.current_level

        level_data = {
            "level_name": f"Level {level_number}",
            "background_color": [0, 0, 0],
            "bricks": [
                {
                    "x": brick.x,
                    "y": brick.y,
                    "hits": brick.hit,
                    "color": 6 if brick.hit == -1 else min(brick.hit, 5)
                }
                for brick in bricks
            ]
        }

        with open(self.get_level_path(level_number), 'w') as f:
            json.dump(level_data, f, indent=4)

def show_modal(screen, font, prev_stats=None):
    """Display modal with three buttons and previous game stats if available"""
    modal_rect = pygame.Rect(100, 200, 800, 200)  # Made taller for stats
    # Define three buttons horizontally arranged
    start_button = pygame.Rect(modal_rect.x + 50, modal_rect.y + 125, 200, 50)
    auto_button = pygame.Rect(modal_rect.x + 300, modal_rect.y + 125, 200, 50)
    fast_button = pygame.Rect(modal_rect.x + 550, modal_rect.y + 125, 200, 50)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
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
    level_manager = LevelManager()  # Create level manager once
    
    while True:  # Outer loop to allow restarting the game
        mode = show_modal(screen, font, prev_stats)
        
        game_completed = False
        while not game_completed:  # New loop for level progression
            # Initialize game variables
            paddle = Paddle()
            if mode == "fast_autoplay":
                paddle.speed = FAST_PADDLE_SPEED
            ball = Ball()
            bricks = level_manager.create_bricks()  # Create bricks for current level
            total_initial_hits = sum(b.initial for b in bricks)
            score = prev_stats['score'] if prev_stats else 0  # Maintain score between levels
            lives = STARTING_LIVES
            paddle_hits = 0
            start_time = pygame.time.get_ticks()
            chosen_brick = None

            # Level transition screen
            screen.fill(BLACK)
            level_text = font.render(f"Level {level_manager.current_level}", True, WHITE)
            screen.blit(level_text, (WINDOW_WIDTH//2 - level_text.get_width()//2, WINDOW_HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)

            running = True
            while running:
                clock.tick(FPS)
            
                # Get mouse position for hover effect
                mouse_pos = pygame.mouse.get_pos()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
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

                # Check if all bricks destroyed
                if all(brick.hit <= 0 for brick in bricks):
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
                # First line: Score, Lives, Time
                score_text = font.render(f"Score: {score}", True, WHITE)
                lives_text = font.render(f"Lives: {lives}", True, WHITE)
                level_text = font.render(f"Level: {level_manager.current_level}", True, WHITE)
                elapsed_sec = (pygame.time.get_ticks() - start_time) // 1000
                time_text = font.render(f"Time: {elapsed_sec} sec", True, WHITE)
                
                # Second line: Paddle hits, Misses, Remaining bricks
                hits_text = font.render(f"Paddle Hits: {paddle_hits}", True, WHITE)
                misses_text = font.render(f"Misses: {misses}", True, WHITE)
                remaining_text = font.render(f"Remaining Bricks: {pending_hits}", True, WHITE)
                
                # First line positioning with level
                screen.blit(score_text, (20, 10))
                screen.blit(lives_text, (200, 10))
                screen.blit(level_text, (380, 10))
                screen.blit(time_text, (560, 10))
                
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
            
            if lives <= 0:
                game_completed = True  # Game over if no lives left

            # Modified level completion check
            if all(brick.hit <= 0 or brick.hit == -1 for brick in bricks):
                if level_manager.next_level():
                    running = False  # Go to next level
                else:
                    running = False
                    game_completed = True  # All levels completed

        # Enhanced end screen with detailed stats
        screen.fill(BLACK)
        if lives > 0:
            title_text = font.render("Congratulations! All Levels Completed!", True, WHITE)
        else:
            title_text = font.render("Game Over!", True, WHITE)
        
        # Show detailed stats
        final_score_text = font.render(f"Final Score: {score}", True, WHITE)
        final_time = font.render(f"Time: {elapsed_sec} sec", True, WHITE)
        final_hits = font.render(f"Total Hits: {paddle_hits}", True, WHITE)
        final_misses = font.render(f"Total Misses: {misses}", True, WHITE)
        restart_text = font.render("Press any button to restart", True, WHITE)
        
        # Position all end screen elements
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
        screen.blit(final_score_text, (WINDOW_WIDTH//2 - final_score_text.get_width()//2, WINDOW_HEIGHT//2 - 40))
        screen.blit(final_time, (WINDOW_WIDTH//2 - final_time.get_width()//2, WINDOW_HEIGHT//2))
        screen.blit(final_hits, (WINDOW_WIDTH//2 - final_hits.get_width()//2, WINDOW_HEIGHT//2 + 40))
        screen.blit(final_misses, (WINDOW_WIDTH//2 - final_misses.get_width()//2, WINDOW_HEIGHT//2 + 80))
        screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 140))
        
        pygame.display.flip()
        pygame.time.wait(3000)

        # Reset level manager for next game
        level_manager.current_level = 1

if __name__ == "__main__":
    main()