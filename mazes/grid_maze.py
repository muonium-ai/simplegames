import pygame
import random
import heapq

# Constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 20, 20
CELL_SIZE = WIDTH // COLS
WHITE, BLACK, BLUE, GREEN, RED = (255, 255, 255), (0, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 0)

# Directions
DIRECTIONS = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))
pygame.display.set_caption("Maze Game")
font = pygame.font.Font(None, 36)

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

# Player class
class Player:
    def __init__(self):
        self.x, self.y = 0, 0

    def move(self, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == 0:
            self.x, self.y = nx, ny

player = Player()
generate_maze(0, 0)

def draw_maze():
    screen.fill(WHITE)
    for y in range(ROWS):
        for x in range(COLS):
            color = BLACK if maze[y][x] == 1 else WHITE
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, GREEN, (0, 0, CELL_SIZE, CELL_SIZE))  # Start
    pygame.draw.rect(screen, RED, ((COLS-1) * CELL_SIZE, (ROWS-1) * CELL_SIZE, CELL_SIZE, CELL_SIZE))  # Goal
    pygame.draw.rect(screen, BLUE, (player.x * CELL_SIZE, player.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, BLACK, (WIDTH//2 - 50, HEIGHT + 10, 100, 30))
    text = font.render("Solve", True, WHITE)
    screen.blit(text, (WIDTH//2 - 25, HEIGHT + 15))

def solve_maze():
    start, goal = (0, 0), (COLS-1, ROWS-1)
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: abs(goal[0] - start[0]) + abs(goal[1] - start[1])}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        
        for dx, dy in DIRECTIONS.values():
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < COLS and 0 <= neighbor[1] < ROWS and maze[neighbor[1]][neighbor[0]] == 0:
                temp_g_score = g_score[current] + 1
                if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + abs(goal[0] - neighbor[0]) + abs(goal[1] - neighbor[1])
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

def draw_solution(path):
    for x, y in path:
        pygame.draw.rect(screen, (0, 255, 255), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def main():
    running = True
    solved_path = []
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if WIDTH//2 - 50 <= event.pos[0] <= WIDTH//2 + 50 and HEIGHT + 10 <= event.pos[1] <= HEIGHT + 40:
                    solved_path = solve_maze()
        
        draw_maze()
        if solved_path:
            draw_solution(solved_path)
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
