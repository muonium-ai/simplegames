from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Window dimensions
WINDOW_SIZE = (800, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Multi-Snake Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Snake properties
SNAKE_SIZE = 20
SPEED = 15

# Snake class
class Snake:
    def __init__(self, color):
        self.length = 1
        self.positions = [((WINDOW_SIZE[0] // 2), (WINDOW_SIZE[1] // 2))]
        self.direction = random.choice([(0, -SNAKE_SIZE), (0, SNAKE_SIZE), (-SNAKE_SIZE, 0), (SNAKE_SIZE, 0)])
        self.color = color

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        else:
            self.direction = point

    def move(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = (((cur[0] + x) % WINDOW_SIZE[0]), (cur[1] + y) % WINDOW_SIZE[1])
        
        if len(self.positions) > 2 and new in self.positions[2:]:
            self.reset()
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()

    def reset(self):
        self.length = 1
        self.positions = [((WINDOW_SIZE[0] // 2), (WINDOW_SIZE[1] // 2))]
        self.direction = random.choice([(0, -SNAKE_SIZE), (0, SNAKE_SIZE), (-SNAKE_SIZE, 0), (SNAKE_SIZE, 0)])

    def draw(self, surface):
        for p in self.positions:
            pygame.draw.rect(surface, self.color, (p[0], p[1], SNAKE_SIZE, SNAKE_SIZE))

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != (0, SNAKE_SIZE):
                    self.direction = (0, -SNAKE_SIZE)
                elif event.key == pygame.K_DOWN and self.direction != (0, -SNAKE_SIZE):
                    self.direction = (0, SNAKE_SIZE)
                elif event.key == pygame.K_LEFT and self.direction != (SNAKE_SIZE, 0):
                    self.direction = (-SNAKE_SIZE, 0)
                elif event.key == pygame.K_RIGHT and self.direction != (-SNAKE_SIZE, 0):
                    self.direction = (SNAKE_SIZE, 0)

# Function to place food
def place_food():
    return (random.randint(0, (WINDOW_SIZE[0] - SNAKE_SIZE) // SNAKE_SIZE) * SNAKE_SIZE,
            random.randint(0, (WINDOW_SIZE[1] - SNAKE_SIZE) // SNAKE_SIZE) * SNAKE_SIZE)

# Main game loop
def main(snake_count=3):
    snakes = [Snake(color) for color in [RED, GREEN, BLUE][:snake_count]]
    food = place_food()
    
    clock = pygame.time.Clock()
    
    while True:
        screen.fill(BLACK)
        
        for snake in snakes:
            snake.move()
            snake.handle_keys()
            snake.draw(screen)
            
            # Check if snake has eaten the food
            if snake.get_head_position() == food:
                snake.length += 1
                food = place_food()

        # Draw food
        pygame.draw.rect(screen, WHITE, pygame.Rect(food[0], food[1], SNAKE_SIZE, SNAKE_SIZE))

        pygame.display.update()
        clock.tick(SPEED)

if __name__ == "__main__":
    main()