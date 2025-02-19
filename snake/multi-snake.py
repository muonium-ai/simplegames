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
    def get_safe_directions(snake_head: tuple, obstacles: List, next_positions: List[tuple]) -> List[Direction]:
        """Return list of safe directions that won't result in immediate collision"""
        safe_directions = []
        
        for direction in Direction:
            new_pos = (
                (snake_head[0] + direction.value[0]) % GRID_WIDTH,
                (snake_head[1] + direction.value[1]) % GRID_HEIGHT
            )
            if new_pos not in obstacles and new_pos not in next_positions:
                safe_directions.append(direction)
                
        return safe_directions

    @staticmethod
    def predict_next_positions(snakes: List['Snake']) -> List[tuple]:
        """Predict likely next positions of all snake heads"""
        next_positions = []
        for snake in snakes:
            if snake.alive:
                head = snake.body[0]
                # Predict based on current direction
                next_pos = (
                    (head[0] + snake.direction.value[0]) % GRID_WIDTH,
                    (head[1] + snake.direction.value[1]) % GRID_HEIGHT
                )
                next_positions.append(next_pos)
        return next_positions

    @staticmethod
    def basic_pathfinding(snake_head: tuple, food_pos: tuple, obstacles: List, 
                         all_snakes: List['Snake']=None) -> Direction:
        x, y = snake_head
        food_x, food_y = food_pos
        
        # Get safe directions
        next_positions = AIStrategy.predict_next_positions(all_snakes) if all_snakes else []
        safe_directions = AIStrategy.get_safe_directions(snake_head, obstacles, next_positions)
        
        if not safe_directions:
            return Direction.RIGHT  # Default direction if no safe moves
            
        # Calculate distances for each safe direction
        direction_scores = []
        for direction in safe_directions:
            new_x = (x + direction.value[0]) % GRID_WIDTH
            new_y = (y + direction.value[1]) % GRID_HEIGHT
            
            # Calculate distance to food
            distance = abs(food_x - new_x) + abs(food_y - new_y)
            
            # Calculate distance to nearest obstacle
            min_obstacle_distance = float('inf')
            for obs in obstacles:
                obs_distance = abs(obs[0] - new_x) + abs(obs[1] - new_y)
                min_obstacle_distance = min(min_obstacle_distance, obs_distance)
            
            # Score = food proximity - obstacle proximity (weighted)
            score = -distance + 0.5 * min_obstacle_distance
            direction_scores.append((score, direction))
        
        # Choose direction with highest score
        return max(direction_scores, key=lambda x: x[0])[1]

class Snake:
    def __init__(self, start_pos: tuple, color: tuple, ai_strategy):
        self.body = [start_pos]
        self.color = color
        self.direction = Direction.RIGHT
        self.ai_strategy = ai_strategy
        self.alive = True
        self.length = 1
        self.survival_time = 0
        self.all_snakes = []  # Will be set by Game class
        self.last_move_time = time.time()
        self.stuck_timeout = 2.0  # Seconds before considering snake stuck

    def move(self, food_pos: tuple, obstacles: List):
        if not self.alive:
            return

        current_time = time.time()
        
        # Check if snake is stuck
        if current_time - self.last_move_time > self.stuck_timeout:
            self.alive = False
            return

        # Get new direction from AI with additional snake information
        old_head = self.body[0]
        self.direction = self.ai_strategy(self.body[0], food_pos, obstacles, self.all_snakes)
        
        # Calculate new head position
        new_head = (
            (self.body[0][0] + self.direction.value[0]) % GRID_WIDTH,
            (self.body[0][1] + self.direction.value[1]) % GRID_HEIGHT
        )

        # Check collision with self or other snakes
        if new_head in obstacles or new_head in self.body:
            self.alive = False
            return

        self.body.insert(0, new_head)
        if new_head != food_pos:
            self.body.pop()
        else:
            self.length += 1

        # Update last move time only if position actually changed
        if new_head != old_head:
            self.last_move_time = current_time

class Menu:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        
        # Position buttons side by side
        button_width = 150
        button_height = 50
        button_spacing = 20
        total_width = (button_width * 2) + button_spacing
        start_x = WINDOW_WIDTH//2 - total_width//2
        
        self.buttons = {
            'start': pygame.Rect(start_x, 200, button_width, button_height),
            'quit': pygame.Rect(start_x + button_width + button_spacing, 200, button_width, button_height)
        }

    def draw(self, game_over=False, scores=None):
        self.screen.fill(BLACK)
        
        # Title
        title = "Game Over!" if game_over else "Multi-Snake Game"
        title_text = self.font.render(title, True, WHITE)
        title_rect = title_text.get_rect(centerx=WINDOW_WIDTH//2, y=100)
        self.screen.blit(title_text, title_rect)

        # Draw buttons with better styling
        for text, rect in self.buttons.items():
            pygame.draw.rect(self.screen, WHITE, rect, 2)
            button_text = self.font.render(text.title(), True, WHITE)
            text_rect = button_text.get_rect(center=rect.center)
            self.screen.blit(button_text, text_rect)

        # Show scores in a box below buttons
        if scores:
            score_box = pygame.Rect(WINDOW_WIDTH//4, 300, WINDOW_WIDTH//2, 200)
            pygame.draw.rect(self.screen, WHITE, score_box, 2)
            
            # Draw "Scores" header
            header = self.font.render("Scores", True, WHITE)
            header_rect = header.get_rect(centerx=WINDOW_WIDTH//2, y=310)
            self.screen.blit(header, header_rect)
            
            # Draw scores
            y_pos = 350
            for i, score in enumerate(scores):
                text = f"#{i+1}: Length={score[0]}, Time={int(score[1])}s"
                score_text = self.font.render(text, True, SNAKE_COLORS[i % len(SNAKE_COLORS)])
                text_rect = score_text.get_rect(centerx=WINDOW_WIDTH//2, y=y_pos)
                self.screen.blit(score_text, text_rect)
                y_pos += 30

        pygame.display.flip()

    def handle_click(self, pos):
        """Check if any button was clicked and return the button name"""
        for button_name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return button_name
        return None

class Game:
    def __init__(self, num_snakes=4):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Multi-Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.menu = Menu(self.screen, self.font)
        self.num_snakes = num_snakes
        self.GRAY = (128, 128, 128)  # Add gray color for dead snake outline
        self.initialize_game()

    def initialize_game(self):
        # Initialize snakes
        self.snakes = []
        for i in range(self.num_snakes):
            start_pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            new_snake = Snake(start_pos, SNAKE_COLORS[i], AIStrategy.basic_pathfinding)
            self.snakes.append(new_snake)
        
        # Set all_snakes reference for each snake
        for snake in self.snakes:
            snake.all_snakes = self.snakes
        
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
        
        # Draw snakes with outline for dead ones
        for snake in self.snakes:
            for segment in snake.body:
                x = segment[0]*GRID_SIZE
                y = segment[1]*GRID_SIZE
                width = GRID_SIZE-2
                
                if not snake.alive:
                    # Draw gray outline for dead snake
                    pygame.draw.rect(self.screen, self.GRAY,
                                   (x-1, y-1, width+2, width+2))
                
                # Draw snake segment
                pygame.draw.rect(self.screen, snake.color,
                               (x, y, width, width))
        
        # Draw timer and debug info
        elapsed_time = int(time.time() - self.start_time)
        timer_text = self.font.render(f"Time: {elapsed_time}", True, WHITE)
        self.screen.blit(timer_text, (WINDOW_WIDTH - 150, 10))
        
        # Draw snake status
        y_pos = 10
        for i, snake in enumerate(self.snakes):
            status = "Alive" if snake.alive else "Dead"
            status_text = self.font.render(f"Snake {i+1}: {status} L:{snake.length}", True, snake.color)
            self.screen.blit(status_text, (10, y_pos))
            y_pos += 25
        
        pygame.display.flip()

    def run(self):
        running = True
        game_state = "menu"  # States: menu, playing, game_over

        while running:
            if game_state == "menu":
                self.menu.draw()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        action = self.menu.handle_click(event.pos)
                        if action == "start":
                            game_state = "playing"
                            self.initialize_game()
                        elif action == "quit":
                            running = False

            elif game_state == "playing":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                # Update snake positions
                for snake in self.snakes:
                    if snake.alive:  # Only move alive snakes
                        obstacles = self.get_all_obstacles(snake)
                        snake.move(self.food_pos, obstacles)
                        snake.survival_time = time.time() - self.start_time

                # Check if food is eaten by any alive snake
                for snake in self.snakes:
                    if snake.alive and snake.body[0] == self.food_pos:
                        self.food_pos = self.generate_food()
                        break

                # Check game over condition
                alive_snakes = [snake for snake in self.snakes if snake.alive]
                if len(alive_snakes) == 0:
                    game_state = "game_over"
                
                self.draw()

            elif game_state == "game_over":
                scores = [(snake.length, snake.survival_time) 
                         for snake in sorted(self.snakes, 
                                          key=lambda x: (x.length, x.survival_time),
                                          reverse=True)]
                self.menu.draw(game_over=True, scores=scores)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        action = self.menu.handle_click(event.pos)
                        if action == "start":
                            game_state = "playing"
                            self.initialize_game()
                        elif action == "quit":
                            running = False

            self.clock.tick(10)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
