from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import random
import heapq
import math

# Constants
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 15
HEX_SIZE = 25  # Size of hexagon (radius)
WHITE, BLACK, BLUE, GREEN, RED, YELLOW, LIGHT_BLUE = (255, 255, 255), (0, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (173, 216, 230)

# Hexagonal directions (axial coordinates)
DIRECTIONS = [
    (1, 0), (1, -1), (0, -1),
    (-1, 0), (-1, 1), (0, 1)
]

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))
pygame.display.set_caption("Hexagonal Maze")
font = pygame.font.Font(None, 36)

class HexGrid:
    def __init__(self, size):
        self.size = size
        self.grid = {}
        self.generate_grid()

    def generate_grid(self):
        for q in range(-self.size, self.size + 1):
            for r in range(-self.size, self.size + 1):
                if abs(q + r) <= self.size:
                    self.grid[(q, r)] = 1  # 1 represents wall

    def hex_to_pixel(self, q, r):
        x = HEX_SIZE * (3/2 * q)
        y = HEX_SIZE * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
        return (x + WIDTH//2, y + HEIGHT//2)

    def draw_hexagon(self, q, r, color):
        center = self.hex_to_pixel(q, r)
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            x = center[0] + HEX_SIZE * math.cos(angle_rad)
            y = center[1] + HEX_SIZE * math.sin(angle_rad)
            points.append((x, y))
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, BLACK, points, 1)

class Player:
    def __init__(self, hex_grid):
        self.q = -hex_grid.size
        self.r = hex_grid.size
        self.path = [(self.q, self.r)]
        self.hex_grid = hex_grid
        self.moves = 0  # Add move counter

    def move(self, dq, dr):
        new_q = self.q + dq
        new_r = self.r + dr
        if (new_q, new_r) in self.hex_grid.grid and self.hex_grid.grid[(new_q, new_r)] == 0:
            self.q = new_q
            self.r = new_r
            self.path.append((self.q, self.r))
            self.moves += 1  # Increment move counter
            return True
        return False

def generate_maze(hex_grid):
    start = (-hex_grid.size, hex_grid.size)
    end = (hex_grid.size, -hex_grid.size)
    stack = [start]
    visited = {start}
    hex_grid.grid[start] = 0
    hex_grid.grid[end] = 0

    while stack:
        current = stack[-1]
        neighbors = []
        for dq, dr in DIRECTIONS:
            next_q = current[0] + dq * 2
            next_r = current[1] + dr * 2
            if (next_q, next_r) in hex_grid.grid and (next_q, next_r) not in visited:
                neighbors.append((next_q, next_r))

        if neighbors:
            next_cell = random.choice(neighbors)
            mid_q = (current[0] + next_cell[0]) // 2
            mid_r = (current[1] + next_cell[1]) // 2
            hex_grid.grid[(mid_q, mid_r)] = 0
            hex_grid.grid[next_cell] = 0
            stack.append(next_cell)
            visited.add(next_cell)
        else:
            stack.pop()

class ControlGuide:
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y
        self.hex_size = 30
        self.button_size = 40
        # Rearranged sequence: D,S,E,W,A,Q with proper opposites
        self.directions = {
            'D': (0, -1, 270),      # Top
            'S': (1, -1, 330),      # Top-right
            'E': (1, 0, 30),        # Right
            'W': (0, 1, 90),        # Bottom (opposite to D)
            'A': (-1, 1, 150),      # Bottom-left (opposite to S)
            'Q': (-1, 0, 210)       # Left (opposite to E)
        }

    def draw_arrow(self, x, y, angle):
        # Draw arrow pointing in specified angle
        length = self.hex_size * 0.7
        end_x = x + length * math.cos(math.radians(angle))
        end_y = y + length * math.sin(math.radians(angle))
        
        # Arrow head
        arrow_size = 10
        angle_rad = math.radians(angle)
        pygame.draw.line(screen, BLACK, (x, y), (end_x, end_y), 2)
        pygame.draw.polygon(screen, BLACK, [
            (end_x, end_y),
            (end_x - arrow_size * math.cos(angle_rad - math.pi/6),
             end_y - arrow_size * math.sin(angle_rad - math.pi/6)),
            (end_x - arrow_size * math.cos(angle_rad + math.pi/6),
             end_y - arrow_size * math.sin(angle_rad + math.pi/6))
        ])

    def draw(self):
        # Draw center hexagon
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            x = self.center_x + self.hex_size * math.cos(angle_rad)
            y = self.center_y + self.hex_size * math.sin(angle_rad)
            points.append((x, y))
        pygame.draw.polygon(screen, WHITE, points)
        pygame.draw.polygon(screen, BLACK, points, 2)

        # Draw arrows and buttons
        for key, (dq, dr, angle) in self.directions.items():
            # Draw arrow
            self.draw_arrow(self.center_x, self.center_y, angle)
            
            # Calculate button position
            button_x = self.center_x + (self.hex_size + 20) * math.cos(math.radians(angle))
            button_y = self.center_y + (self.hex_size + 20) * math.sin(math.radians(angle))
            
            # Draw button
            button_rect = pygame.Rect(
                button_x - self.button_size//2,
                button_y - self.button_size//2,
                self.button_size,
                self.button_size
            )
            pygame.draw.rect(screen, WHITE, button_rect)
            pygame.draw.rect(screen, BLACK, button_rect, 2)
            
            # Draw key text
            text = font.render(key, True, BLACK)
            text_rect = text.get_rect(center=(button_x, button_y))
            screen.blit(text, text_rect)

    def check_click(self, pos):
        x, y = pos
        for key, (dq, dr, angle) in self.directions.items():
            button_x = self.center_x + (self.hex_size + 20) * math.cos(math.radians(angle))
            button_y = self.center_y + (self.hex_size + 20) * math.sin(math.radians(angle))
            button_rect = pygame.Rect(
                button_x - self.button_size//2,
                button_y - self.button_size//2,
                self.button_size,
                self.button_size
            )
            if button_rect.collidepoint(x, y):
                return (dq, dr)
        return None

def bfs_solve(hex_grid, start, goal):
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
            return path  # Returns complete path from start to goal
        
        # Explore neighbors using hexagonal directions
        for dq, dr in DIRECTIONS:
            neighbor = (current[0] + dq, current[1] + dr)
            if neighbor in hex_grid.grid and hex_grid.grid[neighbor] == 0 and neighbor not in came_from:
                queue.append(neighbor)
                came_from[neighbor] = current                
    return []

def draw_maze(hex_grid, player, game_won=False, show_modal=False, solution_path=None):
    # Draw maze background first
    screen.fill(WHITE)

    # Draw maze cells
    for (q, r), value in hex_grid.grid.items():
        color = WHITE if value == 0 else BLACK
        hex_grid.draw_hexagon(q, r, color)

    # Draw solution path if exists
    if solution_path:
        for q, r in solution_path:
            if (q, r) not in player.path:  # Only show future path
                hex_grid.draw_hexagon(q, r, LIGHT_BLUE)

    # Draw player path
    for q, r in player.path:
        hex_grid.draw_hexagon(q, r, YELLOW)

    # Draw start and end points
    hex_grid.draw_hexagon(-hex_grid.size, hex_grid.size, GREEN)
    hex_grid.draw_hexagon(hex_grid.size, -hex_grid.size, RED)

    # Draw player current position
    hex_grid.draw_hexagon(player.q, player.r, BLUE)

    # Draw solve button with black background
    solve_button = pygame.Rect(WIDTH//2 - 70, HEIGHT + 10, 140, 30)
    pygame.draw.rect(screen, BLACK, solve_button)
    pygame.draw.rect(screen, WHITE, solve_button, 2)
    solve_text = font.render("Solve", True, WHITE)
    text_rect = solve_text.get_rect(center=(WIDTH//2, HEIGHT + 25))
    screen.blit(solve_text, text_rect)

    # Draw move counter
    moves_text = font.render(f"Moves: {player.moves}", True, BLACK)
    screen.blit(moves_text, (10, HEIGHT + 15))

    # Draw victory screen
    if game_won:
        modal_bg = pygame.Surface((WIDTH, HEIGHT + 50))
        modal_bg.set_alpha(128)
        modal_bg.fill(BLACK)
        screen.blit(modal_bg, (0, 0))

        won_text = font.render("Game Won!", True, WHITE)
        text_rect = won_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
        screen.blit(won_text, text_rect)
        
        # Restart button
        restart_rect = pygame.Rect(WIDTH//2 - 70, HEIGHT//2 - 20, 140, 40)
        pygame.draw.rect(screen, WHITE, restart_rect)
        restart_text = font.render("Restart", True, BLACK)
        text_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(restart_text, text_rect)
        
        # New Game button
        new_game_rect = pygame.Rect(WIDTH//2 - 70, HEIGHT//2 + 30, 140, 40)
        pygame.draw.rect(screen, WHITE, new_game_rect)
        new_game_text = font.render("New Game", True, BLACK)
        text_rect = new_game_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        screen.blit(new_game_text, text_rect)

def reset_game(hex_grid, new_maze=False):
    if new_maze:
        hex_grid = HexGrid(7)
        generate_maze(hex_grid)
    return Player(hex_grid), hex_grid

def main():
    hex_grid = HexGrid(7)
    generate_maze(hex_grid)
    player = Player(hex_grid)
    control_guide = ControlGuide(WIDTH - 150, HEIGHT - 150)
    running = True
    clock = pygame.time.Clock()
    game_won = False
    solution_path = None
    solving = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if game_won:  # Handle victory screen buttons
                    if WIDTH//2 - 70 <= mouse_x <= WIDTH//2 + 70:
                        if HEIGHT//2 - 20 <= mouse_y <= HEIGHT//2 + 20:  # Restart button
                            player, hex_grid = reset_game(hex_grid)
                            game_won = False
                            solution_path = None
                            solving = False
                        elif HEIGHT//2 + 30 <= mouse_y <= HEIGHT//2 + 70:  # New Game button
                            player, hex_grid = reset_game(hex_grid, True)
                            game_won = False
                            solution_path = None
                            solving = False
                # Handle solve button click
                elif HEIGHT + 10 <= mouse_y <= HEIGHT + 40 and WIDTH//2 - 70 <= mouse_x <= WIDTH//2 + 70:
                    if not solving:
                        start = (player.q, player.r)
                        goal = (hex_grid.size, -hex_grid.size)
                        solution_path = bfs_solve(hex_grid, start, goal)
                        if solution_path:
                            solving = True
                            player.path = [(player.q, player.r)]
                elif not solving:  # Handle movement clicks
                    movement = control_guide.check_click(event.pos)
                    if movement:
                        player.move(*movement)
                        if player.q == hex_grid.size and player.r == -hex_grid.size:
                            game_won = True
            
            elif event.type == pygame.KEYDOWN and not game_won and not solving:
                if event.key == pygame.K_d:     # Top
                    player.move(0, -1)
                elif event.key == pygame.K_s:    # Top-right
                    player.move(1, -1)
                elif event.key == pygame.K_e:    # Right
                    player.move(1, 0)
                elif event.key == pygame.K_w:    # Bottom
                    player.move(0, 1)
                elif event.key == pygame.K_a:    # Bottom-left
                    player.move(-1, 1)
                elif event.key == pygame.K_q:    # Left
                    player.move(-1, 0)
                
                # Check win condition after keyboard movement
                if player.q == hex_grid.size and player.r == -hex_grid.size:
                    game_won = True

        # Handle automated solving
        if solving and solution_path:
            current_index = len(player.path) - 1
            if current_index < len(solution_path) - 1:
                next_pos = solution_path[current_index + 1]
                moved = player.move(next_pos[0] - player.q, next_pos[1] - player.r)
                if moved and player.q == hex_grid.size and player.r == -hex_grid.size:
                    game_won = True
                    solving = False
                    solution_path = None
            else:
                solving = False
                solution_path = None
                if player.q == hex_grid.size and player.r == -hex_grid.size:
                    game_won = True

        # Draw game state
        screen.fill(WHITE)
        draw_maze(hex_grid, player, game_won, False, solution_path)
        control_guide.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
