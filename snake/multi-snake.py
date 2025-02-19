from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt

import pygame
import random
import time
from enum import Enum
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
SNAKE_COLORS = [
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 165, 0),  # Orange
    (128, 0, 128)   # Purple
]

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class AIStrategy:
    @staticmethod
    def basic_pathfinding(snake_head: tuple, food_pos: tuple, obstacles: List) -> Direction:
        x, y = snake_head
        food_x, food_y = food_pos
        
        # Simple direction choice based on food position
        if abs(food_x - x) > abs(food_y - y):
            return Direction.RIGHT if food_x > x else Direction.LEFT
        else:
            return Direction.DOWN if food_y > y else Direction.UP

class Snake:
    def __init__(self, start_pos: tuple, color: tuple, ai_strategy):
        self.body = [start_pos]
        self.color = color
        self.direction = Direction.RIGHT
        self.ai_strategy = ai_strategy
        self.alive = True
        self.length = 1
        self.survival_time = 0

    def move(self, food_pos: tuple, obstacles: List):
        if not self.alive:
            return

        # Get new direction from AI
        self.direction = self.ai_strategy(self.body[0], food_pos, obstacles)
        
        # Calculate new head position
        new_head = (
            (self.body[0][0] + self.direction.value[0]) % GRID_WIDTH,
            (self.body[0][1] + self.direction.value[1]) % GRID_HEIGHT
        )

        # Check collision with self or other snakes
        if new_head in obstacles:
            self.alive = False
            return

        self.body.insert(0, new_head)
        if new_head != food_pos:
            self.body.pop()
        else:
            self.length += 1

class Game:
    def __init__(self, num_snakes=4):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Multi-Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Initialize snakes
        self.snakes = []
        for i in range(num_snakes):
            start_pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            self.snakes.append(Snake(start_pos, SNAKE_COLORS[i], AIStrategy.basic_pathfinding))
        
        self.food_pos = self.generate_food()
        self.start_time = time.time()

    def generate_food(self) -> tuple:
        while True:
            pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            if not any(pos in snake.body for snake in self.snakes):
                return pos

    def get_all_obstacles(self, current_snake: Snake) -> List:
        obstacles = []
        for snake in self.snakes:
            if snake != current_snake:
                obstacles.extend(snake.body)
        return obstacles

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw food
        pygame.draw.rect(self.screen, RED, 
                        (self.food_pos[0]*GRID_SIZE, self.food_pos[1]*GRID_SIZE, 
                         GRID_SIZE-2, GRID_SIZE-2))
        
        # Draw snakes
        for snake in self.snakes:
            for segment in snake.body:
                pygame.draw.rect(self.screen, snake.color,
                               (segment[0]*GRID_SIZE, segment[1]*GRID_SIZE,
                                GRID_SIZE-2, GRID_SIZE-2))
        
        # Draw timer
        elapsed_time = int(time.time() - self.start_time)
        timer_text = self.font.render(f"Time: {elapsed_time}", True, WHITE)
        self.screen.blit(timer_text, (WINDOW_WIDTH - 150, 10))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Update snake positions
            for snake in self.snakes:
                obstacles = self.get_all_obstacles(snake)
                snake.move(self.food_pos, obstacles)
                snake.survival_time = time.time() - self.start_time

            # Check if food is eaten
            for snake in self.snakes:
                if snake.body[0] == self.food_pos:
                    self.food_pos = self.generate_food()

            # Check game over condition
            alive_snakes = [snake for snake in self.snakes if snake.alive]
            if len(alive_snakes) <= 1:
                self.show_winner_screen(alive_snakes)
                running = False

            self.draw()
            self.clock.tick(10)

    def show_winner_screen(self, alive_snakes):
        self.screen.fill(BLACK)
        y_pos = 100
        
        title = self.font.render("Game Over - Winners", True, WHITE)
        self.screen.blit(title, (WINDOW_WIDTH//2 - 100, 50))

        # Sort snakes by length and survival time
        all_snakes = sorted(self.snakes, 
                          key=lambda x: (x.length, x.survival_time), 
                          reverse=True)

        for i, snake in enumerate(all_snakes):
            status = "Alive" if snake.alive else "Dead"
            text = f"Snake {i+1}: Length={snake.length}, Time={int(snake.survival_time)}s, {status}"
            text_surface = self.font.render(text, True, snake.color)
            self.screen.blit(text_surface, (100, y_pos))
            y_pos += 50

        pygame.display.flip()
        pygame.time.wait(5000)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
