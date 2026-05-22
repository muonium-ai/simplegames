"""Simple local two-player Pong implementation using pygame.

Supports an optional autoplay AI via the ``--autoplay`` CLI flag. The flag
accepts ``left``, ``right``, ``both`` or ``off`` (default ``off``). When a
side is set to autoplay, that paddle tracks the ball's y-position each tick,
clamped to the paddle's max speed. Paddles under AI control display a small
"AI" label near them. ESC still quits the game (see ticket T-000069).
"""

import argparse
import sys
import time

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt
import pygame
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

    def ai_track(self, target_y):
        """Move paddle toward target_y, clamped to the paddle's max speed."""
        paddle_center = self.y + self.height / 2
        delta = target_y - paddle_center
        # Small dead-zone to avoid jitter when aligned.
        if abs(delta) <= self.speed:
            self.y += delta
        elif delta > 0:
            self.y += self.speed
        else:
            self.y -= self.speed
        if self.y < 0:
            self.y = 0
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
        if (self.dx < 0 and
            self.x <= left_paddle.x + left_paddle.width and
            self.x + BALL_SIZE >= left_paddle.x and
            self.y + BALL_SIZE >= left_paddle.y and
            self.y <= left_paddle.y + left_paddle.height):
            self.x = left_paddle.x + left_paddle.width
            self.dx = -self.dx
            # Optional: make collision more dynamic based on contact point
        if (self.dx > 0 and
            self.x + BALL_SIZE >= right_paddle.x and
            self.x <= right_paddle.x + right_paddle.width and
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
                         (WINDOW_WIDTH // 2, min(y + dash_len, WINDOW_HEIGHT)), 2)
        y += dash_len + gap_len

def blit_centered_text(surface, font, text, y):
    rendered = font.render(text, True, WHITE)
    surface.blit(rendered, (WINDOW_WIDTH // 2 - rendered.get_width() // 2, y))

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Simple two-player Pong with optional AI autoplay."
    )
    parser.add_argument(
        "--autoplay",
        choices=["left", "right", "both", "off"],
        default="off",
        help=(
            "Enable AI control for paddles: 'left', 'right', 'both', or 'off' "
            "(default: off). AI paddles track the ball, clamped to paddle speed."
        ),
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    ai_left = args.autoplay in ("left", "both")
    ai_right = args.autoplay in ("right", "both")

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pong")
    clock = pygame.time.Clock()

    # Uniform autoplay speedup: when any AI is driving, run at ~2x normal FPS.
    autoplay_active = ai_left or ai_right
    effective_fps = FPS * 2 if autoplay_active else FPS

    # Sound placeholders (optional)
    # paddle_sound = pygame.mixer.Sound("paddle_beep.wav")
    # score_sound = pygame.mixer.Sound("score.wav")

    score_font = pygame.font.SysFont(None, SCORE_FONT_SIZE)
    hint_font = pygame.font.SysFont(None, 22)

    left_paddle = Paddle(50, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2)
    right_paddle = Paddle(WINDOW_WIDTH - 50 - PADDLE_WIDTH,
                          WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ball = Ball()

    paused = False
    game_over = False
    winner_text = ""
    # T-000117: track per-round start so autoplay can print outcome timing.
    round_start_time = time.monotonic()

    running = True
    while running:
        clock.tick(effective_fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit(0)
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
            ball_center_y = ball.y + BALL_SIZE / 2

            # Left paddle
            if ai_left:
                left_paddle.ai_track(ball_center_y)
            else:
                if keys[pygame.K_w]:
                    left_paddle.move_up()
                if keys[pygame.K_s]:
                    left_paddle.move_down()

            # Right paddle
            if ai_right:
                right_paddle.ai_track(ball_center_y)
            else:
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

        # AI labels near AI-controlled paddles
        if ai_left:
            ai_label = hint_font.render("AI", True, WHITE)
            screen.blit(
                ai_label,
                (left_paddle.x, max(0, left_paddle.y - ai_label.get_height() - 2)),
            )
        if ai_right:
            ai_label = hint_font.render("AI", True, WHITE)
            screen.blit(
                ai_label,
                (
                    right_paddle.x + right_paddle.width - ai_label.get_width(),
                    max(0, right_paddle.y - ai_label.get_height() - 2),
                ),
            )

        # ESC to quit hint
        hint_surface = hint_font.render("ESC to quit", True, WHITE)
        screen.blit(hint_surface, (10, WINDOW_HEIGHT - hint_surface.get_height() - 8))

        if paused and not game_over:
            blit_centered_text(screen, score_font, "Paused", WINDOW_HEIGHT // 2 - 20)
        if game_over:
            # Display winner
            blit_centered_text(screen, score_font, winner_text, WINDOW_HEIGHT // 2 - 30)
            blit_centered_text(screen, score_font, "Press R to Restart", WINDOW_HEIGHT // 2 + 10)

        pygame.display.flip()

        # T-000117: in autoplay mode, on game over print outcome, hold ~1s, restart.
        if game_over and autoplay_active:
            # If both sides are AI, the winner is just "WIN" (someone won the
            # match). If only one side is AI, treat that side's victory as WIN
            # and the other as LOSS.
            if ai_left and ai_right:
                outcome = "WIN"
            elif ai_left:
                outcome = "WIN" if left_paddle.score >= WINNING_SCORE else "LOSS"
            else:  # ai_right
                outcome = "WIN" if right_paddle.score >= WINNING_SCORE else "LOSS"
            elapsed = time.monotonic() - round_start_time
            print(f"[pong] {outcome} in {elapsed:.2f}s", flush=True)
            restart_deadline = pygame.time.get_ticks() + 1000
            while pygame.time.get_ticks() < restart_deadline:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit(0)
                clock.tick(60)
            left_paddle.score = 0
            right_paddle.score = 0
            ball.reset()
            game_over = False
            winner_text = ""
            round_start_time = time.monotonic()

    pygame.quit()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())