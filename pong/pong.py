
# filepath: /C:/Users/senth/fosstercare/simplegames/pong/pong.py

import pygame
import sys
import random

# --- Constants ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

PADDLE_WIDTH = 10
PADDLE_HEIGHT = 80
BALL_SIZE = 14

PADDLE_SPEED = 5
BALL_SPEED_X = 4
BALL_SPEED_Y = 4

SCORE_FONT_SIZE = 36
WINNING_SCORE = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED
        self.score = 0

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, self.height))

    def move_up(self):
        self.y -= self.speed
        if self.y < 0:
            self.y = 0

    def move_down(self):
        self.y += self.speed
        if self.y + self.height > WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT - self.height

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        # Random initial direction
        self.dx = random.choice([-BALL_SPEED_X, BALL_SPEED_X])
        self.dy = random.choice([-BALL_SPEED_Y, BALL_SPEED_Y])

    def draw(self, surface):
        pygame.draw.ellipse(surface, WHITE, (self.x, self.y, BALL_SIZE, BALL_SIZE))

    def update(self, left_paddle: Paddle, right_paddle: Paddle):
        self.x += self.dx
        self.y += self.dy

        # Collision with top or bottom
        if self.y <= 0:
            self.y = 0
            self.dy = -self.dy
        elif self.y + BALL_SIZE >= WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT - BALL_SIZE
            self.dy = -self.dy

        # Check collision with paddles
        if (self.x <= left_paddle.x + left_paddle.width and
            self.y + BALL_SIZE >= left_paddle.y and
            self.y <= left_paddle.y + left_paddle.height):
            self.x = left_paddle.x + left_paddle.width
            self.dx = -self.dx
            # Optional: make collision more dynamic based on contact point
        if (self.x + BALL_SIZE >= right_paddle.x and
            self.y + BALL_SIZE >= right_paddle.y and
            self.y <= right_paddle.y + right_paddle.height):
            self.x = right_paddle.x - BALL_SIZE
            self.dx = -self.dx
            # Optional: make collision more dynamic based on contact point

        # Scoring
        if self.x < 0:
            right_paddle.score += 1
            self.reset()
        elif self.x > WINDOW_WIDTH:
            left_paddle.score += 1
            self.reset()

def draw_center_line(surface):
    # Dashed line
    dash_len = 10
    gap_len = 10
    y = 0
    while y < WINDOW_HEIGHT:
        pygame.draw.line(surface, WHITE, (WINDOW_WIDTH // 2, y),
                         (WINDOW_WIDTH // 2, y + dash_len), 2)
        y += dash_len + gap_len

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()

    # Sound placeholders (optional)
    # paddle_sound = pygame.mixer.Sound("paddle_beep.wav")
    # score_sound = pygame.mixer.Sound("score.wav")

    score_font = pygame.font.SysFont(None, SCORE_FONT_SIZE)

    left_paddle = Paddle(50, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2)
    right_paddle = Paddle(WINDOW_WIDTH - 50 - PADDLE_WIDTH,
                          WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ball = Ball()

    paused = False
    game_over = False
    winner_text = ""

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_r:
                    left_paddle.score = 0
                    right_paddle.score = 0
                    ball.reset()
                    paused = False
                    game_over = False
                    winner_text = ""

        # Check for winner
        if left_paddle.score >= WINNING_SCORE:
            winner_text = "Left Player Wins!"
            game_over = True
        elif right_paddle.score >= WINNING_SCORE:
            winner_text = "Right Player Wins!"
            game_over = True

        # Handle input for paddles
        keys = pygame.key.get_pressed()
        if not paused and not game_over:
            # Left paddle
            if keys[pygame.K_w]:
                left_paddle.move_up()
            if keys[pygame.K_s]:
                left_paddle.move_down()

            # Right paddle
            if keys[pygame.K_UP]:
                right_paddle.move_up()
            if keys[pygame.K_DOWN]:
                right_paddle.move_down()

            # Update ball
            ball.update(left_paddle, right_paddle)

        screen.fill(BLACK)
        draw_center_line(screen)

        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)

        # Draw scores
        left_score_text = score_font.render(str(left_paddle.score), True, WHITE)
        right_score_text = score_font.render(str(right_paddle.score), True, WHITE)
        screen.blit(left_score_text, (WINDOW_WIDTH // 4, 20))
        screen.blit(right_score_text, (WINDOW_WIDTH * 3 // 4, 20))

        if paused and not game_over:
            pause_text = score_font.render("Paused", True, WHITE)
            screen.blit(pause_text, (WINDOW_WIDTH // 2 - 40, WINDOW_HEIGHT // 2 - 20))
        if game_over:
            # Display winner
            game_over_text = score_font.render(winner_text, True, WHITE)
            screen.blit(game_over_text,
                        (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2,
                         WINDOW_HEIGHT // 2 - 30))
            restart_text = score_font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text,
                        (WINDOW_WIDTH // 2 - restart_text.get_width() // 2,
                         WINDOW_HEIGHT // 2 + 10))

        pygame.display.flip()

if __name__ == "__main__":
    main()