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

    def move(self, dq, dr):
        new_q = self.q + dq
        new_r = self.r + dr
        if (new_q, new_r) in self.hex_grid.grid and self.hex_grid.grid[(new_q, new_r)] == 0:
            self.q = new_q
            self.r = new_r
            self.path.append((self.q, self.r))
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

def main():
    hex_grid = HexGrid(7)  # Smaller size for testing
    generate_maze(hex_grid)
    player = Player(hex_grid)
    control_guide = ControlGuide(WIDTH - 150, HEIGHT - 150)  # Position in bottom-right corner
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Updated keyboard controls to match new direction sequence
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                movement = control_guide.check_click(event.pos)
                if movement:
                    player.move(*movement)

        screen.fill(WHITE)
        
        # Draw maze
        for (q, r), value in hex_grid.grid.items():
            color = WHITE if value == 0 else BLACK
            hex_grid.draw_hexagon(q, r, color)

        # Draw player path
        for q, r in player.path:
            hex_grid.draw_hexagon(q, r, YELLOW)

        # Draw player
        hex_grid.draw_hexagon(player.q, player.r, BLUE)

        # Draw start and end
        hex_grid.draw_hexagon(-hex_grid.size, hex_grid.size, GREEN)
        hex_grid.draw_hexagon(hex_grid.size, -hex_grid.size, RED)

        # Draw control guide
        control_guide.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
