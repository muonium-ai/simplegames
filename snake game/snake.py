import pygame
import random
import sys
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
PROGRESS_BAR_COLOR = (255, 255, 0)

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.reset_game()

        # Load sound effects
        self.game_over_sound = pygame.mixer.Sound("game_over.wav")
        self.eating_sound = pygame.mixer.Sound("eating.wav")

    def reset_game(self):
        self.snake = [(GRID_COUNT // 2, GRID_COUNT // 2)]
        self.direction = Direction.RIGHT
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.progress = 0
        self.progress_to_next_grow = 5

    def spawn_food(self):
        while True:
            food = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
            if food not in self.snake:
                return food

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN
                elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
        return True

    def update(self):
        if self.game_over:
            return

        # Move snake
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = ((head_x + dx) % GRID_COUNT, (head_y + dy) % GRID_COUNT)

        # Check collision with self or boundary
        if new_head in self.snake or new_head[0] < 0 or new_head[0] >= GRID_COUNT or new_head[1] < 0 or new_head[1] >= GRID_COUNT:
            self.game_over = True
            pygame.mixer.Sound.play(self.game_over_sound)
            return

        self.snake.insert(0, new_head)

        # Check if food eaten
        if new_head == self.food:
            self.score += 1
            self.progress += 1
            self.progress_to_next_grow -= 1
            pygame.mixer.Sound.play(self.eating_sound)
            if self.progress_to_next_grow == 0:
                self.snake.append(self.snake[-1])
                self.progress_to_next_grow = 5
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        self.screen.fill(BLACK)

        # Draw snake
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN, 
                           (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, 
                            GRID_SIZE - 2, GRID_SIZE - 2))

        # Draw food
        pygame.draw.rect(self.screen, RED,
                        (self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE,
                         GRID_SIZE - 2, GRID_SIZE - 2))

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw progress bar
        progress_bar_width = (self.progress / self.progress_to_next_grow) * GRID_SIZE * 4
        pygame.draw.rect(self.screen, PROGRESS_BAR_COLOR, (10, 50, progress_bar_width, 20))

        # Draw game over message
        if self.game_over:
            game_over_text = font.render('Game Over! Press R to Restart', True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2))
            self.screen.blit(game_over_text, text_rect)

        pygame.display.flip()

    def run(self):
        while True:
            if not self.handle_input():
                break
            self.update()
            self.draw()
            self.clock.tick(10)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = SnakeGame()
    game.run()