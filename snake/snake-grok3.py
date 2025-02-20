from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import random
from enum import Enum
from typing import List, Tuple, Set
import time

pygame.init()

# Constants moved to global scope for better access
WINDOW_CONFIGS = {
    'small': {'width': 800, 'height': 600, 'num_snakes': 4, 'grid_size': 20},
    'large': {'width': 1920, 'height': 1080, 'num_snakes': 10, 'grid_size': 20}
}
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'GRAY': (128, 128, 128),
    'SNAKE': [(0, 255, 0), (0, 0, 255), (255, 165, 0), (128, 0, 128),
              (255, 0, 255), (0, 255, 255), (255, 255, 0), (165, 42, 42),
              (219, 112, 147), (0, 128, 0)]
}

class Direction(Enum):
    UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

class AIStrategy:
    @staticmethod
    def basic_pathfinding(snake_head: Tuple[int, int], food_pos: Tuple[int, int], 
                         obstacles: Set[Tuple[int, int]], grid_size: Tuple[int, int]) -> Direction:
        x, y = snake_head
        food_x, food_y = food_pos
        grid_width, grid_height = grid_size
        
        best_score = float('-inf')
        best_direction = Direction.RIGHT
        
        for direction in Direction:
            dx, dy = direction.value
            new_x, new_y = x + dx, y + dy
            
            if (new_x < 0 or new_x >= grid_width or 
                new_y < 0 or new_y >= grid_height or 
                (new_x, new_y) in obstacles):
                continue
                
            dist = abs(food_x - new_x) + abs(food_y - new_y)
            score = -dist  # Simplified scoring
            
            if score > best_score:
                best_score = score
                best_direction = direction
                
        return best_direction

class Snake:
    def __init__(self, start_pos: Tuple[int, int], color: Tuple[int, int, int], grid_size: Tuple[int, int]):
        self.body = [start_pos]
        self.color = color
        self.direction = Direction.RIGHT
        self.alive = True
        self.length = 1
        self.survival_time = 0
        self.grid_width, self.grid_height = grid_size
        self.body_set = {start_pos}  # For O(1) lookup
        
    def move(self, food_pos: Tuple[int, int], obstacles: Set[Tuple[int, int]], current_time: float):
        if not self.alive:
            return
            
        x, y = self.body[0]
        self.direction = AIStrategy.basic_pathfinding(
            (x, y), food_pos, obstacles, (self.grid_width, self.grid_height))
        
        dx, dy = self.direction.value
        new_head = (x + dx, y + dy)
        
        # Combined collision checks
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or 
            new_head[1] < 0 or new_head[1] >= self.grid_height or 
            new_head in obstacles or new_head in self.body_set):  # Added self-collision check
            self.alive = False
            return
            
        self.body.insert(0, new_head)
        self.body_set.add(new_head)
        
        if new_head != food_pos and len(self.body) > 1:  # Only remove tail if we didn't eat
            tail = self.body.pop()
            if tail in self.body_set:  # Check if tail exists before removing
                self.body_set.remove(tail)
        elif new_head == food_pos:
            self.length += 1
            
        self.survival_time = current_time

class Game:
    def __init__(self, window_mode: str = 'small'):
        config = WINDOW_CONFIGS[window_mode]
        self.screen = pygame.display.set_mode((config['width'], config['height']))
        pygame.display.set_caption(f"Multi-Snake Game - {window_mode.title()}")
        
        self.grid_size = config['grid_size']
        self.grid_width = config['width'] // self.grid_size
        self.grid_height = config['height'] // self.grid_size
        self.num_snakes = config['num_snakes']
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.food_timeout = 15.0
        self.food_wall_margin = 2
        
        # Pre-calculate rendering constants
        self.cell_size = self.grid_size - 2
        self.dead_border = self.cell_size + 2
        
        self.initialize_game()
        self.running = True
        
    def initialize_game(self):
        self.snakes = [
            Snake((random.randint(0, self.grid_width-1), 
                  random.randint(0, self.grid_height-1)), 
                  COLORS['SNAKE'][i], (self.grid_width, self.grid_height))
            for i in range(self.num_snakes)
        ]
        self.food_pos = self.generate_food()
        self.food_spawn_time = self.start_time = time.time()
        
    def generate_food(self) -> Tuple[int, int]:
        for _ in range(100):
            pos = (random.randint(self.food_wall_margin, self.grid_width - self.food_wall_margin - 1),
                   random.randint(self.food_wall_margin, self.grid_height - self.food_wall_margin - 1))
            if all(pos not in snake.body_set for snake in self.snakes):
                return pos
        return (self.grid_width // 2, self.grid_height // 2)

    def get_obstacles(self, current_snake: Snake) -> Set[Tuple[int, int]]:
        obstacles = set()
        for snake in self.snakes:
            if snake != current_snake:
                obstacles.update(snake.body_set)
        return obstacles

    def draw(self):
        self.screen.fill(COLORS['BLACK'])
        
        # Draw food
        pygame.draw.rect(self.screen, COLORS['RED'], 
                        (self.food_pos[0] * self.grid_size, 
                         self.food_pos[1] * self.grid_size, 
                         self.cell_size, self.cell_size))
        
        # Batch draw snakes
        for snake in self.snakes:
            if not snake.alive:
                for x, y in snake.body:
                    px, py = x * self.grid_size, y * self.grid_size
                    pygame.draw.rect(self.screen, COLORS['GRAY'], 
                                   (px-1, py-1, self.dead_border, self.dead_border))
            for x, y in snake.body:
                pygame.draw.rect(self.screen, snake.color,
                               (x * self.grid_size, y * self.grid_size, 
                                self.cell_size, self.cell_size))
        
        # Draw HUD
        current_time = time.time()
        elapsed = int(current_time - self.start_time)
        total_length = sum(snake.length for snake in self.snakes)
        dead_count = sum(not snake.alive for snake in self.snakes)
        
        self.screen.blit(self.font.render(f"Time: {elapsed}", True, COLORS['WHITE']), (self.screen.get_width() - 150, 10))
        self.screen.blit(self.font.render(f"Length: {total_length}", True, COLORS['WHITE']), (self.screen.get_width() - 350, 10))
        self.screen.blit(self.font.render(f"Dead: {dead_count}", True, COLORS['WHITE']), (self.screen.get_width() - 450, 10))
        
        # Draw snake status efficiently
        y_pos = 10
        for i, snake in enumerate(self.snakes):
            text = self.font.render(f"#{i+1}: {'A' if snake.alive else 'D'} L:{snake.length}", 
                                  True, snake.color)
            self.screen.blit(text, (10, y_pos))
            y_pos += 25
            
        pygame.display.flip()

    def run(self):
        while self.running:
            current_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            if current_time - self.food_spawn_time > self.food_timeout:
                self.food_pos = self.generate_food()
                self.food_spawn_time = current_time
            
            # Update all snakes
            food_eaten = False
            for snake in self.snakes:
                if snake.alive:
                    obstacles = self.get_obstacles(snake)
                    snake.move(self.food_pos, obstacles, current_time - self.start_time)
                    if snake.alive and snake.body[0] == self.food_pos and not food_eaten:
                        self.food_pos = self.generate_food()
                        self.food_spawn_time = current_time
                        food_eaten = True
            
            self.draw()
            self.clock.tick(10)  # ~100ms per frame
            
        pygame.quit()

if __name__ == "__main__":
    Game('small').run()