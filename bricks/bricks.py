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

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Brick Breaker")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

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
                running = False
            elif event.type == pygame.KEYDOWN:
                # Launch the ball if it's stationary
                if event.key == pygame.K_SPACE and ball.dx == 0 and ball.dy == 0:
                    ball.launch()

        # Check continuous key presses for smoother movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move_left()
        if keys[pygame.K_RIGHT]:
            paddle.move_right()

        # Update ball
        if ball.dy != 0 or ball.dx != 0:
            gained_points = ball.update(paddle, bricks)
            score += gained_points

        # Check if ball fell below
        if ball.y > WINDOW_HEIGHT:
            lives -= 1
            ball.reset()
            if lives <= 0:
                # Game Over
                running = False

        # Check if all bricks destroyed
        if all(brick.hit <= 0 for brick in bricks):
            # Next level or game win
            # For simplicity, show end screen
            running = False

        # Draw everything
        screen.fill(BLACK)
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)

        # Draw score and lives
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (200, 10))

        pygame.display.flip()

    # End screen
    screen.fill(BLACK)
    if lives > 0:
        end_text = font.render("You Win!", True, WHITE)
    else:
        end_text = font.render("Game Over!", True, WHITE)
    screen.blit(end_text, (WINDOW_WIDTH // 2 - end_text.get_width() // 2, WINDOW_HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()