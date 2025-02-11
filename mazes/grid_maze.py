import pygame
import random
import heapq

# Constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 20, 20
CELL_SIZE = WIDTH // COLS
WHITE, BLACK, BLUE, GREEN, RED, CYAN, YELLOW = (255, 255, 255), (0, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0)

# Directions
DIRECTIONS = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))
pygame.display.set_caption("Maze Game")
font = pygame.font.Font(None, 36)

distance_traveled = 0

# Generate Maze
maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]
visited = [[False for _ in range(COLS)] for _ in range(ROWS)]

def generate_maze(x, y):
    visited[y][x] = True
    maze[y][x] = 0
    directions = list(DIRECTIONS.values())
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx * 2, y + dy * 2
        if 0 <= nx < COLS and 0 <= ny < ROWS and not visited[ny][nx]:
            maze[y + dy][x + dx] = 0
            generate_maze(nx, ny)

generate_maze(0, 0)
maze[ROWS-1][COLS-2] = 0  # Ensure the end point is open and connected to the path
maze[ROWS-1][COLS-1] = 0

# Player class
class Player:
    def __init__(self):
        self.x, self.y = 0, 0
        self.path = [(0, 0)]

    def move(self, dx, dy):
        global distance_traveled
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == 0:
            self.x, self.y = nx, ny
            self.path.append((nx, ny))
            distance_traveled += 1

player = Player()

def draw_maze():
    screen.fill(WHITE)
    for y in range(ROWS):
        for x in range(COLS):
            color = BLACK if maze[y][x] == 1 else WHITE
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for x, y in player.path:
        pygame.draw.rect(screen, YELLOW, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, GREEN, (0, 0, CELL_SIZE, CELL_SIZE))  # Start
    pygame.draw.rect(screen, RED, ((COLS-1) * CELL_SIZE, (ROWS-1) * CELL_SIZE, CELL_SIZE, CELL_SIZE))  # Goal
    pygame.draw.rect(screen, BLUE, (player.x * CELL_SIZE, player.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, BLACK, (WIDTH//2 - 50, HEIGHT + 10, 100, 30))
    text = font.render("Solve", True, WHITE)
    screen.blit(text, (WIDTH//2 - 25, HEIGHT + 15))
    distance_text = font.render(f"Distance: {distance_traveled}", True, BLACK)
    screen.blit(distance_text, (10, HEIGHT + 15))

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move(0, -1)
                elif event.key == pygame.K_DOWN:
                    player.move(0, 1)
                elif event.key == pygame.K_LEFT:
                    player.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    player.move(1, 0)
        
        draw_maze()
        pygame.display.flip()
        
        if player.x == COLS-1 and player.y == ROWS-1:
            print("You reached the goal!")
            running = False
    
    pygame.quit()

if __name__ == "__main__":
    main()
