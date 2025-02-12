from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt
import pygame
import random
import heapq

# Constants
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 20, 20
CELL_SIZE = WIDTH // COLS
WHITE, BLACK, BLUE, GREEN, RED, CYAN, YELLOW = (255, 255, 255), (0, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0)
LIGHT_BLUE = (173, 216, 230)

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

def a_star_search(start, goal):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for direction in DIRECTIONS.values():
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= neighbor[0] < COLS and 0 <= neighbor[1] < ROWS and maze[neighbor[1]][neighbor[0]] == 0:
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []

def bfs_solve(start, goal):
    queue = [start]
    came_from = {start: None}
    while queue:
        current = queue.pop(0)
        if current == goal:
            path = []
            while current:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        for direction in DIRECTIONS.values():
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= neighbor[0] < COLS and 0 <= neighbor[1] < ROWS and maze[neighbor[1]][neighbor[0]] == 0 and neighbor not in came_from:
                queue.append(neighbor)
                came_from[neighbor] = current
    return []

def draw_maze(game_won=False, show_modal=False, ai_path=None):
    screen.fill(WHITE)
    for y in range(ROWS):
        for x in range(COLS):
            color = BLACK if maze[y][x] == 1 else WHITE
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    if ai_path:
        for x, y in ai_path:
            pygame.draw.rect(screen, LIGHT_BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
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
    if game_won or show_modal:
        modal_bg = pygame.Surface((WIDTH, HEIGHT))
        modal_bg.set_alpha(128)
        modal_bg.fill(BLACK)
        screen.blit(modal_bg, (0, 0))
        won_text = font.render("Game Won!" if game_won else "Game Paused", True, WHITE)
        screen.blit(won_text, (WIDTH//2 - 50, HEIGHT//2 - 60))
        pygame.draw.rect(screen, BLACK, (WIDTH//2 - 50, HEIGHT//2 - 20, 100, 30))
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - 50, HEIGHT//2 - 20, 100, 30))
        restart_text = font.render("Restart", True, BLACK)
        screen.blit(restart_text, (WIDTH//2 - 35, HEIGHT//2 - 15))
        pygame.draw.rect(screen, BLACK, (WIDTH//2 - 50, HEIGHT//2 + 20, 100, 30))
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - 50, HEIGHT//2 + 20, 100, 30))
        new_game_text = font.render("New Game", True, BLACK)
        screen.blit(new_game_text, (WIDTH//2 - 45, HEIGHT//2 + 25))

def main():
    running = True
    clock = pygame.time.Clock()
    move_delay = 100  # milliseconds
    move_time = 0
    acceleration = 1.1
    speed = 1
    game_won = False
    show_modal = False
    ai_path = None
    solving = False

    def reset_game(new_maze=False):
        global distance_traveled, ai_path, solving
        player.__init__()
        distance_traveled = 0
        ai_path = None
        solving = False
        if new_maze:
            global maze, visited
            maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]
            visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
            generate_maze(0, 0)
            maze[ROWS-1][COLS-2] = 0
            maze[ROWS-1][COLS-1] = 0

    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    move_time = current_time
                    speed = 1
                elif event.key == pygame.K_s and not solving:
                    ai_path = bfs_solve((0, 0), (COLS-1, ROWS-1))
                    if ai_path:
                        player.path = [(0, 0)]
                        player.x, player.y = 0, 0
                        solving = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if game_won or show_modal:
                    if WIDTH//2 - 50 <= mouse_x <= WIDTH//2 + 50 and HEIGHT//2 - 20 <= mouse_y <= HEIGHT//2 + 10:
                        reset_game()
                        game_won = False
                        show_modal = False
                    elif WIDTH//2 - 50 <= mouse_x <= WIDTH//2 + 50 and HEIGHT//2 + 20 <= mouse_y <= HEIGHT//2 + 50:
                        reset_game(new_maze=True)
                        game_won = False
                        show_modal = False
                elif WIDTH//2 - 50 <= mouse_x <= WIDTH//2 + 50 and HEIGHT + 10 <= mouse_y <= HEIGHT + 40:
                    if not solving:
                        ai_path = bfs_solve((0, 0), (COLS-1, ROWS-1))
                        if ai_path:
                            player.path = [(0, 0)]
                            player.x, player.y = 0, 0
                            solving = True
                    else:
                        show_modal = True

        if not game_won and not show_modal:
            if solving and ai_path:
                if player.path[-1] != (COLS-1, ROWS-1):
                    next_step = ai_path[len(player.path)]
                    player.move(next_step[0] - player.x, next_step[1] - player.y)
                else:
                    solving = False
                    game_won = True
            else:
                keys = pygame.key.get_pressed()
                if current_time - move_time >= move_delay / speed:
                    if keys[pygame.K_UP]:
                        player.move(0, -1)
                        move_time = current_time
                        speed *= acceleration
                    elif keys[pygame.K_DOWN]:
                        player.move(0, 1)
                        move_time = current_time
                        speed *= acceleration
                    elif keys[pygame.K_LEFT]:
                        player.move(-1, 0)
                        move_time = current_time
                        speed *= acceleration
                    elif keys[pygame.K_RIGHT]:
                        player.move(1, 0)
                        move_time = current_time
                        speed *= acceleration

                if player.x == COLS-1 and player.y == ROWS-1:
                    game_won = True

        draw_maze(game_won, show_modal, ai_path)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
