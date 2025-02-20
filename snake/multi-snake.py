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
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
SNAKE_COLORS = [
    (0, 255, 0),     # Green
    (0, 0, 255),     # Blue
    (255, 165, 0),   # Orange
    (128, 0, 128),   # Purple
    (255, 0, 255),   # Magenta
    (0, 255, 255),   # Cyan
    (255, 255, 0),   # Yellow
    (165, 42, 42),   # Brown
    (219, 112, 147), # Pink
    (0, 128, 0)      # Dark Green
]

# Window size configurations
SMALL_WINDOW = {
    'width': 800,
    'height': 600,
    'num_snakes': 4,
    'grid_size': 20,
}

LARGE_WINDOW = {
    'width': 1920,
    'height': 1080,
    'num_snakes': 10,
    'grid_size': 20,
}

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class AIStrategy:
    @staticmethod
    def basic_pathfinding(snake_head: tuple, food_pos: tuple, obstacles: List, 
                         all_snakes: List['Snake']=None) -> Direction:
        """Simplified pathfinding that prefers clear paths"""
        if not all_snakes:
            return Direction.RIGHT
            
        # Find current snake from all_snakes
        current_snake = next((s for s in all_snakes if s.body[0] == snake_head), None)
        if not current_snake:
            return Direction.RIGHT
            
        # Get grid dimensions from snake instance
        grid_width = current_snake.grid_width
        grid_height = current_snake.grid_height
        
        x, y = snake_head
        food_x, food_y = food_pos

        # Get all possible moves
        possible_moves = []
        for direction in Direction:
            new_x = x + direction.value[0]
            new_y = y + direction.value[1]
            
            # Skip if would hit wall
            if new_x < 0 or new_x >= grid_width or new_y < 0 or new_y >= grid_height:
                continue
                
            new_pos = (new_x, new_y)
            
            # Skip if would hit obstacle
            if new_pos in obstacles:
                continue
                
            # Skip if would hit own body (except tail)
            if new_pos in current_snake.body[:-1]:
                continue
            
            # Calculate score for this move
            food_dist = abs(food_x - new_x) + abs(food_y - new_y)
            
            # Count free spaces in this direction
            free_spaces = 0
            check_x, check_y = new_x, new_y
            for _ in range(3):  # Look ahead 3 spaces
                if (0 <= check_x < grid_width and 
                    0 <= check_y < grid_height and 
                    (check_x, check_y) not in obstacles):
                    free_spaces += 1
                check_x += direction.value[0]
                check_y += direction.value[1]
            
            score = free_spaces * 10 - food_dist
            possible_moves.append((score, direction))
        
        if not possible_moves:
            return Direction.RIGHT
            
        # Choose direction with highest score
        return max(possible_moves, key=lambda x: x[0])[1]

class Snake:
    def __init__(self, start_pos: tuple, color: tuple, ai_strategy):
        self.body = [start_pos]
        self.color = color
        self.direction = Direction.RIGHT
        self.ai_strategy = ai_strategy
        self.alive = True
        self.length = 1
        self.survival_time = 0
        self.all_snakes = []
        self.last_move_time = time.time()
        self.stuck_timeout = 2.0
        self.last_positions = []
        self.position_check_length = 5  # Track last 5 positions
        self.grid_width = None  # Will be set by Game
        self.grid_height = None  # Will be set by Game

    def is_stuck(self) -> bool:
        """Check if snake is stuck in a small area"""
        if len(self.last_positions) < self.position_check_length:
            return False
        unique_positions = set(self.last_positions)
        return len(unique_positions) <= 2

    def move(self, food_pos: tuple, obstacles: List):
        if not self.alive:
            return

        current_time = time.time()
        if current_time - self.last_move_time > self.stuck_timeout:
            self.alive = False
            return

        old_head = self.body[0]
        
        # Get new direction from AI
        new_direction = self.ai_strategy(self.body[0], food_pos, obstacles, self.all_snakes)
        self.direction = new_direction
        
        # Calculate new head position
        new_x = self.body[0][0] + self.direction.value[0]
        new_y = self.body[0][1] + self.direction.value[1]
        
        # Die if hitting wall (using instance grid bounds)
        if new_x < 0 or new_x >= self.grid_width or new_y < 0 or new_y >= self.grid_height:
            self.alive = False
            return
            
        new_head = (new_x, new_y)
        
        # Die if hitting obstacle
        if new_head in obstacles:
            self.alive = False
            return
            
        # Die if hitting self (except tail)
        if new_head in self.body[:-1]:
            self.alive = False
            return

        # Update body
        self.body.insert(0, new_head)
        if new_head != food_pos:
            self.body.pop()
        else:
            self.length += 1

        # Track positions for stuck detection
        self.last_positions.append(new_head)
        if len(self.last_positions) > self.position_check_length:
            self.last_positions.pop(0)

        # Update last move time
        if new_head != old_head:
            self.last_move_time = current_time

class Menu:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        
        # Position buttons in a grid
        button_width = 200
        button_height = 50
        button_spacing = 20
        
        # Calculate positions for all buttons
        center_x = SMALL_WINDOW['width'] // 2  # Use small window size for initial menu
        self.buttons = {
            'start_small': pygame.Rect(center_x - button_width - button_spacing, 200, button_width, button_height),
            'start_large': pygame.Rect(center_x + button_spacing, 200, button_width, button_height),
            'quit': pygame.Rect(center_x - button_width//2, 300, button_width, button_height)
        }

    def draw(self, game_over=False, scores=None):
        self.screen.fill(BLACK)
        
        # Title
        title = "Game Over!" if game_over else "Multi-Snake Game"
        title_text = self.font.render(title, True, WHITE)
        title_rect = title_text.get_rect(centerx=self.screen.get_width()//2, y=100)
        self.screen.blit(title_text, title_rect)

        # Draw buttons with better styling and descriptive text
        button_texts = {
            'start_small': "Small (4 Snakes)",
            'start_large': "Large (10 Snakes)",
            'quit': "Quit"
        }

        for button_name, rect in self.buttons.items():
            pygame.draw.rect(self.screen, WHITE, rect, 2)
            text = self.font.render(button_texts[button_name], True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # Show scores in a box below buttons
        if scores:
            score_box = pygame.Rect(self.screen.get_width()//4, 300, self.screen.get_width()//2, 200)
            pygame.draw.rect(self.screen, WHITE, score_box, 2)
            
            # Draw "Scores" header
            header = self.font.render("Scores", True, WHITE)
            header_rect = header.get_rect(centerx=self.screen.get_width()//2, y=310)
            self.screen.blit(header, header_rect)
            
            # Draw scores
            y_pos = 350
            for i, score in enumerate(scores):
                text = f"#{i+1}: Length={score[0]}, Time={int(score[1])}s"
                score_text = self.font.render(text, True, SNAKE_COLORS[i % len(SNAKE_COLORS)])
                text_rect = score_text.get_rect(centerx=self.screen.get_width()//2, y=y_pos)
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
    def __init__(self, window_mode='small'):
        # Set window configuration based on mode
        config = LARGE_WINDOW if window_mode == 'large' else SMALL_WINDOW
        self.WINDOW_WIDTH = config['width']
        self.WINDOW_HEIGHT = config['height']
        self.num_snakes = config['num_snakes']
        self.GRID_SIZE = config['grid_size']
        
        # Calculate grid dimensions based on window size
        self.GRID_WIDTH = self.WINDOW_WIDTH // self.GRID_SIZE
        self.GRID_HEIGHT = self.WINDOW_HEIGHT // self.GRID_SIZE
        
        # Initialize display
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption(f"Multi-Snake Game - {window_mode.title()}")
        
        # Initialize rest of the game
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.menu = Menu(self.screen, self.font)
        self.GRAY = (128, 128, 128)
        self.food_spawn_time = 0
        self.food_timeout = 15.0
        self.food_wall_margin = 2
        self.initialize_game()

    def is_position_safe(self, pos: tuple) -> bool:
        """Check if position is safe for food placement"""
        x, y = pos
        # Check wall margins
        if (x < self.food_wall_margin or 
            x >= self.GRID_WIDTH - self.food_wall_margin or 
            y < self.food_wall_margin or 
            y >= self.GRID_HEIGHT - self.food_wall_margin):
            return False
            
        # Check if any snake is at this position
        return not any(pos in snake.body for snake in self.snakes)

    def initialize_game(self):
        # Initialize snakes
        self.snakes = []
        for i in range(self.num_snakes):
            start_pos = (random.randint(0, self.GRID_WIDTH-1), random.randint(0, self.GRID_HEIGHT-1))
            new_snake = Snake(start_pos, SNAKE_COLORS[i], AIStrategy.basic_pathfinding)
            self.snakes.append(new_snake)
        
        # Set all_snakes reference for each snake
        for snake in self.snakes:
            snake.all_snakes = self.snakes
            snake.grid_width = self.GRID_WIDTH
            snake.grid_height = self.GRID_HEIGHT
        
        self.food_pos = self.generate_food()
        self.start_time = time.time()

    def generate_food(self) -> tuple:
        """Generate food in safe location away from walls"""
        attempts = 100  # Prevent infinite loop
        while attempts > 0:
            x = random.randint(self.food_wall_margin, self.GRID_WIDTH - self.food_wall_margin - 1)
            y = random.randint(self.food_wall_margin, self.GRID_HEIGHT - self.food_wall_margin - 1)
            pos = (x, y)
            
            if self.is_position_safe(pos):
                self.food_spawn_time = time.time()
                return pos
                
            attempts -= 1
            
        # If no safe spot found, pick center-ish location
        return (self.GRID_WIDTH // 2, self.GRID_HEIGHT // 2)

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
                        (self.food_pos[0]*self.GRID_SIZE, self.food_pos[1]*self.GRID_SIZE, 
                         self.GRID_SIZE-2, self.GRID_SIZE-2))
        
        # Draw snakes with outline for dead ones
        for snake in self.snakes:
            for segment in snake.body:
                x = segment[0]*self.GRID_SIZE
                y = segment[1]*self.GRID_SIZE
                width = self.GRID_SIZE-2
                
                if not snake.alive:
                    # Draw gray outline for dead snake
                    pygame.draw.rect(self.screen, self.GRAY,
                                   (x-1, y-1, width+2, width+2))
                
                # Draw snake segment
                pygame.draw.rect(self.screen, snake.color,
                               (x, y, width, width))
        
        # Draw timer, total length, and dead count
        elapsed_time = int(time.time() - self.start_time)
        total_length = sum(snake.length for snake in self.snakes)
        dead_count = sum(1 for snake in self.snakes if not snake.alive)
        
        timer_text = self.font.render(f"Time: {elapsed_time}", True, WHITE)
        length_text = self.font.render(f"Total Length: {total_length}", True, WHITE)
        dead_text = self.font.render(f"Dead: {dead_count}", True, WHITE)
        
        self.screen.blit(timer_text, (self.WINDOW_WIDTH - 150, 10))
        self.screen.blit(length_text, (self.WINDOW_WIDTH - 350, 10))
        self.screen.blit(dead_text, (self.WINDOW_WIDTH - 450, 10))
        
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
                        if action == "start_small":
                            self.__init__('small')
                            game_state = "playing"
                        elif action == "start_large":
                            self.__init__('large')
                            game_state = "playing"
                        elif action == "quit":
                            running = False

            elif game_state == "playing":
                current_time = time.time()
                
                # Check if food needs to be relocated
                if current_time - self.food_spawn_time > self.food_timeout:
                    self.food_pos = self.generate_food()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                # Update snake positions
                for snake in self.snakes:
                    if snake.alive:  # Only move alive snakes
                        obstacles = self.get_all_obstacles(snake)
                        snake.move(self.food_pos, obstacles)
                        snake.survival_time = current_time - self.start_time

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
                        if action == "start_small":
                            self.__init__('small')
                            game_state = "playing"
                        elif action == "start_large":
                            self.__init__('large')
                            game_state = "playing"
                        elif action == "quit":
                            running = False

            self.clock.tick(10)

if __name__ == "__main__":
    game = Game('small')  # Start with small window for menu
    game.run()
    pygame.quit()
