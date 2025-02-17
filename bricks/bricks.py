from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt

import pygame
import sys
import random

# --- Constants ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 6

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

    def reset(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - 60
        self.dx = 0
        self.dy = 0  # Set 0 so ball is "held" until space pressed

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
        return 0

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x + BALL_SIZE/2), int(self.y + BALL_SIZE/2)), BALL_SIZE//2)

class Brick:
    def __init__(self, x, y, hit=1):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.hit = hit  # Durability
        self.points = 10 * hit

    def draw(self, surface):
        if self.hit > 0:
            color = BLUE if self.hit == 1 else RED
            pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))

def create_bricks(level=1):
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = col * (BRICK_WIDTH + BRICK_GAP)
            y = row * (BRICK_HEIGHT + BRICK_GAP) + 50
            # Optional: increase brick hits with level or row
            hit_value = 1 if row < 2 else 2
            bricks.append(Brick(x, y, hit_value))
    return bricks

def show_modal(screen, font):
    """Display a modal window with two buttons and return 'manual' or 'autoplay'."""
    modal_rect = pygame.Rect(200, 150, 400, 300)
    start_button = pygame.Rect(250, 250, 140, 50)
    auto_button = pygame.Rect(410, 250, 140, 50)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return "manual"
                if auto_button.collidepoint(event.pos):
                    return "autoplay"
        
        screen.fill(BLACK)
        # Draw modal backdrop
        pygame.draw.rect(screen, GRAY, modal_rect)
        # Draw buttons
        pygame.draw.rect(screen, WHITE, start_button)
        pygame.draw.rect(screen, WHITE, auto_button)
        # Render button texts
        start_text = font.render("Start Game", True, BLACK)
        auto_text = font.render("Autoplay", True, BLACK)
        screen.blit(start_text, start_text.get_rect(center=start_button.center))
        screen.blit(auto_text, auto_text.get_rect(center=auto_button.center))
        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Brick Breaker")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    
    while True:  # Outer loop to allow restarting the game
        # Show modal window for mode selection at start/restart
        mode = show_modal(screen, font)
        
        # Initialize game variables
        paddle = Paddle()
        ball = Ball()
        bricks = create_bricks()
        score = 0
        lives = STARTING_LIVES

        running = True
        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif mode == "manual" and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and ball.dx == 0 and ball.dy == 0:
                        ball.launch()
            
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
            else:
                # Manual mode: use keyboard for paddle movement
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    paddle.move_left()
                if keys[pygame.K_RIGHT]:
                    paddle.move_right()

            # Update ball when in motion
            if ball.dx != 0 or ball.dy != 0:
                gained_points = ball.update(paddle, bricks)
                score += gained_points

            # Check if ball fell below
            if ball.y > WINDOW_HEIGHT:
                lives -= 1
                ball.reset()
                if lives <= 0:
                    running = False

            # Check if all bricks destroyed
            if all(brick.hit <= 0 for brick in bricks):
                running = False

            # Drawing game
            screen.fill(BLACK)
            paddle.draw(screen)
            ball.draw(screen)
            for brick in bricks:
                brick.draw(screen)
            score_text = font.render(f"Score: {score}", True, WHITE)
            lives_text = font.render(f"Lives: {lives}", True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(lives_text, (200, 10))
            pygame.display.flip()
        
        # End screen before restarting
        screen.fill(BLACK)
        end_text = font.render("You Win!" if lives > 0 else "Game Over!", True, WHITE)
        screen.blit(end_text, (WINDOW_WIDTH//2 - end_text.get_width()//2, WINDOW_HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(3000)

if __name__ == "__main__":
    main()