import pygame, sys, time, random, math
from pygame.locals import *

# Define colors for each face (using letters for cube state)
BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
RED     = (255,   0,   0)
GREEN   = (  0, 255,   0)
BLUE    = (  0,   0, 255)
ORANGE  = (255, 165,   0)
YELLOW  = (255, 255,   0)

# Map face letter to color for drawing
FACE_COLORS = {
    'U': WHITE,   # Up
    'D': YELLOW,  # Down
    'F': GREEN,   # Front
    'B': BLUE,    # Back
    'L': ORANGE,  # Left
    'R': RED      # Right
}

# Cube Module: Represents cube state as 6 faces (each 3x3)
class RubiksCube:
    def __init__(self):
        # Create solved state: each face represented by its key letter
        self.faces = {face: [[face]*3 for _ in range(3)] for face in "UDFBLR"}
    
    def scramble(self, moves=20):
        # MODIFIED: Randomize each sticker so that the cube visually differs from the solved state.
        for face in self.faces:
            for i in range(3):
                for j in range(3):
                    self.faces[face][i][j] = random.choice("UDFBLR")
        print("Cube scrambled visually")
    
    def apply_move(self, move):
        # Stub: update cube state here (complex rotations omitted)
        print("Applied move:", move)
    
    def is_solved(self):
        for face in self.faces:
            if any(cell != self.faces[face][0][0] for row in self.faces[face] for cell in row):
                return False
        return True
    
    def draw(self, surface):
        # UI Module: Draw a simple flat 2D net of the cube
        sticker_size = 30
        gap = 5
        x_offset = 300
        y_offset = 50
        # Draw Up face
        self.draw_face(surface, self.faces['U'], x_offset, y_offset, sticker_size, gap)
        # Draw Left, Front, Right, Back in a row
        faces_row = ['L','F','R','B']
        for i, face in enumerate(faces_row):
            self.draw_face(surface, self.faces[face], x_offset + i*(3*sticker_size + 3*gap + gap), y_offset + 3*sticker_size + 2*gap, sticker_size, gap)
        # Draw Down face
        self.draw_face(surface, self.faces['D'], x_offset, y_offset + 6*sticker_size + 4*gap, sticker_size, gap)
    
    def draw_face(self, surface, face_matrix, x, y, size, gap):
        for i, row in enumerate(face_matrix):
            for j, val in enumerate(row):
                rect = pygame.Rect(x + j*(size+gap), y + i*(size+gap), size, size)
                pygame.draw.rect(surface, FACE_COLORS.get(val, BLACK), rect)
                pygame.draw.rect(surface, BLACK, rect, 1)

# Solver Module: Implements a stub solver (replace with a real algorithm like Kociemba)
class CubeSolver:
    def __init__(self, cube: RubiksCube):
        self.cube = cube
        self.solution_moves = []
    
    def solve(self):
        if self.cube.is_solved():
            self.solution_moves = []
        else:
            # Stub: fixed sequence as an example.
            self.solution_moves = ['R', "U'", 'F', "L'", 'D']
        print("Solution:", self.solution_moves)
        return self.solution_moves

def main():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Rubik's Cube Solver")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    
    cube = RubiksCube()
    solver = CubeSolver(cube)
    
    # Create button rectangles for mouse control
    solve_button = pygame.Rect(20, 540, 150, 40)
    scramble_button = pygame.Rect(200, 540, 150, 40)
    
    solving = False
    solution_index = 0
    auto_solve = False
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if solve_button.collidepoint(event.pos):
                    moves = solver.solve()
                    solving = True
                    solution_index = 0
                    auto_solve = True
                elif scramble_button.collidepoint(event.pos):
                    cube.scramble(20)
                    solver = CubeSolver(cube)
                    solving = False
                    auto_solve = False

            elif event.type == KEYDOWN:
                if event.key == K_s:
                    moves = solver.solve()
                    solving = True
                    solution_index = 0
                    auto_solve = True
                elif event.key == K_r:
                    cube.scramble(20)
                    solver = CubeSolver(cube)
                    solving = False
                    auto_solve = False

        # If auto-solving, apply moves one at a time
        if solving and auto_solve:
            if solution_index < len(solver.solution_moves):
                move = solver.solution_moves[solution_index]
                cube.apply_move(move)
                solution_index += 1
                # Instead of blocking time.sleep, you can use pygame.time.delay if preferred:
                pygame.time.delay(500)
            else:
                solving = False
        
        screen.fill(WHITE)
        cube.draw(screen)
        
        # Draw buttons
        pygame.draw.rect(screen, BLACK, solve_button, 2)
        solve_text = font.render("Solve", True, BLACK)
        screen.blit(solve_text, solve_text.get_rect(center=solve_button.center))
        
        pygame.draw.rect(screen, BLACK, scramble_button, 2)
        scramble_text = font.render("Scramble", True, BLACK)
        screen.blit(scramble_text, scramble_text.get_rect(center=scramble_button.center))
        
        # Draw instructions
        instr = font.render("Press Solve or Scramble", True, BLACK)
        screen.blit(instr, (20, 20))
        
        pygame.display.flip()
        clock.tick(10)

if __name__ == "__main__":
    main()
